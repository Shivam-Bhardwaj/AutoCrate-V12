# ============================================================================
#   AutoCrate - PowerShell Development Engine
# ============================================================================
$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
. (Join-Path -Path $ScriptRoot -ChildPath "log_manager.ps1")

$LogFile = ""
try {
    $LogFile = Start-LogSession -LogName "dev" -InitialMessage "Dev session started."
    Write-Host "[INFO] Dev session started. Logging to: $LogFile"

    $env:AUTOCRATE_DEV_MODE=1
    $env:AUTOCRATE_SKIP_SECURITY=1
    $env:AUTOCRATE_USE_MOCK_DATA=1
    $env:AUTOCRATE_DEBUG=1

    Write-Log -LogFile $LogFile -Level "INFO" -Message "Starting UI from source (autocrate/nx_expressions_generator.py)"
    
    & python autocrate/nx_expressions_generator.py *>> $LogFile

    Write-Log -LogFile $LogFile -Level "SUCCESS" -Message "Development session finished."
    Write-Host "[SUCCESS] Dev script finished."

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
