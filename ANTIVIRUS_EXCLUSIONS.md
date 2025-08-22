# AutoCrate Antivirus Configuration Guide

## Overview
PyInstaller-built executables like AutoCrate.exe can trigger false positives in antivirus software. This guide provides solutions to prevent these issues.

## Quick Solutions

### 1. Code Signing (Recommended)
**Most effective method** - Sign the executable after building:
```powershell
.\scripts\sign_exe.ps1
```

### 2. Add Antivirus Exclusions
Add these paths to your antivirus exclusion list:

#### Project Directory (Development)
```
C:\Users\[Username]\OneDrive\Desktop\SbT\AutoCrate V12\AutoCrate V12.0.9\
```

#### Final Executable
```
C:\Users\[Username]\OneDrive\Desktop\SbT\AutoCrate V12\AutoCrate V12.0.9\AutoCrate.exe
```

#### Build Process (Temporary)
```
C:\Users\[Username]\OneDrive\Desktop\SbT\AutoCrate V12\AutoCrate V12.0.9\build\
C:\Users\[Username]\OneDrive\Desktop\SbT\AutoCrate V12\AutoCrate V12.0.9\dist\
```

## Antivirus-Specific Instructions

### Windows Defender
1. Open Windows Security → Virus & threat protection
2. Click "Manage settings" under Virus & threat protection settings
3. Scroll down to "Exclusions" and click "Add or remove exclusions"
4. Click "Add an exclusion" → "Folder"
5. Browse to the AutoCrate project directory

### Norton Security
1. Open Norton → Settings → Antivirus
2. Click "Scans and Risks" → "Exclusions/Low Risks"
3. Click "Configure" next to "Items to Exclude from Scans"
4. Add the AutoCrate directory and executable

### McAfee
1. Open McAfee → Navigation → Real-Time Scanning
2. Click "Excluded Files"
3. Add the AutoCrate paths

### Kaspersky
1. Open Kaspersky → Settings → Additional → Threats and Exclusions
2. Click "Manage Exclusions"
3. Add the AutoCrate paths to exclusions

## Why This Happens

PyInstaller-built executables trigger false positives because:
- **Self-extraction**: The executable unpacks itself at runtime
- **Dynamic imports**: Code is loaded dynamically
- **No digital signature**: Unsigned executables are treated as suspicious
- **Heuristic detection**: Antivirus uses pattern matching that can flag legitimate software

## Build Configuration Features

The AutoCrate build process includes these antivirus-friendly settings:
- `--noupx`: Disables UPX compression (often flagged)
- `--exclude-module`: Removes debugging modules
- `--clean`: Ensures clean builds
- `--strip`: Removes debug symbols
- `--runtime-tmpdir .`: Uses current directory for temp files

## Professional Deployment

For production/distribution:
1. **Get a code signing certificate** from a trusted CA
2. **Sign the executable** using the certificate
3. **Submit to antivirus vendors** for whitelisting
4. **Use VirusTotal** to check detection rates

## Emergency Workarounds

If immediate access is needed:
1. **Temporarily disable** real-time protection
2. **Add exclusion** for the specific file
3. **Run from excluded folder**
4. **Use portable antivirus** scanners to verify safety

## Contact Information

If you continue experiencing issues:
- Check Windows Event Viewer for specific detection details
- Contact your IT security team with this documentation
- Submit false positive reports to antivirus vendors

---
*This document is maintained as part of the AutoCrate project to ensure smooth deployment and operation.*