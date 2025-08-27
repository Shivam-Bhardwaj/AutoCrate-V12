'use client'

import { useState } from 'react'
import { Card, CardContent, Typography, Grid, Chip, LinearProgress, Button, Box } from '@mui/material'
import { Check, Warning, Info, Download, Description } from '@mui/icons-material'
import { useCalculationStore } from '@/store/calculationStore'
import { generateNXExpression } from '@/lib/autocrate-calculations'
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
    setDownloading(true)
    try {
      console.log('Generating NX expression client-side...')
      
      // Generate NX expression content directly in browser
      const nxContent = generateNXExpression(results)
      
      // Create blob from the content
      const blob = new Blob([nxContent], { type: 'text/plain' })
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // Generate a valid, sortable filename with timestamp
      const now = new Date();
      const year = now.getFullYear();
      const month = (now.getMonth() + 1).toString().padStart(2, '0');
      const day = now.getDate().toString().padStart(2, '0');
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      const seconds = now.getSeconds().toString().padStart(2, '0');
      const filename = `${year}${month}${day}_${hours}${minutes}${seconds}_Crate.exp`;
      
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Download failed:', error)
      alert('Failed to download NX expression file. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Download Section */}
      <Card>
        <CardContent>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Export Options</Typography>
            <div style={{ display: 'flex', gap: '16px' }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<Download />}
                onClick={handleDownloadNXExpression}
                disabled={downloading}
              >
                {downloading ? 'Generating...' : 'Download NX Expression File'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<Description />}
                disabled
                title="PDF Report feature coming soon"
              >
                PDF Report (Coming Soon)
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Crate Dimensions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="body2" color="textSecondary">External Length</Typography>
              <Typography variant="h6">
                {crate_dimensions?.external_length?.toFixed(2)}"
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="body2" color="textSecondary">External Width</Typography>
              <Typography variant="h6">
                {crate_dimensions?.external_width?.toFixed(2)}"
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="body2" color="textSecondary">External Height</Typography>
              <Typography variant="h6">
                {crate_dimensions?.external_height?.toFixed(2)}"
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Panel Summary
          </Typography>
          <div className="space-y-2">
            {Object.entries(panels || {}).map(([name, panel]: [string, any]) => (
              <div key={name} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <Typography variant="body1" className="capitalize">
                  {name} Panel
                </Typography>
                {panel.error ? (
                  <Chip icon={<Warning />} label="Error" color="error" size="small" />
                ) : (
                  <Chip icon={<Check />} label="Calculated" color="success" size="small" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Materials Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Plywood Sheets</Typography>
              <Typography variant="h4">{materials_summary?.plywood_sheets || 0}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Total Area</Typography>
              <Typography variant="h4">{materials_summary?.total_area_sqft || 0} ft²</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Lumber Length</Typography>
              <Typography variant="h4">{materials_summary?.lumber_length_ft || 0} ft</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Est. Weight</Typography>
              <Typography variant="h4">{materials_summary?.estimated_weight_lbs || 0} lbs</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Compliance & Standards
          </Typography>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Typography variant="body1">ASTM D6251-17</Typography>
              {compliance?.astm_d6251 ? (
                <Chip icon={<Check />} label="Compliant" color="success" size="small" />
              ) : (
                <Chip icon={<Warning />} label="Review Required" color="warning" size="small" />
              )}
            </div>
            <div className="flex items-center justify-between">
              <Typography variant="body1">Safety Factor</Typography>
              <Typography variant="h6">{compliance?.safety_factor || 1.5}x</Typography>
            </div>
            <div className="flex items-center justify-between">
              <Typography variant="body1">Max Load Capacity</Typography>
              <Typography variant="h6">{compliance?.max_load || 0} lbs</Typography>
            </div>
            <div className="mt-3">
              <Typography variant="body2" color="textSecondary">Standards Met:</Typography>
              <div className="flex gap-2 mt-1">
                {compliance?.standards_met?.map((standard: string) => (
                  <Chip key={standard} label={standard} size="small" variant="outlined" />
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-green-50 dark:bg-green-900">
        <CardContent>
          <div className="flex items-center gap-2">
            <Info color="info" />
            <Typography variant="body2">
              Design optimized for minimum material waste while maintaining structural integrity
            </Typography>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}