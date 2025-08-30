'use client';

import React, { useRef, useState, useMemo, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import {
  OrbitControls,
  Environment,
  ContactShadows,
  Html,
  Grid,
  PerspectiveCamera
} from '@react-three/drei';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Stack,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Chip,
  Alert
} from '@mui/material';
import {
  Fullscreen,
  FullscreenExit,
  Layers,
  Build,
  Straighten,
  ViewInAr,
  GridOn
} from '@mui/icons-material';
import * as THREE from 'three';
import { animated, useSpring } from '@react-spring/three';

// Enhanced material definitions
const MATERIALS = {
  plywood: {
    name: 'CDX Plywood',
    color: '#C4915C',
    roughness: 0.9,
    metalness: 0.0,
    clearcoat: 0.1
  },
  osb: {
    name: 'OSB',
    color: '#B8956A',
    roughness: 0.95,
    metalness: 0.0,
    clearcoat: 0.05
  },
  lumber: {
    name: 'Pine Lumber',
    color: '#D4A373',
    roughness: 0.85,
    metalness: 0.0,
    clearcoat: 0.15
  },
  metal: {
    name: 'Steel Hardware',
    color: '#606060',
    roughness: 0.3,
    metalness: 0.9,
    clearcoat: 0
  }
};

// Component type definitions
type ComponentType = 'panel' | 'cleat' | 'skid' | 'floorboard' | 'hardware';

interface CrateComponentProps {
  type: ComponentType;
  subType: string;
  position: [number, number, number];
  dimensions: [number, number, number];
  material: keyof typeof MATERIALS;
  rotation?: [number, number, number];
  opacity?: number;
  isExploded?: boolean;
  explodeOffset?: [number, number, number];
  showDimensions?: boolean;
  highlighted?: boolean;
  visible?: boolean;
  onHover?: (hovered: boolean, info: any) => void;
  onClick?: () => void;
}

// Enhanced Crate Component with proper materials and details
const CrateComponent: React.FC<CrateComponentProps> = ({
  type,
  subType,
  position,
  dimensions,
  material,
  rotation = [0, 0, 0],
  opacity = 1,
  isExploded = false,
  explodeOffset = [0, 0, 0],
  showDimensions = false,
  highlighted = false,
  visible = true,
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
    opacity: visible ? opacity : 0,
    config: { tension: 300, friction: 30 }
  });

  const mat = MATERIALS[material];
  const materialProps = {
    color: highlighted ? '#ff9800' : (hovered ? '#ffa726' : mat.color),
    roughness: mat.roughness,
    metalness: mat.metalness,
    transparent: opacity < 1,
    opacity: opacity,
    side: THREE.DoubleSide
  };

  // Add grain texture for wood materials
  const isWood = material === 'plywood' || material === 'osb' || material === 'lumber';

  if (!visible) return null;

  return (
    <animated.mesh
      ref={meshRef}
      position={springProps.position as any}
      rotation={rotation}
      scale={springProps.scale as any}
      castShadow
      receiveShadow
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
        onHover?.(true, { type, subType, dimensions });
      }}
      onPointerOut={(e) => {
        e.stopPropagation();
        setHovered(false);
        onHover?.(false, null);
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick?.();
      }}
    >
      <boxGeometry args={dimensions} />
      <meshStandardMaterial {...materialProps}>
        {isWood && (
          <>
            <primitive attach="map" object={generateWoodTexture()} />
            <primitive attach="normalMap" object={generateWoodNormalMap()} />
          </>
        )}
      </meshStandardMaterial>
      
      {showDimensions && hovered && (
        <Html center distanceFactor={10}>
          <div style={{
            background: 'rgba(0,0,0,0.85)',
            color: 'white',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '11px',
            whiteSpace: 'nowrap',
            fontFamily: 'monospace',
            border: '1px solid rgba(255,255,255,0.2)'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{subType}</div>
            <div>{dimensions[0].toFixed(2)}" × {dimensions[1].toFixed(2)}" × {dimensions[2].toFixed(2)}"</div>
            <div style={{ fontSize: '10px', opacity: 0.8, marginTop: '2px' }}>{mat.name}</div>
          </div>
        </Html>
      )}
    </animated.mesh>
  );
};

