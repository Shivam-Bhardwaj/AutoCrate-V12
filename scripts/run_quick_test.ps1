# ============================================================================
#   AutoCrate - PowerShell Quick Test Engine
# ============================================================================
$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
$ProjectRoot = (Get-Item $ScriptRoot).Parent.FullName
. (Join-Path -Path $ScriptRoot -ChildPath "log_manager.ps1")

$LogFile = ""
try {
    $LogFile = Start-LogSession -LogName "quick_test" -InitialMessage "Quick test process started."
    Write-Host "[INFO] Quick test started. Logging to: $LogFile"

    $outputDir = Join-Path -Path $ProjectRoot -ChildPath "expressions\quick_test"

    Write-Log -LogFile $LogFile -Level "STAGE" -Message "1/3: Cleaning output directory..."
    if (Test-Path $outputDir) {
        Remove-Item -Recurse -Force $outputDir
    }
    New-Item -Path $outputDir -ItemType Directory | Out-Null
    Write-Log -LogFile $LogFile -Level "INFO" -Message "Directory '$outputDir' is ready."

    Write-Log -LogFile $LogFile -Level "STAGE" -Message "2/3: Generating quick test expressions..."
    & python scripts/quick_test.py *>> $LogFile
    Write-Log -LogFile $LogFile -Level "INFO" -Message "Script completed."

    Write-Log -LogFile $LogFile -Level "STAGE" -Message "3/3: Verifying generated files..."
    $fileCount = (Get-ChildItem -Path $outputDir -Filter "*.exp").Count
    if ($fileCount -eq 0) {
        Write-Log -LogFile $LogFile -Level "WARNING" -Message "No expression files were generated!"
    } else {
        Write-Log -LogFile $LogFile -Level "INFO" -Message "$fileCount expression files generated successfully."
    }

    Write-Log -LogFile $LogFile -Level "SUCCESS" -Message "Quick test complete."
    Write-Host "[SUCCESS] Quick test finished."

} catch {
    $errorMessage = $_.Exception.Message
    Write-Host "[FATAL] An error occurred: $errorMessage" -ForegroundColor Red
    if ($LogFile) {
        Write-Log -LogFile $LogFile -Level "FATAL" -Message "An error occurred: $errorMessage"
        Write-Host "[INFO] See log for details: $LogFile"
    }
    Read-Host "Press Enter to exit"
    exit 1
}
