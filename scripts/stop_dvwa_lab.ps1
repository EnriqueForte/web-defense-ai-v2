$ErrorActionPreference = "Stop"
$composeFile = Join-Path $PSScriptRoot "..\compose.lab.yaml"

& docker compose --file $composeFile stop
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo detener el laboratorio DVWA."
}

Write-Host "Laboratorio detenido. Los contenedores y la base DVWA se conservan; captura los logs antes de eliminarlos." -ForegroundColor Green
