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
  // Start with light mode during SSR, will update on client
  const [mode, setMode] = useState<'light' | 'dark'>('light')
  const [mounted, setMounted] = useState(false)

  // Initialize theme properly on client side
  useEffect(() => {
    // Get saved preference or system preference
    const savedMode = localStorage.getItem('themeMode')
    if (savedMode === 'dark' || savedMode === 'light') {
      setMode(savedMode as 'light' | 'dark')
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setMode(prefersDark ? 'dark' : 'light')
    }
    setMounted(true)
    
    // Force a re-render to apply styles properly
    setTimeout(() => {
      document.documentElement.setAttribute('data-theme', mode)
    }, 0)
  }, [])

  // Update localStorage and document attribute when mode changes
  useEffect(() => {
    if (mounted) {
      localStorage.setItem('themeMode', mode)
      document.documentElement.setAttribute('data-theme', mode)
      
      // Force Material-UI to update colors
      const event = new Event('theme-change')
      window.dispatchEvent(event)
    }
  }, [mode, mounted])

  const toggleTheme = () => {
    setMode((prevMode) => {
      const newMode = prevMode === 'light' ? 'dark' : 'light'
      // Immediately update document attribute for faster response
      document.documentElement.setAttribute('data-theme', newMode)
      return newMode
    })
  }

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                // Light Mode Palette
                primary: { 
                  main: '#0D47A1',
                  light: '#5472D3',
                  dark: '#002171',
                  contrastText: '#fff'
                },
                secondary: { 
                  main: '#FF8F00',
                  light: '#FFC046',
                  dark: '#C56000',
                  contrastText: '#000'
                },
                background: {
                  default: '#F4F6F8',
                  paper: '#FFFFFF',
                },
                text: {
                  primary: 'rgba(0, 0, 0, 0.87)',
                  secondary: 'rgba(0, 0, 0, 0.6)',
                  disabled: 'rgba(0, 0, 0, 0.38)'
                },
                divider: 'rgba(0, 0, 0, 0.12)',
                action: {
                  active: 'rgba(0, 0, 0, 0.54)',
                  hover: 'rgba(0, 0, 0, 0.04)',
                  selected: 'rgba(0, 0, 0, 0.08)',
                  disabled: 'rgba(0, 0, 0, 0.26)',
                  disabledBackground: 'rgba(0, 0, 0, 0.12)'
                }
              }
            : {
                // Dark Mode Palette
                primary: { 
                  main: '#42A5F5',
                  light: '#80D8FF',
                  dark: '#0077C2',
                  contrastText: '#000'
                },
                secondary: { 
                  main: '#FFB74D',
                  light: '#FFE97D',
                  dark: '#C88719',
                  contrastText: '#000'
                },
                background: {
                  default: '#161C24',
                  paper: '#212B36',
                },
                text: {
                  primary: 'rgba(255, 255, 255, 0.87)',
                  secondary: 'rgba(255, 255, 255, 0.6)',
                  disabled: 'rgba(255, 255, 255, 0.38)'
                },
                divider: 'rgba(255, 255, 255, 0.12)',
                action: {
                  active: 'rgba(255, 255, 255, 0.54)',
                  hover: 'rgba(255, 255, 255, 0.04)',
                  selected: 'rgba(255, 255, 255, 0.08)',
                  disabled: 'rgba(255, 255, 255, 0.26)',
                  disabledBackground: 'rgba(255, 255, 255, 0.12)'
                }
              }),
          error: { main: '#D32F2F' },
          warning: { main: '#FFA000' },
          success: { main: '#388E3C' },
          info: { main: '#1976D2' }
        },
        typography: {
          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          h1: {
            fontWeight: 600,
          },
          h2: {
            fontWeight: 600,
          },
          h3: {
            fontWeight: 600,
          },
          h4: {
            fontWeight: 600,
          },
          h5: {
            fontWeight: 600,
          },
          h6: {
            fontWeight: 600,
          },
          subtitle1: {
            fontWeight: 500,
          },
          subtitle2: {
            fontWeight: 500,
          },
          body1: {
            fontSize: '1rem',
            fontWeight: 400,
            lineHeight: 1.5,
          },
          body2: {
            fontSize: '0.875rem',
            fontWeight: 400,
            lineHeight: 1.43,
          },
          button: {
            fontWeight: 500,
            textTransform: 'none',
          },
          caption: {
            fontSize: '0.75rem',
            fontWeight: 400,
            lineHeight: 1.66,
          },
        },
        components: {
          MuiCssBaseline: {
            styleOverrides: {
              body: {
                transition: 'background-color 0.3s ease, color 0.3s ease',
              },
            },
          },
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
                borderRadius: 8,
                padding: '8px 16px',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 12,
                boxShadow: mode === 'light' 
                  ? '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)'
                  : '0 1px 3px rgba(0, 0, 0, 0.4), 0 1px 2px rgba(0, 0, 0, 0.48)',
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
              },
            },
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
              },
            },
          },
          MuiToolbar: {
            styleOverrides: {
              root: {
                '@media (min-width: 600px)': {
                  minHeight: 56,
                },
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                '& .MuiOutlinedInput-root': {
                  borderRadius: 8,
                },
              },
            },
          },
          MuiSelect: {
            styleOverrides: {
              root: {
                borderRadius: 8,
              },
            },
          },
        },
      }),
    [mode]
  )

  // Always provide the context, even during initial mount
  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <MUIThemeProvider theme={theme}>
        <CssBaseline />
        {/* Hide content until client-side mounted to avoid hydration mismatch */}
        {!mounted ? (
          <div style={{ visibility: 'hidden' }}>{children}</div>
        ) : (
          children
        )}
      </MUIThemeProvider>
    </ThemeContext.Provider>
  )
}