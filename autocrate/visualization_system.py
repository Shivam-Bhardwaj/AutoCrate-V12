#!/usr/bin/env python3
"""
AutoCrate V12 - Comprehensive Visualization System
Provides 3D visualization, interactive models, and visual analytics for crate designs.

This module implements:
- Interactive 3D crate model with component visualization
- Exploded view capability for assembly understanding
- Dimension annotations and measurement tools
- Material highlighting and selection
- Assembly sequence animation
- Cross-platform support (tkinter and web)
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import base64
from io import BytesIO


class ViewMode(Enum):
    """Visualization view modes."""
    ASSEMBLED = "assembled"
    EXPLODED = "exploded"
    WIREFRAME = "wireframe"
    TRANSPARENT = "transparent"
    CUTAWAY = "cutaway"


class ComponentType(Enum):
    """Crate component types for visualization."""
    FRONT_PANEL = "front_panel"
    BACK_PANEL = "back_panel"
    LEFT_PANEL = "left_panel"
    RIGHT_PANEL = "right_panel"
    TOP_PANEL = "top_panel"
    BOTTOM_PANEL = "bottom_panel"
    SKID = "skid"
    CLEAT = "cleat"
    FLOORBOARD = "floorboard"
    KLIMP = "klimp"


@dataclass
class Component3D:
    """Represents a 3D component of the crate."""
    name: str
    component_type: ComponentType
    vertices: np.ndarray
    faces: List[List[int]]
    color: str = "#8B7355"  # Wood brown default
    opacity: float = 1.0
    material: str = "plywood"
    thickness: float = 0.75  # inches
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_center(self) -> np.ndarray:
        """Calculate the center point of the component."""
        return np.mean(self.vertices, axis=0)
    
    def translate(self, offset: np.ndarray):
        """Translate the component by the given offset."""
        self.vertices += offset
    
    def rotate(self, angle: float, axis: str = 'z'):
        """Rotate the component around the specified axis."""
        rad = np.radians(angle)
        if axis == 'x':
            rotation_matrix = np.array([
                [1, 0, 0],
                [0, np.cos(rad), -np.sin(rad)],
                [0, np.sin(rad), np.cos(rad)]
            ])
        elif axis == 'y':
            rotation_matrix = np.array([
                [np.cos(rad), 0, np.sin(rad)],
                [0, 1, 0],
                [-np.sin(rad), 0, np.cos(rad)]
            ])
        else:  # z-axis
            rotation_matrix = np.array([
                [np.cos(rad), -np.sin(rad), 0],
                [np.sin(rad), np.cos(rad), 0],
                [0, 0, 1]
            ])
        
        center = self.get_center()
        self.vertices = (self.vertices - center) @ rotation_matrix + center


@dataclass
class CrateModel3D:
    """3D model representation of a complete crate."""
    length: float  # inches
    width: float   # inches
    height: float  # inches
    components: List[Component3D] = field(default_factory=list)
    assembly_sequence: List[str] = field(default_factory=list)
    
    def add_component(self, component: Component3D):
        """Add a component to the crate model."""
        self.components.append(component)
        self.assembly_sequence.append(component.name)
    
    def get_bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get the bounding box of the entire crate."""
        all_vertices = np.vstack([comp.vertices for comp in self.components])
        return np.min(all_vertices, axis=0), np.max(all_vertices, axis=0)
    
    def explode(self, factor: float = 1.5):
        """Create an exploded view of the crate."""
        center = np.array([self.length/2, self.width/2, self.height/2])
        
        for component in self.components:
            comp_center = component.get_center()
            direction = comp_center - center
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
                component.translate(direction * factor * 10)  # 10 inches base explosion


