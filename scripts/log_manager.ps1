# ============================================================================
#   PowerShell Logging Module for AutoCrate - v6
# ============================================================================
#  This script is now a module. It exports functions to be used by other
#  PowerShell scripts.
# ============================================================================

# --- Configuration ---
$ScriptRoot = $PSScriptRoot
$ProjectRoot = (Get-Item $ScriptRoot).Parent.FullName
$LogDirectory = Join-Path -Path $ProjectRoot -ChildPath "logs"
$MaxLogFiles = 10

# --- Ensure Log Directory Exists ---
if (-not (Test-Path $LogDirectory)) {
    New-Item -Path $LogDirectory -ItemType Directory | Out-Null
}

# --- Functions ---
function Start-LogSession {
    param (
        [string]$LogName,
        [string]$InitialMessage
    )
    $LogDate = Get-Date -Format "yyyyMMdd_HHmmss"
    $LogFile = Join-Path -Path $LogDirectory -ChildPath "${LogName}_${LogDate}.log"

    # Create the file and write the initial message
    New-Item -Path $LogFile -ItemType File | Out-Null
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "[$Timestamp] [SYSTEM] - Log session started for '$LogName'."
    Add-Content -Path $LogFile -Value "[$Timestamp] [STAGE] - $InitialMessage"

    # Rotate old logs for this log type
    $LogFiles = Get-ChildItem -Path $LogDirectory -Filter "${LogName}*.log" | Sort-Object LastWriteTime -Descending
    if ($LogFiles.Count -gt $MaxLogFiles) {
        $FilesToDelete = $LogFiles | Select-Object -Skip $MaxLogFiles
        foreach ($File in $FilesToDelete) {
            Add-Content -Path $LogFile -Value "[$Timestamp] [SYSTEM] - Rotating old log file: $($File.Name)"
            Remove-Item -Path $File.FullName -Force
        }
    }
    
    # Return the full path to the new log file
    return $LogFile
}

function Write-Log {
    param (
        [string]$LogFile,
        [string]$Level,
        [string]$Message
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogLine = "[$Timestamp] [$Level] - $Message"
    Add-Content -Path $LogFile -Value $LogLine
}

# --- End of functions ---