'use client';

import React, { useRef, useState, useMemo, Suspense, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import {
  OrbitControls,
  PerspectiveCamera,
  Environment,
  ContactShadows,
  Text,
  Box as DreiBox,
  Html,
  useTexture,
  Stage,
  AccumulativeShadows,
  RandomizedLight,
  Backdrop,
  Grid,
  Center,
  PresentationControls,
  Float,
  MeshReflectorMaterial,
  useHelper,
  Stats
} from '@react-three/drei';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  ButtonGroup,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  Stack,
  Switch,
  FormControlLabel,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  ViewInAr,
  ZoomIn,
  ZoomOut,
  RotateLeft,
  RotateRight,
  Fullscreen,
  FullscreenExit,
  Refresh,
  Settings,
  Visibility,
  VisibilityOff,
  CameraAlt,
  Download,
  Share,
  Layers,
  Animation,
  Palette,
  WbSunny,
  AutoFixHigh,
  ThreeDRotation,
  Timeline,
  Build,
  Info,
  ViewModule,
  Texture,
  GridOn,
  Straighten
} from '@mui/icons-material';
import * as THREE from 'three';
import { EffectComposer, Bloom, DepthOfField, Vignette, ChromaticAberration, SSAO } from '@react-three/postprocessing';
import { useControls } from 'leva';
import { animated, useSpring } from '@react-spring/three';

// Wood texture types
const WOOD_MATERIALS = {
  oak: {
    name: 'Oak',
    color: '#8B7355',
    roughness: 0.8,
    metalness: 0.1
  },
  pine: {
    name: 'Pine',
    color: '#DEB887',
    roughness: 0.7,
    metalness: 0.05
  },
  mahogany: {
    name: 'Mahogany',
    color: '#6F4E37',
    roughness: 0.6,
    metalness: 0.15
  },
  birch: {
    name: 'Birch Plywood',
    color: '#F5DEB3',
    roughness: 0.5,
    metalness: 0.02
  },
  walnut: {
    name: 'Walnut',
    color: '#4B3621',
    roughness: 0.7,
    metalness: 0.1
  }
};

// Camera presets
const CAMERA_PRESETS = {
  isometric: { position: [50, 50, 50], rotation: [0, 0, 0] },
  front: { position: [0, 0, 80], rotation: [0, 0, 0] },
  side: { position: [80, 0, 0], rotation: [0, Math.PI / 2, 0] },
  top: { position: [0, 80, 0], rotation: [-Math.PI / 2, 0, 0] },
  perspective: { position: [60, 40, 60], rotation: [0, 0, 0] }
};

interface CrateComponentProps {
  type: string;
  position: [number, number, number];
  dimensions: [number, number, number];
  material: string;
  opacity?: number;
  isExploded?: boolean;
  explodeOffset?: [number, number, number];
  showDimensions?: boolean;
  highlighted?: boolean;
  onHover?: (hovered: boolean) => void;
  onClick?: () => void;
}

// Individual crate component
const CrateComponent: React.FC<CrateComponentProps> = ({
  type,
  position,
  dimensions,
  material,
  opacity = 1,
  isExploded = false,
  explodeOffset = [0, 0, 0],
  showDimensions = false,
  highlighted = false,
  onHover,
  onClick
}) => {
  const meshRef = useRef<THREE.Mesh>();
  const [hovered, setHovered] = useState(false);
  
  const springProps = useSpring({
    position: isExploded 
      ? [position[0] + explodeOffset[0], position[1] + explodeOffset[1], position[2] + explodeOffset[2]]
      : position,
    scale: highlighted ? [1.02, 1.02, 1.02] : [1, 1, 1],
    config: { tension: 300, friction: 30 }
  });

  const materialProps = {
    color: highlighted ? '#ff9800' : WOOD_MATERIALS[material as keyof typeof WOOD_MATERIALS].color,
    roughness: WOOD_MATERIALS[material as keyof typeof WOOD_MATERIALS].roughness,
    metalness: WOOD_MATERIALS[material as keyof typeof WOOD_MATERIALS].metalness,
    transparent: opacity < 1,
    opacity: opacity
  };

  return (
    <animated.mesh
      ref={meshRef}
      position={springProps.position as any}
      scale={springProps.scale as any}
      castShadow
      receiveShadow
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
        onHover?.(true);
      }}
      onPointerOut={(e) => {
        e.stopPropagation();
        setHovered(false);
        onHover?.(false);
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick?.();
      }}
    >
      <boxGeometry args={dimensions} />
      <meshStandardMaterial {...materialProps} />
      
      {showDimensions && hovered && (
        <Html center distanceFactor={10}>
          <div style={{
            background: 'rgba(0,0,0,0.8)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            whiteSpace: 'nowrap'
          }}>
            {type}: {dimensions[0].toFixed(1)}" × {dimensions[1].toFixed(1)}" × {dimensions[2].toFixed(1)}"
          </div>
        </Html>
      )}
    </animated.mesh>
  );
};

