#!/usr/bin/env python3
"""
AutoCrate Development Interface - Streamlit Version

Fast development interface using Streamlit for instant testing and iteration.
Provides the same functionality as the tkinter GUI but with hot reload and web-based UI.
"""

import streamlit as st
import pandas as pd
import json
import io
import time
from pathlib import Path
from typing import Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import AutoCrate modules
try:
    from autocrate.nx_expressions_generator import *
    from security import initialize_security, SecurityLevel
except ImportError as e:
    st.error(f"Failed to import AutoCrate modules: {e}")
    st.info("Make sure you're running from the project root directory")
    st.stop()

# Configure Streamlit
st.set_page_config(
    page_title="AutoCrate Development Interface",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional modern appearance
st.markdown("""
<style>
/* Professional color scheme */
:root {
    --primary-color: #1a237e;
    --secondary-color: #3949ab;
    --accent-color: #5c6bc0;
    --success-color: #00695c;
    --error-color: #b71c1c;
    --background-light: #f5f5f5;
    --background-card: #ffffff;
    --text-primary: #212121;
    --text-secondary: #616161;
    --border-color: #e0e0e0;
}

/* Make app responsive to screen resolution */
.stApp {
    max-width: 100%;
}

/* Professional header */
.main-header {
    background: var(--primary-color);
    color: white;
    padding: 2rem 1rem;
    margin: -1rem -1rem 2rem -1rem;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.main-header h1 {
    font-size: 2.5rem;
    font-weight: 300;
    margin: 0;
    letter-spacing: 1px;
}

.main-header p {
    font-size: 1rem;
    opacity: 0.9;
    margin-top: 0.5rem;
}

/* Clean metric cards */
.metric-card {
    background: var(--background-card);
    padding: 1.5rem;
    border-radius: 4px;
    border: 1px solid var(--border-color);
    margin: 0.5rem 0;
    color: var(--text-primary);
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: box-shadow 0.3s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.metric-card h4 {
    color: var(--primary-color);
    font-weight: 500;
    margin-bottom: 1rem;
}

/* Status boxes */
.success-box {
    background: #e8f5e9;
    border-left: 4px solid var(--success-color);
    color: var(--success-color);
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}

.error-box {
    background: #ffebee;
    border-left: 4px solid var(--error-color);
    color: var(--error-color);
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}

/* Streamlit component overrides for consistency */
.stButton > button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: var(--secondary-color);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.stButton > button[kind="primary"] {
    background-color: var(--accent-color);
}

/* Input fields styling */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 0.5rem;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: var(--background-light);
}

/* Dataframe styling */
.dataframe {
    border: 1px solid var(--border-color) !important;
    border-radius: 4px;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--background-light);
    border-radius: 4px;
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary);
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

/* Metric component styling */
div[data-testid="metric-container"] {
    background-color: var(--background-card);
    border: 1px solid var(--border-color);
    padding: 1rem;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


class StreamlitDevInterface:
    """Streamlit-based development interface for AutoCrate."""
    
    def __init__(self):
        self.session_state = st.session_state
        if 'calculation_results' not in self.session_state:
            self.session_state.calculation_results = None
        if 'last_inputs' not in self.session_state:
            self.session_state.last_inputs = {}
    
    def render_header(self):
        """Render the application header."""
        st.markdown("""
        <div class="main-header">
            <h1>AutoCrate Professional</h1>
            <p>Advanced Shipping Crate Design System</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render sidebar with input controls."""
        st.sidebar.header("Design Parameters")
        
        # Professional status indicator
        with st.sidebar.container():
            st.markdown("""
            <div style="background: #e3f2fd; padding: 0.5rem; border-radius: 4px; margin-bottom: 1rem;">
                <small style="color: #1565c0;">Real-time Calculation Engine</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Product specifications
        st.sidebar.subheader("Product Specifications")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            length = st.number_input("Length (in)", min_value=1.0, max_value=1000.0, value=36.0, step=0.5)
            width = st.number_input("Width (in)", min_value=1.0, max_value=1000.0, value=24.0, step=0.5)
        
        with col2:
            height = st.number_input("Height (in)", min_value=1.0, max_value=1000.0, value=48.0, step=0.5)
            weight = st.number_input("Weight (lbs)", min_value=1.0, max_value=100000.0, value=2500.0, step=10.0)
        
        # Material specifications
        st.sidebar.subheader("Material Specifications")
        
        material_type = st.sidebar.selectbox(
            "Material Type",
            ["Plywood", "OSB", "Solid Wood"],
            index=0
        )
        
        panel_thickness = st.sidebar.select_slider(
            "Panel Thickness (in)",
            options=[0.375, 0.5, 0.625, 0.75, 1.0],
            value=0.75,
            format_func=lambda x: f"{x}\" ({x*25.4:.1f}mm)"
        )
        
        cleat_size = st.sidebar.selectbox(
            "Cleat Size",
            ["2x2", "2x3", "2x4", "3x3", "3x4", "4x4"],
            index=3  # 3x3 default
        )
        
        # Clearance specifications
        st.sidebar.subheader("Clearances")
        
        clearance_all = st.sidebar.number_input(
            "All Sides Clearance (in)", 
            min_value=0.0, max_value=100.0, value=2.0, step=0.25
        )
        
        use_individual = st.sidebar.checkbox("Use Individual Clearances")
        
        if use_individual:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                clearance_length = st.number_input("Length Clearance", value=clearance_all, step=0.25)
                clearance_width = st.number_input("Width Clearance", value=clearance_all, step=0.25)
            with col2:
                clearance_height = st.number_input("Height Clearance", value=clearance_all, step=0.25)
        else:
            clearance_length = clearance_width = clearance_height = clearance_all
        
        # Advanced options
        with st.sidebar.expander("Advanced Options"):
            enable_optimization = st.checkbox("Enable Material Optimization", value=True)
            astm_compliance = st.checkbox("ASTM Compliance Validation", value=True)
            generate_reports = st.checkbox("Generate Detailed Reports", value=False)
            safety_factor = st.slider("Safety Factor", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
        
        # Output options
        st.sidebar.subheader("Output Options")
        output_filename = st.sidebar.text_input(
            "Output Filename", 
            value=f"Crate_{int(length)}x{int(width)}x{int(height)}",
            help="Filename for the .exp file (extension added automatically)"
        )
        
        return {
            'length': length,
            'width': width, 
            'height': height,
            'weight': weight,
            'material_type': material_type,
            'panel_thickness': panel_thickness,
            'cleat_size': cleat_size,
            'clearance_length': clearance_length,
            'clearance_width': clearance_width,
            'clearance_height': clearance_height,
            'enable_optimization': enable_optimization,
            'astm_compliance': astm_compliance,
            'generate_reports': generate_reports,
            'safety_factor': safety_factor,
            'output_filename': output_filename
        }
    
    def render_main_content(self, inputs: Dict[str, Any]):
        """Render main content area."""
        # Quick action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            calculate_btn = st.button("Calculate Design", type="primary", use_container_width=True)
        
        with col2:
            if st.button(" Generate Report", use_container_width=True):
                self.generate_detailed_report(inputs)
        
        with col3:
            if st.button(" Show 3D Preview", use_container_width=True):
                self.show_3d_preview(inputs)
        
        with col4:
            if st.button(" Reset to Defaults", use_container_width=True):
                st.rerun()
        
        # Auto-calculate on input change (with debouncing)
        input_changed = self.session_state.last_inputs != inputs
        if input_changed or calculate_btn:
            self.session_state.last_inputs = inputs.copy()
            
            with st.spinner(" Calculating crate design..."):
                results = self.calculate_crate_design(inputs)
                self.session_state.calculation_results = results
        
        # Display results if available
        if self.session_state.calculation_results:
            self.display_results(self.session_state.calculation_results, inputs)
    
    def generate_detailed_bom(self, results: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed Bill of Materials with individual components grouped by length."""
        bom = {
            'plywood': [],
            'cleats': {},
            'floorboards': [],
            'skids': [],
            'hardware': []
        }
        
        # Plywood sheets (4'x8' standard)
        plywood_count = results['material_summary']['plywood_sheets']
        bom['plywood'].append({
            'description': 'Plywood Sheet',
            'size': '4\' x 8\' x ' + str(inputs['panel_thickness']) + '"',
            'quantity': plywood_count,
            'unit': 'sheets'
        })
        
        # Cleats by length
        cleat_size = inputs['cleat_size']
        
        # Edge cleats for each panel
        panels = results['panel_details']
        
        # Front/Back panels - horizontal cleats
        fb_horiz_length = panels['front_panel']['width']
        fb_horiz_count = 4  # 2 per panel (top/bottom)
        
        # Front/Back panels - vertical cleats  
        fb_vert_length = panels['front_panel']['height'] - (2 * 3.5)  # Minus horizontal cleat widths
        fb_vert_count = 4  # 2 per panel (left/right)
        
        # Left/Right panels - horizontal cleats
        lr_horiz_length = panels['left_panel']['width']
        lr_horiz_count = 4  # 2 per panel
        
        # Left/Right panels - vertical cleats
        lr_vert_length = panels['left_panel']['height'] - (2 * 3.5)
        lr_vert_count = 4  # 2 per panel
        
        # Top panel cleats
        top_primary_length = panels['top_panel']['width']
        top_primary_count = 2
        top_secondary_length = panels['top_panel']['height'] - (2 * 3.5)
        top_secondary_count = 2
        
        # Group cleats by length
        cleat_lengths = {}
        
        # Add front/back horizontal cleats
        if fb_horiz_length > 0:
            key = f"{fb_horiz_length:.1f}"
            if key not in cleat_lengths:
                cleat_lengths[key] = 0
            cleat_lengths[key] += fb_horiz_count
            
        # Add front/back vertical cleats
        if fb_vert_length > 0:
            key = f"{fb_vert_length:.1f}"
            if key not in cleat_lengths:
                cleat_lengths[key] = 0
            cleat_lengths[key] += fb_vert_count
            
        # Add left/right horizontal cleats
        if lr_horiz_length > 0:
            key = f"{lr_horiz_length:.1f}"
            if key not in cleat_lengths:
                cleat_lengths[key] = 0
            cleat_lengths[key] += lr_horiz_count
            
        # Add left/right vertical cleats
        if lr_vert_length > 0:
            key = f"{lr_vert_length:.1f}"
            if key not in cleat_lengths:
                cleat_lengths[key] = 0
            cleat_lengths[key] += lr_vert_count
            
        # Add top panel cleats
        if top_primary_length > 0:
            key = f"{top_primary_length:.1f}"
            if key not in cleat_lengths:
                cleat_lengths[key] = 0
            cleat_lengths[key] += top_primary_count
            
        if top_secondary_length > 0:
            key = f"{top_secondary_length:.1f}"
            if key not in cleat_lengths:
                cleat_lengths[key] = 0
            cleat_lengths[key] += top_secondary_count
        
        # Convert to BOM format
        for length_str, count in sorted(cleat_lengths.items(), key=lambda x: float(x[0]), reverse=True):
            bom['cleats'][length_str] = {
                'description': f'Cleat {cleat_size}',
                'length': float(length_str),
                'quantity': count,
                'unit': 'pieces'
            }
        
        # Floorboards
        floorboard_count = 8  # Example count
        bom['floorboards'].append({
            'description': 'Floorboard 2x12',
            'length': inputs['width'] + 4,  # Approximate
            'quantity': floorboard_count,
            'unit': 'pieces'
        })
        
        # Skids
        skid_info = results['skid_details']
        bom['skids'].append({
            'description': f'Skid {skid_info["lumber_size"]}',
            'length': results['overall_dimensions']['length'],
            'quantity': skid_info['skid_count'],
            'unit': 'pieces'
        })
        
        # Hardware estimate
        bom['hardware'].append({
            'description': 'Wood Screws #10 x 2.5"',
            'quantity': 200,
            'unit': 'pieces (est)'
        })
        bom['hardware'].append({
            'description': 'Wood Screws #10 x 3.5"',
            'quantity': 100,
            'unit': 'pieces (est)'
        })
        
        return bom
    
    def calculate_crate_design(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate crate design using AutoCrate logic."""
        try:
            start_time = time.time()
            
            # Mock calculation for development (replace with actual AutoCrate logic)
            results = {
                'success': True,
                'calculation_time': 0,
                'overall_dimensions': {
                    'length': inputs['length'] + 2 * inputs['clearance_length'] + 2 * inputs['panel_thickness'],
                    'width': inputs['width'] + 2 * inputs['clearance_width'] + 2 * inputs['panel_thickness'],
                    'height': inputs['height'] + inputs['clearance_height'] + inputs['panel_thickness']
                },
                'material_summary': {
                    'plywood_sheets': 8,
                    'linear_feet_cleats': 145.2,
                    'total_weight': inputs['weight'] + 125,  # Crate weight
                    'estimated_cost': 285.50
                },
                'panel_details': {
                    'front_panel': {'width': inputs['length'] + 4, 'height': inputs['height'] + 2, 'cleats': 4},
                    'back_panel': {'width': inputs['length'] + 4, 'height': inputs['height'] + 2, 'cleats': 4},
                    'left_panel': {'width': inputs['width'], 'height': inputs['height'] + 2, 'cleats': 3},
                    'right_panel': {'width': inputs['width'], 'height': inputs['height'] + 2, 'cleats': 3},
                    'top_panel': {'width': inputs['length'] + 4, 'height': inputs['width'], 'cleats': 6}
                },
                'skid_details': {
                    'lumber_size': self.determine_skid_size(inputs['weight']),
                    'skid_count': max(3, int(inputs['length'] / 24) + 1),
                    'spacing': min(22, inputs['length'] / 3)
                },
                'compliance': {
                    'astm_compliant': inputs['astm_compliance'],
                    'safety_factor_met': inputs['safety_factor'] >= 1.5,
                    'load_rating': inputs['weight'] * inputs['safety_factor']
                }
            }
            
            results['calculation_time'] = time.time() - start_time
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'calculation_time': time.time() - start_time
            }
    
    def determine_skid_size(self, weight: float) -> str:
        """Determine appropriate skid lumber size based on weight."""
        if weight <= 500:
            return "3x4"
        elif weight <= 2000:
            return "4x4"
        elif weight <= 5000:
            return "4x6"
        else:
            return "6x6"
    
    def display_results(self, results: Dict[str, Any], inputs: Dict[str, Any]):
        """Display calculation results."""
        if not results['success']:
            st.markdown(f"""
            <div class="error-box">
                <h3> Calculation Error</h3>
                <p>{results.get('error', 'Unknown error occurred')}</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Success message with timing
        st.markdown(f"""
        <div class="success-box">
            <h3> Design Calculated Successfully</h3>
            <p>Calculation completed in {results['calculation_time']:.3f} seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics
        st.subheader(" Overall Dimensions")
        
        col1, col2, col3, col4 = st.columns(4)
        dims = results['overall_dimensions']
        
        with col1:
            st.metric("Length", f"{dims['length']:.1f} in", f"+{dims['length'] - inputs['length']:.1f}")
        with col2:
            st.metric("Width", f"{dims['width']:.1f} in", f"+{dims['width'] - inputs['width']:.1f}")
        with col3:
            st.metric("Height", f"{dims['height']:.1f} in", f"+{dims['height'] - inputs['height']:.1f}")
        with col4:
            volume_cuft = (dims['length'] * dims['width'] * dims['height']) / 1728
            st.metric("Volume", f"{volume_cuft:.1f} ft")
        
        # Material summary
        st.subheader(" Material Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            materials = results['material_summary']
            st.markdown("""
            <div class="metric-card">
                <h4 style="color: #333;"> Material Requirements</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Plywood Sheets (4'x8')", materials['plywood_sheets'])
            st.metric("Cleat Linear Feet", f"{materials['linear_feet_cleats']:.1f} ft")
            st.metric("Total Crate Weight", f"{materials['total_weight']:.0f} lbs")
            st.metric("Estimated Cost", f"${materials['estimated_cost']:.2f}")
        
        with col2:
            # Compliance status
            compliance = results['compliance']
            st.markdown("""
            <div class="metric-card">
                <h4 style="color: #333;"> Compliance Status</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("ASTM Compliant" if compliance['astm_compliant'] else "ASTM Review Required")
            st.info(f"Safety Factor: {inputs['safety_factor']:.1f}x")
            st.info(f"Load Rating: {compliance['load_rating']:.0f} lbs")
        
        # Panel breakdown
        st.subheader(" Panel Breakdown")
        
        panel_data = []
        for panel_name, details in results['panel_details'].items():
            panel_data.append({
                'Panel': panel_name.replace('_', ' ').title(),
                'Width (in)': details['width'],
                'Height (in)': details['height'],
                'Cleats': details['cleats'],
                'Area (sq ft)': round(details['width'] * details['height'] / 144, 1)
            })
        
        df_panels = pd.DataFrame(panel_data)
        st.dataframe(df_panels, use_container_width=True)
        
        # Bill of Materials
        st.subheader(" Bill of Materials (BOM)")
        
        bom = self.generate_detailed_bom(results, inputs)
        
        # Display BOM in organized sections
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Plywood**")
            for item in bom['plywood']:
                st.write(f"• {item['description']} {item['size']}: {item['quantity']} {item['unit']}")
            
            st.markdown("**Skids**")
            for item in bom['skids']:
                st.write(f"• {item['description']} @ {item['length']:.1f}\": {item['quantity']} {item['unit']}")
        
        with col2:
            st.markdown("**Cleats (grouped by length)**")
            for length, item in bom['cleats'].items():
                st.write(f"• {item['description']} @ {item['length']:.1f}\": {item['quantity']} {item['unit']}")
        
        with col3:
            st.markdown("**Floorboards**")
            for item in bom['floorboards']:
                st.write(f"• {item['description']} @ {item['length']:.1f}\": {item['quantity']} {item['unit']}")
            
            st.markdown("**Hardware**")
            for item in bom['hardware']:
                st.write(f"• {item['description']}: {item['quantity']} {item['unit']}")
        
        # Download section
        st.subheader(" Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Generate NX expression file
            exp_content = self.generate_nx_expressions(results, inputs)
            st.download_button(
                " Download .exp File",
                exp_content,
                file_name=f"{inputs['output_filename']}.exp",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # Generate CSV report
            csv_content = self.generate_csv_report(results, inputs)
            st.download_button(
                " Download CSV Report",
                csv_content,
                file_name=f"{inputs['output_filename']}_report.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # Generate JSON data
            json_content = json.dumps({**results, **inputs}, indent=2)
            st.download_button(
                " Download JSON Data",
                json_content,
                file_name=f"{inputs['output_filename']}_data.json",
                mime="application/json",
                use_container_width=True
            )
    
    def generate_nx_expressions(self, results: Dict[str, Any], inputs: Dict[str, Any]) -> str:
        """Generate NX expressions file content."""
        # Mock NX expressions (replace with actual AutoCrate logic)
        exp_content = f"""
# AutoCrate Generated Expressions - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Development Interface Version

# Product Dimensions
Product_Length = {inputs['length']:.3f}
Product_Width = {inputs['width']:.3f}
Product_Height = {inputs['height']:.3f}
Product_Weight = {inputs['weight']:.1f}

# Overall Crate Dimensions
Overall_Length = {results['overall_dimensions']['length']:.3f}
Overall_Width = {results['overall_dimensions']['width']:.3f}
Overall_Height = {results['overall_dimensions']['height']:.3f}

# Material Specifications
Panel_Thickness = {inputs['panel_thickness']:.3f}
Cleat_Size = \"{inputs['cleat_size']}\"

# Clearances
Clearance_Length = {inputs['clearance_length']:.3f}
Clearance_Width = {inputs['clearance_width']:.3f}
Clearance_Height = {inputs['clearance_height']:.3f}

# Panel Dimensions
Front_Panel_Width = {results['panel_details']['front_panel']['width']:.3f}
Front_Panel_Height = {results['panel_details']['front_panel']['height']:.3f}
Back_Panel_Width = {results['panel_details']['back_panel']['width']:.3f}
Back_Panel_Height = {results['panel_details']['back_panel']['height']:.3f}

# Skid Information
Skid_Lumber_Size = \"{results['skid_details']['lumber_size']}\"
Skid_Count = {results['skid_details']['skid_count']}
Skid_Spacing = {results['skid_details']['spacing']:.3f}

# Compliance Information
ASTM_Compliant = {1 if results['compliance']['astm_compliant'] else 0}
Safety_Factor = {inputs['safety_factor']:.2f}
Load_Rating = {results['compliance']['load_rating']:.1f}

# Material Summary
Plywood_Sheets_Required = {results['material_summary']['plywood_sheets']}
Cleat_Linear_Feet = {results['material_summary']['linear_feet_cleats']:.2f}
Total_Crate_Weight = {results['material_summary']['total_weight']:.1f}
Estimated_Cost = {results['material_summary']['estimated_cost']:.2f}
"""
        return exp_content
    
    def generate_csv_report(self, results: Dict[str, Any], inputs: Dict[str, Any]) -> str:
        """Generate CSV report content."""
        # Create comprehensive CSV report
        report_data = []
        
        # Add input parameters
        report_data.extend([
            ['Parameter', 'Value', 'Unit'],
            ['Product Length', inputs['length'], 'inches'],
            ['Product Width', inputs['width'], 'inches'],
            ['Product Height', inputs['height'], 'inches'],
            ['Product Weight', inputs['weight'], 'pounds'],
            ['Panel Thickness', inputs['panel_thickness'], 'inches'],
            ['Cleat Size', inputs['cleat_size'], ''],
            ['', '', ''],  # Separator
            ['Results', '', ''],
            ['Overall Length', results['overall_dimensions']['length'], 'inches'],
            ['Overall Width', results['overall_dimensions']['width'], 'inches'],
            ['Overall Height', results['overall_dimensions']['height'], 'inches'],
            ['Plywood Sheets', results['material_summary']['plywood_sheets'], 'sheets'],
            ['Cleat Linear Feet', results['material_summary']['linear_feet_cleats'], 'feet'],
            ['Total Weight', results['material_summary']['total_weight'], 'pounds'],
            ['Estimated Cost', results['material_summary']['estimated_cost'], 'dollars'],
            ['', '', ''],  # Separator
            ['Bill of Materials', '', '']
        ])
        
        # Add BOM details
        bom = self.generate_detailed_bom(results, inputs)
        
        # Plywood
        report_data.append(['Plywood', '', ''])
        for item in bom['plywood']:
            report_data.append(['', f"{item['description']} {item['size']}", f"{item['quantity']} {item['unit']}"])
        
        # Cleats
        report_data.append(['', '', ''])
        report_data.append(['Cleats (by length)', '', ''])
        for length, item in sorted(bom['cleats'].items(), key=lambda x: float(x[0]), reverse=True):
            report_data.append(['', f"{item['description']} @ {item['length']:.1f}\"", f"{item['quantity']} {item['unit']}"])
        
        # Floorboards
        report_data.append(['', '', ''])
        report_data.append(['Floorboards', '', ''])
        for item in bom['floorboards']:
            report_data.append(['', f"{item['description']} @ {item['length']:.1f}\"", f"{item['quantity']} {item['unit']}"])
        
        # Skids
        report_data.append(['', '', ''])
        report_data.append(['Skids', '', ''])
        for item in bom['skids']:
            report_data.append(['', f"{item['description']} @ {item['length']:.1f}\"", f"{item['quantity']} {item['unit']}"])
        
        # Hardware
        report_data.append(['', '', ''])
        report_data.append(['Hardware', '', ''])
        for item in bom['hardware']:
            report_data.append(['', item['description'], f"{item['quantity']} {item['unit']}"])
        
        # Convert to CSV string
        csv_output = io.StringIO()
        for row in report_data:
            csv_output.write(','.join(map(str, row)) + '\n')
        
        return csv_output.getvalue()
    
    def show_3d_preview(self, inputs: Dict[str, Any]):
        """Show 3D preview of the crate design."""
        st.subheader(" 3D Crate Preview")
        
        if self.session_state.calculation_results:
            results = self.session_state.calculation_results
            dims = results['overall_dimensions']
            
            # Create 3D wireframe
            fig = go.Figure()
            
            # Crate outline
            x = [0, dims['length'], dims['length'], 0, 0]
            y = [0, 0, dims['width'], dims['width'], 0]
            z_bottom = [0, 0, 0, 0, 0]
            z_top = [dims['height']] * 5
            
            # Bottom rectangle
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z_bottom,
                mode='lines',
                name='Bottom',
                line=dict(color='blue', width=4)
            ))
            
            # Top rectangle
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z_top,
                mode='lines',
                name='Top',
                line=dict(color='red', width=4)
            ))
            
            # Vertical edges
            for i in range(4):
                fig.add_trace(go.Scatter3d(
                    x=[x[i], x[i]], y=[y[i], y[i]], z=[0, dims['height']],
                    mode='lines',
                    showlegend=False,
                    line=dict(color='green', width=2)
                ))
            
            # Product outline (inside crate)
            prod_x_offset = inputs['clearance_length'] + inputs['panel_thickness']
            prod_y_offset = inputs['clearance_width'] + inputs['panel_thickness']
            prod_z_offset = inputs['panel_thickness']
            
            px = [prod_x_offset, prod_x_offset + inputs['length'], 
                  prod_x_offset + inputs['length'], prod_x_offset, prod_x_offset]
            py = [prod_y_offset, prod_y_offset, prod_y_offset + inputs['width'], 
                  prod_y_offset + inputs['width'], prod_y_offset]
            pz_bottom = [prod_z_offset] * 5
            pz_top = [prod_z_offset + inputs['height']] * 5
            
            fig.add_trace(go.Scatter3d(
                x=px, y=py, z=pz_bottom,
                mode='lines',
                name='Product Bottom',
                line=dict(color='orange', width=3, dash='dash')
            ))
            
            fig.add_trace(go.Scatter3d(
                x=px, y=py, z=pz_top,
                mode='lines',
                name='Product Top',
                line=dict(color='orange', width=3, dash='dash')
            ))
            
            fig.update_layout(
                title="3D Crate Design Preview",
                scene=dict(
                    xaxis_title="Length (inches)",
                    yaxis_title="Width (inches)",
                    zaxis_title="Height (inches)",
                    aspectmode='data',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                height=800,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please calculate the design first to see the 3D preview.")
    
    def generate_detailed_report(self, inputs: Dict[str, Any]):
        """Generate detailed engineering report."""
        st.subheader(" Detailed Engineering Report")
        
        if self.session_state.calculation_results:
            results = self.session_state.calculation_results
            
            # Report sections
            tab1, tab2, tab3, tab4 = st.tabs(["Design Summary", "Material Details", "Compliance", "Cost Analysis"])
            
            with tab1:
                st.markdown("### Design Summary")
                st.write(f"**Project:** {inputs['output_filename']}")
                st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Calculation Time:** {results['calculation_time']:.3f} seconds")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Product Specifications:**")
                    st.write(f"- Dimensions: {inputs['length']}\" x {inputs['width']}\" x {inputs['height']}\"")
                    st.write(f"- Weight: {inputs['weight']:,.0f} lbs")
                    st.write(f"- Material: {inputs['material_type']}")
                
                with col2:
                    st.markdown("**Crate Specifications:**")
                    dims = results['overall_dimensions']
                    st.write(f"- Overall: {dims['length']:.1f}\" x {dims['width']:.1f}\" x {dims['height']:.1f}\"")
                    st.write(f"- Panel Thickness: {inputs['panel_thickness']}\"")
                    st.write(f"- Cleat Size: {inputs['cleat_size']}")
            
            with tab2:
                st.markdown("### Material Details")
                materials = results['material_summary']
                
                # Material breakdown chart
                fig = px.pie(
                    values=[materials['plywood_sheets'] * 32, materials['linear_feet_cleats'] * 2.5, 50],
                    names=['Plywood (sq ft)', 'Cleats (board ft)', 'Hardware (est)'],
                    title="Material Distribution by Board Feet"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed material list
                material_df = pd.DataFrame([
                    {'Item': 'Plywood Sheets (4\'x8\')', 'Quantity': materials['plywood_sheets'], 'Unit': 'sheets'},
                    {'Item': 'Cleat Lumber', 'Quantity': materials['linear_feet_cleats'], 'Unit': 'linear ft'},
                    {'Item': 'Screws/Hardware', 'Quantity': 'Est. 200-300', 'Unit': 'pieces'},
                    {'Item': 'Total Weight', 'Quantity': materials['total_weight'], 'Unit': 'lbs'}
                ])
                st.dataframe(material_df, use_container_width=True)
            
            with tab3:
                st.markdown("### Compliance & Engineering")
                compliance = results['compliance']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Structural Compliance:**")
                    st.success(" ASTM Standards Met" if compliance['astm_compliant'] else " Review Required")
                    st.info(f"Safety Factor: {inputs['safety_factor']:.1f}x")
                    st.info(f"Load Rating: {compliance['load_rating']:,.0f} lbs")
                
                with col2:
                    st.markdown("**Design Validation:**")
                    st.write(f"- Skid Lumber: {results['skid_details']['lumber_size']}")
                    st.write(f"- Skid Count: {results['skid_details']['skid_count']}")
                    st.write(f"- Max Spacing: {results['skid_details']['spacing']:.1f}\"")
            
            with tab4:
                st.markdown("### Cost Analysis")
                cost = materials['estimated_cost']
                
                # Cost breakdown
                cost_breakdown = {
                    'Plywood': cost * 0.65,
                    'Lumber': cost * 0.25,
                    'Hardware': cost * 0.10
                }
                
                fig = px.bar(
                    x=list(cost_breakdown.keys()),
                    y=list(cost_breakdown.values()),
                    title="Cost Breakdown",
                    labels={'y': 'Cost ($)', 'x': 'Category'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.metric("Total Estimated Cost", f"${cost:.2f}")
                st.metric("Cost per Cubic Foot", f"${cost / ((dims['length'] * dims['width'] * dims['height']) / 1728):.2f}")
        else:
            st.info("Please calculate the design first to generate a detailed report.")
    
    def run(self):
        """Run the Streamlit development interface."""
        self.render_header()
        
        # Get inputs from sidebar
        inputs = self.render_sidebar()
        
        # Render main content
        self.render_main_content(inputs)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem 1rem;">
            <p style="margin: 0;">AutoCrate Professional Edition v12.0.2</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">ASTM Compliant | Engineering-Grade Design System</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main entry point for the development interface."""
    try:
        # Initialize development interface
        dev_interface = StreamlitDevInterface()
        dev_interface.run()
        
    except Exception as e:
        st.error(f"Application Error: {e}")
        st.info("Please check the console for detailed error information.")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
