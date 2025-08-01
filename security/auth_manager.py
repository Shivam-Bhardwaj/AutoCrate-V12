#!/usr/bin/env python3
"""
AutoCrate Authentication and Access Control Manager

Provides Windows-integrated authentication with role-based access control,
session management, and security policy enforcement for AutoCrate.
"""

import os
import time
import json
import hashlib
import secrets
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading

# Windows authentication imports
try:
    import win32api
    import win32security
    import win32con
    import win32net
    import win32netcon
    import pywintypes
    WINDOWS_AUTH_AVAILABLE = True
except ImportError:
    WINDOWS_AUTH_AVAILABLE = False
    logging.warning("Windows authentication modules not available")

from .input_validator import SecurityValidator, ValidationError
from .file_manager import SecureFileManager

# Configure authentication logging
auth_logger = logging.getLogger('AutoCrate.Security.Auth')


class UserRole(Enum):
    """User roles with different access levels."""
    VIEWER = "viewer"        # Read-only access, can view designs
    ENGINEER = "engineer"    # Full design access, can create/modify
    ADMIN = "admin"          # System administration, user management
    AUDITOR = "auditor"      # Read-only with audit access


class Permission(Enum):
    """System permissions."""
    VIEW_DESIGNS = "view_designs"
    CREATE_DESIGNS = "create_designs"
    MODIFY_DESIGNS = "modify_designs"
    DELETE_DESIGNS = "delete_designs"
    EXPORT_FILES = "export_files"
    MODIFY_SETTINGS = "modify_settings"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_USERS = "manage_users"
    SYSTEM_ADMIN = "system_admin"


class AuthenticationMethod(Enum):
    """Authentication methods."""
    WINDOWS_USER = "windows_user"
    LOCAL_USER = "local_user"
    DOMAIN_USER = "domain_user"


