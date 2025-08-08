#!/usr/bin/env python3
"""
AutoCrate AI Integration Example
Simple example showing how to use the token optimization system with AutoCrate.

This example demonstrates:
- Setting up AI assistance for AutoCrate development
- Token-aware conversation management
- Integration with AutoCrate workflows
- Memory optimization best practices

Author: AutoCrate Development Team
Created: August 2025
Version: 1.0.0
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from autocrate_ai_integration import create_ai_assistant

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def autocrate_development_session():
    """Simulate a typical AutoCrate development session with AI assistance."""
    
    print("AutoCrate AI Development Session - Example")
    print("=" * 50)
    
    # Create AI assistant with AutoCrate-optimized settings
    ai = create_ai_assistant(
        project_name="Industrial Crate Design",
        max_tokens=25000,          # Reasonable limit for development session
        auto_optimize=True,        # Enable automatic optimization
        warning_threshold=0.7,     # Get warnings at 70% usage
        save_conversations=True    # Save for later reference
    )
    
    try:
        print("AI Assistant initialized for AutoCrate development")
        print(f"Project: {ai.project_name}")
        print(f"Session ID: {ai.current_session_id[:8]}...")
        
        # Simulate typical AutoCrate development workflow
        development_tasks = [
            {
                "task": "Initial Design Consultation",
                "message": "I need to design a shipping crate for industrial equipment. The equipment is 96x48x30 inches and weighs 2500 pounds. What should I consider?",
                "expected_topics": ["dimensions", "weight", "materials", "structural"]
            },
            {
                "task": "Material Selection", 
                "message": "Based on the 2500 lb weight, what plywood thickness and cleat dimensions should I use? I need to meet ASTM D6251 requirements.",
                "expected_topics": ["plywood", "thickness", "cleats", "ASTM"]
            },
            {
                "task": "NX Expression Generation",
                "message": "Can you help me generate the NX expressions for the front panel calculation? I need to account for intermediate vertical cleats.",
                "expected_topics": ["expressions", "front panel", "cleats", "calculations"]
            },
            {
                "task": "Optimization Review",
                "message": "How can I optimize this design for material efficiency while maintaining structural integrity?",
                "expected_topics": ["optimization", "material", "efficiency", "structural"]
            },
            {
                "task": "Testing Strategy",
                "message": "What testing approach should I use to validate these calculations? I want to run the AutoCrate test suite.",
                "expected_topics": ["testing", "validation", "calculations", "AutoCrate"]
            }
        ]
        
        conversation_results = []
        
        for i, task in enumerate(development_tasks, 1):
            print(f"\n--- Task {i}: {task['task']} ---")
            
            # Process the development task
            result = ai.chat(task["message"])
            
            # Store results
            conversation_results.append({
                "task": task["task"],
                "tokens_used": result["session_stats"]["token_usage"]["total"],
                "response_length": len(result["assistant_response"]),
                "recommendations": len(result.get("recommendations", []))
            })
            
            print(f"Response generated ({len(result['assistant_response'])} characters)")
            print(f"Tokens used this turn: {result['session_stats']['token_usage']['total']}")
            
            # Show relevant part of response
            response = result["assistant_response"]
            if len(response) > 200:
                preview = response[:200] + "..."
            else:
                preview = response
            print(f"Preview: {preview}")
            
            # Check for optimization recommendations
            if result.get("recommendations"):
                print(f"Optimization recommendations: {len(result['recommendations'])}")
        
        # Generate final session report
        print("\n" + "=" * 50)
        print("SESSION SUMMARY")
        print("=" * 50)
        
        usage_report = ai.get_usage_report()
        session_stats = usage_report["overall_statistics"]
        
        print(f"Total tasks completed: {len(conversation_results)}")
        print(f"Session duration: {session_stats['session_duration_hours']:.2f} hours")
        print(f"Total interactions: {session_stats['total_interactions']}")  
        print(f"Total tokens used: {session_stats['total_tokens_used']}")
        print(f"Average tokens per task: {session_stats['average_tokens_per_interaction']:.1f}")
        
        # Token usage breakdown
        token_usage = usage_report["token_optimization"]["token_usage"]
        print(f"Token usage ratio: {token_usage['usage_ratio']:.1%}")
        print(f"Remaining capacity: {token_usage['remaining_tokens']} tokens")
        
        # Show optimization status
        if session_stats.get("optimizations_performed", 0) > 0:
            print(f"Memory optimizations performed: {session_stats['optimizations_performed']}")
        
        # Task-by-task breakdown
        print(f"\nTask Breakdown:")
        for i, task_result in enumerate(conversation_results, 1):
            print(f"  {i}. {task_result['task']}")
            print(f"     Tokens: {task_result['tokens_used']}, Response: {task_result['response_length']} chars")
        
        # Export conversation for later reference
        print(f"\nExporting conversation for documentation...")
        export_data = ai.export_conversation(include_metadata=True)
        
        # Save export to file
        export_file = f"autocrate_ai_session_{ai.current_session_id[:8]}.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Conversation exported to: {export_file}")
        
        # Show recommendations for future sessions
        recommendations = usage_report.get("recommendations", [])
        if recommendations:
            print(f"\nRecommendations for future sessions:")
            for rec in recommendations:
                print(f"  - [{rec['priority'].upper()}] {rec['message']}")
        
    finally:
        # Clean shutdown with final statistics
        print(f"\nShutting down AI assistant...")
        final_stats = ai.shutdown()
        print(f"Final session report saved")
        print(f"AI assistant shutdown complete")

def quick_autocrate_consultation():
    """Quick example of using AI for a simple AutoCrate question."""
    
    print("\nQuick AutoCrate Consultation Example")
    print("-" * 40)
    
    # Create AI for quick consultation
    ai = create_ai_assistant(
        project_name="Quick Consultation",
        max_tokens=5000  # Smaller limit for quick questions
    )
    
    try:
        # Ask a quick question
        question = "What's the formula for calculating cleat spacing in AutoCrate?"
        print(f"Question: {question}")
        
        result = ai.chat(question)
        
        print(f"\nAnswer: {result['assistant_response']}")
        print(f"Tokens used: {result['session_stats']['token_usage']['total']}")
        
    finally:
        ai.shutdown()

def main():
    """Run the examples."""
    
    try:
        # Run the full development session example
        autocrate_development_session()
        
        # Run the quick consultation example
        quick_autocrate_consultation()
        
        print("\n" + "=" * 50)
        print("EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 50)
        print("\nThe AutoCrate Token Optimization System is working correctly!")
        print("You can now integrate it into your AutoCrate development workflows.")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nExample error: {e}")
        logging.exception("Example failed")

if __name__ == "__main__":
    main()