// Generate wood texture procedurally
function generateWoodTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d')!;
  
  // Wood grain pattern
  const gradient = ctx.createLinearGradient(0, 0, 512, 0);
  gradient.addColorStop(0, '#D4A373');
  gradient.addColorStop(0.5, '#C4915C');
  gradient.addColorStop(1, '#B8956A');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 512, 512);
  
  // Add grain lines
  ctx.strokeStyle = 'rgba(0,0,0,0.1)';
  ctx.lineWidth = 1;
  for (let i = 0; i < 512; i += 4) {
    ctx.beginPath();
    ctx.moveTo(0, i + Math.sin(i * 0.01) * 10);
    ctx.lineTo(512, i + Math.sin(i * 0.01 + 1) * 10);
    ctx.stroke();
  }
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(2, 2);
  return texture;
}

// Generate wood normal map
function generateWoodNormalMap() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d')!;
  
  // Normal map base color
  ctx.fillStyle = 'rgb(128, 128, 255)';
  ctx.fillRect(0, 0, 512, 512);
  
  // Add depth variation
  for (let i = 0; i < 100; i++) {
    const x = Math.random() * 512;
    const y = Math.random() * 512;
    const radius = Math.random() * 20 + 5;
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
    gradient.addColorStop(0, 'rgba(128, 128, 255, 0.5)');
    gradient.addColorStop(1, 'rgba(128, 128, 200, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
  }
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(2, 2);
  return texture;
}

