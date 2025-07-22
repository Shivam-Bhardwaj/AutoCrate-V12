import pytest
from unittest.mock import mock_open, patch
from plywood_layout_generator import (
    calculate_layout,
    generate_nx_expressions,
    read_panel_dimensions_from_exp,
    write_exp_file,
    main,
    MAX_PLYWOOD_INSTANCES
)
import argparse
import os

# Test cases for calculate_layout to cover more scenarios
def test_calculate_layout_horizontal_priority():
    """
    Test case where horizontal arrangement is preferred.
    Panel: 100x40
    Horizontal: ceil(100/96)=2, ceil(40/48)=1 -> 2*1=2 sheets
    Vertical: ceil(100/48)=3, ceil(40/96)=1 -> 3*1=3 sheets
    """
    sheets = calculate_layout(100, 40)
    assert len(sheets) == 2
    assert sheets[0] == {'x': 0, 'y': 0, 'width': 96, 'height': 40}
    assert sheets[1] == {'x': 96, 'y': 0, 'width': 4, 'height': 40}

def test_calculate_layout_no_zero_dimension_sheets():
    """
    Test that sheets with zero width or height are not added.
    """
    # This should result in exactly one sheet, not a second one with 0 width.
    sheets = calculate_layout(96, 48)
    assert len(sheets) == 1

# Tests for read_panel_dimensions_from_exp
def test_read_panel_dimensions_from_exp_success():
    """
    Test reading dimensions from a valid .exp file.
    """
    mock_content = "Front_Panel_Width = 120.5\nFront_Panel_Height = 80.0\n"
    m = mock_open(read_data=mock_content)
    with patch('builtins.open', m):
        width, height = read_panel_dimensions_from_exp("dummy_path.exp")
        assert width == 120.5
        assert height == 80.0

def test_read_panel_dimensions_from_exp_missing_dims():
    """
    Test .exp file missing one or both dimension values.
    """
    mock_content = "Front_Panel_Width = 120.5\n"
    m = mock_open(read_data=mock_content)
    with patch('builtins.open', m):
        with pytest.raises(ValueError, match="Could not find panel dimensions"):
            read_panel_dimensions_from_exp("dummy_path.exp")

def test_read_panel_dimensions_from_exp_file_not_found():
    """
    Test handling of file not found error.
    """
    with patch('builtins.open', side_effect=FileNotFoundError):
        with pytest.raises(ValueError, match="Error reading panel dimensions"):
            read_panel_dimensions_from_exp("non_existent_file.exp")

# Tests for write_exp_file
def test_write_exp_file_success():
    """
    Test successful writing of an .exp file.
    """
    m = mock_open()
    with patch('builtins.open', m):
        expressions = ["expr1", "expr2"]
        write_exp_file("dummy_output.exp", expressions)
        m.assert_called_once_with("dummy_output.exp", 'w')
        handle = m()
        handle.write.assert_any_call("expr1\n")
        handle.write.assert_any_call("expr2\n")

def test_write_exp_file_error():
    """
    Test handling of an error during file writing.
    """
    m = mock_open()
    m.side_effect = IOError("Disk full")
    with patch('builtins.open', m), patch('builtins.print') as mock_print:
        write_exp_file("dummy_output.exp", ["expr1"])
        mock_print.assert_called_with("Error writing to dummy_output.exp: Disk full")

# Tests for the main function and argument parsing
@patch('argparse.ArgumentParser.parse_args')
@patch('plywood_layout_generator.read_panel_dimensions_from_exp')
@patch('plywood_layout_generator.calculate_layout')
@patch('plywood_layout_generator.generate_nx_expressions')
@patch('plywood_layout_generator.write_exp_file')
def test_main_flow_from_input_file(mock_write, mock_generate, mock_calculate, mock_read, mock_parse_args):
    """
    Test the main execution flow when reading from an input file.
    """
    mock_parse_args.return_value = argparse.Namespace(
        input='input.exp', output='output.exp', manual_dimensions=False, width=None, height=None
    )
    mock_read.return_value = (100, 50)
    mock_calculate.return_value = [{'x': 0, 'y': 0, 'width': 48, 'height': 50}]
    mock_generate.return_value = ["...expressions..."]

    main()

    mock_read.assert_called_once_with('input.exp')
    mock_calculate.assert_called_once_with(100, 50)
    mock_generate.assert_called_once_with([{'x': 0, 'y': 0, 'width': 48, 'height': 50}])
    mock_write.assert_called_once_with('output.exp', ["...expressions..."])

@patch('argparse.ArgumentParser.parse_args')
@patch('plywood_layout_generator.calculate_layout')
@patch('plywood_layout_generator.generate_nx_expressions')
@patch('plywood_layout_generator.write_exp_file')
def test_main_flow_manual_dimensions(mock_write, mock_generate, mock_calculate, mock_parse_args):
    """
    Test the main execution flow with manually provided dimensions.
    """
    mock_parse_args.return_value = argparse.Namespace(
        input=None, output='output.exp', manual_dimensions=True, width=120, height=60
    )
    mock_calculate.return_value = []
    mock_generate.return_value = []

    main()

    mock_calculate.assert_called_once_with(120, 60)
    mock_write.assert_called_once_with('output.exp', [])

@patch('argparse.ArgumentParser.parse_args')
def test_main_manual_dimensions_missing_args(mock_parse_args):
    """
    Test error handling when manual dimensions are selected but not provided.
    """
    mock_parse_args.return_value = argparse.Namespace(
        input=None, output='output.exp', manual_dimensions=True, width=None, height=60
    )
    with pytest.raises(SystemExit): # argparse.error calls sys.exit
        main()

@patch('argparse.ArgumentParser.parse_args')
@patch('plywood_layout_generator.read_panel_dimensions_from_exp', side_effect=ValueError("Test error"))
def test_main_read_error_handling(mock_read, mock_parse_args):
    """
    Test error handling when reading dimensions from a file fails.
    """
    mock_parse_args.return_value = argparse.Namespace(
        input='bad.exp', output='output.exp', manual_dimensions=False, width=None, height=None
    )
    with pytest.raises(SystemExit):
        main()

@patch('argparse.ArgumentParser.parse_args')
@patch('plywood_layout_generator.calculate_layout')
@patch('builtins.print')
def test_main_warning_for_too_many_sheets(mock_print, mock_calculate, mock_parse_args):
    """
    Test that a warning is printed if the layout requires too many sheets.
    """
    mock_parse_args.return_value = argparse.Namespace(
        input=None, output='output.exp', manual_dimensions=True, width=1000, height=1000
    )
    # Create a layout with more sheets than available instances
    sheets = [{'x': 0, 'y': 0}] * (MAX_PLYWOOD_INSTANCES + 1)
    mock_calculate.return_value = sheets

    main()

    mock_print.assert_any_call(f"WARNING: Layout requires {len(sheets)} sheets, but only {MAX_PLYWOOD_INSTANCES} instances available.")
