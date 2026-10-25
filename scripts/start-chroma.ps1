param([string]$SharedRoot = $env:SHARED_CHROMA_ROOT)
$ErrorActionPreference = 'Stop'
# Reuse the separately managed shared service. Never allocate another port/store.
if (-not $SharedRoot) {
    $projectRoot = Split-Path $PSScriptRoot -Parent
    $SharedRoot = Join-Path (Split-Path $projectRoot -Parent) 'chroma db'
}
$sharedStart = Join-Path ([System.IO.Path]::GetFullPath($SharedRoot)) 'start-shared.ps1'
if (-not (Test-Path -LiteralPath $sharedStart -PathType Leaf)) {
    throw 'Shared Chroma launcher is missing. Set SHARED_CHROMA_ROOT to the existing shared service directory. See docs/SHARED_CHROMA.md. No replacement instance will be created.'
}
& $sharedStart