// Complete Crate Assembly with all components
const EnhancedCrateAssembly: React.FC<{
  crateData: any;
  exploded: boolean;
  showDimensions: boolean;
  showComponents: {
    panels: boolean;
    cleats: boolean;
    skids: boolean;
    floorboards: boolean;
    hardware: boolean;
  };
  wireframe: boolean;
  highlightedComponent?: string;
}> = ({ 
  crateData, 
  exploded, 
  showDimensions, 
  showComponents,
  wireframe,
  highlightedComponent 
}) => {
  const [hoveredComponent, setHoveredComponent] = useState<any>(null);
  
  // Parse and calculate all dimensions
  const dimensions = useMemo(() => {
    if (!crateData) {
      return {
        length: 48,
        width: 40,
        height: 36,
        panelThickness: 0.75,
        cleatThickness: 1.5,
        cleatWidth: 3.5,
        floorboardThickness: 1.5,
        skidHeight: 3.5,
        skidWidth: 3.5
      };
    }
    
    return {
      length: crateData.crate_dimensions?.external_length || 48,
      width: crateData.crate_dimensions?.external_width || 40,
      height: crateData.crate_dimensions?.external_height || 36,
      panelThickness: crateData.inputs?.panel_thickness || 0.75,
      cleatThickness: crateData.inputs?.cleat_thickness || 1.5,
      cleatWidth: crateData.inputs?.cleat_member_width || 3.5,
      floorboardThickness: crateData.inputs?.floorboard_thickness || 1.5,
      skidHeight: crateData.skid_parameters?.actual_height || 3.5,
      skidWidth: crateData.skid_parameters?.actual_width || 3.5,
      
      // Internal dimensions
      internalLength: crateData.crate_dimensions?.internal_length || 46,
      internalWidth: crateData.crate_dimensions?.internal_width || 38,
      internalHeight: crateData.crate_dimensions?.internal_height || 34
    };
  }, [crateData]);
  
  // Generate all components
  const components = useMemo(() => {
    const comps: any[] = [];
    const halfWidth = dimensions.width / 2;
    const halfLength = dimensions.length / 2;
    const halfHeight = dimensions.height / 2;
    
    // PANELS - Just the plywood sheets
    if (showComponents.panels) {
      // Front panel (plywood only)
      comps.push({
        type: 'panel',
        subType: 'Front Panel',
        position: [0, halfHeight, -halfLength + dimensions.panelThickness/2],
        dimensions: [dimensions.width, dimensions.height, dimensions.panelThickness],
        material: 'plywood',
        explodeOffset: [0, 0, -20]
      });
      
      // Back panel
      comps.push({
        type: 'panel',
        subType: 'Back Panel',
        position: [0, halfHeight, halfLength - dimensions.panelThickness/2],
        dimensions: [dimensions.width, dimensions.height, dimensions.panelThickness],
        material: 'plywood',
        explodeOffset: [0, 0, 20]
      });
      
      // Left panel
      comps.push({
        type: 'panel',
        subType: 'Left Panel',
        position: [-halfWidth + dimensions.panelThickness/2, halfHeight, 0],
        dimensions: [dimensions.panelThickness, dimensions.height, dimensions.length - 2*dimensions.panelThickness],
        material: 'plywood',
        explodeOffset: [-20, 0, 0]
      });
      
      // Right panel
      comps.push({
        type: 'panel',
        subType: 'Right Panel',
        position: [halfWidth - dimensions.panelThickness/2, halfHeight, 0],
        dimensions: [dimensions.panelThickness, dimensions.height, dimensions.length - 2*dimensions.panelThickness],
        material: 'plywood',
        explodeOffset: [20, 0, 0]
      });
      
      // Top panel (if exists)
      if (crateData?.panels?.top) {
        comps.push({
          type: 'panel',
          subType: 'Top Panel',
          position: [0, dimensions.height - dimensions.panelThickness/2, 0],
          dimensions: [dimensions.width, dimensions.panelThickness, dimensions.length],
          material: 'plywood',
          explodeOffset: [0, 25, 0]
        });
      }
    }
    
    // CLEATS - Structural reinforcements
    if (showComponents.cleats) {
      // Vertical corner cleats
      const cleatInset = dimensions.panelThickness;
      
      // Front-left vertical cleat
      comps.push({
        type: 'cleat',
        subType: 'FL Vertical Cleat',
        position: [-halfWidth + cleatInset + dimensions.cleatWidth/2, halfHeight, -halfLength + cleatInset + dimensions.cleatWidth/2],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber',
        explodeOffset: [-10, 0, -10]
      });
      
      // Front-right vertical cleat
      comps.push({
        type: 'cleat',
        subType: 'FR Vertical Cleat',
        position: [halfWidth - cleatInset - dimensions.cleatWidth/2, halfHeight, -halfLength + cleatInset + dimensions.cleatWidth/2],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber',
        explodeOffset: [10, 0, -10]
      });
      
      // Back-left vertical cleat
      comps.push({
        type: 'cleat',
        subType: 'BL Vertical Cleat',
        position: [-halfWidth + cleatInset + dimensions.cleatWidth/2, halfHeight, halfLength - cleatInset - dimensions.cleatWidth/2],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber',
        explodeOffset: [-10, 0, 10]
      });
      
      // Back-right vertical cleat
      comps.push({
        type: 'cleat',
        subType: 'BR Vertical Cleat',
        position: [halfWidth - cleatInset - dimensions.cleatWidth/2, halfHeight, halfLength - cleatInset - dimensions.cleatWidth/2],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber',
        explodeOffset: [10, 0, 10]
      });
      
      // Top horizontal cleats (if top panel exists)
      if (crateData?.panels?.top) {
        // Front top cleat
        comps.push({
          type: 'cleat',
          subType: 'Front Top Cleat',
          position: [0, dimensions.height - cleatInset - dimensions.cleatThickness/2, -halfLength + cleatInset + dimensions.cleatWidth/2],
          dimensions: [dimensions.width - 2*(cleatInset + dimensions.cleatWidth), dimensions.cleatThickness, dimensions.cleatWidth],
          material: 'lumber',
          explodeOffset: [0, 15, -10]
        });
        
        // Back top cleat
        comps.push({
          type: 'cleat',
          subType: 'Back Top Cleat',
          position: [0, dimensions.height - cleatInset - dimensions.cleatThickness/2, halfLength - cleatInset - dimensions.cleatWidth/2],
          dimensions: [dimensions.width - 2*(cleatInset + dimensions.cleatWidth), dimensions.cleatThickness, dimensions.cleatWidth],
          material: 'lumber',
          explodeOffset: [0, 15, 10]
        });
      }
      
      // Bottom perimeter cleats
      // Front bottom cleat
      comps.push({
        type: 'cleat',
        subType: 'Front Bottom Cleat',
        position: [0, cleatInset + dimensions.cleatThickness/2, -halfLength + cleatInset + dimensions.cleatWidth/2],
        dimensions: [dimensions.width - 2*(cleatInset + dimensions.cleatWidth), dimensions.cleatThickness, dimensions.cleatWidth],
        material: 'lumber',
        explodeOffset: [0, -15, -10]
      });
      
      // Back bottom cleat
      comps.push({
        type: 'cleat',
        subType: 'Back Bottom Cleat',
        position: [0, cleatInset + dimensions.cleatThickness/2, halfLength - cleatInset - dimensions.cleatWidth/2],
        dimensions: [dimensions.width - 2*(cleatInset + dimensions.cleatWidth), dimensions.cleatThickness, dimensions.cleatWidth],
        material: 'lumber',
        explodeOffset: [0, -15, 10]
      });
      
      // Left bottom cleat
      comps.push({
        type: 'cleat',
        subType: 'Left Bottom Cleat',
        position: [-halfWidth + cleatInset + dimensions.cleatWidth/2, cleatInset + dimensions.cleatThickness/2, 0],
        dimensions: [dimensions.cleatWidth, dimensions.cleatThickness, dimensions.length - 2*(cleatInset + dimensions.cleatWidth)],
        material: 'lumber',
        explodeOffset: [-10, -15, 0]
      });
      
      // Right bottom cleat
      comps.push({
        type: 'cleat',
        subType: 'Right Bottom Cleat',
        position: [halfWidth - cleatInset - dimensions.cleatWidth/2, cleatInset + dimensions.cleatThickness/2, 0],
        dimensions: [dimensions.cleatWidth, dimensions.cleatThickness, dimensions.length - 2*(cleatInset + dimensions.cleatWidth)],
        material: 'lumber',
        explodeOffset: [10, -15, 0]
      });
    }
    
    // SKIDS - Base runners
    if (showComponents.skids && crateData?.skid_parameters) {
      const skidCount = crateData.skid_parameters.count || 3;
      const skidSpacing = (dimensions.width - dimensions.skidWidth) / (skidCount - 1);
      
      for (let i = 0; i < skidCount; i++) {
        const xPos = -halfWidth + dimensions.skidWidth/2 + i * skidSpacing;
        comps.push({
          type: 'skid',
          subType: `Skid ${i + 1}`,
          position: [xPos, -dimensions.skidHeight/2, 0],
          dimensions: [dimensions.skidWidth, dimensions.skidHeight, dimensions.length],
          material: 'lumber',
          explodeOffset: [0, -20, 0]
        });
      }
    }
    
    // FLOORBOARDS
    if (showComponents.floorboards && crateData?.floorboard_parameters?.instances) {
      const activeFloorboards = crateData.floorboard_parameters.instances
        .filter((fb: any) => fb.suppress_flag === 1);
      
      activeFloorboards.forEach((fb: any, i: number) => {
        const zPos = -halfLength + fb.y_pos_abs + fb.actual_width/2;
        comps.push({
          type: 'floorboard',
          subType: `Floorboard ${i + 1}`,
          position: [0, dimensions.floorboardThickness/2, zPos],
          dimensions: [dimensions.width, dimensions.floorboardThickness, fb.actual_width],
          material: 'lumber',
          explodeOffset: [0, -10, 0]
        });
      });
    }
    
    return comps;
  }, [crateData, dimensions, showComponents]);
  
  return (
    <group>
      {components.map((comp, index) => (
        <CrateComponent
          key={`${comp.type}_${comp.subType}_${index}`}
          type={comp.type}
          subType={comp.subType}
          position={comp.position}
          dimensions={comp.dimensions}
          material={comp.material}
          rotation={comp.rotation}
          isExploded={exploded}
          explodeOffset={comp.explodeOffset}
          showDimensions={showDimensions}
          highlighted={highlightedComponent === comp.subType}
          visible={true}
          opacity={wireframe ? 0.3 : 1}
          onHover={(hovered, info) => setHoveredComponent(hovered ? info : null)}
        />
      ))}
      
      {/* Overall dimensions display */}
      {showDimensions && !exploded && (
        <Html
          position={[0, dimensions.height + 10, 0]}
          center
          distanceFactor={10}
        >
          <div style={{
            background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '600',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            whiteSpace: 'nowrap',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}>
            Overall: {dimensions.length.toFixed(1)}" L × {dimensions.width.toFixed(1)}" W × {dimensions.height.toFixed(1)}" H
          </div>
        </Html>
      )}
      
      {/* Component info display */}
      {hoveredComponent && (
        <Html
          position={[0, -dimensions.height/2 - 10, 0]}
          center
          distanceFactor={10}
        >
          <Alert severity="info" sx={{ py: 0.5, px: 1.5 }}>
            <Typography variant="caption">
              <strong>{hoveredComponent.subType}:</strong> {hoveredComponent.dimensions[0].toFixed(1)}" × {hoveredComponent.dimensions[1].toFixed(1)}" × {hoveredComponent.dimensions[2].toFixed(1)}"
            </Typography>
          </Alert>
        </Html>
      )}
    </group>
  );
};

// Main Enhanced Viewer Component
const EnhancedProfessionalCrateViewer: React.FC<{
  crateData?: any;
  className?: string;
}> = ({ crateData, className }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [exploded, setExploded] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const [showDimensions, setShowDimensions] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [wireframe, setWireframe] = useState(false);
  const [showComponents, setShowComponents] = useState({
    panels: true,
    cleats: true,
    skids: true,
    floorboards: true,
    hardware: false
  });
  const containerRef = useRef<HTMLDivElement>(null);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const toggleComponent = (component: keyof typeof showComponents) => {
    setShowComponents(prev => ({
      ...prev,
      [component]: !prev[component]
    }));
  };

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        width: '100%',
        height: '100%',
        backgroundColor: '#f0f2f5',
        borderRadius: isFullscreen ? 0 : 1,
        overflow: 'hidden'
      }}
      className={className}
    >
      <Canvas
        shadows
        camera={{ position: [80, 60, 80], fov: 45 }}
        gl={{ preserveDrawingBuffer: true }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[20, 30, 10]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-far={100}
          shadow-camera-left={-50}
          shadow-camera-right={50}
          shadow-camera-top={50}
          shadow-camera-bottom={-50}
        />
        <pointLight position={[-20, 10, -10]} intensity={0.3} />
        
        <Suspense fallback={null}>
          <EnhancedCrateAssembly
            crateData={crateData}
            exploded={exploded}
            showDimensions={showDimensions}
            showComponents={showComponents}
            wireframe={wireframe}
          />
          
          {showGrid && (
            <Grid
              renderOrder={-1}
              position={[0, -20, 0]}
              infiniteGrid
              cellSize={10}
              cellThickness={0.5}
              cellColor="#c0c0c0"
              sectionSize={50}
              sectionThickness={1}
              sectionColor="#808080"
              fadeDistance={150}
              fadeStrength={1}
              followCamera={false}
            />
          )}
          
          <Environment preset="warehouse" />
          <ContactShadows
            position={[0, -20, 0]}
            opacity={0.6}
            scale={150}
            blur={2.5}
            far={30}
          />
        </Suspense>
        
        <OrbitControls
          enablePan
          enableZoom
          enableRotate
          autoRotate={autoRotate}
          autoRotateSpeed={0.5}
          minDistance={30}
          maxDistance={200}
          minPolarAngle={0}
          maxPolarAngle={Math.PI / 2}
        />
        
        <PerspectiveCamera makeDefault position={[80, 60, 80]} fov={45} />
      </Canvas>
      
      {/* Enhanced Controls Panel */}
      <Paper
        sx={{
          position: 'absolute',
          top: 12,
          left: 12,
          p: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: 2,
          minWidth: 240,
          maxHeight: isFullscreen ? '90vh' : '80vh',
          overflowY: 'auto'
        }}
        elevation={3}
      >
        <Stack spacing={2}>
          <Typography variant="subtitle1" fontWeight={700}>
            3D View Controls
          </Typography>
          
          <Divider />
          
          <Typography variant="caption" fontWeight={600} color="primary">
            VIEW OPTIONS
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={exploded}
                onChange={(e) => setExploded(e.target.checked)}
                size="small"
                color="primary"
              />
            }
            label={<Typography variant="body2">Exploded View</Typography>}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={showDimensions}
                onChange={(e) => setShowDimensions(e.target.checked)}
                size="small"
                color="primary"
              />
            }
            label={<Typography variant="body2">Show Dimensions</Typography>}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={wireframe}
                onChange={(e) => setWireframe(e.target.checked)}
                size="small"
                color="primary"
              />
            }
            label={<Typography variant="body2">Wireframe</Typography>}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={autoRotate}
                onChange={(e) => setAutoRotate(e.target.checked)}
                size="small"
                color="primary"
              />
            }
            label={<Typography variant="body2">Auto Rotate</Typography>}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={showGrid}
                onChange={(e) => setShowGrid(e.target.checked)}
                size="small"
                color="primary"
              />
            }
            label={<Typography variant="body2">Show Grid</Typography>}
          />
          
          <Divider />
          
          <Typography variant="caption" fontWeight={600} color="primary">
            COMPONENTS
          </Typography>
          
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip
              icon={<Layers />}
              label="Panels"
              size="small"
              color={showComponents.panels ? "primary" : "default"}
              onClick={() => toggleComponent('panels')}
              variant={showComponents.panels ? "filled" : "outlined"}
            />
            <Chip
              icon={<Build />}
              label="Cleats"
              size="small"
              color={showComponents.cleats ? "primary" : "default"}
              onClick={() => toggleComponent('cleats')}
              variant={showComponents.cleats ? "filled" : "outlined"}
            />
            <Chip
              icon={<ViewInAr />}
              label="Skids"
              size="small"
              color={showComponents.skids ? "primary" : "default"}
              onClick={() => toggleComponent('skids')}
              variant={showComponents.skids ? "filled" : "outlined"}
            />
            <Chip
              icon={<Straighten />}
              label="Floor"
              size="small"
              color={showComponents.floorboards ? "primary" : "default"}
              onClick={() => toggleComponent('floorboards')}
              variant={showComponents.floorboards ? "filled" : "outlined"}
            />
          </Stack>
          
          {crateData && (
            <>
              <Divider />
              <Typography variant="caption" fontWeight={600} color="primary">
                CRATE INFO
              </Typography>
              <Box sx={{ pl: 1 }}>
                <Typography variant="caption" display="block">
                  External: {crateData.crate_dimensions?.external_length?.toFixed(1)}" × {crateData.crate_dimensions?.external_width?.toFixed(1)}" × {crateData.crate_dimensions?.external_height?.toFixed(1)}"
                </Typography>
                <Typography variant="caption" display="block">
                  Material: {crateData.inputs?.material_type === 'plywood' ? 'CDX Plywood' : 'OSB'}
                </Typography>
                <Typography variant="caption" display="block">
                  Panel: {crateData.inputs?.panel_thickness}" thick
                </Typography>
              </Box>
            </>
          )}
        </Stack>
      </Paper>
      
      {/* Component Legend */}
      <Paper
        sx={{
          position: 'absolute',
          bottom: 12,
          left: 12,
          p: 1.5,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(10px)',
          borderRadius: 1
        }}
        elevation={2}
      >
        <Stack direction="row" spacing={2} alignItems="center">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 16, height: 16, bgcolor: MATERIALS.plywood.color, borderRadius: 0.5 }} />
            <Typography variant="caption">Plywood</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 16, height: 16, bgcolor: MATERIALS.lumber.color, borderRadius: 0.5 }} />
            <Typography variant="caption">Lumber</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 16, height: 16, bgcolor: MATERIALS.metal.color, borderRadius: 0.5 }} />
            <Typography variant="caption">Hardware</Typography>
          </Box>
        </Stack>
      </Paper>
      
      {/* Fullscreen button */}
      <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
        <IconButton
          sx={{
            position: 'absolute',
            top: 12,
            right: 12,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
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

export default EnhancedProfessionalCrateViewer;