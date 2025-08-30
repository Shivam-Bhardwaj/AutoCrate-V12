'use client';

import { useState, useEffect } from 'react'
import { Calculator } from '@/components/Calculator'
import { ResultsPanel } from '@/components/ResultsPanel'
import { BOMPanel } from '@/components/BOMPanel'
import { Documentation } from '@/components/Documentation'
import LogViewer from '@/components/LogViewer'
// import ProfessionalCrateViewer from '@/components/ProfessionalCrateViewer-fixed'
// import SimpleCrateViewer from '@/components/SimpleCrateViewer'
import Basic3DViewer from '@/components/Basic3DViewer'
import VersionInfo from '@/components/VersionInfo'
import { 
  IconButton, 
  Tooltip, 
  Tabs, 
  Tab,
  Paper,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  AppBar,
  Toolbar,
  Dialog,
  Button,
  Divider,
  Stack
} from '@mui/material'
import { 
  Help, 
  GitHub, 
  LightMode, 
  DarkMode, 
  Inventory2, 
  BugReport,
  Calculate,
  ViewInAr,
  Description,
  Engineering,
  CheckCircle,
  Warning,
  AttachMoney,
  Build
} from '@mui/icons-material'
import { useCalculationStore } from '@/store/calculationStore'
import { useTheme } from '@/components/ThemeProvider'
import { useWebLogger } from '@/hooks/useWebLogger'

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && children}
    </div>
  );
}

