#!/usr/bin/env python3
"""
AutoCrate Token Usage Optimization System
A comprehensive system for managing conversation resources and optimizing token usage.

This module provides:
- Token usage tracking and monitoring
- Conversation memory management with automatic summarization
- Memory pruning strategies for long conversations
- Configurable thresholds and alerts
- Metrics and reporting
- Seamless integration with AutoCrate architecture

Author: AutoCrate Development Team
Created: August 2025
Version: 1.0.0
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import threading
import pickle
import gzip

# Configure logging
logger = logging.getLogger(__name__)

class TokenUsageLevel(Enum):
    """Token usage alert levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ConversationState(Enum):
    """Conversation state indicators."""
    ACTIVE = "active"
    SUMMARIZING = "summarizing"
    PRUNING = "pruning"
    ARCHIVED = "archived"

@dataclass
class TokenUsageStats:
    """Token usage statistics container."""
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    conversation_turns: int = 0
    average_per_turn: float = 0.0
    peak_usage: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def update_average(self):
        """Update average tokens per turn."""
        if self.conversation_turns > 0:
            self.average_per_turn = self.total_tokens / self.conversation_turns

@dataclass
class ConversationTurn:
    """Individual conversation turn data."""
    turn_id: int
    timestamp: datetime
    input_tokens: int
    output_tokens: int
    total_tokens: int
    content_hash: str
    summary: Optional[str] = None
    is_archived: bool = False
    
    @classmethod
    def from_content(cls, turn_id: int, input_content: str, output_content: str, 
                    input_tokens: int, output_tokens: int) -> 'ConversationTurn':
        """Create a conversation turn from content."""
        content_hash = hashlib.md5((input_content + output_content).encode()).hexdigest()
        return cls(
            turn_id=turn_id,
            timestamp=datetime.now(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            content_hash=content_hash
        )

@dataclass
class OptimizationConfig:
    """Configuration for token optimization."""
    # Token limits
    max_tokens_per_conversation: int = 100000
    warning_threshold: float = 0.75  # Warn at 75% of max
    critical_threshold: float = 0.9   # Critical at 90% of max
    
    # Memory management
    max_turns_in_memory: int = 50
    summarization_trigger_turns: int = 20
    compression_ratio_target: float = 0.3  # Compress to 30% of original
    
    # Pruning settings
    auto_prune_enabled: bool = True
    prune_threshold_days: int = 7
    keep_recent_turns: int = 10
    
    # Performance
    background_processing: bool = True
    cache_summaries: bool = True
    save_interval_minutes: int = 5
    
    # File settings
    data_directory: str = "logs/token_optimization"
    backup_enabled: bool = True
    compression_enabled: bool = True

class ConversationMemoryManager:
    """Manages conversation memory with summarization and pruning."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.turns: deque = deque(maxlen=config.max_turns_in_memory)
        self.summaries: Dict[str, str] = {}
        self.archived_turns: List[ConversationTurn] = []
        self.total_turns = 0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Data persistence
        self.data_dir = Path(config.data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_state()
    
    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a new conversation turn."""
        with self._lock:
            self.turns.append(turn)
            self.total_turns += 1
            
            # Check if summarization is needed
            if len(self.turns) >= self.config.summarization_trigger_turns:
                self._trigger_summarization()
    
    def _trigger_summarization(self) -> None:
        """Trigger summarization of older turns."""
        if len(self.turns) < self.config.summarization_trigger_turns:
            return
        
        logger.info("Triggering conversation summarization")
        
        # Take the oldest half of turns for summarization
        turns_to_summarize = len(self.turns) // 2
        old_turns = []
        
        for _ in range(turns_to_summarize):
            if self.turns:
                old_turns.append(self.turns.popleft())
        
        if old_turns:
            summary = self._create_summary(old_turns)
            summary_key = f"summary_{old_turns[0].turn_id}_{old_turns[-1].turn_id}"
            self.summaries[summary_key] = summary
            
            # Archive the turns
            for turn in old_turns:
                turn.is_archived = True
                turn.summary = summary_key
                self.archived_turns.append(turn)
            
            logger.info(f"Summarized {len(old_turns)} turns into summary '{summary_key}'")
    
    def _create_summary(self, turns: List[ConversationTurn]) -> str:
        """Create a summary of conversation turns."""
        if not turns:
            return ""
        
        # Simple summarization strategy - in practice, this could use AI summarization
        total_tokens = sum(turn.total_tokens for turn in turns)
        start_time = turns[0].timestamp
        end_time = turns[-1].timestamp
        duration = end_time - start_time
        
        summary = {
            "turn_range": f"{turns[0].turn_id}-{turns[-1].turn_id}",
            "total_turns": len(turns),
            "total_tokens": total_tokens,
            "average_tokens_per_turn": total_tokens / len(turns),
            "duration_minutes": duration.total_seconds() / 60,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "content_hashes": [turn.content_hash for turn in turns]
        }
        
        return json.dumps(summary, indent=2)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        with self._lock:
            active_tokens = sum(turn.total_tokens for turn in self.turns)
            archived_tokens = sum(turn.total_tokens for turn in self.archived_turns)
            
            return {
                "active_turns": len(self.turns),
                "archived_turns": len(self.archived_turns),
                "total_turns": self.total_turns,
                "active_tokens": active_tokens,
                "archived_tokens": archived_tokens,
                "total_tokens": active_tokens + archived_tokens,
                "summaries_count": len(self.summaries),
                "compression_ratio": self._calculate_compression_ratio()
            }
    
    def _calculate_compression_ratio(self) -> float:
        """Calculate the compression ratio achieved by summarization."""
        if not self.archived_turns:
            return 1.0
        
        archived_tokens = sum(turn.total_tokens for turn in self.archived_turns)
        summary_tokens = sum(len(s.split()) * 1.3 for s in self.summaries.values())  # Rough estimate
        
        if archived_tokens == 0:
            return 1.0
        
        return summary_tokens / archived_tokens
    
    def prune_old_conversations(self, days_threshold: Optional[int] = None) -> int:
        """Prune conversations older than the threshold."""
        if not self.config.auto_prune_enabled:
            return 0
        
        days_threshold = days_threshold or self.config.prune_threshold_days
        cutoff_time = datetime.now() - timedelta(days=days_threshold)
        
        with self._lock:
            pruned_count = 0
            new_archived = []
            
            for turn in self.archived_turns:
                if turn.timestamp > cutoff_time:
                    new_archived.append(turn)
                else:
                    pruned_count += 1
            
            self.archived_turns = new_archived
            
            # Also clean up old summaries
            old_summaries = list(self.summaries.keys())
            for key in old_summaries:
                # Remove summaries that no longer have associated turns
                if not any(turn.summary == key for turn in self.archived_turns):
                    del self.summaries[key]
            
            if pruned_count > 0:
                logger.info(f"Pruned {pruned_count} old conversation turns")
            
            return pruned_count
    
    def _save_state(self) -> None:
        """Save the current state to disk."""
        try:
            state_file = self.data_dir / "memory_state.pkl.gz"
            state_data = {
                "turns": list(self.turns),
                "summaries": self.summaries,
                "archived_turns": self.archived_turns,
                "total_turns": self.total_turns,
                "saved_at": datetime.now()
            }
            
            with gzip.open(state_file, 'wb') as f:
                pickle.dump(state_data, f)
                
        except Exception as e:
            logger.error(f"Failed to save memory state: {e}")
    
    def _load_state(self) -> None:
        """Load state from disk."""
        try:
            state_file = self.data_dir / "memory_state.pkl.gz"
            if not state_file.exists():
                return
            
            with gzip.open(state_file, 'rb') as f:
                state_data = pickle.load(f)
            
            self.turns = deque(state_data.get("turns", []), maxlen=self.config.max_turns_in_memory)
            self.summaries = state_data.get("summaries", {})
            self.archived_turns = state_data.get("archived_turns", [])
            self.total_turns = state_data.get("total_turns", 0)
            
            logger.info(f"Loaded memory state with {len(self.turns)} active turns and {len(self.archived_turns)} archived turns")
            
        except Exception as e:
            logger.error(f"Failed to load memory state: {e}")

class TokenUsageMonitor:
    """Monitors token usage and provides alerts."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.current_stats = TokenUsageStats()
        self.usage_history: List[TokenUsageStats] = []
        self.alerts: List[Dict[str, Any]] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Data persistence
        self.data_dir = Path(config.data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_stats()
    
    def record_usage(self, input_tokens: int, output_tokens: int, turn_id: int) -> None:
        """Record token usage for a conversation turn."""
        with self._lock:
            self.current_stats.input_tokens += input_tokens
            self.current_stats.output_tokens += output_tokens
            self.current_stats.total_tokens += input_tokens + output_tokens
            self.current_stats.conversation_turns += 1
            self.current_stats.update_average()
            
            # Update peak usage
            turn_total = input_tokens + output_tokens
            if turn_total > self.current_stats.peak_usage:
                self.current_stats.peak_usage = turn_total
            
            # Check for alerts
            self._check_usage_alerts()
            
            logger.debug(f"Recorded {input_tokens + output_tokens} tokens for turn {turn_id}")
    
    def _check_usage_alerts(self) -> None:
        """Check if usage has exceeded alert thresholds."""
        usage_ratio = self.current_stats.total_tokens / self.config.max_tokens_per_conversation
        
        alert_level = None
        if usage_ratio >= self.config.critical_threshold:
            alert_level = TokenUsageLevel.CRITICAL
        elif usage_ratio >= self.config.warning_threshold:
            alert_level = TokenUsageLevel.HIGH
        elif usage_ratio >= 0.5:
            alert_level = TokenUsageLevel.MEDIUM
        else:
            alert_level = TokenUsageLevel.LOW
        
        # Only alert on level increases
        if self._should_create_alert(alert_level):
            self._create_alert(alert_level, usage_ratio)
    
    def _should_create_alert(self, level: TokenUsageLevel) -> bool:
        """Check if an alert should be created for the given level."""
        if not self.alerts:
            return level != TokenUsageLevel.LOW
        
        last_alert_level = TokenUsageLevel(self.alerts[-1]["level"])
        level_priorities = {
            TokenUsageLevel.LOW: 0,
            TokenUsageLevel.MEDIUM: 1,
            TokenUsageLevel.HIGH: 2,
            TokenUsageLevel.CRITICAL: 3
        }
        
        return level_priorities[level] > level_priorities[last_alert_level]
    
    def _create_alert(self, level: TokenUsageLevel, usage_ratio: float) -> None:
        """Create a usage alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "usage_ratio": usage_ratio,
            "total_tokens": self.current_stats.total_tokens,
            "max_tokens": self.config.max_tokens_per_conversation,
            "conversation_turns": self.current_stats.conversation_turns,
            "message": self._get_alert_message(level, usage_ratio)
        }
        
        self.alerts.append(alert)
        
        # Log the alert
        log_method = {
            TokenUsageLevel.LOW: logger.debug,
            TokenUsageLevel.MEDIUM: logger.info,
            TokenUsageLevel.HIGH: logger.warning,
            TokenUsageLevel.CRITICAL: logger.critical
        }[level]
        
        log_method(f"Token usage alert: {alert['message']}")
    
    def _get_alert_message(self, level: TokenUsageLevel, usage_ratio: float) -> str:
        """Get an appropriate alert message."""
        percentage = usage_ratio * 100
        
        messages = {
            TokenUsageLevel.MEDIUM: f"Token usage at {percentage:.1f}% - consider summarization",
            TokenUsageLevel.HIGH: f"High token usage at {percentage:.1f}% - summarization recommended",
            TokenUsageLevel.CRITICAL: f"Critical token usage at {percentage:.1f}% - immediate action required"
        }
        
        return messages.get(level, f"Token usage at {percentage:.1f}%")
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        with self._lock:
            return {
                **asdict(self.current_stats),
                "usage_ratio": self.current_stats.total_tokens / self.config.max_tokens_per_conversation,
                "remaining_tokens": self.config.max_tokens_per_conversation - self.current_stats.total_tokens,
                "recent_alerts": self.alerts[-5:] if self.alerts else []
            }
    
    def reset_stats(self) -> None:
        """Reset current statistics (e.g., for a new conversation)."""
        with self._lock:
            # Save current stats to history
            if self.current_stats.total_tokens > 0:
                self.usage_history.append(self.current_stats)
            
            # Create new stats
            self.current_stats = TokenUsageStats()
            self.alerts = []
            
            logger.info("Token usage statistics reset for new conversation")
    
    def _save_stats(self) -> None:
        """Save statistics to disk."""
        try:
            stats_file = self.data_dir / "usage_stats.json"
            data = {
                "current_stats": asdict(self.current_stats),
                "usage_history": [asdict(stats) for stats in self.usage_history[-100:]],  # Keep last 100
                "alerts": self.alerts[-50:],  # Keep last 50 alerts
                "saved_at": datetime.now().isoformat()
            }
            
            # Handle datetime serialization
            def datetime_handler(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(stats_file, 'w') as f:
                json.dump(data, f, indent=2, default=datetime_handler)
                
        except Exception as e:
            logger.error(f"Failed to save usage statistics: {e}")
    
    def _load_stats(self) -> None:
        """Load statistics from disk."""
        try:
            stats_file = self.data_dir / "usage_stats.json"
            if not stats_file.exists():
                return
            
            with open(stats_file, 'r') as f:
                data = json.load(f)
            
            # Load current stats
            current_data = data.get("current_stats", {})
            if current_data:
                # Convert timestamp string back to datetime
                if "timestamp" in current_data and current_data["timestamp"]:
                    current_data["timestamp"] = datetime.fromisoformat(current_data["timestamp"])
                self.current_stats = TokenUsageStats(**current_data)
            
            # Load history
            history_data = data.get("usage_history", [])
            self.usage_history = []
            for stats_dict in history_data:
                if "timestamp" in stats_dict and stats_dict["timestamp"]:
                    stats_dict["timestamp"] = datetime.fromisoformat(stats_dict["timestamp"])
                self.usage_history.append(TokenUsageStats(**stats_dict))
            
            # Load alerts
            self.alerts = data.get("alerts", [])
            
            logger.info(f"Loaded usage statistics with {len(self.usage_history)} historical records")
            
        except Exception as e:
            logger.error(f"Failed to load usage statistics: {e}")

class TokenOptimizer:
    """Main token optimization system coordinator."""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.memory_manager = ConversationMemoryManager(self.config)
        self.usage_monitor = TokenUsageMonitor(self.config)
        self.state = ConversationState.ACTIVE
        self.session_id = self._generate_session_id()
        
        # Background processing
        self._background_thread = None
        self._shutdown_event = threading.Event()
        
        if self.config.background_processing:
            self._start_background_processing()
        
        logger.info(f"TokenOptimizer initialized with session ID: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"autocrate_{timestamp}_{os.getpid()}"
    
    def record_conversation_turn(self, input_content: str, output_content: str, 
                               input_tokens: int, output_tokens: int) -> int:
        """Record a complete conversation turn."""
        turn_id = self.memory_manager.total_turns + 1
        
        # Create conversation turn
        turn = ConversationTurn.from_content(
            turn_id, input_content, output_content, input_tokens, output_tokens
        )
        
        # Add to memory manager
        self.memory_manager.add_turn(turn)
        
        # Record usage statistics
        self.usage_monitor.record_usage(input_tokens, output_tokens, turn_id)
        
        logger.debug(f"Recorded conversation turn {turn_id} with {input_tokens + output_tokens} tokens")
        
        return turn_id
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Simple estimation: ~4 characters per token for English text
        # This is a rough approximation - real tokenization would be more accurate
        return max(1, len(text) // 4)
    
    def should_summarize(self) -> bool:
        """Check if conversation should be summarized."""
        usage = self.usage_monitor.get_current_usage()
        memory_usage = self.memory_manager.get_memory_usage()
        
        return (
            usage["usage_ratio"] > self.config.warning_threshold or
            memory_usage["active_turns"] >= self.config.summarization_trigger_turns
        )
    
    def should_prune(self) -> bool:
        """Check if old conversations should be pruned."""
        if not self.config.auto_prune_enabled:
            return False
        
        memory_usage = self.memory_manager.get_memory_usage()
        return memory_usage["archived_turns"] > self.config.max_turns_in_memory * 2
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization operations."""
        results = {
            "summarization_performed": False,
            "pruning_performed": False,
            "tokens_saved": 0,
            "turns_processed": 0
        }
        
        # Get initial state
        initial_usage = self.memory_manager.get_memory_usage()
        
        # Perform summarization if needed
        if self.should_summarize():
            self.state = ConversationState.SUMMARIZING
            self.memory_manager._trigger_summarization()
            results["summarization_performed"] = True
            logger.info("Performed conversation summarization")
        
        # Perform pruning if needed
        if self.should_prune():
            self.state = ConversationState.PRUNING
            pruned_count = self.memory_manager.prune_old_conversations()
            results["pruning_performed"] = True
            results["turns_processed"] = pruned_count
            logger.info(f"Performed conversation pruning - removed {pruned_count} turns")
        
        # Calculate tokens saved
        final_usage = self.memory_manager.get_memory_usage()
        results["tokens_saved"] = initial_usage["total_tokens"] - final_usage["total_tokens"]
        
        self.state = ConversationState.ACTIVE
        return results
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate a comprehensive optimization report."""
        usage_stats = self.usage_monitor.get_current_usage()
        memory_stats = self.memory_manager.get_memory_usage()
        
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value,
            "token_usage": usage_stats,
            "memory_usage": memory_stats,
            "optimization_recommendations": self._get_recommendations(usage_stats, memory_stats),
            "config": asdict(self.config)
        }
        
        return report
    
    def _get_recommendations(self, usage_stats: Dict, memory_stats: Dict) -> List[Dict[str, str]]:
        """Generate optimization recommendations."""
        recommendations = []
        
        usage_ratio = usage_stats.get("usage_ratio", 0)
        
        if usage_ratio > self.config.critical_threshold:
            recommendations.append({
                "priority": "high",
                "action": "immediate_summarization",
                "description": "Critical token usage - immediate summarization required"
            })
        elif usage_ratio > self.config.warning_threshold:
            recommendations.append({
                "priority": "medium", 
                "action": "schedule_summarization",
                "description": "High token usage - schedule summarization soon"
            })
        
        if memory_stats["active_turns"] > self.config.max_turns_in_memory:
            recommendations.append({
                "priority": "medium",
                "action": "memory_pruning",
                "description": f"Too many active turns ({memory_stats['active_turns']}) - consider pruning"
            })
        
        compression_ratio = memory_stats.get("compression_ratio", 1.0)
        if compression_ratio > 0.5:
            recommendations.append({
                "priority": "low",
                "action": "improve_summarization",
                "description": f"Low compression ratio ({compression_ratio:.2f}) - improve summarization strategy"
            })
        
        return recommendations
    
    def _start_background_processing(self) -> None:
        """Start background processing thread."""
        self._background_thread = threading.Thread(target=self._background_worker, daemon=True)
        self._background_thread.start()
        logger.info("Background processing thread started")
    
    def _background_worker(self) -> None:
        """Background worker for periodic tasks."""
        save_interval = self.config.save_interval_minutes * 60  # Convert to seconds
        
        while not self._shutdown_event.is_set():
            try:
                # Periodic saves
                self.memory_manager._save_state()
                self.usage_monitor._save_stats()
                
                # Auto-optimization
                if self.should_summarize() or self.should_prune():
                    self.optimize_memory()
                
                # Wait for next interval or shutdown
                self._shutdown_event.wait(save_interval)
                
            except Exception as e:
                logger.error(f"Background processing error: {e}")
                self._shutdown_event.wait(60)  # Wait 1 minute before retry
    
    def shutdown(self) -> None:
        """Shutdown the optimizer and save state."""
        logger.info("Shutting down TokenOptimizer")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for background thread
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=5.0)
        
        # Final save
        try:
            self.memory_manager._save_state()
            self.usage_monitor._save_stats()
        except Exception as e:
            logger.error(f"Error during final save: {e}")
        
        logger.info("TokenOptimizer shutdown complete")

# Convenience functions for easy integration
def create_optimizer(config: Optional[Dict[str, Any]] = None) -> TokenOptimizer:
    """Create a token optimizer with optional configuration."""
    if config:
        opt_config = OptimizationConfig(**config)
    else:
        opt_config = OptimizationConfig()
    
    return TokenOptimizer(opt_config)

def estimate_tokens(text: str) -> int:
    """Quick token estimation for text."""
    return max(1, len(text) // 4)

def get_default_config() -> Dict[str, Any]:
    """Get the default optimization configuration."""
    return asdict(OptimizationConfig())

# Export main classes and functions
__all__ = [
    'TokenOptimizer',
    'OptimizationConfig', 
    'ConversationMemoryManager',
    'TokenUsageMonitor',
    'ConversationTurn',
    'TokenUsageStats',
    'TokenUsageLevel',
    'ConversationState',
    'create_optimizer',
    'estimate_tokens',
    'get_default_config'
]

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)
    
    # Create optimizer with custom config
    config = OptimizationConfig(
        max_tokens_per_conversation=50000,
        warning_threshold=0.7,
        max_turns_in_memory=30
    )
    
    optimizer = TokenOptimizer(config)
    
    # Simulate some conversation turns
    for i in range(10):
        input_text = f"This is test input number {i}" * 10
        output_text = f"This is test output number {i}" * 15
        
        input_tokens = optimizer.estimate_tokens(input_text)
        output_tokens = optimizer.estimate_tokens(output_text)
        
        turn_id = optimizer.record_conversation_turn(
            input_text, output_text, input_tokens, output_tokens
        )
        print(f"Recorded turn {turn_id}")
    
    # Generate report
    report = optimizer.get_optimization_report()
    print("\nOptimization Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Cleanup
    optimizer.shutdown()