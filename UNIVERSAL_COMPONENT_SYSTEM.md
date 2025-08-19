# Universal Component Orientation System
## AutoCrate v12.1.4 Technical Documentation

### Overview

AutoCrate's Universal Component Orientation System provides a comprehensive framework for positioning and orienting any 3D component in crate assemblies. This system uses intuitive direction vectors to achieve full 6DOF (six degrees of freedom) control while eliminating mathematical complexities like gimbal lock.

### Core Principles

#### 1. Direction Vector Philosophy
Every 3D component is defined by three orthogonal (perpendicular) direction vectors that represent the component's local coordinate system within the global crate coordinate system.

#### 2. Global Coordinate System
- **X-axis**: Sideways (left/right)
- **Y-axis**: Away from screen (depth into screen)
- **Z-axis**: Up (vertical)

#### 3. Universal Variable Structure
Every component uses exactly 13 variables:
```
// Position (3 variables)
[Inch]COMP_XX_X        // Global X position
[Inch]COMP_XX_Y        // Global Y position  
[Inch]COMP_XX_Z        // Global Z position

// Orientation (9 variables) - Local axes in global coordinates
COMP_XX_X_DIR_X        // Local X-axis direction X component
COMP_XX_X_DIR_Y        // Local X-axis direction Y component
COMP_XX_X_DIR_Z        // Local X-axis direction Z component
COMP_XX_Y_DIR_X        // Local Y-axis direction X component
COMP_XX_Y_DIR_Y        // Local Y-axis direction Y component
COMP_XX_Y_DIR_Z        // Local Y-axis direction Z component
COMP_XX_Z_DIR_X        // Local Z-axis direction X component
COMP_XX_Z_DIR_Y        // Local Z-axis direction Y component
COMP_XX_Z_DIR_Z        // Local Z-axis direction Z component

// Control (1 variable)
COMP_XX_SUPPRESS       // 0=hide, 1=show
```

### Component Types and Axis Definitions

#### Klimps (KL_XX) - L-Shaped Angle Brackets
**Purpose**: Structural corner reinforcement between crate panels

**Axis Definitions**:
- **X-axis**: Width direction (across bracket thickness)
- **Y-axis**: Short side direction  
- **Z-axis**: Long side direction

**Panel Orientations**:
- **Top Panel**: Long side down (-Z), short side away (+Y), width sideways (±X)
- **Left Panel**: Long side away (+Y), short side inward (+X), width vertical (±Z)
- **Right Panel**: Long side away (+Y), short side inward (-X), width vertical (±Z)

#### Vinyl Labels/Decals (VN_XX, DC_XX)
**Purpose**: Informational labels and graphics

**Axis Definitions**:
- **X-axis**: Text reading direction (left-to-right)
- **Y-axis**: Text "up" direction (bottom-to-top of letters)
- **Z-axis**: Surface normal (perpendicular away from surface)

#### Lag Screws (LS_XX)
**Purpose**: Structural fasteners

**Axis Definitions**:
- **X-axis**: Screw head slot/hex orientation
- **Y-axis**: Perpendicular reference for head orientation
- **Z-axis**: Screw insertion/drilling direction

#### Handles (HD_XX)
**Purpose**: Lifting and carrying assistance

**Axis Definitions**:
- **X-axis**: Handle grip direction (length of handle)
- **Y-axis**: Handle "up" direction (which way is up for the handle)
- **Z-axis**: Handle mounting direction (perpendicular to mounting surface)

### Siemens NX Implementation

#### Phase 1: Import Expression File
1. **Tools** → **Expression**
2. **Import** → Select your `.exp` file
3. Verify all component variables imported correctly

#### Phase 2: Create Parametric Coordinate Systems
For each component:

1. **Insert** → **Datum/Point** → **Coordinate System**
2. **Origin Section**:
   - X: Enter `COMP_XX_X`
   - Y: Enter `COMP_XX_Y`  
   - Z: Enter `COMP_XX_Z`
3. **Type**: Select **"By Vectors"**
4. **X-Axis Direction**:
   - X Component: `COMP_XX_X_DIR_X`
   - Y Component: `COMP_XX_X_DIR_Y`
   - Z Component: `COMP_XX_X_DIR_Z`
5. **Y-Axis Direction**:
   - X Component: `COMP_XX_Y_DIR_X`
   - Y Component: `COMP_XX_Y_DIR_Y`
   - Z Component: `COMP_XX_Y_DIR_Z`
6. **OK** → Rename to `COMP_XX_CSYS`

#### Phase 3: Insert and Constrain Components
1. **Assemblies** → **Add Component** → Select part file
2. **Assemblies** → **Assembly Constraints**
3. **Mate**: Component origin to coordinate system origin
4. **Align** all three axes:
   - Component X-axis to coordinate system X-axis
   - Component Y-axis to coordinate system Y-axis  
   - Component Z-axis to coordinate system Z-axis

#### Phase 4: Set Up Conditional Suppression
1. Right-click component → **Properties** → **Conditional**
2. Check **"Suppress using expression"**
3. Enter: `COMP_XX_SUPPRESS == 0`
4. **OK**

### Practical Examples

