# AutoCrate Token Usage Optimization System

A comprehensive token management and optimization system designed specifically for AutoCrate development workflows. This system helps prevent running out of tokens during AI-assisted development sessions and provides intelligent resource management.

## 🎯 Overview

The AutoCrate Token Optimization System provides:

- **Token Usage Tracking**: Real-time monitoring of token consumption
- **Conversation Memory Management**: Automatic summarization and archiving
- **AI Integration**: Seamless integration with AutoCrate workflows  
- **Performance Monitoring**: Detailed metrics and reporting
- **Production-Ready**: Robust error handling and configuration management

## 📁 System Components

### Core Modules

1. **`token_optimizer.py`** - Main token tracking and optimization engine
2. **`conversation_state_manager.py`** - Lightweight conversation state management
3. **`autocrate_ai_integration.py`** - AI integration for AutoCrate workflows
4. **`token_utils.py`** - Configuration management and utility functions

### Key Features

#### Token Optimizer (`TokenOptimizer`)
- Tracks token usage per conversation turn
- Implements automatic conversation summarization
- Provides configurable thresholds and alerts
- Supports background processing and persistence

#### Conversation State Manager (`ConversationStateManager`)
- Manages multiple conversation sessions
- Preserves context across interactions
- Handles session archiving and cleanup
- Thread-safe operations

#### AutoCrate AI Integration (`AutoCrateAI`)
- Easy-to-use AI interface for AutoCrate
- Context-aware conversation handling
- Built-in optimization triggers
- Comprehensive usage reporting

## 🚀 Quick Start

### Basic Usage

```python
from scripts.autocrate_ai_integration import create_ai_assistant

# Create AI assistant with optimization
ai = create_ai_assistant(
    project_name="My AutoCrate Project",
    max_tokens=50000,
    auto_optimize=True
)

# Use for AI interactions
result = ai.chat("I need to design a crate for 96x48x24 equipment")
print(result["assistant_response"])

# Get usage statistics
report = ai.get_usage_report()
print(f"Tokens used: {report['overall_statistics']['total_tokens_used']}")

# Clean shutdown
ai.shutdown()
```

### Manual Token Optimization

```python
from scripts.token_optimizer import TokenOptimizer, OptimizationConfig

# Configure optimizer
config = OptimizationConfig(
    max_tokens_per_conversation=25000,
    warning_threshold=0.75,
    critical_threshold=0.9
)

optimizer = TokenOptimizer(config)

# Record conversation turns
turn_id = optimizer.record_conversation_turn(
    user_input="How do I calculate crate dimensions?",
    assistant_output="To calculate crate dimensions...",
    input_tokens=10,
    output_tokens=50
)

# Get optimization report
report = optimizer.get_optimization_report()
print(f"Usage: {report['token_usage']['usage_ratio']:.1%}")

optimizer.shutdown()
```

### Conversation Management

```python
from scripts.conversation_state_manager import ConversationStateManager, MessageRole

# Create state manager
manager = ConversationStateManager(data_directory="my_conversations")

# Create session
session_id = manager.create_session(
    project_name="Crate Design Project",
    task_description="Design shipping crate for industrial equipment"
)

# Add messages
manager.add_message("What materials should I use?", MessageRole.USER)
manager.add_message("I recommend 3/4 inch plywood...", MessageRole.ASSISTANT)

# Get session stats
stats = manager.get_session_statistics()
print(f"Messages: {stats['message_count']}, Tokens: {stats['token_usage']['total']}")

manager.shutdown()
```

## ⚙️ Configuration

### Default Configuration

```python
# Default OptimizationConfig settings
config = {
    "max_tokens_per_conversation": 100000,
    "warning_threshold": 0.75,        # Warn at 75%
    "critical_threshold": 0.9,        # Critical at 90%
    "max_turns_in_memory": 50,
    "summarization_trigger_turns": 20,
    "auto_prune_enabled": True,
    "prune_threshold_days": 7,
    "background_processing": True,
    "data_directory": "logs/token_optimization"
}
```

