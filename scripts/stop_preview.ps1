# scripts/stop_preview.ps1
$PSScriptRoot_ = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Workspace = Split-Path -Parent $PSScriptRoot_

python "$Workspace\scripts\stop_preview.py"
