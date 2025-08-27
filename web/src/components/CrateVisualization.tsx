'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Box, Paper, Typography, IconButton, Tooltip, ButtonGroup, Button } from '@mui/material';
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
  VisibilityOff
} from '@mui/icons-material';

interface CrateVisualizationProps {
  crateData?: any;
  width?: number;
  height?: number;
  className?: string;
}

interface Component3D {
  name: string;
  type: string;
  vertices: number[][];
  faces: number[][];
  color: string;
  opacity: number;
  material: string;
  thickness: number;
}

interface CrateModel3D {
  length: number;
  width: number;
  height: number;
  components: Component3D[];
}

const CrateVisualization: React.FC<CrateVisualizationProps> = ({ 
  crateData, 
  width = 800, 
  height = 600,
  className 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showWireframe, setShowWireframe] = useState(false);
  const [showDimensions, setShowDimensions] = useState(true);
  const [rotation, setRotation] = useState({ x: 0.3, y: 0.3, z: 0 });
  const [zoom, setZoom] = useState(1);
  const [model, setModel] = useState<CrateModel3D | null>(null);

  // Create 3D model from crate data
  const createCrateModel = (data: any): CrateModel3D => {
    if (!data) {
      // Default model for demonstration
      return {
        length: 48,
        width: 40,
        height: 36,
        components: []
      };
    }

    const length = data.dimensions?.length || data.length || 48;
    const width = data.dimensions?.width || data.width || 40;
    const height = data.dimensions?.height || data.height || 36;
    const plywoodThickness = data.plywood_thickness || 0.75;

    const components: Component3D[] = [];

    // Create front panel
    components.push({
      name: 'Front Panel',
      type: 'front_panel',
      vertices: [
        [0, 0, 0],
        [length, 0, 0],
        [length, 0, height],
        [0, 0, height],
        [0, plywoodThickness, 0],
        [length, plywoodThickness, 0],
        [length, plywoodThickness, height],
        [0, plywoodThickness, height]
      ],
      faces: [
        [0, 1, 2, 3], // Front face
        [4, 7, 6, 5], // Back face
        [0, 4, 5, 1], // Bottom face
        [3, 2, 6, 7], // Top face
        [0, 3, 7, 4], // Left face
        [1, 5, 6, 2]  // Right face
      ],
      color: '#8B7355',
      opacity: 0.8,
      material: 'plywood',
      thickness: plywoodThickness
    });

    // Create back panel
    const backVertices = components[0].vertices.map(v => [v[0], v[1] + width - plywoodThickness, v[2]]);
    components.push({
      name: 'Back Panel',
      type: 'back_panel',
      vertices: backVertices,
      faces: components[0].faces,
      color: '#8B7355',
      opacity: 0.8,
      material: 'plywood',
      thickness: plywoodThickness
    });

    // Create left panel
    components.push({
      name: 'Left Panel',
      type: 'left_panel',
      vertices: [
        [0, 0, 0],
        [0, width, 0],
        [0, width, height],
        [0, 0, height],
        [plywoodThickness, 0, 0],
        [plywoodThickness, width, 0],
        [plywoodThickness, width, height],
        [plywoodThickness, 0, height]
      ],
      faces: components[0].faces,
      color: '#8B7355',
      opacity: 0.8,
      material: 'plywood',
      thickness: plywoodThickness
    });

    // Create right panel
    const rightVertices = components[2].vertices.map(v => [v[0] + length - plywoodThickness, v[1], v[2]]);
    components.push({
      name: 'Right Panel',
      type: 'right_panel',
      vertices: rightVertices,
      faces: components[0].faces,
      color: '#8B7355',
      opacity: 0.8,
      material: 'plywood',
      thickness: plywoodThickness
    });

    // Create top panel
    components.push({
      name: 'Top Panel',
      type: 'top_panel',
      vertices: [
        [0, 0, height - plywoodThickness],
        [length, 0, height - plywoodThickness],
        [length, width, height - plywoodThickness],
        [0, width, height - plywoodThickness],
        [0, 0, height],
        [length, 0, height],
        [length, width, height],
        [0, width, height]
      ],
      faces: components[0].faces,
      color: '#8B7355',
      opacity: 0.8,
      material: 'plywood',
      thickness: plywoodThickness
    });

    // Create bottom/floor boards
    const boardWidth = data.floorboard_width || 5.5;
    const boardThickness = data.floorboard_thickness || 0.75;
    const numBoards = Math.ceil(width / boardWidth);

    for (let i = 0; i < numBoards; i++) {
      const yPos = i * boardWidth;
      const actualWidth = Math.min(boardWidth, width - yPos);
      
      components.push({
        name: `Floorboard ${i + 1}`,
        type: 'floorboard',
        vertices: [
          [0, yPos, 0],
          [length, yPos, 0],
          [length, yPos + actualWidth, 0],
          [0, yPos + actualWidth, 0],
          [0, yPos, boardThickness],
          [length, yPos, boardThickness],
          [length, yPos + actualWidth, boardThickness],
          [0, yPos + actualWidth, boardThickness]
        ],
        faces: components[0].faces,
        color: '#7A6A5A',
        opacity: 0.9,
        material: 'lumber',
        thickness: boardThickness
      });
    }

    return {
      length,
      width,
      height,
      components
    };
  };

  // 3D rendering functions
  const project3D = (vertex: number[], cameraDistance: number = 500) => {
    const [x, y, z] = vertex;
    
    // Apply rotation
    const cos_x = Math.cos(rotation.x);
    const sin_x = Math.sin(rotation.x);
    const cos_y = Math.cos(rotation.y);
    const sin_y = Math.sin(rotation.y);
    const cos_z = Math.cos(rotation.z);
    const sin_z = Math.sin(rotation.z);

    // Rotate around X axis
    let y1 = y * cos_x - z * sin_x;
    let z1 = y * sin_x + z * cos_x;
    
    // Rotate around Y axis
    let x2 = x * cos_y + z1 * sin_y;
    let z2 = -x * sin_y + z1 * cos_y;
    
    // Rotate around Z axis
    let x3 = x2 * cos_z - y1 * sin_z;
    let y3 = x2 * sin_z + y1 * cos_z;

    // Apply zoom and projection
    const factor = cameraDistance / (cameraDistance + z2);
    const screenX = x3 * factor * zoom;
    const screenY = y3 * factor * zoom;

    return [screenX, screenY, z2];
  };

  const drawComponent = (ctx: CanvasRenderingContext2D, component: Component3D, centerX: number, centerY: number) => {
    const projectedVertices = component.vertices.map(vertex => {
      // Center the model
      const centeredVertex = [
        vertex[0] - model!.length / 2,
        vertex[1] - model!.width / 2,
        vertex[2] - model!.height / 2
      ];
      const projected = project3D(centeredVertex);
      return [projected[0] + centerX, projected[1] + centerY, projected[2]];
    });

    // Sort faces by average Z depth for proper rendering order
    const facesWithDepth = component.faces.map(face => {
      const avgZ = face.reduce((sum, vertexIndex) => sum + projectedVertices[vertexIndex][2], 0) / face.length;
      return { face, avgZ };
    });

    facesWithDepth.sort((a, b) => b.avgZ - a.avgZ);

    // Draw faces
    facesWithDepth.forEach(({ face }) => {
      ctx.beginPath();
      
      face.forEach((vertexIndex, i) => {
        const [x, y] = projectedVertices[vertexIndex];
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.closePath();

      if (showWireframe) {
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 1;
        ctx.stroke();
      } else {
        // Fill face
        ctx.fillStyle = component.color;
        ctx.globalAlpha = component.opacity;
        ctx.fill();
        
        // Draw outline
        ctx.strokeStyle = '#444444';
        ctx.lineWidth = 0.5;
        ctx.globalAlpha = 1;
        ctx.stroke();
      }
    });

    ctx.globalAlpha = 1;
  };

  const drawDimensions = (ctx: CanvasRenderingContext2D, centerX: number, centerY: number) => {
    if (!model || !showDimensions) return;

    ctx.fillStyle = '#FF0000';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';

    // Length dimension
    ctx.fillText(`${model.length}"`, centerX, centerY + 150);
    
    // Width dimension
    ctx.save();
    ctx.translate(centerX - 150, centerY);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(`${model.width}"`, 0, 0);
    ctx.restore();

    // Height dimension
    ctx.fillText(`${model.height}"`, centerX + 150, centerY);
  };

  const render = () => {
    const canvas = canvasRef.current;
    if (!canvas || !model) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Draw components
    model.components.forEach(component => {
      drawComponent(ctx, component, centerX, centerY);
    });

    // Draw dimensions
    drawDimensions(ctx, centerX, centerY);
  };

  const animate = () => {
    render();
    animationRef.current = requestAnimationFrame(animate);
  };

  // Initialize model and start animation
  useEffect(() => {
    const newModel = createCrateModel(crateData);
    setModel(newModel);
  }, [crateData]);

  useEffect(() => {
    if (model) {
      animate();
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [model, rotation, zoom, showWireframe, showDimensions]);

  // Control handlers
  const handleRotateLeft = () => {
    setRotation(prev => ({ ...prev, y: prev.y - 0.1 }));
  };

  const handleRotateRight = () => {
    setRotation(prev => ({ ...prev, y: prev.y + 0.1 }));
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.1, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.1, 0.3));
  };

  const handleReset = () => {
    setRotation({ x: 0.3, y: 0.3, z: 0 });
    setZoom(1);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const toggleWireframe = () => {
    setShowWireframe(!showWireframe);
  };

  const toggleDimensions = () => {
    setShowDimensions(!showDimensions);
  };

  // Mouse controls for rotation
  const handleMouseDown = (e: React.MouseEvent) => {
    const startX = e.clientX;
    const startY = e.clientY;
    const startRotation = { ...rotation };

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      
      setRotation({
        x: startRotation.x + deltaY * 0.01,
        y: startRotation.y + deltaX * 0.01,
        z: startRotation.z
      });
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // Wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(prev => Math.max(0.3, Math.min(3, prev * delta)));
  };

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        height: isFullscreen ? '100vh' : height,
        width: isFullscreen ? '100vw' : '100%',
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? 9999 : 'auto',
        backgroundColor: 'background.paper',
        borderRadius: isFullscreen ? 0 : 1,
        overflow: 'hidden'
      }}
      className={className}
    >
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ViewInAr color="primary" />
          <Typography variant="h6">
            3D Crate Visualization
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <ButtonGroup size="small" variant="outlined">
            <Tooltip title="Zoom Out">
              <IconButton onClick={handleZoomOut} size="small">
                <ZoomOut />
              </IconButton>
            </Tooltip>
            <Tooltip title="Zoom In">
              <IconButton onClick={handleZoomIn} size="small">
                <ZoomIn />
              </IconButton>
            </Tooltip>
            <Tooltip title="Rotate Left">
              <IconButton onClick={handleRotateLeft} size="small">
                <RotateLeft />
              </IconButton>
            </Tooltip>
            <Tooltip title="Rotate Right">
              <IconButton onClick={handleRotateRight} size="small">
                <RotateRight />
              </IconButton>
            </Tooltip>
            <Tooltip title="Reset View">
              <IconButton onClick={handleReset} size="small">
                <Refresh />
              </IconButton>
            </Tooltip>
          </ButtonGroup>

          <ButtonGroup size="small" variant="outlined">
            <Tooltip title={showWireframe ? "Solid View" : "Wireframe View"}>
              <IconButton onClick={toggleWireframe} size="small">
                <Settings />
              </IconButton>
            </Tooltip>
            <Tooltip title={showDimensions ? "Hide Dimensions" : "Show Dimensions"}>
              <IconButton onClick={toggleDimensions} size="small">
                {showDimensions ? <Visibility /> : <VisibilityOff />}
              </IconButton>
            </Tooltip>
            <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
              <IconButton onClick={toggleFullscreen} size="small">
                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
              </IconButton>
            </Tooltip>
          </ButtonGroup>
        </Box>
      </Box>

      {/* 3D Canvas */}
      <Box sx={{ 
        position: 'relative',
        height: `calc(100% - 73px)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f5f5f5',
        backgroundImage: `
          linear-gradient(45deg, #e0e0e0 25%, transparent 25%), 
          linear-gradient(-45deg, #e0e0e0 25%, transparent 25%), 
          linear-gradient(45deg, transparent 75%, #e0e0e0 75%), 
          linear-gradient(-45deg, transparent 75%, #e0e0e0 75%)
        `,
        backgroundSize: '20px 20px',
        backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px'
      }}>
        <canvas
          ref={canvasRef}
          width={isFullscreen ? window.innerWidth : width}
          height={isFullscreen ? window.innerHeight - 73 : height - 73}
          style={{ 
            cursor: 'grab',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: 'white'
          }}
          onMouseDown={handleMouseDown}
          onWheel={handleWheel}
        />

        {/* Loading/Empty State */}
        {!model && (
          <Box sx={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
            color: 'text.secondary'
          }}>
            <ViewInAr sx={{ fontSize: 48 }} />
            <Typography variant="h6">
              3D Model Loading...
            </Typography>
            <Typography variant="body2">
              Interactive 3D visualization will appear here
            </Typography>
          </Box>
        )}

        {/* Controls Help */}
        <Box sx={{
          position: 'absolute',
          bottom: 16,
          left: 16,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          p: 1,
          borderRadius: 1,
          fontSize: '0.75rem'
        }}>
          <Typography variant="caption" display="block">
            • Click and drag to rotate
          </Typography>
          <Typography variant="caption" display="block">
            • Scroll to zoom
          </Typography>
          <Typography variant="caption" display="block">
            • Use toolbar for controls
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default CrateVisualization;