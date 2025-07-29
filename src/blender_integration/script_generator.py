"""
Blender Python script generation module.

This module provides functionality to generate parametric Blender Python (bpy) scripts
for creating 3D objects with proper validation and formatting.
"""

from typing import Tuple, Optional, Union, Dict


class ScriptGenerationError(Exception):
    """Exception raised when script generation fails."""
    pass


class ScriptGenerator:
    """Generates Blender Python scripts for 3D object creation."""
    
    def __init__(self, clear_scene: bool = True, origin: Tuple[float, float, float] = (0, 0, 0)):
        """
        Initialize ScriptGenerator.
        
        Args:
            clear_scene: Whether to clear existing objects before creating new ones
            origin: Default origin point for object placement
        """
        self.clear_scene = clear_scene
        self.origin = origin
    
    def generate_cube_script(
        self, 
        size: float, 
        position: Optional[Tuple[float, float, float]] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        material: Optional[Dict[str, any]] = None
    ) -> str:
        """
        Generate a Blender Python script to create a cube.
        
        Args:
            size: Size of the cube (must be positive)
            position: Position tuple (x, y, z). Uses origin if None.
            rotation: Rotation tuple (x, y, z) in radians. No rotation if None.
            material: Material properties dictionary. None for default material.
            
        Returns:
            Complete Blender Python script as string
            
        Raises:
            ScriptGenerationError: If parameters are invalid
        """
        # Validate parameters
        self._validate_size(size)
        
        if position is None:
            position = self.origin
        else:
            self._validate_position(position)
        
        if rotation is not None:
            self._validate_rotation(rotation)
        
        # Build script components
        script_parts = []
        
        # Add header
        script_parts.append("import bpy")
        script_parts.append("")
        
        # Add scene clearing if enabled
        if self.clear_scene:
            script_parts.append(self._generate_clear_scene_script())
            script_parts.append("")
        
        # Add cube creation
        script_parts.append("# Create cube")
        cube_command = f"bpy.ops.mesh.primitive_cube_add(size={size}, location={self._format_vector(position)})"
        script_parts.append(cube_command)
        
        # Add rotation if specified
        if rotation is not None:
            script_parts.append("")
            script_parts.append("# Apply rotation")
            script_parts.append(f"bpy.context.object.rotation_euler = {self._format_vector(rotation)}")
        
        # Add material if specified
        if material is not None:
            script_parts.append(self._generate_material_script(material))
        
        # Add success message
        script_parts.append("")
        script_parts.append('print("Cube generated successfully")')
        
        return "\n".join(script_parts)
    
    def _validate_size(self, size: Union[int, float]) -> None:
        """
        Validate size parameter.
        
        Args:
            size: Size value to validate
            
        Raises:
            ScriptGenerationError: If size is invalid
        """
        if size is None:
            raise ScriptGenerationError("Size cannot be None")
        
        if not isinstance(size, (int, float)):
            raise ScriptGenerationError("Size must be a number")
        
        if size <= 0:
            raise ScriptGenerationError("Size must be positive")
    
    def _validate_position(self, position: Tuple[float, float, float]) -> None:
        """
        Validate position parameter.
        
        Args:
            position: Position tuple to validate
            
        Raises:
            ScriptGenerationError: If position is invalid
        """
        if position is None:
            raise ScriptGenerationError("Position cannot be None")
        
        if not isinstance(position, tuple):
            raise ScriptGenerationError("Position must be a tuple")
        
        if len(position) != 3:
            raise ScriptGenerationError("Position must be a 3-element tuple (x, y, z)")
        
        for i, coord in enumerate(position):
            if not isinstance(coord, (int, float)):
                raise ScriptGenerationError(f"Position coordinate {i} must be a number")
    
    def _validate_rotation(self, rotation: Tuple[float, float, float]) -> None:
        """
        Validate rotation parameter.
        
        Args:
            rotation: Rotation tuple to validate
            
        Raises:
            ScriptGenerationError: If rotation is invalid
        """
        if rotation is None:
            raise ScriptGenerationError("Rotation cannot be None")
        
        if not isinstance(rotation, tuple):
            raise ScriptGenerationError("Rotation must be a tuple")
        
        if len(rotation) != 3:
            raise ScriptGenerationError("Rotation must be a 3-element tuple (x, y, z)")
        
        for i, angle in enumerate(rotation):
            if not isinstance(angle, (int, float)):
                raise ScriptGenerationError(f"Rotation angle {i} must be a number")
    
    def _format_vector(self, vector: Tuple[float, float, float]) -> str:
        """
        Format a 3D vector tuple as a string.
        
        Args:
            vector: Vector tuple to format
            
        Returns:
            Formatted vector string
        """
        return f"({vector[0]}, {vector[1]}, {vector[2]})"
    
    def generate_sphere_script(
        self, 
        radius: float, 
        position: Optional[Tuple[float, float, float]] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        subdivisions: int = 2,
        material: Optional[Dict[str, any]] = None
    ) -> str:
        """
        Generate a Blender Python script to create a sphere.
        
        Args:
            radius: Radius of the sphere (must be positive)
            position: Position tuple (x, y, z). Uses origin if None.
            rotation: Rotation tuple (x, y, z) in radians. No rotation if None.
            subdivisions: Level of detail (1-6, default 2)
            material: Material properties dictionary. None for default material.
            
        Returns:
            Complete Blender Python script as string
            
        Raises:
            ScriptGenerationError: If parameters are invalid
        """
        # Validate parameters
        self._validate_radius(radius)
        self._validate_subdivisions(subdivisions)
        
        if position is None:
            position = self.origin
        else:
            self._validate_position(position)
        
        if rotation is not None:
            self._validate_rotation(rotation)
        
        # Build script components
        script_parts = []
        
        # Add header
        script_parts.append("import bpy")
        script_parts.append("")
        
        # Add scene clearing if enabled
        if self.clear_scene:
            script_parts.append(self._generate_clear_scene_script())
            script_parts.append("")
        
        # Add sphere creation
        script_parts.append("# Create sphere")
        sphere_command = f"bpy.ops.mesh.primitive_uv_sphere_add(radius={radius}, location={self._format_vector(position)}, segments={subdivisions})"
        script_parts.append(sphere_command)
        
        # Add rotation if specified
        if rotation is not None:
            script_parts.append("")
            script_parts.append("# Apply rotation")
            script_parts.append(f"bpy.context.object.rotation_euler = {self._format_vector(rotation)}")
        
        # Add material if specified
        if material is not None:
            script_parts.append(self._generate_material_script(material))
        
        # Add success message
        script_parts.append("")
        script_parts.append('print("Sphere generated successfully")')
        
        return "\n".join(script_parts)
    
    def _validate_radius(self, radius: Union[int, float]) -> None:
        """
        Validate radius parameter.
        
        Args:
            radius: Radius value to validate
            
        Raises:
            ScriptGenerationError: If radius is invalid
        """
        if radius is None:
            raise ScriptGenerationError("Radius cannot be None")
        
        if not isinstance(radius, (int, float)):
            raise ScriptGenerationError("Radius must be a number")
        
        if radius <= 0:
            raise ScriptGenerationError("Radius must be positive")
    
    def generate_cylinder_script(
        self, 
        radius: float,
        depth: float,
        position: Optional[Tuple[float, float, float]] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        vertices: int = 32,
        material: Optional[Dict[str, any]] = None
    ) -> str:
        """
        Generate a Blender Python script to create a cylinder.
        
        Args:
            radius: Radius of the cylinder (must be positive)
            depth: Height/depth of the cylinder (must be positive)
            position: Position tuple (x, y, z). Uses origin if None.
            rotation: Rotation tuple (x, y, z) in radians. No rotation if None.
            vertices: Number of vertices for the circle (8-128, default 32)
            material: Material properties dictionary. None for default material.
            
        Returns:
            Complete Blender Python script as string
            
        Raises:
            ScriptGenerationError: If parameters are invalid
        """
        # Validate parameters
        self._validate_radius(radius)
        self._validate_depth(depth)
        self._validate_vertices(vertices)
        
        if position is None:
            position = self.origin
        else:
            self._validate_position(position)
        
        if rotation is not None:
            self._validate_rotation(rotation)
        
        # Build script components
        script_parts = []
        
        # Add header
        script_parts.append("import bpy")
        script_parts.append("")
        
        # Add scene clearing if enabled
        if self.clear_scene:
            script_parts.append(self._generate_clear_scene_script())
            script_parts.append("")
        
        # Add cylinder creation
        script_parts.append("# Create cylinder")
        cylinder_command = f"bpy.ops.mesh.primitive_cylinder_add(radius={radius}, depth={depth}, location={self._format_vector(position)}, vertices={vertices})"
        script_parts.append(cylinder_command)
        
        # Add rotation if specified
        if rotation is not None:
            script_parts.append("")
            script_parts.append("# Apply rotation")
            script_parts.append(f"bpy.context.object.rotation_euler = {self._format_vector(rotation)}")
        
        # Add material if specified
        if material is not None:
            script_parts.append(self._generate_material_script(material))
        
        # Add success message
        script_parts.append("")
        script_parts.append('print("Cylinder generated successfully")')
        
        return "\n".join(script_parts)
    
    def _validate_subdivisions(self, subdivisions: int) -> None:
        """
        Validate subdivisions parameter.
        
        Args:
            subdivisions: Subdivisions value to validate
            
        Raises:
            ScriptGenerationError: If subdivisions is invalid
        """
        if not isinstance(subdivisions, int):
            raise ScriptGenerationError("Subdivisions must be an integer")
        
        if subdivisions < 1 or subdivisions > 6:
            raise ScriptGenerationError("Subdivisions must be between 1 and 6")
    
    def _validate_depth(self, depth: Union[int, float]) -> None:
        """
        Validate depth parameter.
        
        Args:
            depth: Depth value to validate
            
        Raises:
            ScriptGenerationError: If depth is invalid
        """
        if depth is None:
            raise ScriptGenerationError("Depth cannot be None")
        
        if not isinstance(depth, (int, float)):
            raise ScriptGenerationError("Depth must be a number")
        
        if depth <= 0:
            raise ScriptGenerationError("Depth must be positive")
    
    def generate_plane_script(
        self, 
        size: float,
        position: Optional[Tuple[float, float, float]] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        material: Optional[Dict[str, any]] = None
    ) -> str:
        """
        Generate a Blender Python script to create a plane.
        
        Args:
            size: Size of the plane (must be positive)
            position: Position tuple (x, y, z). Uses origin if None.
            rotation: Rotation tuple (x, y, z) in radians. No rotation if None.
            material: Material properties dictionary. None for default material.
            
        Returns:
            Complete Blender Python script as string
            
        Raises:
            ScriptGenerationError: If parameters are invalid
        """
        # Validate parameters
        self._validate_size(size)
        
        if position is None:
            position = self.origin
        else:
            self._validate_position(position)
        
        if rotation is not None:
            self._validate_rotation(rotation)
        
        # Build script components
        script_parts = []
        
        # Add header
        script_parts.append("import bpy")
        script_parts.append("")
        
        # Add scene clearing if enabled
        if self.clear_scene:
            script_parts.append(self._generate_clear_scene_script())
            script_parts.append("")
        
        # Add plane creation
        script_parts.append("# Create plane")
        plane_command = f"bpy.ops.mesh.primitive_plane_add(size={size}, location={self._format_vector(position)})"
        script_parts.append(plane_command)
        
        # Add rotation if specified
        if rotation is not None:
            script_parts.append("")
            script_parts.append("# Apply rotation")
            script_parts.append(f"bpy.context.object.rotation_euler = {self._format_vector(rotation)}")
        
        # Add material if specified
        if material is not None:
            script_parts.append(self._generate_material_script(material))
        
        # Add success message
        script_parts.append("")
        script_parts.append('print("Plane generated successfully")')
        
        return "\n".join(script_parts)
    
    def _validate_vertices(self, vertices: int) -> None:
        """
        Validate vertices parameter.
        
        Args:
            vertices: Vertices value to validate
            
        Raises:
            ScriptGenerationError: If vertices is invalid
        """
        if not isinstance(vertices, int):
            raise ScriptGenerationError("Vertices must be an integer")
        
        if vertices < 8 or vertices > 128:
            raise ScriptGenerationError("Vertices must be between 8 and 128")
    
    def _generate_clear_scene_script(self) -> str:
        """
        Generate script to clear existing objects from the scene.
        
        Returns:
            Script snippet for clearing scene
        """
        return """# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)"""
    
    def _generate_material_script(self, material_props: Optional[Dict[str, any]] = None) -> str:
        """
        Generate script to create and apply material to active object.
        
        Args:
            material_props: Dictionary with material properties:
                - color: RGB tuple or hex string
                - metallic: Float 0-1
                - roughness: Float 0-1
                - emission: Boolean
                - emission_strength: Float
                
        Returns:
            Script snippet for material creation and application
        """
        if not material_props:
            return ""
        
        script_parts = []
        script_parts.append("\n# Create and apply material")
        script_parts.append("import bpy")
        script_parts.append("obj = bpy.context.active_object")
        script_parts.append("")
        script_parts.append("# Create new material")
        script_parts.append("mat = bpy.data.materials.new(name='GeneratedMaterial')")
        script_parts.append("mat.use_nodes = True")
        script_parts.append("nodes = mat.node_tree.nodes")
        script_parts.append("links = mat.node_tree.links")
        script_parts.append("")
        script_parts.append("# Clear default nodes")
        script_parts.append("nodes.clear()")
        script_parts.append("")
        script_parts.append("# Add Principled BSDF shader")
        script_parts.append("bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')")
        script_parts.append("bsdf.location = (0, 0)")
        script_parts.append("")
        
        # Handle color
        if 'color' in material_props:
            color = material_props['color']
            if isinstance(color, str) and color.startswith('#'):
                # Convert hex to RGB
                color = color.lstrip('#')
                r = int(color[0:2], 16) / 255.0
                g = int(color[2:4], 16) / 255.0
                b = int(color[4:6], 16) / 255.0
                script_parts.append(f"bsdf.inputs['Base Color'].default_value = ({r}, {g}, {b}, 1.0)")
            elif isinstance(color, (tuple, list)) and len(color) >= 3:
                script_parts.append(f"bsdf.inputs['Base Color'].default_value = ({color[0]}, {color[1]}, {color[2]}, 1.0)")
        
        # Handle metallic
        if 'metallic' in material_props:
            script_parts.append(f"bsdf.inputs['Metallic'].default_value = {material_props['metallic']}")
        
        # Handle roughness
        if 'roughness' in material_props:
            script_parts.append(f"bsdf.inputs['Roughness'].default_value = {material_props['roughness']}")
        
        # Handle emission
        if material_props.get('emission', False):
            strength = material_props.get('emission_strength', 1.0)
            script_parts.append("")
            script_parts.append("# Add emission")
            script_parts.append(f"bsdf.inputs['Emission Strength'].default_value = {strength}")
            if 'color' in material_props:
                # Use same color for emission
                script_parts.append("bsdf.inputs['Emission Color'].default_value = bsdf.inputs['Base Color'].default_value")
        
        script_parts.append("")
        script_parts.append("# Add output node")
        script_parts.append("output = nodes.new(type='ShaderNodeOutputMaterial')")
        script_parts.append("output.location = (300, 0)")
        script_parts.append("")
        script_parts.append("# Connect nodes")
        script_parts.append("links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])")
        script_parts.append("")
        script_parts.append("# Apply material to object")
        script_parts.append("if obj.data.materials:")
        script_parts.append("    obj.data.materials[0] = mat")
        script_parts.append("else:")
        script_parts.append("    obj.data.materials.append(mat)")
        
        return "\n".join(script_parts)