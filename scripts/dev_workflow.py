#!/usr/bin/env python3
"""
AutoCrate Development Workflow Automation

Automates the development cycle: code change detection, testing, and executable generation.
Provides hot reload for GUI development and fast iteration cycles.
"""

import os
import sys
import time
import subprocess
import threading
import logging
from pathlib import Path
from typing import List, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import queue
import signal
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
dev_logger = logging.getLogger('AutoCrate.DevWorkflow')


class DevelopmentWorkflow:
    """Automated development workflow for AutoCrate."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.python_files = list(project_root.glob('**/*.py'))
        self.gui_process = None
        self.build_queue = queue.Queue()
        self.last_build_time = 0
        self.build_debounce = 2.0  # seconds
        self.auto_build_enabled = True
        self.auto_test_enabled = True
        self.hot_reload_enabled = True
        
        # Development configuration
        self.dev_config = {
            'skip_security_init': True,
            'use_mock_data': True,
            'enable_debug_logging': True,
            'fast_startup': True,
            'development_mode': True
        }
        
        dev_logger.info(f"Development workflow initialized for: {project_root}")
    
    def start_file_watcher(self) -> None:
        """Start watching for file changes."""
        event_handler = CodeChangeHandler(self)
        observer = Observer()
        
        # Watch Python files
        observer.schedule(event_handler, str(self.project_root), recursive=True)
        
        observer.start()
        dev_logger.info("File watcher started")
        
        try:
            # Start build processor
            build_thread = threading.Thread(target=self._process_build_queue, daemon=True)
            build_thread.start()
            
            # Keep the watcher running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            observer.stop()
            self._cleanup()
        
        observer.join()
    
    def on_code_change(self, filepath: str) -> None:
        """Handle code change event."""
        dev_logger.info(f"Code changed: {filepath}")
        
        # Add to build queue with debouncing
        current_time = time.time()
        if current_time - self.last_build_time > self.build_debounce:
            self.build_queue.put({
                'timestamp': current_time,
                'filepath': filepath,
                'action': 'full_cycle'
            })
    
    def _process_build_queue(self) -> None:
        """Process build queue in background thread."""
        while True:
            try:
                # Wait for build request
                build_request = self.build_queue.get(timeout=5)
                
                # Update last build time
                self.last_build_time = build_request['timestamp']
                
                # Execute development cycle
                self._execute_dev_cycle(build_request)
                
                # Mark as done
                self.build_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                dev_logger.error(f"Build processing error: {e}")
    
    def _execute_dev_cycle(self, build_request: dict) -> None:
        """Execute complete development cycle."""
        dev_logger.info("=== Starting Development Cycle ===")
        start_time = time.time()
        
        try:
            # Step 1: Run quick tests
            if self.auto_test_enabled:
                test_success = self._run_quick_tests()
                if not test_success:
                    dev_logger.warning("Tests failed - skipping build")
                    return
            
            # Step 2: Hot reload GUI if running
            if self.hot_reload_enabled:
                self._hot_reload_gui()
            
            # Step 3: Build executable (in background)
            if self.auto_build_enabled:
                threading.Thread(target=self._build_executable, daemon=True).start()
            
            elapsed = time.time() - start_time
            dev_logger.info(f"=== Dev Cycle Complete ({elapsed:.1f}s) ===")
            
        except Exception as e:
            dev_logger.error(f"Development cycle failed: {e}")
    
    def _run_quick_tests(self) -> bool:
        """Run quick validation tests."""
        dev_logger.info("Running quick tests...")
        
        try:
            # Quick syntax check
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', 'nx_expressions_generator.py'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                dev_logger.error(f"Syntax check failed: {result.stderr}")
                return False
            
            # Quick import test
            result = subprocess.run(
                [sys.executable, '-c', 'import nx_expressions_generator; print("Import OK")'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                dev_logger.error(f"Import test failed: {result.stderr}")
                return False
            
            dev_logger.info("[SUCCESS] Quick tests passed")
            return True
            
        except subprocess.TimeoutExpired:
            dev_logger.error("Quick tests timed out")
            return False
        except Exception as e:
            dev_logger.error(f"Quick test error: {e}")
            return False
    
    def _hot_reload_gui(self) -> None:
        """Hot reload the GUI application."""
        try:
            # Kill existing GUI process
            if self.gui_process and self.gui_process.poll() is None:
                self.gui_process.terminate()
                time.sleep(0.5)
                if self.gui_process.poll() is None:
                    self.gui_process.kill()
            
            # Start new GUI process with development config
            env = os.environ.copy()
            env.update({
                'AUTOCRATE_DEV_MODE': '1',
                'AUTOCRATE_SKIP_SECURITY': '1' if self.dev_config['skip_security_init'] else '0',
                'AUTOCRATE_USE_MOCK_DATA': '1' if self.dev_config['use_mock_data'] else '0',
                'AUTOCRATE_DEBUG': '1' if self.dev_config['enable_debug_logging'] else '0'
            })
            
            self.gui_process = subprocess.Popen(
                [sys.executable, 'nx_expressions_generator.py'],
                cwd=self.project_root,
                env=env
            )
            
            dev_logger.info("[INFO] GUI hot reloaded")
            
        except Exception as e:
            dev_logger.error(f"Hot reload failed: {e}")
    
    def _build_executable(self) -> None:
        """Build executable in background."""
        dev_logger.info("[INFO] Building executable...")
        build_start = time.time()
        
        try:
            # Fast build configuration
            build_cmd = [
                'python', '-m', 'PyInstaller',
                '--noconfirm',
                '--onefile',
                '--windowed',
                '--name', 'AutoCrate_dev',
                '--distpath', 'dist/dev',
                '--workpath', 'build/dev',
                '--specpath', 'build/dev',
                'nx_expressions_generator.py'
            ]
            
            result = subprocess.run(
                build_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes max
            )
            
            build_time = time.time() - build_start
            
            if result.returncode == 0:
                exe_path = self.project_root / 'dist/dev/AutoCrate_dev.exe'
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    dev_logger.info(f"[SUCCESS] Executable built successfully ({build_time:.1f}s, {size_mb:.1f}MB)")
                    dev_logger.info(f"   Location: {exe_path}")
                else:
                    dev_logger.warning("Build reported success but executable not found")
            else:
                dev_logger.error(f"Executable build failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            dev_logger.error("Executable build timed out")
        except Exception as e:
            dev_logger.error(f"Build error: {e}")
    
    def start_development_server(self) -> None:
        """Start development server with live reload."""
        dev_logger.info("Starting development server...")
        
        # Start GUI with development mode
        self._hot_reload_gui()
        
        # Start file watcher
        self.start_file_watcher()
    
    def create_development_launcher(self) -> None:
        """Create development launcher script."""
        launcher_content = f"""
