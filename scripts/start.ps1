$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create a virtual environment and install requirements.txt first.' }
& $pythonPath -m scripts.configure_access
if ($LASTEXITCODE -ne 0) { throw 'Could not configure API authentication.' }
$logDirectory = Join-Path $projectRoot 'runtime\logs'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
& (Join-Path $PSScriptRoot 'start-chroma.ps1')
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$api = Start-Process -FilePath $pythonPath -ArgumentList '-m','scripts.serve' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory "api-$stamp.out.log") -RedirectStandardError (Join-Path $logDirectory "api-$stamp.err.log") -PassThru
$npmPath = (Get-Command npm.cmd).Source
$web = Start-Process -FilePath $npmPath -ArgumentList 'run','dev' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory "web-$stamp.out.log") -RedirectStandardError (Join-Path $logDirectory "web-$stamp.err.log") -PassThru
@{api_pid=$api.Id; frontend_pid=$web.Id; dashboard='http://127.0.0.1:5180'; api='http://127.0.0.1:8010'; logs=$logDirectory} | ConvertTo-Json