class CrateVisualizer:
    """Main visualization engine for AutoCrate."""
    
    def __init__(self, platform: str = "tkinter"):
        """
        Initialize the visualizer.
        
        Args:
            platform: Target platform ('tkinter' or 'web')
        """
        self.platform = platform
        self.current_model: Optional[CrateModel3D] = None
        self.view_mode = ViewMode.ASSEMBLED
        self.selected_component: Optional[Component3D] = None
        self.show_dimensions = True
        self.show_annotations = True
        self.animation_speed = 1.0
        
    def create_crate_model(self, crate_data: Dict[str, Any]) -> CrateModel3D:
        """
        Create a 3D model from crate calculation data.
        
        Args:
            crate_data: Dictionary containing crate dimensions and component data
            
        Returns:
            CrateModel3D object
        """
        length = crate_data.get('length', 48)
        width = crate_data.get('width', 40)
        height = crate_data.get('height', 36)
        
        model = CrateModel3D(length=length, width=width, height=height)
        
        # Create panels
        self._add_panels(model, crate_data)
        
        # Create cleats
        self._add_cleats(model, crate_data)
        
        # Create skids
        self._add_skids(model, crate_data)
        
        # Create floorboards
        self._add_floorboards(model, crate_data)
        
        self.current_model = model
        return model
    
    def _add_panels(self, model: CrateModel3D, crate_data: Dict):
        """Add panel components to the model."""
        plywood_thickness = crate_data.get('plywood_thickness', 0.75)
        
        # Front panel
        front_vertices = np.array([
            [0, 0, 0],
            [model.length, 0, 0],
            [model.length, 0, model.height],
            [0, 0, model.height],
            [0, plywood_thickness, 0],
            [model.length, plywood_thickness, 0],
            [model.length, plywood_thickness, model.height],
            [0, plywood_thickness, model.height]
        ])
        
        front_faces = [
            [0, 1, 2, 3],  # Front face
            [4, 7, 6, 5],  # Back face
            [0, 4, 5, 1],  # Bottom face
            [3, 2, 6, 7],  # Top face
            [0, 3, 7, 4],  # Left face
            [1, 5, 6, 2]   # Right face
        ]
        
        front_panel = Component3D(
            name="Front Panel",
            component_type=ComponentType.FRONT_PANEL,
            vertices=front_vertices,
            faces=front_faces,
            color="#8B7355",
            material="plywood",
            thickness=plywood_thickness
        )
        model.add_component(front_panel)
        
        # Back panel
        back_vertices = front_vertices.copy()
        back_vertices[:, 1] = model.width - plywood_thickness + back_vertices[:, 1]
        
        back_panel = Component3D(
            name="Back Panel",
            component_type=ComponentType.BACK_PANEL,
            vertices=back_vertices,
            faces=front_faces,
            color="#8B7355",
            material="plywood",
            thickness=plywood_thickness
        )
        model.add_component(back_panel)
        
        # Left panel
        left_vertices = np.array([
            [0, 0, 0],
            [0, model.width, 0],
            [0, model.width, model.height],
            [0, 0, model.height],
            [plywood_thickness, 0, 0],
            [plywood_thickness, model.width, 0],
            [plywood_thickness, model.width, model.height],
            [plywood_thickness, 0, model.height]
        ])
        
        left_panel = Component3D(
            name="Left Panel",
            component_type=ComponentType.LEFT_PANEL,
            vertices=left_vertices,
            faces=front_faces,
            color="#8B7355",
            material="plywood",
            thickness=plywood_thickness
        )
        model.add_component(left_panel)
        
        # Right panel
        right_vertices = left_vertices.copy()
        right_vertices[:, 0] = model.length - plywood_thickness + right_vertices[:, 0]
        
        right_panel = Component3D(
            name="Right Panel",
            component_type=ComponentType.RIGHT_PANEL,
            vertices=right_vertices,
            faces=front_faces,
            color="#8B7355",
            material="plywood",
            thickness=plywood_thickness
        )
        model.add_component(right_panel)
        
        # Top panel
        top_vertices = np.array([
            [0, 0, model.height - plywood_thickness],
            [model.length, 0, model.height - plywood_thickness],
            [model.length, model.width, model.height - plywood_thickness],
            [0, model.width, model.height - plywood_thickness],
            [0, 0, model.height],
            [model.length, 0, model.height],
            [model.length, model.width, model.height],
            [0, model.width, model.height]
        ])
        
        top_panel = Component3D(
            name="Top Panel",
            component_type=ComponentType.TOP_PANEL,
            vertices=top_vertices,
            faces=front_faces,
            color="#8B7355",
            material="plywood",
            thickness=plywood_thickness
        )
        model.add_component(top_panel)
    
    def _add_cleats(self, model: CrateModel3D, crate_data: Dict):
        """Add cleat components to the model."""
        cleat_width = crate_data.get('cleat_width', 2.0)
        cleat_height = crate_data.get('cleat_height', 4.0)
        
        # Add corner cleats for each panel
        cleat_positions = [
            (0, 0, 0, "Front-Left Cleat"),
            (model.length - cleat_width, 0, 0, "Front-Right Cleat"),
            (0, model.width - cleat_height, 0, "Back-Left Cleat"),
            (model.length - cleat_width, model.width - cleat_height, 0, "Back-Right Cleat"),
        ]
        
        for x, y, z, name in cleat_positions:
            cleat_vertices = np.array([
                [x, y, z],
                [x + cleat_width, y, z],
                [x + cleat_width, y + cleat_height, z],
                [x, y + cleat_height, z],
                [x, y, z + model.height],
                [x + cleat_width, y, z + model.height],
                [x + cleat_width, y + cleat_height, z + model.height],
                [x, y + cleat_height, z + model.height]
            ])
            
            cleat_faces = [
                [0, 1, 2, 3],
                [4, 7, 6, 5],
                [0, 4, 5, 1],
                [3, 2, 6, 7],
                [0, 3, 7, 4],
                [1, 5, 6, 2]
            ]
            
            cleat = Component3D(
                name=name,
                component_type=ComponentType.CLEAT,
                vertices=cleat_vertices,
                faces=cleat_faces,
                color="#6B5D54",  # Darker wood for cleats
                material="lumber",
                thickness=cleat_width
            )
            model.add_component(cleat)
    
    def _add_skids(self, model: CrateModel3D, crate_data: Dict):
        """Add skid components to the model."""
        skid_width = crate_data.get('skid_width', 4.0)
        skid_height = crate_data.get('skid_height', 4.0)
        num_skids = crate_data.get('num_skids', 3)
        
        skid_spacing = model.length / (num_skids + 1)
        
        for i in range(num_skids):
            x_pos = skid_spacing * (i + 1) - skid_width / 2
            
            skid_vertices = np.array([
                [x_pos, 0, -skid_height],
                [x_pos + skid_width, 0, -skid_height],
                [x_pos + skid_width, model.width, -skid_height],
                [x_pos, model.width, -skid_height],
                [x_pos, 0, 0],
                [x_pos + skid_width, 0, 0],
                [x_pos + skid_width, model.width, 0],
                [x_pos, model.width, 0]
            ])
            
            skid_faces = [
                [0, 1, 2, 3],
                [4, 7, 6, 5],
                [0, 4, 5, 1],
                [3, 2, 6, 7],
                [0, 3, 7, 4],
                [1, 5, 6, 2]
            ]
            
            skid = Component3D(
                name=f"Skid {i+1}",
                component_type=ComponentType.SKID,
                vertices=skid_vertices,
                faces=skid_faces,
                color="#5C4E42",  # Even darker for skids
                material="lumber",
                thickness=skid_width
            )
            model.add_component(skid)
    
    def _add_floorboards(self, model: CrateModel3D, crate_data: Dict):
        """Add floorboard components to the model."""
        board_width = crate_data.get('floorboard_width', 5.5)
        board_thickness = crate_data.get('floorboard_thickness', 0.75)
        num_boards = int(model.width / board_width) + 1
        
        for i in range(num_boards):
            y_pos = i * board_width
            if y_pos + board_width > model.width:
                board_width = model.width - y_pos
            
            board_vertices = np.array([
                [0, y_pos, 0],
                [model.length, y_pos, 0],
                [model.length, y_pos + board_width, 0],
                [0, y_pos + board_width, 0],
                [0, y_pos, board_thickness],
                [model.length, y_pos, board_thickness],
                [model.length, y_pos + board_width, board_thickness],
                [0, y_pos + board_width, board_thickness]
            ])
            
            board_faces = [
                [0, 1, 2, 3],
                [4, 7, 6, 5],
                [0, 4, 5, 1],
                [3, 2, 6, 7],
                [0, 3, 7, 4],
                [1, 5, 6, 2]
            ]
            
            floorboard = Component3D(
                name=f"Floorboard {i+1}",
                component_type=ComponentType.FLOORBOARD,
                vertices=board_vertices,
                faces=board_faces,
                color="#7A6A5A",
                material="lumber",
                thickness=board_thickness
            )
            model.add_component(floorboard)
    
    def render_matplotlib(self, model: Optional[CrateModel3D] = None, 
                         fig_size: Tuple[int, int] = (12, 9)) -> plt.Figure:
        """
        Render the crate model using matplotlib (for tkinter integration).
        
        Args:
            model: CrateModel3D to render (uses current_model if None)
            fig_size: Figure size in inches
            
        Returns:
            Matplotlib figure object
        """
        if model is None:
            model = self.current_model
        
        if model is None:
            raise ValueError("No model to render")
        
        fig = plt.figure(figsize=fig_size)
        ax = fig.add_subplot(111, projection='3d')
        
        # Apply view mode transformations
        if self.view_mode == ViewMode.EXPLODED:
            model.explode(factor=1.5)
        
        # Render each component
        for component in model.components:
            if self.view_mode == ViewMode.WIREFRAME:
                self._render_wireframe_component(ax, component)
            else:
                self._render_solid_component(ax, component)
        
        # Add dimensions if enabled
        if self.show_dimensions:
            self._add_dimension_annotations(ax, model)
        
        # Set labels and title
        ax.set_xlabel('Length (inches)')
        ax.set_ylabel('Width (inches)')
        ax.set_zlabel('Height (inches)')
        ax.set_title('AutoCrate 3D Model Visualization')
        
        # Set equal aspect ratio
        self._set_equal_aspect(ax, model)
        
        return fig
    
    def _render_solid_component(self, ax: Axes3D, component: Component3D):
        """Render a solid component."""
        for face in component.faces:
            vertices = component.vertices[face]
            poly = [[vertices[j] for j in range(len(vertices))]]
            
            alpha = component.opacity
            if self.view_mode == ViewMode.TRANSPARENT:
                alpha = 0.3
            
            ax.add_collection3d(Poly3DCollection(
                poly,
                facecolors=component.color,
                edgecolors='black',
                alpha=alpha,
                linewidths=0.5
            ))
    
    def _render_wireframe_component(self, ax: Axes3D, component: Component3D):
        """Render a wireframe component."""
        for face in component.faces:
            vertices = component.vertices[face]
            for i in range(len(vertices)):
                start = vertices[i]
                end = vertices[(i + 1) % len(vertices)]
                ax.plot3D(*zip(start, end), color='black', linewidth=1)
    
    def _add_dimension_annotations(self, ax: Axes3D, model: CrateModel3D):
        """Add dimension annotations to the visualization."""
        # Length dimension
        ax.text(model.length/2, -5, -10, f"{model.length}\"", 
                fontsize=10, ha='center', color='red')
        
        # Width dimension
        ax.text(-5, model.width/2, -10, f"{model.width}\"", 
                fontsize=10, ha='center', color='green', rotation=90)
        
        # Height dimension
        ax.text(-10, -5, model.height/2, f"{model.height}\"", 
                fontsize=10, ha='center', color='blue')
    
    def _set_equal_aspect(self, ax: Axes3D, model: CrateModel3D):
        """Set equal aspect ratio for 3D plot."""
        min_bound, max_bound = model.get_bounding_box()
        
        max_range = np.array([
            max_bound[0] - min_bound[0],
            max_bound[1] - min_bound[1],
            max_bound[2] - min_bound[2]
        ]).max() / 2.0
        
        mid_x = (max_bound[0] + min_bound[0]) * 0.5
        mid_y = (max_bound[1] + min_bound[1]) * 0.5
        mid_z = (max_bound[2] + min_bound[2]) * 0.5
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    def render_plotly(self, model: Optional[CrateModel3D] = None) -> go.Figure:
        """
        Render the crate model using Plotly (for web/Streamlit).
        
        Args:
            model: CrateModel3D to render (uses current_model if None)
            
        Returns:
            Plotly figure object
        """
        if model is None:
            model = self.current_model
        
        if model is None:
            raise ValueError("No model to render")
        
        # Apply view mode transformations
        if self.view_mode == ViewMode.EXPLODED:
            model.explode(factor=1.5)
        
        traces = []
        
        # Create traces for each component
        for component in model.components:
            if self.view_mode == ViewMode.WIREFRAME:
                trace = self._create_wireframe_trace(component)
            else:
                trace = self._create_mesh_trace(component)
            traces.append(trace)
        
        # Create figure
        fig = go.Figure(data=traces)
        
        # Update layout for better 3D visualization
        fig.update_layout(
            title="AutoCrate 3D Model Visualization",
            scene=dict(
                xaxis_title="Length (inches)",
                yaxis_title="Width (inches)",
                zaxis_title="Height (inches)",
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0)
                )
            ),
            showlegend=True,
            height=800,
            width=1200
        )
        
        # Add dimension annotations if enabled
        if self.show_dimensions:
            self._add_plotly_annotations(fig, model)
        
        return fig
    
    def _create_mesh_trace(self, component: Component3D) -> go.Mesh3d:
        """Create a Plotly mesh trace for a component."""
        vertices = component.vertices
        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
        
        # Flatten faces for Plotly
        i, j, k = [], [], []
        for face in component.faces:
            if len(face) >= 3:
                # Triangulate faces with more than 3 vertices
                for idx in range(1, len(face) - 1):
                    i.append(face[0])
                    j.append(face[idx])
                    k.append(face[idx + 1])
        
        opacity = component.opacity
        if self.view_mode == ViewMode.TRANSPARENT:
            opacity = 0.3
        
        return go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            name=component.name,
            color=component.color,
            opacity=opacity,
            hovertemplate=f"<b>{component.name}</b><br>" +
                         f"Material: {component.material}<br>" +
                         f"Thickness: {component.thickness}\"<br>" +
                         "<extra></extra>"
        )
    
    def _create_wireframe_trace(self, component: Component3D) -> go.Scatter3d:
        """Create a Plotly wireframe trace for a component."""
        x, y, z = [], [], []
        
        for face in component.faces:
            vertices = component.vertices[face]
            for i in range(len(vertices)):
                x.extend([vertices[i][0], vertices[(i+1)%len(vertices)][0], None])
                y.extend([vertices[i][1], vertices[(i+1)%len(vertices)][1], None])
                z.extend([vertices[i][2], vertices[(i+1)%len(vertices)][2], None])
        
        return go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            name=component.name,
            line=dict(color='black', width=2)
        )
    
    def _add_plotly_annotations(self, fig: go.Figure, model: CrateModel3D):
        """Add dimension annotations to Plotly figure."""
        annotations = [
            dict(
                x=model.length/2, y=-10, z=-15,
                text=f"Length: {model.length}\"",
                showarrow=False,
                font=dict(size=12, color="red")
            ),
            dict(
                x=-10, y=model.width/2, z=-15,
                text=f"Width: {model.width}\"",
                showarrow=False,
                font=dict(size=12, color="green")
            ),
            dict(
                x=-15, y=-10, z=model.height/2,
                text=f"Height: {model.height}\"",
                showarrow=False,
                font=dict(size=12, color="blue")
            )
        ]
        
        fig.update_layout(scene_annotations=annotations)
    
    def create_assembly_animation(self, model: CrateModel3D, 
                                 duration: float = 10.0) -> animation.FuncAnimation:
        """
        Create an assembly sequence animation.
        
        Args:
            model: CrateModel3D to animate
            duration: Total animation duration in seconds
            
        Returns:
            Matplotlib animation object
        """
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Calculate frame timing
        num_components = len(model.components)
        frames_per_component = int(30 * duration / num_components)  # 30 fps
        total_frames = frames_per_component * num_components
        
        def update_frame(frame_num):
            ax.clear()
            
            # Determine which components to show
            components_to_show = min(
                frame_num // frames_per_component + 1,
                num_components
            )
            
            # Render visible components
            for i in range(components_to_show):
                component = model.components[i]
                
                # Animate the current component being added
                if i == components_to_show - 1:
                    progress = (frame_num % frames_per_component) / frames_per_component
                    temp_component = Component3D(
                        name=component.name,
                        component_type=component.component_type,
                        vertices=component.vertices.copy(),
                        faces=component.faces,
                        color=component.color,
                        opacity=progress,
                        material=component.material,
                        thickness=component.thickness
                    )
                    
                    # Animate sliding in from above
                    offset = np.array([0, 0, 20 * (1 - progress)])
                    temp_component.translate(offset)
                    self._render_solid_component(ax, temp_component)
                else:
                    self._render_solid_component(ax, component)
            
            # Set labels and limits
            ax.set_xlabel('Length (inches)')
            ax.set_ylabel('Width (inches)')
            ax.set_zlabel('Height (inches)')
            ax.set_title(f'Assembly Animation - Step {components_to_show}/{num_components}')
            self._set_equal_aspect(ax, model)
        
        anim = animation.FuncAnimation(
            fig, update_frame,
            frames=total_frames,
            interval=1000/30,  # 30 fps
            repeat=True
        )
        
        return anim
    
    def export_to_html(self, model: Optional[CrateModel3D] = None, 
                      filepath: Path = Path("crate_visualization.html")) -> Path:
        """
        Export visualization to standalone HTML file.
        
        Args:
            model: CrateModel3D to export
            filepath: Output file path
            
        Returns:
            Path to exported file
        """
        fig = self.render_plotly(model)
        
        # Add custom controls and interactivity
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=[
                        dict(label="Assembled",
                             method="relayout",
                             args=["scene.camera.eye", dict(x=1.5, y=1.5, z=1.5)]),
                        dict(label="Top View",
                             method="relayout",
                             args=["scene.camera.eye", dict(x=0, y=0, z=2.5)]),
                        dict(label="Front View",
                             method="relayout",
                             args=["scene.camera.eye", dict(x=0, y=-2.5, z=0)]),
                        dict(label="Side View",
                             method="relayout",
                             args=["scene.camera.eye", dict(x=2.5, y=0, z=0)])
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.11,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ]
        )
        
        # Save to HTML
        fig.write_html(str(filepath))
        return filepath
    
    def create_comparison_view(self, models: List[CrateModel3D], 
                              labels: List[str]) -> go.Figure:
        """
        Create a comparison view of multiple crate designs.
        
        Args:
            models: List of CrateModel3D objects to compare
            labels: Labels for each model
            
        Returns:
            Plotly figure with subplots
        """
        from plotly.subplots import make_subplots
        
        rows = (len(models) + 1) // 2
        cols = 2
        
        fig = make_subplots(
            rows=rows, cols=cols,
            specs=[[{'type': 'scatter3d'} for _ in range(cols)] for _ in range(rows)],
            subplot_titles=labels
        )
        
        for idx, (model, label) in enumerate(zip(models, labels)):
            row = idx // 2 + 1
            col = idx % 2 + 1
            
            # Create traces for this model
            for component in model.components:
                trace = self._create_mesh_trace(component)
                fig.add_trace(trace, row=row, col=col)
        
        fig.update_layout(
            title="Crate Design Comparison",
            height=800 * rows,
            showlegend=False
        )
        
        return fig


