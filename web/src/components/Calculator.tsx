'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import {
  TextField,
  Button,
  FormControl,
  FormLabel,
  Select,
  MenuItem,
  FormHelperText,
  CircularProgress,
  Checkbox,
  FormControlLabel,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Box,
  Typography
} from '@mui/material'
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Add as AddIcon
} from '@mui/icons-material'
import { useCalculationStore } from '@/store/calculationStore'
import { AutoCrateCalculator } from '@/lib/autocrate-calculations-fixed'
import { useWebLogger } from '@/hooks/useWebLogger'
// Removed external API imports for offline version

interface FormData {
  productLength: number
  productWidth: number
  productHeight: number
  productWeight: number
  panelThickness: number
  materialType: string
  clearance: number
  includeTop: boolean
}

export function Calculator() {
  const { setCalculationResult, setLoading, setError, calculationResult } = useCalculationStore()
  const [isCalculating, setIsCalculating] = useState(false)
  const { logUserInteraction, logError, logInfo, logPerformance } = useWebLogger('Calculator')

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue
  } = useForm<FormData>({
    defaultValues: {
      productLength: 48,
      productWidth: 40,
      productHeight: 36,
      productWeight: 500,
      panelThickness: 0.25,
      materialType: 'plywood',
      clearance: 2.0,
      includeTop: true
    }
  })

  const onSubmit = async (data: FormData) => {
    const startTime = performance.now()
    
    logUserInteraction('calculation-started', 'calculate-button', data)
    logInfo('Starting calculation', data)
    
    setIsCalculating(true)
    setLoading(true)
    setError(null)

    try {
      // Use TypeScript calculator for offline operation
      logInfo('Using TypeScript calculator (offline mode)')
      const calculator = new AutoCrateCalculator()
      
      const result: any = calculator.calculate(
        {
          length: data.productLength,
          width: data.productWidth,
          height: data.productHeight,
          weight: data.productWeight
        },
        {
          panelThickness: data.panelThickness,
          materialType: data.materialType as 'plywood' | 'osb',
          lumberSizes: ['1.5x3.5', '1.5x5.5']
        },
        data.clearance,
        data.includeTop,
        2.0, // clearanceAbove
        4.0, // groundClearance
        1.5, // cleatThickness
        3.5, // cleatMemberWidth
        1.5, // floorboardThickness
        true, // allow3x4Skids
        6.0, // maxGap
        1.5, // minCustom
        false // forceCustomBoard
      )
      // Mark as offline calculation
      result.engine = 'offline'
      
      const endTime = performance.now()
      const duration = endTime - startTime
      
      logPerformance('calculation-duration', duration, { inputData: data })
      logInfo('Calculation completed successfully', { 
        duration,
        resultSummary: {
          externalLength: result.crate_dimensions?.external_length,
          externalWidth: result.crate_dimensions?.external_width,
          externalHeight: result.crate_dimensions?.external_height,
          hasResult: !!result
        }
      })
      
      // Store the request data for downloads
      const requestData = {
        product: {
          length: data.productLength,
          width: data.productWidth,
          height: data.productHeight,
          weight: data.productWeight
        },
        materials: {
          panel_thickness: data.panelThickness,
          material_type: data.materialType,
          lumber_sizes: ['1.5x3.5', '1.5x5.5']
        },
        clearance: data.clearance,
        include_top: data.includeTop
      }
      
      // Store results and request data
      useCalculationStore.setState({ 
        lastRequest: requestData,
        calculationResult: result as any,
        isLoading: false
      })
      
      setCalculationResult(result as any)
    } catch (err: any) {
      const endTime = performance.now()
      const duration = endTime - startTime
      
      logError(err, 'calculation-error', { duration, inputData: data })
      setError(err.message || 'Calculation failed')
    } finally {
      setIsCalculating(false)
      setLoading(false)
    }
  }

  const [presets, setPresets] = useState([
    { name: 'Small Crate', icon: 'S', length: 24, width: 18, height: 20, weight: 150, desc: 'Small electronics or tools' },
    { name: 'Medium Crate', icon: 'M', length: 48, width: 36, height: 32, weight: 500, desc: 'Standard shipping size' },
    { name: 'Large Crate', icon: 'L', length: 96, width: 48, height: 40, weight: 1200, desc: 'Machinery or furniture' },
    { name: 'Narrow Tall', icon: 'NT', length: 20, width: 20, height: 96, weight: 800, desc: 'Pipes or long items' },
    { name: 'Wide Flat', icon: 'WF', length: 120, width: 96, height: 24, weight: 600, desc: 'Panels or sheets' },
    { name: 'Heavy Duty', icon: 'HD', length: 72, width: 60, height: 48, weight: 3000, desc: 'Industrial equipment' },
    { name: 'Extra Large', icon: 'XL', length: 120, width: 120, height: 72, weight: 5000, desc: 'Maximum capacity' },
    { name: 'Minimal', icon: 'MIN', length: 12, width: 12, height: 18, weight: 75, desc: 'Smallest possible crate' }
  ]);
  const [editingRow, setEditingRow] = useState<string | null>(null);
  const [editedPreset, setEditedPreset] = useState<any>(null);

  const handlePresetSelect = (preset: any) => {
    logUserInteraction('preset-selected', 'preset-button', { presetName: preset.name })
    setValue('productLength', preset.length)
    setValue('productWidth', preset.width)
    setValue('productHeight', preset.height)
    setValue('productWeight', preset.weight)
  }

  const handleEdit = (preset: any) => {
    setEditingRow(preset.name);
    setEditedPreset({ ...preset });
  };

  const handleSave = () => {
    setPresets(presets.map(p => p.name === editedPreset.name ? editedPreset : p));
    setEditingRow(null);
    setEditedPreset(null);
  };

  const handleDelete = (presetName: string) => {
    setPresets(presets.filter(p => p.name !== presetName));
  };

  const handleAdd = () => {
    const newPreset = { name: `New Preset ${presets.length + 1}`, icon: 'N', length: 0, width: 0, height: 0, weight: 0, desc: '' };
    setPresets([...presets, newPreset]);
    handleEdit(newPreset);
  };

  return (
    <Box sx={{ 
      height: { xs: 'auto', md: '100%' }, 
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Calculate Button - Fixed at top */}
      <Box sx={{ p: 2, flexShrink: 0, borderBottom: 1, borderColor: 'divider' }}>
        <Button
          type="submit"
          variant="contained"
          fullWidth
          size="medium"
          disabled={isCalculating}
          onClick={handleSubmit(onSubmit)}
          startIcon={isCalculating ? <CircularProgress size={18} /> : null}
          sx={{ py: 1.5, mb: 1 }}
        >
          {isCalculating ? 'Calculating...' : 'Calculate Design'}
        </Button>
        
        {/* Generate Crate Button - visible after calculation */}
        {calculationResult && (
          <Button
            variant="outlined"
            fullWidth
            size="medium"
            color="success"
            onClick={() => {
              console.log('Generate Crate button clicked')
              console.log('Looking for download button...')
              // Trigger the download from ResultsPanel
              const downloadButton = document.querySelector('[data-download-nx="true"]') as HTMLButtonElement
              console.log('Download button found:', downloadButton)
              if (downloadButton) {
                console.log('Clicking download button...')
                downloadButton.click()
              } else {
                console.warn('Download button not found in DOM')
                // Try alternative method
                const allButtons = document.querySelectorAll('button')
                const nxButton = Array.from(allButtons).find(btn => btn.textContent?.includes('Download NX'))
                if (nxButton) {
                  console.log('Found NX button by text, clicking...')
                  nxButton.click()
                } else {
                  alert('Please use the Download NX File button in the Results panel')
                }
              }
            }}
            sx={{ py: 1.5 }}
          >
            Generate Crate Files
          </Button>
        )}
      </Box>

      {/* Scrollable Form Content */}
      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto',
        px: 2,
        pb: 2,
        '&::-webkit-scrollbar': { width: '6px' },
        '&::-webkit-scrollbar-track': { bgcolor: 'transparent' },
        '&::-webkit-scrollbar-thumb': { 
          bgcolor: 'divider', 
          borderRadius: '3px',
          '&:hover': { bgcolor: 'text.disabled' }
        }
      }}>
        <form className="space-y-4">
          {/* Quick Presets - Compact */}
          <Box sx={{ pt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Quick Presets</Typography>
              <IconButton onClick={handleAdd} size="small"><AddIcon fontSize="small" /></IconButton>
            </Box>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(80px, 1fr))', 
              gap: 1,
              mb: 2
            }}>
              {presets.slice(0, 6).map((preset) => (
                <Box
                  key={preset.name}
                  onClick={() => handlePresetSelect(preset)}
                  onDoubleClick={() => handleEdit(preset)}
                  sx={{
                    p: 1,
                    bgcolor: 'background.paper',
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    cursor: 'pointer',
                    textAlign: 'center',
                    transition: 'all 0.2s',
                    '&:hover': {
                      borderColor: 'primary.main',
                      bgcolor: 'action.hover'
                    }
                  }}
                >
                  <Typography variant="caption" display="block" sx={{ fontWeight: 600, fontSize: '0.7rem' }}>
                    {preset.icon}
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ fontSize: '0.65rem', lineHeight: 1.2 }}>
                    {preset.name.split(' ')[0]}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>

          <Divider />

          {/* Product Dimensions - Compact Grid */}
          <div>
            <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>Product Dimensions</Typography>
            
            <div className="grid grid-cols-2 gap-2">
              <TextField
                label="L (in)"
                type="number"
                size="small"
                fullWidth
                {...register('productLength', {
                  required: 'Length required',
                  min: { value: 12, message: 'Min 12"' },
                  max: { value: 130, message: 'Max 130"' }
                })}
                error={!!errors.productLength}
                helperText={errors.productLength?.message}
              />
              
              <TextField
                label="W (in)"
                type="number"
                size="small"
                fullWidth
                {...register('productWidth', {
                  required: 'Width required',
                  min: { value: 12, message: 'Min 12"' },
                  max: { value: 130, message: 'Max 130"' }
                })}
                error={!!errors.productWidth}
                helperText={errors.productWidth?.message}
              />
              
              <TextField
                label="H (in)"
                type="number"
                size="small"
                fullWidth
                {...register('productHeight', {
                  required: 'Height required',
                  min: { value: 12, message: 'Min 12"' },
                  max: { value: 130, message: 'Max 130"' }
                })}
                error={!!errors.productHeight}
                helperText={errors.productHeight?.message}
              />
              
              <TextField
                label="Wt (lbs)"
                type="number"
                size="small"
                fullWidth
                {...register('productWeight', {
                  required: 'Weight required',
                  min: { value: 1, message: 'Min 1 lb' },
                  max: { value: 20000, message: 'Max 20k lbs' }
                })}
                error={!!errors.productWeight}
                helperText={errors.productWeight?.message}
              />
            </div>
          </div>

          <Divider />

          {/* Materials - Compact */}
          <div>
            <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>Materials</Typography>
            
            <div className="space-y-2">
              <Box sx={{ display: 'flex', gap: 1 }}>
                <FormControl size="small" sx={{ flex: 1 }}>
                  <Select
                    {...register('materialType')}
                    defaultValue="plywood"
                  >
                    <MenuItem value="plywood">Plywood</MenuItem>
                    <MenuItem value="osb">OSB</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl size="small" sx={{ flex: 1 }}>
                  <Select
                    {...register('panelThickness')}
                    defaultValue={0.25}
                  >
                    <MenuItem value={0.25}>1/4" (Standard)</MenuItem>
                    <MenuItem value={0.375}>3/8"</MenuItem>
                    <MenuItem value={0.5}>1/2"</MenuItem>
                    <MenuItem value={0.625}>5/8"</MenuItem>
                    <MenuItem value={0.75}>3/4"</MenuItem>
                    <MenuItem value={1.0}>1"</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <TextField
                  label="Clearance (in)"
                  type="number"
                  size="small"
                  sx={{ flex: 1 }}
                  {...register('clearance', {
                    required: 'Required',
                    min: { value: 0.5, message: 'Min 0.5"' },
                    max: { value: 6, message: 'Max 6"' }
                  })}
                  error={!!errors.clearance}
                  helperText={errors.clearance?.message}
                />
                
                <FormControlLabel
                  control={
                    <Checkbox
                      {...register('includeTop')}
                      defaultChecked
                      size="small"
                    />
                  }
                  label={<Typography variant="caption">Top</Typography>}
                  sx={{ ml: 1 }}
                />
              </Box>
            </div>
          </div>

          <Divider />

          {/* Extended Presets Table - Collapsible */}
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>All Presets</Typography>
            </Box>
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 200 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Name</TableCell>
                    <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>L</TableCell>
                    <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>W</TableCell>
                    <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>H</TableCell>
                    <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Wt</TableCell>
                    <TableCell align="right" sx={{ py: 0.5, fontSize: '0.75rem' }}>Edit</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {presets.map((preset) => (
                    <TableRow 
                      key={preset.name} 
                      hover 
                      onClick={() => handlePresetSelect(preset)}
                      sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
                    >
                      {editingRow === preset.name ? (
                        <>
                          <TableCell sx={{ py: 0.5 }}><TextField size="small" value={editedPreset.name} onChange={(e) => setEditedPreset({...editedPreset, name: e.target.value})} /></TableCell>
                          <TableCell sx={{ py: 0.5 }}><TextField size="small" type="number" value={editedPreset.length} onChange={(e) => setEditedPreset({...editedPreset, length: Number(e.target.value)})} /></TableCell>
                          <TableCell sx={{ py: 0.5 }}><TextField size="small" type="number" value={editedPreset.width} onChange={(e) => setEditedPreset({...editedPreset, width: Number(e.target.value)})} /></TableCell>
                          <TableCell sx={{ py: 0.5 }}><TextField size="small" type="number" value={editedPreset.height} onChange={(e) => setEditedPreset({...editedPreset, height: Number(e.target.value)})} /></TableCell>
                          <TableCell sx={{ py: 0.5 }}><TextField size="small" type="number" value={editedPreset.weight} onChange={(e) => setEditedPreset({...editedPreset, weight: Number(e.target.value)})} /></TableCell>
                          <TableCell align="right" sx={{ py: 0.5 }}>
                            <IconButton onClick={handleSave} size="small"><SaveIcon fontSize="small" /></IconButton>
                          </TableCell>
                        </>
                      ) : (
                        <>
                          <TableCell component="th" scope="row" sx={{ py: 0.5, fontSize: '0.75rem' }}>{preset.name}</TableCell>
                          <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{preset.length}</TableCell>
                          <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{preset.width}</TableCell>
                          <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{preset.height}</TableCell>
                          <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{preset.weight}</TableCell>
                          <TableCell align="right" sx={{ py: 0.5 }}>
                            <IconButton onClick={(e) => {e.stopPropagation(); handleEdit(preset)}} size="small">
                              <EditIcon fontSize="small" />
                            </IconButton>
                            <IconButton onClick={(e) => {e.stopPropagation(); handleDelete(preset.name)}} size="small">
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </>
                      )}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          <Typography variant="caption" display="block" sx={{ textAlign: 'center', color: 'text.secondary', pt: 1 }}>
            ASTM D6251-17 Compliant
          </Typography>
        </form>
      </Box>
    </Box>
  )
}