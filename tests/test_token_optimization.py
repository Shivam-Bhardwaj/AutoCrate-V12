#!/usr/bin/env python3
"""
Test suite for AutoCrate Token Optimization System
Comprehensive tests for token tracking, conversation management, and AI integration.

Author: AutoCrate Development Team
Created: August 2025
Version: 1.0.0
"""

import pytest
import tempfile
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
# Add scripts directory to path for imports
scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from token_optimizer import (
    TokenOptimizer, OptimizationConfig, TokenUsageStats, 
    ConversationTurn, TokenUsageLevel
)
from conversation_state_manager import (
    ConversationStateManager, ConversationSession, ConversationMessage,
    MessageRole, ConversationStatus
)
from autocrate_ai_integration import AutoCrateAI, AutoCrateWorkflowAI
from token_utils import ConfigManager, TokenAnalyzer, PerformanceMonitor, IntegrationTester

class TestTokenOptimizer:
    """Test cases for TokenOptimizer class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config(self, temp_dir):
        """Create test configuration."""
        return OptimizationConfig(
            max_tokens_per_conversation=10000,
            warning_threshold=0.7,
            critical_threshold=0.9,
            data_directory=temp_dir,
            background_processing=False  # Disable for tests
        )
    
    @pytest.fixture  
    def optimizer(self, config):
        """Create TokenOptimizer instance for testing."""
        optimizer = TokenOptimizer(config)
        yield optimizer
        optimizer.shutdown()
    
    def test_optimizer_initialization(self, optimizer, config):
        """Test that optimizer initializes correctly."""
        assert optimizer.config.max_tokens_per_conversation == config.max_tokens_per_conversation
        assert optimizer.config.warning_threshold == config.warning_threshold
        assert optimizer.memory_manager is not None
        assert optimizer.usage_monitor is not None
    
    def test_record_conversation_turn(self, optimizer):
        """Test recording conversation turns."""
        turn_id = optimizer.record_conversation_turn(
            "Test input", "Test output", 100, 150
        )
        
        assert turn_id == 1
        assert optimizer.memory_manager.total_turns == 1
        
        # Record another turn
        turn_id2 = optimizer.record_conversation_turn(
            "Second input", "Second output", 200, 250  
        )
        
        assert turn_id2 == 2
        assert optimizer.memory_manager.total_turns == 2
    
    def test_token_estimation(self, optimizer):
        """Test token estimation functionality."""
        text = "This is a test message with some content."
        estimated = optimizer.estimate_tokens(text)
        
        assert estimated > 0
        assert isinstance(estimated, int)
        # Rough check - should be approximately len(text) / 4
        expected_range = (len(text) // 6, len(text) // 2)
        assert expected_range[0] <= estimated <= expected_range[1]
    
    def test_should_summarize_conditions(self, optimizer):
        """Test conditions that trigger summarization."""
        # Initially should not need summarization
        assert not optimizer.should_summarize()
        
        # Add many turns to trigger summarization
        for i in range(25):  # More than summarization_trigger_turns
            optimizer.record_conversation_turn(
                f"Input {i}", f"Output {i}", 200, 300
            )
        
        # Now should trigger summarization
        assert optimizer.should_summarize()
    
    def test_optimization_report(self, optimizer):
        """Test optimization report generation."""
        # Record some conversation turns
        for i in range(5):
            optimizer.record_conversation_turn(
                f"Input {i}", f"Output {i}", 100, 150
            )
        
        report = optimizer.get_optimization_report()
        
        assert "session_id" in report
        assert "timestamp" in report
        assert "token_usage" in report
        assert "memory_usage" in report
        assert "optimization_recommendations" in report
        
        # Check token usage
        assert report["token_usage"]["total"] == 1250  # 5 turns * 250 tokens each
    
    def test_memory_optimization(self, optimizer):
        """Test memory optimization functionality."""
        # Add enough turns to trigger optimization
        for i in range(30):
            optimizer.record_conversation_turn(
                f"Long input message {i}" * 10, 
                f"Long output response {i}" * 15, 
                100, 150
            )
        
        result = optimizer.optimize_memory()
        
        assert "summarization_performed" in result
        assert "pruning_performed" in result
        assert isinstance(result["tokens_saved"], int)

class TestConversationStateManager:
    """Test cases for ConversationStateManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Create ConversationStateManager for testing."""
        manager = ConversationStateManager(
            data_directory=temp_dir,
            max_active_sessions=3,
            auto_save_interval=1  # Short interval for testing
        )
        yield manager
        manager.shutdown()
    
    def test_session_creation(self, state_manager):
        """Test creating conversation sessions."""
        session_id = state_manager.create_session(
            project_name="Test Project",
            task_description="Testing session creation"
        )
        
        assert session_id is not None
        assert session_id in state_manager.active_sessions
        assert state_manager.current_session is not None
        assert state_manager.current_session.session_id == session_id
    
    def test_message_handling(self, state_manager):
        """Test adding and retrieving messages."""
        session_id = state_manager.create_session(project_name="Test")
        
        # Add user message
        user_msg_id = state_manager.add_message(
            "Hello, I need help with AutoCrate",
            MessageRole.USER
        )
        
        # Add assistant message
        assistant_msg_id = state_manager.add_message(
            "I'd be happy to help with AutoCrate!",
            MessageRole.ASSISTANT
        )
        
        messages = state_manager.get_session_messages()
        
        assert len(messages) >= 2  # Plus system message
        assert any(msg.role == MessageRole.USER for msg in messages)
        assert any(msg.role == MessageRole.ASSISTANT for msg in messages)
    
    def test_session_switching(self, state_manager):
        """Test switching between sessions."""
        # Create first session
        session1 = state_manager.create_session(project_name="Project 1")
        
        # Create second session
        session2 = state_manager.create_session(project_name="Project 2")
        
        assert state_manager.current_session.session_id == session2
        
        # Switch back to first session
        success = state_manager.switch_session(session1)
        
        assert success
        assert state_manager.current_session.session_id == session1
    
    def test_session_statistics(self, state_manager):
        """Test session statistics calculation."""
        session_id = state_manager.create_session(project_name="Stats Test")
        
        # Add some messages
        for i in range(5):
            state_manager.add_message(f"Message {i}", MessageRole.USER)
            state_manager.add_message(f"Response {i}", MessageRole.ASSISTANT)
        
        stats = state_manager.get_session_statistics()
        
        assert stats["session_id"] == session_id
        assert "message_count" in stats
        assert "token_usage" in stats
        assert stats["message_count"] >= 10  # 5 pairs + system messages
    
    def test_session_archiving(self, state_manager):
        """Test session archiving functionality."""
        session_id = state_manager.create_session(project_name="Archive Test")
        
        # Add a message
        state_manager.add_message("Test message", MessageRole.USER)
        
        # Archive the session
        success = state_manager.archive_session(session_id)
        
        assert success
        assert session_id not in state_manager.active_sessions
        assert state_manager.current_session is None

class TestAutocrateAI:
    """Test cases for AutoCrateAI integration class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def ai_assistant(self, temp_dir):
        """Create AutoCrateAI instance for testing."""
        ai = AutoCrateAI(
            project_name="Test Project",
            working_directory=temp_dir,
            config={
                'max_tokens': 10000,
                'auto_optimize': False,  # Disable for tests
                'background_processing': False
            }
        )
        yield ai
        ai.shutdown()
    
    def test_ai_initialization(self, ai_assistant, temp_dir):
        """Test AI assistant initialization."""
        assert ai_assistant.project_name == "Test Project"
        assert ai_assistant.working_directory == temp_dir
        assert ai_assistant.token_optimizer is not None
        assert ai_assistant.state_manager is not None
        assert ai_assistant.current_session_id is not None
    
    def test_chat_functionality(self, ai_assistant):
        """Test chat functionality."""
        result = ai_assistant.chat("I need help with crate design")
        
        assert "user_message_id" in result
        assert "assistant_message_id" in result  
        assert "assistant_response" in result
        assert "session_stats" in result
        assert "token_usage" in result
        
        # Check that response contains relevant content
        response = result["assistant_response"]
        assert len(response) > 0
        assert "crate" in response.lower()
    
    def test_session_management(self, ai_assistant):
        """Test session management functionality."""
        # Create new session
        new_session_id = ai_assistant.start_new_session(
            "New task",
            {"priority": "high"}
        )
        
        assert new_session_id != ai_assistant.current_session_id
        assert ai_assistant.current_session_id == new_session_id
        
        # Get session summary
        summary = ai_assistant.get_session_summary()
        
        assert summary["session_statistics"]["session_id"] == new_session_id
        assert "conversation_topics" in summary
        assert "optimization_status" in summary
    
    def test_conversation_export(self, ai_assistant):
        """Test conversation export functionality."""
        # Add some messages
        ai_assistant.chat("How do I calculate crate dimensions?")
        ai_assistant.chat("What materials should I use?")
        
        export_data = ai_assistant.export_conversation()
        
        assert "export_timestamp" in export_data
        assert "session_statistics" in export_data
        assert "messages" in export_data
        assert len(export_data["messages"]) >= 4  # User + assistant pairs + system
    
    def test_usage_report(self, ai_assistant):
        """Test usage report generation."""
        # Simulate some usage
        for i in range(3):
            ai_assistant.chat(f"Question {i}")
        
        report = ai_assistant.get_usage_report()
        
        assert "overall_statistics" in report
        assert "current_session" in report  
        assert "token_optimization" in report
        assert "recommendations" in report
        
        stats = report["overall_statistics"]
        assert stats["total_interactions"] >= 3
        assert stats["total_tokens_used"] > 0

