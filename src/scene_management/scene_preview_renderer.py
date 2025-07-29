"""
Scene Preview Renderer for multi-object scenes.

This module extends the preview functionality to handle complex scenes
with multiple objects, generating composite preview images for entire scenes.
"""

import logging
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add utils to path for resource manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.resource_manager import create_temp_script_file, cleanup_old_temp_files

# Import scene management components
from .scene_models import Scene, SceneObject

# Import existing preview functionality
try:
    from blender_integration.preview_renderer import PreviewRenderer, PreviewRenderError
    from blender_integration.script_generator import ScriptGenerator
    PREVIEW_AVAILABLE = True
except ImportError:
    PreviewRenderer = None
    PreviewRenderError = Exception
    ScriptGenerator = None
    PREVIEW_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScenePreviewRenderError(Exception):
    """Exception raised when scene preview rendering fails."""
    pass


class ScenePreviewRenderer:
    """Generates preview images for multi-object scenes."""
    
    def __init__(self, blender_executable: Optional[str] = None):
        """
        Initialize the scene preview renderer.
        
        Args:
            blender_executable: Path to Blender executable
        """
        if not PREVIEW_AVAILABLE:
            raise ScenePreviewRenderError("Preview rendering not available - dependencies missing")
        
        self.preview_renderer = PreviewRenderer(blender_executable)
        self.script_generator = ScriptGenerator(clear_scene=True)
        
        # Scene preview settings
        self.scene_camera_distance = 15.0
        self.scene_camera_height = 8.0
        self.scene_render_samples = 64  # Higher quality for scenes
        
        logger.info("Scene preview renderer initialized")
    
    def render_scene_preview(self, scene: Scene, output_path: str, 
                           render_settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Generate a preview image for an entire scene.
        
        Args:
            scene: Scene object to render
            output_path: Path where preview image will be saved
            render_settings: Optional render settings override
            
        Returns:
            True if successful, False otherwise
        """
        if not scene or scene.object_count == 0:
            logger.error("Cannot render empty scene")
            return False
        
        try:
            # Generate scene script
            scene_script = self.script_generator.generate_scene_script(scene)
            
            # Add scene-specific camera positioning
            enhanced_script = self._enhance_script_for_scene_preview(scene_script, scene)
            
            # Use settings optimized for scenes
            scene_render_settings = self._get_scene_render_settings(render_settings)
            
            # Create temporary script file with managed cleanup
            with create_temp_script_file(enhanced_script, suffix='.py') as temp_script_path:
                # Render using the preview renderer
                success = self.preview_renderer.render_preview(
                    str(temp_script_path), output_path, scene_render_settings
                )
                
                if success:
                    logger.info(f"Successfully rendered scene preview: {scene.name}")
                else:
                    logger.error(f"Failed to render scene preview: {scene.name}")
                
                return success
                
        except Exception as e:
            logger.error(f"Scene preview rendering failed: {str(e)}")
            return False
    
    def render_individual_object_preview(self, scene_object: SceneObject, 
                                       scene_context: Optional[Scene] = None,
                                       output_path: str = "",
                                       render_settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Generate a preview for a single object from a scene with scene context.
        
        Args:
            scene_object: Object to render
            scene_context: Optional scene for context (lighting, etc.)
            output_path: Path where preview image will be saved
            render_settings: Optional render settings override
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate individual object script with scene context
            object_script = self.script_generator.generate_individual_object_script(
                scene_object, scene_context
            )
            
            # Use standard preview renderer settings for individual objects
            individual_render_settings = render_settings or {}
            
            # Create temporary script file with managed cleanup
            with create_temp_script_file(object_script, suffix='.py') as temp_script_path:
                success = self.preview_renderer.render_preview(
                    str(temp_script_path), output_path, individual_render_settings
                )
                
                if success:
                    logger.info(f"Successfully rendered individual object preview: {scene_object.name}")
                else:
                    logger.error(f"Failed to render individual object preview: {scene_object.name}")
                
                return success
                
        except Exception as e:
            logger.error(f"Individual object preview rendering failed: {str(e)}")
            return False
    
    def render_selective_objects_preview(self, object_ids: List[str], scene: Scene,
                                       output_path: str,
                                       render_settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Generate a preview for selected objects from a scene.
        
        Args:
            object_ids: List of object IDs to include in preview
            scene: Scene containing the objects
            output_path: Path where preview image will be saved
            render_settings: Optional render settings override
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate selective objects script
            selective_script = self.script_generator.generate_selective_objects_script(
                object_ids, scene
            )
            
            # Enhance script for better scene preview
            enhanced_script = self._enhance_script_for_scene_preview(selective_script, scene)
            
            # Use scene render settings
            scene_render_settings = self._get_scene_render_settings(render_settings)
            
            # Create temporary script file with managed cleanup
            with create_temp_script_file(enhanced_script, suffix='.py') as temp_script_path:
                success = self.preview_renderer.render_preview(
                    str(temp_script_path), output_path, scene_render_settings
                )
                
                if success:
                    logger.info(f"Successfully rendered selective objects preview: {len(object_ids)} objects")
                else:
                    logger.error(f"Failed to render selective objects preview")
                
                return success
                
        except Exception as e:
            logger.error(f"Selective objects preview rendering failed: {str(e)}")
            return False
    
    def render_scene_thumbnails(self, scene: Scene, output_directory: str,
                              thumbnail_size: Tuple[int, int] = (256, 256)) -> Dict[str, str]:
        """
        Generate thumbnail previews for all objects in a scene.
        
        Args:
            scene: Scene to generate thumbnails for
            output_directory: Directory to save thumbnails
            thumbnail_size: Size of thumbnail images (width, height)
            
        Returns:
            Dictionary mapping object IDs to thumbnail file paths
        """
        thumbnails = {}
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)
        
        # Thumbnail render settings
        thumbnail_settings = {
            'resolution': thumbnail_size,
            'samples': 16,  # Lower quality for thumbnails
            'file_format': 'PNG'
        }
        
        for obj in scene.objects:
            thumbnail_path = output_dir / f"{obj.id}_thumbnail.png"
            
            try:
                success = self.render_individual_object_preview(
                    obj, scene, str(thumbnail_path), thumbnail_settings
                )
                
                if success:
                    thumbnails[obj.id] = str(thumbnail_path)
                    logger.info(f"Generated thumbnail for {obj.name}")
                else:
                    logger.warning(f"Failed to generate thumbnail for {obj.name}")
                    
            except Exception as e:
                logger.error(f"Thumbnail generation failed for {obj.name}: {str(e)}")
        
        return thumbnails
    
    def _enhance_script_for_scene_preview(self, base_script: str, scene: Scene) -> str:
        """Enhance script with optimal camera positioning for scene preview."""
        
        # Calculate scene bounds for optimal camera positioning
        bounds = scene.get_scene_bounds()
        scene_center = (
            (bounds['min'][0] + bounds['max'][0]) / 2,
            (bounds['min'][1] + bounds['max'][1]) / 2,
            (bounds['min'][2] + bounds['max'][2]) / 2
        )
        
        # Calculate scene size to determine camera distance
        scene_size = max(
            bounds['max'][0] - bounds['min'][0],
            bounds['max'][1] - bounds['min'][1],
            bounds['max'][2] - bounds['min'][2]
        )
        
        # Dynamic camera positioning based on scene size
        camera_distance = max(self.scene_camera_distance, scene_size * 1.5)
        camera_height = max(self.scene_camera_height, scene_size * 0.6)
        
        enhanced_camera_script = f"""

# Enhanced camera positioning for scene preview
import math

# Scene bounds and center
scene_center = {scene_center}
scene_size = {scene_size}

# Position camera for optimal scene view
if 'Camera' in bpy.data.objects:
    camera = bpy.data.objects['Camera']
    
    # Position camera at optimal distance and angle
    camera_distance = {camera_distance}
    camera_height = {camera_height}
    
    # Camera position: elevated and angled view
    camera.location = (
        scene_center[0] + camera_distance * 0.7,
        scene_center[1] - camera_distance * 0.7,
        scene_center[2] + camera_height
    )
    
    # Point camera at scene center
    direction = [scene_center[i] - camera.location[i] for i in range(3)]
    
    # Calculate rotation to look at scene center
    camera.rotation_euler = (
        math.atan2(math.sqrt(direction[0]**2 + direction[1]**2), direction[2]) - math.pi/2,
        0,
        math.atan2(direction[1], direction[0]) + math.pi/2
    )

# Enhance lighting for scene
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links

# Clear existing world nodes
world_nodes.clear()

# Add world background
bg_node = world_nodes.new(type='ShaderNodeBackground')
bg_node.location = (0, 0)
bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1.0)  # Dark blue background
bg_node.inputs['Strength'].default_value = 0.1

