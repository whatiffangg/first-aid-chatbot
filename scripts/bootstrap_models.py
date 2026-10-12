"""Download official Qwen weights and a portable llama.cpp runtime locally."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def download(url, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f"Already exists: {target.name}", flush=True)
        return
    temp = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as src, temp.open("wb") as dst:
        total = int(src.headers.get("Content-Length", 0)); count = 0; last = 0
        while block := src.read(2**20):
            dst.write(block); count += len(block)
            if count - last > 100 * 2**20:
                print(f"{target.name}: {count // 2**20}/{total // 2**20} MB", flush=True); last = count
    temp.replace(target)
    print(f"Downloaded {target.name}", flush=True)

if __name__ == "__main__":
    releases = json.load(urllib.request.urlopen("https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=5"))
    release, asset = next((r, a) for r in releases for a in r["assets"] if a["name"].endswith("bin-win-cpu-x64.zip"))
    jobs = [(asset["browser_download_url"], ROOT / "runtime/llama.zip")]
    jobs.append(("https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/main/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", ROOT / "models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf"))
    for name in ["Qwen3-Embedding-0.6B"]:
        filename = name + "-Q8_0.gguf"
        jobs.append((f"https://huggingface.co/Qwen/{name}-GGUF/resolve/main/{filename}", ROOT / "models" / filename))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(lambda x: download(*x), jobs))
    with zipfile.ZipFile(ROOT / "runtime/llama.zip") as archive:
        archive.extractall(ROOT / "runtime/llama")
    manifest = {"runtime_release": release["tag_name"], "files": []}
    for url, path in jobs:
        digest = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
        manifest["files"].append({"url": url, "file": str(path.relative_to(ROOT)), "sha256": digest, "bytes": path.stat().st_size})
    (ROOT / "models/manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
