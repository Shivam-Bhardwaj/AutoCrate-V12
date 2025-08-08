#!/usr/bin/env python3
"""
AutoCrate AI Integration System
Seamless integration of token optimization and conversation management with AutoCrate.

This module provides:
- Easy-to-use AI integration for AutoCrate workflows
- Automatic token management during development sessions
- Context-aware conversation handling
- Integration with existing AutoCrate logging and architecture
- Production-ready AI assistance utilities

Author: AutoCrate Development Team  
Created: August 2025
Version: 1.0.0
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from contextlib import contextmanager
import functools
import threading

# Add the autocrate directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
autocrate_dir = os.path.join(os.path.dirname(current_dir), 'autocrate')
if autocrate_dir not in sys.path:
    sys.path.insert(0, autocrate_dir)

from token_optimizer import TokenOptimizer, OptimizationConfig, TokenUsageLevel
from conversation_state_manager import ConversationStateManager, MessageRole, ConversationStatus

# Try to import AutoCrate components
try:
    from debug_logger import get_logger, AutoCrateLogger
except ImportError:
    # Fallback to standard logging if AutoCrate logger not available
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

class AutoCrateAI:
    """
    Main AI integration class for AutoCrate.
    Provides a simple interface for AI-powered development assistance.
    """
    
    def __init__(self, 
                 project_name: str = "AutoCrate Project",
                 working_directory: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        
        self.project_name = project_name
        self.working_directory = working_directory or os.getcwd()
        
        # Initialize configuration
        self.config = self._create_config(config or {})
        
        # Initialize token optimizer
        opt_config = OptimizationConfig(
            max_tokens_per_conversation=self.config.get('max_tokens', 100000),
            warning_threshold=self.config.get('warning_threshold', 0.75),
            critical_threshold=self.config.get('critical_threshold', 0.9),
            data_directory=str(Path(self.working_directory) / "logs" / "ai_optimization")
        )
        self.token_optimizer = TokenOptimizer(opt_config)
        
        # Initialize conversation state manager  
        self.state_manager = ConversationStateManager(
            data_directory=str(Path(self.working_directory) / "logs" / "ai_conversations"),
            token_optimizer=self.token_optimizer,
            max_active_sessions=self.config.get('max_sessions', 5)
        )
        
        # Set up callbacks
        self._setup_callbacks()
        
        # Create initial session
        self.current_session_id = self.state_manager.create_session(
            project_name=self.project_name,
            working_directory=self.working_directory,
            context_data={"initialization_config": self.config}
        )
        
        # Statistics tracking
        self.session_stats = {
            "sessions_created": 1,
            "total_interactions": 0,
            "total_tokens_used": 0,
            "optimizations_performed": 0,
            "start_time": datetime.now()
        }
        
        logger.info(f"AutoCrateAI initialized for project '{project_name}'")
    
    def _create_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration with defaults."""
        default_config = {
            'max_tokens': 100000,
            'warning_threshold': 0.75,
            'critical_threshold': 0.9,
            'max_sessions': 5,
            'auto_optimize': True,
            'save_conversations': True,
            'enable_metrics': True,
            'log_level': 'INFO',
            'context_window_size': 50  # Number of recent messages to maintain
        }
        
        # Merge with user config
        config = default_config.copy()
        config.update(user_config)
        
        return config
    
    def _setup_callbacks(self) -> None:
        """Set up event callbacks for monitoring."""
        
        def on_message(message):
            """Handle message events."""
            if hasattr(self, 'session_stats'):
                self.session_stats["total_interactions"] += 1
                self.session_stats["total_tokens_used"] += message.token_count or 0
            
            # Check if optimization is needed
            if self.config.get('auto_optimize', True):
                if self.token_optimizer.should_summarize():
                    self._perform_optimization("auto_summarization")
        
        def on_session_event(session, event_type):
            """Handle session events."""
            if hasattr(self, 'session_stats'):
                if event_type == "created":
                    self.session_stats["sessions_created"] += 1
                elif event_type == "archived":
                    logger.info(f"Session archived: {session.session_id}")
        
        self.state_manager.add_message_callback(on_message)
        self.state_manager.add_session_callback(on_session_event)
    
    def chat(self, 
             user_message: str,
             context: Optional[Dict[str, Any]] = None,
             session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a chat message and return response information.
        This simulates an AI conversation turn for testing and development.
        """
        
        # Add user message
        user_msg_id = self.state_manager.add_message(
            content=user_message,
            role=MessageRole.USER,
            session_id=session_id,
            metadata=context or {}
        )
        
        # Simulate AI processing (in real implementation, this would call actual AI)
        assistant_response = self._generate_simulated_response(user_message, context)
        
        # Add assistant response
        assistant_msg_id = self.state_manager.add_message(
            content=assistant_response,
            role=MessageRole.ASSISTANT,
            session_id=session_id,
            metadata={"simulated": True}
        )
        
        # Get updated session stats
        session_stats = self.state_manager.get_session_statistics(session_id)
        
        # Check for optimization recommendations
        optimization_report = self.token_optimizer.get_optimization_report()
        
        return {
            "user_message_id": user_msg_id,
            "assistant_message_id": assistant_msg_id,
            "assistant_response": assistant_response,
            "session_stats": session_stats,
            "token_usage": optimization_report["token_usage"],
            "recommendations": optimization_report["optimization_recommendations"]
        }
    
    def _generate_simulated_response(self, user_message: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate a simulated AI response for testing purposes."""
        
        # Analyze the message for AutoCrate-specific keywords
        autocrate_keywords = {
            "expression": "I can help you generate NX expressions for AutoCrate. What specific calculations do you need?",
            "crate": "Let me assist with your crate design. What are the dimensions and requirements?", 
            "plywood": "I can help with plywood layout optimization. What panel dimensions are you working with?",
            "test": "I can help you run tests or analyze test results. What would you like to test?",
            "debug": "I'll help you debug the issue. Can you share the error details or logs?",
            "optimize": "I can help optimize your AutoCrate workflow. What area needs improvement?",
            "calculate": "I can assist with engineering calculations. What parameters do you need to calculate?"
        }
        
        user_lower = user_message.lower()
        
        # Check for keywords
        for keyword, response in autocrate_keywords.items():
            if keyword in user_lower:
                return f"{response}\n\nBased on your message: '{user_message[:100]}...'\n\nI'm ready to provide specific AutoCrate engineering assistance."
        
        # Default response
        return f"I understand you're working on: '{user_message[:100]}...'\n\nAs your AutoCrate AI assistant, I can help with:\n- NX expression generation\n- Crate design calculations\n- Plywood layout optimization\n- Testing and debugging\n- Performance optimization\n- Engineering analysis\n\nWhat specific assistance do you need?"
    
    def start_new_session(self, 
                         task_description: str,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Start a new conversation session for a specific task."""
        
        session_id = self.state_manager.create_session(
            project_name=self.project_name,
            task_description=task_description,
            working_directory=self.working_directory,
            context_data=context or {}
        )
        
        self.current_session_id = session_id
        
        logger.info(f"Started new AI session for task: {task_description}")
        return session_id
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to an existing session."""
        success = self.state_manager.switch_session(session_id)
        if success:
            self.current_session_id = session_id
            logger.info(f"Switched to AI session: {session_id}")
        return success
    
    def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a comprehensive summary of a session."""
        stats = self.state_manager.get_session_statistics(session_id)
        context = self.state_manager.get_session_context(session_id)
        recent_messages = self.state_manager.get_session_messages(
            session_id=session_id, 
            limit=self.config.get('context_window_size', 50)
        )
        
        # Analyze conversation topics
        topics = self._analyze_conversation_topics(recent_messages)
        
        return {
            "session_statistics": stats,
            "context": {
                "project_name": context.project_name if context else None,
                "task_description": context.task_description if context else None,
                "working_directory": context.working_directory if context else None
            },
            "conversation_topics": topics,
            "recent_message_count": len(recent_messages),
            "optimization_status": self.token_optimizer.get_optimization_report()
        }
    
    def _analyze_conversation_topics(self, messages: List) -> Dict[str, int]:
        """Analyze conversation topics from messages."""
        topics = {}
        autocrate_topics = {
            "expressions": ["expression", "nx", "formula", "equation"],
            "design": ["crate", "design", "dimension", "size"],
            "materials": ["plywood", "lumber", "material", "wood"],
            "testing": ["test", "debug", "error", "issue"],
            "optimization": ["optimize", "performance", "speed", "memory"],
            "calculations": ["calculate", "math", "compute", "result"]
        }
        
        for message in messages:
            content_lower = message.content.lower()
            for topic, keywords in autocrate_topics.items():
                count = sum(1 for keyword in keywords if keyword in content_lower)
                topics[topic] = topics.get(topic, 0) + count
        
        return topics
    
    def optimize_memory(self, force: bool = False) -> Dict[str, Any]:
        """Perform memory optimization."""
        if not force and not (self.token_optimizer.should_summarize() or self.token_optimizer.should_prune()):
            return {"message": "No optimization needed"}
        
        result = self._perform_optimization("manual_request")
        return result
    
    def _perform_optimization(self, trigger: str) -> Dict[str, Any]:
        """Internal method to perform optimization."""
        
        self.session_stats["optimizations_performed"] += 1
        
        # Perform the optimization
        result = self.token_optimizer.optimize_memory()
        
        # Also optimize the session
        session_result = self.state_manager.optimize_session_memory(self.current_session_id)
        
        # Combine results
        combined_result = {
            "trigger": trigger,
            "timestamp": datetime.now().isoformat(),
            "token_optimization": result,
            "session_optimization": session_result,
            "total_optimizations": self.session_stats["optimizations_performed"]
        }
        
        logger.info(f"Memory optimization completed (trigger: {trigger})")
        return combined_result
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get a comprehensive usage report."""
        
        session_duration = datetime.now() - self.session_stats["start_time"]
        
        # Get token optimizer report
        optimizer_report = self.token_optimizer.get_optimization_report()
        
        # Get active sessions
        active_sessions = self.state_manager.list_active_sessions()
        
        report = {
            "overall_statistics": {
                **self.session_stats,
                "session_duration_hours": session_duration.total_seconds() / 3600,
                "average_tokens_per_interaction": (
                    self.session_stats["total_tokens_used"] / max(1, self.session_stats["total_interactions"])
                )
            },
            "current_session": self.get_session_summary(self.current_session_id),
            "active_sessions": active_sessions,
            "token_optimization": optimizer_report,
            "configuration": self.config,
            "recommendations": self._generate_usage_recommendations()
        }
        
        return report
    
    def _generate_usage_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on current usage."""
        recommendations = []
        
        duration_hours = (datetime.now() - self.session_stats["start_time"]).total_seconds() / 3600
        
        # Long session recommendation
        if duration_hours > 4:
            recommendations.append({
                "type": "session_management",
                "priority": "medium",
                "message": "Consider starting a new session for extended work periods"
            })
        
        # High token usage
        if self.session_stats["total_tokens_used"] > 50000:
            recommendations.append({
                "type": "token_management", 
                "priority": "high",
                "message": "High token usage detected - enable auto-optimization"
            })
        
        # Many sessions
        if len(self.state_manager.active_sessions) > 3:
            recommendations.append({
                "type": "session_cleanup",
                "priority": "low", 
                "message": "Multiple active sessions - consider archiving unused sessions"
            })
        
        return recommendations
    
    def export_conversation(self, 
                          session_id: Optional[str] = None,
                          format: str = "json",
                          include_metadata: bool = True) -> Dict[str, Any]:
        """Export a conversation session."""
        
        session_stats = self.state_manager.get_session_statistics(session_id)
        messages = self.state_manager.get_session_messages(session_id)
        context = self.state_manager.get_session_context(session_id)
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "format_version": "1.0",
            "session_statistics": session_stats,
            "conversation_context": {
                "project_name": context.project_name if context else None,
                "task_description": context.task_description if context else None,
                "working_directory": context.working_directory if context else None
            },
            "messages": []
        }
        
        # Export messages
        for msg in messages:
            msg_data = {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "token_count": msg.token_count
            }
            
            if include_metadata:
                msg_data["id"] = msg.id
                msg_data["metadata"] = msg.metadata
            
            export_data["messages"].append(msg_data)
        
        return export_data
    
    @contextmanager
    def conversation_session(self, task_description: str, **context):
        """Context manager for temporary conversation sessions."""
        session_id = self.start_new_session(task_description, context)
        old_session = self.current_session_id
        
        try:
            yield session_id
        finally:
            self.state_manager.archive_session(session_id)
            if old_session and old_session in self.state_manager.active_sessions:
                self.switch_session(old_session)
    
    def add_file_context(self, file_paths: Union[str, List[str]], session_id: Optional[str] = None) -> None:
        """Add file context to a conversation session."""
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        context = self.state_manager.get_session_context(session_id)
        if context:
            context.active_files.update(file_paths)
            logger.debug(f"Added {len(file_paths)} files to session context")
    
    def shutdown(self) -> Dict[str, Any]:
        """Shutdown the AI system and return final statistics."""
        
        logger.info("Shutting down AutoCrateAI system")
        
        # Get final statistics
        final_stats = self.get_usage_report()
        
        # Shutdown components
        self.state_manager.shutdown()
        
        # Save final report
        try:
            report_file = Path(self.working_directory) / "logs" / "ai_session_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(final_stats, f, indent=2, default=str)
            
            logger.info(f"Final session report saved to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save final report: {e}")
        
        logger.info("AutoCrateAI shutdown complete")
        return final_stats

# Convenience functions for easy integration
def create_ai_assistant(project_name: str = "AutoCrate Project", **config) -> AutoCrateAI:
    """Create an AI assistant for AutoCrate with optional configuration."""
    return AutoCrateAI(project_name=project_name, config=config)

def quick_chat(message: str, ai: Optional[AutoCrateAI] = None) -> str:
    """Quick chat function for simple interactions."""
    if ai is None:
        ai = AutoCrateAI()
    
    result = ai.chat(message)
    return result["assistant_response"]

# Decorator for AI-enhanced functions
def ai_enhanced(ai_description: str = ""):
    """Decorator to add AI monitoring to functions."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # This could integrate with token tracking for function calls
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                duration = datetime.now() - start_time
                
                logger.debug(f"AI-enhanced function '{func.__name__}' completed in {duration.total_seconds():.2f}s")
                return result
                
            except Exception as e:
                logger.error(f"AI-enhanced function '{func.__name__}' failed: {e}")
                raise
                
        return wrapper
    return decorator

# Integration with AutoCrate workflows
class AutoCrateWorkflowAI:
    """AI integration specifically for AutoCrate workflows."""
    
    def __init__(self, ai: AutoCrateAI):
        self.ai = ai
    
    def analyze_crate_requirements(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """AI analysis of crate requirements."""
        message = f"Analyze these crate specifications: {json.dumps(specifications, indent=2)}"
        return self.ai.chat(message)
    
    def suggest_optimizations(self, current_design: Dict[str, Any]) -> Dict[str, Any]:
        """AI suggestions for design optimization."""
        message = f"Suggest optimizations for this crate design: {json.dumps(current_design, indent=2)}"
        return self.ai.chat(message)
    
    def debug_expression_generation(self, error_details: str) -> Dict[str, Any]:
        """AI assistance with debugging expression generation."""
        message = f"Help debug this NX expression generation issue: {error_details}"
        return self.ai.chat(message)
    
    def review_test_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """AI review of test results."""
        message = f"Review these test results and suggest improvements: {json.dumps(test_results, indent=2)}"
        return self.ai.chat(message)

# Export main classes and functions
__all__ = [
    'AutoCrateAI',
    'AutoCrateWorkflowAI',
    'create_ai_assistant',
    'quick_chat',
    'ai_enhanced'
]

if __name__ == "__main__":
    # Example usage and demonstration
    logging.basicConfig(level=logging.INFO)
    
    # Create AI assistant
    ai = create_ai_assistant(
        project_name="Demo AutoCrate Project",
        max_tokens=50000,
        auto_optimize=True
    )
    
    print("=== AutoCrate AI Assistant Demo ===")
    
    # Simulate some interactions
    interactions = [
        "I need to generate NX expressions for a 48x36x24 crate",
        "How do I optimize plywood layout for this design?", 
        "Can you help me debug an expression generation error?",
        "What are the best practices for crate testing?",
        "How can I improve the performance of my calculations?"
    ]
    
    for i, message in enumerate(interactions, 1):
        print(f"\n--- Interaction {i} ---")
        print(f"User: {message}")
        
        result = ai.chat(message)
        print(f"Assistant: {result['assistant_response'][:200]}...")
        
        # Show token usage
        print(f"Tokens used: {result['session_stats']['token_usage']['total']}")
    
    # Show final report
    print("\n=== Final Usage Report ===")
    report = ai.get_usage_report()
    print(f"Total interactions: {report['overall_statistics']['total_interactions']}")
    print(f"Total tokens used: {report['overall_statistics']['total_tokens_used']}")
    print(f"Optimizations performed: {report['overall_statistics']['optimizations_performed']}")
    
    # Export conversation
    conversation = ai.export_conversation()
    print(f"\nConversation exported with {len(conversation['messages'])} messages")
    
    # Cleanup
    final_stats = ai.shutdown()
    print(f"AI assistant shutdown complete")