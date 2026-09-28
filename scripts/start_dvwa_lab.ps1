$ErrorActionPreference = "Stop"
$composeFile = Join-Path $PSScriptRoot "..\compose.lab.yaml"

$dockerInfo = & docker info --format '{{.ServerVersion}}' 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker CLI está instalado, pero el motor de Docker Desktop no responde." -ForegroundColor Red
    Write-Host "Abre Docker Desktop y espera a que indique que el motor está en ejecución." -ForegroundColor Yellow
    Write-Host "Comprueba que usa contenedores Linux (motor WSL 2). Después verifica con: docker info" -ForegroundColor Yellow
    exit 1
}

& docker compose --file $composeFile up --detach
if ($LASTEXITCODE -ne 0) {
    throw "Docker responde, pero Compose no pudo iniciar el laboratorio. Revisa el error anterior y los puertos 4280, 8025 y 1025."
}

Write-Host "DVWA:    http://127.0.0.1:4280" -ForegroundColor Cyan
Write-Host "Mailpit: http://127.0.0.1:8025" -ForegroundColor Cyan
Write-Host "SMTP de pruebas: 127.0.0.1:1025" -ForegroundColor Cyan
Write-Host "Para detenerlo conservando datos: .\scripts\stop_dvwa_lab.ps1" -ForegroundColor Yellow
