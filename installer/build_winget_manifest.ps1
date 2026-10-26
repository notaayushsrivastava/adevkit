<#
.SYNOPSIS
    Generates and validates WinGet manifests for adevkit.

.DESCRIPTION
    Creates the required multi-file WinGet manifests:
    - notaayushsrivastava.adevkit.yaml (Version)
    - notaayushsrivastava.adevkit.locale.en-US.yaml (Locale)
    - notaayushsrivastava.adevkit.installer.yaml (Installer)
    Optionally computes the SHA256 checksum from a local MSI and validates with winget validate.

.PARAMETER Version
    The package version (e.g. 0.1.4). Auto-detected from pyproject.toml if omitted.

.PARAMETER PackageIdentifier
    WinGet package identifier (default: notaayushsrivastava.adevkit).

.PARAMETER MsiPath
    Optional path to the local MSI file to compute SHA256 and product code.

.PARAMETER Sha256
    Optional SHA256 checksum if MsiPath is not available locally.

.PARAMETER OutputDir
    Destination directory for the manifest files.

.PARAMETER Repo
    GitHub repository in owner/repo format (default: notaayushsrivastava/adevkit).
#>

param(
    [string]$Version,
    [string]$PackageIdentifier = "notaayushsrivastava.adevkit",
    [string]$MsiPath,
    [string]$Sha256,
    [string]$OutputDir,
    [string]$Repo = "notaayushsrivastava/adevkit",
    [switch]$Validate
)

$ErrorActionPreference = "Stop"

# 1. Determine Version
if (-not $Version -or $Version.Trim() -eq "") {
    if (Test-Path "pyproject.toml") {
        $content = Get-Content "pyproject.toml" -Raw
        if ($content -match 'version\s*=\s*["'']([^"'']+)["'']') {
            $Version = $matches[1]
        }
    }
}
if (-not $Version) {
    $Version = "0.1.4"
}
$Version = $Version.Trim().TrimStart('v')

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building WinGet Manifest for $PackageIdentifier v$Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 2. Determine Output Directory
if (-not $OutputDir -or $OutputDir.Trim() -eq "") {
    $firstChar = $PackageIdentifier.Substring(0, 1).ToLower()
    $parts = $PackageIdentifier.Split('.')
    $pub = $parts[0]
    $pkg = if ($parts.Length -gt 1) { $parts[1] } else { $parts[0] }
    $OutputDir = Join-Path $PSScriptRoot "winget\manifests\$firstChar\$pub\$pkg\$Version"
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

# 3. Locate MSI & Determine SHA256 / ProductCode
$UpgradeCode = "{e8f4a180-2a8e-4a65-8b3d-71b56a938c41}"
$ProductCode = $UpgradeCode

if (-not $MsiPath) {
    $candidates = @(
        "output\AayushsDevKit-v$Version-x64.msi",
        "dist\AayushsDevKit-v$Version-x64.msi"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $MsiPath = $cand
            break
        }
    }
}

