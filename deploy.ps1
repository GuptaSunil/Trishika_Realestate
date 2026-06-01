Param(
  [switch]$NoTests
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

if (-not (Test-Path .venv)) {
  python -m venv .venv
}

$activate = Join-Path .venv "Scripts\Activate.ps1"
. $activate

python -m pip install --upgrade pip
if (Test-Path requirements.txt) {
  pip install -r requirements.txt
}

if (-not $NoTests) {
  if (Get-Command pytest -ErrorAction SilentlyContinue) {
    pytest
  }
}

if (Get-Command gunicorn -ErrorAction SilentlyContinue) {
  gunicorn -w 4 -b 0.0.0.0:8000 main:app
} else {
  python main.py
}
