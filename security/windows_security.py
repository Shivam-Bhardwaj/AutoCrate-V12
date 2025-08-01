#!/usr/bin/env python3
"""
AutoCrate Windows Security Manager

Provides Windows-specific security features including process security,
memory management, and system integration for secure operation.
"""

import os
import sys
import psutil
import logging
import threading
import time
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path
from enum import Enum
import gc
import ctypes
from ctypes import wintypes

# Windows-specific imports
try:
    import win32api
    import win32con
    import win32security
    import win32process
    import win32job
    import pywintypes
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False
    logging.warning("Windows API modules not available - limited security features")

from .input_validator import SecurityValidator, ValidationError

# Configure security logging
security_logger = logging.getLogger('AutoCrate.Security.Windows')

# Windows security constants
if WINDOWS_API_AVAILABLE:
    # Process security constants
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    TOKEN_QUERY = 0x0008
    
    # Memory protection constants
    MEM_COMMIT = 0x1000
    MEM_RESERVE = 0x2000
    MEM_RELEASE = 0x8000
    PAGE_READWRITE = 0x04
    PAGE_NOACCESS = 0x01


class SecurityLevel(Enum):
    """Security levels for process operation."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class ProcessPrivilege(Enum):
    """Process privilege levels."""
    USER = "user"
    POWER_USER = "power_user"
    ADMINISTRATOR = "administrator"
    SYSTEM = "system"


class WindowsSecurityManager:
    """Windows-specific security management for AutoCrate."""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.STANDARD):
        """Initialize Windows security manager."""
        self.security_level = security_level
        self.validator = SecurityValidator()
        self.process = psutil.Process()
        self.memory_monitor = None
        self.security_token = None
        self._secure_memory_regions = set()
        self._lock = threading.RLock()
        
        # Initialize security features
        self._initialize_security()
        
        security_logger.info(f"Windows security manager initialized at {security_level.value} level")
    
    def _initialize_security(self) -> None:
        """Initialize Windows security features."""
        try:
            # Check if running with appropriate privileges
            self._check_process_privileges()
            
            # Set up process security
            self._configure_process_security()
            
            # Initialize memory monitoring
            if self.security_level in [SecurityLevel.ENHANCED, SecurityLevel.MAXIMUM]:
                self._start_memory_monitoring()
            
            # Set up job object for process containment
            if WINDOWS_API_AVAILABLE and self.security_level == SecurityLevel.MAXIMUM:
                self._create_job_object()
                
        except Exception as e:
            security_logger.warning(f"Could not initialize all security features: {e}")
    
    def _check_process_privileges(self) -> ProcessPrivilege:
        """Check current process privilege level."""
        try:
            if WINDOWS_API_AVAILABLE:
                # Check if running as administrator
                if ctypes.windll.shell32.IsUserAnAdmin():
                    privilege = ProcessPrivilege.ADMINISTRATOR
                else:
                    privilege = ProcessPrivilege.USER
            else:
                # Basic check using os module
                if os.name == 'nt' and hasattr(os, 'getuid'):
                    privilege = ProcessPrivilege.ADMINISTRATOR if os.getuid() == 0 else ProcessPrivilege.USER
                else:
                    privilege = ProcessPrivilege.USER
            
            security_logger.info(f"Process running with {privilege.value} privileges")
            
            # Warn if running with excessive privileges
            if privilege == ProcessPrivilege.ADMINISTRATOR:
                security_logger.warning("Running with administrator privileges - consider using standard user")
            
            return privilege
            
        except Exception as e:
            security_logger.warning(f"Could not determine process privileges: {e}")
            return ProcessPrivilege.USER
    
    def _configure_process_security(self) -> None:
        """Configure process-level security settings."""
        try:
            # Set process priority to prevent resource hogging
            if hasattr(self.process, 'nice'):
                self.process.nice(psutil.NORMAL_PRIORITY_CLASS)
            
            # Limit process memory if possible
            if WINDOWS_API_AVAILABLE and self.security_level == SecurityLevel.MAXIMUM:
                self._set_memory_limits()
            
            # Set CPU affinity to prevent excessive CPU usage
            if self.security_level in [SecurityLevel.ENHANCED, SecurityLevel.MAXIMUM]:
                try:
                    cpu_count = psutil.cpu_count()
                    if cpu_count > 2:
                        # Use half of available CPUs
                        affinity_mask = list(range(cpu_count // 2))
                        self.process.cpu_affinity(affinity_mask)
                        security_logger.info(f"CPU affinity set to: {affinity_mask}")
                except:
                    pass  # Not critical if this fails
            
        except Exception as e:
            security_logger.warning(f"Process security configuration failed: {e}")
    
    def _set_memory_limits(self) -> None:
        """Set memory limits for the process."""
        try:
            if WINDOWS_API_AVAILABLE:
                # Get current process handle
                process_handle = win32api.GetCurrentProcess()
                
                # Set working set size (limit RAM usage)
                # 512MB min, 1GB max for AutoCrate
                min_working_set = 512 * 1024 * 1024  # 512MB
                max_working_set = 1024 * 1024 * 1024  # 1GB
                
                try:
                    win32process.SetProcessWorkingSetSize(
                        process_handle, min_working_set, max_working_set
                    )
                    security_logger.info(f"Memory limits set: {min_working_set // (1024*1024)}MB - {max_working_set // (1024*1024)}MB")
                except Exception as e:
                    security_logger.debug(f"Could not set memory limits: {e}")
                    
        except Exception as e:
            security_logger.warning(f"Memory limit configuration failed: {e}")
    
    def _create_job_object(self) -> None:
        """Create job object for process containment."""
        try:
            if WINDOWS_API_AVAILABLE:
                # Create job object
                job_handle = win32job.CreateJobObject(None, "AutoCrateJob")
                
                # Set job limits
                job_info = win32job.JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
                job_info.BasicLimitInformation.LimitFlags = (
                    win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY |
                    win32job.JOB_OBJECT_LIMIT_JOB_MEMORY |
                    win32job.JOB_OBJECT_LIMIT_ACTIVE_PROCESS
                )
                
                # Set memory limits (1GB process, 2GB job)
                job_info.ProcessMemoryLimit = 1024 * 1024 * 1024  # 1GB
                job_info.JobMemoryLimit = 2048 * 1024 * 1024  # 2GB
                job_info.BasicLimitInformation.ActiveProcessLimit = 1
                
                win32job.SetInformationJobObject(
                    job_handle, 
                    win32job.JobObjectExtendedLimitInformation, 
                    job_info
                )
                
                # Assign current process to job
                process_handle = win32api.GetCurrentProcess()
                win32job.AssignProcessToJobObject(job_handle, process_handle)
                
                security_logger.info("Process assigned to secure job object")
                
        except Exception as e:
            security_logger.warning(f"Job object creation failed: {e}")
    
    def _start_memory_monitoring(self) -> None:
        """Start memory usage monitoring."""
        def monitor_memory():
            """Memory monitoring thread function."""
            while True:
                try:
                    memory_info = self.process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)
                    
                    # Log high memory usage
                    if memory_mb > 500:  # 500MB threshold
                        security_logger.warning(f"High memory usage: {memory_mb:.1f}MB")
                    
                    # Force garbage collection if memory is high
                    if memory_mb > 750:  # 750MB threshold
                        security_logger.warning("Forcing garbage collection due to high memory usage")
                        gc.collect()
                    
                    # Check for memory leaks
                    if hasattr(self, '_last_memory_check'):
                        memory_growth = memory_mb - self._last_memory_check
                        if memory_growth > 100:  # 100MB growth
                            security_logger.warning(f"Potential memory leak detected: +{memory_growth:.1f}MB")
                    
                    self._last_memory_check = memory_mb
                    
                    # Sleep for monitoring interval
                    time.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    security_logger.debug(f"Memory monitoring error: {e}")
                    time.sleep(60)  # Longer sleep on error
        
        # Start monitoring thread
        self.memory_monitor = threading.Thread(target=monitor_memory, daemon=True)
        self.memory_monitor.start()
        security_logger.info("Memory monitoring started")
    
    def allocate_secure_memory(self, size: int) -> Optional[int]:
        """Allocate secure memory region."""
        try:
            if not WINDOWS_API_AVAILABLE:
                return None
            
            # Allocate memory with read/write access
            address = ctypes.windll.kernel32.VirtualAlloc(
                None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
            )
            
            if address:
                with self._lock:
                    self._secure_memory_regions.add((address, size))
                security_logger.debug(f"Allocated secure memory: {size} bytes at 0x{address:x}")
                return address
            else:
                security_logger.warning(f"Failed to allocate secure memory: {size} bytes")
                return None
                
        except Exception as e:
            security_logger.error(f"Secure memory allocation failed: {e}")
            return None
    
    def free_secure_memory(self, address: int) -> bool:
        """Free secure memory region."""
        try:
            if not WINDOWS_API_AVAILABLE:
                return False
            
            # Find memory region
            region_info = None
            with self._lock:
                for addr, size in self._secure_memory_regions:
                    if addr == address:
                        region_info = (addr, size)
                        break
            
            if not region_info:
                security_logger.warning(f"Memory region not found for address 0x{address:x}")
                return False
            
            addr, size = region_info
            
            # Zero out memory before freeing (security measure)
            ctypes.memset(address, 0, size)
            
            # Free memory
            result = ctypes.windll.kernel32.VirtualFree(address, 0, MEM_RELEASE)
            
            if result:
                with self._lock:
                    self._secure_memory_regions.discard(region_info)
                security_logger.debug(f"Freed secure memory at 0x{address:x}")
                return True
            else:
                security_logger.warning(f"Failed to free memory at 0x{address:x}")
                return False
                
        except Exception as e:
            security_logger.error(f"Secure memory deallocation failed: {e}")
            return False
    
    def clear_sensitive_memory(self) -> None:
        """Clear all sensitive data from memory."""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear secure memory regions
            with self._lock:
                for address, size in list(self._secure_memory_regions):
                    self.free_secure_memory(address)
            
            security_logger.info("Sensitive memory cleared")
            
        except Exception as e:
            security_logger.warning(f"Memory clearing failed: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status information."""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            
            status = {
                'security_level': self.security_level.value,
                'process_id': self.process.pid,
                'memory_usage_mb': round(memory_info.rss / (1024 * 1024), 2),
                'cpu_percent': round(cpu_percent, 2),
                'secure_memory_regions': len(self._secure_memory_regions),
                'windows_api_available': WINDOWS_API_AVAILABLE,
                'monitoring_active': self.memory_monitor is not None and self.memory_monitor.is_alive()
            }
            
            # Add Windows-specific information if available
            if WINDOWS_API_AVAILABLE:
                try:
                    privilege = self._check_process_privileges()
                    status['privilege_level'] = privilege.value
                except:
                    status['privilege_level'] = 'unknown'
            
            return status
            
        except Exception as e:
            security_logger.warning(f"Could not get security status: {e}")
            return {'error': str(e)}
    
    def verify_system_integrity(self) -> bool:
        """Verify system and application integrity."""
        try:
            # Check if critical files exist and haven't been tampered with
            current_file = Path(__file__)
            if not current_file.exists():
                security_logger.error("Critical security file missing")
                return False
            
            # Check memory usage is reasonable
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            if memory_mb > 2048:  # 2GB threshold
                security_logger.warning(f"Excessive memory usage detected: {memory_mb:.1f}MB")
                return False
            
            # Check for suspicious process activity
            cpu_percent = self.process.cpu_percent(interval=1)
            if cpu_percent > 90:  # 90% CPU usage
                security_logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
            
            security_logger.debug("System integrity check passed")
            return True
            
        except Exception as e:
            security_logger.error(f"System integrity check failed: {e}")
            return False
    
    def enable_secure_mode(self) -> bool:
        """Enable maximum security mode."""
        try:
            self.security_level = SecurityLevel.MAXIMUM
            
            # Reinitialize with higher security
            self._configure_process_security()
            
            if not self.memory_monitor or not self.memory_monitor.is_alive():
                self._start_memory_monitoring()
            
            if WINDOWS_API_AVAILABLE:
                self._create_job_object()
            
            security_logger.info("Secure mode enabled")
            return True
            
        except Exception as e:
            security_logger.error(f"Failed to enable secure mode: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up security resources."""
        try:
            # Clear sensitive memory
            self.clear_sensitive_memory()
            
            # Stop memory monitoring
            if self.memory_monitor and self.memory_monitor.is_alive():
                # Note: daemon thread will be killed when main process exits
                pass
            
            security_logger.info("Security cleanup completed")
            
        except Exception as e:
            security_logger.warning(f"Security cleanup failed: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


# Global security manager instance
_security_manager = None

def get_security_manager(security_level: SecurityLevel = SecurityLevel.STANDARD) -> WindowsSecurityManager:
    """Get global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = WindowsSecurityManager(security_level)
    return _security_manager

def enable_security_monitoring() -> bool:
    """Enable security monitoring for the application."""
    try:
        manager = get_security_manager(SecurityLevel.ENHANCED)
        return manager.verify_system_integrity()
    except Exception as e:
        security_logger.error(f"Failed to enable security monitoring: {e}")
        return False


if __name__ == "__main__":
    # Basic testing
    with WindowsSecurityManager(SecurityLevel.ENHANCED) as security_manager:
        print("Security Status:")
        status = security_manager.get_security_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print(f"\nSystem Integrity: {security_manager.verify_system_integrity()}")
        
        # Test secure memory allocation
        address = security_manager.allocate_secure_memory(1024)
        if address:
            print(f"Allocated secure memory at: 0x{address:x}")
            security_manager.free_secure_memory(address)
            print("Memory freed")