// Fixed Crate Assembly with proper coordinate system
const CrateAssembly: React.FC<{
  crateData: any;
  exploded: boolean;
  showDimensions: boolean;
  showWireframe: boolean;
  material: string;
  highlightedComponent?: string;
}> = ({ crateData, exploded, showDimensions, showWireframe, material, highlightedComponent }) => {
  const [hoveredComponent, setHoveredComponent] = useState<string | null>(null);
  
  // Parse crate data with proper dimension mapping
  const dimensions = useMemo(() => {
    if (!crateData) {
      return {
        length: 48,
        width: 40,
        height: 36,
        panelThickness: 0.75,
        cleatThickness: 1.5,
        floorboardThickness: 1.5,
        skidHeight: 3.5
      };
    }
    
    // Map from calculation results to 3D dimensions
    // The calculation uses different naming conventions
    return {
      // Overall crate dimensions from calculation
      length: crateData.crate_dimensions?.overall_length_od || 
              crateData.crate_dimensions?.external_length || 48,
      width: crateData.crate_dimensions?.overall_width_od || 
             crateData.crate_dimensions?.external_width || 40,
      height: crateData.crate_dimensions?.external_height || 36,
      
      // Panel and material dimensions
      panelThickness: crateData.inputs?.panel_thickness || 0.75,
      cleatThickness: crateData.inputs?.cleat_thickness || 1.5,
      floorboardThickness: crateData.inputs?.floorboard_thickness || 
                          crateData.floorboard_parameters?.actual_thickness || 1.5,
      skidHeight: crateData.skid_parameters?.actual_height || 3.5,
      skidWidth: crateData.skid_parameters?.actual_width || 3.5,
      
      // Panel specific dimensions
      frontPanelWidth: crateData.panels?.front?.width || 40,
      frontPanelHeight: crateData.panels?.front?.height || 36,
      backPanelWidth: crateData.panels?.back?.width || 40,
      backPanelHeight: crateData.panels?.back?.height || 36,
      leftPanelWidth: crateData.panels?.left?.width || 48,
      leftPanelHeight: crateData.panels?.left?.height || 36,
      rightPanelWidth: crateData.panels?.right?.width || 48,
      rightPanelHeight: crateData.panels?.right?.height || 36,
      topPanelWidth: crateData.panels?.top?.width || 40,
      topPanelLength: crateData.panels?.top?.length || 
                     crateData.panels?.top?.height || 48
    };
  }, [crateData]);
  
  // Calculate component positions and dimensions using NX coordinate system
  const components = useMemo(() => {
    const comps = [];
    const panelAssemblyThickness = dimensions.panelThickness + dimensions.cleatThickness;
    
    // In NX/AutoCrate coordinate system:
    // X = Width (left-right)
    // Y = Length (front-back) 
    // Z = Height (up-down)
    
    // For Three.js display, we'll map:
    // X (width) -> X
    // Y (length) -> Z (depth)
    // Z (height) -> Y (vertical)
    
    const halfWidth = dimensions.width / 2;
    const halfLength = dimensions.length / 2;
    
    // Front panel (at Y=0 in NX, maps to -Z in Three.js)
    comps.push({
      type: 'front_panel',
      position: [0, dimensions.frontPanelHeight/2, -halfLength + panelAssemblyThickness/2] as [number, number, number],
      dimensions: [dimensions.frontPanelWidth, dimensions.frontPanelHeight, panelAssemblyThickness] as [number, number, number],
      explodeOffset: [0, 0, -15] as [number, number, number]
    });
    
    // Back panel (at Y=length in NX, maps to +Z in Three.js)
    comps.push({
      type: 'back_panel', 
      position: [0, dimensions.backPanelHeight/2, halfLength - panelAssemblyThickness/2] as [number, number, number],
      dimensions: [dimensions.backPanelWidth, dimensions.backPanelHeight, panelAssemblyThickness] as [number, number, number],
      explodeOffset: [0, 0, 15] as [number, number, number]
    });
    
    // Left panel (at X=0 in NX)
    comps.push({
      type: 'left_panel',
      position: [-halfWidth + panelAssemblyThickness/2, dimensions.leftPanelHeight/2, 0] as [number, number, number],
      dimensions: [panelAssemblyThickness, dimensions.leftPanelHeight, dimensions.leftPanelWidth] as [number, number, number],
      explodeOffset: [-15, 0, 0] as [number, number, number]
    });
    
    // Right panel (at X=width in NX)
    comps.push({
      type: 'right_panel',
      position: [halfWidth - panelAssemblyThickness/2, dimensions.rightPanelHeight/2, 0] as [number, number, number],
      dimensions: [panelAssemblyThickness, dimensions.rightPanelHeight, dimensions.rightPanelWidth] as [number, number, number],
      explodeOffset: [15, 0, 0] as [number, number, number]
    });
    
    // Top panel (if exists)
    if (crateData?.panels?.top) {
      comps.push({
        type: 'top_panel',
        position: [0, dimensions.height - panelAssemblyThickness/2, 0] as [number, number, number],
        dimensions: [dimensions.topPanelWidth, panelAssemblyThickness, dimensions.topPanelLength] as [number, number, number],
        explodeOffset: [0, 20, 0] as [number, number, number]
      });
    }
    
    // Skids (run along Y-axis/length)
    if (crateData?.skid_parameters) {
      const skidCount = crateData.skid_parameters.count || 3;
      const skidPitch = crateData.skid_parameters.pitch || dimensions.width / (skidCount - 1);
      const skidStartX = -halfWidth + dimensions.skidWidth/2;
      
      for (let i = 0; i < skidCount; i++) {
        const xPos = skidStartX + i * skidPitch;
        comps.push({
          type: `skid_${i}`,
          position: [xPos, -dimensions.skidHeight/2, 0] as [number, number, number],
          dimensions: [dimensions.skidWidth, dimensions.skidHeight, dimensions.length] as [number, number, number],
          explodeOffset: [0, -10 - i * 3, 0] as [number, number, number]
        });
      }
    }
    
    // Floorboards (run across width)
    if (crateData?.floorboard_parameters?.instances) {
      const activeFloorboards = crateData.floorboard_parameters.instances
        .filter((fb: any) => fb.suppress_flag === 1);
      
      activeFloorboards.forEach((fb: any, i: number) => {
        const zPos = -halfLength + fb.y_pos_abs + fb.actual_width/2;
        comps.push({
          type: `floorboard_${i}`,
          position: [0, dimensions.floorboardThickness/2, zPos] as [number, number, number],
          dimensions: [dimensions.width, dimensions.floorboardThickness, fb.actual_width] as [number, number, number],
          explodeOffset: [0, -5 - i * 2, 0] as [number, number, number]
        });
      });
    }
    
    return comps;
  }, [crateData, dimensions]);
  
  return (
    <group>
      {components.map((comp, index) => (
        <CrateComponent
          key={`${comp.type}_${index}`}
          type={comp.type}
          position={comp.position}
          dimensions={comp.dimensions}
          material={material}
          isExploded={exploded}
          explodeOffset={comp.explodeOffset}
          showDimensions={showDimensions}
          highlighted={highlightedComponent === comp.type || hoveredComponent === comp.type}
          onHover={(hovered) => setHoveredComponent(hovered ? comp.type : null)}
          opacity={showWireframe ? 0.3 : 1}
        />
      ))}
      
      {/* Overall dimensions display */}
      {showDimensions && !exploded && (
        <Html
          position={[0, dimensions.height + 10, 0]}
          center
          distanceFactor={10}
          style={{
            transition: 'opacity 0.5s',
            pointerEvents: 'none'
          }}
        >
          <div style={{
            background: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(245,245,245,0.95))',
            color: '#2c3e50',
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '600',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            whiteSpace: 'nowrap',
            border: '1px solid rgba(0,0,0,0.1)',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}>
            L: {dimensions.length.toFixed(1)}" × W: {dimensions.width.toFixed(1)}" × H: {dimensions.height.toFixed(1)}"
          </div>
        </Html>
      )}
    </group>
  );
};

