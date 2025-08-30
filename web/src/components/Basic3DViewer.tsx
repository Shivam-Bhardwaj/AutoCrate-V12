'use client';

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Box, Text } from '@react-three/drei';
import { Box as MuiBox, Typography } from '@mui/material';
import * as THREE from 'three';

interface Basic3DViewerProps {
  crateData?: any;
}

function CrateModel({ dimensions }: { dimensions: any }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Rotate the crate slowly
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }
  });

  if (!dimensions) return null;

  const width = dimensions.external_width || 48;
  const height = dimensions.external_height || 36;
  const length = dimensions.external_length || 48;

  // Scale down for display (divide by 10 to fit in view)
  const scale = 0.1;
  const w = width * scale;
  const h = height * scale;
  const l = length * scale;

  return (
    <group>
      {/* Main crate box */}
      <Box 
        ref={meshRef}
        args={[w, h, l]} 
        position={[0, 0, 0]}
      >
        <meshStandardMaterial 
          color="#8B7355" 
          wireframe={false}
          opacity={0.9}
          transparent
        />
      </Box>
      
      {/* Dimension labels */}
      <Text
        position={[0, -h/2 - 1, 0]}
        fontSize={0.5}
        color="black"
        anchorX="center"
        anchorY="middle"
      >
        {`${width.toFixed(1)}" × ${length.toFixed(1)}" × ${height.toFixed(1)}"`}
      </Text>
    </group>
  );
}

export default function Basic3DViewer({ crateData }: Basic3DViewerProps) {
  console.log('Basic3DViewer rendered with data:', crateData);
  
  const dimensions = useMemo(() => {
    if (!crateData?.crate_dimensions) return null;
    return crateData.crate_dimensions;
  }, [crateData]);

  if (!dimensions) {
    return (
      <MuiBox sx={{ 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        bgcolor: '#f5f5f5'
      }}>
        <Typography variant="body2" color="textSecondary">
          Calculate a crate design to see 3D preview
        </Typography>
      </MuiBox>
    );
  }

  return (
    <MuiBox sx={{ height: '100%', width: '100%' }}>
      <Canvas
        camera={{ position: [15, 10, 15], fov: 50 }}
        style={{ background: '#f0f0f0' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />
        
        <CrateModel dimensions={dimensions} />
        
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
        />
        
        {/* Grid helper */}
        <gridHelper args={[20, 20]} />
      </Canvas>
    </MuiBox>
  );
}