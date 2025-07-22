"""
Settings and configuration management for AutoCrate.

This module handles application settings, user preferences,
and configuration persistence.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from ..exceptions import ConfigurationError
from ..utils.constants import DEFAULTS, LUMBER_SIZES, MATERIAL_CONSTANTS


class Settings:
    """Manages application settings and configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self._config_file = config_file or self._get_default_config_path()
        self._settings = {}
        self._load_defaults()
        self.load()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Try to use AppData on Windows, or home directory on others
        if os.name == 'nt':  # Windows
            config_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = os.path.join(config_dir, 'AutoCrate')
        else:
            config_dir = os.path.join(os.path.expanduser('~'), '.autocrate')
        
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, 'settings.json')
    
    def _load_defaults(self):
        """Load default settings."""
        self._settings = {
            'application': {
                'version': '12.0.2',
                'last_run': None,
                'check_updates': True,
            },
            'ui': {
                'window_width': 1000,
                'window_height': 700,
                'window_maximized': False,
                'theme': 'default',
                'font_size': 9,
                'show_tooltips': True,
                'recent_files': [],
                'max_recent_files': 10,
            },
            'calculations': {
                'default_clearance': DEFAULTS['clearance'],
                'cleat_member_width': DEFAULTS['cleat_member_width'],
                'panel_sheathing_thickness': DEFAULTS['panel_sheathing_thickness'],
                'adjustment_threshold': DEFAULTS['adjustment_threshold'],
                'adjustment_increment': DEFAULTS['adjustment_increment'],
                'strategy': 'hybrid',
                'debug_mode': False,
            },
            'materials': {
                'lumber_sizes': dict(LUMBER_SIZES),
                'plywood_thickness': MATERIAL_CONSTANTS['plywood_thickness'],
                'cleat_thickness': MATERIAL_CONSTANTS['cleat_thickness'],
                'wood_density': MATERIAL_CONSTANTS['wood_density_psf'],
                'plywood_density': MATERIAL_CONSTANTS['plywood_density_psf'],
            },
            'output': {
                'default_directory': os.path.expanduser('~'),
                'auto_save': False,
                'backup_files': True,
                'include_metadata': True,
            },
            'advanced': {
                'calculation_timeout': 30,  # seconds
                'memory_limit': 512,  # MB
                'parallel_processing': True,
                'cache_calculations': True,
            }
        }
    
    def load(self):
        """Load settings from configuration file."""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge loaded settings with defaults
                self._merge_settings(self._settings, loaded_settings)
                
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def save(self):
        """Save settings to configuration file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            
            with open(self._config_file, 'w') as f:
                json.dump(self._settings, f, indent=2, sort_keys=True)
                
        except IOError as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")
    
    def _merge_settings(self, default: Dict, loaded: Dict):
        """Recursively merge loaded settings with defaults."""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_settings(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.
        
        Args:
            key: Setting key in dot notation (e.g., 'ui.window_width')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set a setting value using dot notation.
        
        Args:
            key: Setting key in dot notation (e.g., 'ui.window_width')
            value: Value to set
        """
        keys = key.split('.')
        setting_dict = self._settings
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in setting_dict:
                setting_dict[k] = {}
            setting_dict = setting_dict[k]
        
        # Set the value
        setting_dict[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire settings section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary containing section settings
        """
        return self._settings.get(section, {}).copy()
    
    def update_section(self, section: str, values: Dict[str, Any]):
        """
        Update an entire settings section.
        
        Args:
            section: Section name
            values: Dictionary of values to update
        """
        if section not in self._settings:
            self._settings[section] = {}
        
        self._settings[section].update(values)
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self._load_defaults()
    
    def reset_section(self, section: str):
        """
        Reset a specific section to defaults.
        
        Args:
            section: Section name to reset
        """
        defaults = Settings()  # Create new instance to get defaults
        if section in defaults._settings:
            self._settings[section] = defaults._settings[section].copy()
    
    def add_recent_file(self, filepath: str):
        """
        Add a file to the recent files list.
        
        Args:
            filepath: Path to the file
        """
        recent_files = self.get('ui.recent_files', [])
        
        # Remove if already exists
        if filepath in recent_files:
            recent_files.remove(filepath)
        
        # Add to beginning
        recent_files.insert(0, filepath)
        
        # Limit to max recent files
        max_files = self.get('ui.max_recent_files', 10)
        recent_files = recent_files[:max_files]
        
        self.set('ui.recent_files', recent_files)
    
    def get_recent_files(self) -> list:
        """Get list of recent files, filtered to existing files only."""
        recent_files = self.get('ui.recent_files', [])
        
        # Filter to files that still exist
        existing_files = [f for f in recent_files if os.path.exists(f)]
        
        # Update the list if it changed
        if len(existing_files) != len(recent_files):
            self.set('ui.recent_files', existing_files)
        
        return existing_files
    
    def validate(self) -> list:
        """
        Validate configuration settings.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate numeric ranges
        numeric_validations = [
            ('ui.window_width', 400, 3840, "Window width"),
            ('ui.window_height', 300, 2160, "Window height"),
            ('ui.font_size', 6, 72, "Font size"),
            ('calculations.cleat_member_width', 0.1, 20, "Cleat member width"),
            ('calculations.adjustment_threshold', 0.1, 10, "Adjustment threshold"),
            ('advanced.calculation_timeout', 1, 300, "Calculation timeout"),
            ('advanced.memory_limit', 64, 4096, "Memory limit"),
        ]
        
        for key, min_val, max_val, description in numeric_validations:
            value = self.get(key)
            if value is not None:
                try:
                    num_value = float(value)
                    if not (min_val <= num_value <= max_val):
                        errors.append(
                            f"{description} must be between {min_val} and {max_val}"
                        )
                except (ValueError, TypeError):
                    errors.append(f"{description} must be a valid number")
        
        # Validate strategy
        strategy = self.get('calculations.strategy')
        valid_strategies = ['hybrid', 'dimension', 'position']
        if strategy and strategy not in valid_strategies:
            errors.append(f"Strategy must be one of: {', '.join(valid_strategies)}")
        
        return errors
    
    def export_settings(self, filepath: str):
        """
        Export settings to a file.
        
        Args:
            filepath: Path to export file
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self._settings, f, indent=2, sort_keys=True)
        except IOError as e:
            raise ConfigurationError(f"Failed to export settings: {str(e)}")
    
    def import_settings(self, filepath: str):
        """
        Import settings from a file.
        
        Args:
            filepath: Path to import file
        """
        try:
            with open(filepath, 'r') as f:
                imported_settings = json.load(f)
            
            # Validate before importing
            temp_settings = Settings()
            temp_settings._settings = imported_settings
            errors = temp_settings.validate()
            
            if errors:
                raise ConfigurationError(f"Invalid settings file: {'; '.join(errors)}")
            
            # Import settings
            self._merge_settings(self._settings, imported_settings)
            
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to import settings: {str(e)}")