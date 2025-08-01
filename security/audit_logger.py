#!/usr/bin/env python3
"""
AutoCrate Security Audit Logger

Provides comprehensive security event logging with Windows Event Log integration,
tamper-proof audit trails, and compliance reporting for AutoCrate.
"""

import os
import json
import logging
import logging.handlers
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import threading
import hashlib
import hmac
import secrets

# Windows Event Log imports
try:
    import win32evtlog
    import win32evtlogutil
    import win32con
    import win32api
    WINDOWS_EVENTLOG_AVAILABLE = True
except ImportError:
    WINDOWS_EVENTLOG_AVAILABLE = False
    logging.warning("Windows Event Log modules not available")

from .input_validator import SecurityValidator, ValidationError
from .file_manager import SecureFileManager

# Configure audit logging
audit_logger = logging.getLogger('AutoCrate.Security.Audit')


class EventType(Enum):
    """Security event types."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    FILE_ACCESS = "file_access"
    SYSTEM_ACCESS = "system_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class EventSeverity(Enum):
    """Event severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventOutcome(Enum):
    """Event outcome status."""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    UNKNOWN = "unknown"


@dataclass
class SecurityEvent:
    """Security event record."""
    timestamp: datetime
    event_type: EventType
    severity: EventSeverity
    outcome: EventOutcome
    username: Optional[str]
    session_id: Optional[str]
    description: str
    details: Dict[str, Any]
    source_ip: Optional[str] = None
    process_id: Optional[int] = None
    thread_id: Optional[int] = None
    event_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate event ID after initialization."""
        if not self.event_id:
            self.event_id = self._generate_event_id()
        
        if not self.process_id:
            self.process_id = os.getpid()
        
        if not self.thread_id:
            self.thread_id = threading.get_ident()
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        event_data = f"{self.timestamp.isoformat()}{self.username}{self.description}"
        return hashlib.sha256(event_data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['outcome'] = self.outcome.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityEvent':
        """Create SecurityEvent from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            event_type=EventType(data['event_type']),
            severity=EventSeverity(data['severity']),
            outcome=EventOutcome(data['outcome']),
            username=data.get('username'),
            session_id=data.get('session_id'),
            description=data['description'],
            details=data.get('details', {}),
            source_ip=data.get('source_ip'),
            process_id=data.get('process_id'),
            thread_id=data.get('thread_id'),
            event_id=data.get('event_id')
        )


