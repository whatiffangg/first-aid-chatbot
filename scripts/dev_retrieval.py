"""Parameter exploration uses dev questions, never test references in retrieval."""
import json
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    questions=json.loads((ROOT/'evaluation/dev_questions.json').read_text(encoding='utf-8'))
    rows=[]
    for k in [3,5,8]:
        for mode in ['vector','graph']:
            for q in questions:
                r=requests.post('http://127.0.0.1:8080/api/retrieve',json={'question':q['question'],'k':k,'mode':mode},timeout=120);r.raise_for_status()
                c=r.json()['contexts'];retrieved={x['document_id'] for x in c};expected=set(q['required_documents'])
                rows.append({'question':q['question'],'k':k,'mode':mode,'evidence_recall':len(retrieved&expected)/len(expected),'top_score':c[0]['score'],'documents':sorted(retrieved)})
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/dev_retrieval.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))
