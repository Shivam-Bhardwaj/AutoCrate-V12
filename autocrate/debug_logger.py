"""
AutoCrate Debug Logging System
Comprehensive logging for debugging, error tracking, and performance monitoring.
"""

import logging
import os
import sys
import datetime
import traceback
import functools
from pathlib import Path
from typing import Optional, Any, Dict
import json

class AutoCrateLogger:
    """
    Centralized logging system for AutoCrate with multiple output formats and debug levels.
    """
    
    def __init__(self, name: str = "AutoCrate", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamp for this session
        self.session_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{self.session_timestamp}_{os.getpid()}"
        
        # Initialize loggers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Setup file handlers
        self._setup_file_handlers()
        
        # Setup console handler
        self._setup_console_handler()
        
        # Performance tracking
        self.performance_data = {}
        self.function_calls = {}
        
        # Log session start
        self.info(f"=== AutoCrate Debug Session Started ===")
        self.info(f"Session ID: {self.session_id}")
        self.info(f"Python Version: {sys.version}")
        self.info(f"Working Directory: {os.getcwd()}")
        self.info(f"Log Directory: {self.log_dir.absolute()}")
    
    def _setup_file_handlers(self):
        """Setup file handlers for different log levels."""
        
        # Main debug log (everything)
        debug_log = self.log_dir / f"debug_{self.session_timestamp}.log"
        debug_handler = logging.FileHandler(debug_log, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        debug_handler.setFormatter(debug_formatter)
        self.logger.addHandler(debug_handler)
        
        # Error log (errors only)
        error_log = self.log_dir / f"errors_{self.session_timestamp}.log"
        error_handler = logging.FileHandler(error_log, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s | ERROR | %(name)s | %(funcName)s:%(lineno)d | %(message)s\n%(message)s\n'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
        
        # Performance log (JSON format)
        self.perf_log_file = self.log_dir / f"performance_{self.session_timestamp}.json"
        
    def _setup_console_handler(self):
        """Setup console handler for immediate feedback."""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Set console level based on environment
        debug_mode = os.getenv('AUTOCRATE_DEBUG', '0') == '1'
        console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-5s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, extra_data: Optional[Dict] = None):
        """Log debug message with optional structured data."""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, default=str)}"
        self.logger.debug(message)
    
    def info(self, message: str, extra_data: Optional[Dict] = None):
        """Log info message with optional structured data."""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, default=str)}"
        self.logger.info(message)
    
    def warning(self, message: str, extra_data: Optional[Dict] = None):
        """Log warning message with optional structured data."""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, default=str)}"
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None, extra_data: Optional[Dict] = None):
        """Log error message with optional exception and structured data."""
        error_info = {
            'message': message,
            'session_id': self.session_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if exception:
            error_info.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': traceback.format_exc()
            })
        
        if extra_data:
            error_info['extra_data'] = extra_data
        
        # Log to both regular log and structured error log
        self.logger.error(f"{message} | Error Info: {json.dumps(error_info, default=str)}")
        
        # Also save detailed error to separate file
        error_file = self.log_dir / f"error_detail_{self.session_timestamp}.json"
        try:
            with open(error_file, 'a', encoding='utf-8') as f:
                json.dump(error_info, f, default=str, indent=2)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write detailed error log: {e}")
    
    def critical(self, message: str, exception: Optional[Exception] = None):
        """Log critical error that may cause application failure."""
        self.error(f"CRITICAL: {message}", exception)
        self.logger.critical(message)
    
    def log_function_entry(self, func_name: str, args: tuple = (), kwargs: dict = None):
        """Log function entry with parameters."""
        kwargs = kwargs or {}
        self.debug(f"ENTER {func_name}", {
            'args': str(args) if args else None,
            'kwargs': kwargs if kwargs else None
        })
    
    def log_function_exit(self, func_name: str, result: Any = None, duration: Optional[float] = None):
        """Log function exit with result and duration."""
        extra_data = {}
        if result is not None:
            extra_data['result_type'] = type(result).__name__
            if hasattr(result, '__len__'):
                extra_data['result_length'] = len(result)
        if duration is not None:
            extra_data['duration_ms'] = round(duration * 1000, 2)
            
        self.debug(f"EXIT {func_name}", extra_data)
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict] = None):
        """Log performance metrics."""
        perf_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'session_id': self.session_id,
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'details': details or {}
        }
        
        # Store in memory for analysis
        if operation not in self.performance_data:
            self.performance_data[operation] = []
        self.performance_data[operation].append(perf_data)
        
        # Log to file
        try:
            with open(self.perf_log_file, 'a', encoding='utf-8') as f:
                json.dump(perf_data, f, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write performance log: {e}")
        
        self.info(f"PERFORMANCE: {operation} completed in {perf_data['duration_ms']}ms")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary for current session."""
        summary = {}
        for operation, data_points in self.performance_data.items():
            durations = [dp['duration_ms'] for dp in data_points]
            summary[operation] = {
                'count': len(durations),
                'avg_ms': round(sum(durations) / len(durations), 2),
                'min_ms': min(durations),
                'max_ms': max(durations),
                'total_ms': round(sum(durations), 2)
            }
        return summary
    
    def log_test_results(self, test_name: str, status: str, duration: float, details: Optional[Dict] = None):
        """Log test execution results with structured data."""
        test_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'session_id': self.session_id,
            'test_name': test_name,
            'status': status,
            'duration_ms': round(duration * 1000, 2),
            'details': details or {}
        }
        
        # Log to main log
        status_icon = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', 'ERROR': '💥'}.get(status, '❓')
        self.info(f"TEST {status_icon} {test_name} ({test_data['duration_ms']}ms)", test_data)
        
        # Save to separate test log
        test_log_file = self.log_dir / f"test_results_{self.session_timestamp}.json"
        try:
            with open(test_log_file, 'a', encoding='utf-8') as f:
                json.dump(test_data, f, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write test results: {e}")
    
    def log_test_suite_summary(self, suite_name: str, passed: int, failed: int, skipped: int, duration: float):
        """Log test suite execution summary."""
        total_tests = passed + failed + skipped
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            'suite_name': suite_name,
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': round(pass_rate, 1),
            'duration_seconds': round(duration, 2),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        status_icon = '✅' if failed == 0 else '❌'
        self.info(f"TEST SUITE {status_icon} {suite_name}: {passed}/{total_tests} passed ({pass_rate:.1f}%)", summary)

    def finalize_session(self):
        """Finalize logging session and write summary."""
        summary = {
            'session_id': self.session_id,
            'end_time': datetime.datetime.now().isoformat(),
            'performance_summary': self.get_performance_summary(),
            'function_call_counts': self.function_calls
        }
        
        # Write session summary
        summary_file = self.log_dir / f"session_summary_{self.session_timestamp}.json"
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, default=str, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write session summary: {e}")
        
        self.info("=== AutoCrate Debug Session Ended ===")
        self.info(f"Session Summary: {summary_file}")

def debug_function(logger: AutoCrateLogger):
    """Decorator to automatically log function entry/exit and performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Track function calls
            if func_name not in logger.function_calls:
                logger.function_calls[func_name] = 0
            logger.function_calls[func_name] += 1
            
            # Log entry
            logger.log_function_entry(func_name, args, kwargs)
            
            # Execute with timing
            start_time = datetime.datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.datetime.now() - start_time).total_seconds()
                
                # Log exit
                logger.log_function_exit(func_name, result, duration)
                logger.log_performance(func_name, duration, {
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
                
                return result
                
            except Exception as e:
                duration = (datetime.datetime.now() - start_time).total_seconds()
                logger.error(f"Exception in {func_name}", e, {
                    'duration_ms': round(duration * 1000, 2),
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
                raise
                
        return wrapper
    return decorator

# Global logger instance
_global_logger: Optional[AutoCrateLogger] = None

def get_logger(name: str = "AutoCrate") -> AutoCrateLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = AutoCrateLogger(name)
    return _global_logger

def finalize_logging():
    """Finalize the global logging session."""
    global _global_logger
    if _global_logger is not None:
        _global_logger.finalize_session()

# Convenience functions
def debug(message: str, extra_data: Optional[Dict] = None):
    get_logger().debug(message, extra_data)

def info(message: str, extra_data: Optional[Dict] = None):
    get_logger().info(message, extra_data)

def warning(message: str, extra_data: Optional[Dict] = None):
    get_logger().warning(message, extra_data)

def error(message: str, exception: Optional[Exception] = None, extra_data: Optional[Dict] = None):
    get_logger().error(message, exception, extra_data)

def critical(message: str, exception: Optional[Exception] = None):
    get_logger().critical(message, exception)

def log_performance(operation: str, duration: float, details: Optional[Dict] = None):
    get_logger().log_performance(operation, duration, details)

def log_test_results(test_name: str, status: str, duration: float, details: Optional[Dict] = None):
    get_logger().log_test_results(test_name, status, duration, details)

def log_test_suite_summary(suite_name: str, passed: int, failed: int, skipped: int, duration: float):
    get_logger().log_test_suite_summary(suite_name, passed, failed, skipped, duration)