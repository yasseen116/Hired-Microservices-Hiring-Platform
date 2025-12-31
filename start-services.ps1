param(
    [switch]$SkipInstall,
    [switch]$SkipStop
)

$ErrorActionPreference = "Stop"

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $baseDir

function Resolve-Python {
    $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonCmd) {
        $pythonCmd = (Get-Command py -ErrorAction SilentlyContinue).Source
        if ($pythonCmd) {
            $pythonCmd = "$pythonCmd -3"
        }
    }
    if (-not $pythonCmd) {
        throw "Python not found. Install Python 3 and ensure it is on PATH."
    }
    return $pythonCmd
}

function Stop-Port {
    param([int]$Port)
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            if ($conn.OwningProcess) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # Ignore stop failures on systems without Get-NetTCPConnection
    }
}

$pythonCmd = Resolve-Python
$venvPython = Join-Path $baseDir ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    & $pythonCmd -m venv (Join-Path $baseDir ".venv")
}

$python = $venvPython

if (-not $SkipStop) {
    Stop-Port 8000
    Stop-Port 8002
    Stop-Port 8003
    Stop-Port 5000
}

if (-not $SkipInstall) {
    & $python -m pip install -r (Join-Path $baseDir "auth-service\auth-service\requirements.txt")
    & $python -m pip install -r (Join-Path $baseDir "job-service\jobs-service\requirements.txt")
    & $python -m pip install -r (Join-Path $baseDir "omar-application-service\requirements.txt")
    & $python -m pip install -r (Join-Path $baseDir "hired-front-end\requirements.txt")
}

$logsDir = Join-Path $env:TEMP "hired-logs"
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

function Start-Uvicorn {
    param(
        [string]$Name,
        [string]$WorkDir,
        [string]$Module,
        [int]$Port,
        [string]$BindHost = "127.0.0.1"
    )
    $logFile = Join-Path $logsDir "$Name.log"
    $errFile = Join-Path $logsDir "$Name-error.log"
    Start-Process -NoNewWindow -FilePath $python `
        -ArgumentList "-m", "uvicorn", $Module, "--host", $BindHost, "--port", $Port, "--reload" `
        -WorkingDirectory $WorkDir `
        -RedirectStandardOutput $logFile `
        -RedirectStandardError $errFile
    Write-Host "* $Name started (port $Port)"
    Write-Host "  Log: $logFile"
}

Start-Uvicorn -Name "job-service" -WorkDir (Join-Path $baseDir "job-service\jobs-service") -Module "main:app" -Port 8000
Start-Uvicorn -Name "auth-service" -WorkDir (Join-Path $baseDir "auth-service\auth-service") -Module "main:app" -Port 8002
Start-Uvicorn -Name "application-service" -WorkDir (Join-Path $baseDir "omar-application-service") -Module "main:app" -Port 8003
Start-Uvicorn -Name "frontend" -WorkDir (Join-Path $baseDir "hired-front-end") -Module "app:app" -Port 5000 -BindHost "0.0.0.0"

Write-Host ""
Write-Host "Frontend:     http://localhost:5000"
Write-Host "Jobs API:     http://localhost:8000/docs"
Write-Host "Auth API:     http://localhost:8002/docs"
Write-Host "Apps API:     http://localhost:8003/docs"

