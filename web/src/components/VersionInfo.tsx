'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  Button,
  Tooltip,
  Paper,
  Stack,
  Alert,
  Collapse,
  LinearProgress
} from '@mui/material';
import {
  Info,
  Update,
  CheckCircle,
  History,
  GitHub,
  Close,
  ExpandMore,
  ExpandLess,
  NewReleases,
  Schedule,
  Build
} from '@mui/icons-material';
import versionData from '../../version.json';

interface ChangelogEntry {
  version: string;
  deployment: number;
  date: string;
  changes: string[];
  commit: string;
}

interface VersionData {
  version: string;
  deploymentNumber: number;
  lastDeployment: string | null;
  environment: string;
  buildNumber: string;
  gitCommit: string;
  gitBranch?: string;
  changelog: ChangelogEntry[];
}

export default function VersionInfo() {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [versionInfo, setVersionInfo] = useState<VersionData>(versionData as VersionData);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check for updates periodically
    const checkForUpdates = async () => {
      try {
        // In production, this would fetch from your API
        const response = await fetch('/api/version', { cache: 'no-store' });
        if (response.ok) {
          const remoteVersion = await response.json();
          if (remoteVersion.deploymentNumber > versionInfo.deploymentNumber) {
            setUpdateAvailable(true);
          }
        }
      } catch (error) {
        console.debug('Version check failed:', error);
      }
    };

    checkForUpdates();
    const interval = setInterval(checkForUpdates, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [versionInfo]);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getEnvironmentColor = (env: string) => {
    switch (env.toLowerCase()) {
      case 'production':
        return 'success';
      case 'staging':
        return 'warning';
      case 'development':
        return 'info';
      default:
        return 'default';
    }
  };

  const getTimeSinceDeployment = () => {
    if (!versionInfo.lastDeployment) return 'N/A';
    
    const deployTime = new Date(versionInfo.lastDeployment);
    const now = new Date();
    const diff = now.getTime() - deployTime.getTime();
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) return `${days}d ${hours}h ago`;
    if (hours > 0) return `${hours}h ${minutes}m ago`;
    return `${minutes}m ago`;
  };

  return (
    <>
      {/* Version Badge - Always visible */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        <Tooltip title="View version details">
          <Chip
            icon={<Info />}
            label={`v${versionInfo.version}`}
            color={getEnvironmentColor(versionInfo.environment) as any}
            onClick={() => setOpen(true)}
            sx={{
              cursor: 'pointer',
              fontWeight: 'bold',
              '&:hover': {
                transform: 'scale(1.05)',
                transition: 'transform 0.2s'
              }
            }}
          />
        </Tooltip>
        
        {versionInfo.deploymentNumber > 0 && (
          <Tooltip title={`Deployment #${versionInfo.deploymentNumber}`}>
            <Chip
              icon={<Build />}
              label={`#${versionInfo.deploymentNumber}`}
              variant="outlined"
              size="small"
            />
          </Tooltip>
        )}

        {updateAvailable && (
          <Tooltip title="Update available! Click to refresh">
            <IconButton
              color="primary"
              size="small"
              onClick={handleRefresh}
              sx={{
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': { transform: 'scale(1)' },
                  '50%': { transform: 'scale(1.1)' },
                  '100%': { transform: 'scale(1)' }
                }
              }}
            >
              <Update />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {/* Version Details Dialog */}
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {loading && <LinearProgress />}
        
        <DialogTitle sx={{ pb: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h5" fontWeight="bold">
              AutoCrate Version Information
            </Typography>
            <IconButton onClick={() => setOpen(false)} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          {/* Current Version Card */}
          <Paper elevation={2} sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
            <Stack spacing={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h3" fontWeight="bold" color="primary">
                    v{versionInfo.version}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    Deployment #{versionInfo.deploymentNumber}
                  </Typography>
                </Box>
                <Stack direction="row" spacing={1}>
                  <Chip
                    label={versionInfo.environment}
                    color={getEnvironmentColor(versionInfo.environment) as any}
                    icon={<CheckCircle />}
                  />
                  {versionInfo.gitBranch && (
                    <Chip
                      label={versionInfo.gitBranch}
                      variant="outlined"
                      icon={<GitHub />}
                      size="small"
                    />
                  )}
                </Stack>
              </Box>

              <Divider />

              <Stack direction="row" spacing={3}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Last Deployment
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {formatDate(versionInfo.lastDeployment)}
                  </Typography>
                  <Typography variant="caption" color="primary">
                    {getTimeSinceDeployment()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Build Number
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {versionInfo.buildNumber || 'N/A'}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Git Commit
                  </Typography>
                  <Typography variant="body2" fontWeight="medium" fontFamily="monospace">
                    {versionInfo.gitCommit || 'unknown'}
                  </Typography>
                </Box>
              </Stack>
            </Stack>
          </Paper>

          {/* Update Alert */}
          {updateAvailable && (
            <Alert
              severity="info"
              action={
                <Button color="inherit" size="small" onClick={handleRefresh}>
                  Refresh Now
                </Button>
              }
              sx={{ mb: 2 }}
            >
              A new version is available! Refresh the page to get the latest updates.
            </Alert>
          )}

          {/* Recent Changes */}
          <Box>
            <Button
              fullWidth
              startIcon={expanded ? <ExpandLess /> : <ExpandMore />}
              endIcon={<History />}
              onClick={() => setExpanded(!expanded)}
              sx={{ justifyContent: 'space-between', mb: 2 }}
            >
              Recent Changes ({versionInfo.changelog?.length || 0})
            </Button>

            <Collapse in={expanded}>
              <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto', p: 2 }}>
                {versionInfo.changelog && versionInfo.changelog.length > 0 ? (
                  <List>
                    {versionInfo.changelog.map((entry, index) => (
                      <React.Fragment key={index}>
                        <ListItem alignItems="flex-start">
                          <ListItemText
                            primary={
                              <Box display="flex" alignItems="center" gap={1}>
                                <NewReleases color="primary" fontSize="small" />
                                <Typography variant="subtitle1" fontWeight="bold">
                                  v{entry.version}
                                </Typography>
                                <Chip
                                  label={`Deploy #${entry.deployment}`}
                                  size="small"
                                  variant="outlined"
                                />
                                <Typography variant="caption" color="text.secondary">
                                  {new Date(entry.date).toLocaleDateString()}
                                </Typography>
                              </Box>
                            }
                            secondary={
                              <Box mt={1}>
                                {entry.changes.map((change, i) => (
                                  <Typography
                                    key={i}
                                    variant="body2"
                                    component="li"
                                    sx={{ ml: 2, mb: 0.5 }}
                                  >
                                    {change}
                                  </Typography>
                                ))}
                                {entry.commit && (
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                    sx={{ mt: 1, display: 'block' }}
                                  >
                                    Commit: {entry.commit}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < versionInfo.changelog.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Typography color="text.secondary" align="center">
                    No changelog entries available
                  </Typography>
                )}
              </Paper>
            </Collapse>
          </Box>

          {/* Footer */}
          <Box mt={3} display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="caption" color="text.secondary">
              AutoCrate V12 - Professional Crate Design System
            </Typography>
            <Stack direction="row" spacing={1}>
              <Button
                size="small"
                startIcon={<GitHub />}
                onClick={() => window.open('https://github.com/your-repo', '_blank')}
              >
                View Source
              </Button>
              <Button
                size="small"
                startIcon={<Schedule />}
                onClick={handleRefresh}
                disabled={loading}
              >
                Check for Updates
              </Button>
            </Stack>
          </Box>
        </DialogContent>
      </Dialog>
    </>
  );
}