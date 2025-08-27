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
  Divider
} from '@mui/material'
import { useCalculationStore } from '@/store/calculationStore'
import { AutoCrateCalculator } from '@/lib/autocrate-calculations'
import { useWebLogger } from '@/hooks/useWebLogger'
import { loggedFetch } from '@/lib/api-logger'

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
  const { setCalculationResult, setLoading, setError } = useCalculationStore()
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
      panelThickness: 0.75,
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
      // Initialize calculator
      const calculator = new AutoCrateCalculator()
      
      // Perform comprehensive calculation client-side matching desktop version
      const result = calculator.calculate(
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

  const quickTestPresets = [
    { name: 'Small Crate', icon: '📦', length: 24, width: 18, height: 20, weight: 150, desc: 'Small electronics or tools' },
    { name: 'Medium Crate', icon: '📋', length: 48, width: 36, height: 32, weight: 500, desc: 'Standard shipping size' },
    { name: 'Large Crate', icon: '📊', length: 96, width: 48, height: 40, weight: 1200, desc: 'Machinery or furniture' },
    { name: 'Narrow Tall', icon: '🏗️', length: 20, width: 20, height: 96, weight: 800, desc: 'Pipes or long items' },
    { name: 'Wide Flat', icon: '🪟', length: 120, width: 96, height: 24, weight: 600, desc: 'Panels or sheets' },
    { name: 'Heavy Duty', icon: '⚡', length: 72, width: 60, height: 48, weight: 3000, desc: 'Industrial equipment' },
    { name: 'Extra Large', icon: '🏢', length: 120, width: 120, height: 72, weight: 5000, desc: 'Maximum capacity' },
    { name: 'Minimal', icon: '💎', length: 12, width: 12, height: 18, weight: 75, desc: 'Smallest possible crate' }
  ]

  const handlePresetSelect = (preset: any) => {
    logUserInteraction('preset-selected', 'preset-button', { presetName: preset.name })
    setValue('productLength', preset.length)
    setValue('productWidth', preset.width)
    setValue('productHeight', preset.height)
    setValue('productWeight', preset.weight)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-2">Product Dimensions</h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <TextField
            label="Length (inches)"
            type="number"
            size="small"
            fullWidth
            {...register('productLength', {
              required: 'Length is required',
              min: { value: 12, message: 'Min 12 inches' },
              max: { value: 130, message: 'Max 130 inches' }
            })}
            error={!!errors.productLength}
            helperText={errors.productLength?.message}
          />
          
          <TextField
            label="Width (inches)"
            type="number"
            size="small"
            fullWidth
            {...register('productWidth', {
              required: 'Width is required',
              min: { value: 12, message: 'Min 12 inches' },
              max: { value: 130, message: 'Max 130 inches' }
            })}
            error={!!errors.productWidth}
            helperText={errors.productWidth?.message}
          />
          
          <TextField
            label="Height (inches)"
            type="number"
            size="small"
            fullWidth
            {...register('productHeight', {
              required: 'Height is required',
              min: { value: 12, message: 'Min 12 inches' },
              max: { value: 130, message: 'Max 130 inches' }
            })}
            error={!!errors.productHeight}
            helperText={errors.productHeight?.message}
          />
          
          <TextField
            label="Weight (lbs)"
            type="number"
            size="small"
            fullWidth
            {...register('productWeight', {
              required: 'Weight is required',
              min: { value: 1, message: 'Min 1 lb' },
              max: { value: 20000, message: 'Max 20,000 lbs' }
            })}
            error={!!errors.productWeight}
            helperText={errors.productWeight?.message}
          />
        </div>
      </div>

      <Divider />

      <div>
        <h3 className="text-lg font-semibold mb-2">Material Settings</h3>
        
        <div className="space-y-3">
          <FormControl fullWidth size="small">
            <FormLabel>Panel Material</FormLabel>
            <Select
              {...register('materialType')}
              defaultValue="plywood"
            >
              <MenuItem value="plywood">CDX Plywood</MenuItem>
              <MenuItem value="osb">OSB</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth size="small">
            <FormLabel>Panel Thickness</FormLabel>
            <Select
              {...register('panelThickness')}
              defaultValue={0.75}
            >
              <MenuItem value={0.5}>1/2 inch</MenuItem>
              <MenuItem value={0.625}>5/8 inch</MenuItem>
              <MenuItem value={0.75}>3/4 inch</MenuItem>
              <MenuItem value={1.0}>1 inch</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="Clearance (inches)"
            type="number"
            size="small"
            fullWidth
            {...register('clearance', {
              required: 'Clearance is required',
              min: { value: 0.5, message: 'Min 0.5 inches' },
              max: { value: 6, message: 'Max 6 inches' }
            })}
            error={!!errors.clearance}
            helperText={errors.clearance?.message || 'Space between product and crate walls'}
          />
          
          <FormControlLabel
            control={
              <Checkbox
                {...register('includeTop')}
                defaultChecked
              />
            }
            label="Include Top Panel"
          />
        </div>
      </div>

      <Divider />

      <div className="space-y-2">
        <Button
          type="submit"
          variant="contained"
          fullWidth
          size="large"
          disabled={isCalculating}
          startIcon={isCalculating ? <CircularProgress size={20} /> : null}
        >
          {isCalculating ? 'Calculating...' : 'Calculate Crate Design'}
        </Button>
        
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Quick Test Presets</h4>
          <div className="grid grid-cols-2 gap-2">
            {quickTestPresets.map((preset) => (
              <Button
                key={preset.name}
                variant="outlined"
                size="small"
                onClick={() => handlePresetSelect(preset)}
                disabled={isCalculating}
                className="text-xs p-2 h-auto flex flex-col items-start"
              >
                <div className="flex items-center gap-1 mb-1">
                  <span className="text-lg">{preset.icon}</span>
                  <span className="font-medium">{preset.name}</span>
                </div>
                <div className="text-xs text-gray-500 text-left">
                  {preset.length}"×{preset.width}"×{preset.height}" • {preset.weight}lbs
                </div>
              </Button>
            ))}
          </div>
        </div>
      </div>

      <div className="text-xs text-gray-600 dark:text-gray-400 text-center">
        All calculations comply with ASTM D6251-17 standards
      </div>
    </form>
  )
}