#!/usr/bin/env python3
"""
AutoCreat Input Validation and Sanitization Framework

Provides comprehensive input validation for all user inputs with Windows security focus.
Prevents injection attacks, validates ranges, and sanitizes all data before processing.
"""

import re
import os
import string
from typing import Union, Optional, Tuple, List, Any
from pathlib import Path, PurePath
import logging
from decimal import Decimal, InvalidOperation
from enum import Enum

# Configure security logging
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger('AutoCrate.Security')


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


class InputType(Enum):
    """Enumeration of input types for validation."""
    DIMENSION = "dimension"
    WEIGHT = "weight"
    THICKNESS = "thickness"
    CLEARANCE = "clearance"
    FILENAME = "filename"
    FILEPATH = "filepath"
    TEXT = "text"
    INTEGER = "integer"
    BOOLEAN = "boolean"


class SecurityValidator:
    """Comprehensive input validation with Windows security focus."""
    
    # Security constants
    MAX_STRING_LENGTH = 1000
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 260  # Windows MAX_PATH
    
    # Engineering value ranges (inches and pounds)
    DIMENSION_RANGE = (0.1, 1000.0)  # 0.1" to 1000"
    WEIGHT_RANGE = (0.1, 100000.0)   # 0.1 lb to 100,000 lbs
    THICKNESS_RANGE = (0.125, 6.0)   # 1/8" to 6"
    CLEARANCE_RANGE = (0.0, 100.0)   # 0" to 100"
    
    # Allowed characters for different input types
    SAFE_FILENAME_CHARS = set(string.ascii_letters + string.digits + '._-')
    SAFE_TEXT_CHARS = set(string.ascii_letters + string.digits + ' ._-,()')
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'[<>:"|?*]',  # Windows invalid filename chars
        r'\\\\',      # UNC paths
        r'\.\./',      # Directory traversal
        r'\.\.\\',     # Directory traversal Windows
        r'\$\w+',      # Environment variables
        r'%\w+%',      # Windows environment variables
        r'[\x00-\x1f]', # Control characters
        r'script',     # Script injection
        r'eval',       # Code execution
        r'exec',       # Code execution
    ]
    
    def __init__(self):
        """Initialize the security validator."""
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                for pattern in self.DANGEROUS_PATTERNS]
        security_logger.info("Security validator initialized")
    
    def validate_dimension(self, value: Any, name: str = "dimension") -> float:
        """Validate dimensional input (length, width, height)."""
        return self._validate_numeric_range(
            value, name, self.DIMENSION_RANGE, InputType.DIMENSION
        )
    
    def validate_weight(self, value: Any, name: str = "weight") -> float:
        """Validate weight input."""
        return self._validate_numeric_range(
            value, name, self.WEIGHT_RANGE, InputType.WEIGHT
        )
    
    def validate_thickness(self, value: Any, name: str = "thickness") -> float:
        """Validate material thickness input."""
        return self._validate_numeric_range(
            value, name, self.THICKNESS_RANGE, InputType.THICKNESS
        )
    
    def validate_clearance(self, value: Any, name: str = "clearance") -> float:
        """Validate clearance input."""
        return self._validate_numeric_range(
            value, name, self.CLEARANCE_RANGE, InputType.CLEARANCE
        )
    
    def validate_filename(self, filename: str) -> str:
        """Validate and sanitize filename for Windows."""
        if not isinstance(filename, str):
            raise ValidationError(f"Filename must be string, got {type(filename)}")
        
        # Basic length check
        if len(filename) > self.MAX_FILENAME_LENGTH:
            raise ValidationError(f"Filename too long: {len(filename)} > {self.MAX_FILENAME_LENGTH}")
        
        # Check for empty or whitespace-only
        if not filename.strip():
            raise ValidationError("Filename cannot be empty")
        
        # Check for dangerous patterns
        self._check_dangerous_patterns(filename, "filename")
        
        # Windows reserved names
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_part = filename.split('.')[0].upper()
        if name_part in reserved_names:
            raise ValidationError(f"Filename uses Windows reserved name: {name_part}")
        
        # Sanitize characters
        sanitized = ''.join(c for c in filename if c in self.SAFE_FILENAME_CHARS or c == '.')
        
        # Ensure we have an .exp extension for expression files
        if not sanitized.lower().endswith('.exp'):
            sanitized += '.exp'
        
        security_logger.info(f"Filename validated and sanitized: {filename} -> {sanitized}")
        return sanitized
    
    def validate_filepath(self, filepath: str) -> Path:
        """Validate and sanitize file path for Windows."""
        if not isinstance(filepath, str):
            raise ValidationError(f"Filepath must be string, got {type(filepath)}")
        
        # Length check
        if len(filepath) > self.MAX_PATH_LENGTH:
            raise ValidationError(f"Path too long: {len(filepath)} > {self.MAX_PATH_LENGTH}")
        
        # Check for dangerous patterns
        self._check_dangerous_patterns(filepath, "filepath")
        
        try:
            # Use pathlib for safe path handling
            path = Path(filepath)
            
            # Check if path is absolute and within safe boundaries
            if path.is_absolute():
                # Ensure it's within the current drive or a safe location
                current_drive = Path.cwd().anchor
                if not str(path).startswith(current_drive):
                    # Allow if it's in a standard Windows location
                    safe_roots = [r'C:\Users', r'C:\ProgramData', r'C:\temp']
                    if not any(str(path).startswith(root) for root in safe_roots):
                        raise ValidationError(f"Path outside safe boundaries: {path}")
            
            # Resolve to prevent directory traversal
            resolved_path = path.resolve()
            
            # Additional security check after resolution
            if '..' in str(resolved_path):
                raise ValidationError("Path contains directory traversal after resolution")
            
            security_logger.info(f"Filepath validated: {filepath} -> {resolved_path}")
            return resolved_path
            
        except (OSError, ValueError) as e:
            raise ValidationError(f"Invalid path: {e}")
    
    def validate_text_input(self, text: str, max_length: int = None) -> str:
        """Validate and sanitize general text input."""
        if not isinstance(text, str):
            raise ValidationError(f"Text input must be string, got {type(text)}")
        
        max_len = max_length or self.MAX_STRING_LENGTH
        if len(text) > max_len:
            raise ValidationError(f"Text too long: {len(text)} > {max_len}")
        
        # Check for dangerous patterns
        self._check_dangerous_patterns(text, "text input")
        
        # Sanitize characters
        sanitized = ''.join(c for c in text if c in self.SAFE_TEXT_CHARS)
        
        security_logger.debug(f"Text input validated: {len(text)} chars -> {len(sanitized)} chars")
        return sanitized.strip()
    
    def validate_integer(self, value: Any, min_val: int = None, max_val: int = None) -> int:
        """Validate integer input with optional range checking."""
        try:
            if isinstance(value, str):
                # Remove any non-numeric characters except minus
                clean_value = re.sub(r'[^\d-]', '', value)
                int_val = int(clean_value)
            else:
                int_val = int(value)
            
            if min_val is not None and int_val < min_val:
                raise ValidationError(f"Integer {int_val} below minimum {min_val}")
            
            if max_val is not None and int_val > max_val:
                raise ValidationError(f"Integer {int_val} above maximum {max_val}")
            
            return int_val
            
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid integer: {value} ({e})")
    
    def validate_boolean(self, value: Any) -> bool:
        """Validate boolean input from various sources."""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            lower_val = value.lower().strip()
            if lower_val in ('true', '1', 'yes', 'on', 'enabled'):
                return True
            elif lower_val in ('false', '0', 'no', 'off', 'disabled'):
                return False
            else:
                raise ValidationError(f"Invalid boolean string: {value}")
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        raise ValidationError(f"Cannot convert to boolean: {value} ({type(value)})")
    
    def _validate_numeric_range(self, value: Any, name: str, 
                              valid_range: Tuple[float, float], 
                              input_type: InputType) -> float:
        """Internal method for numeric range validation."""
        try:
            # Handle string inputs
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point and minus
                clean_value = re.sub(r'[^\d.-]', '', value)
                if not clean_value:
                    raise ValidationError(f"No numeric content in {name}: {value}")
                
                # Use Decimal for precise validation
                decimal_val = Decimal(clean_value)
                float_val = float(decimal_val)
            else:
                float_val = float(value)
            
            # Range validation
            min_val, max_val = valid_range
            if not (min_val <= float_val <= max_val):
                raise ValidationError(
                    f"{name} {float_val} outside valid range [{min_val}, {max_val}]"
                )
            
            # Check for reasonable precision (prevent extremely precise inputs)
            if isinstance(value, str) and '.' in value:
                decimal_places = len(value.split('.')[1])
                if decimal_places > 6:
                    security_logger.warning(f"High precision input detected: {value}")
            
            security_logger.debug(f"{input_type.value} validated: {value} -> {float_val}")
            return float_val
            
        except (ValueError, TypeError, InvalidOperation) as e:
            raise ValidationError(f"Invalid {name}: {value} ({e})")
    
    def _check_dangerous_patterns(self, text: str, context: str) -> None:
        """Check text against dangerous patterns."""
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                security_logger.warning(f"Dangerous pattern detected in {context}: {text}")
                raise ValidationError(f"Invalid characters detected in {context}")
    
    def sanitize_nx_variable_name(self, name: str) -> str:
        """Sanitize variable name for NX expressions."""
        if not isinstance(name, str):
            raise ValidationError(f"Variable name must be string, got {type(name)}")
        
        # NX variable names must start with letter, contain only alphanumeric and underscore
        # Check for dangerous patterns first
        self._check_dangerous_patterns(name, "NX variable name")
        
        # Remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure it starts with a letter
        if not sanitized[0].isalpha():
            sanitized = 'var_' + sanitized
        
        # Limit length
        if len(sanitized) > 64:  # NX variable name limit
            sanitized = sanitized[:64]
        
        security_logger.debug(f"NX variable name sanitized: {name} -> {sanitized}")
        return sanitized
    
    def validate_expression_value(self, value: Any) -> str:
        """Validate and format value for NX expression."""
        if isinstance(value, (int, float)):
            # Format numeric values safely
            if abs(value) > 1e10:
                raise ValidationError(f"Expression value too large: {value}")
            return f"{value:.6f}".rstrip('0').rstrip('.')
        
        elif isinstance(value, str):
            # Validate string expressions
            self._check_dangerous_patterns(value, "expression value")
            # Only allow safe mathematical expressions
            if not re.match(r'^[\d\s+\-*/().]+$', value):
                raise ValidationError(f"Invalid expression characters: {value}")
            return value
        
        else:
            raise ValidationError(f"Invalid expression value type: {type(value)}")


