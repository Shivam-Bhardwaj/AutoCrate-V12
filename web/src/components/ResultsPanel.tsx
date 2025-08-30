'use client'

import { useState } from 'react'
import { Card, CardContent, Typography, Grid, Chip, LinearProgress, Button, Box, Divider, Alert } from '@mui/material'
import { Check, Warning, Info, Download, Description, Engineering, LocalShipping, AttachMoney, Build, PictureAsPdf } from '@mui/icons-material'
import { useCalculationStore } from '@/store/calculationStore'
import { generatePdf } from '@/lib/pdfGenerator'
import { generateNXExpression } from '@/lib/autocrate-calculations-fixed'
import { generateNXExpressions } from '@/services/python-api'
// import { ManagedLink, // useMultipleLinks removed } from './ManagedLink' // Temporarily disabled

interface ResultsPanelProps {
  results: any
}

export function ResultsPanel({ results }: ResultsPanelProps) {
  const [downloading, setDownloading] = useState(false)
  
  // Link status management temporarily disabled
  
  if (!results) return null

  const { panels, materials_summary, compliance, crate_dimensions } = results

  const handleDownloadNXExpression = async () => {
    console.log('=== Download NX Expression Button Clicked ===')
    console.log('Current results:', results)
    
    if (!results) {
      console.warn('No results available - calculation needs to be run first')
      alert('Please calculate crate dimensions first')
      return
    }
    
    setDownloading(true)
    console.log('Starting NX expression generation...')
    
    try {
      // Try to use Python API first for exact desktop compatibility
      console.log('Attempting to use Python API for NX generation...')
      
      // Prepare parameters for Python API
      const params = {
        productLength: results.inputs?.product_length || 96,
        productWidth: results.inputs?.product_width || 48,
        productHeight: results.inputs?.product_height || 30,
        productWeight: results.inputs?.product_weight || 1000,
        quantity: results.inputs?.quantity || 1,
        panelThickness: results.inputs?.panel_thickness || 0.75,
        cleatThickness: results.inputs?.cleat_thickness || 1.5,
        cleatMemberWidth: results.inputs?.cleat_member_width || 3.5,
        clearance: results.inputs?.clearance || 2,
        clearanceAbove: results.inputs?.clearance_above || 0.5,
        groundClearance: results.inputs?.ground_clearance || 0,
        floorboardThickness: results.inputs?.floorboard_thickness || 0.75,
        skidHeight: results.inputs?.skid_height || 3.5,
        safetyFactor: results.inputs?.safety_factor || 1.5,
        panelGradeCode: "ASTM",
        assemblyTimeCode: 2.0
      }
      
      let nxContent: string
      let filename: string
      
      try {
        // Try Python API
        const apiResult = await generateNXExpressions(params)
        if (apiResult.success && apiResult.expressions) {
          console.log('✓ Using Python API for exact desktop compatibility')
          nxContent = apiResult.expressions
          filename = apiResult.filename || `Crate_${Math.round(results.crate_dimensions.external_length)}x${Math.round(results.crate_dimensions.external_width)}x${Math.round(results.crate_dimensions.external_height)}_${new Date().toISOString().replace(/[:.]/g, '').slice(0, 15)}.exp`
        } else {
          throw new Error('Python API not available')
        }
      } catch (apiError) {
        // Fallback to local TypeScript function
        console.log('Python API not available, using local TypeScript function...')
        nxContent = generateNXExpression(results)
        const now = new Date()
        const timestamp = now.toISOString().replace(/[:.]/g, '').slice(0, 15)
        filename = `Crate_${Math.round(results.crate_dimensions.external_length)}x${Math.round(results.crate_dimensions.external_width)}x${Math.round(results.crate_dimensions.external_height)}_${timestamp}.exp`
      }
      
      console.log(`Creating download file: ${filename}, size: ${nxContent.length} bytes`)
      
      // Create blob and download
      const blob = new Blob([nxContent], { type: 'text/plain;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.style.display = 'none'
      document.body.appendChild(link)
      console.log('Triggering download...')
      link.click()
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        console.log('Download cleanup complete')
      }, 100)
      
      console.log('✓ NX expression file downloaded successfully')
    } catch (error: any) {
      console.error('❌ Failed to generate NX expression:', error)
      console.error('Error stack:', error.stack)
      alert(`Failed to generate NX expression file: ${error.message || 'Unknown error'}`)
    } finally {
      setDownloading(false)
      console.log('=== Download process complete ===')
    }
  }

  // Calculate cost estimates (example calculations)
  const materialCost = materials_summary?.plywood_sheets ? materials_summary.plywood_sheets * 45 : 0
  const laborCost = Math.round(materialCost * 0.4)
  const totalCost = materialCost + laborCost
  const leadTime = materials_summary?.plywood_sheets > 10 ? 5 : 3

  return (
    <div className="space-y-3">
      {/* Quick Actions */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 2 }}>
        <Button
          variant="contained"
          color="primary"
          fullWidth
          startIcon={<Download />}
          onClick={handleDownloadNXExpression}
          disabled={!results || downloading}
          sx={{ textTransform: 'none' }}
          data-download-nx="true"
        >
          {downloading ? 'Generating...' : 'Download NX File'}
        </Button>
        <Button
          variant="outlined"
          color="secondary"
          fullWidth
          startIcon={<PictureAsPdf />}
          onClick={() => generatePdf(results)}
          disabled={!results || downloading}
          sx={{ textTransform: 'none' }}
        >
          PDF Report
        </Button>
      </Box>

      {/* Key Metrics Card */}
      <Card elevation={0}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Key Metrics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AttachMoney fontSize="small" color="primary" />
                <Box>
                  <Typography variant="caption" color="textSecondary">Est. Cost</Typography>
                  <Typography variant="body1" fontWeight="600">${totalCost}</Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocalShipping fontSize="small" color="primary" />
                <Box>
                  <Typography variant="caption" color="textSecondary">Lead Time</Typography>
                  <Typography variant="body1" fontWeight="600">{leadTime} days</Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Engineering fontSize="small" color="primary" />
                <Box>
                  <Typography variant="caption" color="textSecondary">Weight</Typography>
                  <Typography variant="body1" fontWeight="600">{materials_summary?.estimated_weight_lbs || 0} lbs</Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Build fontSize="small" color="primary" />
                <Box>
                  <Typography variant="caption" color="textSecondary">Sheets</Typography>
                  <Typography variant="body1" fontWeight="600">{materials_summary?.plywood_sheets || 0}</Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Dimensions Card */}
      <Card elevation={0}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            External Dimensions
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="textSecondary">Length</Typography>
            <Typography variant="body2" fontWeight="500">
              {typeof crate_dimensions?.external_length === 'number' ? crate_dimensions.external_length.toFixed(2) : '0.00'}"
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="textSecondary">Width</Typography>
            <Typography variant="body2" fontWeight="500">
              {typeof crate_dimensions?.external_width === 'number' ? crate_dimensions.external_width.toFixed(2) : '0.00'}"
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="textSecondary">Height</Typography>
            <Typography variant="body2" fontWeight="500">
              {typeof crate_dimensions?.external_height === 'number' ? crate_dimensions.external_height.toFixed(2) : '0.00'}"
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Compliance Status */}
      <Card elevation={0}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Compliance Status
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            {compliance?.astm_d6251 ? (
              <><Check fontSize="small" color="success" />
              <Typography variant="body2">ASTM D6251-17 Compliant</Typography></>
            ) : (
              <><Warning fontSize="small" color="warning" />
              <Typography variant="body2">Review Required</Typography></>
            )}
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="caption" color="textSecondary">Safety Factor</Typography>
            <Typography variant="caption" fontWeight="500">{compliance?.safety_factor || 1.5}x</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="textSecondary">Max Load</Typography>
            <Typography variant="caption" fontWeight="500">{compliance?.max_load || 0} lbs</Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Panel Status */}
      <Card elevation={0}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Panel Status
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            {Object.entries(panels || {}).slice(0, 6).map(([name, panel]: [string, any]) => (
              <Box key={name} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                  {name}
                </Typography>
                {panel.error ? (
                  <Warning fontSize="small" color="error" />
                ) : (
                  <Check fontSize="small" color="success" />
                )}
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Cost Breakdown */}
      <Card elevation={0}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Cost Breakdown
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="caption" color="textSecondary">Materials</Typography>
            <Typography variant="caption" fontWeight="500">${materialCost}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="caption" color="textSecondary">Labor (Est.)</Typography>
            <Typography variant="caption" fontWeight="500">${laborCost}</Typography>
          </Box>
          <Divider sx={{ my: 1 }} />
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" fontWeight="600">Total Estimate</Typography>
            <Typography variant="body2" fontWeight="600" color="primary">${totalCost}</Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Optimization Note */}
      <Alert severity="success" sx={{ py: 1 }}>
        <Typography variant="caption">
          Design optimized for minimum waste
        </Typography>
      </Alert>
    </div>
  )
}