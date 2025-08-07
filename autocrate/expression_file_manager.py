"""
Expression File Manager for AutoCrate
Manages intelligent replacement of expression files based on parameters.
Ensures only the latest version of each unique parameter combination is kept.
"""

import os
import re
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class ExpressionParameters:
    """Represents the parameters of an expression file."""
    length: float
    width: float
    height: float
    weight: float
    material_type: str
    panel_thickness: float
    clearance: float
    timestamp: str = ""
    
    def matches(self, other: 'ExpressionParameters', tolerance: float = 0.1) -> bool:
        """
        Check if two parameter sets match within tolerance.
        
        Args:
            other: Another ExpressionParameters instance
            tolerance: Tolerance for floating point comparison (default 0.1 for rounding differences)
            
        Returns:
            bool: True if parameters match
        """
        return (
            abs(self.length - other.length) <= tolerance and
            abs(self.width - other.width) <= tolerance and
            abs(self.height - other.height) <= tolerance and
            abs(self.weight - other.weight) <= tolerance and
            self.material_type == other.material_type and
            abs(self.panel_thickness - other.panel_thickness) <= tolerance and
            abs(self.clearance - other.clearance) <= tolerance
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for easy comparison."""
        return {
            'length': round(self.length, 2),
            'width': round(self.width, 2),
            'height': round(self.height, 2),
            'weight': round(self.weight, 2),
            'material_type': self.material_type,
            'panel_thickness': round(self.panel_thickness, 2),
            'clearance': round(self.clearance, 2)
        }


class ExpressionFileManager:
    """Manages expression files with intelligent replacement based on parameters."""
    
    # Regex patterns for different filename formats
    PATTERNS = [
        # Format with underscores in decimals: YYYYMMDD_HHMMSS_Crate_LxWxH_Wweight_5P_Material0_XX_CX_X_ASTM.exp
        re.compile(
            r'(\d{8}_\d{6})_Crate_'
            r'(\d+)x(\d+)x(\d+)_'
            r'W(\d+)_'
            r'(?:\d+P_)?'
            r'(PLY|OSB)(\d+[_\.]?\d*)_'
            r'C(\d+[_\.]?\d*)_'
            r'.*\.exp$'
        ),
        # New format with dots: YYYYMMDD_HHMMSS_Crate_LxWxH_WweightLBS_5P_MaterialThickness_Cclearance_ASTM.exp
        re.compile(
            r'(\d{8}_\d{6})_Crate_'
            r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)_'
            r'W(\d+(?:\.\d+)?)_'
            r'(?:\d+P_)?'
            r'(PLY|OSB)(\d+(?:\.\d+)?)_'
            r'C(\d+(?:\.\d+)?)_'
            r'.*\.exp$'
        ),
        # Quick test format with dots
        re.compile(
            r'(\d{8}_\d{6})_QuickTest_\d+_'
            r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)_'
            r'W(\d+(?:\.\d+)?)_'
            r'(PLY|OSB)(\d+(?:\.\d+)?)_'
            r'C(\d+(?:\.\d+)?)_'
            r'.*\.exp$'
        ),
        # Alternative format without 5P
        re.compile(
            r'(\d{8}_\d{6})_Crate_'
            r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)_'
            r'(\d+(?:\.\d+)?)lbs_'
            r'(PLY|OSB)(\d+(?:\.\d+)?)_'
            r'CLR(\d+(?:\.\d+)?)'
            r'.*\.exp$'
        ),
        # Legacy format variations
        re.compile(
            r'(\d{8}_\d{6})_Crate_'
            r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)_'
            r'(\d+(?:\.\d+)?)lbs_'
            r'(OSB|PLY)_(\d+(?:\.\d+)?)in_'
            r'.*\.exp$'
        )
    ]
    
    def __init__(self, expressions_dir: str):
        """
        Initialize the ExpressionFileManager.
        
        Args:
            expressions_dir: Path to the expressions directory
        """
        self.expressions_dir = expressions_dir
    
    def parse_filename(self, filename: str) -> Optional[ExpressionParameters]:
        """
        Parse an expression filename to extract parameters.
        
        Args:
            filename: The filename to parse
            
        Returns:
            ExpressionParameters or None if parsing fails
        """
        basename = os.path.basename(filename)
        
        for pattern in self.PATTERNS:
            match = pattern.match(basename)
            if match:
                groups = match.groups()
                try:
                    if len(groups) >= 8:
                        # Format with all parameters
                        # Handle underscores in decimal numbers
                        panel_thickness_str = groups[6].replace('_', '.')
                        clearance_str = groups[7].replace('_', '.')
                        
                        return ExpressionParameters(
                            timestamp=groups[0],
                            length=float(groups[1]),
                            width=float(groups[2]),
                            height=float(groups[3]),
                            weight=float(groups[4]),
                            material_type=groups[5],
                            panel_thickness=float(panel_thickness_str),
                            clearance=float(clearance_str)
                        )
                    elif len(groups) >= 7:
                        # Format without clearance
                        panel_thickness_str = groups[6].replace('_', '.')
                        
                        return ExpressionParameters(
                            timestamp=groups[0],
                            length=float(groups[1]),
                            width=float(groups[2]),
                            height=float(groups[3]),
                            weight=float(groups[4]),
                            material_type=groups[5],
                            panel_thickness=float(panel_thickness_str),
                            clearance=2.0  # Default clearance
                        )
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def find_matching_files(self, params: ExpressionParameters) -> List[str]:
        """
        Find all expression files that match the given parameters.
        
        Args:
            params: The parameters to match
            
        Returns:
            List of matching file paths
        """
        matching_files = []
        
        # Check main expressions directory
        exp_files = glob.glob(os.path.join(self.expressions_dir, "*.exp"))
        
        for exp_file in exp_files:
            existing_params = self.parse_filename(exp_file)
            if existing_params and existing_params.matches(params):
                matching_files.append(exp_file)
        
        return matching_files
    
    def clean_duplicates(self, params: ExpressionParameters, new_file_path: str) -> List[str]:
        """
        Remove duplicate expression files based on parameters.
        Keeps only the new file being created.
        
        Args:
            params: The parameters of the new expression
            new_file_path: Path of the new file being created
            
        Returns:
            List of deleted file paths
        """
        deleted_files = []
        matching_files = self.find_matching_files(params)
        
        for file_path in matching_files:
            # Don't delete the file we're about to create
            if os.path.abspath(file_path) != os.path.abspath(new_file_path):
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                except OSError as e:
                    print(f"Warning: Could not delete duplicate file {file_path}: {e}")
        
        return deleted_files
    
    def generate_filename(self, params: ExpressionParameters, 
                         panel_count: int = 5,
                         include_astm: bool = True) -> str:
        """
        Generate a standardized filename for an expression file.
        
        Args:
            params: The parameters for the expression
            panel_count: Number of panels (default 5)
            include_astm: Whether to include ASTM in filename
            
        Returns:
            Generated filename
        """
        # Generate timestamp if not provided
        if not params.timestamp:
            params.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Build filename components
        filename = (
            f"{params.timestamp}_Crate_"
            f"{params.length:.0f}x{params.width:.0f}x{params.height:.0f}_"
            f"W{params.weight:.0f}_"
            f"{panel_count}P_"
            f"{params.material_type}{params.panel_thickness:.2f}_"
            f"C{params.clearance:.1f}"
        )
        
        if include_astm:
            filename += "_ASTM"
        
        filename += ".exp"
        
        return filename
    
    def manage_expression_file(self, params: ExpressionParameters, 
                              output_path: str = None) -> Tuple[str, List[str]]:
        """
        Main method to manage expression files with intelligent replacement.
        
        Args:
            params: The parameters for the new expression
            output_path: Optional specific output path
            
        Returns:
            Tuple of (final_output_path, list_of_deleted_files)
        """
        # Generate filename if no specific path provided
        if not output_path:
            filename = self.generate_filename(params)
            output_path = os.path.join(self.expressions_dir, filename)
        
        # Clean up duplicates before saving
        deleted_files = self.clean_duplicates(params, output_path)
        
        return output_path, deleted_files


def extract_parameters_from_inputs(
    product_length: float,
    product_width: float,
    product_height: float,
    product_weight: float,
    panel_thickness: float,
    clearance: float
) -> ExpressionParameters:
    """
    Create ExpressionParameters from input values.
    
    Args:
        product_length: Product length in inches
        product_width: Product width in inches
        product_height: Product height in inches
        product_weight: Product weight in pounds
        panel_thickness: Panel thickness in inches
        clearance: Clearance in inches
        
    Returns:
        ExpressionParameters instance
    """
    # Determine material type based on thickness
    material_type = "PLY" if panel_thickness >= 0.5 else "OSB"
    
    return ExpressionParameters(
        length=product_length,
        width=product_width,
        height=product_height,
        weight=product_weight,
        material_type=material_type,
        panel_thickness=panel_thickness,
        clearance=clearance
    )