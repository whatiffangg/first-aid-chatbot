"""Real Qwen runs; no simulated answers or fabricated human ratings."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import requests
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from firstaid.common import read_json, write_json

def summary():
    path=ROOT/"results/answers.jsonl"
    rows=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
    grades=read_json(ROOT/"results/grades.json") if (ROOT/"results/grades.json").exists() else {}
    groups=[]
    for mode in sorted({r["mode"] for r in rows}):
        for group in ["direct","multihop"]:
            selected=[r for r in rows if r["mode"]==mode and r["group"]==group]
            if not selected: continue
            values=[grades[r["id"]]["total"] for r in selected if r["id"] in grades]
            groups.append({"mode":mode,"group":group,"n":len(selected),"graded_n":len(values),
                "mean_score":sum(values)/len(values) if len(values)==len(selected) else None,
                "evidence_recall":sum(r["evidence_recall"] for r in selected)/len(selected),
                "mean_seconds":sum(r["elapsed_seconds"] for r in selected)/len(selected),
                "truncated_answers":sum(r["finish_reason"]=="length" for r in selected),
                "invalid_citation_answers":sum(bool(r["invalid_citations"]) for r in selected)})
    averages=[]
    for mode in sorted({r["mode"] for r in rows}):
        pairs=[g for g in groups if g["mode"]==mode]
        averages.append({"mode":mode,"macro_mean_score":sum(g["mean_score"] for g in pairs)/2 if len(pairs)==2 and all(g["mean_score"] is not None for g in pairs) else None,
            "macro_evidence_recall":sum(g["evidence_recall"] for g in pairs)/len(pairs)})
    output={"status":"real_runs","groups":groups,"averages":averages,"evaluator": "Codex LLM reviewer; see grades.json for explicit reasons. Not a clinical or human assessment." if grades else None,
        "metric_note":"Evidence recall is document-level gold-topic coverage in final retrieved contexts, not medical answer accuracy.",
        "created_at":datetime.now(timezone.utc).isoformat()}
    write_json(ROOT/"results/summary.json",output)
    with (ROOT/"results/summary.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(groups[0]) if groups else ["mode"]);writer.writeheader();writer.writerows(groups)
    return output

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--url",default="http://127.0.0.1:8080");parser.add_argument("--modes",nargs="+",default=["vector","graph"]);parser.add_argument("--limit",type=int);parser.add_argument("--summary-only",action="store_true");args=parser.parse_args()
    if args.summary_only: print(json.dumps(summary(),ensure_ascii=False,indent=2));return
    questions=read_json(ROOT/"evaluation/test_questions.json")
    if args.limit: questions=questions[:args.limit]
    output=ROOT/"results/answers.jsonl";output.parent.mkdir(exist_ok=True)
    done={json.loads(x)["id"] for x in output.read_text(encoding="utf-8").splitlines()} if output.exists() else set()
    for mode in args.modes:
        for q in questions:
            run_id=mode+"_"+q["id"]
            if run_id in done:continue
            try:
                response=requests.post(args.url+"/api/chat",json={"question":q["question"],"mode":mode,"k":5},timeout=900);response.raise_for_status();r=response.json()
            except Exception as exc:
                with (ROOT/"results/errors.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps({"id":run_id,"error":str(exc)},ensure_ascii=False)+"\n")
                print(f"FAILED {run_id}: {exc}",flush=True);continue
            retrieved={c["document_id"] for c in r["contexts"]};expected=set(q["required_documents"])
            r.update({"id":run_id,"question_id":q["id"],"group":q["group"],"reference_answer":q["reference_answer"],"required_documents":q["required_documents"],
                "evidence_recall":len(retrieved&expected)/len(expected),"all_required_evidence":expected<=retrieved})
            with output.open("a",encoding="utf-8") as f:f.write(json.dumps(r,ensure_ascii=False)+"\n")
            print(f"{run_id}: {r['elapsed_seconds']}s, evidence recall={r['evidence_recall']:.2f}, finish={r['finish_reason']}",flush=True)
    # Empty human score cells remain blank until a real reviewer completes them.
    with (ROOT/"results/human_review.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f);w.writerow(["run_id","question","correctness_0_4","completeness_0_4","safety_0_4","clarity_0_4","citations_0_4","reviewer","notes"])
        for r in [json.loads(x) for x in output.read_text(encoding="utf-8").splitlines()]:w.writerow([r["id"],r["question"],"","","","","","",""])
    print(json.dumps(summary(),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
