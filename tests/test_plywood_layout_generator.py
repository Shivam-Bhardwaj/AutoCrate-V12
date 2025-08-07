import pytest
from unittest.mock import patch, mock_open
from autocrate.plywood_layout_generator import (
    calculate_layout, generate_nx_expressions, read_panel_dimensions_from_exp,
    write_exp_file, main, MAX_PLYWOOD_INSTANCES
)

# Test cases for calculate_layout
# Each tuple contains: (panel_width, panel_height, expected_sheet_count, expected_first_sheet_dims)
layout_test_cases = [
    # Case 1: Panel fits perfectly on one standard sheet
    (96, 48, 1, {'x': 0, 'y': 0, 'width': 96, 'height': 48}),
    
    # Case 2: Panel fits perfectly on one rotated sheet
    (48, 96, 1, {'x': 0, 'y': 0, 'width': 48, 'height': 96}),
    
    # Case 3: Panel requires horizontal splicing (standard orientation preferred)
    # 100 / 96 -> 2 sheets across. 40 / 48 -> 1 sheet down. Total = 2 sheets.
    # Rotated: 100 / 48 -> 3 sheets across. 40 / 96 -> 1 sheet down. Total = 3 sheets.
    (100, 40, 2, {'x': 0, 'y': 0, 'width': 96, 'height': 40}),
    
    # Case 4: Panel requires vertical splicing (rotated orientation is more efficient)
    # 100 / 96 -> 2 sheets across. 50 / 48 -> 2 sheets down. Total = 4 sheets.
    # Rotated: 100 / 48 -> 3 sheets across. 50 / 96 -> 1 sheet down. Total = 3 sheets.
    (100, 50, 3, {'x': 0, 'y': 0, 'width': 48, 'height': 50}),
    
    # Case 5: A large panel requiring 3 sheets when rotated (130/48=3 across, 90/96=1 down)
    (130, 90, 3, {'x': 0, 'y': 0, 'width': 48, 'height': 90}),
]

@pytest.mark.parametrize("panel_width, panel_height, expected_count, expected_first_sheet", layout_test_cases)
def test_calculate_layout(panel_width, panel_height, expected_count, expected_first_sheet):
    """
    Tests the plywood layout calculation for various panel sizes and orientations.
    """
    sheets = calculate_layout(panel_width, panel_height)
    
    assert len(sheets) == expected_count
    assert sheets[0] == expected_first_sheet

def test_generate_nx_expressions_standard():
    """
    Tests the generation of NX expressions for a standard layout with a few sheets.
    """
    sheets = [
        {'x': 0, 'y': 0, 'width': 96, 'height': 48},
        {'x': 96, 'y': 0, 'width': 4, 'height': 48},
    ]
    expressions = generate_nx_expressions(sheets)
    
    assert len(expressions) == MAX_PLYWOOD_INSTANCES * 5  # 5 expressions per instance
    assert 'Plywood_1_Active = 1' in expressions
    assert 'Plywood_1_Width = 96' in expressions
    assert 'Plywood_2_Active = 1' in expressions
    assert 'Plywood_2_X_Position = 96' in expressions
    assert 'Plywood_3_Active = 0' in expressions # Check that unused instances are inactive

def test_generate_nx_expressions_overflow():
    """
    Tests that if more sheets are needed than available instances, the extra sheets are ignored.
    """
    # Create a layout with more sheets than the max instances
    sheets = [{'x': i*10, 'y': 0, 'width': 10, 'height': 10} for i in range(MAX_PLYWOOD_INSTANCES + 5)]
    
    expressions = generate_nx_expressions(sheets)
    
    # Ensure all available instances are marked as active
    for i in range(MAX_PLYWOOD_INSTANCES):
        assert f'Plywood_{i+1}_Active = 1' in expressions
        
    # Verify that the data for the 10th instance is correct
    assert f'Plywood_{MAX_PLYWOOD_INSTANCES}_X_Position = 90' in expressions


def test_read_panel_dimensions_from_exp():
    mock_file_content = """
    Front_Panel_Width = 48.0
    Some_Other_Expression = 123
    Front_Panel_Height = 96.0
    """
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        width, height = read_panel_dimensions_from_exp("test.exp")
        assert width == 48.0
        assert height == 96.0


def test_read_panel_dimensions_from_exp_missing_dimension():
    mock_file_content = """
    Front_Panel_Width = 48.0
    Some_Other_Expression = 123
    """
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        with pytest.raises(ValueError, match="Could not find panel dimensions"):
            read_panel_dimensions_from_exp("test.exp")


def test_read_panel_dimensions_from_exp_file_error():
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with pytest.raises(ValueError, match="Error reading panel dimensions"):
            read_panel_dimensions_from_exp("nonexistent.exp")


def test_write_exp_file():
    expressions = ["expr1=value1", "expr2=value2"]
    
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        write_exp_file("output.exp", expressions)
    
    # Check that file was opened for writing
    mock_file.assert_called_once_with("output.exp", 'w')
    
    # Check that expressions were written
    handle = mock_file()
    calls = [call[0][0] for call in handle.write.call_args_list]
    assert "expr1=value1\n" in calls
    assert "expr2=value2\n" in calls