### Custom Configuration

```python
from scripts.token_utils import ConfigManager

# Load/create configuration
config_manager = ConfigManager("my_config.json")

# Set custom values
config_manager.update({
    "max_tokens": 25000,
    "warning_threshold": 0.6,
    "project_settings": {
        "default_plywood_thickness": 0.75,
        "standard_cleat_width": 3.5
    }
})

# Save configuration
config_manager.save_config()
```

## 📊 Monitoring and Reporting

### Usage Reports

The system provides comprehensive usage reports:

```python
# Get detailed usage report
ai = create_ai_assistant("My Project")
# ... use the AI ...
report = ai.get_usage_report()

print(f"Session Duration: {report['overall_statistics']['session_duration_hours']:.2f} hours")
print(f"Total Interactions: {report['overall_statistics']['total_interactions']}")
print(f"Total Tokens: {report['overall_statistics']['total_tokens_used']}")
print(f"Optimizations: {report['overall_statistics']['optimizations_performed']}")
```

### Performance Monitoring

```python
from scripts.token_utils import PerformanceMonitor

monitor = PerformanceMonitor("performance_log.json")

# Record operations
monitor.record_operation("crate_calculation", duration=1.5, tokens_processed=500)

# Generate report
report = monitor.get_performance_report()
print(f"Average tokens/sec: {report['performance']['average_tokens_per_second']:.0f}")
```

## 🛠️ Command-Line Interface

The system includes a command-line interface for management tasks:

### Run Integration Tests

```bash
cd scripts
python token_utils.py test --working-dir .. --verbose
```

### Analyze Text for Token Usage

```bash
python token_utils.py analyze "Your text content here" --suggestions
```

### Configuration Management

```bash
# Show current configuration
python token_utils.py config show

# Reset to defaults  
python token_utils.py config reset
```

### Performance Analysis

```bash
python token_utils.py performance --log-file logs/performance.json --hours 24
```

## 🔧 Integration with AutoCrate

### In AutoCrate Scripts

```python
# Add to your AutoCrate script
import sys
import os
scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, scripts_dir)

from autocrate_ai_integration import AutoCrateAI

# Create AI assistant for your specific task
ai = AutoCrateAI(
    project_name="NX Expression Generation",
    working_directory=os.getcwd(),
    config={
        'max_tokens': 30000,
        'auto_optimize': True,
        'context_window_size': 30
    }
)

# Use in your workflow
result = ai.chat("Generate expressions for 48x36x24 crate with 1500 lb capacity")

# Add file context
ai.add_file_context(["crate_specs.json", "requirements.txt"])

# Get workflow-specific assistance
workflow_ai = AutoCrateWorkflowAI(ai)
analysis = workflow_ai.analyze_crate_requirements({
    "length": 48, "width": 36, "height": 24,
    "weight": 1500, "material": "plywood"
})

# Cleanup
ai.shutdown()
```

### With Existing AutoCrate Components

The system integrates seamlessly with existing AutoCrate logging:

```python
# Uses AutoCrate's debug_logger if available
from autocrate_ai_integration import AutoCrateAI

ai = AutoCrateAI("Integration Test")
# Logs will appear in standard AutoCrate log files
```

## 📈 Memory Optimization Strategies

### Automatic Summarization

The system automatically summarizes conversations when:
- Token usage exceeds warning threshold (75% by default)
- Number of turns exceeds trigger limit (20 by default)
- Memory usage becomes excessive

### Manual Optimization

```python
# Force optimization
optimizer = TokenOptimizer(config)
result = optimizer.optimize_memory()

print(f"Summarization performed: {result['summarization_performed']}")
print(f"Tokens saved: {result['tokens_saved']}")
```

### Custom Optimization Triggers

