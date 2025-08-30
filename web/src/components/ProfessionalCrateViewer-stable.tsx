'use client';

import React, { useRef, useState, useMemo, Suspense, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import {
  OrbitControls,
  Environment,
  ContactShadows,
  Html,
  Grid,
  PerspectiveCamera,
  useProgress,
  Loader,
  BakeShadows,
  AdaptiveDpr,
  AdaptiveEvents,
  PerformanceMonitor
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
  LinearProgress,
  Alert
} from '@mui/material';
import {
  Fullscreen,
  FullscreenExit,
  Layers,
  Build,
  Straighten,
  ViewInAr,
  GridOn,
  ZoomIn,
  ZoomOut,
  RestartAlt,
  ThreeDRotation,
  Speed,
  HighQuality,
  CheckCircle
} from '@mui/icons-material';
import * as THREE from 'three';

// Optimized material definitions with better performance
const MATERIALS = {
  plywood: {
    name: 'CDX Plywood',
    color: '#C4915C',
    roughness: 0.9,
    metalness: 0.0,
  },
  osb: {
    name: 'OSB',
    color: '#B8956A',
    roughness: 0.95,
    metalness: 0.0,
  },
  lumber: {
    name: 'Pine Lumber',
    color: '#D4A373',
    roughness: 0.85,
    metalness: 0.0,
  }
};

// Component type definitions
interface CrateComponentProps {
  type: 'panel' | 'cleat' | 'skid' | 'floorboard';
  subType: string;
  position: [number, number, number];
  dimensions: [number, number, number];
  material: keyof typeof MATERIALS;
  rotation?: [number, number, number];
  opacity?: number;
  visible?: boolean;
  onHover?: (hovered: boolean, info: any) => void;
  onClick?: () => void;
}

// Optimized component with instanced rendering where possible
const StableCrateComponent: React.FC<CrateComponentProps> = React.memo(({
  type,
  subType,
  position,
  dimensions,
  material,
  rotation = [0, 0, 0],
  opacity = 1,
  visible = true,
  onHover,
  onClick
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  
  const mat = MATERIALS[material];
  
  // Memoize material to prevent recreation
  const materialConfig = useMemo(() => ({
    color: hovered ? '#ffa726' : mat.color,
    roughness: mat.roughness,
    metalness: mat.metalness,
    transparent: opacity < 1,
    opacity: opacity,
    side: THREE.FrontSide, // Use FrontSide to prevent z-fighting
  }), [hovered, mat, opacity]);

  // Use callback to prevent unnecessary re-renders
  const handlePointerOver = useCallback((e: any) => {
    e.stopPropagation();
    setHovered(true);
    onHover?.(true, { type, subType, dimensions });
  }, [type, subType, dimensions, onHover]);

  const handlePointerOut = useCallback((e: any) => {
    e.stopPropagation();
    setHovered(false);
    onHover?.(false, null);
  }, [onHover]);

  const handleClick = useCallback((e: any) => {
    e.stopPropagation();
    onClick?.();
  }, [onClick]);

  if (!visible) return null;

  return (
    <mesh
      ref={meshRef}
      position={position}
      rotation={rotation as [number, number, number]}
      castShadow
      receiveShadow
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
      onClick={handleClick}
      frustumCulled
      renderOrder={type === 'panel' ? 0 : 1} // Render panels first to avoid z-fighting
    >
      <boxGeometry args={dimensions} />
      <meshStandardMaterial {...materialConfig} />
    </mesh>
  );
});

StableCrateComponent.displayName = 'StableCrateComponent';

// Stable Crate Assembly with proper geometry separation
const StableCrateAssembly: React.FC<{
  crateData: any;
  showComponents: {
    panels: boolean;
    cleats: boolean;
    skids: boolean;
    floorboards: boolean;
  };
  wireframe: boolean;
}> = React.memo(({ 
  crateData, 
  showComponents,
  wireframe
}) => {
  const [hoveredComponent, setHoveredComponent] = useState<any>(null);
  
  // Parse dimensions with defaults
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
      skidWidth: crateData.skid_parameters?.actual_width || 3.5
    };
  }, [crateData]);
  
  // Generate components with proper spacing to avoid z-fighting
  const components = useMemo(() => {
    const comps: any[] = [];
    const halfWidth = dimensions.width / 2;
    const halfLength = dimensions.length / 2;
    const halfHeight = dimensions.height / 2;
    
    // Small offset to prevent z-fighting
    const OFFSET = 0.01;
    
    // PANELS
    if (showComponents.panels) {
      // Front panel
      comps.push({
        type: 'panel',
        subType: 'Front Panel',
        position: [0, halfHeight, -halfLength + dimensions.panelThickness/2],
        dimensions: [dimensions.width - OFFSET, dimensions.height - OFFSET, dimensions.panelThickness],
        material: 'plywood'
      });
      
      // Back panel
      comps.push({
        type: 'panel',
        subType: 'Back Panel',
        position: [0, halfHeight, halfLength - dimensions.panelThickness/2],
        dimensions: [dimensions.width - OFFSET, dimensions.height - OFFSET, dimensions.panelThickness],
        material: 'plywood'
      });
      
      // Left panel - adjusted to not overlap
      comps.push({
        type: 'panel',
        subType: 'Left Panel',
        position: [-halfWidth + dimensions.panelThickness/2, halfHeight, 0],
        dimensions: [dimensions.panelThickness, dimensions.height - OFFSET, dimensions.length - 2*dimensions.panelThickness - OFFSET],
        material: 'plywood'
      });
      
      // Right panel - adjusted to not overlap
      comps.push({
        type: 'panel',
        subType: 'Right Panel',
        position: [halfWidth - dimensions.panelThickness/2, halfHeight, 0],
        dimensions: [dimensions.panelThickness, dimensions.height - OFFSET, dimensions.length - 2*dimensions.panelThickness - OFFSET],
        material: 'plywood'
      });
      
      // Top panel (if exists)
      if (crateData?.panels?.top) {
        comps.push({
          type: 'panel',
          subType: 'Top Panel',
          position: [0, dimensions.height - dimensions.panelThickness/2, 0],
          dimensions: [dimensions.width - 2*OFFSET, dimensions.panelThickness, dimensions.length - 2*OFFSET],
          material: 'plywood'
        });
      }
    }
    
    // CLEATS - with proper inset
    if (showComponents.cleats) {
      const cleatInset = dimensions.panelThickness + OFFSET;
      
      // Vertical corner cleats - properly positioned inside panels
      // Front-left
      comps.push({
        type: 'cleat',
        subType: 'FL Corner',
        position: [
          -halfWidth + cleatInset + dimensions.cleatWidth/2,
          halfHeight,
          -halfLength + cleatInset + dimensions.cleatWidth/2
        ],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber'
      });
      
      // Front-right
      comps.push({
        type: 'cleat',
        subType: 'FR Corner',
        position: [
          halfWidth - cleatInset - dimensions.cleatWidth/2,
          halfHeight,
          -halfLength + cleatInset + dimensions.cleatWidth/2
        ],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber'
      });
      
      // Back-left
      comps.push({
        type: 'cleat',
        subType: 'BL Corner',
        position: [
          -halfWidth + cleatInset + dimensions.cleatWidth/2,
          halfHeight,
          halfLength - cleatInset - dimensions.cleatWidth/2
        ],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber'
      });
      
      // Back-right
      comps.push({
        type: 'cleat',
        subType: 'BR Corner',
        position: [
          halfWidth - cleatInset - dimensions.cleatWidth/2,
          halfHeight,
          halfLength - cleatInset - dimensions.cleatWidth/2
        ],
        dimensions: [dimensions.cleatWidth, dimensions.height - 2*cleatInset, dimensions.cleatWidth],
        material: 'lumber'
      });
      
      // Horizontal bottom cleats
      const bottomY = cleatInset + dimensions.cleatThickness/2;
      
      // Front bottom
      comps.push({
        type: 'cleat',
        subType: 'Front Bottom',
        position: [0, bottomY, -halfLength + cleatInset + dimensions.cleatWidth/2],
        dimensions: [
          dimensions.width - 2*(cleatInset + dimensions.cleatWidth) - OFFSET,
          dimensions.cleatThickness,
          dimensions.cleatWidth
        ],
        material: 'lumber'
      });
      
      // Back bottom
      comps.push({
        type: 'cleat',
        subType: 'Back Bottom',
        position: [0, bottomY, halfLength - cleatInset - dimensions.cleatWidth/2],
        dimensions: [
          dimensions.width - 2*(cleatInset + dimensions.cleatWidth) - OFFSET,
          dimensions.cleatThickness,
          dimensions.cleatWidth
        ],
        material: 'lumber'
      });
    }
    
    // SKIDS - properly spaced
    if (showComponents.skids && crateData?.skid_parameters) {
      const skidCount = crateData.skid_parameters.count || 3;
      const totalSpacing = dimensions.width - dimensions.skidWidth;
      const skidSpacing = totalSpacing / (skidCount - 1);
      
      for (let i = 0; i < skidCount; i++) {
        const xPos = -halfWidth + dimensions.skidWidth/2 + i * skidSpacing;
        comps.push({
          type: 'skid',
          subType: `Skid ${i + 1}`,
          position: [xPos, -dimensions.skidHeight/2 + OFFSET, 0],
          dimensions: [dimensions.skidWidth, dimensions.skidHeight, dimensions.length - OFFSET],
          material: 'lumber'
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
          subType: `Floor ${i + 1}`,
          position: [0, dimensions.floorboardThickness/2, zPos],
          dimensions: [dimensions.width - OFFSET, dimensions.floorboardThickness, fb.actual_width - OFFSET],
          material: 'lumber'
        });
      });
    }
    
    return comps;
  }, [crateData, dimensions, showComponents]);
  
  return (
    <group>
      {/* Use instanced mesh for better performance */}
      {components.map((comp, index) => (
        <StableCrateComponent
          key={`${comp.type}_${comp.subType}_${index}`}
          type={comp.type}
          subType={comp.subType}
          position={comp.position}
          dimensions={comp.dimensions}
          material={comp.material}
          rotation={comp.rotation}
          visible={true}
          opacity={wireframe ? 0.3 : 1}
          onHover={(hovered, info) => setHoveredComponent(hovered ? info : null)}
        />
      ))}
      
      {/* Info display */}
      {hoveredComponent && (
        <Html
          position={[0, -dimensions.height/2 - 5, 0]}
          center
          distanceFactor={10}
          style={{ pointerEvents: 'none' }}
        >
          <Alert 
            severity="info" 
            sx={{ 
              py: 0.5, 
              px: 1.5,
              backgroundColor: 'rgba(33, 150, 243, 0.95)',
              color: 'white',
              '& .MuiAlert-icon': { color: 'white' }
            }}
          >
            <Typography variant="caption">
              <strong>{hoveredComponent.subType}:</strong> {hoveredComponent.dimensions[0].toFixed(1)}" × {hoveredComponent.dimensions[1].toFixed(1)}" × {hoveredComponent.dimensions[2].toFixed(1)}"
            </Typography>
          </Alert>
        </Html>
      )}
    </group>
  );
});

