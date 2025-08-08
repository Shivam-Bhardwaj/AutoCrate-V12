#!/usr/bin/env python3
"""
AutoCrate Token Optimization System Demonstration
Shows how to use the token optimization system in practice.

This script demonstrates:
- Basic token optimization setup
- Conversation management
- AI integration with AutoCrate
- Memory optimization strategies
- Usage reporting and monitoring

Author: AutoCrate Development Team
Created: August 2025
Version: 1.0.0
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from token_optimizer import TokenOptimizer, OptimizationConfig
from conversation_state_manager import ConversationStateManager, MessageRole
from autocrate_ai_integration import AutoCrateAI, create_ai_assistant
from token_utils import ConfigManager, TokenAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(message)s'
)
logger = logging.getLogger(__name__)

def demo_basic_token_optimization():
    """Demonstrate basic token optimization functionality."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Token Optimization")
    print("="*60)
    
    # Create configuration
    config = OptimizationConfig(
        max_tokens_per_conversation=5000,
        warning_threshold=0.6,
        critical_threshold=0.8,
        data_directory="demo_data/token_optimization"
    )
    
    # Create optimizer
    optimizer = TokenOptimizer(config)
    
    try:
        print(f"[OK] Created TokenOptimizer with max tokens: {config.max_tokens_per_conversation}")
        
        # Simulate conversation turns
        conversation_data = [
            ("I need to design a crate for shipping industrial equipment", 
             "I can help you design a crate. What are the dimensions and weight of the equipment?"),
            ("The equipment is 96x48x30 inches and weighs 2500 pounds",
             "For equipment of this size and weight, I recommend using 3/4 inch plywood with reinforcement cleats..."),
            ("What spacing should I use for the vertical cleats?",
             "For structural integrity with this load, I recommend 16-inch spacing for vertical cleats..."),
            ("Can you generate the NX expressions for this design?",
             "I'll generate the complete set of NX expressions for your crate design..."),
        ]
        
        print(f"Simulating {len(conversation_data)} conversation turns...")
        
        for i, (user_input, assistant_response) in enumerate(conversation_data, 1):
            input_tokens = len(user_input) // 4  # Rough estimation
            output_tokens = len(assistant_response) // 4
            
            turn_id = optimizer.record_conversation_turn(
                user_input, assistant_response, input_tokens, output_tokens
            )
            
            print(f"  Turn {turn_id}: {input_tokens + output_tokens} tokens")
        
        # Get optimization report
        report = optimizer.get_optimization_report()
        
        print(f"\nToken Usage Summary:")
        print(f"  Total tokens: {report['token_usage']['total_tokens']}")
        print(f"  Conversation turns: {report['token_usage']['conversation_turns']}")
        print(f"  Average per turn: {report['token_usage']['average_per_turn']:.1f}")
        print(f"  Usage ratio: {report['token_usage']['usage_ratio']:.1%}")
        
        # Show recommendations
        recommendations = report['optimization_recommendations']
        if recommendations:
            print(f"\nOptimization Recommendations:")
            for rec in recommendations:
                print(f"  - [{rec['priority'].upper()}] {rec['description']}")
        else:
            print(f"\n[OK] No optimization needed at current usage level")
            
    finally:
        optimizer.shutdown()

