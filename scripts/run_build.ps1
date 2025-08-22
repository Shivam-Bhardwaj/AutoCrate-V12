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
    Write-Host "[INFO] Build process started. Logging to: $LogFile" -ForegroundColor Cyan
    Write-Host "[INFO] Project root: $ProjectRoot" -ForegroundColor Gray
    Write-Host "" # Add spacing

    # Set Environment Variable for Python script
    $env:AUTOCRATE_TEST_MODE = 1

    # --- 1. Clean previous builds ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "1/4: Cleaning previous builds..."
    Write-Host "[STAGE 1/4] Cleaning previous builds..." -ForegroundColor Yellow
    
    $buildPath = Join-Path -Path $ProjectRoot -ChildPath "build"
    $distPath = Join-Path -Path $ProjectRoot -ChildPath "dist"
    $exePath = Join-Path -Path $ProjectRoot -ChildPath "AutoCrate.exe"
    
    if (Test-Path $buildPath) { 
        Write-Host "  - Removing build folder..." -ForegroundColor Gray
        Remove-Item -Recurse -Force $buildPath 
    }
    if (Test-Path $distPath) { 
        Write-Host "  - Removing dist folder..." -ForegroundColor Gray
        Remove-Item -Recurse -Force $distPath 
    }
    if (Test-Path $exePath) { 
        Write-Host "  - Removing old AutoCrate.exe..." -ForegroundColor Gray
        Remove-Item -Force $exePath 
    }
    Write-Log -LogFile $LogFile -Level "INFO" -Message "Previous artifacts cleaned."
    Write-Host "  [DONE] Cleanup complete" -ForegroundColor Green
    Write-Host "" # Add spacing

    # --- 2. Build Executable ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "2/4: Building optimized executable..."
    Write-Host "[STAGE 2/4] Building optimized executable..." -ForegroundColor Yellow
    Write-Host "  - This will take 30-60 seconds..." -ForegroundColor Gray
    Write-Host "  - Running PyInstaller with optimization flags..." -ForegroundColor Gray
    Write-Host "  - Output mode: Single executable file" -ForegroundColor Gray
    Write-Host "  - Optimization level: 1 (bytecode optimization)" -ForegroundColor Gray
    Write-Host "  - Compression: Disabled for faster startup" -ForegroundColor Gray
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
        "--hidden-import", "customtkinter",
        "--hidden-import", "autocrate.ultra_modern_gui",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "PIL.ImageFilter",
        "--collect-all", "customtkinter",
        "--exclude-module", "pytest",
        "--exclude-module", "hypothesis",
        "--exclude-module", "pydevd",
        "--exclude-module", "pdb",
        "--exclude-module", "doctest",
        "--exclude-module", "unittest",
        "--strip",
        "--optimize", "1",
        "--noupx",
        "--runtime-tmpdir", ".",
        "--clean",
        "--uac-admin",
        "autocrate/nx_expressions_generator.py"
    )
    
    # Show detailed command being executed
    Write-Host "" # Add spacing
    Write-Host "  Executing command:" -ForegroundColor Cyan
    Write-Host "  python -m PyInstaller" -ForegroundColor White
    foreach ($arg in $pyInstallerArgs) {
        if ($arg -match "^--") {
            Write-Host "    $arg" -ForegroundColor DarkCyan
        } else {
            Write-Host "      $arg" -ForegroundColor Gray
        }
    }
    Write-Host "" # Add spacing
    Write-Host "  PyInstaller Output:" -ForegroundColor Cyan
    Write-Host "  ==================" -ForegroundColor DarkCyan
    
    # Run PyInstaller with real-time output
    $OldErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    
    # Create a temp file for output
    $tempOutput = [System.IO.Path]::GetTempFileName()
    
    # Start PyInstaller process with output redirection
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "python"
    $pinfo.Arguments = "-m PyInstaller " + ($pyInstallerArgs -join " ")
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $pinfo
    
    Write-Host "  Starting PyInstaller..." -ForegroundColor Yellow
    $process.Start() | Out-Null
    
    # Read output in real-time
    while (!$process.HasExited) {
        $output = $process.StandardOutput.ReadLine()
        if ($output) {
            # Parse and display output with appropriate formatting
            if ($output -match "INFO:") {
                Write-Host "  [INFO] $($output -replace '.*INFO:\s*', '')" -ForegroundColor Gray
            } elseif ($output -match "WARNING:") {
                Write-Host "  [WARN] $($output -replace '.*WARNING:\s*', '')" -ForegroundColor Yellow
            } elseif ($output -match "Building") {
                Write-Host "  [BUILD] $output" -ForegroundColor Cyan
            } elseif ($output -match "Analyzing") {
                Write-Host "  [ANALYZE] $output" -ForegroundColor Magenta
            } elseif ($output -match "Processing") {
                Write-Host "  [PROCESS] $output" -ForegroundColor Blue
            } elseif ($output -match "Writing") {
                Write-Host "  [WRITE] $output" -ForegroundColor Green
            } else {
                Write-Host "  $output" -ForegroundColor DarkGray
            }
            # Also write to log
            $output | Out-File -FilePath $LogFile -Append
        }
        
        # Also check stderr
        $errorOutput = $process.StandardError.ReadLine()
        if ($errorOutput) {
            Write-Host "  [STDERR] $errorOutput" -ForegroundColor DarkYellow
            $errorOutput | Out-File -FilePath $LogFile -Append
        }
    }
    
    # Get any remaining output
    $remainingOutput = $process.StandardOutput.ReadToEnd()
    if ($remainingOutput) {
        $remainingOutput -split "`n" | ForEach-Object {
            if ($_.Trim()) {
                Write-Host "  $_" -ForegroundColor DarkGray
                $_ | Out-File -FilePath $LogFile -Append
            }
        }
    }
    
    $remainingError = $process.StandardError.ReadToEnd()
    if ($remainingError) {
        $remainingError -split "`n" | ForEach-Object {
            if ($_.Trim()) {
                Write-Host "  [STDERR] $_" -ForegroundColor DarkYellow
                $_ | Out-File -FilePath $LogFile -Append
            }
        }
    }
    
    $PyInstallerExitCode = $process.ExitCode
    $process.Dispose()
    
    # Clean up temp file
    if (Test-Path $tempOutput) {
        Remove-Item $tempOutput -Force
    }
    
    Write-Host "  ==================" -ForegroundColor DarkCyan
    Write-Host "" # New line
    
    $ErrorActionPreference = $OldErrorActionPreference
    
    if ($PyInstallerExitCode -ne 0) {
        throw "PyInstaller failed with exit code $PyInstallerExitCode"
    }
    
    Write-Log -LogFile $LogFile -Level "INFO" -Message "PyInstaller completed."
    Write-Host "  [DONE] PyInstaller build complete" -ForegroundColor Green
    Write-Host "  - Build artifacts created in 'dist' folder" -ForegroundColor Gray
    Write-Host "" # Add spacing

    # --- 3. Validate and Move ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "3/4: Validating and moving executable..."
    Write-Host "[STAGE 3/4] Validating and moving executable..." -ForegroundColor Yellow
    
    $exePath = Join-Path -Path $ProjectRoot -ChildPath "dist\AutoCrate.exe"
    Write-Host "  - Checking for executable at: dist\AutoCrate.exe" -ForegroundColor Gray
    Write-Host "  - Verifying file integrity..." -ForegroundColor Gray
    
    if (-not (Test-Path $exePath)) {
        throw "Executable not found in 'dist' folder after build!"
    }
    
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host ("  - Executable size: {0:N2} MB" -f $fileSize) -ForegroundColor Gray
    Write-Log -LogFile $LogFile -Level "INFO" -Message ("Executable created (Size: {0:N2} MB)." -f $fileSize)
    
    Write-Host "  - Moving to project root..." -ForegroundColor Gray
    Move-Item -Path $exePath -Destination (Join-Path -Path $ProjectRoot -ChildPath "AutoCrate.exe") -Force
    Write-Log -LogFile $LogFile -Level "INFO" -Message "Moved executable to project root."
    Write-Host "  [DONE] Executable validated and moved" -ForegroundColor Green
    Write-Host "" # Add spacing

    # --- 4. Final Cleanup ---
    Write-Log -LogFile $LogFile -Level "STAGE" -Message "4/4: Cleaning up build folders..."
    Write-Host "[STAGE 4/4] Cleaning up build folders..." -ForegroundColor Yellow
    
    Write-Host "  - Removing temporary build folder..." -ForegroundColor Gray
    $buildPath = Join-Path -Path $ProjectRoot -ChildPath "build"
    $buildItems = (Get-ChildItem -Path $buildPath -Recurse | Measure-Object).Count
    Write-Host "    Deleting $buildItems temporary build files..." -ForegroundColor DarkGray
    Remove-Item -Recurse -Force $buildPath
    
    Write-Host "  - Removing temporary dist folder..." -ForegroundColor Gray
    Remove-Item -Recurse -Force (Join-Path -Path $ProjectRoot -ChildPath "dist")
    
    Write-Log -LogFile $LogFile -Level "INFO" -Message "'build' and 'dist' folders cleaned."
    Write-Host "  [DONE] Cleanup complete" -ForegroundColor Green
    Write-Host "" # Add spacing

    # --- Success ---
    Write-Log -LogFile $LogFile -Level "SUCCESS" -Message "Build and cleanup complete. Executable is ready."
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Build complete!" -ForegroundColor Green
    Write-Host "[SUCCESS] AutoCrate.exe is ready in: $ProjectRoot" -ForegroundColor Green
    Write-Host "[SUCCESS] Log file: $LogFile" -ForegroundColor DarkGreen
    Write-Host "============================================" -ForegroundColor Green
    
    # Optional: Sign the executable
    Write-Host "[INFO] To sign the executable and prevent antivirus issues:" -ForegroundColor Cyan
    Write-Host "[INFO] Run: .\scripts\sign_exe.ps1" -ForegroundColor Cyan
    Write-Host "" # Add spacing
    Write-Host "The window will close in 5 seconds..." -ForegroundColor Gray
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
