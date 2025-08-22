# ============================================================================
#   AutoCrate - Code Signing Script
# ============================================================================
# This script signs the AutoCrate.exe to prevent antivirus false positives
# ============================================================================

param(
    [string]$CertificatePath,
    [string]$CertificatePassword,
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Get-Item $PSScriptRoot).Parent.FullName
$ExePath = Join-Path -Path $ProjectRoot -ChildPath "AutoCrate.exe"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "AutoCrate Code Signing Utility" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if executable exists
if (-not (Test-Path $ExePath)) {
    Write-Host "[ERROR] AutoCrate.exe not found at: $ExePath" -ForegroundColor Red
    Write-Host "[ERROR] Please build the executable first using build.bat" -ForegroundColor Red
    exit 1
}

# Check for certificate
if (-not $CertificatePath -or -not (Test-Path $CertificatePath)) {
    Write-Host "[INFO] No certificate provided or certificate not found." -ForegroundColor Yellow
    Write-Host "[INFO] Self-signing with test certificate..." -ForegroundColor Yellow
    Write-Host ""
    
    # Create self-signed certificate for testing
    $cert = New-SelfSignedCertificate -DnsName "AutoCrate" -CertStoreLocation "cert:\CurrentUser\My" -Type CodeSigning
    $certPath = "cert:\CurrentUser\My\$($cert.Thumbprint)"
    
    try {
        Write-Host "[SIGN] Signing with self-signed certificate..." -ForegroundColor Green
        Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -TimestampServer $TimestampUrl
        Write-Host "[SUCCESS] Executable signed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to sign executable: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    # Use provided certificate
    Write-Host "[SIGN] Signing with provided certificate: $CertificatePath" -ForegroundColor Green
    
    try {
        if ($CertificatePassword) {
            $securePassword = ConvertTo-SecureString -String $CertificatePassword -AsPlainText -Force
            $cert = Get-PfxCertificate -FilePath $CertificatePath -Password $securePassword
        } else {
            $cert = Get-PfxCertificate -FilePath $CertificatePath
        }
        
        Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -TimestampServer $TimestampUrl
        Write-Host "[SUCCESS] Executable signed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to sign executable: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "[INFO] Code signing complete!" -ForegroundColor Green
Write-Host "[INFO] Signed executable: $ExePath" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green