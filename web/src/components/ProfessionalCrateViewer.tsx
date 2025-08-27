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
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  
  const woodMaterial = WOOD_MATERIALS[material as keyof typeof WOOD_MATERIALS] || WOOD_MATERIALS.oak;

  // Animation for exploded view
  const { explodePosition } = useSpring({
    explodePosition: isExploded ? explodeOffset : [0, 0, 0],
    config: { mass: 1, tension: 280, friction: 60 }
  });

  // Hover animation
  useFrame((state) => {
    if (meshRef.current && hovered) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 2) * 0.02;
    }
  });

  return (
    <animated.group position={explodePosition as any}>
      <mesh
        ref={meshRef}
        position={position}
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
        castShadow
        receiveShadow
      >
        <boxGeometry args={dimensions} />
        <meshStandardMaterial
          color={highlighted ? '#FFD700' : woodMaterial.color}
          roughness={woodMaterial.roughness}
          metalness={woodMaterial.metalness}
          transparent={opacity < 1}
          opacity={opacity}
          emissive={hovered ? woodMaterial.color : 'black'}
          emissiveIntensity={hovered ? 0.1 : 0}
        />
      </mesh>
      
      {/* Dimension labels with improved visibility and 3D text */}
      {showDimensions && (
        <>
          {/* Length dimension - 3D Text */}
          <Text
            position={[dimensions[0] / 2 + 8, 0, 0]}
            rotation={[0, Math.PI / 2, 0]}
            fontSize={4}
            color="#ff6b6b"
            anchorX="center"
            anchorY="middle"
            fontWeight="bold"
            outlineWidth={0.2}
            outlineColor="#ffffff"
          >
            {dimensions[0].toFixed(1)}"
          </Text>
          
          {/* Width dimension - 3D Text */}
          <Text
            position={[0, dimensions[1] / 2 + 8, 0]}
            rotation={[0, 0, 0]}
            fontSize={4}
            color="#4ecdc4"
            anchorX="center"
            anchorY="middle"
            fontWeight="bold"
            outlineWidth={0.2}
            outlineColor="#ffffff"
          >
            {dimensions[1].toFixed(1)}"
          </Text>
          
          {/* Height dimension - 3D Text */}
          <Text
            position={[0, 0, dimensions[2] / 2 + 8]}
            rotation={[0, 0, Math.PI / 2]}
            fontSize={4}
            color="#667eea"
            anchorX="center"
            anchorY="middle"
            fontWeight="bold"
            outlineWidth={0.2}
            outlineColor="#ffffff"
          >
            {dimensions[2].toFixed(1)}"
          </Text>

          {/* HTML labels for better readability */}
          <Html 
            position={[dimensions[0] / 2 + 12, 0, 0]} 
            center
            distanceFactor={3}
            style={{ pointerEvents: 'none' }}
          >
            <div style={{
              background: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
              color: 'white',
              padding: '10px 16px',
              borderRadius: '8px',
              fontSize: '24px',
              fontWeight: 'bold',
              whiteSpace: 'nowrap',
              fontFamily: 'Arial, sans-serif',
              boxShadow: '0 6px 20px rgba(0,0,0,0.4)',
              border: '3px solid white',
              textAlign: 'center'
            }}>
              LENGTH<br/>{dimensions[0].toFixed(1)}"
            </div>
          </Html>
          
          <Html 
            position={[0, dimensions[1] / 2 + 12, 0]} 
            center
            distanceFactor={3}
            style={{ pointerEvents: 'none' }}
          >
            <div style={{
              background: 'linear-gradient(135deg, #4ecdc4, #44a08d)',
              color: 'white',
              padding: '10px 16px',
              borderRadius: '8px',
              fontSize: '24px',
              fontWeight: 'bold',
              whiteSpace: 'nowrap',
              fontFamily: 'Arial, sans-serif',
              boxShadow: '0 6px 20px rgba(0,0,0,0.4)',
              border: '3px solid white',
              textAlign: 'center'
            }}>
              WIDTH<br/>{dimensions[1].toFixed(1)}"
            </div>
          </Html>
          
          <Html 
            position={[0, 0, dimensions[2] / 2 + 12]} 
            center
            distanceFactor={3}
            style={{ pointerEvents: 'none' }}
          >
            <div style={{
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              padding: '10px 16px',
              borderRadius: '8px',
              fontSize: '24px',
              fontWeight: 'bold',
              whiteSpace: 'nowrap',
              fontFamily: 'Arial, sans-serif',
              boxShadow: '0 6px 20px rgba(0,0,0,0.4)',
              border: '3px solid white',
              textAlign: 'center'
            }}>
              HEIGHT<br/>{dimensions[2].toFixed(1)}"
            </div>
          </Html>

          {/* Add dimension lines */}
          <group>
            {/* Length line */}
            <mesh position={[0, -dimensions[1]/2 - 2, -dimensions[2]/2 - 2]}>
              <boxGeometry args={[dimensions[0], 0.2, 0.2]} />
              <meshBasicMaterial color="#ff6b6b" />
            </mesh>
            
            {/* Width line */}
            <mesh position={[dimensions[0]/2 + 2, 0, -dimensions[2]/2 - 2]}>
              <boxGeometry args={[0.2, dimensions[1], 0.2]} />
              <meshBasicMaterial color="#4ecdc4" />
            </mesh>
            
            {/* Height line */}
            <mesh position={[dimensions[0]/2 + 2, dimensions[1]/2 + 2, 0]}>
              <boxGeometry args={[0.2, 0.2, dimensions[2]]} />
              <meshBasicMaterial color="#667eea" />
            </mesh>
          </group>
        </>
      )}
      
      {/* Component label on hover */}
      {hovered && (
        <Html 
          position={[0, dimensions[1] / 2 + 6, 0]} 
          center
          distanceFactor={10}
          style={{ 
            pointerEvents: 'none',
            zIndex: 1000
          }}
        >
          <div style={{
            background: 'linear-gradient(135deg, #fff, #f8f8f8)',
            color: '#2c3e50',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: '600',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            whiteSpace: 'nowrap',
            border: '1px solid rgba(0,0,0,0.1)',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            textTransform: 'capitalize'
          }}>
            {type.replace(/_/g, ' ')}
          </div>
        </Html>
      )}
    </animated.group>
  );
};

