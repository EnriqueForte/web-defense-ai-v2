# Captura accesos Apache desde la salida Docker, sin tocar logs operativos.
$ErrorActionPreference = "Stop"
$stateDir = Join-Path $PSScriptRoot "..\.local-state\dvwa-lab"
$destination = Join-Path $stateDir "access.log"
$temporary = Join-Path $stateDir (".access.log.{0}.tmp" -f [guid]::NewGuid().ToString("N"))

try {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
    # Windows PowerShell puede convertir stderr nativo en un ErrorRecord y,
    # con ErrorActionPreference=Stop, interrumpir aquí aunque docker logs salga
    # correctamente. Capturamos ambos flujos y conservamos solo líneas Apache.
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $dockerOutput = @(& docker logs --timestamps=false web-defense-ai-v2-lab-dvwa 2>&1)
        $dockerExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($dockerExitCode -ne 0) {
        throw "Docker no pudo leer la salida del contenedor. Comprueba que DVWA está iniciado."
    }

    $accessLines = @($dockerOutput | ForEach-Object { "$_" } | Where-Object { $_ -match '^\S+ \S+ \S+ \[[^\]]+\] ' })
    [System.IO.File]::WriteAllLines($temporary, [string[]]$accessLines, [System.Text.UTF8Encoding]::new($false))

    if (Test-Path -LiteralPath $destination -PathType Leaf) {
        Move-Item -LiteralPath $temporary -Destination $destination -Force
    } else {
        Move-Item -LiteralPath $temporary -Destination $destination
    }

    Write-Host "Log de laboratorio capturado en .local-state\dvwa-lab\access.log ($($accessLines.Count) líneas)" -ForegroundColor Green
} catch {
    Write-Error "Error al copiar el log: $($_.Exception.Message)"
    exit 1
} finally {
    if (Test-Path -LiteralPath $temporary) {
        Remove-Item -LiteralPath $temporary -Force
    }
}
