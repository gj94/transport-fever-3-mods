param(
    [Parameter(Mandatory=$true)][string]$LocalRoot,
    [string]$BackupRoot = 'D:\TF3Mods'
)
$ErrorActionPreference = 'Stop'
$taskRepo = Split-Path -Parent $PSScriptRoot
$taskSource = Join-Path $taskRepo 'game_build\gj94_indian_rail_pack'
if (-not (Test-Path -LiteralPath (Join-Path $taskSource 'mod.json'))) { throw 'Build the mod first.' }
$taskManifest = Get-Content -Raw -LiteralPath (Join-Path $taskSource 'mod.json') | ConvertFrom-Json
if ($taskManifest.modId -ne 'gj94_indian_rail_pack') { throw 'Unexpected source mod ID.' }
if (Get-Process -Name TransportFever3 -ErrorAction SilentlyContinue) { throw 'Save and exit TF3 before installing.' }
$taskSource = (Resolve-Path -LiteralPath $taskSource).Path
$taskLocal = (Resolve-Path -LiteralPath $LocalRoot).Path
$taskStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
foreach ($taskArea in @('mods','staging_area')) {
    $taskDestination = Join-Path $taskLocal "$taskArea\gj94_indian_rail_pack"
    if (Test-Path -LiteralPath $taskDestination) {
        $taskInstalled = Get-Content -Raw -LiteralPath (Join-Path $taskDestination 'mod.json') | ConvertFrom-Json
        if ($taskInstalled.modId -ne $taskManifest.modId) { throw 'Unexpected installed mod ID.' }
        $taskBackup = Join-Path $BackupRoot "Indian-Rail-Prototype-Pack-before-Vande-Bharat-$taskArea-$taskStamp.zip"
        Compress-Archive -LiteralPath $taskDestination -DestinationPath $taskBackup -CompressionLevel Optimal
        Write-Output "Backup: $taskBackup"
    } else {
        New-Item -ItemType Directory -Path $taskDestination -Force | Out-Null
    }
    Get-ChildItem -LiteralPath $taskSource -Force | Copy-Item -Destination $taskDestination -Recurse -Force
    foreach ($taskFile in Get-ChildItem -LiteralPath $taskSource -File -Recurse) {
        $taskRelative = $taskFile.FullName.Substring($taskSource.Length + 1)
        $taskCopied = Join-Path $taskDestination $taskRelative
        if ((Get-FileHash -LiteralPath $taskFile.FullName).Hash -ne (Get-FileHash -LiteralPath $taskCopied).Hash) {
            throw "Installed file differs: $taskRelative"
        }
    }
    Write-Output "Installed and verified revision $($taskManifest.revision): $taskDestination"
}
