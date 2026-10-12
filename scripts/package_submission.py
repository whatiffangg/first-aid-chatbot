"""Bundle code, reports, real evaluation artifacts; exclude large local runtimes."""
import csv
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    rows=[json.loads(x) for x in (ROOT/'results/answers.jsonl').read_text(encoding='utf-8').splitlines()]
    grades=json.loads((ROOT/'results/grades.json').read_text(encoding='utf-8'))
    with (ROOT/'results/answer_scores.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['run_id','mode','group','question','correctness','completeness','safety','clarity','citations','total_20','evidence_recall','elapsed_seconds','reason','screenshot'])
        for r in rows:
            g=grades[r['id']];w.writerow([r['id'],r['mode'],r['group'],r['question'],*[g[k] for k in ['correctness','completeness','safety','clarity','citations','total']],r['evidence_recall'],r['elapsed_seconds'],g['reason'],'screenshots/'+r['id']+'.png'])
    lines=['# ภาพหน้าจอบทสนทนาที่ทดสอบจริง','', 'คำตอบเป็นผล Qwen ที่บันทึกจริง เปิดในเว็บด้วย replay; คะแนนเป็น LLM review มีข้อผิดพลาดที่ต้องดูประกอบ ไม่ใช้เป็นคู่มือรักษา','']
    for mode in ['vector','graph']:
        for group in ['direct','multihop']:
            lines += ['## '+mode+' / '+group,'']
            for r in rows:
                if r['mode']==mode and r['group']==group:
                    lines.append(f"- [{r['id']}]({r['id']}.png) — {r['question']} — {grades[r['id']]['total']}/20")
            lines.append('')
    lines += ['- [ผลประเมินรวม](evaluation.png)','- [กราฟความรู้](knowledge_graph.png)','- [ทดสอบส่งคำถามผ่านหน้าจอสด](live_e2e.png)']
    (ROOT/'results/screenshots/index.md').write_text('\n'.join(lines),encoding='utf-8')
    bundle=ROOT/'firstaid-qwen-submission.zip'
    files=[]
    for folder in ['firstaid','web','evaluation','tests','scripts','docs','results','templates']:
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'conversations' not in p.parts]
    files += [ROOT/x for x in ['README.md','README_OLLAMA.md','firstaid_ollama.py','requirements.txt','requirements-lock.txt','config.json','start.ps1','.gitignore']]
    files += [ROOT/'data'/x for x in ['sources.json','documents.json','chunks.json','knowledge_graph.json','outdoor_guidance_th.json','outdoor_steps_th.json']]
    files.append(ROOT/'models/manifest.json')
    files.append(ROOT/'runtime/Modelfile.firstaid')
    # No index_manifest in bundle: start.ps1 correctly rebuilds Qdrant on another computer.
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for path in files:z.write(path,path.relative_to(ROOT))
    print(f'{bundle.name}: {len(files)} files, {bundle.stat().st_size/2**20:.1f} MB')
