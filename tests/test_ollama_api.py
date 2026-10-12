from unittest.mock import Mock, patch
import pytest
from firstaid_ollama import OllamaChat, FirstAid, create_app, localize_emergency_phone

def response(body, status=200):
    r=Mock();r.status_code=status;r.json.return_value=body;return r

def test_cloud_key_goes_only_in_bearer_header():
    client=OllamaChat('https://ollama.com','test-model','test-only-token')
    with patch('firstaid_ollama.requests.post',return_value=response({'message':{'content':'พร้อม'},'done_reason':'stop'})) as post:
        assert client.call([{'role':'user','content':'test'}])['answer']=='พร้อม'
        args,kwargs=post.call_args
        assert args[0]=='https://ollama.com/api/chat'
        assert kwargs['headers']['Authorization']=='Bearer test-only-token'
        assert kwargs['allow_redirects'] is False
        assert 'test-only-token' not in str(kwargs['json'])

def test_local_ollama_does_not_receive_cloud_key():
    with patch('firstaid_ollama.requests.post',return_value=response({'message':{'content':'ready'}})) as post:
        OllamaChat('http://127.0.0.1:11434','qwen3:4b','test-only-token').call([])
        assert 'Authorization' not in post.call_args.kwargs['headers']

def test_untrusted_hosts_and_http_cloud_are_rejected():
    with pytest.raises(ValueError):OllamaChat('https://example.com','qwen','test-only-token')
    with pytest.raises(ValueError):OllamaChat('http://ollama.com','qwen','test-only-token')

def test_retired_model_reports_failure_and_redacts_key():
    client=OllamaChat('https://ollama.com','retired-model','test-only-token')
    with patch('firstaid_ollama.requests.post',return_value=response({'error':'retired test-only-token'},410)):
        with pytest.raises(RuntimeError) as exc:client.call([])
        assert '410' in str(exc.value)
        assert 'test-only-token' not in str(exc.value)

def test_model_timeout_has_an_actionable_message():
    import requests
    with patch('firstaid_ollama.requests.post',side_effect=requests.ReadTimeout):
        with pytest.raises(RuntimeError,match='90 วินาที'):
            OllamaChat('http://127.0.0.1:11434','firstaid-qwen').call([])

def test_unfinished_thinking_is_not_displayed_as_an_answer():
    with patch('firstaid_ollama.requests.post',return_value=response({'message':{'content':"Okay, let's tackle this question..."},'done_reason':'length'})):
        with pytest.raises(RuntimeError,match='คิดวิเคราะห์'):
            OllamaChat('http://127.0.0.1:11434','qwen3:4b').call([])

def test_only_final_answer_is_returned_after_thinking_close():
    with patch('firstaid_ollama.requests.post',return_value=response({'message':{'content':'hidden reasoning</think>\n1. คำตอบสั้น'},'done_reason':'stop'})):
        result=OllamaChat('http://127.0.0.1:11434','firstaid-qwen').call([])
        assert result['answer']=='1. คำตอบสั้น'

def test_thai_emergency_numbers_do_not_change_measurements():
    assert localize_emergency_phone('โทร 999 หรือ 112 ทันที')=='โทร 1669 ทันที'
    assert localize_emergency_phone('ความดัน 112 และอุณหภูมิ 39')=='ความดัน 112 และอุณหภูมิ 39'

def test_structured_steps_have_valid_references(tmp_path):
    engine=FirstAid(tmp_path,OllamaChat('http://127.0.0.1:11434','firstaid-qwen'))
    try:
        with patch.object(engine.chat,'call',return_value={'answer':'{"steps":[{"text":"คำตอบสั้น","sources":[1]}],"seek_help":{"text":"โทร 999 หากอาการรุนแรง","sources":[1]}}','model':'firstaid-qwen','finish_reason':'stop'}):
            result=engine.answer('เลือดกำเดาไหล')
            assert result['answer']=='1. คำตอบสั้น [S1]\n2. โทร 1669 หากอาการรุนแรง [S1]'
        with patch.object(engine.chat,'call',return_value={'answer':'{"steps":[{"text":"คำตอบสั้น","sources":[999]}],"seek_help":null}','model':'firstaid-qwen','finish_reason':'stop'}):
            with pytest.raises(RuntimeError,match='ขั้นตอนไม่ครบ'):
                engine.answer('เลือดกำเดาไหล')
    finally:engine.close()

def test_single_file_database_retrieves_real_sources_and_graph(tmp_path):
    engine=FirstAid(tmp_path,OllamaChat('http://127.0.0.1:11434','qwen3:4b'))
    try:
        contexts,paths=engine.retrieve('ผู้ใหญ่เลือดกำเดาไหล',mode='graph')
        assert 'nosebleed' in {c['document_id'] for c in contexts}
        assert all(c['source_url'].startswith('https://') for c in contexts)
        assert engine.info['chunks']==81 and engine.info['graph_nodes']==649
        from fastapi.testclient import TestClient
        with TestClient(create_app(engine)) as client:
            assert client.get('/api/status').json()['ready'] is True
            assert 'qwen3:4b · Ollama ในเครื่อง' in client.get('/').text
            assert client.post('/api/chat',json={'question':'x','mode':'graph','k':5}).status_code==422
    finally:engine.close()

def test_explicit_outdoor_topics_exclude_unrelated_vector_evidence(tmp_path):
    engine=FirstAid(tmp_path,OllamaChat('http://127.0.0.1:11434','firstaid-qwen'))
    try:
        cases={'แมงกะพรุน':'jellyfish-stings-thailand','งูกัด':'snake-bites',
               'เห็บติดผิวหนัง':'tick-bite','ขาดน้ำ':'dehydration',
               'ผิวไหม้แดด':'sunburn','เสื้อเปียกและหนาวสั่น':'hypothermia'}
        for question,expected in cases.items():
            contexts,_=engine.retrieve(question,mode='vector')
            assert contexts and {c['document_id'] for c in contexts}=={expected}
        contexts,paths=engine.retrieve('โดนแมงกะพรุน',mode='graph')
        assert 'cpr' in {c['document_id'] for c in contexts}
        assert paths
    finally:engine.close()

def test_outdoor_source_completion_preserves_tick_timing(tmp_path):
    engine=FirstAid(tmp_path,OllamaChat('http://127.0.0.1:11434','firstaid-qwen'))
    try:
        with patch.object(engine.chat,'call',return_value={'answer':'{"steps":[{"text":"ดึงเห็บแรง ๆ","sources":[1]}],"seek_help":null}','model':'firstaid-qwen','finish_reason':'stop'}):
            result=engine.answer('เห็บกัดต้องทำอย่างไร?')
            assert 'ภายใน 3 เดือน' in result['answer']
            assert 'หลัง 3 เดือน' not in result['answer']
            assert 'ดึงเห็บแรง' not in result['answer']
            assert 'ใช้แหนบ' in result['answer'] and 'ห้ามกระชาก' in result['answer']
            assert result['generation_mode']=='qwen_constrained_source_steps'
            assert result['source_completion_applied'] is True
    finally:engine.close()
