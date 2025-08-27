'use client';

import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
// import { XRButton } from '@react-three/xr'; // Commented out due to compatibility issues
import { Box as DreiBox, Text, OrbitControls, Environment } from '@react-three/drei';
import { Box, Paper, Typography, Button, Alert, Snackbar } from '@mui/material';
import { ViewInAr, Close, PhotoCamera, TouchApp } from '@mui/icons-material';
import * as THREE from 'three';

interface ARViewerProps {
  crateData?: any;
  open: boolean;
  onClose: () => void;
}

const ARCrate: React.FC<{ crateData: any; scale?: number }> = ({ crateData, scale = 0.01 }) => {
  const dimensions = {
    length: (crateData?.dimensions?.length || crateData?.length || 48) * scale,
    width: (crateData?.dimensions?.width || crateData?.width || 40) * scale,
    height: (crateData?.dimensions?.height || crateData?.height || 36) * scale,
    plywoodThickness: (crateData?.plywood_thickness || 0.75) * scale
  };

  return (
    <group>
      {/* Front Panel */}
      <mesh position={[0, 0, dimensions.height / 2]}>
        <boxGeometry args={[dimensions.length, dimensions.plywoodThickness, dimensions.height]} />
        <meshStandardMaterial color="#8B7355" roughness={0.8} metalness={0.1} />
      </mesh>

      {/* Back Panel */}
      <mesh position={[0, dimensions.width - dimensions.plywoodThickness, dimensions.height / 2]}>
        <boxGeometry args={[dimensions.length, dimensions.plywoodThickness, dimensions.height]} />
        <meshStandardMaterial color="#8B7355" roughness={0.8} metalness={0.1} />
      </mesh>

      {/* Left Panel */}
      <mesh position={[-dimensions.length / 2 + dimensions.plywoodThickness / 2, dimensions.width / 2, dimensions.height / 2]}>
        <boxGeometry args={[dimensions.plywoodThickness, dimensions.width - 2 * dimensions.plywoodThickness, dimensions.height]} />
        <meshStandardMaterial color="#8B7355" roughness={0.8} metalness={0.1} />
      </mesh>

      {/* Right Panel */}
      <mesh position={[dimensions.length / 2 - dimensions.plywoodThickness / 2, dimensions.width / 2, dimensions.height / 2]}>
        <boxGeometry args={[dimensions.plywoodThickness, dimensions.width - 2 * dimensions.plywoodThickness, dimensions.height]} />
        <meshStandardMaterial color="#8B7355" roughness={0.8} metalness={0.1} />
      </mesh>

      {/* Top Panel */}
      <mesh position={[0, dimensions.width / 2, dimensions.height - dimensions.plywoodThickness / 2]}>
        <boxGeometry args={[dimensions.length - 2 * dimensions.plywoodThickness, dimensions.width - 2 * dimensions.plywoodThickness, dimensions.plywoodThickness]} />
        <meshStandardMaterial color="#8B7355" roughness={0.8} metalness={0.1} />
      </mesh>

      {/* Dimension Text */}
      <Text
        position={[0, dimensions.width / 2, dimensions.height + 0.1]}
        fontSize={0.05}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {`${crateData?.length || 48}" × ${crateData?.width || 40}" × ${crateData?.height || 36}"`}
      </Text>
    </group>
  );
};

const ARViewer: React.FC<ARViewerProps> = ({ crateData, open, onClose }) => {
  const [isARSupported, setIsARSupported] = useState(false);
  const [showInstructions, setShowInstructions] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if WebXR is supported
    if ('xr' in navigator) {
      (navigator as any).xr?.isSessionSupported('immersive-ar').then((supported: boolean) => {
        setIsARSupported(supported);
        if (!supported) {
          setError('AR is not supported on this device. Please use a compatible mobile device or AR-enabled browser.');
        }
      });
    } else {
      setError('WebXR is not available in this browser.');
    }
  }, []);

  if (!open) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 10000,
        backgroundColor: 'rgba(0, 0, 0, 0.95)'
      }}
    >
      {/* Header */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          background: 'linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%)',
          p: 2,
          zIndex: 10001,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <ViewInAr sx={{ color: 'white', fontSize: 32 }} />
          <Box>
            <Typography variant="h5" sx={{ color: 'white', fontWeight: 'bold' }}>
              AR Viewer
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              View your crate in augmented reality
            </Typography>
          </Box>
        </Box>
        
        <Button
          variant="contained"
          startIcon={<Close />}
          onClick={onClose}
          sx={{
            backgroundColor: 'rgba(255,255,255,0.2)',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.3)'
            }
          }}
        >
          Close AR
        </Button>
      </Box>

      {/* AR Canvas */}
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        style={{ height: '100%', width: '100%' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />
        
        <Environment preset="city" />
        
        <ARCrate crateData={crateData} scale={0.01} />
        
        <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
      </Canvas>

      {/* AR Button */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 40,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10002
        }}
      >
        <Button
          variant="contained"
          disabled={!isARSupported}
          size="large"
          startIcon={<ViewInAr />}
          sx={{
            background: isARSupported 
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : undefined,
            borderRadius: '30px',
            px: 5,
            py: 2,
            fontSize: '18px',
            fontWeight: 'bold',
            boxShadow: isARSupported 
              ? '0 4px 20px rgba(102, 126, 234, 0.4)'
              : undefined,
            '&:hover': isARSupported ? {
              background: 'linear-gradient(135deg, #5567da 0%, #653a92 100%)',
            } : undefined
          }}
          onClick={() => {
            // This would typically initiate WebXR session
            // For now, just show a message
            setError('AR mode is currently in preview. Full AR support coming soon!');
          }}
        >
          {isARSupported ? 'Start AR Experience' : 'AR Not Available'}
        </Button>
      </Box>

      {/* Instructions */}
      {showInstructions && isARSupported && (
        <Paper
          sx={{
            position: 'absolute',
            bottom: 140,
            left: '50%',
            transform: 'translateX(-50%)',
            p: 3,
            maxWidth: 400,
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderRadius: 2,
            zIndex: 10002
          }}
        >
          <Typography variant="h6" gutterBottom>
            AR Instructions
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <PhotoCamera color="primary" />
              <Typography variant="body2">
                Point your device at a flat surface
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <TouchApp color="primary" />
              <Typography variant="body2">
                Tap to place the crate in your space
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <ViewInAr color="primary" />
              <Typography variant="body2">
                Use pinch gestures to scale and rotate
              </Typography>
            </Box>
          </Box>
          <Button
            variant="text"
            onClick={() => setShowInstructions(false)}
            sx={{ mt: 2 }}
          >
            Got it
          </Button>
        </Paper>
      )}

      {/* Error Message */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="warning" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ARViewer;