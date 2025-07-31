#!/usr/bin/env python3
"""
Plywood Layout Generator for Siemens NX

This script calculates the optimal layout of standard plywood sheets to cover a panel face,
minimizing the number of sheets used and prioritizing vertical splices over horizontal ones.
The output is a Siemens NX expressions (.exp) file.
"""

import math
import argparse
import os
from typing import List, Tuple, Dict

# Constants
MAX_PLYWOOD_DIMS = (96, 48)  # inches (width, height)
MAX_PLYWOOD_INSTANCES = 10   # Maximum number of plywood instances available in NX


def calculate_layout(panel_width: float, panel_height: float) -> List[Dict]:
    """
    Calculate the optimal layout of plywood sheets for the given panel dimensions.
    
    Args:
        panel_width: Width of the panel in inches
        panel_height: Height of the panel in inches
        
    Returns:
        List of dictionaries containing position and dimensions of each plywood sheet
    """
    # Determine how many sheets needed in each direction
    sheets_across = math.ceil(panel_width / MAX_PLYWOOD_DIMS[0])
    sheets_down = math.ceil(panel_height / MAX_PLYWOOD_DIMS[1])
    
    # Calculate total sheets needed for horizontal and vertical arrangements
    horizontal_priority_count = sheets_across * sheets_down
    
    # Try vertical arrangement (rotate sheets 90 degrees)
    rotated_sheets_across = math.ceil(panel_width / MAX_PLYWOOD_DIMS[1])
    rotated_sheets_down = math.ceil(panel_height / MAX_PLYWOOD_DIMS[0])
    vertical_priority_count = rotated_sheets_across * rotated_sheets_down
    
    # Choose the arrangement with fewer sheets, preferring vertical splices if tied
    sheets = []
    
    if vertical_priority_count <= horizontal_priority_count:
        # Use vertical arrangement (rotated sheets)
        for row in range(rotated_sheets_down):
            for col in range(rotated_sheets_across):
                x_pos = col * MAX_PLYWOOD_DIMS[1]
                y_pos = row * MAX_PLYWOOD_DIMS[0]
                
                # Calculate actual sheet width (may be smaller at edges)
                sheet_width = min(MAX_PLYWOOD_DIMS[1], panel_width - x_pos)
                sheet_height = min(MAX_PLYWOOD_DIMS[0], panel_height - y_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x': x_pos,
                        'y': y_pos,
                        'width': sheet_width,
                        'height': sheet_height
                    })
    else:
        # Use horizontal arrangement (standard orientation)
        for row in range(sheets_down):
            for col in range(sheets_across):
                x_pos = col * MAX_PLYWOOD_DIMS[0]
                y_pos = row * MAX_PLYWOOD_DIMS[1]
                
                # Calculate actual sheet width (may be smaller at edges)
                sheet_width = min(MAX_PLYWOOD_DIMS[0], panel_width - x_pos)
                sheet_height = min(MAX_PLYWOOD_DIMS[1], panel_height - y_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x': x_pos,
                        'y': y_pos,
                        'width': sheet_width,
                        'height': sheet_height
                    })
    
    return sheets


def generate_nx_expressions(sheets: List[Dict]) -> List[str]:
    """
    Generate NX expression statements for the calculated sheet layout.
    
    Args:
        sheets: List of sheet dictionaries with position and dimensions
        
    Returns:
        List of NX expression statements as strings
    """
    expressions = []
    
    # Set values for used plywood instances
    for i, sheet in enumerate(sheets[:MAX_PLYWOOD_INSTANCES]):
        instance_num = i + 1
        expressions.append(f'Plywood_{instance_num}_Active = 1')
        expressions.append(f'Plywood_{instance_num}_X_Position = {sheet["x"]}')
        expressions.append(f'Plywood_{instance_num}_Y_Position = {sheet["y"]}')
        expressions.append(f'Plywood_{instance_num}_Width = {sheet["width"]}')
        expressions.append(f'Plywood_{instance_num}_Height = {sheet["height"]}')
    
    # Set remaining unused instances to inactive
    for i in range(len(sheets), MAX_PLYWOOD_INSTANCES):
        instance_num = i + 1
        expressions.append(f'Plywood_{instance_num}_Active = 0')
        expressions.append(f'Plywood_{instance_num}_X_Position = 0')
        expressions.append(f'Plywood_{instance_num}_Y_Position = 0')
        expressions.append(f'Plywood_{instance_num}_Width = 0')
        expressions.append(f'Plywood_{instance_num}_Height = 0')
    
    return expressions


def read_panel_dimensions_from_exp(nx_exp_file: str) -> Tuple[float, float]:
    """
    Read panel dimensions from an existing NX expressions file.
    
    Args:
        nx_exp_file: Path to the NX expressions file
        
    Returns:
        Tuple of (panel_width, panel_height) in inches
    """
    panel_width = None
    panel_height = None
    
    try:
        with open(nx_exp_file, 'r') as f:
            for line in f:
                line = line.strip()
                if 'Front_Panel_Width' in line:
                    panel_width = float(line.split('=')[1].strip())
                elif 'Front_Panel_Height' in line:
                    panel_height = float(line.split('=')[1].strip())
                
                # If we found both dimensions, we can stop reading
                if panel_width is not None and panel_height is not None:
                    break
    except Exception as e:
        raise ValueError(f"Error reading panel dimensions from {nx_exp_file}: {e}")
    
    if panel_width is None or panel_height is None:
        raise ValueError(f"Could not find panel dimensions in {nx_exp_file}")
    
    return panel_width, panel_height


def write_exp_file(output_file: str, expressions: List[str]) -> None:
    """
    Write expressions to an NX expressions file.
    
    Args:
        output_file: Path to the output file
        expressions: List of expression statements
    """
    try:
        with open(output_file, 'w') as f:
            for expr in expressions:
                f.write(expr + '\n')
        print(f"Successfully wrote expressions to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Generate plywood layout for Siemens NX')
    parser.add_argument('--input', required=True, help='Input NX expressions file to read panel dimensions')
    parser.add_argument('--output', required=True, help='Output NX expressions file')
    parser.add_argument('--manual-dimensions', action='store_true', help='Manually specify panel dimensions')
    parser.add_argument('--width', type=float, help='Panel width in inches (if manual dimensions)')
    parser.add_argument('--height', type=float, help='Panel height in inches (if manual dimensions)')
    
    args = parser.parse_args()
    
    # Get panel dimensions
    if args.manual_dimensions:
        if args.width is None or args.height is None:
            parser.error("--width and --height are required with --manual-dimensions")
        panel_width = args.width
        panel_height = args.height
    else:
        try:
            panel_width, panel_height = read_panel_dimensions_from_exp(args.input)
        except ValueError as e:
            parser.error(str(e))
    
    # Calculate layout
    sheets = calculate_layout(panel_width, panel_height)
    
    # Check if we have too many sheets
    if len(sheets) > MAX_PLYWOOD_INSTANCES:
        print(f"WARNING: Layout requires {len(sheets)} sheets, but only {MAX_PLYWOOD_INSTANCES} instances available.")
        print("Only the first 10 sheets will be included in the output.")
    
    # Generate expressions
    expressions = generate_nx_expressions(sheets)
    
    # Write expressions file
    write_exp_file(args.output, expressions)
    
    # Print summary
    print(f"Panel dimensions: {panel_width} × {panel_height} inches")
    print(f"Plywood layout: {len(sheets)} sheets required (using {min(len(sheets), MAX_PLYWOOD_INSTANCES)})")


if __name__ == "__main__":
    main()
