#!/usr/bin/env python3
"""
AutoCrate Security Module

Comprehensive security framework providing input validation, secure file operations,
Windows authentication, audit logging, and process security for AutoCrate.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Import security components
from .input_validator import (
    SecurityValidator, ValidationError, InputType,
    validate_dimension, validate_weight, validate_filename, 
    validate_filepath, sanitize_for_nx
)

from .file_manager import (
    SecureFileManager, FilePermission, secure_file_operation,
    get_file_manager, write_expression_file_secure
)

from .windows_security import (
    WindowsSecurityManager, SecurityLevel, ProcessPrivilege,
    get_security_manager, enable_security_monitoring
)

from .auth_manager import (
    AuthenticationManager, User, Session, UserRole, Permission,
    AuthenticationMethod, get_auth_manager, require_permission
)

from .audit_logger import (
    SecurityAuditLogger, SecurityEvent, EventType, EventSeverity, EventOutcome,
    get_audit_logger, log_authentication_event, log_file_access_event, log_security_violation
)

# Configure security logging
security_logger = logging.getLogger('AutoCrate.Security')


class AutoCrateSecurityManager:
    """Integrated security manager for AutoCrate application."""
    
    def __init__(self, 
                 security_level: SecurityLevel = SecurityLevel.STANDARD,
                 enable_authentication: bool = True,
                 enable_audit_logging: bool = True,
                 config_path: Optional[Path] = None):
        """Initialize comprehensive security manager."""
        
        self.security_level = security_level
        self.enable_authentication = enable_authentication
        self.enable_audit_logging = enable_audit_logging
        self.config_path = config_path
        
        # Initialize security components
        self.validator = SecurityValidator()
        self.file_manager = get_file_manager()
        self.windows_security = get_security_manager(security_level)
        
        # Initialize authentication if enabled
        if enable_authentication:
            self.auth_manager = get_auth_manager()
        else:
            self.auth_manager = None
        
        # Initialize audit logging if enabled
        if enable_audit_logging:
            self.audit_logger = get_audit_logger()
            self._log_initialization()
        else:
            self.audit_logger = None
        
        security_logger.info(f"AutoCrate security manager initialized (level: {security_level.value})")
    
    def _log_initialization(self) -> None:
        """Log security initialization event."""
        if self.audit_logger:
            self.audit_logger.log_event(
                EventType.SYSTEM_ACCESS,
                EventSeverity.INFO,
                EventOutcome.SUCCESS,
                "AutoCrate security manager initialized",
                details={
                    'security_level': self.security_level.value,
                    'authentication_enabled': self.enable_authentication,
                    'audit_logging_enabled': self.enable_audit_logging
                }
            )
    
    def authenticate_user(self, username: str, password: Optional[str] = None) -> Optional[Session]:
        """Authenticate user and create session."""
        if not self.auth_manager:
            security_logger.warning("Authentication attempted but not enabled")
            return None
        
        session = self.auth_manager.authenticate_user(username, password)
        
        # Log authentication attempt
        if self.audit_logger:
            log_authentication_event(
                username=username,
                success=session is not None,
                session_id=session.session_id if session else None,
                details={'auth_method': 'integrated'}
            )
        
        return session
    
    def validate_session(self, session_id: str) -> Optional[Session]:
        """Validate user session."""
        if not self.auth_manager:
            return None
        
        session = self.auth_manager.validate_session(session_id)
        
        # Log session validation if it fails
        if not session and self.audit_logger:
            self.audit_logger.log_event(
                EventType.AUTHORIZATION,
                EventSeverity.LOW,
                EventOutcome.FAILURE,
                "Session validation failed",
                details={'session_id': session_id[:8] + "..."}
            )
        
        return session
    
    def check_permission(self, session_id: str, permission: Permission) -> bool:
        """Check user permission."""
        if not self.auth_manager:
            return True  # No authentication = full access
        
        has_permission = self.auth_manager.check_permission(session_id, permission)
        
        # Log permission check failures
        if not has_permission and self.audit_logger:
            session = self.auth_manager.validate_session(session_id)
            self.audit_logger.log_event(
                EventType.AUTHORIZATION,
                EventSeverity.MEDIUM,
                EventOutcome.FAILURE,
                f"Permission denied: {permission.value}",
                username=session.user.username if session else None,
                session_id=session_id,
                details={'permission': permission.value}
            )
        
        return has_permission
    
    def validate_input(self, value: Any, input_type: InputType, name: str = None) -> Any:
        """Validate user input with logging."""
        try:
            # Use appropriate validation method
            if input_type == InputType.DIMENSION:
                return self.validator.validate_dimension(value, name or "dimension")
            elif input_type == InputType.WEIGHT:
                return self.validator.validate_weight(value, name or "weight")
            elif input_type == InputType.THICKNESS:
                return self.validator.validate_thickness(value, name or "thickness")
            elif input_type == InputType.CLEARANCE:
                return self.validator.validate_clearance(value, name or "clearance")
            elif input_type == InputType.FILENAME:
                return self.validator.validate_filename(value)
            elif input_type == InputType.FILEPATH:
                return self.validator.validate_filepath(value)
            elif input_type == InputType.TEXT:
                return self.validator.validate_text_input(value)
            elif input_type == InputType.INTEGER:
                return self.validator.validate_integer(value)
            elif input_type == InputType.BOOLEAN:
                return self.validator.validate_boolean(value)
            else:
                raise ValidationError(f"Unknown input type: {input_type}")
                
        except ValidationError as e:
            # Log validation failure
            if self.audit_logger:
                log_security_violation(
                    f"Input validation failed: {e}",
                    details={
                        'input_type': input_type.value,
                        'input_value': str(value)[:100],  # Limit logged value length
                        'field_name': name
                    }
                )
            raise
    
    def write_secure_file(self, filepath: str, content: str, 
                         username: Optional[str] = None,
                         session_id: Optional[str] = None) -> Path:
        """Write file with security logging."""
        try:
            # Write file securely
            result_path = self.file_manager.write_expression_file(filepath, content)
            
            # Log successful file operation
            if self.audit_logger:
                log_file_access_event(
                    username=username or "system",
                    filepath=str(result_path),
                    operation="write",
                    success=True,
                    session_id=session_id
                )
            
            return result_path
            
        except Exception as e:
            # Log failed file operation
            if self.audit_logger:
                log_file_access_event(
                    username=username or "system",
                    filepath=filepath,
                    operation="write",
                    success=False,
                    session_id=session_id
                )
            raise
    
    def read_secure_file(self, filepath: str, 
                        username: Optional[str] = None,
                        session_id: Optional[str] = None) -> str:
        """Read file with security logging."""
        try:
            # Read file securely
            content = self.file_manager.read_file_safely(filepath)
            
            # Log successful file operation
            if self.audit_logger:
                log_file_access_event(
                    username=username or "system",
                    filepath=filepath,
                    operation="read",
                    success=True,
                    session_id=session_id
                )
            
            return content
            
        except Exception as e:
            # Log failed file operation
            if self.audit_logger:
                log_file_access_event(
                    username=username or "system",
                    filepath=filepath,
                    operation="read",
                    success=False,
                    session_id=session_id
                )
            raise
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status."""
        status = {
            'security_level': self.security_level.value,
            'authentication_enabled': self.enable_authentication,
            'audit_logging_enabled': self.enable_audit_logging,
            'components': {}
        }
        
        # Windows security status
        if self.windows_security:
            status['components']['windows_security'] = self.windows_security.get_security_status()
        
        # Authentication status
        if self.auth_manager:
            active_sessions = self.auth_manager.get_active_sessions()
            status['components']['authentication'] = {
                'active_sessions': len(active_sessions),
                'total_users': len(self.auth_manager.users)
            }
        
        # System integrity check
        if self.windows_security:
            status['system_integrity'] = self.windows_security.verify_system_integrity()
        
        return status
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        report = {
            'generated_at': str(datetime.now()),
            'security_status': self.get_security_status()
        }
        
        # Add audit report if available
        if self.audit_logger:
            audit_report = self.audit_logger.generate_audit_report()
            report['audit_summary'] = audit_report
        
        return report
    
    def enable_secure_mode(self) -> bool:
        """Enable maximum security mode."""
        try:
            # Enable enhanced Windows security
            if self.windows_security:
                self.windows_security.enable_secure_mode()
            
            self.security_level = SecurityLevel.MAXIMUM
            
            # Log security mode change
            if self.audit_logger:
                self.audit_logger.log_event(
                    EventType.CONFIGURATION_CHANGE,
                    EventSeverity.HIGH,
                    EventOutcome.SUCCESS,
                    "Secure mode enabled",
                    details={'new_level': SecurityLevel.MAXIMUM.value}
                )
            
            security_logger.info("Secure mode enabled")
            return True
            
        except Exception as e:
            security_logger.error(f"Failed to enable secure mode: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up security resources."""
        try:
            # Clean up Windows security
            if self.windows_security:
                self.windows_security.cleanup()
            
            # Clean up file manager
            if self.file_manager:
                self.file_manager.cleanup_temp_files()
            
            # Clean up audit logger
            if self.audit_logger:
                self.audit_logger.cleanup()
            
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

def initialize_security(security_level: SecurityLevel = SecurityLevel.STANDARD,
                       enable_authentication: bool = True,
                       enable_audit_logging: bool = True,
                       config_path: Optional[Path] = None) -> AutoCrateSecurityManager:
    """Initialize AutoCrate security system."""
    global _security_manager
    
    if _security_manager is None:
        _security_manager = AutoCrateSecurityManager(
            security_level=security_level,
            enable_authentication=enable_authentication,
            enable_audit_logging=enable_audit_logging,
            config_path=config_path
        )
    
    return _security_manager

def get_security_manager() -> Optional[AutoCrateSecurityManager]:
    """Get the global security manager instance."""
    return _security_manager

def require_authentication(func):
    """Decorator to require authentication for function access."""
    def wrapper(*args, **kwargs):
        security_manager = get_security_manager()
        if security_manager and security_manager.enable_authentication:
            # Implementation would depend on how session info is passed
            # This is a placeholder for the concept
            pass
        return func(*args, **kwargs)
    return wrapper

def require_permission_decorator(permission: Permission):
    """Decorator to require specific permission for function access."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            security_manager = get_security_manager()
            if security_manager and security_manager.enable_authentication:
                # Implementation would depend on how session info is passed
                # This is a placeholder for the concept
                pass
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Public API exports
__all__ = [
    # Core classes
    'AutoCrateSecurityManager',
    'SecurityValidator', 'SecureFileManager', 'WindowsSecurityManager',
    'AuthenticationManager', 'SecurityAuditLogger',
    
    # Enums
    'SecurityLevel', 'UserRole', 'Permission', 'EventType', 'EventSeverity', 'InputType',
    
    # Data classes
    'User', 'Session', 'SecurityEvent',
    
    # Exceptions
    'ValidationError',
    
    # Convenience functions
    'initialize_security', 'get_security_manager',
    'validate_dimension', 'validate_weight', 'validate_filename', 'sanitize_for_nx',
    'write_expression_file_secure', 'enable_security_monitoring',
    'log_authentication_event', 'log_file_access_event', 'log_security_violation',
    
    # Decorators
    'require_authentication', 'require_permission_decorator', 'require_permission'
]


if __name__ == "__main__":
    # Basic testing
    with initialize_security(SecurityLevel.ENHANCED) as security_manager:
        print("Security Status:")
        status = security_manager.get_security_status()
        print(json.dumps(status, indent=2, default=str))
        
        # Test input validation
        try:
            length = security_manager.validate_input(36.5, InputType.DIMENSION, "length")
            print(f"Validated dimension: {length}")
            
            filename = security_manager.validate_input("test_crate.exp", InputType.FILENAME)
            print(f"Validated filename: {filename}")
            
        except ValidationError as e:
            print(f"Validation error: {e}")