// Studio lighting setup
const StudioLighting: React.FC<{ intensity?: number }> = ({ intensity = 1 }) => {
  return (
    <>
      {/* Key light */}
      <directionalLight
        position={[10, 10, 5]}
        intensity={intensity * 0.8}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={50}
        shadow-camera-left={-10}
        shadow-camera-right={10}
        shadow-camera-top={10}
        shadow-camera-bottom={-10}
      />
      
      {/* Fill light */}
      <directionalLight
        position={[-10, 5, -5]}
        intensity={intensity * 0.4}
        color="#87CEEB"
      />
      
      {/* Rim light */}
      <directionalLight
        position={[0, 10, -10]}
        intensity={intensity * 0.6}
        color="#FFE4B5"
      />
      
      {/* Ambient light */}
      <ambientLight intensity={intensity * 0.3} />
      
      {/* Point lights for accent */}
      <pointLight position={[15, 15, 15]} intensity={intensity * 0.2} color="#FFA500" />
      <pointLight position={[-15, 15, -15]} intensity={intensity * 0.2} color="#87CEEB" />
    </>
  );
};

// Complete crate assembly
const CrateAssembly: React.FC<{
  crateData: any;
  exploded: boolean;
  showDimensions: boolean;
  showWireframe: boolean;
  material: string;
  highlightedComponent?: string;
}> = ({ crateData, exploded, showDimensions, showWireframe, material, highlightedComponent }) => {
  const [hoveredComponent, setHoveredComponent] = useState<string | null>(null);

  // Parse crate data
  const dimensions = {
    length: crateData?.dimensions?.length || crateData?.length || 48,
    width: crateData?.dimensions?.width || crateData?.width || 40,
    height: crateData?.dimensions?.height || crateData?.height || 36,
    plywoodThickness: crateData?.plywood_thickness || 0.75,
    boardThickness: crateData?.floorboard_thickness || 0.75,
    boardWidth: crateData?.floorboard_width || 5.5
  };

  // Calculate component positions and dimensions
  const components = useMemo(() => {
    const comps = [];
    const t = dimensions.plywoodThickness;
    const l = dimensions.length;
    const w = dimensions.width;
    const h = dimensions.height;

    // Front panel
    comps.push({
      type: 'front_panel',
      position: [0, 0, h/2 - t/2] as [number, number, number],
      dimensions: [l, t, h] as [number, number, number],
      explodeOffset: [0, -10, 0] as [number, number, number]
    });

    // Back panel
    comps.push({
      type: 'back_panel',
      position: [0, w - t, h/2 - t/2] as [number, number, number],
      dimensions: [l, t, h] as [number, number, number],
      explodeOffset: [0, 10, 0] as [number, number, number]
    });

    // Left panel
    comps.push({
      type: 'left_panel',
      position: [-l/2 + t/2, w/2, h/2 - t/2] as [number, number, number],
      dimensions: [t, w - 2*t, h] as [number, number, number],
      explodeOffset: [-10, 0, 0] as [number, number, number]
    });

    // Right panel
    comps.push({
      type: 'right_panel',
      position: [l/2 - t/2, w/2, h/2 - t/2] as [number, number, number],
      dimensions: [t, w - 2*t, h] as [number, number, number],
      explodeOffset: [10, 0, 0] as [number, number, number]
    });

    // Top panel
    comps.push({
      type: 'top_panel',
      position: [0, w/2, h - t/2] as [number, number, number],
      dimensions: [l - 2*t, w - 2*t, t] as [number, number, number],
      explodeOffset: [0, 0, 15] as [number, number, number]
    });

    // Floor boards
    const numBoards = Math.ceil(w / dimensions.boardWidth);
    for (let i = 0; i < numBoards; i++) {
      const yPos = i * dimensions.boardWidth - w/2 + dimensions.boardWidth/2;
      const actualWidth = Math.min(dimensions.boardWidth, w - i * dimensions.boardWidth);
      
      comps.push({
        type: `floorboard_${i}`,
        position: [0, yPos, dimensions.boardThickness/2] as [number, number, number],
        dimensions: [l - 2*t, actualWidth, dimensions.boardThickness] as [number, number, number],
        explodeOffset: [0, 0, -10 - i * 2] as [number, number, number]
      });
    }

    return comps;
  }, [crateData, dimensions]);

  return (
    <group position={[0, -dimensions.width/2, 0]}>
      {components.map((comp, index) => (
        <CrateComponent
          key={`${comp.type}_${index}`}
          type={comp.type}
          position={comp.position}
          dimensions={comp.dimensions}
          material={material}
          isExploded={exploded}
          explodeOffset={comp.explodeOffset}
          showDimensions={showDimensions && comp.type.includes('panel')}
          highlighted={highlightedComponent === comp.type || hoveredComponent === comp.type}
          onHover={(hovered) => setHoveredComponent(hovered ? comp.type : null)}
          opacity={showWireframe ? 0.3 : 1}
        />
      ))}
      
      {/* Overall dimensions display with better visibility */}
      {showDimensions && !exploded && (
        <group>
          <Html
            position={[0, -dimensions.width/2 - 12, dimensions.height/2]}
            center
            distanceFactor={4}
            style={{
              transition: 'opacity 0.5s',
              pointerEvents: 'none',
              fontSize: '20px'
            }}
          >
            <div style={{
              background: 'linear-gradient(135deg, #1e3c72, #2a5298)',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '12px',
              fontSize: '20px',
              fontWeight: 'bold',
              boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
              whiteSpace: 'nowrap',
              border: '3px solid white',
              fontFamily: 'Arial, sans-serif',
              letterSpacing: '1px'
            }}>
              📏 L: {dimensions.length}" × W: {dimensions.width}" × H: {dimensions.height}"
            </div>
          </Html>

          {/* Add floating dimension arrows */}
          <group>
            {/* Length arrow */}
            <arrowHelper 
              args={[
                new THREE.Vector3(1, 0, 0),
                new THREE.Vector3(-dimensions.length/2, -dimensions.width/2 - 8, -dimensions.height/2 - 8),
                dimensions.length,
                0xff6b6b,
                dimensions.length * 0.2,
                dimensions.length * 0.1
              ]}
            />
            
            {/* Width arrow */}
            <arrowHelper 
              args={[
                new THREE.Vector3(0, 1, 0),
                new THREE.Vector3(dimensions.length/2 + 8, -dimensions.width/2, -dimensions.height/2 - 8),
                dimensions.width,
                0x4ecdc4,
                dimensions.width * 0.2,
                dimensions.width * 0.1
              ]}
            />
            
            {/* Height arrow */}
            <arrowHelper 
              args={[
                new THREE.Vector3(0, 0, 1),
                new THREE.Vector3(dimensions.length/2 + 8, dimensions.width/2 + 8, -dimensions.height/2),
                dimensions.height,
                0x667eea,
                dimensions.height * 0.2,
                dimensions.height * 0.1
              ]}
            />
          </group>
        </group>
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
  const [environmentPreset, setEnvironmentPreset] = useState('studio');
  const [postProcessing, setPostProcessing] = useState(false);
  const [showDimensions, setShowDimensions] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [showStats, setShowStats] = useState(false);
  const [lightIntensity, setLightIntensity] = useState(1);
  const [cameraView, setCameraView] = useState('default');

  const containerRef = useRef<HTMLDivElement>(null);

  // Handle screenshot
  const handleScreenshot = () => {
    const canvas = containerRef.current?.querySelector('canvas');
    if (canvas) {
      const link = document.createElement('a');
      link.download = 'crate-visualization.png';
      link.href = canvas.toDataURL();
      link.click();
    }
  };

  // Handle view reset
  const handleReset = () => {
    setCameraView('default');
    setExploded(false);
    setAutoRotate(false);
  };

  return (
    <Paper
      ref={containerRef}
      elevation={3}
      sx={{
        height: isFullscreen ? '100vh' : 700,
        width: isFullscreen ? '100vw' : '100%',
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? 9999 : 'auto',
        backgroundColor: '#1a1a1a',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}
      className={className}
    >
      {/* Professional Header */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 20px rgba(0,0,0,0.3)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <ViewInAr sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h5" fontWeight="bold">
              Professional 3D Crate Viewer
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Studio-Grade Visualization System
            </Typography>
          </Box>
        </Box>

        {/* Main Controls */}
        <Stack direction="row" spacing={2} alignItems="center">
          {/* View Presets */}
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <Select
              value={cameraView}
              onChange={(e) => setCameraView(e.target.value)}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.1)',
                color: 'white',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.3)'
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.5)'
                }
              }}
            >
              <MenuItem value="default">Default</MenuItem>
              <MenuItem value="front">Front</MenuItem>
              <MenuItem value="top">Top</MenuItem>
            </Select>
          </FormControl>

          {/* Material Selector */}
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <Select
              value={material}
              onChange={(e) => setMaterial(e.target.value)}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.1)',
                color: 'white',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.3)'
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.5)'
                }
              }}
            >
              {Object.entries(WOOD_MATERIALS).map(([key, value]) => (
                <MenuItem key={key} value={key}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box
                      sx={{
                        width: 16,
                        height: 16,
                        backgroundColor: value.color,
                        borderRadius: '2px',
                        border: '1px solid rgba(0,0,0,0.2)'
                      }}
                    />
                    {value.name}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Action Buttons */}
          <ButtonGroup variant="contained" size="small">
            <Tooltip title="Exploded View">
              <Button
                onClick={() => setExploded(!exploded)}
                color={exploded ? 'secondary' : 'primary'}
                startIcon={<Layers />}
              >
                {exploded ? 'Assembled' : 'Exploded'}
              </Button>
            </Tooltip>
            <Tooltip title="Auto Rotate">
              <Button
                onClick={() => setAutoRotate(!autoRotate)}
                color={autoRotate ? 'secondary' : 'primary'}
                startIcon={<ThreeDRotation />}
              >
                Rotate
              </Button>
            </Tooltip>
            <Tooltip title="Screenshot">
              <Button onClick={handleScreenshot} startIcon={<CameraAlt />}>
                Capture
              </Button>
            </Tooltip>
          </ButtonGroup>

          {/* Display Options */}
          <ButtonGroup variant="outlined" size="small">
            <Tooltip title="Toggle Dimensions">
              <IconButton
                onClick={() => setShowDimensions(!showDimensions)}
                color={showDimensions ? 'primary' : 'default'}
                size="small"
                sx={{ color: 'white' }}
              >
                <Straighten />
              </IconButton>
            </Tooltip>
            <Tooltip title="Toggle Grid">
              <IconButton
                onClick={() => setShowGrid(!showGrid)}
                color={showGrid ? 'primary' : 'default'}
                size="small"
                sx={{ color: 'white' }}
              >
                <GridOn />
              </IconButton>
            </Tooltip>
            <Tooltip title="Toggle Wireframe">
              <IconButton
                onClick={() => setShowWireframe(!showWireframe)}
                color={showWireframe ? 'primary' : 'default'}
                size="small"
                sx={{ color: 'white' }}
              >
                <ViewModule />
              </IconButton>
            </Tooltip>
            <Tooltip title="Post Processing">
              <IconButton
                onClick={() => setPostProcessing(!postProcessing)}
                color={postProcessing ? 'primary' : 'default'}
                size="small"
                sx={{ color: 'white' }}
              >
                <AutoFixHigh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Performance Stats">
              <IconButton
                onClick={() => setShowStats(!showStats)}
                color={showStats ? 'primary' : 'default'}
                size="small"
                sx={{ color: 'white' }}
              >
                <Timeline />
              </IconButton>
            </Tooltip>
          </ButtonGroup>

          {/* View Control Buttons */}
          <ButtonGroup variant="contained" size="small">
            <Tooltip title="Front View">
              <IconButton
                onClick={() => {
                  setCameraView('front');
                  // Camera position will be handled by a camera controller
                }}
                size="small"
                sx={{ color: cameraView === 'front' ? '#1976D2' : 'white' }}
              >
                <ViewModule />
              </IconButton>
            </Tooltip>
            <Tooltip title="Top View">
              <IconButton
                onClick={() => setCameraView('top')}
                size="small"
                sx={{ color: cameraView === 'top' ? '#1976D2' : 'white' }}
              >
                <Straighten />
              </IconButton>
            </Tooltip>
            <Tooltip title="Toggle Exploded View">
              <IconButton
                onClick={() => setExploded(!exploded)}
                color={exploded ? 'primary' : 'default'}
                size="small"
                sx={{ color: 'white' }}
              >
                <Animation />
              </IconButton>
            </Tooltip>
            <Tooltip title="Toggle Grid">
              <IconButton
                onClick={() => setShowGrid(!showGrid)}
                color={showGrid ? 'primary' : 'default'}
                size="small"
                sx={{ color: 'white' }}
              >
                <GridOn />
              </IconButton>
            </Tooltip>
          </ButtonGroup>

          {/* Fullscreen Toggle */}
          <IconButton
            onClick={() => setIsFullscreen(!isFullscreen)}
            sx={{ color: 'white' }}
          >
            {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
          </IconButton>
        </Stack>
      </Box>

      {/* Light Intensity Slider */}
      <Box
        sx={{
          position: 'absolute',
          top: 80,
          right: 20,
          zIndex: 10,
          backgroundColor: 'rgba(0,0,0,0.7)',
          borderRadius: 2,
          p: 2,
          minWidth: 200
        }}
      >
        <Typography variant="caption" color="white" gutterBottom>
          Light Intensity
        </Typography>
        <Slider
          value={lightIntensity}
          onChange={(e, value) => setLightIntensity(value as number)}
          min={0.2}
          max={2}
          step={0.1}
          valueLabelDisplay="auto"
          sx={{ color: 'white' }}
        />
      </Box>

      {/* 3D Canvas */}
      <Box sx={{ flex: 1, position: 'relative' }}>
        <Canvas
          shadows
          dpr={[1, 2]}
          camera={{ position: [120, 80, 120], fov: 45 }}
          gl={{
            antialias: true,
            toneMapping: THREE.ACESFilmicToneMapping,
            toneMappingExposure: 1.2
          }}
        >
          {/* Camera Controls */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            autoRotate={autoRotate}
            autoRotateSpeed={1.5}
            minDistance={50}
            maxDistance={300}
            minPolarAngle={Math.PI * 0.1}
            maxPolarAngle={Math.PI * 0.45}
            panSpeed={0.8}
            rotateSpeed={0.5}
            zoomSpeed={1.2}
            target={[0, 0, 10]}
            makeDefault
          />

          {/* Studio Lighting */}
          <StudioLighting intensity={lightIntensity} />

          {/* Environment */}
          <Environment
            preset={environmentPreset as any}
            background={false}
            blur={0.5}
          />

          {/* Background Gradient */}
          <color attach="background" args={['#1a1a2e']} />
          <fog attach="fog" args={['#1a1a2e', 100, 300]} />

          {/* Ground Plane with Reflection */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -20, 0]} receiveShadow>
            <planeGeometry args={[200, 200]} />
            <MeshReflectorMaterial
              blur={[300, 30]}
              resolution={2048}
              mixBlur={1}
              mixStrength={80}
              roughness={1}
              depthScale={1.2}
              minDepthThreshold={0.4}
              maxDepthThreshold={1.4}
              color="#202020"
              metalness={0.8}
              mirror={0}
            />
          </mesh>

          {/* Grid Helper */}
          {showGrid && (
            <gridHelper args={[200, 40, '#444444', '#222222']} position={[0, -19.9, 0]} />
          )}

          {/* Main Crate Assembly */}
          <Suspense fallback={null}>
            <CrateAssembly
              crateData={crateData}
              exploded={exploded}
              showDimensions={showDimensions}
              showWireframe={showWireframe}
              material={material}
              highlightedComponent={undefined}
            />
          </Suspense>

          {/* Soft shadows */}
          <AccumulativeShadows
            temporal
            frames={60}
            alphaTest={0.85}
            scale={20}
            position={[0, -19.8, 0]}
          >
            <RandomizedLight
              amount={4}
              radius={9}
              intensity={0.55}
              ambient={0.25}
              position={[5, 10, -5]}
            />
            <RandomizedLight
              amount={4}
              radius={5}
              intensity={0.25}
              ambient={0.55}
              position={[-5, 5, -9]}
            />
          </AccumulativeShadows>

          {/* Post Processing Effects */}
          {postProcessing && (
            <EffectComposer>
              <Bloom
                intensity={0.5}
                luminanceThreshold={0.9}
                luminanceSmoothing={0.025}
                mipmapBlur
              />
              <Vignette offset={0.1} darkness={0.3} />
              {/* SSAO temporarily disabled due to type issues */}
              {/* <SSAO
                samples={31}
                radius={5}
                intensity={30}
                luminanceInfluence={0.1}
              /> */}
              <DepthOfField
                focusDistance={0.01}
                focalLength={0.05}
                bokehScale={2}
                height={480}
              />
            </EffectComposer>
          )}

          {/* Performance Stats */}
          {showStats && <Stats />}
        </Canvas>

        {/* Loading State */}
        {!crateData && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
              color: 'white'
            }}
          >
            <ViewInAr sx={{ fontSize: 64, mb: 2, opacity: 0.7 }} />
            <Typography variant="h5" gutterBottom>
              Studio 3D Visualization
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.7 }}>
              Professional engineering visualization system ready
            </Typography>
          </Box>
        )}

        {/* Controls Help Overlay */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 20,
            left: 20,
            backgroundColor: 'rgba(0,0,0,0.8)',
            color: 'white',
            p: 2,
            borderRadius: 2,
            maxWidth: 300
          }}
        >
          <Typography variant="subtitle2" gutterBottom fontWeight="bold">
            Interactive Controls
          </Typography>
          <Stack spacing={0.5}>
            <Typography variant="caption">
              • Left Click + Drag: Rotate view
            </Typography>
            <Typography variant="caption">
              • Right Click + Drag: Pan camera
            </Typography>
            <Typography variant="caption">
              • Scroll: Zoom in/out
            </Typography>
            <Typography variant="caption">
              • Hover: Highlight components
            </Typography>
            <Typography variant="caption">
              • Click: Select component
            </Typography>
          </Stack>
        </Box>

        {/* Component Info Panel */}
        <Box
          sx={{
            position: 'absolute',
            top: 20,
            left: 20,
            backgroundColor: 'rgba(0,0,0,0.8)',
            color: 'white',
            p: 2,
            borderRadius: 2,
            maxWidth: 250
          }}
        >
          <Typography variant="subtitle2" gutterBottom fontWeight="bold">
            Crate Specifications
          </Typography>
          <Stack spacing={1}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption">Dimensions:</Typography>
              <Typography variant="caption" fontWeight="bold">
                {crateData?.length || 48}" × {crateData?.width || 40}" × {crateData?.height || 36}"
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption">Material:</Typography>
              <Typography variant="caption" fontWeight="bold">
                {WOOD_MATERIALS[material as keyof typeof WOOD_MATERIALS]?.name}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption">Panel Thickness:</Typography>
              <Typography variant="caption" fontWeight="bold">
                {crateData?.plywood_thickness || 0.75}"
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption">Components:</Typography>
              <Typography variant="caption" fontWeight="bold">
                {5 + Math.ceil((crateData?.width || 40) / (crateData?.floorboard_width || 5.5))} pieces
              </Typography>
            </Box>
          </Stack>
        </Box>

        {/* Quality Badge */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 20,
            right: 20,
            backgroundColor: 'rgba(102, 126, 234, 0.9)',
            color: 'white',
            px: 2,
            py: 1,
            borderRadius: 20,
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          <AutoFixHigh sx={{ fontSize: 20 }} />
          <Typography variant="caption" fontWeight="bold">
            STUDIO QUALITY
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default ProfessionalCrateViewer;