if ($MsiPath -and (Test-Path $MsiPath)) {
    Write-Host "[*] Found local MSI: $MsiPath" -ForegroundColor Green
    $Sha256 = (Get-FileHash -Path $MsiPath -Algorithm SHA256).Hash
    Write-Host "[*] Computed SHA256: $Sha256" -ForegroundColor Green

    # Try extracting exact ProductCode from MSI table
    try {
        $windowsInstaller = New-Object -ComObject WindowsInstaller.Installer
        $database = $windowsInstaller.OpenDatabase((Resolve-Path $MsiPath).Path, 0)
        $view = $database.OpenView("SELECT Value FROM Property WHERE Property='ProductCode'")
        $view.Execute()
        $record = $view.Fetch()
        if ($record) {
            $extracted = $record.StringData(1)
            if ($extracted -and $extracted.StartsWith("{")) {
                $ProductCode = $extracted
                Write-Host "[*] Extracted ProductCode from MSI: $ProductCode" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "[-] Note: Using UpgradeCode as fallback ProductCode: $ProductCode" -ForegroundColor Yellow
    }
} elseif (-not $Sha256) {
    # Check SHA256SUMS.txt if present
    if (Test-Path "output\SHA256SUMS.txt") {
        $checksumLine = Get-Content "output\SHA256SUMS.txt" | Where-Object { $_ -match "AayushsDevKit-v$Version-x64\.msi" }
        if ($checksumLine -match '^([a-fA-F0-9]{64})') {
            $Sha256 = $matches[1].ToUpper()
            Write-Host "[*] Extracted SHA256 from SHA256SUMS.txt: $Sha256" -ForegroundColor Green
        }
    }
}

if (-not $Sha256) {
    $Sha256 = "0000000000000000000000000000000000000000000000000000000000000000"
    Write-Host "[-] Warning: No local MSI or SHA256 provided; using placeholder hash." -ForegroundColor Yellow
}

$InstallerUrl = "https://github.com/$Repo/releases/download/v$Version/AayushsDevKit-v$Version-x64.msi"

# 4. Generate Version Manifest
$versionManifestPath = Join-Path $OutputDir "$PackageIdentifier.yaml"
$versionManifestContent = @"
# Created using adevkit WinGet generator
# yaml-language-server: `$schema=https://aka.ms/winget-manifest.version.1.6.0.schema.json

PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.6.0
"@
Set-Content -Path $versionManifestPath -Value $versionManifestContent -Encoding utf8 -NoNewline

# 5. Generate Locale Manifest
$localeManifestPath = Join-Path $OutputDir "$PackageIdentifier.locale.en-US.yaml"
$localeManifestContent = @"
# Created using adevkit WinGet generator
# yaml-language-server: `$schema=https://aka.ms/winget-manifest.defaultLocale.1.6.0.schema.json

PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
PackageLocale: en-US
Publisher: Aayush Srivastava
PublisherUrl: https://aayushsrivastava.com
PublisherSupportUrl: https://github.com/$Repo/issues
Author: Aayush Srivastava
PackageName: adevkit
PackageUrl: https://github.com/$Repo
License: MIT
LicenseUrl: https://github.com/$Repo/blob/main/LICENSE
Copyright: Copyright (c) Aayush Srivastava
ShortDescription: Single-command project scaffolding and agentic environment setup with curated AI agent skills.
Description: adevkit (Aayush's DevKit) is a unified CLI tool for scaffolding projects with pre-configured agentic environments, AI skills, and developer toolchains. It automatically provisions virtual environments (pip or uv), project configurations, and modern AI coding assistants.
Moniker: adevkit
Tags:
  - cli
  - developer-tools
  - scaffolding
  - agentic-ai
  - ai-agents
  - python
  - uv
ManifestType: defaultLocale
ManifestVersion: 1.6.0
"@
Set-Content -Path $localeManifestPath -Value $localeManifestContent -Encoding utf8 -NoNewline

# 6. Generate Installer Manifest
$installerManifestPath = Join-Path $OutputDir "$PackageIdentifier.installer.yaml"
$installerManifestContent = @"
# Created using adevkit WinGet generator
# yaml-language-server: `$schema=https://aka.ms/winget-manifest.installer.1.6.0.schema.json

PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
InstallerLocale: en-US
Platform:
  - Windows.Desktop
MinimumOSVersion: 10.0.0.0
InstallerType: msi
Scope: machine
InstallModes:
  - interactive
  - silent
  - silentWithProgress
UpgradeBehavior: install
Commands:
  - adevkit
  - devkit
ProductCode: '$ProductCode'
AppsAndFeaturesEntries:
  - DisplayName: adevkit
    Publisher: Aayush Srivastava
    DisplayVersion: $Version
    ProductCode: '$ProductCode'
    UpgradeCode: '$UpgradeCode'
Installers:
  - Architecture: x64
    InstallerType: msi
    InstallerUrl: $InstallerUrl
    InstallerSha256: $Sha256
ManifestType: installer
ManifestVersion: 1.6.0
"@
Set-Content -Path $installerManifestPath -Value $installerManifestContent -Encoding utf8 -NoNewline

Write-Host "[+] Generated WinGet Manifests in: $OutputDir" -ForegroundColor Green
Write-Host "    - $versionManifestPath" -ForegroundColor Gray
Write-Host "    - $localeManifestPath" -ForegroundColor Gray
Write-Host "    - $installerManifestPath" -ForegroundColor Gray

# 7. Validation
if ($Validate -or (Get-Command "winget" -ErrorAction SilentlyContinue)) {
    Write-Host "`n[*] Validating manifest with winget validate..." -ForegroundColor Cyan
    try {
        & winget validate --manifest $OutputDir
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[+] WinGet manifest validation passed!" -ForegroundColor Green
        } else {
            Write-Host "[-] WinGet validation exited with code $LASTEXITCODE" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[-] winget validate encountered an error: $_" -ForegroundColor Yellow
    }
}
