$ErrorActionPreference='Stop'
$projRoot=Split-Path -Parent $PSScriptRoot
foreach ($port in @(8090,8091)) {
  $pidFile=Join-Path $projRoot "runtime/server-$port.pid"
  if (Test-Path -LiteralPath $pidFile) {
    $modelPid=[int](Get-Content -LiteralPath $pidFile)
    $process=Get-Process -Id $modelPid -ErrorAction SilentlyContinue
    if ($process -and $process.Path -and $process.Path.StartsWith((Join-Path $projRoot 'runtime'),[System.StringComparison]::OrdinalIgnoreCase)) { Stop-Process -Id $modelPid }
  }
}
