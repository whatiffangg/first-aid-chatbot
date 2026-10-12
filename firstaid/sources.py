"""Topic aliases enrich retrieval, never act as medical instructions."""
TOPICS = [
 ("primary-survey", "การประเมินเบื้องต้น", "ประเมิน ปฐมพยาบาล DRABC ความปลอดภัย ไม่รู้สึกตัว หายใจ", "all"),
 ("cpr", "CPR ผู้ใหญ่", "กู้ชีพ กดหน้าอก ซีพีอาร์ ผู้ใหญ่ หัวใจหยุดเต้น ไม่หายใจ", "adult"),
 ("how-to-use-a-defibrillator", "เครื่อง AED", "เออีดี เครื่องกระตุกหัวใจ ไฟฟ้า กู้ชีพ", "all"),
 ("recovery-position", "ท่าพักฟื้น", "หมดสติ ไม่รู้สึกตัว หายใจปกติ ท่าพักฟื้น ตะแคง", "adult"),
 ("cuts-and-grazes", "แผลถลอกและแผลเล็ก", "แผลถลอก แผลเล็ก แผลบาด ทำแผล", "all"),
 ("severe-bleeding", "เลือดออกรุนแรง", "ห้ามเลือด เลือดออก แผลฉีกขาด กดแผล", "all"),
 ("shock", "ภาวะช็อก", "ช็อก ตัวเย็น ซีด เสียเลือด เหงื่อ", "all"),
 ("burns-and-scalds", "แผลไหม้น้ำร้อนลวก", "น้ำร้อนลวก แผลไหม้ ไฟไหม้ ผิวหนัง", "all"),
 ("chemical-burn", "แผลไหม้สารเคมี", "สารเคมี กรด ด่าง ผิวหนัง แผลไหม้", "all"),
 ("nosebleed", "เลือดกำเดา", "เลือดกำเดา จมูก เงยหน้า ก้มหน้า", "all"),
 ("fainting", "เป็นลม", "เป็นลม วูบ หน้ามืด", "all"),
 ("fractures-and-broken-bones", "กระดูกหัก", "กระดูกหัก แขนหัก ขาหัก ดาม", "all"),
 ("sprains-and-strains", "ข้อแพลง", "ข้อแพลง ข้อเท้าแพลง เคล็ด บวม", "all"),
 ("choking", "ผู้ใหญ่สำลัก", "สำลัก อุดกั้นทางเดินหายใจ ไอ พูดไม่ได้ ผู้ใหญ่", "adult"),
 ("baby-choking", "ทารกสำลัก", "ทารก เด็กเล็ก ต่ำกว่า 1 ปี สำลัก", "infant"),
 ("child-choking", "เด็กสำลัก", "เด็ก สำลัก อุดกั้นทางเดินหายใจ", "child"),
 ("anaphylaxis", "แพ้รุนแรง", "แพ้รุนแรง แอนาฟิแล็กซิส หายใจลำบาก ลิ้นบวม", "all"),
 ("insect-bites-and-stings", "แมลงต่อย", "ผึ้งต่อย แมลงต่อย เหล็กใน แพ้", "all"),
 ("seizure", "ชัก", "ชัก ลมชัก เกร็ง หมดสติ", "all"),
 ("heatstroke", "ลมแดด", "ลมแดด ฮีทสโตรก ตัวร้อน สับสน อากาศร้อน", "all"),
 ("heat-exhaustion", "เพลียแดด", "เพลียแดด ร้อน เหงื่อ เวียนหัว", "all"),
 ("stroke", "โรคหลอดเลือดสมอง", "สโตรก หน้าเบี้ยว แขนอ่อนแรง พูดไม่ชัด FAST", "all"),
 ("drowning", "จมน้ำ", "จมน้ำ ไม่หายใจ น้ำ กู้ชีพ", "all"),
 ("electrocution", "ไฟฟ้าช็อต", "ไฟฟ้าช็อต ไฟดูด กระแสไฟฟ้า", "all"),
 ("head-injury", "บาดเจ็บศีรษะ", "หัวกระแทก บาดเจ็บศีรษะ ปวดหัว อุบัติเหตุ", "all"),
 ("spinal-injury", "บาดเจ็บกระดูกสันหลัง", "กระดูกสันหลัง คอ อุบัติเหตุ เคลื่อนย้าย", "all"),
 ("poisoning", "ได้รับสารพิษ", "สารพิษ กินน้ำยาล้างห้องน้ำ ยาพิษ อาเจียน", "all"),
 ("asthma-attack", "หอบหืด", "หอบหืด หายใจลำบาก ยาพ่น", "all"),
 ("heart-attack", "หัวใจวาย", "หัวใจวาย เจ็บหน้าอก เหงื่อ หัวใจ", "adult"),
 ("tick-bite", "เห็บกัดระหว่างเดินป่า", "เห็บกัด เห็บติดผิวหนัง ถอนเห็บ เดินป่า แคมป์ปิ้ง", "all"),
 ("dehydration", "ภาวะขาดน้ำ", "ขาดน้ำ กระหายน้ำ ปากแห้ง ปัสสาวะน้อย เดินป่า ท่องเที่ยว", "all"),
 ("sunburn", "ผิวไหม้แดด", "ผิวไหม้แดด แดดเผา ผิวแดง เที่ยวทะเล", "all"),
 ("hypothermia", "อุณหภูมิร่างกายต่ำ", "ตัวเย็น หนาวสั่น อุณหภูมิต่ำ เสื้อเปียก เดินป่า ตั้งแคมป์", "all"),
]

