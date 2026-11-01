$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$env:PYTHONPATH = Join-Path $projectRoot 'src'
& (Join-Path $projectRoot '.venv/Scripts/python.exe') -m placement_system.init_db
