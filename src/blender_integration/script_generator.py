"""
Blender Python script generation module.

This module provides functionality to generate parametric Blender Python (bpy) scripts
for creating 3D objects with proper validation and formatting.
"""

from typing import Tuple, Optional, Union, Dict, List, Any

# Import scene management components
try:
    from scene_management import Scene, SceneObject
    SCENE_MANAGEMENT_AVAILABLE = True
except ImportError:
    SCENE_MANAGEMENT_AVAILABLE = False
    Scene = None
    SceneObject = None


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
    
    # ===== SCENE GENERATION METHODS =====
    
    def generate_scene_script(self, scene: 'Scene') -> str:
        """
        Generate a complete Blender Python script for a multi-object scene.
        
        Args:
            scene: Scene object containing multiple objects and relationships
            
        Returns:
            Complete Blender Python script as string
            
        Raises:
            ScriptGenerationError: If scene generation fails
        """
        if not SCENE_MANAGEMENT_AVAILABLE:
            raise ScriptGenerationError("Scene management not available")
        
        if not scene or not scene.objects:
            raise ScriptGenerationError("Scene is empty or invalid")
        
        try:
            script_parts = []
            
            # Add header and imports
            script_parts.extend(self._generate_scene_header(scene))
            script_parts.append("")
            
            # Clear scene if enabled
            if self.clear_scene:
                script_parts.append(self._generate_clear_scene_script())
                script_parts.append("")
            
            # Generate each object in the scene
            for i, scene_object in enumerate(scene.objects):
                script_parts.append(f"# Create object {i+1}: {scene_object.name} ({scene_object.object_type})")
                
                # Generate individual object script
                object_script = self._generate_scene_object_script(scene_object, scene)
                script_parts.append(object_script)
                script_parts.append("")
            
            # Add scene-level setup
            script_parts.extend(self._generate_scene_setup_script(scene))
            script_parts.append("")
            
            # Add success message
            script_parts.append(f'print("Scene \\"{scene.name}\\" generated successfully with {scene.object_count} objects")')
            
            return "\n".join(script_parts)
            
        except Exception as e:
            raise ScriptGenerationError(f"Failed to generate scene script: {str(e)}")
    
    def generate_individual_object_script(self, scene_object: 'SceneObject', 
                                        scene_context: Optional['Scene'] = None) -> str:
        """
        Generate a Blender script for a single object from a scene with scene context.
        
        Args:
            scene_object: Individual scene object to generate
            scene_context: Optional scene for context (lighting, etc.)
            
        Returns:
            Blender Python script for individual object
            
        Raises:
            ScriptGenerationError: If object generation fails
        """
        if not SCENE_MANAGEMENT_AVAILABLE:
            raise ScriptGenerationError("Scene management not available")
        
        try:
            script_parts = []
            
            # Add header
            script_parts.append("import bpy")
            script_parts.append("import math")
            script_parts.append("")
            script_parts.append(f"# Individual object: {scene_object.name}")
            script_parts.append("")
            
            # Clear scene if enabled
            if self.clear_scene:
                script_parts.append(self._generate_clear_scene_script())
                script_parts.append("")
            
            # Generate the object
            object_script = self._generate_scene_object_script(scene_object, scene_context)
            script_parts.append(object_script)
            script_parts.append("")
            
            # Add scene context if available
            if scene_context:
                script_parts.extend(self._generate_scene_setup_script(scene_context))
                script_parts.append("")
            
            script_parts.append(f'print("Object \\"{scene_object.name}\\" generated successfully")')
            
            return "\n".join(script_parts)
            
        except Exception as e:
            raise ScriptGenerationError(f"Failed to generate individual object script: {str(e)}")
    
    def generate_selective_objects_script(self, object_ids: List[str], scene: 'Scene') -> str:
        """
        Generate a Blender script for selected objects from a scene.
        
        Args:
            object_ids: List of object IDs to include
            scene: Scene containing the objects
            
        Returns:
            Blender Python script for selected objects
            
        Raises:
            ScriptGenerationError: If selective generation fails
        """
        if not SCENE_MANAGEMENT_AVAILABLE:
            raise ScriptGenerationError("Scene management not available")
        
        # Find selected objects
        selected_objects = []
        for obj_id in object_ids:
            scene_obj = scene.get_object_by_id(obj_id)
            if scene_obj:
                selected_objects.append(scene_obj)
        
        if not selected_objects:
            raise ScriptGenerationError("No valid objects found for selection")
        
        try:
            script_parts = []
            
            # Add header
            script_parts.extend(self._generate_scene_header(scene))
            script_parts.append("")
            script_parts.append(f"# Selected objects from scene: {scene.name}")
            script_parts.append("")
            
            # Clear scene if enabled
            if self.clear_scene:
                script_parts.append(self._generate_clear_scene_script())
                script_parts.append("")
            
            # Generate selected objects
            for i, scene_object in enumerate(selected_objects):
                script_parts.append(f"# Create selected object {i+1}: {scene_object.name}")
                object_script = self._generate_scene_object_script(scene_object, scene)
                script_parts.append(object_script)
                script_parts.append("")
            
            # Add scene-level setup
            script_parts.extend(self._generate_scene_setup_script(scene))
            script_parts.append("")
            
            script_parts.append(f'print("Generated {len(selected_objects)} selected objects from scene \\"{scene.name}\\"")')
            
            return "\n".join(script_parts)
            
        except Exception as e:
            raise ScriptGenerationError(f"Failed to generate selective objects script: {str(e)}")
    
    def _generate_scene_header(self, scene: 'Scene') -> List[str]:
        """Generate scene header with imports and metadata."""
        header = [
            "import bpy",
            "import math",
            "",
            f"# Generated scene: {scene.name}",
            f"# Description: {scene.description}",
            f"# Objects: {scene.object_count}",
            f"# Created: {scene.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        if scene.composition_notes:
            header.append(f"# Composition: {scene.composition_notes}")
        
        return header
    
    def _generate_scene_object_script(self, scene_object: 'SceneObject', 
                                    scene_context: Optional['Scene'] = None) -> str:
        """Generate script for a single scene object."""
        # Convert SceneObject parameters to the format expected by existing methods
        params = scene_object.parameters
        
        # Extract position
        position = (
            params.get('pos_x', 0.0),
            params.get('pos_y', 0.0), 
            params.get('pos_z', 0.0)
        )
        
        # Extract rotation (convert degrees to radians)
        rotation = None
        if any(key in params for key in ['rot_x', 'rot_y', 'rot_z']):
            import math
            rotation = (
                math.radians(params.get('rot_x', 0.0)),
                math.radians(params.get('rot_y', 0.0)),
                math.radians(params.get('rot_z', 0.0))
            )
        
        # Extract material
        material = None
        if 'color' in params:
            material = {
                'color': params.get('color', '#888888'),
                'metallic': params.get('metallic', 0.0),
                'roughness': params.get('roughness', 0.5),
            }
            if params.get('emission'):
                material['emission'] = True
                material['emission_strength'] = params.get('emission_strength', 1.0)
        
        # Generate object script using existing methods (without clearing scene)
        original_clear_setting = self.clear_scene
        self.clear_scene = False
        
        try:
            if scene_object.object_type == 'cube':
                object_script = self.generate_cube_script(
                    size=params.get('size', 2.0),
                    position=position,
                    rotation=rotation,
                    material=material
                )
            elif scene_object.object_type == 'sphere':
                object_script = self.generate_sphere_script(
                    radius=params.get('size', 2.0),
                    position=position,
                    rotation=rotation,
                    material=material
                )
            elif scene_object.object_type == 'cylinder':
                object_script = self.generate_cylinder_script(
                    radius=params.get('size', 2.0),
                    depth=params.get('size', 2.0) * 2,  # Default height is 2x radius
                    position=position,
                    rotation=rotation,
                    material=material
                )
            elif scene_object.object_type == 'plane':
                object_script = self.generate_plane_script(
                    size=params.get('size', 2.0),
                    position=position,
                    rotation=rotation,
                    material=material
                )
            else:
                raise ScriptGenerationError(f"Unsupported object type: {scene_object.object_type}")
            
            # Extract just the object creation part (remove header and clear scene)
            lines = object_script.split('\n')
            
            # Find the actual object creation commands (skip imports and clear scene)
            object_lines = []
            skip_until_create = True
            
            for line in lines:
                if 'Create' in line and '#' in line:  # Found creation comment
                    skip_until_create = False
                
                if not skip_until_create:
                    # Skip import and clear scene lines
                    if (not line.startswith('import ') and 
                        not 'bpy.ops.object.select_all' in line and
                        not 'bpy.ops.object.delete' in line and
                        line.strip()):
                        object_lines.append(line)
            
            # Add object naming
            object_lines.append("")
            object_lines.append(f"# Name the object")
            object_lines.append(f'bpy.context.object.name = "{scene_object.name}"')
            
            return '\n'.join(object_lines)
            
        finally:
            self.clear_scene = original_clear_setting
    
    def _generate_scene_setup_script(self, scene: 'Scene') -> List[str]:
        """Generate scene-level setup (lighting, camera, etc.)."""
        setup_lines = [
            "# Scene setup",
            "",
            "# Set up basic lighting",
            "if 'Light' not in bpy.data.objects:",
            "    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))",
            "    sun = bpy.context.object",
            "    sun.data.energy = 3.0",
            "",
            "# Position camera for scene view",
            "if 'Camera' in bpy.data.objects:",
            "    camera = bpy.data.objects['Camera']",
            "    camera.location = (7, -7, 5)",
            "    camera.rotation_euler = (1.1, 0, 0.785)",
            "",
            "# Set render settings",
            "bpy.context.scene.render.engine = 'CYCLES'",
            "bpy.context.scene.cycles.samples = 32"
        ]
        
        # Add scene-specific lighting if configured
        if scene.lighting_setup:
            setup_lines.append("")
            setup_lines.append("# Custom lighting setup")
            # Could add custom lighting logic here
        
        return setup_lines