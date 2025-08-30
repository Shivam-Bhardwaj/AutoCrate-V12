'use client';

import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface SimpleCrateViewerProps {
  crateData?: any;
}

export default function SimpleCrateViewer({ crateData }: SimpleCrateViewerProps) {
  console.log('SimpleCrateViewer rendered with data:', crateData);
  
  if (!crateData) {
    return (
      <Box sx={{ 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        bgcolor: '#f5f5f5'
      }}>
        <Typography variant="body2" color="textSecondary">
          Calculate a crate design to see 3D preview
        </Typography>
      </Box>
    );
  }

  const { crate_dimensions } = crateData;
  
  return (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center',
      bgcolor: '#f0f0f0',
      p: 2
    }}>
      <Paper sx={{ p: 3, maxWidth: 400 }}>
        <Typography variant="h6" gutterBottom>
          Crate Dimensions (3D View Placeholder)
        </Typography>
        
        <Typography variant="body2" gutterBottom>
          External Dimensions:
        </Typography>
        
        <Box sx={{ pl: 2 }}>
          <Typography variant="body2">
            Length: {crate_dimensions?.external_length?.toFixed(2) || 0}" 
          </Typography>
          <Typography variant="body2">
            Width: {crate_dimensions?.external_width?.toFixed(2) || 0}"
          </Typography>
          <Typography variant="body2">
            Height: {crate_dimensions?.external_height?.toFixed(2) || 0}"
          </Typography>
        </Box>
        
        <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
          3D visualization temporarily disabled for debugging
        </Typography>
      </Paper>
    </Box>
  );
}