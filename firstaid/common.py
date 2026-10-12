import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
def config():
    return read_json(ROOT / "config.json")
