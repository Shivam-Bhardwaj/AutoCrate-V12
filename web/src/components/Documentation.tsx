'use client'

import { useState } from 'react'
import { 
  Dialog, 
  DialogContent, 
  DialogTitle, 
  IconButton, 
  Typography, 
  Tab, 
  Tabs,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material'
import { 
  Close, 
  Info, 
  Build, 
  Engineering, 
  School, 
  Security, 
  Speed,
  CheckCircle,
  Warning,
  BugReport,
  Psychology
} from '@mui/icons-material'

interface DocumentationProps {
  open: boolean
  onClose: () => void
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`doc-tabpanel-${index}`}
      aria-labelledby={`doc-tab-${index}`}
      {...other}
    >
      {value === index && <div style={{ padding: '16px' }}>{children}</div>}
    </div>
  )
}

export function Documentation({ open, onClose }: DocumentationProps) {
  const [tabValue, setTabValue] = useState(0)

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { height: '80vh' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="div" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <School color="primary" />
          AutoCrate V12 Documentation
        </Typography>
        <IconButton onClick={onClose} size="small">
          <Close />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          variant="scrollable" 
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<Info />} label="Overview" />
          <Tab icon={<Build />} label="Features" />
          <Tab icon={<Engineering />} label="Technical Specs" />
          <Tab icon={<Security />} label="Compliance" />
          <Tab icon={<Psychology />} label="AI Development" />
        </Tabs>
        
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <TabPanel value={tabValue} index={0}>
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  Professional CAD Automation Tool
                </Typography>
                <Typography variant="body1" paragraph>
                  AutoCrate is a sophisticated web application that automates the design and manufacturing 
                  data generation for custom shipping crates. Built for professional manufacturing environments, 
                  it integrates with Siemens NX CAD software to produce parametric 3D models and technical drawings.
                </Typography>
                
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                  <Chip icon={<CheckCircle />} label="ASTM D6251-17 Compliant" color="success" size="small" />
                  <Chip icon={<Security />} label="Professional Engineering" color="primary" size="small" />
                  <Chip icon={<Psychology />} label="AI-Assisted Development" color="secondary" size="small" />
                </div>

                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Key Capabilities
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><Build /></ListItemIcon>
                    <ListItemText primary="Parametric Crate Design" secondary="Fully customizable dimensions and materials" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Engineering /></ListItemIcon>
                    <ListItemText primary="CAD Integration" secondary="Direct export to Siemens NX with expression files" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Speed /></ListItemIcon>
                    <ListItemText primary="Real-time Calculation" secondary="Instant design validation and optimization" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning color="warning" />
                  Important Notice
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This software is provided for educational and demonstration purposes. ASTM compliance 
                  calculations reference industry standards - users must obtain official standards for 
                  commercial use. Any commercial application requires validation by licensed professional engineers.
                </Typography>
              </CardContent>
            </Card>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Typography variant="h6" gutterBottom>Core Features</Typography>
            
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Intelligent Design System
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="Smart Material Optimization" secondary="Minimizes plywood waste through intelligent layout algorithms" /></ListItem>
                  <ListItem><ListItemText primary="Structural Engineering" secondary="Automated cleat placement based on ASTM-derived requirements" /></ListItem>
                  <ListItem><ListItemText primary="Load Distribution" secondary="Proper weight distribution and safety factor calculations" /></ListItem>
                </List>
              </CardContent>
            </Card>

            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Professional Output
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="NX Expression Files (.exp)" secondary="Ready-to-import parametric models for Siemens NX" /></ListItem>
                  <ListItem><ListItemText primary="Bill of Materials" secondary="Complete material lists with costs and optimization suggestions" /></ListItem>
                  <ListItem><ListItemText primary="3D Visualization" secondary="Real-time 3D preview with interactive controls" /></ListItem>
                </List>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Advanced Analytics
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="Material Efficiency Analysis" secondary="Waste percentage and optimization recommendations" /></ListItem>
                  <ListItem><ListItemText primary="Cost Estimation" secondary="Real-time pricing with labor and overhead calculations" /></ListItem>
                  <ListItem><ListItemText primary="Compliance Verification" secondary="Automatic ASTM standard compliance checking" /></ListItem>
                </List>
              </CardContent>
            </Card>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>Technical Specifications</Typography>
            
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Design Constraints
                </Typography>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div>
                    <Typography variant="subtitle2" color="text.secondary">Dimensions</Typography>
                    <Typography>Length: 12" - 130"</Typography>
                    <Typography>Width: 12" - 130"</Typography>
                    <Typography>Height: 12" - 130"</Typography>
                  </div>
                  <div>
                    <Typography variant="subtitle2" color="text.secondary">Load Capacity</Typography>
                    <Typography>Weight: 1 - 20,000 lbs</Typography>
                    <Typography>Safety Factor: 1.5x</Typography>
                  </div>
                  <div>
                    <Typography variant="subtitle2" color="text.secondary">Materials</Typography>
                    <Typography>Plywood: 1/2", 5/8", 3/4", 1"</Typography>
                    <Typography>Lumber: 2x4, 2x6 standard</Typography>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Calculation Engine
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="Load Distribution Analysis" secondary="Advanced algorithms for proper weight distribution across frame members" /></ListItem>
                  <ListItem><ListItemText primary="Material Properties" secondary="Database of wood species properties and engineering characteristics" /></ListItem>
                  <ListItem><ListItemText primary="Optimization Algorithms" secondary="Genetic algorithms for material layout optimization" /></ListItem>
                  <ListItem><ListItemText primary="Finite Element Concepts" secondary="Simplified FEA principles for structural validation" /></ListItem>
                </List>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  CAD Integration
                </Typography>
                <Typography variant="body2" paragraph>
                  AutoCrate generates comprehensive NX expression files containing:
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="767 parametric expressions" secondary="Complete model definition with all components" /></ListItem>
                  <ListItem><ListItemText primary="Component hierarchy" secondary="Organized structure for panels, cleats, and hardware" /></ListItem>
                  <ListItem><ListItemText primary="Material assignments" secondary="Automatic material property assignments" /></ListItem>
                  <ListItem><ListItemText primary="Suppression logic" secondary="Smart component visibility based on design requirements" /></ListItem>
                </List>
              </CardContent>
            </Card>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Typography variant="h6" gutterBottom>Standards & Compliance</Typography>
            
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="success.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle />
                  ASTM D6251-17 Compliance
                </Typography>
                <Typography variant="body2" paragraph>
                  All calculations reference ASTM D6251-17 "Standard Specification for Nailed Wood Shipping Container". 
                  This ensures structural integrity and shipping reliability.
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="Load Testing Requirements" secondary="Meets compression, vibration, and impact testing standards" /></ListItem>
                  <ListItem><ListItemText primary="Material Specifications" secondary="Wood grade requirements and moisture content limits" /></ListItem>
                  <ListItem><ListItemText primary="Construction Standards" secondary="Fastener specifications and joint requirements" /></ListItem>
                </List>
              </CardContent>
            </Card>

            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Safety Factors
                </Typography>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
                  <div>
                    <Typography variant="subtitle2" color="text.secondary">Structural Safety</Typography>
                    <Typography>1.5x minimum safety factor</Typography>
                    <Typography>Dynamic load considerations</Typography>
                  </div>
                  <div>
                    <Typography variant="subtitle2" color="text.secondary">Material Safety</Typography>
                    <Typography>Conservative wood strength values</Typography>
                    <Typography>Environmental factor allowances</Typography>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" color="warning.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning />
                  Professional Engineering Required
                </Typography>
                <Typography variant="body2">
                  While AutoCrate provides ASTM-compliant calculations, any commercial use requires validation 
                  by licensed professional engineers. The software serves as a design tool and starting point 
                  for professional engineering analysis.
                </Typography>
              </CardContent>
            </Card>
          </TabPanel>

          <TabPanel value={tabValue} index={4}>
            <Typography variant="h6" gutterBottom>AI-Assisted Development</Typography>
            
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="secondary.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Psychology />
                  Human-AI Collaboration
                </Typography>
                <Typography variant="body2" paragraph>
                  AutoCrate demonstrates the power of AI-assisted software development, where complex 
                  engineering calculations, comprehensive testing, and professional documentation were 
                  created through human-AI collaboration.
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                  AI Contributions:
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="Architecture Design" secondary="System structure and component organization" /></ListItem>
                  <ListItem><ListItemText primary="Engineering Calculations" secondary="ASTM-compliant structural analysis algorithms" /></ListItem>
                  <ListItem><ListItemText primary="Testing Framework" secondary="Comprehensive test suite with property-based testing" /></ListItem>
                  <ListItem><ListItemText primary="Code Quality" secondary="Best practices, documentation, and maintainability" /></ListItem>
                </List>
              </CardContent>
            </Card>

            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Development Methodology
                </Typography>
                <List dense>
                  <ListItem><ListItemText primary="Iterative Refinement" secondary="Continuous improvement through human feedback and AI optimization" /></ListItem>
                  <ListItem><ListItemText primary="Quality Assurance" secondary="AI-generated test cases covering edge cases and failure modes" /></ListItem>
                  <ListItem><ListItemText primary="Documentation" secondary="Comprehensive technical documentation and user guides" /></ListItem>
                  <ListItem><ListItemText primary="Professional Standards" secondary="Industry-standard coding practices and engineering principles" /></ListItem>
                </List>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" color="info.main" gutterBottom>
                  Educational Value
                </Typography>
                <Typography variant="body2">
                  This project serves as a demonstration of how AI can augment human expertise to create 
                  sophisticated engineering software. It showcases the potential for AI-assisted development 
                  in technical domains while maintaining the rigor required for professional engineering applications.
                </Typography>
              </CardContent>
            </Card>
          </TabPanel>
        </div>
      </DialogContent>
    </Dialog>
  )
}