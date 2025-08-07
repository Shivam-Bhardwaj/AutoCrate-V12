#!/usr/bin/env python3
"""
AutoCrate Main Launcher
Launches the AutoCrate application with proper path setup and comprehensive logging.
"""

import sys
import os
import time
import atexit
from pathlib import Path

# Add the autocrate directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
autocrate_dir = os.path.join(current_dir, 'autocrate')
if autocrate_dir not in sys.path:
    sys.path.insert(0, autocrate_dir)

def main():
    """Main application launcher with logging and error handling."""
    logger = None
    start_time = time.time()
    
    try:
        # Initialize logging system
        from debug_logger import get_logger, finalize_logging
        from startup_analyzer import run_startup_analysis
        
        # Get the main application logger
        logger = get_logger("AutoCrate.Main")
        logger.info("AutoCrate application starting...")
        
        # Run startup analysis to check previous runs
        try:
            startup_result = run_startup_analysis(enable_console_output=True)
            logger.info("Startup analysis completed", {
                'previous_run_status': startup_result.get('status'),
                'critical_issues': len([i for i in startup_result.get('insights', []) if i.get('type') == 'error'])
            })
        except Exception as e:
            logger.warning(f"Startup analysis failed: {e}")
        
        # Import and initialize main application
        logger.info("Loading AutoCrate application components...")
        from nx_expressions_generator import CrateApp
        import tkinter as tk
        
        # Create main window
        logger.info("Creating main application window...")
        root = tk.Tk()
        root.title("AutoCrate v12.0 - Professional Crate Engineering")
        
        # Set up window close handler for clean shutdown
        def on_closing():
            logger.info("Application closing requested by user")
            try:
                duration = time.time() - start_time
                logger.info(f"Application session completed", {
                    'duration_seconds': round(duration, 2),
                    'exit_type': 'user_requested'
                })
            finally:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Initialize the main application
        logger.info("Initializing CrateApp...")
        app = CrateApp(root)
        
        # Log successful initialization
        init_time = time.time() - start_time
        logger.info(f"AutoCrate initialization complete", {
            'initialization_time_ms': round(init_time * 1000, 2),
            'components_loaded': 'CrateApp, GUI, Logger'
        })
        
        # Start the main event loop
        logger.info("Starting main application event loop...")
        root.mainloop()
        
        # Log clean shutdown
        duration = time.time() - start_time
        logger.info("AutoCrate application ended normally", {
            'total_session_duration_seconds': round(duration, 2)
        })
        
        # Run automated post-session tests if enabled
        run_post_session_tests = os.getenv('AUTOCRATE_RUN_TESTS', '0') == '1'
        if run_post_session_tests:
            try:
                logger.info("Running post-session automated tests...")
                from autocrate.test_agent import AutoCrateTestAgent
                test_agent = AutoCrateTestAgent()
                test_results = test_agent.run_quick_validation_tests()
                
                logger.info("Post-session test results", {
                    'tests_passed': test_results.get('passed', 0),
                    'tests_failed': test_results.get('failed', 0),
                    'overall_status': 'PASS' if test_results.get('all_passed', False) else 'FAIL'
                })
                
                if not test_results.get('all_passed', False):
                    logger.warning("Some post-session tests failed - check test reports for details")
                    
            except ImportError:
                logger.debug("Test agent not available - skipping post-session tests")
            except Exception as e:
                logger.warning(f"Post-session tests failed: {e}")
        
    except ImportError as e:
        error_msg = f"Failed to import required AutoCrate modules: {e}"
        if logger:
            logger.critical(error_msg, e, {
                'python_path': sys.path[:3],
                'autocrate_dir': autocrate_dir,
                'current_dir': current_dir
            })
        else:
            print(f"CRITICAL ERROR: {error_msg}")
            print(f"Python path: {sys.path[:3]}")
            print(f"AutoCrate directory: {autocrate_dir}")
        return 1
        
    except Exception as e:
        error_msg = f"Unexpected error during AutoCrate startup: {e}"
        if logger:
            logger.critical(error_msg, e, {
                'startup_duration': round(time.time() - start_time, 2)
            })
        else:
            print(f"CRITICAL ERROR: {error_msg}")
        return 1
    
    finally:
        # Ensure logging is finalized
        try:
            if logger:
                finalize_logging()
        except:
            pass  # Don't let logging errors prevent shutdown
    
    return 0

# Register cleanup function
def cleanup_on_exit():
    """Cleanup function called on program exit."""
    try:
        from debug_logger import finalize_logging
        finalize_logging()
    except:
        pass

atexit.register(cleanup_on_exit)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)