def demo_conversation_management():
    """Demonstrate conversation state management."""
    print("\n" + "="*60)
    print("DEMO 2: Conversation State Management")  
    print("="*60)
    
    # Create state manager
    manager = ConversationStateManager(
        data_directory="demo_data/conversations",
        max_active_sessions=3
    )
    
    try:
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session_id = manager.create_session(
                project_name=f"AutoCrate Project {i+1}",
                task_description=f"Designing crate type {i+1}"
            )
            sessions.append(session_id)
            print(f"[OK] Created session {i+1}: {session_id[:8]}...")
        
        # Add messages to different sessions
        test_conversations = {
            0: [
                ("I need to calculate material requirements", MessageRole.USER),
                ("I can help calculate materials. What are your crate dimensions?", MessageRole.ASSISTANT)
            ],
            1: [
                ("How do I optimize plywood layout?", MessageRole.USER),
                ("For plywood optimization, I recommend analyzing the panel arrangement...", MessageRole.ASSISTANT)
            ],
            2: [
                ("Can you debug this NX expression error?", MessageRole.USER),
                ("I'll help debug the expression. Can you share the error details?", MessageRole.ASSISTANT)
            ]
        }
        
        for session_idx, messages in test_conversations.items():
            session_id = sessions[session_idx]
            manager.switch_session(session_id)
            
            for content, role in messages:
                manager.add_message(content, role)
            
            print(f"[OK] Added {len(messages)} messages to session {session_idx+1}")
        
        # Show session statistics
        print(f"\nActive Sessions Summary:")
        active_sessions = manager.list_active_sessions()
        
        for session in active_sessions:
            current_indicator = " (current)" if session["is_current"] else ""
            print(f"  - {session['project_name']}: {session['message_count']} messages, "
                 f"{session['total_tokens']} tokens{current_indicator}")
        
        # Export a conversation
        if sessions:
            print(f"\nExporting first session...")
            context = manager.get_session_context(sessions[0])
            messages = manager.get_session_messages(sessions[0])
            
            print(f"  Project: {context.project_name}")
            print(f"  Task: {context.task_description}")
            print(f"  Messages: {len(messages)}")
            
    finally:
        manager.shutdown()

def demo_ai_integration():
    """Demonstrate AutoCrate AI integration."""
    print("\n" + "="*60)
    print("DEMO 3: AutoCrate AI Integration")
    print("="*60)
    
    # Create AI assistant with custom configuration
    ai = create_ai_assistant(
        project_name="AutoCrate AI Demo",
        max_tokens=10000,
        auto_optimize=True,
        enable_metrics=True
    )
    
    try:
        print(f"[OK] Created AI assistant for project: {ai.project_name}")
        
        # Simulate realistic AutoCrate interactions
        interactions = [
            "I need to create a shipping crate for a 72x48x36 inch product weighing 1500 lbs",
            "What plywood thickness should I use for this application?",
            "Can you generate the NX expressions for the front panel?",
            "How do I optimize the cleat spacing for structural integrity?",
            "What's the best way to test these calculations?",
            "Can you review my design specifications?"
        ]
        
        print(f"Processing {len(interactions)} AI interactions...")
        
        results = []
        for i, message in enumerate(interactions, 1):
            print(f"  Processing interaction {i}...")
            result = ai.chat(message)
            results.append(result)
            
            # Brief pause to simulate real usage
            time.sleep(0.2)
        
        # Show results summary
        print(f"\nAI Interaction Results:")
        total_tokens = sum(r["session_stats"]["token_usage"]["total"] for r in results)
        print(f"  Total interactions: {len(results)}")
        print(f"  Total tokens processed: {total_tokens}")
        print(f"  Average response length: {sum(len(r['assistant_response']) for r in results) // len(results)} chars")
        
        # Get comprehensive usage report
        usage_report = ai.get_usage_report()
        
        print(f"\nOverall Usage Statistics:")
        stats = usage_report["overall_statistics"]
        print(f"  Session duration: {stats['session_duration_hours']:.2f} hours")
        print(f"  Total interactions: {stats['total_interactions']}")
        print(f"  Total tokens used: {stats['total_tokens_used']}")
        print(f"  Average tokens per interaction: {stats['average_tokens_per_interaction']:.1f}")
        
        # Show optimization status
        optimization = usage_report["token_optimization"]
        print(f"\nToken Optimization Status:")
        print(f"  Current usage: {optimization['token_usage']['usage_ratio']:.1%}")
        print(f"  Remaining capacity: {optimization['token_usage']['remaining_tokens']} tokens")
        
        if optimization["optimization_recommendations"]:
            print(f"  Recommendations: {len(optimization['optimization_recommendations'])} items")
            for rec in optimization["optimization_recommendations"][:2]:  # Show first 2
                print(f"    - {rec['description']}")
        
    finally:
        final_stats = ai.shutdown()
        print(f"[OK] AI assistant shutdown complete")