class SecurityAuditLogger:
    """Comprehensive security audit logging system."""
    
    def __init__(self, log_directory: Optional[Path] = None, 
                 enable_windows_eventlog: bool = True,
                 enable_tamper_protection: bool = True):
        """Initialize security audit logger."""
        self.validator = SecurityValidator()
        self.file_manager = SecureFileManager()
        self.log_directory = log_directory or Path("security/logs")
        self.enable_windows_eventlog = enable_windows_eventlog and WINDOWS_EVENTLOG_AVAILABLE
        self.enable_tamper_protection = enable_tamper_protection
        
        # Create secure log directory
        self.file_manager.create_secure_directory(self.log_directory)
        
        # Initialize logging components
        self._init_file_logging()
        self._init_windows_eventlog()
        self._init_tamper_protection()
        
        # Event queue for batch processing
        self.event_queue = []
        self.queue_lock = threading.RLock()
        self.batch_size = 100
        self.flush_interval = 60  # seconds
        
        # Start background processing
        self._start_background_processing()
        
        audit_logger.info("Security audit logger initialized")
        self.log_event(
            EventType.SYSTEM_ACCESS,
            EventSeverity.INFO,
            EventOutcome.SUCCESS,
            "Security audit logger started",
            details={'component': 'SecurityAuditLogger'}
        )
    
    def _init_file_logging(self) -> None:
        """Initialize file-based logging."""
        try:
            # Create rotating log file handler
            log_file = self.log_directory / "security_audit.log"
            
            # Use rotating file handler (10MB max, 5 backups)
            self.file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            
            # Set secure permissions on log files
            if log_file.exists():
                from .file_manager import FilePermission
                self.file_manager._set_secure_permissions(log_file, FilePermission.READ_WRITE)
            
            # JSON formatter for structured logging
            formatter = logging.Formatter('%(message)s')
            self.file_handler.setFormatter(formatter)
            
            audit_logger.info("File logging initialized")
            
        except Exception as e:
            audit_logger.error(f"Failed to initialize file logging: {e}")
    
    def _init_windows_eventlog(self) -> None:
        """Initialize Windows Event Log integration."""
        try:
            if self.enable_windows_eventlog:
                # Register AutoCrate as event source
                self.event_source = "AutoCrate Security"
                
                try:
                    win32evtlogutil.AddSourceToRegistry(
                        self.event_source,
                        "Application",
                        "C:\\Windows\\System32\\EventCreate.exe"  # Use system event creator
                    )
                except Exception as e:
                    audit_logger.debug(f"Event source registration note: {e}")
                
                audit_logger.info("Windows Event Log integration enabled")
            else:
                audit_logger.info("Windows Event Log integration disabled")
                
        except Exception as e:
            audit_logger.warning(f"Windows Event Log initialization failed: {e}")
            self.enable_windows_eventlog = False
    
    def _init_tamper_protection(self) -> None:
        """Initialize tamper protection for audit logs."""
        try:
            if self.enable_tamper_protection:
                # Generate or load signing key
                key_file = self.log_directory / ".audit_key"
                
                if key_file.exists():
                    self.signing_key = self.file_manager.read_file_safely(key_file).encode()
                else:
                    self.signing_key = secrets.token_bytes(32)
                    key_content = self.signing_key.hex()
                    self.file_manager.write_expression_file(key_file, key_content)
                    
                    # Hide and protect key file
                    if os.name == 'nt':
                        os.system(f'attrib +h "{key_file}"')  # Hide file on Windows
                
                audit_logger.info("Tamper protection initialized")
            else:
                self.signing_key = None
                
        except Exception as e:
            audit_logger.warning(f"Tamper protection initialization failed: {e}")
            self.enable_tamper_protection = False
            self.signing_key = None
    
    def log_event(self, event_type: EventType, severity: EventSeverity, 
                  outcome: EventOutcome, description: str,
                  username: Optional[str] = None, session_id: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  source_ip: Optional[str] = None) -> str:
        """Log security event."""
        try:
            # Validate inputs
            clean_description = self.validator.validate_text_input(description, 1000)
            
            if username:
                username = self.validator.validate_text_input(username, 100)
            
            if session_id:
                session_id = self.validator.validate_text_input(session_id, 100)
            
            # Create event
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type=event_type,
                severity=severity,
                outcome=outcome,
                username=username,
                session_id=session_id,
                description=clean_description,
                details=details or {},
                source_ip=source_ip
            )
            
            # Add to queue for processing
            with self.queue_lock:
                self.event_queue.append(event)
            
            # Immediate processing for critical events
            if severity in [EventSeverity.CRITICAL, EventSeverity.HIGH]:
                self._process_event_immediately(event)
            
            return event.event_id
            
        except Exception as e:
            audit_logger.error(f"Failed to log security event: {e}")
            return ""
    
    def _process_event_immediately(self, event: SecurityEvent) -> None:
        """Process high-priority event immediately."""
        try:
            self._write_to_file([event])
            self._write_to_windows_eventlog(event)
            
        except Exception as e:
            audit_logger.error(f"Immediate event processing failed: {e}")
    
    def _start_background_processing(self) -> None:
        """Start background event processing thread."""
        def process_events():
            """Background event processing."""
            while True:
                try:
                    events_to_process = []
                    
                    with self.queue_lock:
                        if len(self.event_queue) >= self.batch_size:
                            events_to_process = self.event_queue[:self.batch_size]
                            self.event_queue = self.event_queue[self.batch_size:]
                    
                    if events_to_process:
                        self._process_event_batch(events_to_process)
                    
                    time.sleep(self.flush_interval)
                    
                    # Periodic flush of remaining events
                    with self.queue_lock:
                        if self.event_queue:
                            remaining_events = self.event_queue.copy()
                            self.event_queue.clear()
                            self._process_event_batch(remaining_events)
                    
                except Exception as e:
                    audit_logger.error(f"Background processing error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        processing_thread = threading.Thread(target=process_events, daemon=True)
        processing_thread.start()
    
    def _process_event_batch(self, events: List[SecurityEvent]) -> None:
        """Process batch of events."""
        try:
            self._write_to_file(events)
            
            # Write high-priority events to Windows Event Log
            for event in events:
                if event.severity in [EventSeverity.CRITICAL, EventSeverity.HIGH]:
                    self._write_to_windows_eventlog(event)
            
        except Exception as e:
            audit_logger.error(f"Batch processing failed: {e}")
    
    def _write_to_file(self, events: List[SecurityEvent]) -> None:
        """Write events to log file."""
        try:
            log_entries = []
            
            for event in events:
                # Create log entry
                log_entry = event.to_dict()
                
                # Add tamper protection signature if enabled
                if self.enable_tamper_protection and self.signing_key:
                    signature = self._sign_event(log_entry)
                    log_entry['signature'] = signature
                
                log_entries.append(json.dumps(log_entry))
            
            # Write to file
            log_content = '\n'.join(log_entries) + '\n'
            
            # Append to current log file
            log_file = self.log_directory / "security_audit.log"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_content)
                f.flush()
                os.fsync(f.fileno())
            
        except Exception as e:
            audit_logger.error(f"File writing failed: {e}")
    
    def _write_to_windows_eventlog(self, event: SecurityEvent) -> None:
        """Write event to Windows Event Log."""
        try:
            if not self.enable_windows_eventlog:
                return
            
            # Map severity to Windows event type
            if event.severity == EventSeverity.CRITICAL:
                event_type = win32evtlog.EVENTLOG_ERROR_TYPE
            elif event.severity == EventSeverity.HIGH:
                event_type = win32evtlog.EVENTLOG_WARNING_TYPE
            else:
                event_type = win32evtlog.EVENTLOG_INFORMATION_TYPE
            
            # Create event message
            message = (
                f"AutoCrate Security Event\n"
                f"Type: {event.event_type.value}\n"
                f"User: {event.username or 'Unknown'}\n"
                f"Description: {event.description}\n"
                f"Details: {json.dumps(event.details, indent=2)}"
            )
            
            # Write to event log
            win32evtlogutil.ReportEvent(
                self.event_source,
                1000,  # Event ID
                eventType=event_type,
                strings=[message]
            )
            
        except Exception as e:
            audit_logger.debug(f"Windows Event Log writing failed: {e}")
    
    def _sign_event(self, event_data: Dict[str, Any]) -> str:
        """Create tamper-proof signature for event."""
        try:
            # Create canonical representation
            event_string = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
            
            # Create HMAC signature
            signature = hmac.new(
                self.signing_key,
                event_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            audit_logger.error(f"Event signing failed: {e}")
            return ""
    
    def verify_event_integrity(self, event_data: Dict[str, Any]) -> bool:
        """Verify event integrity using signature."""
        try:
            if not self.enable_tamper_protection or not self.signing_key:
                return True  # No tamper protection enabled
            
            stored_signature = event_data.pop('signature', '')
            if not stored_signature:
                return False  # No signature found
            
            calculated_signature = self._sign_event(event_data)
            return hmac.compare_digest(stored_signature, calculated_signature)
            
        except Exception as e:
            audit_logger.error(f"Event verification failed: {e}")
            return False
    
    def search_events(self, start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     event_type: Optional[EventType] = None,
                     username: Optional[str] = None,
                     severity: Optional[EventSeverity] = None,
                     limit: int = 1000) -> List[SecurityEvent]:
        """Search audit events with filters."""
        try:
            events = []
            log_file = self.log_directory / "security_audit.log"
            
            if not log_file.exists():
                return events
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    if line_num >= limit:
                        break
                    
                    try:
                        event_data = json.loads(line.strip())
                        
                        # Verify integrity if tamper protection is enabled
                        if self.enable_tamper_protection:
                            if not self.verify_event_integrity(event_data.copy()):
                                audit_logger.warning(f"Tampered event detected at line {line_num + 1}")
                                continue
                        
                        event = SecurityEvent.from_dict(event_data)
                        
                        # Apply filters
                        if start_time and event.timestamp < start_time:
                            continue
                        if end_time and event.timestamp > end_time:
                            continue
                        if event_type and event.event_type != event_type:
                            continue
                        if username and event.username != username:
                            continue
                        if severity and event.severity != severity:
                            continue
                        
                        events.append(event)
                        
                    except json.JSONDecodeError:
                        audit_logger.warning(f"Invalid JSON in audit log at line {line_num + 1}")
                        continue
            
            return events
            
        except Exception as e:
            audit_logger.error(f"Event search failed: {e}")
            return []
    
    def generate_audit_report(self, start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        try:
            if not start_time:
                start_time = datetime.now() - timedelta(days=30)  # Last 30 days
            if not end_time:
                end_time = datetime.now()
            
            events = self.search_events(start_time=start_time, end_time=end_time)
            
            # Generate statistics
            report = {
                'report_period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'total_events': len(events),
                'events_by_type': {},
                'events_by_severity': {},
                'events_by_outcome': {},
                'events_by_user': {},
                'security_incidents': [],
                'generated_at': datetime.now().isoformat()
            }
            
            # Analyze events
            for event in events:
                # Count by type
                event_type = event.event_type.value
                report['events_by_type'][event_type] = report['events_by_type'].get(event_type, 0) + 1
                
                # Count by severity
                severity = event.severity.value
                report['events_by_severity'][severity] = report['events_by_severity'].get(severity, 0) + 1
                
                # Count by outcome
                outcome = event.outcome.value
                report['events_by_outcome'][outcome] = report['events_by_outcome'].get(outcome, 0) + 1
                
                # Count by user
                username = event.username or 'Unknown'
                report['events_by_user'][username] = report['events_by_user'].get(username, 0) + 1
                
                # Identify security incidents
                if (event.severity in [EventSeverity.CRITICAL, EventSeverity.HIGH] or
                    event.event_type == EventType.SECURITY_VIOLATION):
                    report['security_incidents'].append({
                        'timestamp': event.timestamp.isoformat(),
                        'type': event.event_type.value,
                        'severity': event.severity.value,
                        'description': event.description,
                        'username': event.username
                    })
            
            return report
            
        except Exception as e:
            audit_logger.error(f"Audit report generation failed: {e}")
            return {'error': str(e)}
    
    def flush_events(self) -> None:
        """Immediately flush all queued events."""
        with self.queue_lock:
            if self.event_queue:
                events_to_flush = self.event_queue.copy()
                self.event_queue.clear()
                self._process_event_batch(events_to_flush)
    
    def cleanup(self) -> None:
        """Clean up audit logger resources."""
        try:
            # Flush any remaining events
            self.flush_events()
            
            # Log shutdown event
            self.log_event(
                EventType.SYSTEM_ACCESS,
                EventSeverity.INFO,
                EventOutcome.SUCCESS,
                "Security audit logger shutdown"
            )
            
            audit_logger.info("Security audit logger cleanup completed")
            
        except Exception as e:
            audit_logger.warning(f"Audit logger cleanup failed: {e}")


# Convenience functions for common events
def log_authentication_event(username: str, success: bool, session_id: Optional[str] = None,
                            details: Optional[Dict[str, Any]] = None) -> str:
    """Log authentication event."""
    logger = get_audit_logger()
    return logger.log_event(
        EventType.AUTHENTICATION,
        EventSeverity.MEDIUM,
        EventOutcome.SUCCESS if success else EventOutcome.FAILURE,
        f"User authentication {'successful' if success else 'failed'}",
        username=username,
        session_id=session_id,
        details=details
    )

def log_file_access_event(username: str, filepath: str, operation: str,
                         success: bool, session_id: Optional[str] = None) -> str:
    """Log file access event."""
    logger = get_audit_logger()
    return logger.log_event(
        EventType.FILE_ACCESS,
        EventSeverity.LOW,
        EventOutcome.SUCCESS if success else EventOutcome.FAILURE,
        f"File {operation}: {filepath}",
        username=username,
        session_id=session_id,
        details={'filepath': filepath, 'operation': operation}
    )

def log_security_violation(description: str, username: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None) -> str:
    """Log security violation."""
    logger = get_audit_logger()
    return logger.log_event(
        EventType.SECURITY_VIOLATION,
        EventSeverity.HIGH,
        EventOutcome.WARNING,
        description,
        username=username,
        details=details
    )


# Global audit logger instance
_audit_logger = None

def get_audit_logger() -> SecurityAuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger()
    return _audit_logger


if __name__ == "__main__":
    # Basic testing
    audit_logger = SecurityAuditLogger()
    
    # Test event logging
    event_id = audit_logger.log_event(
        EventType.AUTHENTICATION,
        EventSeverity.MEDIUM,
        EventOutcome.SUCCESS,
        "Test authentication event",
        username="test_user",
        details={'test': True}
    )
    
    print(f"Logged event: {event_id}")
    
    # Test event search
    events = audit_logger.search_events(limit=10)
    print(f"Found {len(events)} events")
    
    # Generate report
    report = audit_logger.generate_audit_report()
    print(f"Report generated with {report['total_events']} events")
