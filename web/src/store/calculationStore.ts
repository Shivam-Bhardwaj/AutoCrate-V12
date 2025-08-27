import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { CrateCalculationResult } from '@/lib/autocrate-calculations'

// Use the proper CrateCalculationResult interface
type CalculationResult = CrateCalculationResult

interface GeometryData {
  panels: Array<{
    name: string
    position: number[]
    size: number[]
    color: string
  }>
  cleats: Array<{
    position: number[]
    size: number[]
    rotation?: number[]
    color?: string
  }>
  dimensions: any
}

interface BOMData {
  items: Array<{
    category: string
    description: string
    quantity: number
    unit: string
    unit_cost?: number
    total_cost?: number
  }>
  total_cost: number
  project: string
  date: string
}

interface CalculationStore {
  // State
  calculationResult: CalculationResult | null
  geometry: GeometryData | null
  bomData: BOMData | null
  lastRequest: any | null
  isLoading: boolean
  error: string | null
  
  // Actions
  setCalculationResult: (result: CalculationResult) => void
  setGeometry: (geometry: GeometryData) => void
  setBOMData: (data: BOMData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearResults: () => void
}

export const useCalculationStore = create<CalculationStore>()(
  devtools(
    (set) => ({
      // Initial state
      calculationResult: null,
      geometry: null,
      bomData: null,
      lastRequest: null,
      isLoading: false,
      error: null,
      
      // Actions
      setCalculationResult: (result) => set({ calculationResult: result, error: null }),
      setGeometry: (geometry) => set({ geometry }),
      setBOMData: (data) => set({ bomData: data }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error, isLoading: false }),
      clearResults: () => set({
        calculationResult: null,
        geometry: null,
        bomData: null,
        error: null
      })
    }),
    {
      name: 'calculation-store'
    }
  )
)