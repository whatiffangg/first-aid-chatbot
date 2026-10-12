"""Optional NVIDIA CUDA runtime; keep CPU runtime as a fallback."""
import concurrent.futures
import json
import urllib.request
import zipfile
from bootstrap_models import ROOT, download
if __name__=='__main__':
    releases=json.load(urllib.request.urlopen('https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=5'))
    candidates=[(r,a) for r in releases for a in r['assets'] if a['name'].endswith('bin-win-cuda-13.4-x64.zip') and a['name'].startswith('llama-')]
    release,asset=candidates[0]
    cudart=next(a for a in release['assets'] if a['name']=='cudart-llama-bin-win-cuda-13.4-x64.zip')
    jobs=[(asset['browser_download_url'],ROOT/'runtime/llama-cuda.zip'),(cudart['browser_download_url'],ROOT/'runtime/cudart.zip')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda x:download(*x),jobs))
    for _,path in jobs:
        with zipfile.ZipFile(path) as archive:archive.extractall(ROOT/'runtime/llama-cuda')
