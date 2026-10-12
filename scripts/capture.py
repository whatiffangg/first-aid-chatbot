"""Capture the actual web app replaying saved real conversations, not mockups."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--url",default="http://127.0.0.1:8080");args=parser.parse_args()
    rows=[json.loads(line) for line in (ROOT/"results/answers.jsonl").read_text(encoding="utf-8").splitlines()]
    folder=ROOT/"results/screenshots";folder.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport={"width":1440,"height":1080},device_scale_factor=1)
        for row in rows:
            page.goto(args.url+"/?run="+row["id"]);page.wait_for_function("window.appReady === true");page.wait_for_selector(".message.assistant")
            page.screenshot(path=str(folder/(row["id"]+".png")),full_page=True)
            print(row["id"],flush=True)
        page.goto(args.url);page.wait_for_function("window.appReady === true");page.locator('[data-tab="eval"]').click();page.screenshot(path=str(folder/"evaluation.png"),full_page=True)
        page.locator('[data-tab="graph"]').click();page.screenshot(path=str(folder/"knowledge_graph.png"),full_page=True)
        browser.close()