#### Example 1: Top Panel Klimp
```
// Position at top-left of crate
[Inch]KL_1_X = -54.25    // Left side
[Inch]KL_1_Y = 0.000     // On top surface
[Inch]KL_1_Z = 140.5     // Top height

// L-bracket orientation: long side down, short side away
KL_1_X_DIR_X = 1.000     // Width spans sideways
KL_1_X_DIR_Y = 0.000
KL_1_X_DIR_Z = 0.000
KL_1_Y_DIR_X = 0.000     // Short side extends away
KL_1_Y_DIR_Y = 1.000
KL_1_Y_DIR_Z = 0.000
KL_1_Z_DIR_X = 0.000     // Long side extends down
KL_1_Z_DIR_Y = 0.000
KL_1_Z_DIR_Z = -1.000

KL_1_SUPPRESS = 1        // Show this klimp
```

#### Example 2: Vinyl Label on Front Panel
```
// Position on front panel center
[Inch]VN_1_X = 0.000     // Centered sideways
[Inch]VN_1_Y = -1.000    // Front surface
[Inch]VN_1_Z = 70.000    // Middle height

// Text reads horizontally, right-side-up
VN_1_X_DIR_X = 1.000     // Text direction (left-to-right)
VN_1_X_DIR_Y = 0.000
VN_1_X_DIR_Z = 0.000
VN_1_Y_DIR_X = 0.000     // Text "up" direction
VN_1_Y_DIR_Y = 0.000
VN_1_Y_DIR_Z = 1.000
VN_1_Z_DIR_X = 0.000     // Surface normal (outward)
VN_1_Z_DIR_Y = -1.000
VN_1_Z_DIR_Z = 0.000

VN_1_SUPPRESS = 1
```

#### Example 3: Lag Screw on Right Panel
```
// Position on right panel
[Inch]LS_1_X = 67.000    // Right panel surface
[Inch]LS_1_Y = 30.000    // Toward front
[Inch]LS_1_Z = 50.000    // Lower position

// Screw drives inward with horizontal head orientation
LS_1_X_DIR_X = 0.000     // Head orientation (horizontal)
LS_1_X_DIR_Y = 0.000
LS_1_X_DIR_Z = 1.000
LS_1_Y_DIR_X = 0.000     // Head reference direction  
LS_1_Y_DIR_Y = 1.000
LS_1_Y_DIR_Z = 0.000
LS_1_Z_DIR_X = -1.000    // Screw insertion (inward)
LS_1_Z_DIR_Y = 0.000
LS_1_Z_DIR_Z = 0.000

LS_1_SUPPRESS = 1
```

### System Benefits

#### Engineering Advantages
- **Intuitive Control**: Each axis has clear physical meaning
- **No Gimbal Lock**: Direction vectors eliminate mathematical singularities
- **Visual Debugging**: Easy to verify orientations by inspection
- **Engineering-Friendly**: Matches how engineers think about components

#### Technical Advantages
- **Universal Framework**: Same pattern for all component types
- **Scalable**: Add unlimited component types with consistent structure
- **NX-Compatible**: Direct mapping to CAD coordinate systems
- **Parametric**: Full expression-driven updates in real-time

#### Development Advantages
- **Consistent**: Same 13-variable pattern across all components
- **Extensible**: Easy to add new component types
- **Maintainable**: Clear naming conventions and documentation
- **Future-Proof**: Supports any orientation requirement

### Adding New Component Types

To add a new component type (example: Hinges):

1. **Define Axis Meanings**:
   - X-axis: Hinge pin direction (axis of rotation)
   - Y-axis: Door swing reference direction
   - Z-axis: Mounting surface normal

2. **Create Variable Structure**:
   ```
   [Inch]HG_XX_X/Y/Z          // Position
   HG_XX_X_DIR_X/Y/Z          // Pin direction
   HG_XX_Y_DIR_X/Y/Z          // Swing reference
   HG_XX_Z_DIR_X/Y/Z          // Mount normal
   HG_XX_SUPPRESS             // Visibility
   ```

3. **Document Orientations**: Create examples for different panel locations

4. **Implement in Code**: Follow the established patterns in the expression generator

### Validation Requirements

#### Mathematical Validation
- Each direction vector must have unit length: √(X² + Y² + Z²) = 1.0
- Direction vectors must be orthogonal: X·Y = 0, Y·Z = 0, Z·X = 0
- Right-handed coordinate system: Z = X × Y

#### Engineering Validation
- Component orientations must make physical sense
- Mounting directions must be appropriate for surfaces
- Component interference must be checked

#### NX Validation
- Coordinate systems must create without errors
- Component constraints must fully define position
- Suppress logic must work correctly

### Troubleshooting

#### Common Issues
1. **Invalid Coordinate System**: Check vector orthogonality and unit length
2. **Wrong Orientation**: Verify axis definitions match component geometry
3. **Expression Linking Fails**: Check exact spelling and variable existence
4. **Suppress Not Working**: Verify conditional expression syntax

#### Debug Tools
Create verification expressions:
```
// Check vector lengths
MAG_X_1 = sqrt(KL_1_X_DIR_X^2 + KL_1_X_DIR_Y^2 + KL_1_X_DIR_Z^2)

// Check orthogonality  
DOT_XY_1 = KL_1_X_DIR_X*KL_1_Y_DIR_X + KL_1_X_DIR_Y*KL_1_Y_DIR_Y + KL_1_X_DIR_Z*KL_1_Y_DIR_Z
```

All should equal 1.0 and 0.0 respectively.

### Conclusion

The Universal Component Orientation System provides AutoCrate with a robust, intuitive, and extensible framework for positioning any 3D component. By using direction vectors with clear physical meanings, the system achieves mathematical rigor while remaining accessible to engineers and CAD users.

This system positions AutoCrate as a comprehensive platform for crate design automation, capable of handling not just structural components but also hardware, labels, fasteners, and future component types with consistent, professional-grade precision.