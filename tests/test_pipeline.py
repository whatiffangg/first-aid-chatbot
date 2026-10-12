from firstaid.ingest import chunk_text, extract_html, build_graph
from firstaid.retrieval import age_constraint
from firstaid.common import ROOT, read_json
import pytest

def test_extraction_excludes_related_articles_and_duplicate_steps():
    html='<h1>First aid</h1><h2>What to do</h2><ol><li><p>'+('Important clinical action. '*20)+'</p></li></ol><p>If you found this article helpful, donate.</p><h2>Related first aid advice</h2><p>Unrelated topic that should never be indexed.</p>'
    text=extract_html(html)
    assert text.count('Important clinical action.')==20
    assert 'Unrelated' not in text and 'donate' not in text

def test_chunk_coverage_and_configuration():
    text=' '.join(f'word{i}' for i in range(500))
    parts=chunk_text(text,100,20)
    assert set(text.split())==set(' '.join(parts).split())
    with pytest.raises(ValueError):chunk_text(text,20,20)

def test_age_filters_prevent_infant_adult_mixup():
    assert age_constraint('ทารก 8 เดือนสำลัก')=='infant'
    assert age_constraint('ผู้ใหญ่สำลัก')=='adult'
    assert age_constraint('เด็กสำลัก')=='child'
    assert age_constraint('คนสำลัก') is None

def test_gold_groups_and_linked_evidence_are_explicit():
    rows=read_json(ROOT/'evaluation/test_questions.json')
    assert len({q['id'] for q in rows})==len(rows)
    for group in ['direct','multihop']:assert sum(q['group']==group for q in rows)==10
    assert all(len(q['required_documents'])>=2 for q in rows if q['group']=='multihop')
    docs=read_json(ROOT/'data/documents.json')
    ids={d['id'] for d in docs}
    assert all(set(q['required_documents'])<=ids for q in rows)

def test_real_corpus_has_no_related_footer_or_replacement_characters():
    docs=read_json(ROOT/'data/documents.json')
    assert len(docs)==35
    assert all('Related first aid advice' not in d['text'] and '\ufffd' not in d['text'] for d in docs)

def test_guidance_graph_preserves_source_and_conditions():
    import networkx as nx
    from firstaid.common import DATA
    graph=nx.node_link_graph(read_json(DATA/'knowledge_graph.json'))
    guidance=[n for n,d in graph.nodes(data=True) if d['type'] in ['Sign','GuidanceStep','Contraindication']]
    assert len(guidance)>100
    for node in guidance:
        data=graph.nodes[node]
        assert data['text'] and data['document_id']
        assert any(edge['relation']=='FROM_SOURCE' for _,_,edge in graph.out_edges(node,data=True))

def test_thai_outdoor_sources_retain_important_contraindications():
    docs={d['id']:d for d in read_json(ROOT/'data/documents.json')}
    jelly=docs['jellyfish-stings-thailand']
    assert jelly['publisher']=='กรมควบคุมโรค' and jelly['language']=='th'
    assert all(term in jelly['text'] for term in ['30 วินาที','ห้ามราดด้วยน้ำจืด','1669'])
    snake=docs['snake-bites']
    assert 'ห้าม!' in snake['text'] and 'กรีด/ดูด/พอกแผล' in snake['text']
    for topic in ['tick-bite','dehydration','sunburn','hypothermia']:
        assert docs[topic]['guidance_th']
        assert docs[topic]['translation_status']=='project_translation_not_clinically_validated'
