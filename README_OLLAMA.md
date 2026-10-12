# ไฟล์เดียว: firstaid_ollama.py

Created by: skibi rizz sigma 67 scuba ohio tung tung

ไฟล์ .py นี้มีหน้าจอแชต ข้อมูลปฐมพยาบาล 35 หัวข้อ / 81 chunks, Qdrant, Knowledge Graph 649 nodes และชุดคำถามทดสอบในตัว ไม่ต้องคัดลอกโฟลเดอร์ firstaid หรือ web ไปด้วย แต่ต้องติดตั้ง Python และ dependencies

## ใช้ Qwen ผ่าน Ollama ในเครื่อง

ติดตั้ง Ollama จาก https://ollama.com/download แล้วเปิด PowerShell:

```powershell
python -m pip install requests qdrant-client networkx fastapi uvicorn
ollama create firstaid-qwen -f runtime/Modelfile.firstaid
python firstaid_ollama.py
```

เปิด http://127.0.0.1:8081 — โหมด local ไม่ต้องใช้ API key และโปรแกรมจะไม่ส่ง Cloud key ไป localhost

โมเดลเริ่มต้นคือ firstaid-qwen ซึ่งสร้างจาก Qwen3-4B-Instruct-2507 ที่อยู่ใน models/ เป็นรุ่นไม่มี thinking template เพื่อให้ตอบตรงคำถาม หากย้ายไปเครื่องใหม่ ให้รัน scripts/bootstrap_models.py ของโปรเจกต์เพื่อดาวน์โหลดไฟล์ GGUF ก่อนสร้างโมเดล

คำตอบใช้ภาษาไทยง่าย ๆ เป็นขั้นตอน 1–5 ข้อ ไม่เกริ่นยาว จำกัดประมาณ 100 คำ/420 tokens ให้โมเดลส่งขั้นตอนและหมายเลขหลักฐานด้วย JSON schema แล้วแสดงเป็นข้อความ ใช้ context 4096 และเก็บโมเดลในหน่วยความจำ 30 นาที หน้าเว็บแสดงเวลาที่รอและหยุดรอเมื่อเกิน 100 วินาที Backend แจ้ง timeout ที่ 90 วินาที ครั้งแรกที่โหลดโมเดลยังอาจใช้เวลานานกว่าครั้งถัดไป

ในเครื่องของโปรเจกต์นี้ใช้ Python ที่เตรียมไว้ได้:

```powershell
.\.venv\Scripts\python.exe firstaid_ollama.py
```

## ใช้ API key กับ Ollama Cloud

ตรวจวันที่ 12 ตุลาคม 2026: ทดลอง qwen3.5:397b ได้ HTTP 410 (retired) และหน้า [Cloud models](https://ollama.com/search?c=cloud) ไม่มี Qwen ในรายการปัจจุบัน จึงไม่ตั้งชื่อ Qwen ที่ใช้ไม่ได้เป็นค่าเริ่มต้น Cloud และไม่เปลี่ยนตระกูลโมเดลให้เอง

หากเลือกโมเดล Cloud อื่นที่บัญชีมีสิทธิ์ หรือมี Qwen Cloud เปิดใหม่ ให้ระบุชื่อจริงด้วย --model:

```powershell
$env:OLLAMA_API_KEY = 'ใส่คีย์ของคุณในเครื่องเท่านั้น'
python firstaid_ollama.py --cloud --model ชื่อโมเดลที่ใช้ได้ --check
python firstaid_ollama.py --cloud --model ชื่อโมเดลที่ใช้ได้
```

หากไม่ได้ตั้งตัวแปร โปรแกรมจะถาม API key แบบไม่แสดงตัวอักษรผ่าน getpass ใน terminal โดยไม่บันทึกคีย์ลงดิสก์ อ่านแนวทาง [Ollama Cloud](https://docs.ollama.com/cloud) และ [Authentication](https://docs.ollama.com/api/authentication) คีย์ถูกส่งเฉพาะ Authorization Bearer ไป https://ollama.com และไม่ตาม redirect ไป host อื่น

## Vector Database และ embeddings

เพื่อให้ไฟล์เดียวเปิดได้โดยไม่ต้องมี embedding server เพิ่ม ค่าเริ่มต้นใช้ hashed character TF-IDF 2048 มิติ + cosine ใน Qdrant เป็น **การค้นแบบ lexical ไม่ใช่ semantic embeddings** เลือก Qwen Embedding รุ่นเดิมของโปรเจกต์แทนได้:

```powershell
python firstaid_ollama.py --embedding-url http://127.0.0.1:8091/v1
```

ต้องเปิด Qwen3-Embedding-0.6B server จากโปรเจกต์เดิมก่อน หากระบุ endpoint แต่เชื่อมต่อไม่ได้ โปรแกรมจะแจ้งผิดพลาด ไม่เปลี่ยน embedding โดยเงียบๆ เก็บดัชนีแยกตาม configuration เพื่อไม่ผสมเวกเตอร์คนละชนิด

## ตัวเลือกเพิ่มเติม

```powershell
python firstaid_ollama.py --prepare
python firstaid_ollama.py --question 'ผู้ใหญ่เลือดกำเดาไหลควรทำอย่างไร?'
python firstaid_ollama.py --evaluate
python firstaid_ollama.py --help
```

ข้อมูลที่สร้างใหม่เก็บใน .firstaid_ollama/ แยกจากผลทดสอบและฐานข้อมูลเดิม --evaluate เรียกโมเดลจริง 40 ครั้งและเก็บคำตอบ/เฉลย/evidence recall ไม่ให้คะแนนคุณภาพขึ้นมาเอง ต้องให้คนหรือ LLM อื่นให้คะแนนภายหลัง คะแนนเดิมของ Qwen ผ่าน llama.cpp ใช้แทนคะแนน Ollama รุ่นนี้ไม่ได้

ใช้เพื่อการเรียนและการทดลอง คำตอบอาจผิดพลาดตามที่พบในโปรเจกต์เดิม หากเปลี่ยนโมเดลหรือการค้นต้องประเมินใหม่ก่อนนำไปใช้งานจริง

## เที่ยวทะเลและเดินป่า

เพิ่มแมงกะพรุนพิษในทะเลไทย งูกัด เห็บกัด ขาดน้ำ ผิวไหม้แดด และอุณหภูมิร่างกายต่ำ รวมกับหัวข้อเดิม เช่น ลมแดด แมลงต่อย ข้อแพลง และจมน้ำ แหล่งข้อมูลอยู่ใน docs/sources.md
ไฟล์ firstaid_ollama.py สร้าง Qdrant ของข้อมูลชุดใหม่อัตโนมัติเมื่อรัน ผลคะแนนเดิมเป็นของ corpus 29 หัวข้อ ยังไม่ใช่คะแนนของหัวข้อที่เพิ่ม

หัวข้อกลางแจ้งใหม่ใช้ Qwen เลือกข้อความจากขั้นตอนที่แปลอิงแหล่งข้อมูลด้วย constrained JSON schema และระบบเติมขั้นตอนจำเป็นที่ตกหล่น ไม่แก้ตัวเลขหรือข้อห้ามตามข้อความที่โมเดลแต่ง ผล smoke checks อยู่ที่ results/outdoor_smoke_checks.json และภาพจริงใน results/screenshots/outdoor_*.png ยังไม่มีคะแนนการประเมินทางคลินิกของหัวข้อใหม่
