# NX Coordinate System Mapping Documentation

## Overview
This document defines the coordinate system mappings between Siemens NX CAD and the AutoCrate web 3D viewer (Three.js).

## NX Coordinate System

### Axes Definition
- **X-axis**: Width (left-right)
  - Positive X: Right direction
  - Negative X: Left direction
- **Y-axis**: Length (front-back) 
  - Positive Y: Back direction
  - Negative Y: Front direction
- **Z-axis**: Height (up-down)
  - Positive Z: Up direction
  - Negative Z: Down direction

### Origin Point
- Located at the **front-left-bottom corner** of the crate
- Coordinates: (0, 0, 0)
- All measurements extend positively from this origin

### Panel Positions in NX
```
Front Panel: Y = 0 (at origin)
Back Panel:  Y = Overall_Length
Left Panel:  X = 0 (at origin)
Right Panel: X = Overall_Width
Bottom:      Z = 0 (at origin)
Top Panel:   Z = Overall_Height
```

## Three.js Coordinate System (Web 3D Viewer)

### Axes Definition
- **X-axis**: Width (left-right) - Same as NX
- **Y-axis**: Height (up-down) - Different from NX!
- **Z-axis**: Depth (front-back) - Different from NX!

### Coordinate Transformation
To convert from NX to Three.js coordinates:
```javascript
threejs.x = nx.x  // Width remains the same
threejs.y = nx.z  // NX height becomes Three.js Y
threejs.z = nx.y  // NX length becomes Three.js Z (depth)
```

## Panel Positioning Mapping

### Front Panel
- **NX Position**: (Width/2, 0, Height/2)
- **Three.js Position**: [0, Height/2, -Length/2 + thickness/2]
- **Dimensions**: [Width, Height, thickness]

### Back Panel  
- **NX Position**: (Width/2, Length, Height/2)
- **Three.js Position**: [0, Height/2, Length/2 - thickness/2]
- **Dimensions**: [Width, Height, thickness]

### Left Panel
- **NX Position**: (0, Length/2, Height/2)
- **Three.js Position**: [-Width/2 + thickness/2, Height/2, 0]
- **Dimensions**: [thickness, Height, Length]

### Right Panel
- **NX Position**: (Width, Length/2, Height/2)
- **Three.js Position**: [Width/2 - thickness/2, Height/2, 0]
- **Dimensions**: [thickness, Height, Length]

### Top Panel
- **NX Position**: (Width/2, Length/2, Height)
- **Three.js Position**: [0, Height - thickness/2, 0]
- **Dimensions**: [Width, thickness, Length]

### Bottom/Floorboards
- **NX Position**: (Width/2, Length/2, 0)
- **Three.js Position**: [0, thickness/2, 0]
- **Dimensions**: [Width, thickness, Length]

## Critical Calculations

### Panel Assembly Thickness
```
panel_assembly_thickness = panel_thickness + cleat_thickness
```
This affects the positioning of all panels as they must account for the combined thickness of the panel material and cleats.

### End Panel Adjustments
End panels (left/right) are sandwiched between front and back panels:
```
end_panel_length = overall_length - (2 * panel_assembly_thickness)
```

### Vertical Cleat Material Additions
When panels exceed 48" in width, additional vertical cleats are added:
```javascript
if (panel_width > 48) {
    additional_cleats = Math.ceil((panel_width - 48) / 48);
    material_needed = additional_cleats * cleat_width;
    panel_width += material_needed;
    overall_dimension += material_needed;
}
```

## Common Issues and Solutions

### Issue 1: Panels Not Aligning
**Cause**: Not accounting for panel assembly thickness
**Solution**: Always use `panel_assembly_thickness` (panel + cleat) when calculating positions

### Issue 2: Coordinate Mismatch
**Cause**: Direct use of NX coordinates in Three.js
**Solution**: Apply the transformation: (x, y, z) → (x, z, y)

### Issue 3: Origin Confusion
**Cause**: Three.js uses center-based positioning by default
**Solution**: Adjust positions to account for centered geometry in Three.js

## Verification Checklist

When implementing or debugging coordinate mappings:

1. ✅ Verify origin is at front-left-bottom corner
2. ✅ Check X-axis points right in both systems
3. ✅ Confirm Y/Z swap between NX and Three.js
4. ✅ Account for panel assembly thickness
5. ✅ Test with different crate sizes
6. ✅ Verify cleat material adjustments are applied
7. ✅ Check that all panels connect properly at edges

## Example Coordinate Conversion

For a crate with dimensions 96" × 48" × 30":
```
NX Front Panel Center: (48, 0, 15)
Three.js Front Panel: [0, 15, -48]

NX Top Panel Center: (48, 48, 30)  
Three.js Top Panel: [0, 30, 0]

NX Right Panel Center: (96, 48, 15)
Three.js Right Panel: [48, 15, 0]
```

## Testing Commands

To verify coordinate mappings:
```bash
# Desktop version
python test_nx_generation.py

# Web version  
cd web && npm run test:coordinates

# Compare outputs
python test_nx_comparison.py
```

## References

- NX Expression Format: `autocrate/nx_expressions_generator.py`
- Web 3D Viewer: `web/src/components/ProfessionalCrateViewer-fixed.tsx`
- Calculation Engine: `web/src/lib/autocrate-calculations-fixed.ts`
- Desktop GUI: `main.py`

---
*Last Updated: August 2024*
*Version: 1.0.0*