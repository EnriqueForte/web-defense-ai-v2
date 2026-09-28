$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "No se encontró el intérprete del proyecto: $python"
}

Push-Location $repoRoot
try {
    & $python -B -m dashboard.services.dvwa_lab_capture
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo capturar el log del laboratorio DVWA. Comprueba que Docker y el contenedor están activos."
    }
}
finally {
    Pop-Location
}
