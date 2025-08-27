import { useCallback, useEffect } from 'react'
import { logger } from '@/services/logger'

export const useWebLogger = (componentName: string) => {
  useEffect(() => {
    logger.debug(`Component ${componentName} mounted`, 'component-lifecycle')
    
    return () => {
      logger.debug(`Component ${componentName} unmounted`, 'component-lifecycle')
    }
  }, [componentName])

  const logUserInteraction = useCallback((action: string, element?: string, data?: any) => {
    logger.logUserAction(action, element, {
      component: componentName,
      ...data
    })
  }, [componentName])

  const logError = useCallback((error: Error | string, context?: string, data?: any) => {
    const errorMessage = error instanceof Error ? error.message : error
    const errorStack = error instanceof Error ? error.stack : undefined
    
    logger.error(`${componentName}: ${errorMessage}`, 'component-error', {
      context,
      stack: errorStack,
      component: componentName,
      ...data
    })
  }, [componentName])

  const logInfo = useCallback((message: string, data?: any) => {
    logger.info(`${componentName}: ${message}`, 'component', {
      component: componentName,
      ...data
    })
  }, [componentName])

  const logWarning = useCallback((message: string, data?: any) => {
    logger.warn(`${componentName}: ${message}`, 'component', {
      component: componentName,
      ...data
    })
  }, [componentName])

  const logPerformance = useCallback((metric: string, value: number, data?: any) => {
    logger.logPerformance(`${componentName}.${metric}`, value, {
      component: componentName,
      ...data
    })
  }, [componentName])

  return {
    logUserInteraction,
    logError,
    logInfo,
    logWarning,
    logPerformance,
    logger
  }
}
