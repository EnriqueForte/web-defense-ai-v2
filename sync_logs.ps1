# Sincroniza el log de DVWA y solo publica la copia si Docker termina correctamente.
$ErrorActionPreference = "Stop"
$logDir = Join-Path $PSScriptRoot "logs"
$destino = Join-Path $logDir "access.log"
$temporal = Join-Path $logDir (".access.log.{0}.tmp" -f [guid]::NewGuid().ToString("N"))

try {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    Write-Host "Sincronizando logs desde DVWA..." -ForegroundColor Cyan
    & docker cp "dvwa-app:/var/log/apache2/access.log" $temporal
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $temporal -PathType Leaf)) {
        throw "Docker no pudo crear la copia temporal del access.log."
    }

    if (Test-Path -LiteralPath $destino -PathType Leaf) {
        [System.IO.File]::Replace($temporal, $destino, $null)
    } else {
        [System.IO.File]::Move($temporal, $destino)
    }
    $lineas = (Get-Content -LiteralPath $destino).Count
    Write-Host "Log sincronizado: $lineas líneas" -ForegroundColor Green
} catch {
    Write-Error "Error al sincronizar el log: $($_.Exception.Message)"
    exit 1
} finally {
    if (Test-Path -LiteralPath $temporal) {
        Remove-Item -LiteralPath $temporal -Force
    }
}