EXTRA_SOURCES = [
 {"id":"jellyfish-stings-thailand", "title_th":"แมงกะพรุนพิษในทะเลไทย", "aliases":"แมงกะพรุน แมงกระพรุน แมงกะพรุนกล่อง หนวด น้ำส้มสายชู เที่ยวทะเล",
  "age_group":"all", "publisher":"กรมควบคุมโรค", "language":"th",
  "url":"https://ddc.moph.go.th/doe/news.php?deptcode=doe&news=21057&news_views=302",
  "extraction_kind":"ddc-jellyfish-guidance", "geographic_scope":"Thailand; suspected venomous jellyfish, especially box jellyfish", "source_published":"2021-10-11"},
 {"id":"snake-bites", "title_th":"งูกัด", "aliases":"งูกัด งูพิษ เดินป่า ขันชะเนาะ ดูดพิษ กรีดแผล",
  "age_group":"all", "publisher":"โรงพยาบาลจุฬาลงกรณ์ สภากาชาดไทย", "language":"th",
  "url":"https://kcmh.chulalongkornhospital.go.th/line/งูกัด/",
  "extraction_kind":"chula-snake-guidance", "geographic_scope":"Thailand", "source_published":"2018-02-21"},
]

# These are documented topic cross-references, not inferred diagnoses or prescriptions.
LINKS = [
 ("seizure", "primary-survey"), ("seizure", "recovery-position"), ("seizure", "cpr"),
 ("severe-bleeding", "shock"), ("shock", "primary-survey"),
 ("insect-bites-and-stings", "anaphylaxis"), ("anaphylaxis", "primary-survey"),
 ("drowning", "cpr"), ("drowning", "primary-survey"),
 ("electrocution", "primary-survey"), ("electrocution", "cpr"),
 ("head-injury", "spinal-injury"), ("spinal-injury", "primary-survey"),
 ("cpr", "how-to-use-a-defibrillator"), ("primary-survey", "recovery-position"),
 ("choking", "cpr"), ("heart-attack", "cpr"),
 ("heatstroke", "primary-survey"), ("poisoning", "primary-survey"),
 ("jellyfish-stings-thailand", "primary-survey"), ("jellyfish-stings-thailand", "cpr"),
 ("snake-bites", "primary-survey"), ("snake-bites", "shock"),
 ("dehydration", "heat-exhaustion"), ("heat-exhaustion", "dehydration"),
 ("sunburn", "heat-exhaustion"), ("hypothermia", "primary-survey"),
]

def source_manifest():
    return [{"id": slug, "title_th": title, "aliases": aliases, "age_group": age,
             "publisher": "St John Ambulance", "language": "en",
             "url": f"https://www.sja.org.uk/first-aid-advice/{slug}/",
             "review_status": "official_source_not_clinically_validated_in_this_project"}
            for slug, title, aliases, age in TOPICS] + [
                {**s,"review_status":"official_source_not_clinically_validated_in_this_project"}
                for s in EXTRA_SOURCES]