class VisualizationManager:
    """Manager for handling visualization operations and integration."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize visualization manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.visualizer = CrateVisualizer(
            platform=self.config.get('platform', 'tkinter')
        )
        self.cache: Dict[str, CrateModel3D] = {}
        
    def visualize_crate(self, crate_data: Dict[str, Any], 
                        cache_key: Optional[str] = None) -> Any:
        """
        Create and return visualization for crate data.
        
        Args:
            crate_data: Dictionary containing crate specifications
            cache_key: Optional key for caching the model
            
        Returns:
            Visualization object (matplotlib figure or plotly figure)
        """
        # Check cache
        if cache_key and cache_key in self.cache:
            model = self.cache[cache_key]
        else:
            model = self.visualizer.create_crate_model(crate_data)
            if cache_key:
                self.cache[cache_key] = model
        
        # Return appropriate visualization based on platform
        if self.visualizer.platform == 'tkinter':
            return self.visualizer.render_matplotlib(model)
        else:
            return self.visualizer.render_plotly(model)
    
    def export_visualization(self, crate_data: Dict[str, Any], 
                           format: str = 'html',
                           filepath: Optional[Path] = None) -> Path:
        """
        Export visualization to file.
        
        Args:
            crate_data: Dictionary containing crate specifications
            format: Export format ('html', 'png', 'pdf')
            filepath: Output file path
            
        Returns:
            Path to exported file
        """
        model = self.visualizer.create_crate_model(crate_data)
        
        if filepath is None:
            filepath = Path(f"crate_visualization.{format}")
        
        if format == 'html':
            return self.visualizer.export_to_html(model, filepath)
        elif format == 'png':
            fig = self.visualizer.render_matplotlib(model)
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            return filepath
        elif format == 'pdf':
            fig = self.visualizer.render_matplotlib(model)
            fig.savefig(filepath, format='pdf', bbox_inches='tight')
            return filepath
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def create_animation(self, crate_data: Dict[str, Any], 
                        output_path: Optional[Path] = None) -> Path:
        """
        Create assembly animation.
        
        Args:
            crate_data: Dictionary containing crate specifications
            output_path: Output file path for animation
            
        Returns:
            Path to animation file
        """
        model = self.visualizer.create_crate_model(crate_data)
        anim = self.visualizer.create_assembly_animation(model)
        
        if output_path is None:
            output_path = Path("crate_assembly_animation.mp4")
        
        # Save animation
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=30, metadata=dict(artist='AutoCrate'), bitrate=1800)
        anim.save(str(output_path), writer=writer)
        
        return output_path
    
    def compare_designs(self, crate_designs: List[Dict[str, Any]], 
                        labels: Optional[List[str]] = None) -> go.Figure:
        """
        Create comparison visualization of multiple designs.
        
        Args:
            crate_designs: List of crate data dictionaries
            labels: Optional labels for each design
            
        Returns:
            Plotly figure with comparison
        """
        if labels is None:
            labels = [f"Design {i+1}" for i in range(len(crate_designs))]
        
        models = [self.visualizer.create_crate_model(data) for data in crate_designs]
        return self.visualizer.create_comparison_view(models, labels)


if __name__ == "__main__":
    # Test visualization system
    test_crate_data = {
        'length': 48,
        'width': 40,
        'height': 36,
        'plywood_thickness': 0.75,
        'cleat_width': 2.0,
        'cleat_height': 4.0,
        'skid_width': 4.0,
        'skid_height': 4.0,
        'num_skids': 3,
        'floorboard_width': 5.5,
        'floorboard_thickness': 0.75
    }
    
    # Create visualizer
    visualizer = CrateVisualizer(platform='tkinter')
    model = visualizer.create_crate_model(test_crate_data)
    
    # Test matplotlib rendering
    fig = visualizer.render_matplotlib(model)
    plt.show()
    
    # Test different view modes
    visualizer.view_mode = ViewMode.EXPLODED
    fig = visualizer.render_matplotlib(model)
    plt.show()