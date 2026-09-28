param(
    [ValidateRange(1, 48)]
    [int]$DurationHours = 24,
    [ValidateRange(30, 3600)]
    [int]$IntervalSeconds = 300
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$observationDir = Join-Path $repoRoot '.local-state\phase6-pilot\observation'
New-Item -ItemType Directory -Path $observationDir -Force | Out-Null
$recordsPath = Join-Path $observationDir 'health.jsonl'
$summaryPath = Join-Path $observationDir 'summary.json'
$startedAt = [DateTimeOffset]::UtcNow
$deadline = $startedAt.AddHours($DurationHours)
$sampleCount = 0
$failureCount = 0
$encoding = [System.Text.UTF8Encoding]::new($false)

function Get-HttpStatus([string]$Uri) {
    try {
        $response = Invoke-WebRequest -Uri $Uri -TimeoutSec 10 -UseBasicParsing
        return [int]$response.StatusCode
    }
    catch {
        if ($_.Exception.Response) {
            return [int]$_.Exception.Response.StatusCode
        }
        return 0
    }
}

function Get-ContainerStatus([string]$Name) {
    $value = & docker inspect --format '{{.State.Status}}' $Name 2>$null
    if ($LASTEXITCODE -ne 0) { return 'unavailable' }
    return [string]$value
}

function Get-DatabaseHealth([string]$Name) {
    $value = & docker inspect --format '{{.State.Health.Status}}' $Name 2>$null
    if ($LASTEXITCODE -ne 0) { return 'unavailable' }
    return [string]$value
}

while ([DateTimeOffset]::UtcNow -lt $deadline) {
    $flaskHealth = 'unavailable'
    $nextHealth = 'unavailable'
    try {
        $flaskHealth = [string](Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/v1/salud' -TimeoutSec 10).data.status
    }
    catch { }
    try {
        $nextHealth = [string](Invoke-RestMethod -Uri 'http://127.0.0.1:3000/api/v1/salud' -TimeoutSec 10).data.status
    }
    catch { }

    $dvwaHttp = Get-HttpStatus 'http://127.0.0.1:4280/'
    $mailpitHttp = Get-HttpStatus 'http://127.0.0.1:8025/api/v1/messages'
    $smtp = $false
    try { $smtp = [bool](Test-NetConnection 127.0.0.1 -Port 1025 -InformationLevel Quiet -WarningAction SilentlyContinue) }
    catch { }

    $dvwaContainer = Get-ContainerStatus 'web-defense-ai-v2-lab-dvwa'
    $databaseContainer = Get-ContainerStatus 'web-defense-ai-v2-lab-dvwa-db-1'
    $databaseHealth = Get-DatabaseHealth 'web-defense-ai-v2-lab-dvwa-db-1'
    $mailpitContainer = Get-ContainerStatus 'web-defense-ai-v2-lab-mailpit-1'
    $ok = ($flaskHealth -eq 'ok' -and $nextHealth -eq 'ok' -and
           $dvwaHttp -eq 200 -and $mailpitHttp -eq 200 -and $smtp -and
           $dvwaContainer -eq 'running' -and $databaseContainer -eq 'running' -and
           $databaseHealth -eq 'healthy' -and $mailpitContainer -eq 'running')
    $record = [ordered]@{
        timestamp_utc = [DateTimeOffset]::UtcNow.ToString('o')
        ok = $ok
        flask_api = $flaskHealth
        next_api = $nextHealth
        dvwa_http = $dvwaHttp
        mailpit_http = $mailpitHttp
        mailpit_smtp = $smtp
        dvwa_container = $dvwaContainer
        database_container = $databaseContainer
        database_health = $databaseHealth
        mailpit_container = $mailpitContainer
    }
    [System.IO.File]::AppendAllText($recordsPath, (($record | ConvertTo-Json -Compress) + [Environment]::NewLine), $encoding)
    $sampleCount++
    if (-not $ok) { $failureCount++ }

    $remaining = ($deadline - [DateTimeOffset]::UtcNow).TotalSeconds
    if ($remaining -le 0) { break }
    Start-Sleep -Seconds ([Math]::Min($IntervalSeconds, [Math]::Ceiling($remaining)))
}

$summary = [ordered]@{
    started_at_utc = $startedAt.ToString('o')
    finished_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    duration_hours = $DurationHours
    interval_seconds = $IntervalSeconds
    samples = $sampleCount
    failed_samples = $failureCount
    complete = ([DateTimeOffset]::UtcNow -ge $deadline)
}
[System.IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 3), $encoding)
$summary | ConvertTo-Json -Compress