def demo_token_analysis():
    """Demonstrate token analysis utilities."""
    print("\n" + "="*60)
    print("DEMO 4: Token Analysis and Utilities")
    print("="*60)
    
    # Create token analyzer
    analyzer = TokenAnalyzer()
    
    # Analyze different types of content
    test_contents = {
        "Simple Question": "What are the dimensions of a standard crate?",
        
        "Technical Request": """
        I need to generate NX expressions for a crate design with the following specifications:
        - Product dimensions: 96x48x30 inches
        - Weight: 2500 lbs
        - Plywood thickness: 0.75 inches  
        - Include reinforcement cleats every 16 inches
        Please optimize for material efficiency and structural integrity.
        """,
        
        "Code Example": """
        Can you help me debug this NX expression?
        ```
        panel_width = 96.0
        panel_height = 48.0
        cleat_spacing = calculate_optimal_spacing(panel_width, load_factor)
        ```
        I'm getting an error when trying to calculate the cleat positions.
        """,
        
        "Complex Design Request": """
        I'm designing a custom crate system for shipping heavy industrial equipment.
        The equipment weighs 8000 pounds and has irregular dimensions of 120x96x60 inches.
        I need to account for:
        1. ASTM D6251 testing requirements
        2. Material optimization for cost efficiency  
        3. Stackable design for warehouse storage
        4. Easy assembly with standard tools
        5. Compliance with international shipping regulations
        
        Can you create a comprehensive design with:
        - Complete material specifications
        - Structural calculations
        - Assembly instructions
        - Cost analysis
        - Testing verification plan
        
        Please include all NX expressions and provide detailed documentation.
        """
    }
    
    print(f"Analyzing {len(test_contents)} different content types...")
    
    for content_type, content in test_contents.items():
        analysis = analyzer.analyze_content(content)
        
        print(f"\n{content_type}:")
        print(f"  Characters: {analysis['total_characters']}")
        print(f"  Estimated tokens: {analysis['estimated_tokens']}")
        print(f"  Complexity score: {analysis['complexity_score']:.1f}/10")
        
        # Show pattern analysis
        patterns = analysis['patterns_found']
        interesting_patterns = {k: v for k, v in patterns.items() if v > 0}
        if interesting_patterns:
            print(f"  Patterns found: {', '.join(f'{k}({v})' for k, v in interesting_patterns.items())}")
        
        # Show optimization suggestions
        suggestions = analyzer.suggest_optimizations(analysis)
        if suggestions:
            print(f"  Suggestions: {len(suggestions)} optimization tips")
            for suggestion in suggestions[:1]:  # Show first suggestion
                print(f"    - {suggestion}")

def demo_configuration_management():
    """Demonstrate configuration management."""
    print("\n" + "="*60)
    print("DEMO 5: Configuration Management")
    print("="*60)
    
    # Create configuration manager
    config_file = "demo_data/autocrate_ai_config.json"
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    config_manager = ConfigManager(config_file)
    
    # Demonstrate configuration operations
    print("[OK] Configuration manager initialized")
    
    # Set custom configuration
    custom_settings = {
        "project_settings": {
            "default_plywood_thickness": 0.75,
            "standard_cleat_width": 3.5,
            "max_panel_size": 96
        },
        "optimization_settings": {
            "auto_summarize": True,
            "compression_target": 0.3,
            "warning_threshold": 0.75
        },
        "ui_preferences": {
            "show_debug_info": False,
            "enable_animations": True,
            "theme": "professional"
        }
    }
    
    config_manager.update(custom_settings)
    saved = config_manager.save_config()
    
    print(f"[OK] Configuration saved: {saved}")
    print(f"[OK] Configuration file: {config_file}")
    
    # Show current configuration
    print(f"\nCurrent Configuration Summary:")
    for section, settings in custom_settings.items():
        print(f"  {section.replace('_', ' ').title()}:")
        for key, value in settings.items():
            print(f"    - {key}: {value}")

def main():
    """Run all demonstrations."""
    print("AutoCrate Token Optimization System - Live Demonstration")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all demos
        demo_basic_token_optimization()
        demo_conversation_management() 
        demo_ai_integration()
        demo_token_analysis()
        demo_configuration_management()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print("[OK] All token optimization features demonstrated successfully")
        print("[OK] System is ready for production use with AutoCrate")
        print("\nNext steps:")
        print("  1. Review the generated demo_data/ directory")
        print("  2. Integrate with your AutoCrate workflows")
        print("  3. Customize configuration for your needs")
        print("  4. Monitor token usage in development sessions")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        logger.exception("Demo failed")
    
    print(f"\nDemo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()