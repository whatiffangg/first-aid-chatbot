import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    path=ROOT/'results/summary.json'
    summary=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'groups':[],'averages':[]}
    lines=['| ระบบ | กลุ่ม | จำนวน | คะแนนเฉลี่ย /20 | คะแนน % | Evidence recall | เวลาเฉลี่ย (วินาที) |','|---|---|---:|---:|---:|---:|---:|']
    for g in summary['groups']:
        score=g['mean_score'];lines.append(f"| {g['mode']} | {g['group']} | {g['n']} | {score:.2f} | {score/20*100:.1f} | {g['evidence_recall']:.3f} | {g['mean_seconds']:.1f} |" if score is not None else f"| {g['mode']} | {g['group']} | {g['n']} | ยังไม่ประเมิน | — | {g['evidence_recall']:.3f} | {g['mean_seconds']:.1f} |")
    lines.append('')
    for a in summary['averages']:
        score=a['macro_mean_score'];lines.append(f"- {a['mode']}: ค่าเฉลี่ยสองกลุ่ม {score:.2f}/20 ({score/20*100:.1f}%)" if score is not None else f"- {a['mode']}: ยังไม่มีค่าเฉลี่ยคะแนนคุณภาพครบสองกลุ่ม")
    if len(summary['groups'])==4 and all(g['mean_score'] is not None for g in summary['groups']):
        g=next(x for x in summary['groups'] if x['mode']=='graph' and x['group']=='multihop')
        v=next(x for x in summary['groups'] if x['mode']=='vector' and x['group']=='multihop')
        lines.append(f"\nในการทดลองนี้ กราฟเพิ่มความครอบคลุมหลักฐานคำถามเชื่อมโยงจาก {v['evidence_recall']*100:.1f}% เป็น {g['evidence_recall']*100:.1f}% แต่คะแนนคุณภาพลดจาก {v['mean_score']:.2f} เป็น {g['mean_score']:.2f}/20 จึงยังสรุปไม่ได้ว่ากราฟทำให้ตอบดีขึ้น การเพิ่มบริบทไม่แก้การแปลผิดหรือการละเงื่อนไข ตัวเลขนี้เป็นผลหนึ่งรอบและคะแนน LLM เชิงอัตวิสัย ไม่ใช่ข้อสรุปที่มีนัยสำคัญทางสถิติ")
    grades_path=ROOT/'results/grades.json'
    if grades_path.exists():
        grades=json.loads(grades_path.read_text(encoding='utf-8'));unsafe=[k for k,v in grades.items() if v.get('safety',4)<=1]
        lines.append(f"\nคำตอบที่ได้คะแนน safety ≤1: {len(unsafe)} ข้อ ({', '.join(unsafe) or 'ไม่มี'}) ต้องตรวจข้อผิดพลาดรายข้อ ไม่ใช้คะแนนเฉลี่ยกลบความเสี่ยง")
    if not summary['groups']:lines.append('ยังไม่มีผลการรันจริง ไม่ใส่คะแนนสมมติ')
    template=(ROOT/'docs/report_template.md').read_text(encoding='utf-8')
    index_path=ROOT/'data/index_manifest.json'
    if index_path.exists():
        idx=json.loads(index_path.read_text(encoding='utf-8'))
        lines.insert(0,f"ฐานข้อมูลที่สร้าง: {idx['documents']} เอกสาร, {idx['chunks']} chunks, เวกเตอร์ {idx['vector_dimensions']} มิติ, กราฟ {idx['graph_nodes']} nodes / {idx['graph_edges']} edges\n")
    (ROOT/'docs/report.md').write_text(template.replace('{{RESULTS}}','\n'.join(lines)),encoding='utf-8')
