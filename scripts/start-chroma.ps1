$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$settings = (& $pythonPath -c "import json; from backend.app.config import Settings; s=Settings.from_env(); print(json.dumps({'mode':s.chroma_mode,'host':s.chroma_host,'port':s.chroma_port}))") | ConvertFrom-Json
if ($settings.mode -ne 'http') { Write-Output 'Embedded Chroma selected.'; return }
$endpoint = "http://$($settings.host):$($settings.port)/api/v2/heartbeat"
try { $heartbeat = Invoke-RestMethod $endpoint -TimeoutSec 2; if ($heartbeat.'nanosecond heartbeat') { Write-Output "Chroma is ready at $endpoint"; return } } catch {}
if ($settings.host -notin @('127.0.0.1','localhost') -or $settings.port -ne 8082) { throw 'Configured external Chroma is unavailable; automatic startup is limited to this project on port 8082.' }
if (Get-NetTCPConnection -LocalPort 8082 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 8082 is occupied by another service.' }
$logDirectory = Join-Path $projectRoot 'runtime\logs'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$chroma = Start-Process -FilePath (Join-Path $projectRoot '.venv\Scripts\chroma.exe') -ArgumentList 'run','--path','runtime/chroma-server','--host','127.0.0.1','--port','8082' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory "chroma-$stamp.out.log") -RedirectStandardError (Join-Path $logDirectory "chroma-$stamp.err.log") -PassThru
for ($attempt=0; $attempt -lt 10; $attempt++) {
    Start-Sleep -Seconds 1
    try { $heartbeat = Invoke-RestMethod $endpoint -TimeoutSec 1; if ($heartbeat.'nanosecond heartbeat') { Write-Output "Project Chroma ready; launcher PID $($chroma.Id)"; return } } catch {}
}
throw 'Chroma did not become ready; inspect runtime/logs/chroma-*.'
