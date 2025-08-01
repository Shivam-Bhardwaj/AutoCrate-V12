#!/usr/bin/env python3
"""
AutoCrate Secure File Manager

Provides secure file operations with Windows-specific permission handling,
temporary file management, and protection against file system attacks.
"""

import os
import stat
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from contextlib import contextmanager
import threading
import time
import hashlib
import json
from enum import Enum

# Windows-specific imports
try:
    import win32security
    import win32api
    import win32con
    import win32file
    import ntsecuritycon
    WINDOWS_SECURITY_AVAILABLE = True
except ImportError:
    WINDOWS_SECURITY_AVAILABLE = False
    logging.warning("Windows security modules not available - using basic file operations")

from .input_validator import SecurityValidator, ValidationError

# Configure security logging
security_logger = logging.getLogger('AutoCrate.Security.FileManager')


class FilePermission(Enum):
    """File permission levels."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_CONTROL = "full_control"
    NO_ACCESS = "no_access"


class SecureFileManager:
    """Secure file operations manager for Windows."""
    
    def __init__(self, base_directory: Optional[Union[str, Path]] = None):
        """Initialize secure file manager."""
        self.validator = SecurityValidator()
        self.lock = threading.RLock()
        self._temp_files = set()
        self._active_handles = {}
        
        # Set base directory for file operations
        if base_directory:
            self.base_directory = self.validator.validate_filepath(str(base_directory))
        else:
            self.base_directory = Path.cwd()
        
        # Ensure base directory exists and is secure
        self._ensure_secure_directory(self.base_directory)
        
        security_logger.info(f"SecureFileManager initialized with base: {self.base_directory}")
    
    def create_secure_temp_file(self, suffix: str = ".tmp", prefix: str = "autocrate_") -> Path:
        """Create a secure temporary file."""
        with self.lock:
            try:
                # Validate suffix
                clean_suffix = self.validator.validate_filename(f"temp{suffix}").replace("temp", "")
                clean_prefix = self.validator.sanitize_nx_variable_name(prefix)
                
                # Create temporary file with secure permissions
                fd, temp_path = tempfile.mkstemp(
                    suffix=clean_suffix,
                    prefix=clean_prefix,
                    dir=self._get_secure_temp_dir()
                )
                
                # Close the file descriptor (we'll use Path operations)
                os.close(fd)
                
                temp_path_obj = Path(temp_path)
                
                # Set secure permissions
                self._set_secure_permissions(temp_path_obj, FilePermission.READ_WRITE)
                
                # Track temporary file
                self._temp_files.add(temp_path_obj)
                
                security_logger.info(f"Created secure temp file: {temp_path_obj}")
                return temp_path_obj
                
            except Exception as e:
                security_logger.error(f"Failed to create secure temp file: {e}")
                raise ValidationError(f"Cannot create secure temporary file: {e}")
    
    def write_expression_file(self, filepath: Union[str, Path], content: str, 
                            backup: bool = True) -> Path:
        """Securely write NX expression file."""
        with self.lock:
            try:
                # Validate and sanitize filepath
                if isinstance(filepath, str):
                    secure_path = self.validator.validate_filepath(filepath)
                else:
                    secure_path = filepath
                
                # Ensure the path is within our safe boundaries
                self._check_path_boundaries(secure_path)
                
                # Validate content
                if not isinstance(content, str):
                    raise ValidationError("File content must be string")
                
                if len(content) > 10 * 1024 * 1024:  # 10MB limit
                    raise ValidationError("File content too large")
                
                # Create backup if requested and file exists
                if backup and secure_path.exists():
                    self._create_backup(secure_path)
                
                # Ensure parent directory exists and is secure
                secure_path.parent.mkdir(parents=True, exist_ok=True)
                self._ensure_secure_directory(secure_path.parent)
                
                # Write to temporary file first (atomic operation)
                temp_file = self.create_secure_temp_file(suffix=".exp.tmp")
                
                try:
                    with open(temp_file, 'w', encoding='utf-8', newline='\r\n') as f:
                        f.write(content)
                        f.flush()
                        os.fsync(f.fileno())  # Force write to disk
                    
                    # Set secure permissions on temp file
                    self._set_secure_permissions(temp_file, FilePermission.READ_ONLY)
                    
                    # Atomic move to final location
                    shutil.move(str(temp_file), str(secure_path))
                    
                    # Remove from temp files tracking (moved to final location)
                    self._temp_files.discard(temp_file)
                    
                    # Set final permissions
                    self._set_secure_permissions(secure_path, FilePermission.READ_ONLY)
                    
                    # Log successful write
                    file_hash = self._calculate_file_hash(secure_path)
                    security_logger.info(
                        f"Expression file written securely: {secure_path} "
                        f"(size: {secure_path.stat().st_size}, hash: {file_hash[:16]}...)"
                    )
                    
                    return secure_path
                    
                except Exception as e:
                    # Clean up temp file on error
                    if temp_file.exists():
                        self._secure_delete_file(temp_file)
                    raise
                
            except Exception as e:
                security_logger.error(f"Failed to write expression file {filepath}: {e}")
                raise ValidationError(f"Cannot write expression file: {e}")
    
    def read_file_safely(self, filepath: Union[str, Path], max_size: int = 1024*1024) -> str:
        """Safely read file with size limits and validation."""
        try:
            # Validate filepath
            if isinstance(filepath, str):
                secure_path = self.validator.validate_filepath(filepath)
            else:
                secure_path = filepath
            
            # Check path boundaries
            self._check_path_boundaries(secure_path)
            
            # Check if file exists and is readable
            if not secure_path.exists():
                raise ValidationError(f"File does not exist: {secure_path}")
            
            if not secure_path.is_file():
                raise ValidationError(f"Path is not a file: {secure_path}")
            
            # Check file size
            file_size = secure_path.stat().st_size
            if file_size > max_size:
                raise ValidationError(f"File too large: {file_size} > {max_size}")
            
            # Read file securely
            with open(secure_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            security_logger.debug(f"File read safely: {secure_path} ({file_size} bytes)")
            return content
            
        except Exception as e:
            security_logger.error(f"Failed to read file {filepath}: {e}")
            raise ValidationError(f"Cannot read file safely: {e}")
    
    def create_secure_directory(self, dirpath: Union[str, Path], 
                              permission: FilePermission = FilePermission.READ_WRITE) -> Path:
        """Create directory with secure permissions."""
        try:
            # Validate directory path
            if isinstance(dirpath, str):
                secure_path = self.validator.validate_filepath(dirpath)
            else:
                secure_path = dirpath
            
            # Check path boundaries
            self._check_path_boundaries(secure_path)
            
            # Create directory
            secure_path.mkdir(parents=True, exist_ok=True)
            
            # Set secure permissions
            self._set_secure_permissions(secure_path, permission)
            
            security_logger.info(f"Secure directory created: {secure_path}")
            return secure_path
            
        except Exception as e:
            security_logger.error(f"Failed to create secure directory {dirpath}: {e}")
            raise ValidationError(f"Cannot create secure directory: {e}")
    
    def cleanup_temp_files(self) -> None:
        """Clean up all temporary files."""
        with self.lock:
            cleaned_count = 0
            for temp_file in list(self._temp_files):
                try:
                    if temp_file.exists():
                        self._secure_delete_file(temp_file)
                        cleaned_count += 1
                    self._temp_files.discard(temp_file)
                except Exception as e:
                    security_logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
            
            if cleaned_count > 0:
                security_logger.info(f"Cleaned up {cleaned_count} temporary files")
    
    def _ensure_secure_directory(self, directory: Path) -> None:
        """Ensure directory exists and has secure permissions."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self._set_secure_permissions(directory, FilePermission.READ_WRITE)
        except Exception as e:
            security_logger.warning(f"Could not secure directory {directory}: {e}")
    
    def _get_secure_temp_dir(self) -> Path:
        """Get secure temporary directory."""
        # Use a subdirectory of the base directory for temp files
        temp_dir = self.base_directory / "temp"
        self._ensure_secure_directory(temp_dir)
        return temp_dir
    
    def _check_path_boundaries(self, path: Path) -> None:
        """Check if path is within safe boundaries."""
        try:
            resolved_path = path.resolve()
            base_resolved = self.base_directory.resolve()
            
            # Allow files in base directory or standard Windows locations
            safe_roots = [
                base_resolved,
                Path(os.environ.get('USERPROFILE', 'C:\\Users\\Default')),
                Path('C:\\ProgramData\\AutoCrate'),
                Path(tempfile.gettempdir())
            ]
            
            is_safe = any(
                str(resolved_path).startswith(str(root.resolve()))
                for root in safe_roots
                if root.exists()
            )
            
            if not is_safe:
                raise ValidationError(f"Path outside safe boundaries: {resolved_path}")
                
        except Exception as e:
            raise ValidationError(f"Path boundary check failed: {e}")
    
    def _set_secure_permissions(self, path: Path, permission: FilePermission) -> None:
        """Set secure file permissions (Windows-specific when available)."""
        try:
            if WINDOWS_SECURITY_AVAILABLE:
                self._set_windows_permissions(path, permission)
            else:
                self._set_basic_permissions(path, permission)
        except Exception as e:
            security_logger.warning(f"Could not set secure permissions on {path}: {e}")
    
    def _set_windows_permissions(self, path: Path, permission: FilePermission) -> None:
        """Set Windows-specific ACL permissions."""
        try:
            # Get current user SID
            username = win32api.GetUserName()
            user_sid, domain, type = win32security.LookupAccountName("", username)
            
            # Create security descriptor
            sd = win32security.GetFileSecurity(str(path), win32security.DACL_SECURITY_INFORMATION)
            dacl = sd.GetSecurityDescriptorDacl()
            
            # Set permissions based on level
            if permission == FilePermission.READ_ONLY:
                access_rights = ntsecuritycon.FILE_GENERIC_READ
            elif permission == FilePermission.READ_WRITE:
                access_rights = (ntsecuritycon.FILE_GENERIC_READ | 
                               ntsecuritycon.FILE_GENERIC_WRITE)
            elif permission == FilePermission.FULL_CONTROL:
                access_rights = ntsecuritycon.FILE_ALL_ACCESS
            else:  # NO_ACCESS
                access_rights = 0
            
            # Add ACE for current user
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, access_rights, user_sid)
            
            # Set the updated DACL
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(str(path), win32security.DACL_SECURITY_INFORMATION, sd)
            
            security_logger.debug(f"Windows permissions set: {path} -> {permission.value}")
            
        except Exception as e:
            security_logger.warning(f"Windows permission setting failed: {e}")
            # Fall back to basic permissions
            self._set_basic_permissions(path, permission)
    
    def _set_basic_permissions(self, path: Path, permission: FilePermission) -> None:
        """Set basic file permissions using os.chmod."""
        try:
            if permission == FilePermission.READ_ONLY:
                mode = stat.S_IREAD
            elif permission == FilePermission.READ_WRITE:
                mode = stat.S_IREAD | stat.S_IWRITE
            elif permission == FilePermission.FULL_CONTROL:
                mode = stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC
            else:  # NO_ACCESS
                mode = 0
            
            path.chmod(mode)
            security_logger.debug(f"Basic permissions set: {path} -> {oct(mode)}")
            
        except Exception as e:
            security_logger.warning(f"Basic permission setting failed: {e}")
    
    def _create_backup(self, filepath: Path) -> Path:
        """Create backup of existing file."""
        timestamp = int(time.time())
        backup_path = filepath.with_suffix(f"{filepath.suffix}.backup_{timestamp}")
        
        try:
            shutil.copy2(str(filepath), str(backup_path))
            self._set_secure_permissions(backup_path, FilePermission.READ_ONLY)
            security_logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            security_logger.warning(f"Could not create backup: {e}")
            raise
    
    def _secure_delete_file(self, filepath: Path) -> None:
        """Securely delete file (overwrite then delete)."""
        try:
            if filepath.exists() and filepath.is_file():
                # Get file size
                file_size = filepath.stat().st_size
                
                # Overwrite with random data
                with open(filepath, 'r+b') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
                
                # Delete file
                filepath.unlink()
                security_logger.debug(f"File securely deleted: {filepath}")
                
        except Exception as e:
            security_logger.warning(f"Secure delete failed for {filepath}: {e}")
            # Try regular delete as fallback
            try:
                filepath.unlink()
            except:
                pass
    
    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA-256 hash of file for integrity checking."""
        try:
            hasher = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            security_logger.warning(f"Hash calculation failed for {filepath}: {e}")
            return "unknown"
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.cleanup_temp_files()


@contextmanager
def secure_file_operation(base_directory: Optional[Union[str, Path]] = None):
    """Context manager for secure file operations."""
    manager = SecureFileManager(base_directory)
    try:
        yield manager
    finally:
        manager.cleanup_temp_files()


# Global file manager instance
_file_manager = None

def get_file_manager(base_directory: Optional[Union[str, Path]] = None) -> SecureFileManager:
    """Get global file manager instance."""
    global _file_manager
    if _file_manager is None:
        _file_manager = SecureFileManager(base_directory)
    return _file_manager

def write_expression_file_secure(filepath: Union[str, Path], content: str) -> Path:
    """Convenience function for secure expression file writing."""
    return get_file_manager().write_expression_file(filepath, content)


if __name__ == "__main__":
    # Basic testing
    with secure_file_operation() as fm:
        # Test temp file creation
        temp_file = fm.create_secure_temp_file(suffix=".exp")
        print(f"Created temp file: {temp_file}")
        
        # Test expression file writing
        test_content = "# AutoCrate Test Expression\nLength = 36.0\nWidth = 24.0\nHeight = 48.0\n"
        output_path = fm.write_expression_file("test_output.exp", test_content)
        print(f"Written expression file: {output_path}")
        
        # Test file reading
        read_content = fm.read_file_safely(output_path)
        print(f"Read content: {len(read_content)} characters")
