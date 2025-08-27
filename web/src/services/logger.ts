/**
 * Advanced logging service for AutoCrate Web
 * Provides comprehensive logging with local storage and server sync
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  CRITICAL = 4
}

export interface LogEntry {
  id: string
  timestamp: Date
  level: LogLevel
  message: string
  category?: string
  data?: any
  sessionId?: string
  userAgent?: string
  url?: string
  stack?: string
}

export interface LogFilter {
  level?: LogLevel
  category?: string
  startTime?: Date
  endTime?: Date
  searchTerm?: string
}

class Logger {
  private static instance: Logger
  private logs: LogEntry[] = []
  private maxLogs = 1000
  private sessionId: string
  private enableConsoleOutput = true
  private enableServerSync = false
  private isLogging = false // Prevent recursion
  private originalConsole = {
    log: console.log,
    debug: console.debug,
    info: console.info,
    warn: console.warn,
    error: console.error
  }

  private constructor() {
    this.sessionId = this.generateSessionId()
    this.loadFromLocalStorage()
    
    if (typeof window !== 'undefined') {
      this.setupErrorHandlers()
    }
  }

  private setupErrorHandlers() {
    // Global error handler
    window.addEventListener('error', (event) => {
      if (!this.isLogging) {
        this.isLogging = true
        try {
          this.error('Unhandled Error', 'global', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error?.message || event.error?.toString()
          })
        } finally {
          this.isLogging = false
        }
      }
    })

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      if (!this.isLogging) {
        this.isLogging = true
        try {
          this.error('Unhandled Promise Rejection', 'global', {
            reason: event.reason?.message || event.reason?.toString() || 'Unknown reason'
          })
        } finally {
          this.isLogging = false
        }
      }
    })

    // Override console.error to capture all errors (with recursion prevention)
    const originalError = this.originalConsole.error
    console.error = (...args) => {
      // Always call original first
      originalError.apply(console, args)
      
      // Then try to log if not already logging
      if (!this.isLogging) {
        this.isLogging = true
        try {
          const message = args.map(arg => {
            if (typeof arg === 'string') return arg
            if (arg?.message) return arg.message
            try {
              return JSON.stringify(arg)
            } catch {
              return 'Complex object'
            }
          }).join(' ')
          
          // Only create log entry, don't log to console again
          const entry = this.createLogEntry(LogLevel.ERROR, 'Console Error: ' + message, 'console')
          this.addLog(entry)
        } catch (e) {
          // Silently fail to prevent any issues
        } finally {
          this.isLogging = false
        }
      }
    }

    // Log initial page load
    this.info('Page loaded', 'navigation', {
      url: window.location.href,
      referrer: document.referrer
    })
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }

  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  private createLogEntry(
    level: LogLevel,
    message: string,
    category: string,
    data?: any
  ): LogEntry {
    // Clean data to prevent circular references
    let cleanData = undefined
    if (data) {
      try {
        cleanData = this.cleanData(data)
      } catch {
        cleanData = { error: 'Could not serialize data' }
      }
    }

    return {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      level,
      message,
      category,
      data: cleanData,
      sessionId: this.sessionId,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'SSR',
      url: typeof window !== 'undefined' ? window.location.href : 'SSR',
      stack: level >= LogLevel.ERROR ? new Error().stack : undefined
    }
  }

  private cleanData(obj: any, seen = new WeakSet()): any {
    if (obj === null || obj === undefined) return obj
    if (typeof obj !== 'object') return obj
    
    // Handle circular references
    if (seen.has(obj)) return '[Circular Reference]'
    seen.add(obj)
    
    // Handle special cases
    if (obj instanceof Error) {
      return {
        name: obj.name,
        message: obj.message,
        stack: obj.stack
      }
    }
    
    if (obj instanceof Date) {
      return obj.toISOString()
    }
    
    if (Array.isArray(obj)) {
      return obj.map(item => this.cleanData(item, seen))
    }
    
    // Handle regular objects
    const cleaned: any = {}
    for (const key in obj) {
      try {
        if (obj.hasOwnProperty(key)) {
          cleaned[key] = this.cleanData(obj[key], seen)
        }
      } catch {
        cleaned[key] = '[Unserializable]'
      }
    }
    return cleaned
  }

  private addLog(entry: LogEntry) {
    this.logs.push(entry)
    
    // Keep only the most recent logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs)
    }
    
    // Log to console if enabled (but prevent recursion)
    if (this.enableConsoleOutput && !this.isLogging) {
      this.logToConsole(entry)
    }
    
    // Save to local storage
    this.saveToLocalStorage()
    
    // Sync with server if enabled
    if (this.enableServerSync) {
      this.sendToServer(entry).catch(() => {
        // Silently fail server sync
      })
    }
  }

  private logToConsole(entry: LogEntry) {
    if (!this.enableConsoleOutput || this.isLogging) return
    
    const timestamp = entry.timestamp.toISOString()
    const prefix = `[${timestamp}] [${entry.category || 'general'}]`
    
    // Use original console methods to prevent recursion
    switch (entry.level) {
      case LogLevel.DEBUG:
        this.originalConsole.debug(prefix, entry.message, entry.data)
        break
      case LogLevel.INFO:
        this.originalConsole.info(prefix, entry.message, entry.data)
        break
      case LogLevel.WARN:
        this.originalConsole.warn(prefix, entry.message, entry.data)
        break
      case LogLevel.ERROR:
      case LogLevel.CRITICAL:
        // Don't use console.error as it might be overridden
        this.originalConsole.error(prefix, entry.message, entry.data)
        break
    }
  }

  private async sendToServer(entry: LogEntry) {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      await fetch(`${apiUrl}/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry)
      })
    } catch (error) {
      // Silently fail - don't log to prevent recursion
    }
  }

  private saveToLocalStorage() {
    if (typeof window === 'undefined') return
    
    try {
      const recentLogs = this.logs.slice(-100) // Save only last 100 logs
      localStorage.setItem('autocrate_logs', JSON.stringify(recentLogs))
    } catch (error) {
      // Silently fail if localStorage is full or unavailable
    }
  }

  private loadFromLocalStorage() {
    if (typeof window === 'undefined') return
    
    try {
      const stored = localStorage.getItem('autocrate_logs')
      if (stored) {
        const parsed = JSON.parse(stored)
        this.logs = parsed.map((log: any) => ({
          ...log,
          timestamp: new Date(log.timestamp)
        }))
      }
    } catch (error) {
      // Silently fail if data is corrupted
    }
  }

  // Public logging methods
  debug(message: string, category?: string, data?: any) {
    if (this.isLogging) return
    const entry = this.createLogEntry(LogLevel.DEBUG, message, category || 'general', data)
    this.addLog(entry)
  }

  info(message: string, category?: string, data?: any) {
    if (this.isLogging) return
    const entry = this.createLogEntry(LogLevel.INFO, message, category || 'general', data)
    this.addLog(entry)
  }

  warn(message: string, category?: string, data?: any) {
    if (this.isLogging) return
    const entry = this.createLogEntry(LogLevel.WARN, message, category || 'general', data)
    this.addLog(entry)
  }

  error(message: string, category?: string, data?: any) {
    if (this.isLogging) return
    const entry = this.createLogEntry(LogLevel.ERROR, message, category || 'general', data)
    this.addLog(entry)
  }

  critical(message: string, category?: string, data?: any) {
    if (this.isLogging) return
    const entry = this.createLogEntry(LogLevel.CRITICAL, message, category || 'general', data)
    this.addLog(entry)
  }

  // Query and filter methods
  getLogs(filter?: LogFilter): LogEntry[] {
    let filtered = [...this.logs]
    
    if (filter) {
      if (filter.level !== undefined) {
        filtered = filtered.filter(log => log.level >= filter.level!)
      }
      
      if (filter.category) {
        filtered = filtered.filter(log => log.category === filter.category)
      }
      
      if (filter.startTime) {
        filtered = filtered.filter(log => log.timestamp >= filter.startTime!)
      }
      
      if (filter.endTime) {
        filtered = filtered.filter(log => log.timestamp <= filter.endTime!)
      }
      
      if (filter.searchTerm) {
        const term = filter.searchTerm.toLowerCase()
        filtered = filtered.filter(log => 
          log.message.toLowerCase().includes(term) ||
          JSON.stringify(log.data).toLowerCase().includes(term)
        )
      }
    }
    
    return filtered
  }

  clearLogs() {
    this.logs = []
    this.saveToLocalStorage()
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2)
  }

  // User action logging method
  logUserAction(action: string, element?: string, data?: any) {
    if (this.isLogging) return
    const entry = this.createLogEntry(LogLevel.INFO, `User action: ${action}`, 'user-action', {
      action,
      element,
      ...data
    })
    this.addLog(entry)
  }

  // Performance logging method
  logPerformance(metric: string, value: number, data?: any) {
    if (this.isLogging) return
    const entry = this.createLogEntry(LogLevel.DEBUG, `Performance: ${metric}`, 'performance', {
      metric,
      value,
      unit: 'ms',
      ...data
    })
    this.addLog(entry)
  }

  // Configuration methods
  setConsoleOutput(enabled: boolean) {
    this.enableConsoleOutput = enabled
  }

  setServerSync(enabled: boolean) {
    this.enableServerSync = enabled
  }
}

const logger = Logger.getInstance()
export { logger }
export default logger