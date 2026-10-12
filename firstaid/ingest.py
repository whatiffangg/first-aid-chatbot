"""Fetch traceable source text, chunk it, index Qdrant, persist a knowledge graph."""
import argparse
import hashlib
import re
import uuid
from datetime import datetime, timezone
import networkx as nx
import requests
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient, models
from .common import ROOT, DATA, config, write_json, read_json
from .sources import source_manifest, LINKS
from .llm import embed

def extract_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("script,style,nav,footer,header"):
        tag.decompose()
    heading = soup.find("h1")
    if not heading:
        raise ValueError("Source has no h1; refusing to ingest an error page")
    lines = []; seen = set()
    for tag in heading.find_all_next(["h2", "h3", "p", "li"]):
        if tag.name == "li" and tag.find(["p", "li"]):
            continue  # Do not duplicate nested numbered steps.
        line = tag.get_text(" ", strip=True)
        if any(stop in line for stop in ["If you found this article", "Related first aid advice", "Help us continue", "If you're looking for more", "Newsletter"]):
            break
        if len(line) > 8 and line not in seen:
            seen.add(line); lines.append(line)
    if len(" ".join(lines)) < 200:
        raise ValueError("Insufficient article text")
    return "\n".join(lines)

def chunk_text(text, size=220, overlap=40):
    if size <= overlap or overlap < 0:
        raise ValueError("Chunk size must exceed nonnegative overlap")
    # Keep paragraphs and numbered instructions together where possible.
    paragraphs = text.split("\n"); chunks = []; current = []
    for paragraph in paragraphs:
        words = paragraph.split()
        if current and len(current) + len(words) > size:
            chunks.append(" ".join(current)); current = current[-overlap:] if overlap else []
        current.extend(words)
        while len(current) > size * 1.5:
            chunks.append(" ".join(current[:size])); current = current[size-overlap:]
    if current:
        chunks.append(" ".join(current))
    return chunks

def extract_source(html, source):
    kind = source.get("extraction_kind")
    if not kind:
        return extract_html(html)
    soup = BeautifulSoup(html, "html.parser")
    if kind == "ddc-jellyfish-guidance":
        # Exact guidance paragraph, excluding historic case statistics and site menus.
        lines = [p.get_text(" ", strip=True) for p in soup.find_all("p")
                 if "หากสงสัยว่าอาจโดนแมงกะพรุนพิษ" in p.get_text()]
        if len(lines) != 1:
            raise ValueError("DDC article guidance boundary changed")
        text = re.sub(r"\s+(?=[1-5]\.\s)", "\n", lines[0])
    elif kind == "chula-snake-guidance":
        content = soup.select_one(".elementor-element-74fe554")
        if content is None:
            raise ValueError("Chula article content boundary changed")
        text = content.get_text("\n", strip=True)
    else:
        raise ValueError("Unknown source extractor")
    if len(text) < 200 or "\ufffd" in text:
        raise ValueError("Incomplete source guidance")
    return text

def fetch_sources(refresh=False):
    docs = []; manifest = source_manifest(); failures = []
    for source in manifest:
        raw = DATA / "raw" / (source["id"] + ".html"); raw.parent.mkdir(parents=True, exist_ok=True)
        try:
            if raw.exists() and not refresh:
                html = raw.read_bytes()
            else:
                response = requests.get(source["url"], timeout=45, headers={"User-Agent": "FirstAidResearch/1.0 (educational prototype)"})
                response.raise_for_status(); html = response.content
                raw.write_bytes(html)
            text = extract_source(html, source)
            doc = {**source, "source_url": source["url"], "text": text,
                   "retrieved_at": datetime.now(timezone.utc).isoformat(),
                   "raw_sha256": hashlib.sha256(html).hexdigest()}
            translation_path = DATA / "outdoor_guidance_th.json"
            if translation_path.exists() and source["id"] in read_json(translation_path):
                doc["guidance_th"] = read_json(translation_path)[source["id"]]
                doc["translation_status"] = "project_translation_not_clinically_validated"
            docs.append(doc); print(f"Fetched {source['id']}: {len(text)} characters", flush=True)
        except Exception as exc:
            failures.append({"id": source["id"], "error": str(exc)})
    write_json(DATA / "sources.json", manifest)
    write_json(DATA / "documents.json", docs)
    write_json(DATA / "fetch_failures.json", failures)
    if failures:
        raise RuntimeError(f"{len(failures)} sources failed. See data/fetch_failures.json; rerun to retry.")
    return docs