class TestTokenUtils:
    """Test cases for token utility functions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_config_manager(self, temp_dir):
        """Test configuration management."""
        config_file = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_file)
        
        # Set some values
        manager.set("test_key", "test_value")
        manager.set("number_key", 42)
        
        # Save configuration
        success = manager.save_config()
        assert success
        
        # Create new manager and test loading
        manager2 = ConfigManager(config_file)
        assert manager2.get("test_key") == "test_value"
        assert manager2.get("number_key") == 42
    
    def test_token_analyzer(self):
        """Test token analysis functionality."""
        analyzer = TokenAnalyzer()
        
        test_content = """
        I need to create NX expressions for a crate design.
        The dimensions are 48x36x24 inches.
        ```python
        def calculate_dimensions():
            return width * height * depth
        ```
        What materials should I use?
        """
        
        analysis = analyzer.analyze_content(test_content)
        
        assert "total_characters" in analysis
        assert "estimated_tokens" in analysis
        assert "word_count" in analysis
        assert "patterns_found" in analysis
        assert "complexity_score" in analysis
        
        # Check pattern detection
        patterns = analysis["patterns_found"]
        assert patterns.get("code_blocks", 0) >= 1
        assert patterns.get("technical_terms", 0) >= 1
        assert patterns.get("questions", 0) >= 1
    
    def test_performance_monitor(self, temp_dir):
        """Test performance monitoring."""
        log_file = os.path.join(temp_dir, "perf_test.json")
        monitor = PerformanceMonitor(log_file)
        
        # Record some operations
        monitor.record_operation("test_op1", 0.5, 1000)
        monitor.record_operation("test_op2", 1.2, 2500)
        monitor.record_operation("test_op1", 0.8, 1500)
        
        report = monitor.get_performance_report()
        
        assert report["metric_count"] == 3
        assert "performance" in report
        assert report["performance"]["total_tokens_processed"] == 5000
        assert "test_op1" in report["operations"]
        assert "test_op2" in report["operations"]

class TestIntegrationTester:
    """Test the integration testing utilities."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_integration_tests_run(self, temp_dir):
        """Test that integration tests can be executed."""
        tester = IntegrationTester(temp_dir)
        
        # Run tests (this will test the actual integration)
        results = tester.run_integration_tests()
        
        assert "timestamp" in results
        assert "total_tests" in results
        assert "passed" in results
        assert "failed" in results
        assert "test_details" in results
        assert "overall_status" in results
        
        # Should have run several tests
        assert results["total_tests"] > 0
        assert len(results["test_details"]) == results["total_tests"]
        
        # Most tests should pass (allowing for some environment issues)
        pass_rate = results["passed"] / results["total_tests"]
        assert pass_rate >= 0.5  # At least 50% should pass