```python
# Custom optimization logic
if should_optimize_based_on_custom_logic():
    ai.optimize_memory(force=True)
```

## 🎪 Demo and Examples

Run the comprehensive demonstration:

```bash
cd scripts
python demo_token_optimization.py
```

This demonstrates:
- Basic token optimization
- Conversation state management
- AI integration features
- Token analysis utilities
- Configuration management

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure scripts directory is in Python path
2. **Unicode Issues**: System handles Windows console encoding automatically
3. **File Permissions**: Check write access to log directories
4. **Memory Issues**: Adjust configuration for large conversations

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
import os
os.environ['AUTOCRATE_DEBUG'] = '1'
```

### Log Files

The system creates several log files:
- `logs/token_optimization/` - Token usage data
- `logs/ai_conversations/` - Conversation archives  
- `logs/performance_metrics.json` - Performance data
- `logs/ai_session_report.json` - Final session reports

## 📚 API Reference

### TokenOptimizer

```python
class TokenOptimizer:
    def __init__(self, config: OptimizationConfig)
    def record_conversation_turn(self, input_content: str, output_content: str, 
                               input_tokens: int, output_tokens: int) -> int
    def estimate_tokens(self, text: str) -> int
    def should_summarize(self) -> bool
    def optimize_memory(self) -> Dict[str, Any]
    def get_optimization_report(self) -> Dict[str, Any]
    def shutdown(self) -> None
```

### ConversationStateManager

```python
class ConversationStateManager:
    def __init__(self, data_directory: str, token_optimizer: TokenOptimizer = None)
    def create_session(self, project_name: str, task_description: str = None) -> str
    def switch_session(self, session_id: str) -> bool
    def add_message(self, content: str, role: MessageRole) -> str
    def get_session_statistics(self, session_id: str = None) -> Dict[str, Any]
    def archive_session(self, session_id: str = None) -> bool
    def shutdown(self) -> None
```

### AutoCrateAI

```python
class AutoCrateAI:
    def __init__(self, project_name: str, working_directory: str = None, 
                 config: Dict[str, Any] = None)
    def chat(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]
    def start_new_session(self, task_description: str) -> str
    def get_usage_report(self) -> Dict[str, Any]
    def optimize_memory(self, force: bool = False) -> Dict[str, Any]
    def export_conversation(self, session_id: str = None) -> Dict[str, Any]
    def shutdown(self) -> Dict[str, Any]
```

## 🎯 Production Deployment

### Recommended Settings

For production use with AutoCrate:

```python
production_config = {
    "max_tokens_per_conversation": 75000,  # Conservative limit
    "warning_threshold": 0.7,              # Early warnings
    "critical_threshold": 0.85,            # Conservative critical
    "background_processing": True,         # Enable automation
    "save_interval_minutes": 2,            # Frequent saves
    "compression_ratio_target": 0.25,      # Aggressive compression
    "auto_prune_enabled": True,            # Clean up automatically
    "backup_enabled": True                 # Enable backups
}
```

### Environment Variables

```bash
# Enable debug logging
export AUTOCRATE_DEBUG=1

# Run post-session tests
export AUTOCRATE_RUN_TESTS=1
```

## 🤝 Contributing

The token optimization system is designed to be extensible:

1. **Custom Optimization Strategies**: Implement new optimization algorithms
2. **Additional Storage Backends**: Add support for databases or cloud storage
3. **Enhanced Summarization**: Integrate with advanced AI summarization models
4. **Performance Improvements**: Optimize for specific use cases

## 📄 License

This token optimization system is part of the AutoCrate project and follows the same licensing terms.

---

**System Status: Production Ready**

The AutoCrate Token Usage Optimization System has been thoroughly tested and is ready for production use. It provides robust token management, intelligent optimization, and seamless integration with AutoCrate workflows.

For support or questions, refer to the AutoCrate project documentation or run the integration tests to verify system functionality.