# Global validator instance
_validator = SecurityValidator()

# Convenience functions for common validations
def validate_dimension(value: Any, name: str = "dimension") -> float:
    """Validate dimensional input."""
    return _validator.validate_dimension(value, name)

def validate_weight(value: Any) -> float:
    """Validate weight input."""
    return _validator.validate_weight(value)

def validate_filename(filename: str) -> str:
    """Validate filename."""
    return _validator.validate_filename(filename)

def validate_filepath(filepath: str) -> Path:
    """Validate file path."""
    return _validator.validate_filepath(filepath)

def sanitize_for_nx(name: str) -> str:
    """Sanitize name for NX variable."""
    return _validator.sanitize_nx_variable_name(name)


if __name__ == "__main__":
    # Basic testing
    validator = SecurityValidator()
    
    # Test cases
    test_cases = [
        ("dimension", 36.5),
        ("weight", 2500),
        ("filename", "test_crate.exp"),
        ("dangerous_filename", "../../../evil.exe"),
    ]
    
    for test_name, test_value in test_cases:
        try:
            if test_name == "dimension":
                result = validator.validate_dimension(test_value)
                print(f"[PASS] {test_name}: {test_value} -> {result}")
            elif test_name == "weight":
                result = validator.validate_weight(test_value)
                print(f"[PASS] {test_name}: {test_value} -> {result}")
            elif test_name == "filename" or test_name == "dangerous_filename":
                result = validator.validate_filename(test_value)
                print(f"[PASS] {test_name}: {test_value} -> {result}")
        except ValidationError as e:
            print(f"[FAIL] {test_name}: {test_value} -> ERROR: {e}")
