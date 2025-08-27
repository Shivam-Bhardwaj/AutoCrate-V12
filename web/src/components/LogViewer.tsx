'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { 
  Paper, 
  Typography, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel, 
  Button, 
  TextField, 
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Collapse
} from '@mui/material'
import { 
  ExpandMore as ExpandMoreIcon, 
  ExpandLess as ExpandLessIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material'
import { logger, LogLevel, LogEntry } from '@/services/logger'

const LogViewer: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [selectedLevel, setSelectedLevel] = useState<LogLevel | 'all'>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null)

  useEffect(() => {
    // Load logs on mount
    const loadedLogs = logger.getLogs()
    setLogs(loadedLogs)

    // Set up periodic refresh
    const interval = setInterval(() => {
      const currentLogs = logger.getLogs()
      setLogs(currentLogs)
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(logs.map(log => log.category))
    return Array.from(cats)
  }, [logs])

  // Filter logs
  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (selectedLevel !== 'all' && log.level !== selectedLevel) return false
      if (selectedCategory !== 'all' && log.category !== selectedCategory) return false
      if (searchTerm && !log.message.toLowerCase().includes(searchTerm.toLowerCase())) return false
      return true
    })
  }, [logs, selectedLevel, selectedCategory, searchTerm])

  const getLevelColor = (level: LogLevel) => {
    switch (level) {
      case LogLevel.CRITICAL: return 'error'
      case LogLevel.ERROR: return 'error'
      case LogLevel.WARN: return 'warning'
      case LogLevel.INFO: return 'info'
      case LogLevel.DEBUG: return 'default'
      default: return 'default'
    }
  }

  const getLevelIcon = (level: LogLevel) => {
    switch (level) {
      case LogLevel.CRITICAL: return <ErrorIcon fontSize="small" />
      case LogLevel.ERROR: return <ErrorIcon fontSize="small" />
      case LogLevel.WARN: return <WarningIcon fontSize="small" />
      case LogLevel.INFO: return <InfoIcon fontSize="small" />
      case LogLevel.DEBUG: return <BugReportIcon fontSize="small" />
      default: return null
    }
  }

  const getLevelText = (level: LogLevel) => {
    switch (level) {
      case LogLevel.CRITICAL: return 'CRITICAL'
      case LogLevel.ERROR: return 'ERROR'
      case LogLevel.WARN: return 'WARN'
      case LogLevel.INFO: return 'INFO'
      case LogLevel.DEBUG: return 'DEBUG'
      default: return 'UNKNOWN'
    }
  }

  const toggleRow = (id: string) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const handleClearLogs = () => {
    logger.clearLogs()
    setLogs([])
  }

  return (
    <div style={{ padding: 16 }}>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          AutoCrate Web Logs
        </Typography>
        
        <div style={{ display: 'flex', gap: '16px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Level</InputLabel>
            <Select
              value={selectedLevel}
              label="Level"
              onChange={(e) => setSelectedLevel(e.target.value as LogLevel | 'all')}
            >
              <MenuItem value="all">All Levels</MenuItem>
              <MenuItem value={LogLevel.CRITICAL}>Critical</MenuItem>
              <MenuItem value={LogLevel.ERROR}>Error</MenuItem>
              <MenuItem value={LogLevel.WARN}>Warning</MenuItem>
              <MenuItem value={LogLevel.INFO}>Info</MenuItem>
              <MenuItem value={LogLevel.DEBUG}>Debug</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={selectedCategory}
              label="Category"
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <MenuItem value="all">All Categories</MenuItem>
              {categories.map(cat => (
                <MenuItem key={cat} value={cat}>{cat}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            size="small"
            label="Search"
            variant="outlined"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <Button
            variant="outlined"
            startIcon={<DeleteIcon />}
            onClick={handleClearLogs}
            color="error"
          >
            Clear Logs
          </Button>
        </div>

        <Typography variant="body2" color="text.secondary">
          Total: {logs.length} logs | Showing: {filteredLogs.length} logs
        </Typography>
      </Paper>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell width={50}></TableCell>
              <TableCell width={150}>Timestamp</TableCell>
              <TableCell width={80}>Level</TableCell>
              <TableCell width={120}>Category</TableCell>
              <TableCell>Message</TableCell>
              <TableCell width={100}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredLogs.map((log) => (
              <React.Fragment key={log.id}>
                <TableRow hover>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => toggleRow(log.id)}
                    >
                      {expandedRows.has(log.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getLevelText(log.level)}
                      color={getLevelColor(log.level) as any}
                      size="small"
                      icon={getLevelIcon(log.level) as any}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">{log.category}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{log.message}</Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => setSelectedLog(log)}
                    >
                      <InfoIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
                {expandedRows.has(log.id) && (
                  <TableRow>
                    <TableCell colSpan={6} sx={{ py: 0 }}>
                      <Collapse in={expandedRows.has(log.id)}>
                        <div style={{ padding: '16px', backgroundColor: '#f5f5f5' }}>
                          {log.data && (
                            <>
                              <Typography variant="body2" gutterBottom>
                                <strong>Data:</strong>
                              </Typography>
                              <pre style={{ 
                                fontSize: '11px', 
                                overflow: 'auto',
                                backgroundColor: '#fff',
                                padding: '8px',
                                borderRadius: '4px',
                                maxHeight: '200px'
                              }}>
                                {JSON.stringify(log.data, null, 2)}
                              </pre>
                            </>
                          )}
                          {log.stack && (
                            <>
                              <Typography variant="body2" gutterBottom>
                                <strong>Stack Trace:</strong>
                              </Typography>
                              <pre style={{ 
                                fontSize: '11px', 
                                overflow: 'auto',
                                backgroundColor: '#fff',
                                padding: '8px',
                                borderRadius: '4px',
                                maxHeight: '200px'
                              }}>
                                {log.stack}
                              </pre>
                            </>
                          )}
                        </div>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                )}
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={!!selectedLog}
        onClose={() => setSelectedLog(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Log Details</DialogTitle>
        <DialogContent>
          {selectedLog && (
            <div>
              <Typography><strong>ID:</strong> {selectedLog.id}</Typography>
              <Typography><strong>Timestamp:</strong> {selectedLog.timestamp.toISOString()}</Typography>
              <Typography><strong>Level:</strong> {getLevelText(selectedLog.level)}</Typography>
              <Typography><strong>Category:</strong> {selectedLog.category}</Typography>
              <Typography><strong>Message:</strong> {selectedLog.message}</Typography>
              <Typography><strong>Session ID:</strong> {selectedLog.sessionId}</Typography>
              <Typography><strong>URL:</strong> {selectedLog.url}</Typography>
              <Typography><strong>User Agent:</strong> {selectedLog.userAgent}</Typography>
              
              {selectedLog.data && (
                <>
                  <Typography variant="h6" sx={{ mt: 2 }}>Data:</Typography>
                  <pre style={{ fontSize: '12px', overflow: 'auto', backgroundColor: '#f5f5f5', padding: '8px' }}>
                    {JSON.stringify(selectedLog.data, null, 2)}
                  </pre>
                </>
              )}
              
              {selectedLog.stack && (
                <>
                  <Typography variant="h6" sx={{ mt: 2 }}>Stack Trace:</Typography>
                  <pre style={{ fontSize: '12px', overflow: 'auto', backgroundColor: '#f5f5f5', padding: '8px' }}>
                    {selectedLog.stack}
                  </pre>
                </>
              )}
            </div>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedLog(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}

export default LogViewer