def build_graph(docs, chunks):
    g = nx.MultiDiGraph()
    ids = {d["id"] for d in docs}
    for doc in docs:
        tid = "topic:" + doc["id"]; sid = "source:" + doc["id"]
        g.add_node(tid, type="Topic", label=doc["title_th"], aliases=doc["aliases"], document_id=doc["id"])
        g.add_node(sid, type="Source", url=doc["source_url"], publisher=doc["publisher"], sha256=doc["raw_sha256"])
        age = "age:" + doc["age_group"]; g.add_node(age, type="AgeGroup", label=doc["age_group"])
        g.add_edge(tid, age, relation="APPLIES_TO")
        for chunk in [c for c in chunks if c["document_id"] == doc["id"]]:
            cid = "chunk:" + chunk["id"]
            g.add_node(cid, type="Chunk", chunk_id=chunk["id"], section_index=chunk["section_index"])
            g.add_edge(tid, cid, relation="HAS_EVIDENCE")
            g.add_edge(cid, sid, relation="FROM_SOURCE")
        section = "guidance" if doc.get("extraction_kind") else None
        for line_index, line in enumerate(doc["text"].splitlines()):
            if line == "Signs and symptoms":
                section = "signs"; continue
            if line.startswith("What to do"):
                section = "guidance"; continue
            if not section or line in ["Look for:", "A choking baby may:"] or len(line) < 18:
                continue
            kind = "Sign" if section == "signs" else "GuidanceStep"
            if section == "guidance" and line.startswith(("Do not ", "Never ", "ห้าม", "ไม่แนะนำ")):
                kind = "Contraindication"
            nid = f"{kind.lower()}:{doc['id']}:{line_index}"
            relation = {"Sign":"HAS_SIGN", "GuidanceStep":"HAS_GUIDANCE", "Contraindication":"HAS_CONTRAINDICATION"}[kind]
            g.add_node(nid, type=kind, label=line[:80], text=line, document_id=doc["id"],
                       age_group=doc["age_group"], language=doc["language"], scope="verbatim source statement; retain its conditions",
                       review_status=doc["review_status"])
            g.add_edge(tid, nid, relation=relation)
            g.add_edge(nid, sid, relation="FROM_SOURCE")
            prefix = " ".join(line.split()[:12])
            for chunk in [c for c in chunks if c["document_id"] == doc["id"] and prefix in c["text"]]:
                g.add_edge(nid, "chunk:"+chunk["id"], relation="SUPPORTED_BY")
    for left, right in LINKS:
        if left in ids and right in ids:
            g.add_edge("topic:"+left, "topic:"+right, relation="RELATED_GUIDANCE",
                       provenance="project-authored topic routing; medical actions remain in source chunks",
                       source_urls=[next(d["source_url"] for d in docs if d["id"]==left), next(d["source_url"] for d in docs if d["id"]==right)])
    write_json(DATA / "knowledge_graph.json", nx.node_link_data(g))
    return g

def index(docs):
    cfg = config(); chunks = []
    for doc in docs:
        for i, text in enumerate(chunk_text(doc["text"], cfg["chunk_words"], cfg["overlap_words"])):
            chunks.append({"id": str(uuid.uuid5(uuid.NAMESPACE_URL, doc["url"] + f"#{i}")),
                "document_id": doc["id"], "section_index": i, "title_th": doc["title_th"],
                "aliases": doc["aliases"], "source_url": doc["source_url"], "publisher": doc["publisher"],
                "age_group": doc["age_group"], "retrieved_at": doc["retrieved_at"], "text": text,
                "review_status": doc["review_status"]})
            if doc.get("guidance_th"):
                chunks[-1]["guidance_th"] = doc["guidance_th"]
    vectors = []
    for i in range(0, len(chunks), 6):
        vectors.extend(embed([c["title_th"] + "\n" + c["text"] for c in chunks[i:i+6]]))
        print(f"Embedded {min(i+6,len(chunks))}/{len(chunks)}", flush=True)
    client = QdrantClient(path=str(DATA / "qdrant"))
    try:
        if client.collection_exists("firstaid"):
            client.delete_collection("firstaid")
        client.create_collection("firstaid", vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE))
        client.upsert("firstaid", points=[models.PointStruct(id=c["id"], vector=v, payload=c) for c,v in zip(chunks,vectors)], wait=True)
    finally:
        client.close()
    write_json(DATA / "chunks.json", chunks)
    graph = build_graph(docs, chunks)
    write_json(DATA / "index_manifest.json", {"documents": len(docs), "chunks": len(chunks), "vector_dimensions": len(vectors[0]),
        "embedding_model": cfg["embedding_model"], "distance": "cosine", "graph_nodes": len(graph), "graph_edges": graph.number_of_edges(),
        "config": cfg, "created_at": datetime.now(timezone.utc).isoformat()})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--fetch-only", action="store_true"); parser.add_argument("--cached", action="store_true"); parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args(); docs = read_json(DATA / "documents.json") if args.cached else fetch_sources(args.refresh)
    if not args.fetch_only:
        index(docs)
