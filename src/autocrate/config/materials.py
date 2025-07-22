"""
Material configuration and properties for AutoCrate.

This module manages material properties, lumber specifications,
and construction standards.
"""

import json
import os
from typing import Dict, List, Any, Optional
from ..exceptions import ConfigurationError
from ..utils.constants import MATERIAL_CONSTANTS, LUMBER_SIZES, PLYWOOD_SIZES


class MaterialConfig:
    """Manages material properties and specifications."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize material configuration.
        
        Args:
            config_file: Path to materials configuration file
        """
        self._config_file = config_file
        self._materials = {}
        self._load_defaults()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def _load_defaults(self):
        """Load default material specifications."""
        self._materials = {
            'lumber': {
                'standard_sizes': dict(LUMBER_SIZES),
                'properties': {
                    'density_psf': MATERIAL_CONSTANTS['wood_density_psf'],
                    'moisture_content': MATERIAL_CONSTANTS['lumber_moisture_content'],
                    'strength_grade': 'Construction Grade',
                    'species': 'Douglas Fir',
                },
                'dimensions': {
                    'nominal_to_actual': {
                        '2x4': (1.5, 3.5),
                        '2x6': (1.5, 5.5),
                        '2x8': (1.5, 7.25),
                        '2x10': (1.5, 9.25),
                        '2x12': (1.5, 11.25),
                    },
                    'standard_lengths': [8, 10, 12, 16, 20],  # feet
                },
                'cost_per_bf': 0.85,  # dollars per board foot
            },
            'plywood': {
                'standard_sizes': {
                    'sheet_dimensions': PLYWOOD_SIZES['standard_sheet'],
                    'thickness_options': PLYWOOD_SIZES['thickness_options'],
                },
                'properties': {
                    'density_psf': MATERIAL_CONSTANTS['plywood_density_psf'],
                    'grade': 'CDX',
                    'face_grade': 'C',
                    'back_grade': 'D',
                    'glue_type': 'Exterior',
                },
                'specifications': {
                    'span_rating': '32/16',
                    'exposure_rating': 'Exposure 1',
                    'emission_standard': 'CARB Phase 2',
                },
                'cost_per_sqft': 1.25,  # dollars per square foot
            },
            'fasteners': {
                'screws': {
                    'wood_screws': {
                        'sizes': ['#8', '#10', '#12'],
                        'lengths': [1.25, 1.5, 2.0, 2.5, 3.0],  # inches
                        'material': 'Steel',
                        'coating': 'Zinc Plated',
                        'drive_type': 'Phillips',
                    },
                    'deck_screws': {
                        'sizes': ['#8', '#10'],
                        'lengths': [2.0, 2.5, 3.0],  # inches
                        'material': 'Stainless Steel',
                        'coating': 'None',
                        'drive_type': 'Torx',
                    }
                },
                'nails': {
                    'common_nails': {
                        'sizes': ['8d', '10d', '16d'],
                        'lengths': [2.5, 3.0, 3.5],  # inches
                        'material': 'Steel',
                        'coating': 'Bright',
                    }
                }
            },
            'adhesives': {
                'wood_glue': {
                    'type': 'PVA',
                    'strength': 'Type II',
                    'open_time': 10,  # minutes
                    'clamp_time': 30,  # minutes
                    'cure_time': 24,  # hours
                },
                'construction_adhesive': {
                    'type': 'Polyurethane',
                    'strength': 'Structural',
                    'temperature_range': (-40, 180),  # Fahrenheit
                    'cure_time': 24,  # hours
                }
            }
        }
    
    def get_lumber_properties(self) -> Dict[str, Any]:
        """Get lumber properties and specifications."""
        return self._materials.get('lumber', {}).copy()
    
    def get_plywood_properties(self) -> Dict[str, Any]:
        """Get plywood properties and specifications."""
        return self._materials.get('plywood', {}).copy()
    
    def get_standard_lumber_sizes(self) -> Dict[str, float]:
        """Get standard lumber sizes."""
        return self._materials.get('lumber', {}).get('standard_sizes', {}).copy()
    
    def get_actual_lumber_dimensions(self, nominal_size: str) -> Optional[tuple]:
        """
        Get actual dimensions for nominal lumber size.
        
        Args:
            nominal_size: Nominal size string (e.g., '2x6')
            
        Returns:
            Tuple of (thickness, width) or None if not found
        """
        dimensions = self._materials.get('lumber', {}).get('dimensions', {})
        return dimensions.get('nominal_to_actual', {}).get(nominal_size)
    
    def get_plywood_thickness_options(self) -> List[float]:
        """Get available plywood thickness options."""
        plywood = self._materials.get('plywood', {})
        sizes = plywood.get('standard_sizes', {})
        return sizes.get('thickness_options', []).copy()
    
    def get_material_density(self, material_type: str) -> Optional[float]:
        """
        Get density for a material type.
        
        Args:
            material_type: Type of material ('lumber' or 'plywood')
            
        Returns:
            Density in pounds per cubic foot or None if not found
        """
        material = self._materials.get(material_type, {})
        properties = material.get('properties', {})
        
        if material_type == 'lumber':
            return properties.get('density_psf')
        elif material_type == 'plywood':
            return properties.get('density_psf')
        
        return None
    
    def calculate_material_cost(
        self, 
        material_type: str, 
        quantity: float, 
        unit: str = 'bf'
    ) -> Optional[float]:
        """
        Calculate material cost.
        
        Args:
            material_type: Type of material ('lumber' or 'plywood')
            quantity: Quantity needed
            unit: Unit of measurement ('bf' for board feet, 'sqft' for square feet)
            
        Returns:
            Total cost or None if calculation fails
        """
        material = self._materials.get(material_type, {})
        
        if material_type == 'lumber' and unit == 'bf':
            cost_per_unit = material.get('cost_per_bf', 0)
        elif material_type == 'plywood' and unit == 'sqft':
            cost_per_unit = material.get('cost_per_sqft', 0)
        else:
            return None
        
        return quantity * cost_per_unit
    
    def get_fastener_specs(self, fastener_type: str, fastener_subtype: str) -> Dict:
        """
        Get fastener specifications.
        
        Args:
            fastener_type: Type of fastener ('screws' or 'nails')
            fastener_subtype: Subtype (e.g., 'wood_screws', 'deck_screws')
            
        Returns:
            Dictionary of fastener specifications
        """
        fasteners = self._materials.get('fasteners', {})
        fastener_group = fasteners.get(fastener_type, {})
        return fastener_group.get(fastener_subtype, {}).copy()
    
    def add_custom_lumber_size(self, name: str, width: float):
        """
        Add a custom lumber size.
        
        Args:
            name: Display name for the lumber size
            width: Actual width in inches
        """
        if 'lumber' not in self._materials:
            self._materials['lumber'] = {}
        if 'standard_sizes' not in self._materials['lumber']:
            self._materials['lumber']['standard_sizes'] = {}
        
        self._materials['lumber']['standard_sizes'][name] = width
    
    def remove_lumber_size(self, name: str) -> bool:
        """
        Remove a lumber size.
        
        Args:
            name: Display name of the lumber size to remove
            
        Returns:
            True if removed, False if not found
        """
        lumber = self._materials.get('lumber', {})
        sizes = lumber.get('standard_sizes', {})
        
        if name in sizes:
            del sizes[name]
            return True
        
        return False
    
    def update_material_property(
        self, 
        material_type: str, 
        property_name: str, 
        value: Any
    ):
        """
        Update a material property.
        
        Args:
            material_type: Type of material
            property_name: Name of the property
            value: New value
        """
        if material_type not in self._materials:
            self._materials[material_type] = {}
        if 'properties' not in self._materials[material_type]:
            self._materials[material_type]['properties'] = {}
        
        self._materials[material_type]['properties'][property_name] = value
    
    def load_from_file(self, filepath: str):
        """
        Load material configuration from file.
        
        Args:
            filepath: Path to configuration file
        """
        try:
            with open(filepath, 'r') as f:
                loaded_materials = json.load(f)
            
            # Merge with existing materials
            self._merge_materials(self._materials, loaded_materials)
            
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to load materials config: {str(e)}")
    
    def save_to_file(self, filepath: str):
        """
        Save material configuration to file.
        
        Args:
            filepath: Path to save configuration
        """
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(self._materials, f, indent=2, sort_keys=True)
                
        except IOError as e:
            raise ConfigurationError(f"Failed to save materials config: {str(e)}")
    
    def _merge_materials(self, base: Dict, new: Dict):
        """Recursively merge material configurations."""
        for key, value in new.items():
            if key in base and isinstance(value, dict) and isinstance(base[key], dict):
                self._merge_materials(base[key], value)
            else:
                base[key] = value
    
    def validate_configuration(self) -> List[str]:
        """
        Validate material configuration.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate lumber properties
        lumber = self._materials.get('lumber', {})
        if 'standard_sizes' not in lumber:
            errors.append("Lumber standard sizes not defined")
        else:
            sizes = lumber['standard_sizes']
            for name, width in sizes.items():
                if not isinstance(width, (int, float)) or width <= 0:
                    errors.append(f"Invalid lumber width for {name}: {width}")
        
        # Validate plywood properties
        plywood = self._materials.get('plywood', {})
        if 'standard_sizes' not in plywood:
            errors.append("Plywood standard sizes not defined")
        
        # Validate densities
        for material_type in ['lumber', 'plywood']:
            density = self.get_material_density(material_type)
            if density is None or density <= 0:
                errors.append(f"Invalid density for {material_type}")
        
        return errors
    
    def reset_to_defaults(self):
        """Reset all material properties to defaults."""
        self._load_defaults()
    
    def export_materials(self, filepath: str):
        """Export materials configuration to file."""
        self.save_to_file(filepath)
    
    def get_all_materials(self) -> Dict[str, Any]:
        """Get complete materials configuration."""
        return self._materials.copy()