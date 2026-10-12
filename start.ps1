param([switch]$SkipModels)
$ErrorActionPreference='Stop'
$projRoot=$PSScriptRoot
Set-Location -LiteralPath $projRoot
$pythonExe=Join-Path $projRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $pythonExe)) { throw 'สร้าง .venv และติดตั้ง requirements.txt ก่อน ดู README.md' }
if (!$SkipModels) {
  $serverExe=Join-Path $projRoot 'runtime/llama/llama-server.exe'
  $chatServerExe=$serverExe
  $cudaServerExe=Join-Path $projRoot 'runtime/llama-cuda/llama-server.exe'
  if (Test-Path -LiteralPath $cudaServerExe) { $chatServerExe=$cudaServerExe }
  if (!(Test-Path -LiteralPath $serverExe)) { throw 'รัน python scripts/bootstrap_models.py ก่อน' }
  foreach ($port in @(8090,8091)) {
    try { Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -TimeoutSec 2 | Out-Null; continue } catch {}
    if ($port -eq 8090) {
      $serverArgs=@('-m','models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf','--port','8090','--host','127.0.0.1','-c','8192','-t','8','--alias','Qwen3-4B-Instruct-2507','--jinja')
      $launchExe=$chatServerExe
      if ($chatServerExe -eq $cudaServerExe) { $serverArgs+=@('-ngl','99') }
    } else {
      $serverArgs=@('-m','models/Qwen3-Embedding-0.6B-Q8_0.gguf','--port','8091','--host','127.0.0.1','-c','8192','-b','8192','-ub','2048','-t','4','--embedding','--pooling','last','--alias','Qwen3-Embedding-0.6B')
      $launchExe=$serverExe
    }
    $process=Start-Process -FilePath $launchExe -ArgumentList $serverArgs -WorkingDirectory $projRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput "runtime/server-$port.stdout.log" -RedirectStandardError "runtime/server-$port.stderr.log"
    Set-Content -LiteralPath "runtime/server-$port.pid" -Value $process.Id
  }
  for ($attempt=0;$attempt -lt 90;$attempt++) {
    try { Invoke-RestMethod 'http://127.0.0.1:8090/health' -TimeoutSec 2 | Out-Null; Invoke-RestMethod 'http://127.0.0.1:8091/health' -TimeoutSec 2 | Out-Null; break } catch { Start-Sleep -Seconds 2 }
  }
}
if (!(Test-Path -LiteralPath 'data/index_manifest.json')) { & $pythonExe -m firstaid.ingest; if ($LASTEXITCODE -ne 0) { throw 'นำเข้าข้อมูลไม่สำเร็จ' } }
Write-Host 'เปิด http://127.0.0.1:8080 — กด Ctrl+C เพื่อหยุดเว็บ'
& $pythonExe -m uvicorn firstaid.server:app --host 127.0.0.1 --port 8080
