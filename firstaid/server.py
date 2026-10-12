from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import json
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .common import ROOT, DATA, read_json, write_json
from .retrieval import RAG

@asynccontextmanager
async def lifespan(app):
    app.state.rag = RAG() if (DATA / "index_manifest.json").exists() else None
    yield
    if app.state.rag:
        app.state.rag.close()

app = FastAPI(title="FirstAid Qwen RAG", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")
class Question(BaseModel):
    question: str = Field(min_length=2, max_length=3000)
    mode: Literal["vector", "graph"] = "graph"
    k: int = Field(default=5, ge=1, le=12)
    history: list[dict] = Field(default_factory=list, max_length=4)

@app.get("/")
def home():
    return FileResponse(ROOT / "web/index.html")

@app.get("/api/status")
def status():
    return {"ready": app.state.rag is not None, "index": read_json(DATA / "index_manifest.json") if (DATA / "index_manifest.json").exists() else None}

@app.post("/api/chat")
def answer(body: Question):
    if not app.state.rag:
        raise HTTPException(503, "ยังไม่มีฐานข้อมูล กรุณารัน python -m firstaid.ingest")
    try:
        history = [{"role": h["role"], "content": str(h["content"])[:3000]} for h in body.history if h.get("role") in ["user", "assistant"] and "content" in h]
        result = app.state.rag.answer(body.question, body.mode, body.k, history)
    except Exception as exc:
        raise HTTPException(503, f"เรียกโมเดลหรือฐานข้อมูลไม่สำเร็จ: {exc}") from exc
    result["id"] = str(uuid.uuid4()); result["created_at"] = datetime.now(timezone.utc).isoformat()
    write_json(ROOT / "results/conversations" / (result["id"]+".json"), result)
    return result

@app.post("/api/retrieve")
def retrieve(body: Question):
    if not app.state.rag:
        raise HTTPException(503, "ยังไม่มีฐานข้อมูล")
    contexts, paths = app.state.rag.retrieve(body.question, body.mode, body.k)
    return {"contexts": contexts, "graph_paths": paths}

@app.get("/api/graph")
def graph():
    if not app.state.rag:
        return {"nodes": [], "edges": []}
    g = app.state.rag.graph
    topics = [n for n,d in g.nodes(data=True) if d["type"]=="Topic"]
    return {"nodes": [{"id":n,"label":g.nodes[n]["label"]} for n in topics],
            "edges": [{"from":u,"to":v,"relation":d["relation"]} for u,v,d in g.edges(data=True) if u in topics and v in topics]}

@app.get("/api/evaluation")
def evaluation():
    path = ROOT / "results/summary.json"
    return read_json(path) if path.exists() else {"status":"not_run","message":"ยังไม่มีผลประเมินจริง"}

@app.get("/api/runs")
def runs():
    path = ROOT / "results/answers.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
    grades_path = ROOT / "results/grades.json"
    grades = read_json(grades_path) if grades_path.exists() else {}
    for row in rows:
        row["quality_review"] = grades.get(row["id"])
    return rows

@app.get("/api/run/{run_id}")
def run(run_id: str):
    for row in runs():
        if row["id"] == run_id:
            return row
    raise HTTPException(404,"ไม่พบผลทดสอบ")
