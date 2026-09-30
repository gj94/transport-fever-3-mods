$taskGameRoot = 'D:\SteamLibrary\steamapps\common\Transport Fever 3'
if (-not (Test-Path -LiteralPath (Join-Path $taskGameRoot 'model_editor\ModelEditor.exe'))) {
    throw 'Update taskGameRoot to your Transport Fever 3 installation.'
}
$env:PATH = "$taskGameRoot;$taskGameRoot\model_editor\plugins;$env:PATH"
Start-Process -FilePath (Join-Path $taskGameRoot 'model_editor\ModelEditor.exe') -WorkingDirectory $taskGameRoot -WindowStyle Normal
