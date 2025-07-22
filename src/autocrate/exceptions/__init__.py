"""
Custom exceptions for AutoCrate.

This package defines application-specific exception classes.
"""

class AutoCrateError(Exception):
    """Base exception for all AutoCrate errors."""
    pass

class ValidationError(AutoCrateError):
    """Raised when input validation fails."""
    pass

class CalculationError(AutoCrateError):
    """Raised when calculation logic encounters an error."""
    pass

class ConfigurationError(AutoCrateError):
    """Raised when configuration is invalid."""
    pass

__all__ = [
    "AutoCrateError",
    "ValidationError", 
    "CalculationError",
    "ConfigurationError",
]