# ============================================================================
#   AutoCrate - PowerShell Build Engine
# ============================================================================
#  This script handles the entire build process, with robust logging.
# ============================================================================

# --- Setup ---
$ErrorActionPreference = "Stop" # Exit script on first error
$ScriptRoot = $PSScriptRoot
$ProjectRoot = (Get-Item $ScriptRoot).Parent.FullName

# Import our logging functions
. (Join-Path -Path $ScriptRoot -ChildPath "log_manager.ps1")

# --- Main Process ---
$LogFile = ""
try {
    $LogFile = Start-LogSession -LogName "build" -InitialMessage "Build process started."
    Write-Host "[INFO] Build process started. Logging to: $LogFile"

    # Set Environment Variable for Python script
    $env:AUTOCRATE_TEST_MODE = 1

    # --- 1. Clean previous builds ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "1/4: Cleaning previous builds..."
    if (Test-Path (Join-Path -Path $ProjectRoot -ChildPath "build")) { Remove-Item -Recurse -Force (Join-Path -Path $ProjectRoot -ChildPath "build") }
    if (Test-Path (Join-Path -Path $ProjectRoot -ChildPath "dist")) { Remove-Item -Recurse -Force (Join-Path -Path $ProjectRoot -ChildPath "dist") }
    if (Test-Path (Join-Path -Path $ProjectRoot -ChildPath "AutoCrate.exe")) { Remove-Item -Force (Join-Path -Path $ProjectRoot -ChildPath "AutoCrate.exe") }
    Write-Log -LogFile $LogFile -Level "INFO" -Message "Previous artifacts cleaned."

    # --- 2. Build Executable ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "2/4: Building optimized executable..."
    Write-Log -LogFile $LogFile -Level "INFO" -Message "This will take 30-60 seconds..."
    
    $pyInstallerArgs = @(
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "AutoCrate",
        "--distpath", "dist",
        "--workpath", "build",
        "--add-data", "security;security",
        "--hidden-import", "security",
        "--exclude-module", "pytest",
        "--exclude-module", "hypothesis",
        "--strip",
        "--optimize", "1",
        "--noupx",
        "autocrate/nx_expressions_generator.py"
    )
    
    # The '&' operator executes the command. '2>&1' merges stderr and stdout.
    # The '*' redirects all output streams.
    # Temporarily disable error action preference for PyInstaller since it writes info to stderr
    $OldErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & python -m PyInstaller $pyInstallerArgs *>> $LogFile 2>&1
    $PyInstallerExitCode = $LASTEXITCODE
    $ErrorActionPreference = $OldErrorActionPreference
    
    if ($PyInstallerExitCode -ne 0) {
        throw "PyInstaller failed with exit code $PyInstallerExitCode"
    }
    
    Write-Log -LogFile $LogFile -Level "INFO" -Message "PyInstaller completed."

    # --- 3. Validate and Move ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "3/4: Validating and moving executable..."
    $exePath = Join-Path -Path $ProjectRoot -ChildPath "dist\AutoCrate.exe"
    if (-not (Test-Path $exePath)) {
        throw "Executable not found in 'dist' folder after build!"
    }
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Log -LogFile $LogFile -Level "INFO" -Message ("Executable created (Size: {0:N2} MB)." -f $fileSize)
    
    Move-Item -Path $exePath -Destination (Join-Path -Path $ProjectRoot -ChildPath "AutoCrate.exe") -Force
    Write-Log -LogFile $LogFile -Level "INFO" -Message "Moved executable to project root."

    # --- 4. Final Cleanup ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "4/4: Cleaning up build folders..."
    Remove-Item -Recurse -Force (Join-Path -Path $ProjectRoot -ChildPath "build")
    Remove-Item -Recurse -Force (Join-Path -Path $ProjectRoot -ChildPath "dist")
    Write-Log -LogFile $LogFile -Level "INFO" -Message "'build' and 'dist' folders cleaned."

    # --- Success ---
    Write-Log -LogFile $LogFile -Level "SUCCESS" -Message "Build and cleanup complete. Executable is ready."
    Write-Host "[SUCCESS] Build complete! The window will close in 5 seconds."
    Start-Sleep -Seconds 5

} catch {
    # --- Failure ---
    $errorMessage = $_.Exception.Message
    Write-Host "[FATAL] An error occurred: $errorMessage" -ForegroundColor Red
    if ($LogFile) {
        Write-Log -LogFile $LogFile -Level "FATAL" -Message "An error occurred: $errorMessage"
        Write-Log -LogFile $LogFile -Level "FATAL" -Message "Build process failed. Check log for details."
        Write-Host "[INFO] See log for details: $LogFile"
    }
    # Pause to allow user to see the error
    Read-Host "Press Enter to exit"
    exit 1
}
