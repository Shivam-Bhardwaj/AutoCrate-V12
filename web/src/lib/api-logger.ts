import { logger } from '@/services/logger'

export interface ApiLogConfig {
  logRequests?: boolean
  logResponses?: boolean
  logErrors?: boolean
  logPerformance?: boolean
}

const defaultConfig: ApiLogConfig = {
  logRequests: true,
  logResponses: true,
  logErrors: true,
  logPerformance: true
}

export class ApiLogger {
  private config: ApiLogConfig

  constructor(config: ApiLogConfig = {}) {
    this.config = { ...defaultConfig, ...config }
  }

  // Fetch wrapper with logging
  async loggedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const startTime = performance.now()
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // Log request
    if (this.config.logRequests) {
      logger.info('API Request Started', 'api-request', {
        requestId,
        method: options.method || 'GET',
        url,
        headers: options.headers,
        body: options.body ? this.sanitizeBody(options.body) : undefined
      })
    }

    try {
      const response = await fetch(url, options)
      const endTime = performance.now()
      const duration = endTime - startTime

      // Log performance
      if (this.config.logPerformance) {
        logger.logPerformance('api-call-duration', duration, {
          requestId,
          url,
          method: options.method || 'GET',
          status: response.status
        })
      }

      // Log response
      if (this.config.logResponses) {
        const responseClone = response.clone()
        let responseBody: any = null
        
        try {
          const contentType = response.headers.get('content-type')
          if (contentType?.includes('application/json')) {
            responseBody = await responseClone.json()
          } else {
            responseBody = await responseClone.text()
          }
        } catch (e) {
          // Response body couldn't be parsed
        }

        logger.logApiCall(
          options.method || 'GET',
          url,
          response.status,
          duration,
          {
            requestId,
            responseHeaders: Object.fromEntries(response.headers.entries()),
            responseBody: this.sanitizeResponseBody(responseBody),
            success: response.ok
          }
        )
      }

      // Log errors for non-2xx responses
      if (!response.ok && this.config.logErrors) {
        logger.error('API Request Failed', 'api-error', {
          requestId,
          method: options.method || 'GET',
          url,
          status: response.status,
          statusText: response.statusText,
          duration
        })
      }

      return response
    } catch (error) {
      const endTime = performance.now()
      const duration = endTime - startTime

      // Log network/fetch errors
      if (this.config.logErrors) {
        logger.error('API Request Error', 'api-error', {
          requestId,
          method: options.method || 'GET',
          url,
          error: error instanceof Error ? error.message : String(error),
          duration
        })
      }

      throw error
    }
  }

  private sanitizeBody(body: any): any {
    if (!body) return body
    
    try {
      if (typeof body === 'string') {
        const parsed = JSON.parse(body)
        return this.sanitizeObject(parsed)
      }
      return this.sanitizeObject(body)
    } catch {
      return '[Non-JSON Body]'
    }
  }

  private sanitizeResponseBody(body: any): any {
    if (!body) return body
    return this.sanitizeObject(body)
  }

  private sanitizeObject(obj: any): any {
    if (!obj || typeof obj !== 'object') return obj
    
    const sensitiveKeys = ['password', 'token', 'key', 'secret', 'auth']
    const sanitized = { ...obj }
    
    for (const key in sanitized) {
      if (sensitiveKeys.some(sensitive => key.toLowerCase().includes(sensitive))) {
        sanitized[key] = '[REDACTED]'
      } else if (typeof sanitized[key] === 'object') {
        sanitized[key] = this.sanitizeObject(sanitized[key])
      }
    }
    
    return sanitized
  }
}

// Create singleton instance
export const apiLogger = new ApiLogger()

// Enhanced fetch function
export const loggedFetch = apiLogger.loggedFetch.bind(apiLogger)