export default function OptimizedHomePage() {
  const { mode, toggleTheme } = useTheme()
  const darkMode = mode === 'dark'
  const [docOpen, setDocOpen] = useState(false);
  const [logViewerOpen, setLogViewerOpen] = useState(false)
  const [bottomTabIndex, setBottomTabIndex] = useState(0)
  const results = useCalculationStore((state) => state.calculationResult)
  const { logUserInteraction, logInfo } = useWebLogger('HomePage')

  // Initialize logger on mount
  useEffect(() => {
    logInfo('Application started', { darkMode, hasResults: !!results })
  }, [])


  // Compact results display component
  const CompactResults = () => {
    if (!results) return null;
    
    const { panels, materials_summary, compliance, crate_dimensions } = results;
    const materialCost = materials_summary?.plywood_sheets ? materials_summary.plywood_sheets * 45 : 0;
    const laborCost = Math.round(materialCost * 0.4);
    const totalCost = materialCost + laborCost;

    return (
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Key Metrics
              </Typography>
              <Stack spacing={1.5}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AttachMoney fontSize="small" color="primary" />
                    <Typography variant="body2">Cost</Typography>
                  </Box>
                  <Typography variant="body2" fontWeight={600}>${totalCost}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Engineering fontSize="small" color="primary" />
                    <Typography variant="body2">Weight</Typography>
                  </Box>
                  <Typography variant="body2" fontWeight={600}>
                    {materials_summary?.estimated_weight_lbs || 0} lbs
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Build fontSize="small" color="primary" />
                    <Typography variant="body2">Sheets</Typography>
                  </Box>
                  <Typography variant="body2" fontWeight={600}>
                    {materials_summary?.plywood_sheets || 0}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Dimensions */}
        <Grid item xs={12} md={3}>
          <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                External Dimensions
              </Typography>
              <Stack spacing={1.5}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Length</Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {typeof crate_dimensions?.external_length === 'number' 
                      ? crate_dimensions.external_length.toFixed(2) 
                      : '0.00'}"
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Width</Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {typeof crate_dimensions?.external_width === 'number' 
                      ? crate_dimensions.external_width.toFixed(2) 
                      : '0.00'}"
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Height</Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {typeof crate_dimensions?.external_height === 'number' 
                      ? crate_dimensions.external_height.toFixed(2) 
                      : '0.00'}"
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Volume</Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {typeof crate_dimensions?.external_length === 'number' &&
                     typeof crate_dimensions?.external_width === 'number' &&
                     typeof crate_dimensions?.external_height === 'number'
                      ? ((crate_dimensions.external_length * 
                          crate_dimensions.external_width * 
                          crate_dimensions.external_height) / 1728).toFixed(1)
                      : '0.0'} ft³
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance */}
        <Grid item xs={12} md={3}>
          <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Compliance Status
              </Typography>
              <Stack spacing={1.5}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {compliance?.astm_d6251 ? (
                    <>
                      <CheckCircle fontSize="small" color="success" />
                      <Typography variant="body2">ASTM D6251-17</Typography>
                    </>
                  ) : (
                    <>
                      <Warning fontSize="small" color="warning" />
                      <Typography variant="body2">Review Required</Typography>
                    </>
                  )}
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Safety Factor</Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {compliance?.safety_factor || 1.5}x
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Max Load</Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {compliance?.max_load || 0} lbs
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Standards</Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {compliance?.standards_met?.length || 0} met
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Panel Status */}
        <Grid item xs={12} md={3}>
          <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Panel Status
              </Typography>
              <Stack spacing={1}>
                {Object.entries(panels || {}).slice(0, 5).map(([name, panel]: [string, any]) => (
                  <Box key={name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                      {name}
                    </Typography>
                    {panel.error ? (
                      <Warning fontSize="small" color="error" />
                    ) : (
                      <CheckCircle fontSize="small" color="success" />
                    )}
                  </Box>
                ))}
                <Divider />
                <Typography variant="caption" color="textSecondary">
                  All panels optimized
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      overflow: 'hidden',
      bgcolor: 'background.default' 
    }}>
      {/* Compact Header */}
      <AppBar 
        position="fixed" 
        elevation={1}
        sx={{ 
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          height: 56
        }}
      >
        <Toolbar sx={{ minHeight: 56, height: 56 }}>
          <Inventory2 sx={{ mr: 2, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ flexGrow: 0, mr: 3, color: 'text.primary' }}>
            AutoCrate
          </Typography>
          <Typography variant="body2" sx={{ flexGrow: 1, color: 'text.secondary' }}>
            Professional NX Expression Generator v12.0.2
          </Typography>
          
          <Stack direction="row" spacing={1}>
            <Chip 
              label="ASTM D6251-17" 
              size="small" 
              color="primary" 
              variant="outlined"
            />
            <Tooltip title="Toggle Theme">
              <IconButton onClick={toggleTheme} size="small">
                {darkMode ? <LightMode /> : <DarkMode />}
              </IconButton>
            </Tooltip>
            <Tooltip title="Debug Logs">
              <IconButton onClick={() => setLogViewerOpen(true)} size="small">
                <BugReport />
              </IconButton>
            </Tooltip>
            <Tooltip title="Documentation">
              <IconButton onClick={() => setDocOpen(true)} size="small">
                <Help />
              </IconButton>
            </Tooltip>
            <Tooltip title="GitHub">
              <IconButton 
                href="https://github.com/your-repo/autocrate" 
                target="_blank" 
                size="small"
              >
                <GitHub />
              </IconButton>
            </Tooltip>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Main Content - No Scrolling */}
      <Box sx={{ 
        mt: '56px',
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        overflow: 'hidden',
        height: 'calc(100vh - 56px)'
      }}>
        <Grid container sx={{ height: '100%', overflow: 'hidden' }}>
          {/* Left Column - Calculator */}
          <Grid item xs={12} md={3} sx={{ 
            height: '100%',
            borderRight: 1,
            borderColor: 'divider',
            overflow: 'auto',
            '&::-webkit-scrollbar': { display: 'none' },
            msOverflowStyle: 'none',
            scrollbarWidth: 'none'
          }}>
            <Calculator />
          </Grid>

          {/* Middle Column - 3D Viewer */}
          <Grid item xs={12} md={6} sx={{ 
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}>
            {/* 3D Viewer - Fixed Height */}
            <Box sx={{ 
              height: '60%',
              minHeight: 400,
              position: 'relative',
              borderBottom: 1,
              borderColor: 'divider'
            }}>
              <Basic3DViewer crateData={results} />
            </Box>

            {/* Bottom Section - Tabs with Results */}
            <Box sx={{ 
              height: '40%',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}>
              <Paper sx={{ 
                borderBottom: 1, 
                borderColor: 'divider',
                bgcolor: 'background.paper'
              }}>
                <Tabs 
                  value={bottomTabIndex} 
                  onChange={(e, newValue) => setBottomTabIndex(newValue)}
                  variant="fullWidth"
                  sx={{ minHeight: 40 }}
                >
                  <Tab 
                    label="Results" 
                    icon={<ViewInAr />} 
                    iconPosition="start"
                    sx={{ minHeight: 40 }}
                  />
                  <Tab 
                    label="BOM" 
                    icon={<Inventory2 />} 
                    iconPosition="start"
                    sx={{ minHeight: 40 }}
                  />
                  <Tab 
                    label="Docs" 
                    icon={<Description />} 
                    iconPosition="start"
                    sx={{ minHeight: 40 }}
                  />
                </Tabs>
              </Paper>
              
              <Box sx={{ 
                flex: 1, 
                overflow: 'auto',
                p: 2,
                '&::-webkit-scrollbar': { display: 'none' },
                msOverflowStyle: 'none',
                scrollbarWidth: 'none'
              }}>
                <TabPanel value={bottomTabIndex} index={0}>
                  <CompactResults />
                </TabPanel>
                <TabPanel value={bottomTabIndex} index={1}>
                  <BOMPanel results={results} />
                </TabPanel>
                <TabPanel value={bottomTabIndex} index={2}>
                  <Typography variant="body2" sx={{ p: 2 }}>
                    ASTM D6251-17 Compliant Wooden Crate Design System
                  </Typography>
                </TabPanel>
              </Box>
            </Box>
          </Grid>

          {/* Right Column - Quick Actions & Stats */}
          <Grid item xs={12} md={3} sx={{ 
            height: '100%',
            borderLeft: 1,
            borderColor: 'divider',
            overflow: 'auto',
            '&::-webkit-scrollbar': { display: 'none' },
            msOverflowStyle: 'none',
            scrollbarWidth: 'none'
          }}>
            <ResultsPanel results={results} />
          </Grid>
        </Grid>
      </Box>

      {/* Dialogs */}
      <Documentation 
        open={docOpen} 
        onClose={() => setDocOpen(false)}
      />
      
      <Dialog 
        open={logViewerOpen} 
        onClose={() => setLogViewerOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <LogViewer />
      </Dialog>
      
      {/* Version Info Component */}
      <VersionInfo />
    </Box>
  );
}