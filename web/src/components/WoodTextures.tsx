import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import { useMemo } from 'react';

// Generate procedural wood texture
export function generateWoodTexture(): THREE.Texture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const context = canvas.getContext('2d')!;

  // Create wood grain pattern
  const gradient = context.createLinearGradient(0, 0, 512, 0);
  
  // Wood base colors
  const baseColor = '#8B7355';
  const darkGrain = '#6B5345';
  const lightGrain = '#AB8365';

  // Create multiple wood grain lines
  for (let i = 0; i < canvas.width; i++) {
    const x = i;
    const variation = Math.sin(i * 0.05) * 10 + Math.sin(i * 0.02) * 20;
    
    context.beginPath();
    context.strokeStyle = i % 8 < 4 ? darkGrain : lightGrain;
    context.lineWidth = 1 + Math.random() * 2;
    context.moveTo(x, 0);
    
    for (let y = 0; y < canvas.height; y += 10) {
      const offset = Math.sin(y * 0.01 + i * 0.05) * variation;
      context.lineTo(x + offset, y);
    }
    context.stroke();
  }

  // Add wood knots
  const numKnots = Math.floor(Math.random() * 3) + 1;
  for (let k = 0; k < numKnots; k++) {
    const knotX = Math.random() * canvas.width;
    const knotY = Math.random() * canvas.height;
    const knotRadius = Math.random() * 20 + 10;
    
    const knotGradient = context.createRadialGradient(
      knotX, knotY, 0,
      knotX, knotY, knotRadius
    );
    knotGradient.addColorStop(0, darkGrain);
    knotGradient.addColorStop(0.5, '#4B3621');
    knotGradient.addColorStop(1, baseColor);
    
    context.fillStyle = knotGradient;
    context.beginPath();
    context.arc(knotX, knotY, knotRadius, 0, Math.PI * 2);
    context.fill();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1, 1);
  
  return texture;
}

// Wood material configurations
export const WOOD_CONFIGS = {
  oak: {
    baseColor: '#8B7355',
    roughness: 0.8,
    metalness: 0.1,
    normalScale: 0.5,
    aoIntensity: 1,
    envMapIntensity: 0.5
  },
  pine: {
    baseColor: '#DEB887',
    roughness: 0.7,
    metalness: 0.05,
    normalScale: 0.3,
    aoIntensity: 0.8,
    envMapIntensity: 0.3
  },
  mahogany: {
    baseColor: '#6F4E37',
    roughness: 0.6,
    metalness: 0.15,
    normalScale: 0.4,
    aoIntensity: 1.2,
    envMapIntensity: 0.7
  },
  birch: {
    baseColor: '#F5DEB3',
    roughness: 0.5,
    metalness: 0.02,
    normalScale: 0.2,
    aoIntensity: 0.6,
    envMapIntensity: 0.2
  },
  walnut: {
    baseColor: '#4B3621',
    roughness: 0.7,
    metalness: 0.1,
    normalScale: 0.6,
    aoIntensity: 1.3,
    envMapIntensity: 0.6
  }
};

// Custom wood material with PBR properties
export function WoodMaterial({ type = 'oak', ...props }: { type?: keyof typeof WOOD_CONFIGS } & any) {
  const config = WOOD_CONFIGS[type];
  const woodTexture = useMemo(() => generateWoodTexture(), []);
  
  // Generate normal map from wood texture
  const normalMap = useMemo(() => {
    const normalCanvas = document.createElement('canvas');
    normalCanvas.width = 512;
    normalCanvas.height = 512;
    const ctx = normalCanvas.getContext('2d')!;
    
    // Create a simple normal map effect
    const gradient = ctx.createLinearGradient(0, 0, 512, 512);
    gradient.addColorStop(0, '#8080ff');
    gradient.addColorStop(0.5, '#8080ff');
    gradient.addColorStop(1, '#8080ff');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 512, 512);
    
    return new THREE.CanvasTexture(normalCanvas);
  }, []);

  return (
    <meshStandardMaterial
      map={woodTexture}
      normalMap={normalMap}
      normalScale={new THREE.Vector2(config.normalScale, config.normalScale)}
      roughness={config.roughness}
      metalness={config.metalness}
      color={config.baseColor}
      aoMapIntensity={config.aoIntensity}
      envMapIntensity={config.envMapIntensity}
      {...props}
    />
  );
}

// Plywood edge texture
export function generatePlywoodEdgeTexture(): THREE.Texture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 64;
  const context = canvas.getContext('2d')!;

  // Draw plywood layers
  const layers = 7;
  const layerHeight = canvas.height / layers;
  
  for (let i = 0; i < layers; i++) {
    const y = i * layerHeight;
    const isLight = i % 2 === 0;
    
    context.fillStyle = isLight ? '#D2B48C' : '#8B7355';
    context.fillRect(0, y, canvas.width, layerHeight);
    
    // Add some grain texture to each layer
    context.strokeStyle = isLight ? '#C19A6B' : '#7A6145';
    context.lineWidth = 0.5;
    
    for (let x = 0; x < canvas.width; x += 5) {
      context.beginPath();
      context.moveTo(x, y);
      context.lineTo(x + 2, y + layerHeight);
      context.stroke();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  
  return texture;
}