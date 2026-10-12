"""Live smoke checks; not clinical grading or the historic 20-question evaluation."""
import json
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
CASES=[
 ('jellyfish-stings-thailand','โดนแมงกะพรุนที่ทะเลไทยควรทำอย่างไร?'),
 ('snake-bites','เดินป่าแล้วถูกงูกัดควรช่วยอย่างไร?'),
 ('tick-bite','เห็บติดผิวหนังต้องเอาออกอย่างไร?'),
 ('dehydration','เดินป่าจนกระหายน้ำ ปากแห้ง ปัสสาวะน้อย ต้องทำอย่างไร?'),
 ('sunburn','เที่ยวทะเลแล้วผิวไหม้แดดควรทำอย่างไร?'),
 ('hypothermia','ตั้งแคมป์แล้วเสื้อเปียก หนาวสั่น ตัวเย็น ต้องช่วยอย่างไร?'),
]
rows=[]
for expected,question in CASES:
 response=requests.post('http://127.0.0.1:8081/api/chat',json={'question':question,'mode':'graph','k':5},timeout=110)
 response.raise_for_status();row=response.json()
 row['smoke_expected_topic']=expected
 row['smoke_retrieval_pass']=expected in {c['document_id'] for c in row['contexts']}
 rows.append(row)
 print(expected,row['smoke_retrieval_pass'],row['elapsed_seconds'],row['answer'],sep=' | ',flush=True)
(ROOT/'results/outdoor_smoke_checks.json').write_text(json.dumps({'type':'live smoke checks; no human or clinical scores','rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
assert all(row['smoke_retrieval_pass'] for row in rows)
with sync_playwright() as p:
 browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1080})
 for row in rows[:2]:
  page.goto('http://127.0.0.1:8081/');page.wait_for_function('window.appReady===true');page.evaluate('(row) => loadRun(row)', row)
  assert '[S' not in page.locator('.message.assistant .answer').inner_text()
  assert page.locator('.sources a').count()>0
  page.screenshot(path=str(ROOT/'results/screenshots'/('outdoor_'+row['smoke_expected_topic']+'.png')),full_page=True)
 browser.close()
