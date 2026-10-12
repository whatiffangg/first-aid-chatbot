# FirstAid Qwen RAG — แชตบอทปฐมพยาบาลภาษาไทย

Created by: skibi rizz sigma 67 scuba ohio tung tung

โปรเจกต์สำหรับการเรียนและการประเมิน RAG ใช้ **Qwen3-4B-Instruct-2507**, **Qwen3-Embedding-0.6B**, **Qdrant Local** และ **Knowledge Graph ด้วย NetworkX** ทำงานในเครื่อง ไม่ต้องใช้ OpenAI API key ข้อมูลต้นฉบับเป็นภาษาอังกฤษจาก St John Ambulance 29 หัวข้อ โมเดลตอบเป็นภาษาไทยพร้อมรหัสหลักฐาน

เป็นต้นแบบวิจัยที่ยังไม่ผ่านการรับรองทางคลินิก ไม่ใช้แทนเจ้าหน้าที่ฉุกเฉิน ในประเทศไทยโทร 1669 เมื่อมีเหตุฉุกเฉิน การมีอ้างอิงไม่ได้รับประกันว่าคำตอบถูกต้อง

## เปิดใช้งานในเครื่องนี้

```powershell
cd C:\Users\User\Desktop\ku\01418363\project
.\start.ps1
```

เปิด http://127.0.0.1:8080 เซิร์ฟเวอร์โมเดลอยู่ localhost:8090 และ embedding อยู่ localhost:8091 หากมีบริการอยู่แล้ว script จะใช้บริการที่มีอยู่ ตรวจชื่อโมเดลจาก config.json และ /v1/models ให้ตรงกัน หาก PowerShell ไม่อนุญาตรัน script ใช้ `powershell -ExecutionPolicy Bypass -File .\start.ps1` เฉพาะการเรียกนี้

## ติดตั้งบนเครื่องใหม่

ต้องมี Python 3.12+, พื้นที่ว่างประมาณ 8 GB, แนะนำ RAM 16 GB และเชื่อมต่ออินเทอร์เน็ตเฉพาะตอนติดตั้ง/ดาวน์โหลดข้อมูล Windows x64 ใช้ portable runtime ที่ให้มา

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe scripts/bootstrap_models.py
.\.venv\Scripts\python.exe scripts/bootstrap_gpu.py  # optional: NVIDIA GPU + compatible driver
.\.venv\Scripts\python.exe -m playwright install chromium
.\start.ps1
```

ครั้งแรก start.ps1 จะนำเข้าข้อมูลและสร้างดัชนีอัตโนมัติ หากมี data/qdrant อยู่แล้วจะใช้ฐานเดิม เก็บ requirements.txt สำหรับช่วงเวอร์ชันและ requirements-lock.txt สำหรับเวอร์ชันที่ทดสอบจริง

เครื่องที่ใช้ทดลองมี AMD Ryzen 7 260, RAM ประมาณ 16 GB, NVIDIA RTX 5050 Laptop VRAM 8 GB ใช้ CUDA runtime สำหรับ chat และ CPU สำหรับ embedding หากมี runtime/llama-cuda script จะเลือก GPU ต้องใช้ NVIDIA driver ที่รองรับ CUDA build นั้น หากใช้ CPU ให้ใช้ script โดยย้ายชื่อโฟลเดอร์ CUDA ออกหรือปรับ launch path

## ข้อมูลและเทคนิค

- corpus: `data/documents.json`, manifest URL: `data/sources.json`, ไฟล์ต้นฉบับและ SHA256: `data/raw/`
- แบ่งข้อความตามย่อหน้า ขนาดเป้าหมาย 220 **คำภาษาอังกฤษที่คั่นด้วยช่องว่าง** overlap 40 คำ ไม่ใช่ 220 tokens; หนึ่งย่อหน้าที่ยาวอาจเกินเป้าหมายเพื่อรักษาบริบท
- Qwen3-Embedding-0.6B แบบ Q8_0, 1024 มิติ, last-token pooling, เพิ่ม retrieval instruction เฉพาะ query ตาม model card
- Qdrant: collection `firstaid`, Cosine similarity, candidates 12, final vector k=5, จำกัดไม่เกิน 2 chunks ต่อเอกสาร
- Graph: Topic, AgeGroup, Chunk, Source, Sign, GuidanceStep, Contraindication พร้อม HAS_SIGN / HAS_GUIDANCE / HAS_CONTRAINDICATION / SUPPORTED_BY และเส้นเชื่อมหลักฐาน บันทึก JSON ถาวรและโหลดเป็น NetworkX MultiDiGraph ข้อความขั้นตอนเก็บตามต้นฉบับพร้อมเงื่อนไข ไม่ใช่คำสั่งที่อนุมานจากกราฟ
- Graph retrieval: ตาม RELATED_GUIDANCE แบบมีทิศทาง 1 hop เพิ่มไม่เกิน 3 เอกสาร เลือก chunk ของเอกสารนั้นด้วย vector similarity อีกครั้ง context budget 10000 ตัวอักษร
- กรองกลุ่มอายุเมื่อระบุผู้ใหญ่ เด็ก หรือทารก ไม่อนุมานอายุจากทุกข้อความได้ และไม่รับรองว่าการกรองนี้ครบทุกกรณี
- similarity threshold 0.3 เป็นค่าเริ่มต้น ยังไม่ใช่ค่าที่สอบเทียบทางคลินิก สามารถปรับใน config.json แล้ว restart เว็บ
- Qwen3-4B-Instruct-2507 แบบ GGUF Q4_K_M จาก Unsloth (โมเดลต้นฉบับโดย Qwen), temperature 0.1, output สูงสุด 650 tokens, context runtime 8192 tokens
- กราฟใช้เชื่อมหัวข้อเพื่อค้นหลักฐาน ไม่ใช้ความสัมพันธ์ที่ LLM สร้างเองมาเป็นคำวินิจฉัย การตอบยังใช้ข้อความต้นฉบับ

## ทดสอบและประเมิน

ขณะเว็บเปิดอยู่:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/dev_retrieval.py
.\.venv\Scripts\python.exe scripts/evaluate.py
.\.venv\Scripts\python.exe scripts/capture.py
.\.venv\Scripts\python.exe scripts/evaluate.py --summary-only
```

