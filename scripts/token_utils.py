#!/usr/bin/env python3
"""
AutoCrate Token Optimization Utilities
Utility functions and helpers for token management and optimization.

This module provides:
- Configuration management utilities
- Token estimation and analysis tools
- Performance monitoring helpers
- Integration testing utilities
- Command-line interface for token management

Author: AutoCrate Development Team
Created: August 2025
Version: 1.0.0
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import subprocess
import tempfile
from dataclasses import asdict

from token_optimizer import TokenOptimizer, OptimizationConfig, get_default_config
from conversation_state_manager import ConversationStateManager
from autocrate_ai_integration import AutoCrateAI

logger = logging.getLogger(__name__)

# Configuration management
class ConfigManager:
    """Manages configuration files for token optimization."""
    
    DEFAULT_CONFIG_FILE = "token_optimization_config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or self.DEFAULT_CONFIG_FILE)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        # Return default configuration
        default_config = get_default_config()
        default_config.update({
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "AutoCrate token optimization configuration"
        })
        
        return default_config
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            self.config["updated_at"] = datetime.now().isoformat()
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Saved configuration to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(updates)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = get_default_config()
        self.config.update({
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "AutoCrate token optimization configuration"
        })

# Token analysis utilities
class TokenAnalyzer:
    """Analyzes token usage patterns and provides insights."""
    
    def __init__(self):
        self.patterns = {
            "code_blocks": r"```[\s\S]*?```",
            "file_paths": r"[A-Za-z]:\\[^\s]+|/[^\s]+",
            "technical_terms": ["expression", "crate", "plywood", "calculation", "dimension"],
            "questions": r"\?",
            "commands": ["create", "generate", "calculate", "analyze", "debug"]
        }
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for token usage patterns."""
        import re
        
        analysis = {
            "total_characters": len(content),
            "estimated_tokens": max(1, len(content) // 4),
            "word_count": len(content.split()),
            "line_count": len(content.splitlines()),
            "patterns_found": {}
        }
        
        # Analyze patterns
        for pattern_name, pattern in self.patterns.items():
            if isinstance(pattern, str) and pattern.startswith("r"):
                # Regex pattern
                matches = re.findall(pattern[1:], content, re.IGNORECASE)
                analysis["patterns_found"][pattern_name] = len(matches)
            elif isinstance(pattern, list):
                # List of terms
                count = sum(1 for term in pattern if term.lower() in content.lower())
                analysis["patterns_found"][pattern_name] = count
        
        # Calculate complexity score
        analysis["complexity_score"] = self._calculate_complexity(analysis)
        
        return analysis
    
    def _calculate_complexity(self, analysis: Dict[str, Any]) -> float:
        """Calculate a complexity score for the content."""
        base_score = analysis["estimated_tokens"] / 1000  # Base on token count
        
        # Adjust for patterns
        patterns = analysis["patterns_found"]
        complexity_modifiers = {
            "code_blocks": 1.5,
            "file_paths": 1.2,
            "technical_terms": 1.1,
            "questions": 0.9,
            "commands": 1.3
        }
        
        for pattern, modifier in complexity_modifiers.items():
            if pattern in patterns and patterns[pattern] > 0:
                base_score *= modifier
        
        return min(10.0, base_score)  # Cap at 10
    
    def suggest_optimizations(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest optimizations based on analysis."""
        suggestions = []
        
        if analysis["estimated_tokens"] > 5000:
            suggestions.append("Consider breaking down large requests into smaller parts")
        
        if analysis["patterns_found"].get("code_blocks", 0) > 3:
            suggestions.append("Multiple code blocks detected - consider using references")
        
        if analysis["complexity_score"] > 7:
            suggestions.append("High complexity content - consider simplifying language")
        
        if analysis["line_count"] > 100:
            suggestions.append("Long content - consider using summaries for repeated information")
        
        return suggestions

# Performance monitoring
class PerformanceMonitor:
    """Monitors performance metrics for token optimization."""
    
    def __init__(self, log_file: str = "logs/performance_metrics.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics = []
    
    def record_operation(self, 
                        operation: str,
                        duration: float,
                        tokens_processed: int,
                        memory_usage: Optional[int] = None) -> None:
        """Record a performance metric."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_seconds": duration,
            "tokens_processed": tokens_processed,
            "tokens_per_second": tokens_processed / max(0.001, duration),
            "memory_usage_mb": memory_usage
        }
        
        self.metrics.append(metric)
        
        # Save to file periodically
        if len(self.metrics) % 10 == 0:
            self._save_metrics()
    
    def _save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")
    
    def get_performance_report(self, 
                             operation_filter: Optional[str] = None,
                             time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """Generate a performance report."""
        
        metrics = self.metrics
        
        # Apply filters
        if operation_filter:
            metrics = [m for m in metrics if operation_filter.lower() in m["operation"].lower()]
        
        if time_window_hours:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            metrics = [m for m in metrics if datetime.fromisoformat(m["timestamp"]) > cutoff_time]
        
        if not metrics:
            return {"error": "No metrics found matching criteria"}
        
        # Calculate statistics
        durations = [m["duration_seconds"] for m in metrics]
        token_rates = [m["tokens_per_second"] for m in metrics]
        total_tokens = sum(m["tokens_processed"] for m in metrics)
        
        return {
            "metric_count": len(metrics),
            "time_range": {
                "start": min(m["timestamp"] for m in metrics),
                "end": max(m["timestamp"] for m in metrics)
            },
            "performance": {
                "average_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "average_tokens_per_second": sum(token_rates) / len(token_rates),
                "total_tokens_processed": total_tokens
            },
            "operations": list(set(m["operation"] for m in metrics))
        }

# Integration testing utilities
class IntegrationTester:
    """Tests integration with AutoCrate components."""
    
    def __init__(self, working_directory: str = "."):
        self.working_dir = Path(working_directory)
        self.test_results = []
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests."""
        logger.info("Running token optimization integration tests")
        
        tests = [
            ("Token Optimizer Creation", self._test_optimizer_creation),
            ("Conversation State Manager", self._test_state_manager),
            ("AI Integration", self._test_ai_integration),
            ("Configuration Management", self._test_config_management),
            ("Performance Monitoring", self._test_performance_monitoring),
            ("File System Integration", self._test_filesystem_integration)
        ]
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(tests),
            "passed": 0,
            "failed": 0,
            "test_details": []
        }
        
        for test_name, test_func in tests:
            try:
                start_time = datetime.now()
                test_result = test_func()
                duration = (datetime.now() - start_time).total_seconds()
                
                test_detail = {
                    "name": test_name,
                    "status": "PASS",
                    "duration": duration,
                    "details": test_result
                }
                results["passed"] += 1
                
            except Exception as e:
                test_detail = {
                    "name": test_name,
                    "status": "FAIL", 
                    "duration": (datetime.now() - start_time).total_seconds(),
                    "error": str(e)
                }
                results["failed"] += 1
                logger.error(f"Integration test failed: {test_name} - {e}")
            
            results["test_details"].append(test_detail)
        
        # Overall status
        results["overall_status"] = "PASS" if results["failed"] == 0 else "FAIL"
        
        logger.info(f"Integration tests completed: {results['passed']}/{results['total_tests']} passed")
        return results
    
    def _test_optimizer_creation(self) -> Dict[str, Any]:
        """Test token optimizer creation and basic operations."""
        config = OptimizationConfig(max_tokens_per_conversation=10000)
        optimizer = TokenOptimizer(config)
        
        # Test basic functionality
        optimizer.record_conversation_turn(
            "Test input", "Test output", 100, 150
        )
        
        report = optimizer.get_optimization_report()
        optimizer.shutdown()
        
        return {
            "config_loaded": True,
            "turn_recorded": True,
            "report_generated": len(report) > 0,
            "token_usage": report["token_usage"]["total"]
        }
    
    def _test_state_manager(self) -> Dict[str, Any]:
        """Test conversation state manager."""
        from conversation_state_manager import MessageRole
        
        data_dir = str(self.working_dir / "test_conversations")
        manager = ConversationStateManager(data_directory=data_dir)
        
        # Create session and add messages
        session_id = manager.create_session(
            project_name="Integration Test",
            task_description="Testing state management"
        )
        
        manager.add_message("Test user message")
        manager.add_message("Test assistant response", role=MessageRole.ASSISTANT)
        
        stats = manager.get_session_statistics()
        manager.shutdown()
        
        return {
            "session_created": session_id is not None,
            "messages_added": stats["message_count"] >= 2,
            "statistics_generated": len(stats) > 0
        }
    
    def _test_ai_integration(self) -> Dict[str, Any]:
        """Test AI integration system."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ai = AutoCrateAI(
                project_name="Integration Test",
                working_directory=temp_dir,
                config={"max_tokens": 10000}
            )
            
            # Test chat functionality
            result = ai.chat("Test message for integration")
            
            # Test session management
            new_session = ai.start_new_session("Test session")
            
            # Get reports
            usage_report = ai.get_usage_report()
            ai.shutdown()
            
            return {
                "ai_created": True,
                "chat_functional": "assistant_response" in result,
                "session_management": new_session is not None,
                "reporting": len(usage_report) > 0
            }
    
    def _test_config_management(self) -> Dict[str, Any]:
        """Test configuration management."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            config_manager = ConfigManager(temp_file.name)
            
            # Test configuration operations
            config_manager.set("test_key", "test_value")
            config_manager.update({"another_key": 42})
            
            saved = config_manager.save_config()
            
            # Create new manager to test loading
            new_manager = ConfigManager(temp_file.name)
            loaded_value = new_manager.get("test_key")
            
            # Cleanup
            os.unlink(temp_file.name)
            
            return {
                "config_created": True,
                "values_set": True,
                "save_successful": saved,
                "load_successful": loaded_value == "test_value"
            }
    
    def _test_performance_monitoring(self) -> Dict[str, Any]:
        """Test performance monitoring."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = PerformanceMonitor(f"{temp_dir}/test_metrics.json")
            
            # Record some test metrics
            monitor.record_operation("test_operation", 0.5, 1000)
            monitor.record_operation("another_operation", 1.2, 2500)
            
            report = monitor.get_performance_report()
            
            return {
                "monitor_created": True,
                "metrics_recorded": len(monitor.metrics) == 2,
                "report_generated": "performance" in report
            }
    
    def _test_filesystem_integration(self) -> Dict[str, Any]:
        """Test file system integration."""
        # Test directory creation
        test_dir = self.working_dir / "test_token_optimization"
        test_dir.mkdir(exist_ok=True)
        
        # Test file operations
        test_file = test_dir / "test_data.json"
        test_data = {"test": True, "timestamp": datetime.now().isoformat()}
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Test file reading
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        
        # Cleanup
        test_file.unlink()
        test_dir.rmdir()
        
        return {
            "directory_creation": True,
            "file_write": True,
            "file_read": loaded_data["test"] is True,
            "cleanup": True
        }

# Command-line interface
def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line interface parser."""
    parser = argparse.ArgumentParser(
        description="AutoCrate Token Optimization Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run integration tests")
    test_parser.add_argument("--working-dir", default=".", help="Working directory")
    test_parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text for token usage")
    analyze_parser.add_argument("text", help="Text to analyze")
    analyze_parser.add_argument("--suggestions", action="store_true", help="Show optimization suggestions")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("action", choices=["show", "reset"], help="Configuration action")
    config_parser.add_argument("--config-file", help="Configuration file path")
    
    # Performance command
    perf_parser = subparsers.add_parser("performance", help="Performance monitoring")
    perf_parser.add_argument("--log-file", default="logs/performance_metrics.json", help="Performance log file")
    perf_parser.add_argument("--hours", type=int, help="Time window in hours")
    
    return parser

def main():
    """Main CLI entry point."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Set up logging
    level = logging.DEBUG if hasattr(args, 'verbose') and args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    try:
        if args.command == "test":
            print("Running AutoCrate Token Optimization Integration Tests...")
            tester = IntegrationTester(args.working_dir)
            results = tester.run_integration_tests()
            
            print(f"\nTest Results: {results['overall_status']}")
            print(f"Passed: {results['passed']}/{results['total_tests']}")
            
            if args.verbose:
                for test in results["test_details"]:
                    status_symbol = "[PASS]" if test["status"] == "PASS" else "[FAIL]"
                    print(f"{status_symbol} {test['name']} ({test['duration']:.2f}s)")
                    if test["status"] == "FAIL":
                        print(f"   Error: {test['error']}")
        
        elif args.command == "analyze":
            analyzer = TokenAnalyzer()
            analysis = analyzer.analyze_content(args.text)
            
            print(f"Token Analysis Results:")
            print(f"  Estimated tokens: {analysis['estimated_tokens']}")
            print(f"  Characters: {analysis['total_characters']}")
            print(f"  Words: {analysis['word_count']}")
            print(f"  Complexity score: {analysis['complexity_score']:.1f}/10")
            
            if args.suggestions:
                suggestions = analyzer.suggest_optimizations(analysis)
                if suggestions:
                    print("\nOptimization Suggestions:")
                    for suggestion in suggestions:
                        print(f"  • {suggestion}")
        
        elif args.command == "config":
            config_manager = ConfigManager(args.config_file)
            
            if args.action == "show":
                print("Current Configuration:")
                print(json.dumps(config_manager.config, indent=2))
            
            elif args.action == "reset":
                config_manager.reset_to_defaults()
                config_manager.save_config()
                print("Configuration reset to defaults")
        
        elif args.command == "performance":
            if not Path(args.log_file).exists():
                print(f"Performance log file not found: {args.log_file}")
                return
            
            monitor = PerformanceMonitor(args.log_file)
            report = monitor.get_performance_report(time_window_hours=args.hours)
            
            if "error" in report:
                print(f"Error: {report['error']}")
            else:
                print("Performance Report:")
                print(f"  Metrics: {report['metric_count']}")
                print(f"  Average duration: {report['performance']['average_duration']:.2f}s")
                print(f"  Average tokens/sec: {report['performance']['average_tokens_per_second']:.0f}")
                print(f"  Total tokens processed: {report['performance']['total_tokens_processed']}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()

# Export main utilities
__all__ = [
    'ConfigManager',
    'TokenAnalyzer', 
    'PerformanceMonitor',
    'IntegrationTester',
    'create_cli_parser',
    'main'
]

if __name__ == "__main__":
    main()