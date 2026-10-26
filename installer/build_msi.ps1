param(
    [string]$Version = "0.1.1",
    [string]$DistDir = "dist",
    [string]$OutputDir = "output"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building MSI Installer for Aayush's DevKit v$Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Ensure output directory exists
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$MsiOutput = Join-Path $OutputDir "AayushsDevKit-v$Version-x64.msi"
$SourceDir = (Resolve-Path $DistDir).Path

# Check for WiX v4 (wix.exe)
$wixV4 = Get-Command "wix" -ErrorAction SilentlyContinue

# Check for WiX v3 (candle.exe and light.exe)
$candle = Get-Command "candle.exe" -ErrorAction SilentlyContinue
$light = Get-Command "light.exe" -ErrorAction SilentlyContinue

if ($wixV4) {
    Write-Host "Using WiX v4 CLI to build MSI..." -ForegroundColor Green
    & wix build "installer\devkit.wxs" `
        -d Version=$Version `
        -d SourceDir=$SourceDir `
        -o $MsiOutput
} elseif ($candle -and $light) {
    Write-Host "Using WiX v3 Toolset (candle + light)..." -ForegroundColor Green
    $ObjDir = Join-Path $OutputDir "obj"
    New-Item -ItemType Directory -Path $ObjDir -Force | Out-Null
    
    $WixObj = Join-Path $ObjDir "devkit.wixobj"
    & candle.exe -arch x64 "installer\devkit.wxs" `
        -dVersion=$Version `
        -dSourceDir=$SourceDir `
        -out $WixObj
        
    & light.exe -sval $WixObj `
        -out $MsiOutput
} else {
    Write-Error "Neither WiX v4 (wix.exe) nor WiX v3 (candle.exe/light.exe) found in PATH. Install WiX Toolset to build .msi."
    exit 1
}

if (Test-Path $MsiOutput) {
    Write-Host "Successfully generated MSI: $MsiOutput" -ForegroundColor Green
    $Hash = (Get-FileHash -Path $MsiOutput -Algorithm SHA256).Hash
    Write-Host "SHA256: $Hash" -ForegroundColor Yellow
} else {
    Write-Error "Failed to generate MSI."
    exit 1
}
