"""Build the editable single .py; compress only source data and web assets."""
import base64
import json
from pathlib import Path
import zlib
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    payload={"documents":json.loads((ROOT/'data/documents.json').read_text(encoding='utf-8')),
             "chunks":json.loads((ROOT/'data/chunks.json').read_text(encoding='utf-8')),
             "graph":json.loads((ROOT/'data/knowledge_graph.json').read_text(encoding='utf-8')),
             "outdoor_steps":json.loads((ROOT/'data/outdoor_steps_th.json').read_text(encoding='utf-8')),
             "questions":json.loads((ROOT/'evaluation/test_questions.json').read_text(encoding='utf-8')),
             "web":{p.name:p.read_text(encoding='utf-8') for p in (ROOT/'web').glob('*') if p.is_file()}}
    encoded=base64.b64encode(zlib.compress(json.dumps(payload,ensure_ascii=False).encode(),9)).decode()
    template=(ROOT/'templates/firstaid_ollama.template.py').read_text(encoding='utf-8')
    (ROOT/'firstaid_ollama.py').write_text(template.replace('__ASSET_DATA__',encoded),encoding='utf-8')
    print('Created firstaid_ollama.py (no credentials)')
