"""
NX Expression Generator Module

This module handles the generation of Siemens NX expressions files
from calculated panel components. It preserves the original expression
generation logic while providing a cleaner interface.
"""

import datetime
import math
from typing import Dict, List, Tuple, Any
from ..exceptions import CalculationError, ValidationError


class ExpressionGenerator:
    """Generates NX expressions from calculated panel components."""
    
    def __init__(self):
        """Initialize the expression generator."""
        self.timestamp = None
        self.output_lines = []
    
    def generate_expressions(
        self, 
        panel_components: Dict[str, Any],
        output_filename: str = None
    ) -> str:
        """
        Generate NX expressions from calculated panel components.
        
        Args:
            panel_components: Dictionary containing all calculated panel data
            output_filename: Optional output filename
            
        Returns:
            str: Generated expressions content
            
        Raises:
            CalculationError: If component calculation fails
            ValidationError: If input validation fails
        """
        try:
            self.timestamp = datetime.datetime.now()
            self.output_lines = []
            
            # Add header
            self._add_header()
            
            # Generate expressions for each panel type
            self._generate_front_panel_expressions(panel_components.get('front_panel', {}))
            self._generate_back_panel_expressions(panel_components.get('back_panel', {}))
            self._generate_left_panel_expressions(panel_components.get('left_panel', {}))
            self._generate_right_panel_expressions(panel_components.get('right_panel', {}))
            self._generate_top_panel_expressions(panel_components.get('top_panel', {}))
            self._generate_end_panel_expressions(panel_components.get('end_panel', {}))
            self._generate_skid_expressions(panel_components.get('skid', {}))
            self._generate_floorboard_expressions(panel_components.get('floorboard', {}))
            
            # Join all lines
            content = '\n'.join(self.output_lines)
            
            # Write to file if specified
            if output_filename:
                self._write_to_file(content, output_filename)
            
            return content
            
        except Exception as e:
            raise CalculationError(f"Failed to generate expressions: {str(e)}")
    
    def _add_header(self):
        """Add header with timestamp and metadata."""
        self.output_lines.extend([
            f"// AutoCrate NX Expressions File",
            f"// Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"// AutoCrate Version: 12.0.2",
            "//",
            ""
        ])
    
    def _generate_front_panel_expressions(self, components: Dict[str, Any]):
        """Generate expressions for front panel components."""
        if not components:
            return
            
        self.output_lines.append("// Front Panel Components")
        
        # Add each component as an expression
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _generate_back_panel_expressions(self, components: Dict[str, Any]):
        """Generate expressions for back panel components."""
        if not components:
            return
            
        self.output_lines.append("// Back Panel Components")
        
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _generate_left_panel_expressions(self, components: Dict[str, Any]):
        """Generate expressions for left panel components."""
        if not components:
            return
            
        self.output_lines.append("// Left Panel Components")
        
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _generate_right_panel_expressions(self, components: Dict[str, Any]):
        """Generate expressions for right panel components.""" 
        if not components:
            return
            
        self.output_lines.append("// Right Panel Components")
        
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _generate_top_panel_expressions(self, components: Dict[str, Any]):
        """Generate expressions for top panel components."""
        if not components:
            return
            
        self.output_lines.append("// Top Panel Components")
        
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _generate_end_panel_expressions(self, components: Dict[str, Any]):
        """Generate expressions for end panel components."""
        if not components:
            return
            
        self.output_lines.append("// End Panel Components")
        
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _generate_skid_expressions(self, components: Dict[str, Any]):
        """Generate expressions for skid components."""
        if not components:
            return
            
        self.output_lines.append("// Skid Components")
        
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _generate_floorboard_expressions(self, components: Dict[str, Any]):
        """Generate expressions for floorboard components."""
        if not components:
            return
            
        self.output_lines.append("// Floorboard Components")
        
        for key, value in components.items():
            if isinstance(value, (int, float)):
                self.output_lines.append(f"{key} = {value}")
        
        self.output_lines.append("")
    
    def _write_to_file(self, content: str, filename: str):
        """Write expressions to file."""
        try:
            with open(filename, 'w') as f:
                f.write(content)
        except IOError as e:
            raise CalculationError(f"Failed to write expressions file: {str(e)}")