// Main professional viewer component
interface ProfessionalCrateViewerProps {
  crateData?: any;
  className?: string;
}

const ProfessionalCrateViewer: React.FC<ProfessionalCrateViewerProps> = ({
  crateData,
  className
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [exploded, setExploded] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const [showWireframe, setShowWireframe] = useState(false);
  const [material, setMaterial] = useState('oak');
  const [showDimensions, setShowDimensions] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [cameraPreset, setCameraPreset] = useState('perspective');
  const [highlightedComponent, setHighlightedComponent] = useState<string | undefined>();
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Log data for debugging
  useEffect(() => {
    if (crateData) {
      console.log('ProfessionalCrateViewer received data:', crateData);
    }
  }, [crateData]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        width: '100%',
        height: isFullscreen ? '100vh' : '600px',
        backgroundColor: '#f5f5f5',
        borderRadius: isFullscreen ? 0 : 2,
        overflow: 'hidden'
      }}
      className={className}
    >
      {/* Canvas */}
      <Canvas
        shadows
        camera={{ position: CAMERA_PRESETS[cameraPreset as keyof typeof CAMERA_PRESETS].position as [number, number, number], fov: 50 }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <pointLight position={[-10, -10, -5]} intensity={0.4} />
        
        <Suspense fallback={null}>
          {crateData ? (
            <CrateAssembly
              crateData={crateData}
              exploded={exploded}
              showDimensions={showDimensions}
              showWireframe={showWireframe}
              material={material}
              highlightedComponent={highlightedComponent}
            />
          ) : (
            // Show placeholder when no data
            <group>
              <mesh position={[0, 0, 0]}>
                <boxGeometry args={[40, 36, 48]} />
                <meshStandardMaterial color="#999" wireframe opacity={0.3} transparent />
              </mesh>
              <Html center>
                <div style={{
                  background: 'rgba(0,0,0,0.7)',
                  color: 'white',
                  padding: '10px 20px',
                  borderRadius: '5px',
                  whiteSpace: 'nowrap'
                }}>
                  Calculate a crate design to see 3D preview
                </div>
              </Html>
            </group>
          )}
          
          {showGrid && (
            <Grid
              renderOrder={-1}
              position={[0, -20, 0]}
              infiniteGrid
              cellSize={10}
              cellThickness={0.6}
              cellColor={'#6f6f6f'}
              sectionSize={50}
              sectionThickness={1.5}
              sectionColor={'#9d9d9d'}
              fadeDistance={200}
              fadeStrength={1}
              followCamera={false}
            />
          )}
          
          <Environment preset="apartment" />
          <ContactShadows
            position={[0, -20, 0]}
            opacity={0.4}
            scale={100}
            blur={2}
            far={20}
          />
        </Suspense>
        
        <OrbitControls
          enablePan
          enableZoom
          enableRotate
          autoRotate={autoRotate}
          autoRotateSpeed={1}
        />
      </Canvas>
      
      {/* Controls */}
      <Paper
        sx={{
          position: 'absolute',
          top: 16,
          left: 16,
          p: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(10px)',
          borderRadius: 2,
          minWidth: 200
        }}
        elevation={3}
      >
        <Stack spacing={2}>
          <Typography variant="subtitle2" fontWeight={600}>
            View Controls
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={exploded}
                onChange={(e) => setExploded(e.target.checked)}
                size="small"
              />
            }
            label="Exploded View"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={showDimensions}
                onChange={(e) => setShowDimensions(e.target.checked)}
                size="small"
              />
            }
            label="Show Dimensions"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={autoRotate}
                onChange={(e) => setAutoRotate(e.target.checked)}
                size="small"
              />
            }
            label="Auto Rotate"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={showGrid}
                onChange={(e) => setShowGrid(e.target.checked)}
                size="small"
              />
            }
            label="Show Grid"
          />
          
          <Divider />
          
          <FormControl size="small" fullWidth>
            <InputLabel>Material</InputLabel>
            <Select
              value={material}
              onChange={(e) => setMaterial(e.target.value)}
              label="Material"
            >
              {Object.entries(WOOD_MATERIALS).map(([key, value]) => (
                <MenuItem key={key} value={key}>{value.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl size="small" fullWidth>
            <InputLabel>Camera</InputLabel>
            <Select
              value={cameraPreset}
              onChange={(e) => setCameraPreset(e.target.value)}
              label="Camera"
            >
              {Object.keys(CAMERA_PRESETS).map((key) => (
                <MenuItem key={key} value={key}>
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </Paper>
      
      {/* Fullscreen button */}
      <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
        <IconButton
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 1)'
            }
          }}
          onClick={toggleFullscreen}
        >
          {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
        </IconButton>
      </Tooltip>
    </Box>
  );
};

export default ProfessionalCrateViewer;