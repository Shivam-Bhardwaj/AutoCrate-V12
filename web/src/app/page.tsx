'use client';

import { useState, useEffect } from 'react'
import { Calculator } from '@/components/Calculator'
import { ResultsPanel } from '@/components/ResultsPanel'
import { BOMPanel } from '@/components/BOMPanel'
import { Documentation } from '@/components/Documentation'
import LogViewer from '@/components/LogViewer'
import CrateVisualization from '@/components/CrateVisualization'
import ProfessionalCrateViewer from '@/components/ProfessionalCrateViewer'
import { Paper, Alert, IconButton, Tooltip, ToggleButton, ToggleButtonGroup } from '@mui/material'
import { Brightness4, Brightness7, Help, GitHub, LightMode, DarkMode, Inventory2, BugReport, ViewInAr, ViewModule } from '@mui/icons-material'
import { useCalculationStore } from '@/store/calculationStore'
import { createTheme, ThemeProvider, CssBaseline, Box, AppBar, Toolbar, Typography, Chip, Button, Dialog } from '@mui/material'
import { useWebLogger } from '@/hooks/useWebLogger'
import { logger } from '@/services/logger'

export default function HomePage() {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme')
      return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)
    }
    return false
  })
  const [docOpen, setDocOpen] = useState(false)
  const [logViewerOpen, setLogViewerOpen] = useState(false)
  const [viewMode, setViewMode] = useState<'basic' | 'professional'>('professional')
  const results = useCalculationStore((state) => state.calculationResult)
  const { logUserInteraction, logInfo } = useWebLogger('HomePage')

  // Initialize logger on mount
  useEffect(() => {
    // Logger automatically loads persisted logs in constructor
    logInfo('Application started', { darkMode, hasResults: !!results })
  }, [])

  // Log theme changes
  useEffect(() => {
    logUserInteraction('theme-changed', 'theme-toggle', { darkMode })
  }, [darkMode, logUserInteraction])

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: { main: '#1976D2' },
      secondary: { main: '#FF6B35' },
      background: {
        default: darkMode ? '#0A0E1A' : '#F5F7FA',
        paper: darkMode ? '#1A1F2E' : '#FFFFFF',
      },
      text: {
        primary: darkMode ? '#E1E4E8' : '#2C3E50',
        secondary: darkMode ? '#A0A8B3' : '#64748B',
      }
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h6: { fontWeight: 600 }
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: darkMode 
              ? '0 4px 6px rgba(0, 0, 0, 0.3)' 
              : '0 1px 3px rgba(0, 0, 0, 0.1)',
            backgroundColor: darkMode ? '#1A1F2E' : '#FFFFFF'
          }
        }
      },
      MuiAccordion: {
        styleOverrides: {
          root: {
            backgroundColor: darkMode ? '#1A1F2E' : '#FFFFFF',
            '&:before': {
              backgroundColor: darkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
            }
          }
        }
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: darkMode ? '#1A1F2E' : '#FFFFFF'
          }
        }
      }
    }
  })

  const toggleDarkMode = () => {
    const newMode = !darkMode
    setDarkMode(newMode)
    localStorage.setItem('theme', newMode ? 'dark' : 'light')
    logUserInteraction('clicked', 'theme-toggle', { newMode })
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '100vh', 
        bgcolor: 'background.default' 
      }}>
        {/* Header */}
        <AppBar 
          position="fixed" 
          elevation={1}
          sx={{ 
            height: { xs: 56, sm: 60 }, 
            bgcolor: 'background.paper',
            borderBottom: 1,
            borderColor: 'divider',
            color: 'text.primary'
          }}
        >
          <Toolbar sx={{ height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Inventory2 color="primary" sx={{ fontSize: { xs: 24, sm: 28 } }} />
              <Typography variant="h6" sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                AutoCrate V12
              </Typography>
              <Chip 
                label="PRO" 
                size="small" 
                color="primary" 
                sx={{ display: { xs: 'none', sm: 'flex' } }}
              />
            </Box>
            
            <Box sx={{ flexGrow: 1 }} />
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 0.5, sm: 1 } }}>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={(e, newMode) => {
                  if (newMode) {
                    setViewMode(newMode)
                    logUserInteraction('view-mode-changed', 'view-toggle', { newMode })
                  }
                }}
                size="small"
                sx={{ 
                  mr: 2,
                  display: { xs: 'none', md: 'flex' },
                  '& .MuiToggleButton-root': {
                    color: 'text.secondary',
                    '&.Mui-selected': {
                      color: 'primary.main'
                    }
                  }
                }}
              >
                <ToggleButton value="basic">
                  <Tooltip title="Basic View">
                    <ViewModule />
                  </Tooltip>
                </ToggleButton>
                <ToggleButton value="professional">
                  <Tooltip title="Professional 3D">
                    <ViewInAr />
                  </Tooltip>
                </ToggleButton>
              </ToggleButtonGroup>
              
              <Tooltip title={darkMode ? 'Light Mode' : 'Dark Mode'}>
                <IconButton onClick={toggleDarkMode} color="inherit" size="small">
                  {darkMode ? <LightMode /> : <DarkMode />}
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Debug Logs">
                <IconButton 
                  onClick={() => {
                    setLogViewerOpen(true)
                    logUserInteraction('clicked', 'log-viewer-button')
                  }}
                  color="inherit" 
                  size="small"
                >
                  <BugReport />
                </IconButton>
              </Tooltip>
              
              <Button 
                startIcon={<Help sx={{ display: { xs: 'none', sm: 'block' } }} />}
                onClick={() => {
                  setDocOpen(true)
                  logUserInteraction('clicked', 'docs-button')
                }}
                color="inherit"
                size="small"
                sx={{ minWidth: { xs: 40, sm: 'auto' } }}
              >
                <Typography sx={{ display: { xs: 'none', sm: 'block' } }}>Docs</Typography>
                <Help sx={{ display: { xs: 'block', sm: 'none' }, fontSize: 20 }} />
              </Button>
              
              <Tooltip title="View on GitHub">
                <IconButton 
                  href="https://github.com/yourusername/autocrate-v12" 
                  target="_blank"
                  color="inherit"
                  size="small"
                  sx={{ display: { xs: 'none', md: 'flex' } }}
                >
                  <GitHub />
                </IconButton>
              </Tooltip>
            </Box>
          </Toolbar>
        </AppBar>
        
        {/* Main Content */}
        <Box 
          component="main" 
          sx={{ 
            pt: { xs: '56px', sm: '60px' },
            flex: 1,
            display: 'flex',
            flexDirection: { xs: 'column', lg: 'row' },
            gap: 2,
            p: { xs: 1, sm: 2 },
            overflow: { xs: 'auto', lg: 'hidden' }
          }}
        >
          {/* Input Panel */}
          <Box sx={{ 
            width: { xs: '100%', lg: '30%' },
            minHeight: { xs: 'auto', lg: '100%' },
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Calculator />
          </Box>
          
          {/* 3D Viewer */}
          <Box sx={{ 
            width: { xs: '100%', md: '100%', lg: '40%' },
            height: { xs: 400, md: 500, lg: '100%' },
            display: { xs: 'block', sm: 'block' }
          }}>
            {viewMode === 'professional' ? (
              <ProfessionalCrateViewer crateData={results} />
            ) : (
              <CrateVisualization 
                crateData={results}
                width={800}
                height={600}
              />
            )}
          </Box>
          
          {/* Results Panel */}
          <Box sx={{ 
            width: { xs: '100%', lg: '30%' },
            minHeight: { xs: 'auto', lg: '100%' },
            display: 'flex',
            flexDirection: 'column'
          }}>
            {results ? (
              <>
                {/* Results Panel */}
                <Paper 
                  elevation={0} 
                  sx={{ 
                    transition: 'all 0.2s ease-in-out',
                    backgroundColor: 'background.paper'
                  }}
                >
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold">Calculation Results</h3>
                  </div>
                  <div className="p-4">
                    <ResultsPanel results={results} />
                  </div>
                </Paper>

                {/* BOM Panel */}
                <Paper 
                  elevation={0} 
                  sx={{ 
                    transition: 'all 0.2s ease-in-out',
                    backgroundColor: 'background.paper'
                  }}
                >
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold">Bill of Materials</h3>
                  </div>
                  <div className="p-4">
                    <BOMPanel results={results} />
                  </div>
                </Paper>
              </>
            ) : (
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 12, 
                  textAlign: 'center', 
                  transition: 'all 0.2s ease-in-out',
                  backgroundColor: 'background.paper'
                }}
              >
                <div className={`text-8xl mb-6 text-gray-300`}>
                  📦
                </div>
                <h3 className="text-2xl font-medium mb-4">Ready to Design</h3>
                <p className="text-lg text-gray-600">
                  Enter your product specifications to begin professional crate design.
                </p>
              </Paper>
            )}
          </Box>
        </Box>
        
        {/* Footer - Only on desktop */}
        <Box 
          component="footer"
          sx={{ 
            display: { xs: 'none', lg: 'flex' },
            height: 40,
            px: 3,
            borderTop: 1,
            borderColor: 'divider',
            alignItems: 'center',
            justifyContent: 'space-between',
            bgcolor: 'background.paper'
          }}
        >
          <Typography variant="caption" color="text.secondary">
            &copy; 2024 AutoCrate V12 • ASTM D6251-17 Compliant
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Version 12.0.0
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Engineering Grade
            </Typography>
          </Box>
        </Box>
        
        {/* Documentation Modal */}
        <Documentation 
          open={docOpen} 
          onClose={() => setDocOpen(false)} 
        />
        
        {/* Log Viewer Dialog */}
        <Dialog
          open={logViewerOpen}
          onClose={() => setLogViewerOpen(false)}
          maxWidth="xl"
          fullWidth
          PaperProps={{
            sx: { height: '90vh' }
          }}
        >
          <LogViewer />
        </Dialog>
      </Box>
    </ThemeProvider>
  )
}