# AutoCrate Web Application - Testing Guide

## Issues Fixed

### 1. 3D Viewer Not Rendering
**Problem**: The 3D viewer component was not displaying anything when calculations were done.

**Fix Applied**:
- Changed import from `ProfessionalCrateViewer-enhanced` to `ProfessionalCrateViewer-fixed`
- Added proper null data handling with placeholder message
- Added debugging logs to track data flow
- Fixed coordinate system mapping for proper crate display

### 2. Generate Crate Button Not Working
**Problem**: Users expected a "Generate Crate" button but it was missing or not functional.

**Fix Applied**:
- Added visible "Generate Crate Files" button in Calculator component
- Button appears after calculation is complete
- Connected to existing Download NX functionality
- Added comprehensive logging for debugging
- Added data attribute for button identification

## Manual Testing Steps

### Test 1: Initial Page Load
1. Open http://localhost:3001
2. **Expected**: 
   - Page loads without errors
   - 3D viewer shows placeholder with message "Calculate a crate design to see 3D preview"
   - Calculator form is visible on the left

### Test 2: Calculate Design
1. Enter test values:
   - Length: 48
   - Width: 40
   - Height: 36
   - Weight: 500
2. Click "Calculate Design" button
3. **Expected**:
   - Calculation completes without errors
   - Results appear in panels
   - "Generate Crate Files" button appears below Calculate button
   - 3D viewer shows the crate model

### Test 3: 3D Viewer Interaction
1. After calculation, interact with 3D viewer
2. **Expected**:
   - Crate model is visible and rotates
   - Controls panel works (Exploded View, Show Dimensions, etc.)
   - Hover over components shows dimensions
   - Grid and lighting work properly

### Test 4: Generate Crate Files
1. Click "Generate Crate Files" button
2. **Expected**:
   - Console shows "Generate Crate button clicked"
   - Download NX button is triggered
   - NX expression file downloads (check Downloads folder)
   - File name format: `Crate_[L]x[W]x[H]_[timestamp].exp`

### Test 5: Download NX File (Direct)
1. Click "Download NX File" button in Results panel
2. **Expected**:
   - File downloads immediately
   - Console shows detailed logging
   - No errors in console

## Browser Console Checks

Open Developer Tools (F12) and check Console for:

### During Calculation:
```
Starting calculation
Using TypeScript calculator (offline mode)
Calculation completed successfully
```

### When Clicking Generate:
```
Generate Crate button clicked
=== Download NX Expression Button Clicked ===
NX expression generated, length: [number]
✓ NX expression file downloaded successfully
```

### For 3D Viewer:
```
ProfessionalCrateViewer received data: [object]
```

## Verification Checklist

- [ ] Page loads without errors
- [ ] 3D viewer shows placeholder initially
- [ ] Calculation works with test data
- [ ] 3D model appears after calculation
- [ ] Generate Crate Files button appears after calculation
- [ ] Generate button triggers download
- [ ] Download NX File button works
- [ ] 3D viewer controls work (exploded view, dimensions, etc.)
- [ ] No console errors during operation
- [ ] Downloaded .exp file contains valid NX expressions

## Common Issues & Solutions

### Issue: 3D Viewer is blank
- Check browser console for WebGL errors
- Ensure browser supports WebGL
- Try refreshing the page

### Issue: Generate button doesn't appear
- Ensure calculation completed successfully
- Check if results are displayed
- Look for errors in console

### Issue: Download doesn't work
- Check browser download settings
- Look for popup blockers
- Check console for errors

## Development Server

Start the development server:
```bash
cd web
npm run dev
```

Server runs on: http://localhost:3001 (or 3000 if available)

## Success Criteria

✅ Both critical issues are resolved when:
1. 3D viewer displays crate model after calculation
2. Generate Crate Files button is visible and functional
3. Files download without errors
4. No console errors during normal operation