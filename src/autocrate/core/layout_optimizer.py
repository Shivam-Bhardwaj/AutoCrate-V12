"""
Plywood Layout Optimizer for AutoCrate

This module contains the plywood layout optimization logic that minimizes
waste and prioritizes vertical splices. The original logic is preserved
while providing a cleaner interface.
"""

import math
from typing import List, Dict, Tuple
from ..exceptions import ValidationError, CalculationError


class PlywoodLayoutGenerator:
    """Generates optimal plywood layout for panels."""
    
    # Constants
    MAX_PLYWOOD_DIMS = (96, 48)  # inches (width, height)
    MAX_PLYWOOD_INSTANCES = 10   # Maximum number of plywood instances available in NX
    
    def __init__(self):
        """Initialize the plywood layout generator."""
        self.layouts_calculated = 0
    
    def calculate_layout(
        self, 
        panel_width: float, 
        panel_height: float
    ) -> List[Dict]:
        """
        Calculate the optimal layout of plywood sheets for the given panel dimensions.
        
        Args:
            panel_width: Width of the panel in inches
            panel_height: Height of the panel in inches
            
        Returns:
            List of dictionaries containing position and dimensions of each plywood sheet
            
        Raises:
            ValidationError: If input dimensions are invalid
            CalculationError: If layout calculation fails
        """
        # Validate inputs
        if panel_width <= 0 or panel_height <= 0:
            raise ValidationError("Panel dimensions must be positive")
        
        if panel_width > 1000 or panel_height > 1000:
            raise ValidationError("Panel dimensions are unreasonably large")
        
        try:
            # Determine how many sheets needed in each direction
            sheets_across = math.ceil(panel_width / self.MAX_PLYWOOD_DIMS[0])
            sheets_down = math.ceil(panel_height / self.MAX_PLYWOOD_DIMS[1])
            
            # Calculate total sheets needed for horizontal and vertical arrangements
            horizontal_priority_count = sheets_across * sheets_down
            
            # Try vertical arrangement (rotate sheets 90 degrees)
            rotated_sheets_across = math.ceil(panel_width / self.MAX_PLYWOOD_DIMS[1])
            rotated_sheets_down = math.ceil(panel_height / self.MAX_PLYWOOD_DIMS[0])
            vertical_priority_count = rotated_sheets_across * rotated_sheets_down
            
            # Choose the arrangement with fewer sheets, preferring vertical splices if tied
            sheets = []
            
            if vertical_priority_count <= horizontal_priority_count:
                # Use vertical arrangement (rotated sheets)
                sheets = self._calculate_vertical_layout(
                    panel_width, panel_height, 
                    rotated_sheets_across, rotated_sheets_down
                )
            else:
                # Use horizontal arrangement
                sheets = self._calculate_horizontal_layout(
                    panel_width, panel_height,
                    sheets_across, sheets_down
                )
            
            # Validate sheet count
            if len(sheets) > self.MAX_PLYWOOD_INSTANCES:
                raise CalculationError(
                    f"Layout requires {len(sheets)} sheets, but only "
                    f"{self.MAX_PLYWOOD_INSTANCES} instances available"
                )
            
            self.layouts_calculated += 1
            return sheets
            
        except Exception as e:
            if isinstance(e, (ValidationError, CalculationError)):
                raise
            else:
                raise CalculationError(f"Layout calculation failed: {str(e)}")
    
    def _calculate_vertical_layout(
        self, 
        panel_width: float, 
        panel_height: float,
        sheets_across: int,
        sheets_down: int
    ) -> List[Dict]:
        """Calculate vertical arrangement layout (rotated sheets)."""
        sheets = []
        
        # Calculate remainder height for splice positioning
        total_full_rows = sheets_down - 1
        remainder_height = panel_height - (total_full_rows * self.MAX_PLYWOOD_DIMS[0])
        
        for row in range(sheets_down):
            for col in range(sheets_across):
                x_pos = col * self.MAX_PLYWOOD_DIMS[1]
                
                # Reverse the row order: put smaller panels at bottom, larger panels at top
                if sheets_down > 1:
                    if row == 0:
                        # Bottom row: use remainder height (smaller)
                        y_pos = 0
                        sheet_height = min(remainder_height, panel_height)
                    else:
                        # Upper rows: use full sheet height (larger)
                        y_pos = remainder_height + (row - 1) * self.MAX_PLYWOOD_DIMS[0]
                        sheet_height = min(self.MAX_PLYWOOD_DIMS[0], panel_height - y_pos)
                else:
                    # Single row case
                    y_pos = row * self.MAX_PLYWOOD_DIMS[0]
                    sheet_height = min(self.MAX_PLYWOOD_DIMS[0], panel_height - y_pos)
                
                # Calculate actual sheet width (may be smaller at edges)
                sheet_width = min(self.MAX_PLYWOOD_DIMS[1], panel_width - x_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x_position': x_pos,
                        'y_position': y_pos,
                        'width': sheet_width,
                        'height': sheet_height,
                        'rotated': True,
                        'instance': len(sheets) + 1
                    })
        
        return sheets
    
    def _calculate_horizontal_layout(
        self,
        panel_width: float,
        panel_height: float, 
        sheets_across: int,
        sheets_down: int
    ) -> List[Dict]:
        """Calculate horizontal arrangement layout."""
        sheets = []
        
        for row in range(sheets_down):
            for col in range(sheets_across):
                x_pos = col * self.MAX_PLYWOOD_DIMS[0]
                y_pos = row * self.MAX_PLYWOOD_DIMS[1]
                
                # Calculate actual sheet dimensions (may be smaller at edges)
                sheet_width = min(self.MAX_PLYWOOD_DIMS[0], panel_width - x_pos)
                sheet_height = min(self.MAX_PLYWOOD_DIMS[1], panel_height - y_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x_position': x_pos,
                        'y_position': y_pos,
                        'width': sheet_width,
                        'height': sheet_height,
                        'rotated': False,
                        'instance': len(sheets) + 1
                    })
        
        return sheets
    
    def get_layout_info(
        self, 
        panel_width: float, 
        panel_height: float
    ) -> Dict[str, any]:
        """
        Get layout information without calculating full layout.
        
        Args:
            panel_width: Width of the panel in inches
            panel_height: Height of the panel in inches
            
        Returns:
            Dictionary with layout summary information
        """
        # Calculate both arrangements
        h_across = math.ceil(panel_width / self.MAX_PLYWOOD_DIMS[0])
        h_down = math.ceil(panel_height / self.MAX_PLYWOOD_DIMS[1])
        horizontal_count = h_across * h_down
        
        v_across = math.ceil(panel_width / self.MAX_PLYWOOD_DIMS[1])  
        v_down = math.ceil(panel_height / self.MAX_PLYWOOD_DIMS[0])
        vertical_count = v_across * v_down
        
        optimal_count = min(horizontal_count, vertical_count)
        optimal_arrangement = "vertical" if vertical_count <= horizontal_count else "horizontal"
        
        return {
            'panel_width': panel_width,
            'panel_height': panel_height,
            'horizontal_arrangement_count': horizontal_count,
            'vertical_arrangement_count': vertical_count,
            'optimal_count': optimal_count,
            'optimal_arrangement': optimal_arrangement,
            'waste_percentage': self._calculate_waste_percentage(
                panel_width, panel_height, optimal_count
            )
        }
    
    def _calculate_waste_percentage(
        self, 
        panel_width: float, 
        panel_height: float, 
        sheet_count: int
    ) -> float:
        """Calculate waste percentage for the layout."""
        panel_area = panel_width * panel_height
        sheet_area = self.MAX_PLYWOOD_DIMS[0] * self.MAX_PLYWOOD_DIMS[1]
        total_sheet_area = sheet_count * sheet_area
        
        if total_sheet_area == 0:
            return 0.0
        
        waste_area = total_sheet_area - panel_area
        return (waste_area / total_sheet_area) * 100