class TestRealWorldUsage:
    """Test real-world usage scenarios."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_autocrate_workflow_simulation(self, temp_dir):
        """Simulate a typical AutoCrate development workflow."""
        # Create AI assistant
        ai = AutoCrateAI(
            project_name="Workflow Test",
            working_directory=temp_dir,
            config={'max_tokens': 5000, 'auto_optimize': True}
        )
        
        try:
            # Simulate development workflow
            workflow_messages = [
                "I need to create a crate for a 96x48x24 product weighing 2000 lbs",
                "What plywood thickness should I use for this weight?",
                "Generate the NX expressions for this crate design",
                "How can I optimize the material usage?",
                "Run tests to verify the calculations",
                "Export the final design specifications"
            ]
            
            responses = []
            for message in workflow_messages:
                result = ai.chat(message)
                responses.append(result)
                
                # Small delay to simulate real usage
                time.sleep(0.1)
            
            # Verify workflow results
            assert len(responses) == len(workflow_messages)
            
            # Check that responses are relevant
            for i, result in enumerate(responses):
                assert len(result["assistant_response"]) > 50
                assert "autocrate" in result["assistant_response"].lower() or \
                       "crate" in result["assistant_response"].lower()
            
            # Get final usage report
            report = ai.get_usage_report()
            stats = report["overall_statistics"]
            
            assert stats["total_interactions"] >= len(workflow_messages)
            assert stats["session_duration_hours"] > 0
            assert stats["total_tokens_used"] > 0
            
            # Test optimization if it was triggered
            if stats.get("optimizations_performed", 0) > 0:
                assert "recommendations" in report
        
        finally:
            ai.shutdown()
    
    def test_memory_management_under_load(self, temp_dir):
        """Test memory management under simulated load."""
        config = OptimizationConfig(
            max_tokens_per_conversation=5000,  # Low limit for testing
            warning_threshold=0.6,
            critical_threshold=0.8,
            data_directory=temp_dir,
            background_processing=False
        )
        
        optimizer = TokenOptimizer(config)
        
        try:
            # Generate load that will trigger optimization
            for i in range(50):
                input_text = f"Test input {i} " * 20  # Large messages
                output_text = f"Test output {i} " * 30
                
                optimizer.record_conversation_turn(
                    input_text, output_text,
                    len(input_text) // 4, len(output_text) // 4
                )
                
                # Check if optimization was triggered
                if i % 10 == 0:
                    if optimizer.should_summarize():
                        result = optimizer.optimize_memory()
                        assert result["summarization_performed"] or result["pruning_performed"]
            
            # Final report should show optimization occurred
            report = optimizer.get_optimization_report()
            memory_usage = report["memory_usage"]
            
            # Should have some archived turns or summaries
            assert memory_usage["archived_turns"] > 0 or memory_usage["summaries_count"] > 0
        
        finally:
            optimizer.shutdown()

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])