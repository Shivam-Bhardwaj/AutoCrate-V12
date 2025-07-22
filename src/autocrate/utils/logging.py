"""
Logging configuration and utilities for AutoCrate.

This module provides structured logging capabilities with file rotation,
different log levels, and formatted output.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from ..exceptions import ConfigurationError


class AutoCrateLogger:
    """Custom logger for AutoCrate application."""
    
    def __init__(
        self, 
        name: str = "autocrate",
        log_file: Optional[str] = None,
        log_level: str = "INFO",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize the AutoCrate logger.
        
        Args:
            name: Logger name
            log_file: Path to log file (optional, will create default if None)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_file_size: Maximum log file size in bytes before rotation
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_file = log_file or self._get_default_log_file()
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        self._setup_handlers()
    
    def _get_default_log_file(self) -> str:
        """Get the default log file path."""
        if os.name == 'nt':  # Windows
            log_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            log_dir = os.path.join(log_dir, 'AutoCrate', 'logs')
        else:
            log_dir = os.path.join(os.path.expanduser('~'), '.autocrate', 'logs')
        
        # Create directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        return os.path.join(log_dir, 'autocrate.log')
    
    def _setup_handlers(self):
        """Set up log handlers for file and console output."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler with rotation
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
            
        except (OSError, IOError) as e:
            # If file handler fails, at least set up console handler
            print(f"Warning: Could not create log file handler: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log an info message.""" 
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log an error message."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True, **kwargs)
        else:
            self.logger.error(message, **kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log a critical message."""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", exc_info=True, **kwargs)
        else:
            self.logger.critical(message, **kwargs)
    
    def log_calculation_start(self, calculation_type: str, parameters: dict):
        """Log the start of a calculation with parameters."""
        self.info(f"Starting {calculation_type} calculation", extra={
            'calculation_type': calculation_type,
            'parameters': parameters
        })
    
    def log_calculation_complete(self, calculation_type: str, duration: float, results: dict):
        """Log the completion of a calculation with results."""
        self.info(f"Completed {calculation_type} calculation in {duration:.3f}s", extra={
            'calculation_type': calculation_type,
            'duration': duration,
            'results_count': len(results)
        })
    
    def log_calculation_error(self, calculation_type: str, error: Exception):
        """Log a calculation error."""
        self.error(f"Error in {calculation_type} calculation", exception=error, extra={
            'calculation_type': calculation_type,
            'error_type': type(error).__name__
        })
    
    def log_file_operation(self, operation: str, filepath: str, success: bool = True):
        """Log file operations."""
        if success:
            self.info(f"File {operation} successful: {filepath}")
        else:
            self.error(f"File {operation} failed: {filepath}")
    
    def log_user_action(self, action: str, details: Optional[dict] = None):
        """Log user actions for usage tracking."""
        extra = {'action': action}
        if details:
            extra.update(details)
        
        self.info(f"User action: {action}", extra=extra)
    
    def set_level(self, level: str):
        """
        Change the logging level.
        
        Args:
            level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        new_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(new_level)
        self.log_level = new_level
        
        # Update console handler level
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(new_level)
    
    def get_log_file_path(self) -> str:
        """Get the current log file path."""
        return self.log_file
    
    def get_log_stats(self) -> dict:
        """Get logging statistics."""
        stats = {
            'log_file': self.log_file,
            'log_level': logging.getLevelName(self.log_level),
            'handlers_count': len(self.logger.handlers),
            'file_exists': os.path.exists(self.log_file),
        }
        
        if stats['file_exists']:
            try:
                file_stat = os.stat(self.log_file)
                stats['file_size'] = file_stat.st_size
                stats['last_modified'] = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            except OSError:
                stats['file_size'] = None
                stats['last_modified'] = None
        
        return stats


# Global logger instance
_global_logger: Optional[AutoCrateLogger] = None


def get_logger(
    name: str = "autocrate",
    log_file: Optional[str] = None,
    log_level: str = "INFO"
) -> AutoCrateLogger:
    """
    Get or create the global AutoCrate logger.
    
    Args:
        name: Logger name
        log_file: Path to log file
        log_level: Logging level
        
    Returns:
        AutoCrateLogger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = AutoCrateLogger(name, log_file, log_level)
    
    return _global_logger


def configure_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5
):
    """
    Configure the global logging system.
    
    Args:
        log_file: Path to log file
        log_level: Logging level
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    global _global_logger
    
    _global_logger = AutoCrateLogger(
        "autocrate", log_file, log_level, max_file_size, backup_count
    )


def log_exception(exception: Exception, context: str = ""):
    """
    Log an exception with full traceback.
    
    Args:
        exception: Exception to log
        context: Additional context information
    """
    logger = get_logger()
    
    if context:
        logger.error(f"Exception in {context}", exception=exception)
    else:
        logger.error("Unhandled exception", exception=exception)


class LoggingContextManager:
    """Context manager for logging operations."""
    
    def __init__(self, operation_name: str, logger: Optional[AutoCrateLogger] = None):
        """
        Initialize logging context.
        
        Args:
            operation_name: Name of the operation being logged
            logger: Logger instance (uses global if None)
        """
        self.operation_name = operation_name
        self.logger = logger or get_logger()
        self.start_time = None
    
    def __enter__(self):
        """Enter the context."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name} in {duration:.3f}s")
        else:
            self.logger.error(
                f"Failed {self.operation_name} after {duration:.3f}s", 
                exception=exc_val
            )
        
        return False  # Don't suppress exceptions