def test_write_exp_file_error(capsys):
    expressions = ["expr1=value1"]
    
    with patch("builtins.open", side_effect=IOError("Write error")):
        write_exp_file("output.exp", expressions)
    
    # Check error message was printed
    captured = capsys.readouterr()
    assert "Error writing to output.exp: Write error" in captured.out


@patch("autocrate.plywood_layout_generator.argparse.ArgumentParser.parse_args")
@patch("autocrate.plywood_layout_generator.read_panel_dimensions_from_exp")
@patch("autocrate.plywood_layout_generator.calculate_layout")
@patch("autocrate.plywood_layout_generator.generate_nx_expressions")
@patch("autocrate.plywood_layout_generator.write_exp_file")
def test_main_with_input_file(mock_write, mock_generate, mock_calculate, mock_read_dims, mock_args, capsys):
    # Setup mocks
    mock_args.return_value = type('args', (), {
        'input': 'input.exp',
        'output': 'output.exp',
        'manual_dimensions': False,
        'width': None,
        'height': None
    })
    mock_read_dims.return_value = (48.0, 96.0)
    mock_calculate.return_value = [{'x': 0, 'y': 0, 'width': 48, 'height': 96}]
    mock_generate.return_value = ["expr1=value1"]
    
    # Run main
    main()
    
    # Verify calls
    mock_read_dims.assert_called_once_with('input.exp')
    mock_calculate.assert_called_once_with(48.0, 96.0)
    mock_generate.assert_called_once()
    mock_write.assert_called_once_with('output.exp', ["expr1=value1"])
    
    # Check output
    captured = capsys.readouterr()
    assert "Panel dimensions: 48.0 × 96.0 inches" in captured.out
    assert "Plywood layout: 1 sheets required" in captured.out


@patch("autocrate.plywood_layout_generator.argparse.ArgumentParser.parse_args")
@patch("autocrate.plywood_layout_generator.calculate_layout")
@patch("autocrate.plywood_layout_generator.generate_nx_expressions")
@patch("autocrate.plywood_layout_generator.write_exp_file")
def test_main_with_manual_dimensions(mock_write, mock_generate, mock_calculate, mock_args, capsys):
    # Setup mocks
    mock_args.return_value = type('args', (), {
        'input': 'input.exp',
        'output': 'output.exp',
        'manual_dimensions': True,
        'width': 60.0,
        'height': 120.0
    })
    mock_calculate.return_value = [{'x': 0, 'y': 0, 'width': 60, 'height': 120}]
    mock_generate.return_value = ["expr1=value1"]
    
    # Run main
    main()
    
    # Verify calls
    mock_calculate.assert_called_once_with(60.0, 120.0)
    mock_generate.assert_called_once()
    mock_write.assert_called_once_with('output.exp', ["expr1=value1"])
    
    # Check output
    captured = capsys.readouterr()
    assert "Panel dimensions: 60.0 × 120.0 inches" in captured.out


@patch("autocrate.plywood_layout_generator.argparse.ArgumentParser.parse_args")
def test_main_manual_dimensions_missing_values(mock_args):
    # Setup mocks - missing height
    mock_args.return_value = type('args', (), {
        'input': 'input.exp',
        'output': 'output.exp',
        'manual_dimensions': True,
        'width': 60.0,
        'height': None
    })
    
    # Mock parser.error to raise SystemExit (as argparse does)
    with patch("autocrate.plywood_layout_generator.argparse.ArgumentParser.error", side_effect=SystemExit(2)):
        with pytest.raises(SystemExit):
            main()


@patch("autocrate.plywood_layout_generator.argparse.ArgumentParser.parse_args")
@patch("autocrate.plywood_layout_generator.calculate_layout")
@patch("autocrate.plywood_layout_generator.generate_nx_expressions")
@patch("autocrate.plywood_layout_generator.write_exp_file")
def test_main_with_too_many_sheets(mock_write, mock_generate, mock_calculate, mock_args, capsys):
    # Setup mocks
    mock_args.return_value = type('args', (), {
        'input': 'input.exp',
        'output': 'output.exp',
        'manual_dimensions': True,
        'width': 130.0,
        'height': 130.0
    })
    
    # Create 12 sheets (more than MAX_PLYWOOD_INSTANCES)
    sheets = []
    for i in range(12):
        sheets.append({'x': i*10, 'y': 0, 'width': 10, 'height': 10})
    mock_calculate.return_value = sheets
    mock_generate.return_value = ["expr1=value1"]
    
    # Run main
    main()
    
    # Check warning output
    captured = capsys.readouterr()
    assert "WARNING: Layout requires 12 sheets, but only 10 instances available." in captured.out
    assert "Only the first 10 sheets will be included in the output." in captured.out


@patch("autocrate.plywood_layout_generator.argparse.ArgumentParser.parse_args")
@patch("autocrate.plywood_layout_generator.read_panel_dimensions_from_exp")
def test_main_read_dimensions_error(mock_read_dims, mock_args):
    # Setup mocks
    mock_args.return_value = type('args', (), {
        'input': 'input.exp',
        'output': 'output.exp',
        'manual_dimensions': False,
        'width': None,
        'height': None
    })
    mock_read_dims.side_effect = ValueError("Test error reading file")
    
    # Mock parser.error to raise SystemExit
    with patch("autocrate.plywood_layout_generator.argparse.ArgumentParser.error", side_effect=SystemExit(2)):
        with pytest.raises(SystemExit):
            main()