ชุดทดสอบ 20 ข้อ: direct 10 ข้อ / multihop 10 ข้อ; ทดสอบ Vector และ Vector+Graph รวม 40 บทสนทนา แยก dev_questions.json ออกจาก test_questions.json และไม่ใส่เฉลยลง corpus ประเมินจาก `evaluation/rubric.md` ผลดิบ `results/answers.jsonl`, คะแนน LLM พร้อมเหตุผล `results/grades.json`, ตาราง `results/summary.csv`, ภาพ `results/screenshots/` และแบบประเมินคนที่ยังเว้นคะแนนไว้ `results/human_review.csv`

evaluate.py resume จาก run_id ที่มีอยู่ หากเปลี่ยนโมเดล/config ต้องเก็บผลเดิมในโฟลเดอร์อื่นก่อนรันใหม่ อย่าผสมหลาย config เป็นการทดลองเดียว ข้อผิดพลาด API บันทึกไว้ใน errors.jsonl และไม่สร้างคำตอบปลอมแทน

ภาพ capture เป็นหน้าเว็บที่เปิดผลบทสนทนาที่บันทึกจากการรันจริง (replay) ไม่ใช่ภาพแสดง generation แบบสด `?run=graph_D01` ใช้เปิดผลทดสอบรายข้อ

## เปลี่ยนเป็น Ollama

สามารถเปลี่ยน config.chat_provider เป็น `ollama` และ chat_model เป็น tag Qwen ที่มีในเครื่อง ใช้ embedding server เดิมต่อไปได้ รัน Ollama แยกต่างหาก โค้ดไม่ได้ดาวน์โหลดโมเดล Ollama เอง ผลการทดลองที่แนบใช้ llama.cpp ไม่ใช่ Ollama

## โครงสร้าง

```text
firstaid/       ingestion, embedding, vector+graph retrieval, FastAPI
web/            หน้าจอแชต, กราฟ, ผลประเมิน
evaluation/     คำถามพัฒนา/ทดสอบ, เฉลยร่าง, rubric
scripts/        ดาวน์โหลดโมเดล, รันทดสอบ, capture, สรุปผล
data/           corpus, Qdrant, graph, manifests
results/        คำตอบจริง, คะแนน, CSV, screenshots, pilot
docs/           รายงานและแหล่งอ้างอิง
models/         weights ที่ดาวน์โหลดและ SHA256
runtime/        llama.cpp แบบ portable
```

อ่านรายละเอียดการทดลองและข้อจำกัดใน docs/report.md ข้อมูลเว็บไซต์มีลิขสิทธิ์ของผู้เผยแพร่ การใช้เพื่อการเรียนไม่ได้ให้สิทธิ์เผยแพร่ corpus ต้นฉบับต่อโดยอัตโนมัติ หากแจกโปรเจกต์สาธารณะให้ตรวจเงื่อนไขและแจก manifest พร้อม ingestion script ตามความเหมาะสม

## อัปเดต corpus กลางแจ้ง

สำหรับแอปปัจจุบันให้รัน firstaid_ollama.py ที่พอร์ต 8081 มี 35 หัวข้อ / 81 chunks รวมแมงกะพรุน งูกัด เห็บกัด ขาดน้ำ ผิวไหม้แดด และตัวเย็น ข้อมูล 29 หัวข้อและคะแนนด้านบนเป็นการทดลองเดิม ส่วน Qdrant ของ runtime เดิมที่พอร์ต 8080 ต้องสร้างใหม่ด้วย python -m firstaid.ingest --cached เมื่อเปิด Qwen embedding service แล้ว ดู README_OLLAMA.md สำหรับแอป Ollama ปัจจุบัน