@echo off
echo Starting AutoCrate Development Environment...
echo.

REM Set development environment variables
set AUTOCRATE_DEV_MODE=1
set AUTOCRATE_SKIP_SECURITY=1
set AUTOCRATE_USE_MOCK_DATA=1
set AUTOCRATE_DEBUG=1

REM Start development workflow
python "{self.project_root / 'scripts/dev_workflow.py'}" --mode=server

pause
"""
        
        launcher_path = self.project_root / 'dev_launcher.bat'
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        dev_logger.info(f"Development launcher created: {launcher_path}")
    
    def create_fast_build_script(self) -> None:
        """Create fast build script for quick testing."""
        build_script = f"""
@echo off
echo Fast AutoCrate Build...
echo.

REM Quick syntax check
echo Checking syntax...
python -m py_compile nx_expressions_generator.py
if errorlevel 1 (
    echo Syntax check failed!
    pause
    exit /b 1
)

REM Fast build
echo Building executable...
python -m PyInstaller --noconfirm --onefile --windowed --name AutoCrate_fast --distpath dist/fast nx_expressions_generator.py

if exist "dist/fast/AutoCrate_fast.exe" (
    echo.
    echo Build successful!
    echo Location: dist/fast/AutoCrate_fast.exe
    echo.
    echo Starting executable...
    start "" "dist/fast/AutoCrate_fast.exe"
) else (
    echo Build failed!
)

pause
"""
        
        script_path = self.project_root / 'fast_build.bat'
        with open(script_path, 'w') as f:
            f.write(build_script)
        
        dev_logger.info(f"Fast build script created: {script_path}")
    
    def _cleanup(self) -> None:
        """Clean up development resources."""
        if self.gui_process and self.gui_process.poll() is None:
            self.gui_process.terminate()
        
        dev_logger.info("Development workflow cleanup completed")


class CodeChangeHandler(FileSystemEventHandler):
    """Handle file system events for code changes."""
    
    def __init__(self, workflow: DevelopmentWorkflow):
        self.workflow = workflow
        self.ignored_extensions = {'.pyc', '.pyo', '.log', '.tmp'}
        self.ignored_dirs = {'__pycache__', '.git', 'build', 'dist'}
    
    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            filepath = Path(event.src_path)
            
            # Skip ignored files and directories
            if (filepath.suffix in self.ignored_extensions or
                any(ignored in filepath.parts for ignored in self.ignored_dirs)):
                return
            
            # Only process Python files
            if filepath.suffix == '.py':
                self.workflow.on_code_change(str(filepath))


def main():
    """Main entry point for development workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AutoCrate Development Workflow')
    parser.add_argument('--mode', choices=['watcher', 'server', 'build'], 
                       default='watcher', help='Development mode')
    parser.add_argument('--no-auto-build', action='store_true', 
                       help='Disable automatic executable building')
    parser.add_argument('--no-hot-reload', action='store_true',
                       help='Disable GUI hot reload')
    
    args = parser.parse_args()
    
    # Initialize workflow
    workflow = DevelopmentWorkflow(project_root)
    
    # Configure based on arguments
    if args.no_auto_build:
        workflow.auto_build_enabled = False
    if args.no_hot_reload:
        workflow.hot_reload_enabled = False
    
    # Create development scripts
    workflow.create_development_launcher()
    workflow.create_fast_build_script()
    
    # Handle interrupt signal
    def signal_handler(sig, frame):
        dev_logger.info("Shutting down development workflow...")
        workflow._cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start appropriate mode
    if args.mode == 'server':
        workflow.start_development_server()
    elif args.mode == 'build':
        workflow._build_executable()
    else:
        workflow.start_file_watcher()


if __name__ == '__main__':
    main()
