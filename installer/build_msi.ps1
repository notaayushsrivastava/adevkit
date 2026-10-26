param(
    [string]$Version,
    [string]$DistDir = "dist",
    [string]$OutputDir = "output"
)

$ErrorActionPreference = "Stop"

# Auto-detect version if not supplied or empty
if (-not $Version -or $Version.Trim() -eq "") {
    if (Test-Path "pyproject.toml") {
        $content = Get-Content "pyproject.toml" -Raw
        if ($content -match 'version\s*=\s*["'']([^"'']+)["'']') {
            $Version = $matches[1]
        }
    }
}
if (-not $Version) {
    $Version = "0.1.3"
}
$Version = $Version.Trim().TrimStart('v')
# WiX requires x.x.x or x.x.x.x
if ($Version -notmatch '^\d+(\.\d+){1,3}$') {
    $Version = "0.1.3"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building MSI Installer for adevkit v$Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Ensure output directory exists
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$MsiOutput = Join-Path $OutputDir "AayushsDevKit-v$Version-x64.msi"
$SourceDir = (Resolve-Path $DistDir).Path

# Ensure both adevkit.exe and devkit.exe exist so all triggers work
$adevkitExe = Join-Path $SourceDir "adevkit.exe"
$devkitExe = Join-Path $SourceDir "devkit.exe"
if ((Test-Path $adevkitExe) -and !(Test-Path $devkitExe)) {
    Copy-Item $adevkitExe $devkitExe -Force
} elseif ((Test-Path $devkitExe) -and !(Test-Path $adevkitExe)) {
    Copy-Item $devkitExe $adevkitExe -Force
}

if (!(Test-Path $adevkitExe)) {
    Write-Error "Executable adevkit.exe not found in $SourceDir"
    exit 1
}

# Check for WiX source file (prefer adevkit.wxs)
$wxsFile = if (Test-Path "installer\adevkit.wxs") { "installer\adevkit.wxs" } else { "installer\devkit.wxs" }

# Check for WiX v4 (wix.exe)
$wixV4 = Get-Command "wix" -ErrorAction SilentlyContinue

# Check for WiX v3 (candle.exe and light.exe)
$candle = Get-Command "candle.exe" -ErrorAction SilentlyContinue
$light = Get-Command "light.exe" -ErrorAction SilentlyContinue

if ($wixV4) {
    Write-Host "Using WiX v4 CLI to build MSI..." -ForegroundColor Green
    & wix build $wxsFile `
        -d Version=$Version `
        -d SourceDir=$SourceDir `
        -o $MsiOutput
    if ($LASTEXITCODE -ne 0) {
        Write-Error "wix build failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} elseif ($candle -and $light) {
    Write-Host "Using WiX v3 Toolset (candle + light)..." -ForegroundColor Green
    $ObjDir = Join-Path $OutputDir "obj"
    New-Item -ItemType Directory -Path $ObjDir -Force | Out-Null
    
    $WixObj = Join-Path $ObjDir "adevkit.wixobj"
    
    $candleArgs = @(
        "-nologo",
        "-arch", "x64",
        "-dVersion=$Version",
        "-dSourceDir=$SourceDir",
        "-out", $WixObj,
        $wxsFile
    )
    Write-Host "Invoking candle with Version=$Version" -ForegroundColor Cyan
    & candle.exe @candleArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Error "candle.exe failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }

    $lightArgs = @(
        "-nologo",
        "-sval",
        $WixObj,
        "-out", $MsiOutput
    )
    Write-Host "Invoking light to link MSI..." -ForegroundColor Cyan
    & light.exe @lightArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Error "light.exe failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
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
