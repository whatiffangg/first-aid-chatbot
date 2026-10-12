import re
import threading
import time
import networkx as nx
from qdrant_client import QdrantClient, models
from .common import DATA, config, read_json
from .llm import embed, chat

def age_constraint(question):
    if any(word in question for word in ["ทารก", "ต่ำกว่า 1 ปี", "8 เดือน", "6 เดือน"]):
        return "infant"
    if "ผู้ใหญ่" in question:
        return "adult"
    if "เด็ก" in question:
        return "child"
    return None

class RAG:
    def __init__(self):
        self.cfg = config()
        self.client = QdrantClient(path=str(DATA / "qdrant"))
        self.graph = nx.node_link_graph(read_json(DATA / "knowledge_graph.json"))
        self.lock = threading.RLock()

    def close(self):
        self.client.close()

    def retrieve(self, question, mode="graph", k=None):
        k = k or self.cfg["k"]
        vector = embed([question], query=True)[0]
        age = age_constraint(question)
        filters = []
        if age:
            filters.append(models.FieldCondition(key="age_group", match=models.MatchAny(any=["all", age])))
        query_filter = models.Filter(must=filters) if filters else None
        with self.lock:
            points = self.client.query_points("firstaid", query=vector, limit=self.cfg["candidate_k"], query_filter=query_filter).points
        contexts = []; counts = {}
        for p in points:
            doc = p.payload["document_id"]
            if counts.get(doc,0) >= 2:
                continue
            counts[doc] = counts.get(doc,0) + 1
            contexts.append({**p.payload, "score": p.score, "retrieval": "vector"})
            if len(contexts) >= k:
                break
        paths = []; related = set(); seeds = list(dict.fromkeys(c["document_id"] for c in contexts))
        # Only explicit topic-to-topic edges are traversed; no spurious Source hubs.
        if mode == "graph":
            frontier = [("topic:"+s, []) for s in seeds]
            for _ in range(self.cfg["graph_hops"]):
                next_frontier = []
                for node, path in frontier:
                    for _, dest, edge in self.graph.out_edges(node, data=True):
                        if edge["relation"] != "RELATED_GUIDANCE":
                            continue
                        doc_id = dest.split(":",1)[1]
                        step = {"from": node, "to": dest, "relation": edge["relation"], "source_urls": edge["source_urls"]}
                        next_frontier.append((dest,path+[step]))
                        if doc_id not in seeds and doc_id not in related:
                            related.add(doc_id); paths.append({"document_id": doc_id, "steps": path+[step]})
                frontier = next_frontier
            if related:
                must = filters + [models.FieldCondition(key="document_id", match=models.MatchAny(any=sorted(related)))]
                with self.lock:
                    extra = self.client.query_points("firstaid", query=vector, limit=30, query_filter=models.Filter(must=must)).points
                picked = set()
                for p in extra:
                    doc = p.payload["document_id"]
                    if doc not in picked:
                        contexts.append({**p.payload, "score": p.score, "retrieval": "graph"}); picked.add(doc)
                    if len(picked) >= self.cfg["graph_extra_documents"]:
                        break
                paths = [p for p in paths if p["document_id"] in picked]
        budget = self.cfg["context_char_budget"]; bounded = []; used = 0
        for c in contexts:
            if used + len(c["text"]) <= budget:
                bounded.append(c); used += len(c["text"])
        return bounded, paths

    def answer(self, question, mode="graph", k=None, history=None):
        started = time.perf_counter(); contexts, paths = self.retrieve(question, mode, k)
        best = max((c["score"] for c in contexts if c["retrieval"] == "vector"), default=0)
        if best < self.cfg["min_similarity"]:
            output = {"answer": "ยังไม่พบหลักฐานที่เกี่ยวข้องเพียงพอในชุดข้อมูลนี้ กรุณาระบุอาการ อายุ และสถานการณ์เพิ่มเติม หากเป็นเหตุฉุกเฉินในไทย โทร 1669", "model": None, "usage": {}, "finish_reason": "insufficient_evidence"}
        else:
            output = chat(question, contexts, history)
        cited = [int(x) for x in re.findall(r"\[S(\d+)\]", output["answer"])]
        output.update({"question": question, "mode": mode, "k": k or self.cfg["k"], "elapsed_seconds": round(time.perf_counter()-started,3),
            "contexts": contexts, "graph_paths": paths, "citation_ids": sorted(set(cited)),
            "invalid_citations": sorted(set(n for n in cited if n<1 or n>len(contexts))),
            "citation_validation": "IDs validated only; claim support requires evaluation",
            "config": self.cfg})
        return output
