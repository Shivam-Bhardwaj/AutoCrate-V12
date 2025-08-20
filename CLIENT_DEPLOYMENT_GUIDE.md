# AutoCrate Client Deployment Guide

## Installation Instructions

### Step 1: Download
- Copy `AutoCrate_safe.exe` to the client's computer
- Recommended location: `C:\Program Files\AutoCrate\` or Desktop

### Step 2: First Run - Antivirus Notification
If Windows Defender or antivirus software flags the file:

1. **This is a FALSE POSITIVE** - The software is safe
2. Click "More info" → "Run anyway" (Windows Defender)
3. Or add an exclusion for the AutoCrate folder

### Step 3: Add Antivirus Exclusion (If Needed)

#### Windows Defender:
1. Open Windows Security
2. Go to Virus & threat protection
3. Under "Exclusions", click "Add or remove exclusions"
4. Add folder containing AutoCrate.exe

#### Norton/McAfee/Other:
1. Open your antivirus settings
2. Find "Exclusions" or "Exceptions"
3. Add the AutoCrate folder

## Why Antivirus Detection Occurs

- **New File**: No reputation in antivirus databases
- **PyInstaller**: Python applications packaged as exe often trigger false positives
- **Not Signed**: No digital certificate (requires paid certificate)

## System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum
- **Display**: 1920x1080 or higher
- **Storage**: 100MB free space
- **Prerequisites**: None (all included)

## Features Included

- ✅ Full AutoCrate functionality
- ✅ NX Expression file generation
- ✅ ASTM compliance calculations
- ✅ Responsive UI for all screen sizes
- ✅ Dark mode interface
- ✅ All dependencies bundled

## Troubleshooting

### Issue: "Windows protected your PC"
**Solution**: Click "More info" → "Run anyway"

### Issue: Antivirus quarantines the file
**Solution**: Restore from quarantine and add exclusion

### Issue: UI appears too small/large
**Solution**: The app auto-scales based on screen resolution. Press F11 to toggle fullscreen.

### Issue: Can't generate expression files
**Solution**: Ensure you have write permissions in the expressions folder

## Support

For technical support, contact your system administrator or the AutoCrate development team.

## Version Information
- Version: 12.1.5
- Build Type: Production
- Interface: Ultra-Modern GUI
- Build Date: August 2025