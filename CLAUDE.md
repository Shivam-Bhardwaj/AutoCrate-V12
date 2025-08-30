# AutoCrate V12 - AI Development Guide

## Project Overview
AutoCrate V12 is a professional ASTM D6251-17 compliant wooden crate design system with both desktop (Python/Tkinter) and web (Next.js/React) interfaces. It generates Siemens NX CAD expressions for automated 3D model creation.

## Key Components

### 1. Desktop Application (Python)
- **Main Entry**: `main.py` - Launches the Tkinter GUI
- **Core Logic**: `autocrate/nx_expressions_generator.py` - Main expression generation engine
- **Panel Calculations**: Individual modules for each panel (front, back, left, right, top, end)
- **Build**: `dist/AutoCrate.exe` - Standalone Windows executable

### 2. Web Application (Next.js)
- **Location**: `web/` directory
- **Main Page**: `web/src/app/page.tsx` - Optimized no-scroll layout
- **Calculations**: `web/src/lib/autocrate-calculations-fixed.ts` - Matches desktop logic exactly
- **3D Viewer**: `web/src/components/ProfessionalCrateViewer-fixed.tsx` - Correct NX coordinate system
- **Deploy**: Vercel deployment with version tracking

### 3. Master Control Script
- **File**: `AutoCrate.bat` - Single control panel for all operations
- **Features**:
  - Start development servers
  - Build executables
  - Deploy to production
  - Kill stuck servers (Option K)
  - Clean builds and view logs

## Critical Calculation Logic

### Panel Dimension Formulas (MUST MATCH)
```python
# Panel assembly thickness
panel_assembly_thickness = panel_thickness + cleat_thickness

# End panel dimensions (sandwiched between front/back)
end_panel_length = overall_length - (2 * panel_assembly_thickness)
end_panel_height = skid_height + floorboard_thickness + product_height + clearance_above - ground_clearance

# Front/Back panel dimensions (cover end panels)
front_panel_width = product_width + (2 * clearance) + (2 * panel_assembly_thickness)

# CRITICAL: Vertical cleat material adjustments
if panel_width > 48:
    additional_cleats = ceil((panel_width - 48) / 48)
    material_needed = additional_cleats * cleat_width
    panel_width += material_needed
    overall_width += material_needed
```

### NX Coordinate System
- **X-axis**: Width (left-right)
- **Y-axis**: Length (front-back)
- **Z-axis**: Height (up-down)
- **Origin**: Front-left-bottom corner of crate

## Testing & Validation

### Desktop Testing
```bash
# Test NX expression generation
python test_nx_generation_comparison.py

# Expected output for 96x48x30" @ 1000lbs:
# Overall Width OD: 52.0"
# Overall Length OD: 105.0"
# Front Panel Width: 56.5"
# Front Panel Height: 33.5"
```

### Web Testing
```bash
cd web
npm run dev  # Start at http://localhost:3000
```

## Common Tasks

### 1. Fix Expression Generation Issues
- Check `autocrate/nx_expressions_generator.py` for desktop logic
- Ensure `web/src/lib/autocrate-calculations-fixed.ts` matches exactly
- Verify vertical cleat material calculations are applied

### 2. Fix 3D Viewer Issues
- Edit `web/src/components/ProfessionalCrateViewer-fixed.tsx`
- Ensure coordinate mapping: Y (length) → Z (depth in Three.js)
- Check panel positioning relative to assembly thickness

### 3. Build & Deploy
```bash
# Use master control panel
AutoCrate.bat

# Option 4: Build exe
# Option 5: Deploy to Vercel
# Option K: Kill stuck servers
```

### 4. Kill Stuck Servers
If ports 3000-3003 are blocked:
1. Run `AutoCrate.bat`
2. Press `K` for Kill Servers
3. Confirm to kill node processes if needed

## File Structure
```
AutoCrate V12/
├── AutoCrate.bat           # Master control panel
├── main.py                 # Desktop app entry
├── autocrate/              # Core calculation modules
│   ├── nx_expressions_generator.py
│   ├── front_panel_logic.py
│   ├── back_panel_logic.py
│   └── ...
├── dist/
│   └── AutoCrate.exe      # Built executable
├── web/                    # Web application
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx   # Main page (optimized layout)
│   │   ├── components/
│   │   │   ├── Calculator.tsx
│   │   │   ├── ProfessionalCrateViewer-fixed.tsx
│   │   │   └── ResultsPanel.tsx
│   │   └── lib/
│   │       └── autocrate-calculations-fixed.ts
│   └── package.json
└── expressions/            # Generated NX expression files
```

## Important Notes

1. **ALWAYS** use `autocrate-calculations-fixed.ts` for web calculations (not the original)
2. **ALWAYS** use `ProfessionalCrateViewer-fixed.tsx` for 3D visualization
3. **NEVER** create duplicate batch files - use `AutoCrate.bat` only
4. **TEST** expression generation after any calculation changes
5. **VERIFY** desktop and web generate identical NX expressions

## Compliance Requirements
- ASTM D6251-17 Standard (wooden crate design)
- Safety factor: 1.5x minimum
- Material: 3/4" plywood (default)
- Cleats: 1.5" x 3.5" lumber (default)

## Recent Fixes (Aug 2024)
1. ✅ Fixed NX expression generation logic mismatch
2. ✅ Added vertical cleat material calculations
3. ✅ Fixed 3D viewer coordinate system
4. ✅ Removed scrolling from web interface
5. ✅ Added server kill functionality
6. ✅ Consolidated to single batch file

## Contact & Support
- GitHub Issues: Report bugs and request features
- Logs: Check `logs/` directory for debug information
- Debug Mode: Use LogViewer in web app or view `autocrate.log`

---
*Last Updated: August 27, 2024*
*Version: 1.1.0*