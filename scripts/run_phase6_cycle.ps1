$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$logPath = Join-Path $repoRoot ".local-state\dvwa-lab\access.log"
$pilotRoot = Join-Path $repoRoot ".local-state\phase6-pilot"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "No se encontró el intérprete del proyecto: $python"
}
if (-not (Test-Path -LiteralPath $logPath -PathType Leaf)) {
    throw "Falta la captura del laboratorio. Inicia DVWA y ejecuta scripts/sync_dvwa_lab_logs.ps1."
}
if (-not (Test-NetConnection 127.0.0.1 -Port 1025 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    throw "Mailpit no responde en 127.0.0.1:1025. Inicia el laboratorio DVWA/Mailpit primero."
}

New-Item -ItemType Directory -Path (Join-Path $pilotRoot "reports") -Force | Out-Null

# Aislar captura, reporte e historial del piloto; no tocar los datos habituales.
$env:LOG_PATH = $logPath
$env:LOG_SYNC_SOURCE = "dvwa-lab"
$env:LLM_MODEL = if ($env:LLM_MODEL) { $env:LLM_MODEL } else { "groq/openai/gpt-oss-120b" }
$env:LLM_FALLBACK_MODELS = if ($env:LLM_FALLBACK_MODELS) { $env:LLM_FALLBACK_MODELS } else { "groq/openai/gpt-oss-20b" }
$env:REPORT_PATH = Join-Path $pilotRoot "reports"
$env:ENGINE_DIAGNOSTICS_DIR = Join-Path $pilotRoot "diagnostics"
$env:ANALYSIS_DB_PATH = Join-Path $pilotRoot "analysis.sqlite3"
$env:INTERVALO_MINUTOS = "1440"
$env:ANALYSIS_MANUAL_ENABLED = "0"
$env:NEXT_PRIMARY_ENABLED = "0"

# El ciclo solo puede notificar por SMTP local a Mailpit; Telegram no participa.
$env:NOTIFICATION_DESTINATIONS = "email"
$env:TELEGRAM_BOT_TOKEN = ""
$env:TELEGRAM_CHAT_ID = ""
$env:EMAIL_REMITENTE = "web-defense-ai-v2-lab@example.test"
$env:EMAIL_PASSWORD = ""
$env:EMAIL_DESTINATARIO = "security-lab@example.test"
$env:EMAIL_SMTP_SERVER = "127.0.0.1"
$env:EMAIL_SMTP_PORT = "1025"
$env:EMAIL_SMTP_STARTTLS = "0"

Write-Host "Se ejecutará un único ciclo con el proveedor LLM configurado localmente." -ForegroundColor Yellow
Write-Host "Reportes y SQLite quedan aislados en .local-state\phase6-pilot; las alertas van solo a Mailpit." -ForegroundColor Cyan

Push-Location $repoRoot
try {
    & $python -B pipeline.py --once
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
