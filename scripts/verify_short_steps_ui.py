"""Verify a real Ollama answer and the frontend wait deadline."""
import json
from pathlib import Path
import re
import time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={"width":1440,"height":1080})
    page.goto('http://127.0.0.1:8081')
    page.wait_for_function('window.appReady===true')
    page.locator('#question').fill('เลือดกำเดาไหลควรทำอย่างไร?')
    started=time.perf_counter();page.locator('#send').click()
    page.wait_for_selector('.message.assistant',timeout=110000)
    answer=page.locator('.message.assistant .answer').inner_text()
    print(answer,flush=True)
    assert re.match(r'1\.',answer)
    assert 1<=len(re.findall(r'^\d\.',answer,re.M))<=5
    assert '1669' in answer and 'Okay' not in answer
    assert not page.locator('#send').is_disabled()
    seconds=round(time.perf_counter()-started,2)
    page.screenshot(path=str(ROOT/'results/screenshots/ollama_short_steps.png'),full_page=True)
    check=browser.new_page()
    check.add_init_script("""const actualFetch=window.fetch.bind(window);
      window.fetch=(url,options)=>url==='/api/chat'?new Promise((resolve,reject)=>{
      options.signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')))
      }):actualFetch(url,options);""")
    check.clock.install()
    check.goto('http://127.0.0.1:8081');check.wait_for_function('window.appReady===true')
    check.locator('#question').fill('ทดสอบการหมดเวลารอ');check.locator('#send').click()
    check.clock.fast_forward(100001)
    check.locator('.error').wait_for()
    assert '100 วินาที' in check.locator('.error').inner_text()
    assert not check.locator('#send').is_disabled()
    data={'model':'firstaid-qwen','seconds':seconds,'answer':answer,
          'real_thai_steps':'passed','no_thinking_output':'passed','send_button_reset':'passed',
          'ui_timeout':'passed (mocked delayed fetch and accelerated browser clock)'}
    (ROOT/'results/short_steps_ui_check.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('UI seconds:',seconds,'; timeout/reset passed',flush=True)
    browser.close()