# Add world output
output_node = world_nodes.new(type='ShaderNodeOutputWorld')
output_node.location = (300, 0)

# Connect background to output
world_links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

# Set render settings for scene preview
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600
bpy.context.scene.cycles.samples = {self.scene_render_samples}
"""
        
        return base_script + enhanced_camera_script
    
    def _get_scene_render_settings(self, custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get optimized render settings for scene previews."""
        default_settings = {
            'resolution': (800, 600),
            'samples': self.scene_render_samples,
            'file_format': 'PNG',
            'render_engine': 'CYCLES',
            'use_denoising': True,
            'transparent_background': False
        }
        
        if custom_settings:
            default_settings.update(custom_settings)
        
        return default_settings
    
    def generate_scene_comparison_preview(self, scenes: List[Scene], output_path: str,
                                        grid_size: Optional[Tuple[int, int]] = None) -> bool:
        """
        Generate a comparison preview showing multiple scenes in a grid layout.
        
        Args:
            scenes: List of scenes to compare
            output_path: Path for the comparison image
            grid_size: Optional grid size (cols, rows). Auto-calculated if None.
            
        Returns:
            True if successful, False otherwise
        """
        # This would require image composition functionality
        # For now, we'll log that this is a future enhancement
        logger.info(f"Scene comparison preview requested for {len(scenes)} scenes")
        logger.info("Scene comparison preview is a future enhancement")
        return False
    
    def validate_scene_for_preview(self, scene: Scene) -> Tuple[bool, List[str]]:
        """
        Validate that a scene can be rendered for preview.
        
        Args:
            scene: Scene to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not scene:
            issues.append("Scene is None")
            return False, issues
        
        if scene.object_count == 0:
            issues.append("Scene contains no objects")
        
        # Check for objects with invalid parameters
        for obj in scene.objects:
            if obj.size <= 0:
                issues.append(f"Object '{obj.name}' has invalid size: {obj.size}")
            
            # Check position bounds
            x, y, z = obj.position
            if abs(x) > 100 or abs(y) > 100 or abs(z) > 100:
                issues.append(f"Object '{obj.name}' is very far from origin")
        
        # Check scene bounds
        bounds = scene.get_scene_bounds()
        scene_size = max(
            bounds['max'][0] - bounds['min'][0],
            bounds['max'][1] - bounds['min'][1],
            bounds['max'][2] - bounds['min'][2]
        )
        
        if scene_size > 200:
            issues.append(f"Scene is very large ({scene_size:.1f} units)")
        
        is_valid = len(issues) == 0
        return is_valid, issues