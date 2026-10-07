param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("dev", "lint", "typecheck", "build")]
    [string]$Action
)

$ErrorActionPreference = "Stop"
$frontendRoot = Join-Path $PSScriptRoot "..\frontend"

$nodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
$nodeCandidates = @()
if ($nodeCommand) {
    $nodeCandidates += $nodeCommand.Source
}
if ($env:ProgramFiles) {
    $nodeCandidates += Join-Path $env:ProgramFiles "nodejs\node.exe"
}
if ($env:LOCALAPPDATA) {
    $nodeCandidates += Join-Path $env:LOCALAPPDATA "Programs\nodejs\node.exe"
}
if ($env:USERPROFILE) {
    $nodeCandidates += Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
}

$nodePath = $nodeCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $nodePath) {
    throw "No se encontró Node.js 24 o posterior. Instálalo o añade node.exe al PATH y vuelve a abrir VSCode."
}

$nodeVersion = (& $nodePath --version).Trim()
if ($nodeVersion -notmatch '^v?(\d+)\.' -or [int]$Matches[1] -lt 24) {
    throw "Se requiere Node.js 24 o posterior; se encontró '$nodeVersion'."
}

switch ($Action) {
    "dev" {
        $cli = Join-Path $frontendRoot "node_modules\next\dist\bin\next"
        $arguments = @($cli, "dev", "--hostname", "127.0.0.1")
    }
    "lint" {
        $cli = Join-Path $frontendRoot "node_modules\eslint\bin\eslint.js"
        $arguments = @($cli)
    }
    "typecheck" {
        $cli = Join-Path $frontendRoot "node_modules\typescript\bin\tsc"
        $arguments = @($cli, "--noEmit")
    }
    "build" {
        $cli = Join-Path $frontendRoot "node_modules\next\dist\bin\next"
        $arguments = @($cli, "build")
    }
}

if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) {
    throw "No se encontró la herramienta local '$cli'. Instala las dependencias del frontend antes de ejecutar esta tarea."
}

Push-Location $frontendRoot
try {
    & $nodePath @arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