StableCrateAssembly.displayName = 'StableCrateAssembly';

// Loading component
function LoadingScreen() {
  const { progress } = useProgress();
  return (
    <Html center>
      <Box sx={{ width: 200, textAlign: 'center' }}>
        <Typography variant="body2" gutterBottom>Loading 3D Model</Typography>
        <LinearProgress variant="determinate" value={progress} />
        <Typography variant="caption">{Math.round(progress)}%</Typography>
      </Box>
    </Html>
  );
}

// Main Stable Viewer Component
const StableProfessionalCrateViewer: React.FC<{
  crateData?: any;
  className?: string;
}> = ({ crateData, className }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [autoRotate, setAutoRotate] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [wireframe, setWireframe] = useState(false);
  const [quality, setQuality] = useState<'low' | 'medium' | 'high'>('medium');
  const [showComponents, setShowComponents] = useState({
    panels: true,
    cleats: true,
    skids: true,
    floorboards: true
  });
  const containerRef = useRef<HTMLDivElement>(null);
  const controlsRef = useRef<any>(null);

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

  const resetCamera = () => {
    if (controlsRef.current) {
      controlsRef.current.reset();
    }
  };

  // Quality settings
  const qualitySettings = {
    low: { shadows: false, dpr: [0.5, 1], samples: 1 },
    medium: { shadows: true, dpr: [1, 1.5], samples: 2 },
    high: { shadows: true, dpr: [1, 2], samples: 4 }
  };

  const currentQuality = qualitySettings[quality];

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        width: '100%',
        height: '100%',
        backgroundColor: '#e8eaf0',
        borderRadius: isFullscreen ? 0 : 1,
        overflow: 'hidden'
      }}
      className={className}
    >
      <Canvas
        shadows={currentQuality.shadows}
        dpr={currentQuality.dpr as [number, number]}
        camera={{ 
          position: [60, 40, 60], 
          fov: 45,
          near: 0.1,
          far: 1000
        }}
        gl={{ 
          antialias: quality !== 'low',
          alpha: true,
          powerPreference: quality === 'high' ? 'high-performance' : 'default',
          preserveDrawingBuffer: true
        }}
      >
        {/* Performance monitoring */}
        <PerformanceMonitor
          onDecline={() => quality !== 'low' && setQuality('low')}
        />
        
        {/* Adaptive quality */}
        <AdaptiveDpr pixelated />
        <AdaptiveEvents />
        
        {/* Lighting setup - stable and optimized */}
        <ambientLight intensity={0.6} />
        <directionalLight
          position={[15, 20, 10]}
          intensity={0.8}
          castShadow={currentQuality.shadows}
          shadow-mapSize={[1024, 1024]}
          shadow-camera-far={100}
          shadow-camera-left={-50}
          shadow-camera-right={50}
          shadow-camera-top={50}
          shadow-camera-bottom={-50}
          shadow-bias={-0.001} // Prevent shadow acne
        />
        <pointLight position={[-10, 10, -10]} intensity={0.3} />
        
        <Suspense fallback={<LoadingScreen />}>
          <StableCrateAssembly
            crateData={crateData}
            showComponents={showComponents}
            wireframe={wireframe}
          />
          
          {showGrid && (
            <Grid
              renderOrder={-1}
              position={[0, -20, 0]}
              args={[200, 200]}
              cellSize={10}
              cellThickness={0.5}
              cellColor="#c0c0c0"
              sectionSize={50}
              sectionThickness={1}
              sectionColor="#808080"
              fadeDistance={100}
              fadeStrength={1}
              infiniteGrid
              followCamera={false}
            />
          )}
          
          {/* Simple environment for reflections */}
          <Environment preset="warehouse" background={false} />
          
          {/* Contact shadows for grounding */}
          {currentQuality.shadows && (
            <ContactShadows
              position={[0, -20, 0]}
              opacity={0.4}
              scale={100}
              blur={1.5}
              far={30}
              resolution={256}
              color="#000000"
            />
          )}
          
          {/* Bake shadows for performance */}
          {currentQuality.shadows && <BakeShadows />}
        </Suspense>
        
        {/* Camera controls */}
        <OrbitControls
          ref={controlsRef}
          enablePan
          enableZoom
          enableRotate
          autoRotate={autoRotate}
          autoRotateSpeed={0.5}
          minDistance={20}
          maxDistance={150}
          minPolarAngle={0}
          maxPolarAngle={Math.PI / 2}
          makeDefault
          enableDamping
          dampingFactor={0.05}
          rotateSpeed={0.5}
          zoomSpeed={0.8}
        />
        
        <PerspectiveCamera makeDefault position={[60, 40, 60]} fov={45} />
      </Canvas>
      
      {/* Stable Controls Panel */}
      <Paper
        sx={{
          position: 'absolute',
          top: 12,
          left: 12,
          p: 1.5,
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          backdropFilter: 'blur(20px)',
          borderRadius: 2,
          minWidth: 220,
          maxHeight: isFullscreen ? '85vh' : '70vh',
          overflowY: 'auto',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          '&::-webkit-scrollbar': {
            width: 6,
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'rgba(0,0,0,0.2)',
            borderRadius: 3,
          }
        }}
        elevation={0}
      >
        <Stack spacing={1.5}>
          <Typography variant="subtitle2" fontWeight={700} sx={{ pb: 0.5 }}>
            3D View Controls
          </Typography>
          
          <Divider />
          
          {/* Quick Actions */}
          <Stack direction="row" spacing={1}>
            <Tooltip title="Reset View">
              <IconButton size="small" onClick={resetCamera}>
                <RestartAlt fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Auto Rotate">
              <IconButton 
                size="small" 
                onClick={() => setAutoRotate(!autoRotate)}
                color={autoRotate ? "primary" : "default"}
              >
                <ThreeDRotation fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Grid">
              <IconButton 
                size="small" 
                onClick={() => setShowGrid(!showGrid)}
                color={showGrid ? "primary" : "default"}
              >
                <GridOn fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Wireframe">
              <IconButton 
                size="small" 
                onClick={() => setWireframe(!wireframe)}
                color={wireframe ? "primary" : "default"}
              >
                <ViewInAr fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
          
          <Divider />
          
          {/* Components */}
          <Typography variant="caption" fontWeight={600} color="text.secondary">
            COMPONENTS
          </Typography>
          
          <Stack spacing={0.5}>
            <FormControlLabel
              control={
                <Switch
                  checked={showComponents.panels}
                  onChange={() => toggleComponent('panels')}
                  size="small"
                />
              }
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <Layers fontSize="small" />
                  <Typography variant="body2">Panels</Typography>
                </Stack>
              }
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={showComponents.cleats}
                  onChange={() => toggleComponent('cleats')}
                  size="small"
                />
              }
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <Build fontSize="small" />
                  <Typography variant="body2">Cleats</Typography>
                </Stack>
              }
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={showComponents.skids}
                  onChange={() => toggleComponent('skids')}
                  size="small"
                />
              }
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <ViewInAr fontSize="small" />
                  <Typography variant="body2">Skids</Typography>
                </Stack>
              }
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={showComponents.floorboards}
                  onChange={() => toggleComponent('floorboards')}
                  size="small"
                />
              }
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <Straighten fontSize="small" />
                  <Typography variant="body2">Floorboards</Typography>
                </Stack>
              }
            />
          </Stack>
          
          <Divider />
          
          {/* Quality Settings */}
          <Typography variant="caption" fontWeight={600} color="text.secondary">
            QUALITY
          </Typography>
          
          <FormControl size="small" fullWidth>
            <Select
              value={quality}
              onChange={(e) => setQuality(e.target.value as 'low' | 'medium' | 'high')}
            >
              <MenuItem value="low">
                <Stack direction="row" spacing={1} alignItems="center">
                  <Speed fontSize="small" />
                  <Typography variant="body2">Performance</Typography>
                </Stack>
              </MenuItem>
              <MenuItem value="medium">
                <Stack direction="row" spacing={1} alignItems="center">
                  <CheckCircle fontSize="small" />
                  <Typography variant="body2">Balanced</Typography>
                </Stack>
              </MenuItem>
              <MenuItem value="high">
                <Stack direction="row" spacing={1} alignItems="center">
                  <HighQuality fontSize="small" />
                  <Typography variant="body2">Quality</Typography>
                </Stack>
              </MenuItem>
            </Select>
          </FormControl>
          
          {/* Info */}
          {crateData && (
            <>
              <Divider />
              <Typography variant="caption" fontWeight={600} color="text.secondary">
                DIMENSIONS
              </Typography>
              <Box sx={{ pl: 0.5 }}>
                <Typography variant="caption" display="block" color="text.secondary">
                  {crateData.crate_dimensions?.external_length?.toFixed(1)}" L × {' '}
                  {crateData.crate_dimensions?.external_width?.toFixed(1)}" W × {' '}
                  {crateData.crate_dimensions?.external_height?.toFixed(1)}" H
                </Typography>
              </Box>
            </>
          )}
        </Stack>
      </Paper>
      
      {/* Material Legend - Compact */}
      <Paper
        sx={{
          position: 'absolute',
          bottom: 12,
          left: 12,
          p: 1,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: 1,
          display: 'flex',
          gap: 1.5,
          alignItems: 'center'
        }}
        elevation={0}
      >
        {Object.entries(MATERIALS).slice(0, 3).map(([key, mat]) => (
          <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box 
              sx={{ 
                width: 12, 
                height: 12, 
                bgcolor: mat.color, 
                borderRadius: 0.5,
                border: '1px solid rgba(0,0,0,0.1)'
              }} 
            />
            <Typography variant="caption" color="text.secondary">
              {key === 'lumber' ? 'Cleats/Skids' : mat.name}
            </Typography>
          </Box>
        ))}
      </Paper>
      
      {/* Fullscreen button */}
      <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
        <IconButton
          sx={{
            position: 'absolute',
            top: 12,
            right: 12,
            backgroundColor: 'rgba(255, 255, 255, 0.98)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 1)',
              transform: 'scale(1.1)',
            },
            transition: 'all 0.2s'
          }}
          onClick={toggleFullscreen}
          size="small"
        >
          {isFullscreen ? <FullscreenExit fontSize="small" /> : <Fullscreen fontSize="small" />}
        </IconButton>
      </Tooltip>
      
      {/* Loader for initial load */}
      <Loader />
    </Box>
  );
};

export default StableProfessionalCrateViewer;