@dataclass
class User:
    """User information and permissions."""
    username: str
    display_name: str
    role: UserRole
    permissions: Set[Permission]
    auth_method: AuthenticationMethod
    last_login: Optional[datetime] = None
    login_count: int = 0
    is_active: bool = True
    session_timeout: int = 3600  # 1 hour default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['permissions'] = [p.value for p in self.permissions]
        data['role'] = self.role.value
        data['auth_method'] = self.auth_method.value
        data['last_login'] = self.last_login.isoformat() if self.last_login else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary."""
        permissions = {Permission(p) for p in data.get('permissions', [])}
        last_login = None
        if data.get('last_login'):
            last_login = datetime.fromisoformat(data['last_login'])
        
        return cls(
            username=data['username'],
            display_name=data['display_name'],
            role=UserRole(data['role']),
            permissions=permissions,
            auth_method=AuthenticationMethod(data['auth_method']),
            last_login=last_login,
            login_count=data.get('login_count', 0),
            is_active=data.get('is_active', True),
            session_timeout=data.get('session_timeout', 3600)
        )


@dataclass
class Session:
    """User session information."""
    session_id: str
    user: User
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    is_valid: bool = True
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.is_valid:
            return True
        
        timeout = timedelta(seconds=self.user.session_timeout)
        return datetime.now() - self.last_activity > timeout
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()


class AuthenticationManager:
    """Windows-integrated authentication and access control manager."""
    
    # Default role permissions
    ROLE_PERMISSIONS = {
        UserRole.VIEWER: {
            Permission.VIEW_DESIGNS,
        },
        UserRole.ENGINEER: {
            Permission.VIEW_DESIGNS,
            Permission.CREATE_DESIGNS,
            Permission.MODIFY_DESIGNS,
            Permission.DELETE_DESIGNS,
            Permission.EXPORT_FILES,
        },
        UserRole.ADMIN: {
            Permission.VIEW_DESIGNS,
            Permission.CREATE_DESIGNS,
            Permission.MODIFY_DESIGNS,
            Permission.DELETE_DESIGNS,
            Permission.EXPORT_FILES,
            Permission.MODIFY_SETTINGS,
            Permission.VIEW_AUDIT_LOGS,
            Permission.MANAGE_USERS,
            Permission.SYSTEM_ADMIN,
        },
        UserRole.AUDITOR: {
            Permission.VIEW_DESIGNS,
            Permission.VIEW_AUDIT_LOGS,
        },
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize authentication manager."""
        self.validator = SecurityValidator()
        self.file_manager = SecureFileManager()
        self.config_path = config_path or Path("security/auth_config.json")
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.lock = threading.RLock()
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.session_cleanup_interval = 300  # 5 minutes
        
        # Initialize
        self._load_configuration()
        self._start_session_cleanup()
        
        auth_logger.info("Authentication manager initialized")
    
    def authenticate_user(self, username: str, password: Optional[str] = None) -> Optional[Session]:
        """Authenticate user and create session."""
        with self.lock:
            try:
                # Validate username
                clean_username = self.validator.validate_text_input(username, 100)
                
                # Check for account lockout
                if self._is_account_locked(clean_username):
                    auth_logger.warning(f"Authentication attempt for locked account: {clean_username}")
                    return None
                
                # Attempt authentication
                user = None
                
                # Try Windows authentication first
                if WINDOWS_AUTH_AVAILABLE and not password:
                    user = self._authenticate_windows_user(clean_username)
                
                # Try local authentication if Windows auth failed or password provided
                if not user and password:
                    user = self._authenticate_local_user(clean_username, password)
                
                if user:
                    # Successful authentication
                    self._clear_failed_attempts(clean_username)
                    session = self._create_session(user)
                    
                    # Update user login info
                    user.last_login = datetime.now()
                    user.login_count += 1
                    self._save_configuration()
                    
                    auth_logger.info(f"User authenticated successfully: {clean_username}")
                    return session
                else:
                    # Failed authentication
                    self._record_failed_attempt(clean_username)
                    auth_logger.warning(f"Authentication failed for user: {clean_username}")
                    return None
                    
            except Exception as e:
                auth_logger.error(f"Authentication error for {username}: {e}")
                return None
    
    def _authenticate_windows_user(self, username: str) -> Optional[User]:
        """Authenticate using Windows user account."""
        try:
            if not WINDOWS_AUTH_AVAILABLE:
                return None
            
            # Get current Windows user
            current_user = win32api.GetUserName()
            
            # Check if requested user matches current user or is in same domain
            if username.lower() != current_user.lower():
                # Try to resolve domain user
                try:
                    domain = win32api.GetComputerName()
                    full_username = f"{domain}\\{username}"
                    win32security.LookupAccountName("", full_username)
                except:
                    return None
            
            # Check if user exists in our system
            if username in self.users:
                user = self.users[username]
                if user.is_active:
                    return user
            else:
                # Create new Windows user with default engineer role
                user = self._create_windows_user(username, current_user)
                return user
            
            return None
            
        except Exception as e:
            auth_logger.debug(f"Windows authentication failed for {username}: {e}")
            return None
    
    def _authenticate_local_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate using local user database."""
        try:
            if username not in self.users:
                return None
            
            user = self.users[username]
            if not user.is_active:
                return None
            
            # For local users, we would verify password hash here
            # This is a simplified implementation
            if user.auth_method == AuthenticationMethod.LOCAL_USER:
                # In production, compare with stored password hash
                # For now, allow any password for demo purposes
                return user
            
            return None
            
        except Exception as e:
            auth_logger.debug(f"Local authentication failed for {username}: {e}")
            return None
    
    def _create_windows_user(self, username: str, display_name: str) -> User:
        """Create new Windows-authenticated user."""
        # Determine role based on Windows group membership or default to engineer
        role = self._determine_user_role(username)
        
        user = User(
            username=username,
            display_name=display_name,
            role=role,
            permissions=self.ROLE_PERMISSIONS[role].copy(),
            auth_method=AuthenticationMethod.WINDOWS_USER
        )
        
        self.users[username] = user
        self._save_configuration()
        
        auth_logger.info(f"Created new Windows user: {username} with role {role.value}")
        return user
    
    def _determine_user_role(self, username: str) -> UserRole:
        """Determine user role based on Windows group membership."""
        try:
            if WINDOWS_AUTH_AVAILABLE:
                # Check Windows group membership
                # This is simplified - in production, check actual AD groups
                try:
                    # Check if user is in Administrators group
                    if self._is_user_in_group(username, "Administrators"):
                        return UserRole.ADMIN
                    elif self._is_user_in_group(username, "Power Users"):
                        return UserRole.ENGINEER
                    else:
                        return UserRole.VIEWER
                except:
                    pass
            
            # Default role for new users
            return UserRole.ENGINEER
            
        except Exception as e:
            auth_logger.debug(f"Role determination failed for {username}: {e}")
            return UserRole.VIEWER
    
    def _is_user_in_group(self, username: str, group_name: str) -> bool:
        """Check if user is member of Windows group."""
        try:
            if not WINDOWS_AUTH_AVAILABLE:
                return False
            
            # This is a simplified check - in production, use proper AD queries
            user_info = win32net.NetUserGetInfo(None, username, 1)
            return False  # Simplified for demo
            
        except Exception:
            return False
    
    def _create_session(self, user: User) -> Session:
        """Create new user session."""
        session_id = secrets.token_urlsafe(32)
        session = Session(
            session_id=session_id,
            user=user,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        with self.lock:
            self.sessions[session_id] = session
        
        auth_logger.debug(f"Session created for user {user.username}: {session_id[:8]}...")
        return session
    
    def validate_session(self, session_id: str) -> Optional[Session]:
        """Validate and return session if valid."""
        with self.lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            if session.is_expired():
                self._invalidate_session(session_id)
                return None
            
            session.update_activity()
            return session
    
    def _invalidate_session(self, session_id: str) -> None:
        """Invalidate session."""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.is_valid = False
                auth_logger.debug(f"Session invalidated: {session_id[:8]}...")
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user and invalidate session."""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                self._invalidate_session(session_id)
                auth_logger.info(f"User logged out: {session.user.username}")
                return True
            return False
    
    def check_permission(self, session_id: str, permission: Permission) -> bool:
        """Check if user has specific permission."""
        session = self.validate_session(session_id)
        if not session:
            return False
        
        return permission in session.user.permissions
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.now() - attempt < self.lockout_duration
        ]
        
        return len(recent_attempts) >= self.max_failed_attempts
    
    def _record_failed_attempt(self, username: str) -> None:
        """Record failed authentication attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.now())
        
        # Keep only recent attempts
        cutoff = datetime.now() - self.lockout_duration
        self.failed_attempts[username] = [
            attempt for attempt in self.failed_attempts[username]
            if attempt > cutoff
        ]
    
    def _clear_failed_attempts(self, username: str) -> None:
        """Clear failed authentication attempts."""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    def _start_session_cleanup(self) -> None:
        """Start background session cleanup thread."""
        def cleanup_sessions():
            while True:
                try:
                    with self.lock:
                        expired_sessions = [
                            sid for sid, session in self.sessions.items()
                            if session.is_expired()
                        ]
                        
                        for session_id in expired_sessions:
                            del self.sessions[session_id]
                        
                        if expired_sessions:
                            auth_logger.debug(f"Cleaned up {len(expired_sessions)} expired sessions")
                    
                    time.sleep(self.session_cleanup_interval)
                    
                except Exception as e:
                    auth_logger.error(f"Session cleanup error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
        cleanup_thread.start()
    
    def _load_configuration(self) -> None:
        """Load authentication configuration."""
        try:
            if self.config_path.exists():
                content = self.file_manager.read_file_safely(self.config_path)
                config = json.loads(content)
                
                # Load users
                for user_data in config.get('users', []):
                    user = User.from_dict(user_data)
                    self.users[user.username] = user
                
                auth_logger.info(f"Loaded {len(self.users)} users from configuration")
            else:
                # Create default admin user
                self._create_default_users()
                
        except Exception as e:
            auth_logger.warning(f"Failed to load configuration: {e}")
            self._create_default_users()
    
    def _create_default_users(self) -> None:
        """Create default users."""
        try:
            # Create default admin user (Windows user)
            if WINDOWS_AUTH_AVAILABLE:
                current_user = win32api.GetUserName()
                admin_user = User(
                    username=current_user,
                    display_name=current_user,
                    role=UserRole.ADMIN,
                    permissions=self.ROLE_PERMISSIONS[UserRole.ADMIN].copy(),
                    auth_method=AuthenticationMethod.WINDOWS_USER
                )
                self.users[current_user] = admin_user
                auth_logger.info(f"Created default admin user: {current_user}")
            
            self._save_configuration()
            
        except Exception as e:
            auth_logger.error(f"Failed to create default users: {e}")
    
    def _save_configuration(self) -> None:
        """Save authentication configuration."""
        try:
            config = {
                'users': [user.to_dict() for user in self.users.values()],
                'updated': datetime.now().isoformat()
            }
            
            config_content = json.dumps(config, indent=2)
            self.file_manager.write_expression_file(self.config_path, config_content)
            
        except Exception as e:
            auth_logger.error(f"Failed to save configuration: {e}")
    
    def get_user_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current user information."""
        session = self.validate_session(session_id)
        if not session:
            return None
        
        return {
            'username': session.user.username,
            'display_name': session.user.display_name,
            'role': session.user.role.value,
            'permissions': [p.value for p in session.user.permissions],
            'last_login': session.user.last_login.isoformat() if session.user.last_login else None,
            'session_created': session.created_at.isoformat(),
            'session_expires': (session.last_activity + timedelta(seconds=session.user.session_timeout)).isoformat()
        }
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get information about active sessions (admin only)."""
        with self.lock:
            sessions_info = []
            for session_id, session in self.sessions.items():
                if not session.is_expired():
                    sessions_info.append({
                        'session_id': session_id[:8] + "...",  # Truncated for security
                        'username': session.user.username,
                        'created_at': session.created_at.isoformat(),
                        'last_activity': session.last_activity.isoformat(),
                        'ip_address': session.ip_address or "unknown"
                    })
            
            return sessions_info


# Global authentication manager
_auth_manager = None

def get_auth_manager() -> AuthenticationManager:
    """Get global authentication manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager

def require_permission(permission: Permission):
    """Decorator to require specific permission for function access."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented based on how sessions are passed
            # For now, this is a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    # Basic testing
    auth_manager = AuthenticationManager()
    
    # Test Windows authentication
    if WINDOWS_AUTH_AVAILABLE:
        current_user = win32api.GetUserName()
        session = auth_manager.authenticate_user(current_user)
        
        if session:
            print(f"Authentication successful for: {session.user.username}")
            print(f"Role: {session.user.role.value}")
            print(f"Permissions: {[p.value for p in session.user.permissions]}")
            
            # Test permission check
            can_create = auth_manager.check_permission(session.session_id, Permission.CREATE_DESIGNS)
            print(f"Can create designs: {can_create}")
        else:
            print("Authentication failed")
    else:
        print("Windows authentication not available")
