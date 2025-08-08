#!/usr/bin/env python3
"""
AutoCrate Conversation State Manager
Lightweight conversation state management system for AutoCrate AI interactions.

This module provides:
- Conversation session management
- Context preservation across interactions  
- State persistence and recovery
- Integration with token optimization
- Clean separation of conversation threads

Author: AutoCrate Development Team
Created: August 2025
Version: 1.0.0
"""

import os
import json
import uuid
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from contextlib import contextmanager

from token_optimizer import TokenOptimizer, OptimizationConfig, estimate_tokens

logger = logging.getLogger(__name__)

class ConversationStatus(Enum):
    """Status of a conversation session."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    SUMMARIZING = "summarizing"
    ARCHIVED = "archived"
    ERROR = "error"

class MessageRole(Enum):
    """Role of message participants."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ConversationMessage:
    """Individual message in a conversation."""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.token_count is None:
            self.token_count = estimate_tokens(self.content)

@dataclass  
class ConversationContext:
    """Context information for a conversation."""
    session_id: str
    project_name: Optional[str] = None
    task_description: Optional[str] = None
    working_directory: Optional[str] = None
    environment_info: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    active_files: Set[str] = field(default_factory=set)
    
@dataclass
class ConversationSession:
    """Complete conversation session data."""
    session_id: str
    status: ConversationStatus
    created_at: datetime
    last_activity: datetime
    context: ConversationContext
    messages: List[ConversationMessage] = field(default_factory=list)
    total_tokens: int = 0
    turn_count: int = 0
    summary: Optional[str] = None
    
    def add_message(self, message: ConversationMessage) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.total_tokens += message.token_count or 0
        self.turn_count += 1
        self.last_activity = datetime.now()
    
    def get_recent_messages(self, count: int = 10) -> List[ConversationMessage]:
        """Get the most recent messages."""
        return self.messages[-count:] if self.messages else []
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage breakdown."""
        user_tokens = sum(msg.token_count or 0 for msg in self.messages if msg.role == MessageRole.USER)
        assistant_tokens = sum(msg.token_count or 0 for msg in self.messages if msg.role == MessageRole.ASSISTANT)
        system_tokens = sum(msg.token_count or 0 for msg in self.messages if msg.role == MessageRole.SYSTEM)
        
        return {
            "total": self.total_tokens,
            "user": user_tokens,
            "assistant": assistant_tokens,
            "system": system_tokens
        }

class ConversationStateManager:
    """Manages conversation state and context for AutoCrate interactions."""
    
    def __init__(self, 
                 data_directory: str = "logs/conversations",
                 token_optimizer: Optional[TokenOptimizer] = None,
                 max_active_sessions: int = 5,
                 auto_save_interval: int = 300):  # 5 minutes
        
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_active_sessions = max_active_sessions
        self.auto_save_interval = auto_save_interval
        
        # Token optimization integration
        if token_optimizer is None:
            config = OptimizationConfig(data_directory=str(self.data_dir / "token_optimization"))
            token_optimizer = TokenOptimizer(config)
        self.token_optimizer = token_optimizer
        
        # Active sessions
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.current_session: Optional[ConversationSession] = None
        
        # Event callbacks
        self.message_callbacks: List[Callable[[ConversationMessage], None]] = []
        self.session_callbacks: List[Callable[[ConversationSession, str], None]] = []  # session, event_type
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Background processing
        self._background_thread = None
        self._shutdown_event = threading.Event()
        
        # Load existing sessions
        self._load_active_sessions()
        
        # Start background processing
        self._start_background_processing()
        
        logger.info(f"ConversationStateManager initialized with {len(self.active_sessions)} active sessions")
    
    def create_session(self, 
                      project_name: Optional[str] = None,
                      task_description: Optional[str] = None,
                      working_directory: Optional[str] = None,
                      context_data: Optional[Dict[str, Any]] = None) -> str:
        """Create a new conversation session."""
        
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Create context
        context = ConversationContext(
            session_id=session_id,
            project_name=project_name,
            task_description=task_description,
            working_directory=working_directory or os.getcwd(),
            environment_info=self._gather_environment_info(),
            user_preferences=context_data or {}
        )
        
        # Create session
        session = ConversationSession(
            session_id=session_id,
            status=ConversationStatus.INITIALIZING,
            created_at=now,
            last_activity=now,
            context=context
        )
        
        with self._lock:
            # Clean up old sessions if needed
            self._cleanup_old_sessions()
            
            # Add new session
            self.active_sessions[session_id] = session
            self.current_session = session
            
            # Update status
            session.status = ConversationStatus.ACTIVE
        
        # Notify callbacks
        self._notify_session_callbacks(session, "created")
        
        # Add initial system message
        self._add_system_message(session_id, self._create_system_prompt(context))
        
        logger.info(f"Created new conversation session: {session_id}")
        return session_id
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to an existing session."""
        with self._lock:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found")
                return False
            
            # Update previous session status
            if self.current_session:
                self.current_session.status = ConversationStatus.IDLE
            
            # Switch to new session  
            self.current_session = self.active_sessions[session_id]
            self.current_session.status = ConversationStatus.ACTIVE
            self.current_session.last_activity = datetime.now()
        
        self._notify_session_callbacks(self.current_session, "switched")
        logger.info(f"Switched to session: {session_id}")
        return True
    
    def add_message(self, 
                   content: str,
                   role: MessageRole = MessageRole.USER,
                   session_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a message to the current or specified session."""
        
        with self._lock:
            # Determine target session
            if session_id:
                if session_id not in self.active_sessions:
                    raise ValueError(f"Session {session_id} not found")
                session = self.active_sessions[session_id]
            else:
                if not self.current_session:
                    # Create a default session
                    session_id = self.create_session(project_name="AutoCrate Default")
                    session = self.current_session
                else:
                    session = self.current_session
                    session_id = session.session_id
            
            # Create message
            message_id = str(uuid.uuid4())
            message = ConversationMessage(
                id=message_id,
                role=role,
                content=content,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Add to session
            session.add_message(message)
            
            # Record in token optimizer
            if role == MessageRole.USER:
                # For user messages, we'll wait for the assistant response to record the full turn
                pass
            elif role == MessageRole.ASSISTANT and len(session.messages) >= 2:
                # Record the conversation turn (user + assistant)
                prev_msg = session.messages[-2] if len(session.messages) >= 2 else None
                if prev_msg and prev_msg.role == MessageRole.USER:
                    self.token_optimizer.record_conversation_turn(
                        prev_msg.content,
                        content,
                        prev_msg.token_count or 0,
                        message.token_count or 0
                    )
        
        # Notify callbacks
        self._notify_message_callbacks(message)
        
        logger.debug(f"Added {role.value} message to session {session_id}: {len(content)} chars")
        return message_id
    
    def get_session_context(self, session_id: Optional[str] = None) -> Optional[ConversationContext]:
        """Get the context for a session."""
        with self._lock:
            session = self._get_session(session_id)
            return session.context if session else None
    
    def get_session_messages(self, 
                           session_id: Optional[str] = None,
                           limit: Optional[int] = None,
                           role_filter: Optional[MessageRole] = None) -> List[ConversationMessage]:
        """Get messages from a session with optional filtering."""
        with self._lock:
            session = self._get_session(session_id)
            if not session:
                return []
            
            messages = session.messages
            
            # Apply role filter
            if role_filter:
                messages = [msg for msg in messages if msg.role == role_filter]
            
            # Apply limit
            if limit:
                messages = messages[-limit:]
            
            return messages
    
    def update_context(self, 
                      session_id: Optional[str] = None,
                      **context_updates) -> bool:
        """Update the context for a session."""
        with self._lock:
            session = self._get_session(session_id)
            if not session:
                return False
            
            context = session.context
            
            # Update context fields
            for key, value in context_updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
                else:
                    # Add to user preferences if not a known field
                    context.user_preferences[key] = value
            
            session.last_activity = datetime.now()
        
        logger.debug(f"Updated context for session {session.session_id}")
        return True
    
    def archive_session(self, session_id: Optional[str] = None) -> bool:
        """Archive a session (move to long-term storage)."""
        with self._lock:
            session = self._get_session(session_id)
            if not session:
                return False
            
            session.status = ConversationStatus.ARCHIVED
            
            # Save to archive
            self._save_session_to_archive(session)
            
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Clear current session if it was the archived one
            if self.current_session and self.current_session.session_id == session.session_id:
                self.current_session = None
        
        self._notify_session_callbacks(session, "archived")
        logger.info(f"Archived session: {session.session_id}")
        return True
    
    def get_session_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a session."""
        with self._lock:
            session = self._get_session(session_id)
            if not session:
                return {}
            
            token_usage = session.get_token_usage()
            
            return {
                "session_id": session.session_id,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "duration_minutes": (session.last_activity - session.created_at).total_seconds() / 60,
                "message_count": len(session.messages),
                "turn_count": session.turn_count,
                "token_usage": token_usage,
                "project_name": session.context.project_name,
                "task_description": session.context.task_description
            }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions with basic info."""
        with self._lock:
            sessions = []
            for session in self.active_sessions.values():
                sessions.append({
                    "session_id": session.session_id,
                    "status": session.status.value,
                    "project_name": session.context.project_name,
                    "last_activity": session.last_activity.isoformat(),
                    "message_count": len(session.messages),
                    "total_tokens": session.total_tokens,
                    "is_current": self.current_session and session.session_id == self.current_session.session_id
                })
            
            # Sort by last activity
            sessions.sort(key=lambda x: x["last_activity"], reverse=True)
            return sessions
    
    def optimize_session_memory(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Optimize memory usage for a session."""
        session = self._get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Delegate to token optimizer
        optimization_result = self.token_optimizer.optimize_memory()
        
        # Update session summary if summarization occurred
        if optimization_result.get("summarization_performed"):
            session.summary = f"Conversation summarized on {datetime.now().isoformat()}"
            session.status = ConversationStatus.SUMMARIZING
            
            # After a brief moment, return to active
            def restore_active():
                time.sleep(1)
                session.status = ConversationStatus.ACTIVE
            
            threading.Thread(target=restore_active, daemon=True).start()
        
        logger.info(f"Memory optimization completed for session {session.session_id}")
        return optimization_result
    
    def add_message_callback(self, callback: Callable[[ConversationMessage], None]) -> None:
        """Add a callback for message events."""
        self.message_callbacks.append(callback)
    
    def add_session_callback(self, callback: Callable[[ConversationSession, str], None]) -> None:
        """Add a callback for session events."""
        self.session_callbacks.append(callback)
    
    def _get_session(self, session_id: Optional[str] = None) -> Optional[ConversationSession]:
        """Get a session by ID or current session."""
        if session_id:
            return self.active_sessions.get(session_id)
        else:
            return self.current_session
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up old or excessive sessions."""
        if len(self.active_sessions) <= self.max_active_sessions:
            return
        
        # Sort sessions by last activity
        sessions_by_activity = sorted(
            self.active_sessions.items(),
            key=lambda x: x[1].last_activity
        )
        
        # Archive oldest sessions
        sessions_to_archive = sessions_by_activity[:-self.max_active_sessions]
        for session_id, session in sessions_to_archive:
            logger.info(f"Auto-archiving old session: {session_id}")
            self.archive_session(session_id)
    
    def _add_system_message(self, session_id: str, content: str) -> None:
        """Add a system message to a session."""
        self.add_message(
            content=content,
            role=MessageRole.SYSTEM,
            session_id=session_id,
            metadata={"type": "system_initialization"}
        )
    
    def _create_system_prompt(self, context: ConversationContext) -> str:
        """Create an initial system prompt for the session."""
        prompt_parts = [
            "AutoCrate AI Assistant - Professional Crate Engineering System",
            f"Session ID: {context.session_id}",
            f"Project: {context.project_name or 'Untitled Project'}",
            f"Working Directory: {context.working_directory}",
            f"Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        if context.task_description:
            prompt_parts.append(f"Task: {context.task_description}")
        
        prompt_parts.extend([
            "",
            "I am ready to assist with AutoCrate engineering calculations, crate design,",
            "NX expression generation, testing, and development tasks.",
            "Please let me know how I can help you today."
        ])
        
        return "\n".join(prompt_parts)
    
    def _gather_environment_info(self) -> Dict[str, Any]:
        """Gather information about the current environment."""
        return {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name,
            "working_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat(),
            "process_id": os.getpid()
        }
    
    def _notify_message_callbacks(self, message: ConversationMessage) -> None:
        """Notify message callbacks."""
        for callback in self.message_callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Message callback error: {e}")
    
    def _notify_session_callbacks(self, session: ConversationSession, event_type: str) -> None:
        """Notify session callbacks."""
        for callback in self.session_callbacks:
            try:
                callback(session, event_type)
            except Exception as e:
                logger.error(f"Session callback error: {e}")
    
    def _save_session_to_archive(self, session: ConversationSession) -> None:
        """Save a session to the archive."""
        try:
            archive_dir = self.data_dir / "archived"
            archive_dir.mkdir(exist_ok=True)
            
            # Create filename with timestamp
            timestamp = session.created_at.strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}_{session.session_id}.json"
            archive_file = archive_dir / filename
            
            # Prepare session data for JSON serialization
            session_data = {
                "session_id": session.session_id,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "context": asdict(session.context),
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "token_count": msg.token_count,
                        "metadata": msg.metadata
                    }
                    for msg in session.messages
                ],
                "total_tokens": session.total_tokens,
                "turn_count": session.turn_count,
                "summary": session.summary
            }
            
            # Handle set serialization in context
            if "active_files" in session_data["context"]:
                session_data["context"]["active_files"] = list(session_data["context"]["active_files"])
            
            # Write to file
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved session to archive: {archive_file}")
            
        except Exception as e:
            logger.error(f"Failed to save session to archive: {e}")
    
    def _load_active_sessions(self) -> None:
        """Load active sessions from disk."""
        try:
            active_sessions_file = self.data_dir / "active_sessions.json"
            if not active_sessions_file.exists():
                return
            
            with open(active_sessions_file, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            loaded_count = 0
            for session_data in sessions_data:
                try:
                    # Restore session object
                    session = self._deserialize_session(session_data)
                    
                    # Only restore recent sessions (last 24 hours)
                    if (datetime.now() - session.last_activity).days < 1:
                        self.active_sessions[session.session_id] = session
                        loaded_count += 1
                    else:
                        # Archive old sessions
                        self._save_session_to_archive(session)
                
                except Exception as e:
                    logger.error(f"Failed to restore session: {e}")
            
            if loaded_count > 0:
                logger.info(f"Loaded {loaded_count} active sessions from disk")
                
        except Exception as e:
            logger.error(f"Failed to load active sessions: {e}")
    
    def _deserialize_session(self, session_data: Dict[str, Any]) -> ConversationSession:
        """Deserialize session data from JSON."""
        # Restore context
        context_data = session_data["context"]
        if "active_files" in context_data:
            context_data["active_files"] = set(context_data["active_files"])
        
        context = ConversationContext(**context_data)
        
        # Restore messages
        messages = []
        for msg_data in session_data["messages"]:
            message = ConversationMessage(
                id=msg_data["id"],
                role=MessageRole(msg_data["role"]),
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                token_count=msg_data["token_count"],
                metadata=msg_data["metadata"]
            )
            messages.append(message)
        
        # Restore session
        session = ConversationSession(
            session_id=session_data["session_id"],
            status=ConversationStatus(session_data["status"]),
            created_at=datetime.fromisoformat(session_data["created_at"]),
            last_activity=datetime.fromisoformat(session_data["last_activity"]),
            context=context,
            messages=messages,
            total_tokens=session_data["total_tokens"],
            turn_count=session_data["turn_count"],
            summary=session_data.get("summary")
        )
        
        return session
    
    def _save_active_sessions(self) -> None:
        """Save active sessions to disk."""
        try:
            active_sessions_file = self.data_dir / "active_sessions.json"
            
            sessions_data = []
            for session in self.active_sessions.values():
                session_data = {
                    "session_id": session.session_id,
                    "status": session.status.value,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "context": asdict(session.context),
                    "messages": [
                        {
                            "id": msg.id,
                            "role": msg.role.value,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat(),
                            "token_count": msg.token_count,
                            "metadata": msg.metadata
                        }
                        for msg in session.messages
                    ],
                    "total_tokens": session.total_tokens,
                    "turn_count": session.turn_count,
                    "summary": session.summary
                }
                
                # Handle set serialization
                if "active_files" in session_data["context"]:
                    session_data["context"]["active_files"] = list(session_data["context"]["active_files"])
                
                sessions_data.append(session_data)
            
            with open(active_sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save active sessions: {e}")
    
    def _start_background_processing(self) -> None:
        """Start background processing thread."""
        self._background_thread = threading.Thread(target=self._background_worker, daemon=True)
        self._background_thread.start()
        logger.debug("Background processing thread started")
    
    def _background_worker(self) -> None:
        """Background worker for periodic tasks."""
        while not self._shutdown_event.is_set():
            try:
                # Auto-save active sessions
                self._save_active_sessions()
                
                # Clean up old sessions
                self._cleanup_old_sessions()
                
                # Optimize memory if needed
                for session in self.active_sessions.values():
                    if self.token_optimizer.should_summarize():
                        self.optimize_session_memory(session.session_id)
                        break  # Only optimize one session per cycle
                
                # Wait for next interval
                self._shutdown_event.wait(self.auto_save_interval)
                
            except Exception as e:
                logger.error(f"Background worker error: {e}")
                self._shutdown_event.wait(60)  # Wait 1 minute before retry
    
    def shutdown(self) -> None:
        """Shutdown the state manager."""
        logger.info("Shutting down ConversationStateManager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for background thread
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=5.0)
        
        # Final save
        self._save_active_sessions()
        
        # Shutdown token optimizer
        self.token_optimizer.shutdown()
        
        logger.info("ConversationStateManager shutdown complete")
    
    @contextmanager
    def session_context(self, 
                       project_name: Optional[str] = None,
                       task_description: Optional[str] = None,
                       **context_data):
        """Context manager for temporary conversation sessions."""
        session_id = self.create_session(
            project_name=project_name,
            task_description=task_description,
            context_data=context_data
        )
        
        try:
            yield session_id
        finally:
            self.archive_session(session_id)

# Convenience functions
def create_state_manager(**config) -> ConversationStateManager:
    """Create a conversation state manager with configuration."""
    return ConversationStateManager(**config)

def get_current_session_info(manager: ConversationStateManager) -> Optional[Dict[str, Any]]:
    """Get info about the current session."""
    if not manager.current_session:
        return None
    return manager.get_session_statistics()

# Export main classes and functions
__all__ = [
    'ConversationStateManager',
    'ConversationSession',
    'ConversationMessage', 
    'ConversationContext',
    'ConversationStatus',
    'MessageRole',
    'create_state_manager',
    'get_current_session_info'
]

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    manager = ConversationStateManager()
    
    # Create a session
    session_id = manager.create_session(
        project_name="Test Project",
        task_description="Testing conversation state management"
    )
    
    # Add some messages
    manager.add_message("Hello, I need help with AutoCrate", MessageRole.USER)
    manager.add_message("I'd be happy to help! What would you like to know about AutoCrate?", MessageRole.ASSISTANT)
    manager.add_message("How do I generate NX expressions?", MessageRole.USER)
    
    # Get session stats
    stats = manager.get_session_statistics()
    print("Session Statistics:")
    print(json.dumps(stats, indent=2))
    
    # List active sessions
    sessions = manager.list_active_sessions()
    print("\nActive Sessions:")
    print(json.dumps(sessions, indent=2))
    
    # Cleanup
    manager.shutdown()