# แหล่งข้อมูลและเอกสารเทคนิค

ตรวจค้นวันที่ 12 ตุลาคม 2026 (Asia/Bangkok)

## แหล่งข้อมูลที่นำเข้าจริง

St John Ambulance — [First aid advice](https://www.sja.org.uk/first-aid-advice/): บทความ 29 หัวข้อ ตาม data/sources.json รวมการประเมินเบื้องต้น CPR, AED, แผลเล็ก เลือดออก ช็อก แผลไหม้ สำลักแยกอายุ ชัก แพ้รุนแรง ลมแดด stroke จมน้ำ ไฟดูด บาดเจ็บศีรษะและสันหลัง สารพิษ หอบหืด และหัวใจวาย

แต่ละเอกสารเก็บ URL ผู้เผยแพร่ ภาษา กลุ่มอายุ เวลาที่ดาวน์โหลด และ SHA256 ของ HTML ต้นฉบับ ไม่ตีความวัน crawl ของเครื่องมือค้นหาเป็นวันที่ปรับปรุงแนวทางทางคลินิก เว็บไซต์ระบุว่ามีทีมคลินิกดูแลความถูกต้อง แต่โปรเจกต์นี้ยังไม่ได้ให้บุคลากรสุขภาพตรวจรับรอง corpus หรือการแปลของโมเดล

## แหล่งอ้างอิงประกอบและแหล่งที่ขยายได้

- [สถาบันการแพทย์ฉุกเฉินแห่งชาติ — คู่มืออาสาฉุกเฉินชุมชน 1669](https://www.niems.go.th/th/Upload/File/255806170927272659_RjIY5vBXo478QPsb.pdf): รองรับบริบทหมายเลขฉุกเฉินไทย 1669; ไม่ได้นำข้อความเก่าทั้งคู่มือเข้าฐานตอบ
- [สภากาชาดไทย — ศูนย์ฝึกอบรมปฐมพยาบาลและสุขภาพอนามัย](https://learning.redcross.or.th/): แหล่งภาษาไทยสำหรับขยาย corpus
- [สภากาชาดไทย — การปฐมพยาบาลฉุกเฉินและการกู้ชีพขั้นพื้นฐาน (PDF)](https://rtrc.redcross.or.th/ewt/rtrc_web/download/article/article_20210304140504.pdf): ต้องตรวจรุ่นแนวทางก่อนนำเข้า
- [IFRC International First Aid, Resuscitation and Education Guidelines 2025](https://www.ifrc.org/document/ifrc-international-first-aid-resuscitation-and-education-guidelines-2025): แนวทางสากลสำหรับตรวจเทียบและขยาย ไม่ได้อ้างว่าทั้งเล่มถูกนำเข้าหรือใช้ยืนยันทุกคำตอบในการทดลองนี้
- [American Red Cross — First Aid Steps](https://www.redcross.org/take-a-class/first-aid/performing-first-aid/first-aid-steps): แหล่งตรวจเทียบการประเมินเบื้องต้น
- [British Red Cross — Burns](https://www.redcross.org.uk/first-aid/learn-first-aid/burns): แหล่งตรวจเทียบหัวข้อแผลไหม้

## แหล่งข้อมูลด้านเทคนิค

1. [Qwen3-4B-Instruct-2507 — official model card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507): รุ่น non-thinking, 4B parameters, instruction-following และ multilingual capabilities; ความสามารถที่ผู้สร้างรายงานไม่ใช่หลักฐานความแม่นยำปฐมพยาบาลของโปรเจกต์นี้
2. [Unsloth Qwen3-4B-Instruct-2507 GGUF](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF): ไฟล์ Q4_K_M ที่ใช้รันจริง เป็น quantization จากผู้เผยแพร่รายอื่น ไม่ใช่ไฟล์ GGUF ที่ Qwen อัปโหลดเอง
3. [Qwen3-Embedding-0.6B — official model card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B): last token pooling, query instruction และการสร้าง embedding
4. [Qwen3-Embedding-0.6B GGUF — Qwen](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF): ไฟล์ Q8_0
5. [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388): รายงานโมเดลตระกูล Qwen3
6. [llama.cpp](https://github.com/ggml-org/llama.cpp): runtime และ OpenAI-compatible HTTP endpoints; portable Windows build ตรวจสอบใน models/manifest.json
7. [Qdrant Search](https://qdrant.tech/documentation/search/): query API และ cosine similarity
8. [Qdrant Python client local mode](https://github.com/qdrant/qdrant-client): persistent local storage โดยไม่ต้องมี Docker/server
9. [NetworkX JSON graph serialization](https://networkx.org/documentation/stable/reference/readwrite/json_graph.html): node-link JSON สำหรับเก็บกราฟถาวร
10. [NetworkX MultiDiGraph](https://networkx.org/documentation/stable/reference/classes/multidigraph.html): กราฟมีทิศทางหลายความสัมพันธ์
11. [FastAPI](https://fastapi.tiangolo.com/): REST API และหน้าจอเว็บ
12. [Playwright Python screenshots](https://playwright.dev/python/docs/screenshots): capture หน้าจอบทสนทนาจริงที่บันทึก
13. [Ragas metrics](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/): แนวคิด faithfulness/context recall เป็นอ้างอิงสำหรับแนวทางประเมิน; โค้ดนี้ไม่ได้ใช้ Ragas คำนวณคะแนนโดยอัตโนมัติ

Chunking ของโค้ดนี้เป็น paragraph-aware word chunking ที่พัฒนาในโปรเจกต์ ไม่ได้ใช้ LangChain TextSplitter การประเมิน evidence recall เป็นระดับเอกสารตาม gold topics ไม่ใช่ Ragas Context Recall และไม่ใช่คะแนนความถูกต้องของคำตอบ

## เพิ่มหัวข้อท่องเที่ยวและเดินป่า (12 ตุลาคม 2026)

corpus ปัจจุบันมี 35 เอกสาร / 81 chunks คะแนน 40 คำตอบเดิมเป็นการทดสอบ corpus 29 หัวข้อก่อนการเพิ่มนี้ ไม่ใช่คะแนนประเมินหัวข้อใหม่

- [กรมควบคุมโรค — แมงกะพรุนพิษในทะเลไทย](https://ddc.moph.go.th/doe/news.php?deptcode=doe&news=21057&news_views=302): นำเข้าย่อหน้าคำแนะนำ 5 ขั้นตอนตามต้นฉบับ เผยแพร่ 11 ตุลาคม 2564 เน้นแมงกะพรุนพิษโดยเฉพาะแมงกะพรุนกล่องในทะเลไทย ไม่ใช้เป็นแนวทางเหมารวมสัตว์ทะเลทุกชนิด
- [โรงพยาบาลจุฬาลงกรณ์ สภากาชาดไทย — งูกัด](https://kcmh.chulalongkornhospital.go.th/line/งูกัด/): นำเข้าข้อความบทความ ไม่รวมเมนูเว็บไซต์ ข้อมูล ณ 21 กุมภาพันธ์ 2561
- [St John Ambulance — เห็บกัด](https://www.sja.org.uk/first-aid-advice/tick-bite/)
- [St John Ambulance — ภาวะขาดน้ำ](https://www.sja.org.uk/first-aid-advice/dehydration/)
- [St John Ambulance — ผิวไหม้แดด](https://www.sja.org.uk/first-aid-advice/sunburn/)
- [St John Ambulance — อุณหภูมิร่างกายต่ำ](https://www.sja.org.uk/first-aid-advice/hypothermia/)

เก็บ HTML, SHA256, URL, วันที่ดาวน์โหลด และภาษาไว้ตรวจสอบเช่นเดียวกับข้อมูลเดิม กราฟเชื่อมแมงกะพรุนกับการประเมินเบื้องต้น/CPR และขาดน้ำกับเพลียแดด การเชื่อมเป็นการจัดเส้นทางค้นหลักฐานของโปรเจกต์ ไม่ใช่ข้อวินิจฉัย หัวข้อใหม่ยังไม่ผ่านการให้คะแนนโดยบุคลากรทางการแพทย์

หัวข้อเห็บ ขาดน้ำ ผิวไหม้แดด และตัวเย็นมีคำแปลคำแนะนำภาษาไทยที่จัดทำในโปรเจกต์ (data/outdoor_guidance_th.json) เพื่อช่วย Qwen อ่านหลักฐาน ต้นฉบับอังกฤษยังเก็บไว้แยกกัน คำแปลยังไม่ผ่านการรับรองทางคลินิก การค้นที่ระบุชื่อหัวข้อกลางแจ้งชัดเจนกรองหัวข้อก่อนจัดอันดับ cosine และขยายตามกราฟเฉพาะหัวข้อที่เกี่ยวข้อง

หัวข้อกลางแจ้ง 6 เรื่องใช้ Qwen กับ JSON schema ที่เลือกข้อความจากชุดขั้นตอนภาษาไทยที่อิงต้นฉบับ (data/outdoor_steps_th.json) ระบบเติมขั้นตอนสำคัญที่ตกหล่นและเรียงตามชุดที่กำหนด โดยคงตัวเลข เงื่อนไข และข้อห้าม ไม่ปล่อยให้โมเดลแต่งขั้นตอนใหม่ คำตอบบันทึก generation_mode และ source_completion_applied จึงต้องแยกประเมินจาก RAG รุ่นเดิมที่สร้างข้อความอิสระ ผลทดสอบใหม่เป็น smoke checks ของการทำงาน ไม่ใช่คะแนนความถูกต้องทางคลินิก
