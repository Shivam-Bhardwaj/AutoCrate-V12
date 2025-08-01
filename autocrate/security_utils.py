"""
Security utilities for AutoCrate application.
Provides path validation and input sanitization functions.
"""

import os
import re
from pathlib import Path
from typing import Union, Optional


def validate_output_path(filename: str, allowed_dir: str) -> str:
    """
    Validate and sanitize output file path to prevent path traversal attacks.
    
    Args:
        filename: The requested filename/path
        allowed_dir: The directory where files are allowed to be written
        
    Returns:
        Absolute path if valid
        
    Raises:
        ValueError: If path is invalid or outside allowed directory
    """
    try:
        # Convert to Path objects for better handling
        allowed_path = Path(allowed_dir).resolve()
        requested_path = Path(filename).resolve()
        
        # Check if the requested path is within the allowed directory
        try:
            requested_path.relative_to(allowed_path)
        except ValueError:
            raise ValueError(f"Path outside allowed directory: {filename}")
        
        # Additional security checks
        if '..' in str(filename) or filename.startswith('/') or ':' in filename[1:3]:
            raise ValueError(f"Invalid path characters detected: {filename}")
            
        return str(requested_path)
        
    except Exception as e:
        raise ValueError(f"Path validation failed: {e}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove potentially dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for file system use
    """
    # Remove path separators and dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    # Ensure not empty
    if not sanitized:
        sanitized = "output"
        
    return sanitized


def validate_numeric_input(value: str, min_val: Optional[float] = None, 
                         max_val: Optional[float] = None, 
                         input_name: str = "input") -> float:
    """
    Validate and convert numeric input with range checking.
    
    Args:
        value: String value to validate
        min_val: Minimum allowed value (optional)
        max_val: Maximum allowed value (optional)
        input_name: Name of input for error messages
        
    Returns:
        Validated float value
        
    Raises:
        ValueError: If input is invalid or out of range
    """
    try:
        # Convert to float
        num_value = float(value.strip())
        
        # Check for NaN or infinity
        if not (num_value == num_value) or abs(num_value) == float('inf'):
            raise ValueError(f"Invalid numeric value for {input_name}: {value}")
        
        # Range validation
        if min_val is not None and num_value < min_val:
            raise ValueError(f"{input_name} must be >= {min_val}, got {num_value}")
            
        if max_val is not None and num_value > max_val:
            raise ValueError(f"{input_name} must be <= {max_val}, got {num_value}")
            
        return num_value
        
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(f"Invalid numeric format for {input_name}: {value}")
        raise


def create_secure_directory(directory_path: str) -> bool:
    """
    Securely create directory with proper permissions.
    
    Args:
        directory_path: Path to directory to create
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(directory_path, mode=0o755, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        print(f"Failed to create directory {directory_path}: {e}")
        return False


def is_safe_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Check if file has allowed extension.
    
    Args:
        filename: File name to check
        allowed_extensions: List of allowed extensions (with dots, e.g., ['.exp', '.txt'])
        
    Returns:
        True if extension is allowed
    """
    _, ext = os.path.splitext(filename.lower())
    return ext in [e.lower() for e in allowed_extensions]