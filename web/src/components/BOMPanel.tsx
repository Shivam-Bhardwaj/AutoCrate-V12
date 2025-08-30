'use client'

import { useState, useEffect } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  ButtonGroup,
  Typography,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material'
import { Download, Print, Email, Calculate } from '@mui/icons-material'
// import { div, useMultipleLinks } from './div' // Temporarily disabled

interface BOMItem {
  category: string
  description: string
  quantity: number
  unit: string
  unit_cost?: number
  total_cost?: number
}

interface BOMPanelProps {
  results: any
}

export function BOMPanel({ results }: BOMPanelProps) {
  const [bomData, setBomData] = useState<BOMItem[]>([])
  const [totalCost, setTotalCost] = useState(0)
  const [loading, setLoading] = useState(false)
  
  // Link status management temporarily disabled

  useEffect(() => {
    if (results) {
      generateBOM()
    }
  }, [results])

  const generateBOM = async () => {
    setLoading(true)
    try {
      // Calculate BOM from results
      const materials = results.materials_summary
      const bomItems: BOMItem[] = [
        {
          category: 'Panels',
          description: '3/4" CDX Plywood (4x8 sheets)',
          quantity: materials.plywood_sheets || 4,
          unit: 'sheets',
          unit_cost: 45.00,
          total_cost: (materials.plywood_sheets || 4) * 45.00
        },
        {
          category: 'Lumber',
          description: '2x4 Lumber (8ft pieces)',
          quantity: Math.ceil((materials.lumber_length_ft || 100) / 8),
          unit: 'pieces',
          unit_cost: 8.50,
          total_cost: Math.ceil((materials.lumber_length_ft || 100) / 8) * 8.50
        },
        {
          category: 'Hardware',
          description: 'Wood Screws #8 x 2.5"',
          quantity: 250,
          unit: 'pieces',
          unit_cost: 0.12,
          total_cost: 30.00
        },
        {
          category: 'Hardware',
          description: 'Wood Glue',
          quantity: 1,
          unit: 'bottle',
          unit_cost: 8.00,
          total_cost: 8.00
        },
        {
          category: 'Finishing',
          description: 'Sandpaper (assorted grits)',
          quantity: 1,
          unit: 'pack',
          unit_cost: 12.00,
          total_cost: 12.00
        }
      ]
      
      setBomData(bomItems)
      setTotalCost(bomItems.reduce((sum, item) => sum + (item.total_cost || 0), 0))
    } catch (error) {
      console.error('Failed to generate BOM:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: string) => {
    try {
      if (format === 'csv') {
        // Generate CSV data
        let csvContent = 'Category,Description,Quantity,Unit,Unit Cost,Total Cost\n'
        
        bomData.forEach(item => {
          csvContent += `"${item.category}","${item.description}",${item.quantity},"${item.unit}",${item.unit_cost || 0},${item.total_cost || 0}\n`
        })
        
        // Add summary rows
        const labor = calculateLabor()
        const subtotal = totalCost + labor
        const overhead = subtotal * 0.15
        const margin = subtotal * 1.15 * 0.25
        const recommendedPrice = calculateMarkup(subtotal)
        
        csvContent += '\n'
        csvContent += 'Summary,,,,\n'
        csvContent += `Materials Cost,,,,,${totalCost.toFixed(2)}\n`
        csvContent += `Labor (4 hours @ $35/hr),,,,,${labor.toFixed(2)}\n`
        csvContent += `Subtotal,,,,,${subtotal.toFixed(2)}\n`
        csvContent += `Overhead (15%),,,,,${overhead.toFixed(2)}\n`
        csvContent += `Margin (25%),,,,,${margin.toFixed(2)}\n`
        csvContent += `Recommended Price,,,,,${recommendedPrice.toFixed(2)}\n`
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `BOM_${new Date().toISOString().slice(0,10)}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
      } else if (format === 'excel') {
        // Generate Excel-compatible CSV (can be opened in Excel)
        let excelContent = 'sep=,\n' // Excel separator hint
        excelContent += 'Bill of Materials\n'
        excelContent += `Generated: ${new Date().toLocaleString()}\n`
        excelContent += `Project ID: ${results.request_id?.substring(0, 8) || 'N/A'}\n\n`
        excelContent += 'Category,Description,Quantity,Unit,Unit Cost,Total Cost\n'
        
        bomData.forEach(item => {
          excelContent += `"${item.category}","${item.description}",${item.quantity},"${item.unit}",`
          excelContent += `${item.unit_cost ? '$' + item.unit_cost.toFixed(2) : '-'},`
          excelContent += `${item.total_cost ? '$' + item.total_cost.toFixed(2) : '-'}\n`
        })
        
        // Add summary section
        const labor = calculateLabor()
        const subtotal = totalCost + labor
        const overhead = subtotal * 0.15
        const margin = subtotal * 1.15 * 0.25
        const recommendedPrice = calculateMarkup(subtotal)
        
        excelContent += '\n'
        excelContent += 'Cost Summary\n'
        excelContent += `Materials Cost,,,,,=$${totalCost.toFixed(2)}\n`
        excelContent += `Labor (4 hours @ $35/hr),,,,,=$${labor.toFixed(2)}\n`
        excelContent += `Subtotal,,,,,=$${subtotal.toFixed(2)}\n`
        excelContent += `Overhead (15%),,,,,=$${overhead.toFixed(2)}\n`
        excelContent += `Margin (25%),,,,,=$${margin.toFixed(2)}\n`
        excelContent += `Recommended Price,,,,,=$${recommendedPrice.toFixed(2)}\n`
        
        excelContent += '\n'
        excelContent += 'Material Optimization Suggestions\n'
        excelContent += '- Consider using cutoffs from Sheet 1 for smaller cleats\n'
        excelContent += '- Bulk purchase of screws can reduce cost by 15%\n'
        excelContent += '- Alternative: 1/2" plywood for internal cleats (save ~$20)\n'
        excelContent += '- Group cutting patterns to minimize waste (est. 18% reduction)\n'
        
        const blob = new Blob([excelContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `BOM_Excel_${new Date().toISOString().slice(0,10)}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
      } else if (format === 'print') {
        window.print()
      }
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  const calculateMarkup = (cost: number, margin: number = 0.25) => {
    return cost * (1 + margin)
  }

  const calculateLabor = (hours: number = 4, rate: number = 35) => {
    return hours * rate
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <Typography variant="h6">Bill of Materials</Typography>
        <ButtonGroup size="small">
          <Button 
            onClick={() => handleExport('excel')}
            title="Export to Excel"
          >
            <Download /> Excel
          </Button>
          <Button 
            onClick={() => handleExport('csv')}
            title="Export to CSV"
          >
            <Download /> CSV
          </Button>
          <Button 
            onClick={() => handleExport('print')}
            title="Print BOM"
          >
            <Print /> Print
          </Button>
        </ButtonGroup>
      </div>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell align="center">Unit</TableCell>
              <TableCell align="right">Unit Cost</TableCell>
              <TableCell align="right">Total Cost</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bomData.map((item, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Chip
                    label={item.category}
                    size="small"
                    color={
                      item.category === 'Panels' ? 'primary' :
                      item.category === 'Lumber' ? 'secondary' :
                      'default'
                    }
                  />
                </TableCell>
                <TableCell>{item.description}</TableCell>
                <TableCell align="right">{item.quantity}</TableCell>
                <TableCell align="center">{item.unit}</TableCell>
                <TableCell align="right">
                  ${item.unit_cost?.toFixed(2) || '-'}
                </TableCell>
                <TableCell align="right">
                  <strong>${item.total_cost?.toFixed(2) || '-'}</strong>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Paper className="p-4">
        <Typography variant="h6" className="mb-3">Cost Summary</Typography>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Materials Cost:</span>
            <strong>${totalCost.toFixed(2)}</strong>
          </div>
          <div className="flex justify-between">
            <span>Labor (4 hours @ $35/hr):</span>
            <strong>${calculateLabor().toFixed(2)}</strong>
          </div>
          <div className="flex justify-between">
            <span>Subtotal:</span>
            <strong>${(totalCost + calculateLabor()).toFixed(2)}</strong>
          </div>
          <div className="flex justify-between text-gray-600">
            <span>Overhead (15%):</span>
            <span>${((totalCost + calculateLabor()) * 0.15).toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-gray-600">
            <span>Margin (25%):</span>
            <span>${((totalCost + calculateLabor()) * 1.15 * 0.25).toFixed(2)}</span>
          </div>
          <hr className="my-2" />
          <div className="flex justify-between text-lg font-bold">
            <span>Recommended Price:</span>
            <span className="text-green-600">
              ${calculateMarkup(totalCost + calculateLabor()).toFixed(2)}
            </span>
          </div>
        </div>
      </Paper>

      <Paper className="p-4 bg-blue-50 dark:bg-blue-900">
        <Typography variant="subtitle2" className="mb-2">
          Material Optimization Suggestions:
        </Typography>
        <ul className="list-disc list-inside text-sm space-y-1">
          <li>Consider using cutoffs from Sheet 1 for smaller cleats</li>
          <li>Bulk purchase of screws can reduce cost by 15%</li>
          <li>Alternative: 1/2" plywood for internal cleats (save ~$20)</li>
          <li>Group cutting patterns to minimize waste (est. 18% reduction)</li>
        </ul>
      </Paper>

      <div className="flex justify-between items-center text-sm text-gray-600">
        <span>Generated: {new Date().toLocaleString()}</span>
        <span>Project ID: {results.request_id?.substring(0, 8)}</span>
      </div>
    </div>
  )
}