#!/usr/bin/env python3
"""
AutoCrate Configuration Management

Centralized configuration for development vs production modes,
security settings, and application behavior.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class RunMode(Enum):
    """Application run modes."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AutoCrateConfig:
    """AutoCrate configuration manager."""
    
    def __init__(self):
        # Detect run mode from environment
        self.run_mode = self._detect_run_mode()
        
        # Base configuration
        self.project_root = Path(__file__).parent
        self.version = "12.1.3"
        
        # Mode-specific configuration
        if self.run_mode == RunMode.DEVELOPMENT:
            self._configure_development()
        elif self.run_mode == RunMode.PRODUCTION:
            self._configure_production()
        else:  # TESTING
            self._configure_testing()
    
    def _detect_run_mode(self) -> RunMode:
        """Detect current run mode from environment variables."""
        if os.getenv('AUTOCRATE_DEV_MODE', '0') == '1':
            return RunMode.DEVELOPMENT
        elif os.getenv('AUTOCRATE_TEST_MODE', '0') == '1':
            return RunMode.TESTING
        else:
            return RunMode.PRODUCTION
    
    def _configure_development(self):
        """Configure for development mode."""
        self.gui_type = "streamlit"  # Use Streamlit for development
        self.enable_hot_reload = True
        self.enable_auto_build = True
        
        # Security settings (relaxed for development)
        self.security_enabled = os.getenv('AUTOCRATE_SKIP_SECURITY', '0') != '1'
        self.security_level = "minimal" if not self.security_enabled else "standard"
        self.enable_authentication = False  # Disabled for dev speed
        self.enable_audit_logging = False   # Disabled for dev speed
        
        # Data settings
        self.use_mock_data = os.getenv('AUTOCRATE_USE_MOCK_DATA', '1') == '1'
        self.fast_calculations = True
        self.skip_validation = False  # Keep validation even in dev
        
        # Logging
        self.log_level = "DEBUG" if os.getenv('AUTOCRATE_DEBUG', '0') == '1' else "INFO"
        self.enable_console_logging = True
        self.enable_file_logging = False
        
        # Performance
        self.enable_caching = True
        self.calculation_timeout = 30  # seconds
        self.gui_update_interval = 0.1  # Fast updates for development
        
        # Output
        self.output_directory = self.project_root / "dev_output"
        self.temp_directory = self.project_root / "temp"
        
        # Development-specific features
        self.enable_profiling = True
        self.enable_debug_gui = True
        self.auto_save_inputs = True
    
    def _configure_production(self):
        """Configure for production mode."""
        self.gui_type = "tkinter"  # Use tkinter for production
        self.enable_hot_reload = False
        self.enable_auto_build = False
        
        # Security settings (full security)
        self.security_enabled = True
        self.security_level = "enhanced"
        self.enable_authentication = True
        self.enable_audit_logging = True
        
        # Data settings
        self.use_mock_data = False
        self.fast_calculations = False
        self.skip_validation = False
        
        # Logging
        self.log_level = "INFO"
        self.enable_console_logging = False
        self.enable_file_logging = True
        
        # Performance
        self.enable_caching = True
        self.calculation_timeout = 120  # seconds
        self.gui_update_interval = 0.5  # Balanced updates
        
        # Output
        self.output_directory = Path(os.getenv('AUTOCRATE_OUTPUT_DIR', str(self.project_root / "output")))
        self.temp_directory = Path(os.getenv('TEMP', str(self.project_root / "temp")))
        
        # Production-specific features
        self.enable_profiling = False
        self.enable_debug_gui = False
        self.auto_save_inputs = False
    
    def _configure_testing(self):
        """Configure for testing mode."""
        self.gui_type = "headless"  # No GUI for testing
        self.enable_hot_reload = False
        self.enable_auto_build = False
        
        # Security settings (minimal for testing)
        self.security_enabled = False
        self.security_level = "minimal"
        self.enable_authentication = False
        self.enable_audit_logging = False
        
        # Data settings
        self.use_mock_data = True
        self.fast_calculations = True
        self.skip_validation = False  # Keep validation for testing
        
        # Logging
        self.log_level = "WARNING"  # Reduce test noise
        self.enable_console_logging = True
        self.enable_file_logging = False
        
        # Performance
        self.enable_caching = False  # Disable for consistent testing
        self.calculation_timeout = 10   # Fast timeout for tests
        self.gui_update_interval = 1.0  # Not relevant for testing
        
        # Output
        self.output_directory = self.project_root / "test_output"
        self.temp_directory = self.project_root / "test_temp"
        
        # Testing-specific features
        self.enable_profiling = False
        self.enable_debug_gui = False
        self.auto_save_inputs = False
    
    def get_gui_config(self) -> Dict[str, Any]:
        """Get GUI-specific configuration."""
        if self.gui_type == "streamlit":
            return {
                'type': 'streamlit',
                'port': int(os.getenv('STREAMLIT_PORT', '8501')),
                'host': os.getenv('STREAMLIT_HOST', 'localhost'),
                'auto_open': True,
                'theme': 'light',
                'enable_3d_preview': True,
                'enable_real_time_calc': True
            }
        elif self.gui_type == "tkinter":
            return {
                'type': 'tkinter',
                'window_size': (1000, 700),
                'resizable': True,
                'theme': 'default',
                'enable_tooltips': True,
                'auto_validate_inputs': True
            }
        else:  # headless
            return {
                'type': 'headless'
            }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            'enabled': self.security_enabled,
            'level': self.security_level,
            'authentication': self.enable_authentication,
            'audit_logging': self.enable_audit_logging,
            'config_path': self.project_root / 'security' / 'config.json'
        }
    
    def get_calculation_config(self) -> Dict[str, Any]:
        """Get calculation configuration."""
        return {
            'use_mock_data': self.use_mock_data,
            'fast_mode': self.fast_calculations,
            'skip_validation': self.skip_validation,
            'timeout': self.calculation_timeout,
            'enable_caching': self.enable_caching,
            'astm_compliance': not self.use_mock_data,
            'safety_factor_default': 1.5
        }
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return {
            'output_directory': self.output_directory,
            'temp_directory': self.temp_directory,
            'auto_cleanup_temp': self.run_mode != RunMode.DEVELOPMENT,
            'backup_existing': self.run_mode == RunMode.PRODUCTION,
            'compress_output': False
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'level': self.log_level,
            'console_enabled': self.enable_console_logging,
            'file_enabled': self.enable_file_logging,
            'file_path': self.project_root / 'logs' / 'autocrate.log',
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    
    def get_development_config(self) -> Dict[str, Any]:
        """Get development-specific configuration."""
        return {
            'hot_reload': self.enable_hot_reload,
            'auto_build': self.enable_auto_build,
            'profiling': self.enable_profiling,
            'debug_gui': self.enable_debug_gui,
            'auto_save': self.auto_save_inputs,
            'watch_extensions': ['.py', '.json', '.yaml'],
            'build_on_change': True,
            'test_on_change': True
        }
    
    def create_directories(self):
        """Create necessary directories."""
        directories = [
            self.output_directory,
            self.temp_directory,
        ]
        
        if self.enable_file_logging:
            directories.append(self.project_root / 'logs')
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return self.run_mode == RunMode.DEVELOPMENT
    
    def is_production_mode(self) -> bool:
        """Check if running in production mode."""
        return self.run_mode == RunMode.PRODUCTION
    
    def is_testing_mode(self) -> bool:
        """Check if running in testing mode."""
        return self.run_mode == RunMode.TESTING
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            'run_mode': self.run_mode.value,
            'version': self.version,
            'gui': self.get_gui_config(),
            'security': self.get_security_config(),
            'calculation': self.get_calculation_config(),
            'output': self.get_output_config(),
            'logging': self.get_logging_config(),
            'development': self.get_development_config() if self.is_development_mode() else None
        }


# Global configuration instance
_config = None

def get_config() -> AutoCrateConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = AutoCrateConfig()
        _config.create_directories()
    return _config

def is_development_mode() -> bool:
    """Check if running in development mode."""
    return get_config().is_development_mode()

def is_production_mode() -> bool:
    """Check if running in production mode."""
    return get_config().is_production_mode()

def get_gui_type() -> str:
    """Get current GUI type."""
    return get_config().gui_type


if __name__ == "__main__":
    # Test configuration
    config = get_config()
    print(f"Run Mode: {config.run_mode.value}")
    print(f"GUI Type: {config.gui_type}")
    print(f"Security Enabled: {config.security_enabled}")
    print(f"Use Mock Data: {config.use_mock_data}")
    
    import json
    print("\nFull Configuration:")
    print(json.dumps(config.to_dict(), indent=2, default=str))
