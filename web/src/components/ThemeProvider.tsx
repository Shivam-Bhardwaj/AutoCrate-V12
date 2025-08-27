'use client'

import { createTheme, ThemeProvider as MUIThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { ReactNode, useMemo, useState, useEffect, createContext, useContext } from 'react'

interface ThemeContextType {
  mode: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  // Initialize with system preference or saved preference
  const [mode, setMode] = useState<'light' | 'dark'>(() => {
    // Try to get from localStorage during SSR-safe initialization
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('themeMode')
      if (savedMode === 'dark' || savedMode === 'light') {
        return savedMode as 'light' | 'dark'
      }
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      return prefersDark ? 'dark' : 'light'
    }
    return 'light'
  })
  const [mounted, setMounted] = useState(false)

  // Mark as mounted after hydration
  useEffect(() => {
    setMounted(true)
  }, [])

  // Save theme preference to localStorage when it changes
  useEffect(() => {
    if (mounted) {
      localStorage.setItem('themeMode', mode)
    }
  }, [mode, mounted])

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'))
  }

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                // Light Mode Palette
                primary: { main: '#0D47A1' }, // Deep Blue
                secondary: { main: '#FF8F00' }, // Amber
                background: {
                  default: '#F4F6F8',
                  paper: '#FFFFFF',
                },
                text: {
                  primary: '#212B36',
                  secondary: '#637381',
                },
              }
            : {
                // Dark Mode Palette
                primary: { main: '#42A5F5' }, // Lighter Blue
                secondary: { main: '#FFB74D' }, // Lighter Amber
                background: {
                  default: '#161C24',
                  paper: '#212B36',
                },
                text: {
                  primary: '#FFFFFF',
                  secondary: '#9DA8B7',
                },
              }),
          error: { main: '#D32F2F' },
          warning: { main: '#FFA000' },
          success: { main: '#388E3C' },
        },
        typography: {
          fontFamily: 'Inter, system-ui, sans-serif',
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 12,
              },
            },
          },
        },
      }),
    [mode]
  )

  // Provide theme immediately with proper defaults
  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <MUIThemeProvider theme={theme}>
        <CssBaseline />
        {/* Apply theme class to body for CSS variables */}
        {mounted && (
          <style jsx global>{`
            body {
              transition: background-color 0.3s ease, color 0.3s ease;
            }
          `}</style>
        )}
        {children}
      </MUIThemeProvider>
    </ThemeContext.Provider>
  )
}