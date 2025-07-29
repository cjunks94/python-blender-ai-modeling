"""
Model interpreter for converting AI responses to 3D model parameters.

This module translates AI-generated model descriptions into parameters
that can be used by the Blender integration system.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Import scene management components
try:
    from scene_management import Scene, SceneObject, RelationshipType, ScenePreviewRenderer, SCENE_PREVIEW_AVAILABLE
    SCENE_MANAGEMENT_AVAILABLE = True
except ImportError:
    SCENE_MANAGEMENT_AVAILABLE = False
    SCENE_PREVIEW_AVAILABLE = False
    Scene = None
    SceneObject = None
    RelationshipType = None
    ScenePreviewRenderer = None

logger = logging.getLogger(__name__)


@dataclass
class ModelValidationResult:
    """Result of model parameter validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    corrected_params: Optional[Dict[str, Any]] = None


@dataclass
class InterpretationResult:
    """Result of AI response interpretation."""
    success: bool
    models: List[Dict[str, Any]]
    scene_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ModelInterpreter:
    """Interprets AI responses and converts them to valid model parameters."""
    
    def __init__(self):
        """Initialize the model interpreter."""
        self.valid_object_types = ['cube', 'sphere', 'cylinder', 'plane']
        self.size_range = (0.1, 10.0)
        self.position_range = (-20.0, 20.0)
        self.rotation_range = (-180, 180)
        self.material_ranges = {
            'metallic': (0.0, 1.0),
            'roughness': (0.0, 1.0),
            'emission_strength': (0.0, 10.0)
        }
        
        logger.info("Model interpreter initialized")
    
    def interpret_single_model(self, ai_data: Dict[str, Any]) -> InterpretationResult:
        """
        Interpret AI response for a single model.
        
        Args:
            ai_data: AI response data containing model parameters
            
        Returns:
            InterpretationResult with interpreted model data
        """
        try:
            # Validate and correct the model parameters
            validation = self._validate_model_params(ai_data)
            
            if not validation.is_valid and not validation.corrected_params:
                return InterpretationResult(
                    success=False,
                    models=[],
                    error_message=f"Invalid model parameters: {', '.join(validation.errors)}"
                )
            
            # Use corrected parameters if available, otherwise original
            model_params = validation.corrected_params or ai_data
            
            # Convert to our internal format
            converted_model = self._convert_to_internal_format(model_params)
            
            if validation.warnings:
                logger.warning(f"Model interpretation warnings: {', '.join(validation.warnings)}")
            
            return InterpretationResult(
                success=True,
                models=[converted_model],
                scene_info={
                    'model_count': 1,
                    'reasoning': ai_data.get('reasoning', 'AI-generated model'),
                    'warnings': validation.warnings
                }
            )
            
        except Exception as e:
            logger.error(f"Model interpretation failed: {str(e)}")
            return InterpretationResult(
                success=False,
                models=[],
                error_message=f"Interpretation error: {str(e)}"
            )
    
    def interpret_scene(self, ai_data: Dict[str, Any]) -> InterpretationResult:
        """
        Interpret AI response for a complex scene with multiple objects.
        
        Args:
            ai_data: AI response data containing scene and object parameters
            
        Returns:
            InterpretationResult with interpreted scene data
        """
        try:
            objects_data = ai_data.get('objects', [])
            if not objects_data:
                return InterpretationResult(
                    success=False,
                    models=[],
                    error_message="No objects found in scene data"
                )
            
            converted_models = []
            all_warnings = []
            
            for i, obj_data in enumerate(objects_data):
                # Validate each object
                validation = self._validate_model_params(obj_data)
                
                if not validation.is_valid and not validation.corrected_params:
                    logger.warning(f"Skipping invalid object {i}: {', '.join(validation.errors)}")
                    continue
                
                # Convert to internal format
                model_params = validation.corrected_params or obj_data
                converted_model = self._convert_to_internal_format(model_params, f"object_{i}")
                converted_models.append(converted_model)
                
                if validation.warnings:
                    all_warnings.extend([f"Object {i}: {w}" for w in validation.warnings])
            
            if not converted_models:
                return InterpretationResult(
                    success=False,
                    models=[],
                    error_message="No valid objects could be interpreted from scene"
                )
            
            # Check for object collisions
            collision_warnings = self._check_object_collisions(converted_models)
            all_warnings.extend(collision_warnings)
            
            scene_info = {
                'scene_name': ai_data.get('scene_name', 'AI Generated Scene'),
                'description': ai_data.get('description', ''),
                'model_count': len(converted_models),
                'composition_notes': ai_data.get('composition_notes', ''),
                'warnings': all_warnings
            }
            
            return InterpretationResult(
                success=True,
                models=converted_models,
                scene_info=scene_info
            )
            
        except Exception as e:
            logger.error(f"Scene interpretation failed: {str(e)}")
            return InterpretationResult(
                success=False,
                models=[],
                error_message=f"Scene interpretation error: {str(e)}"
            )
    
    def interpret_material_suggestions(self, ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret AI material suggestions.
        
        Args:
            ai_data: AI response with material suggestions
            
        Returns:
            Processed material suggestions
        """
        try:
            result = {
                'primary': None,
                'alternatives': [],
                'valid': False
            }
            
            # Process primary suggestion
            primary = ai_data.get('primary_suggestion', {})
            if primary:
                validated_primary = self._validate_material_params(primary)
                if validated_primary['is_valid']:
                    result['primary'] = validated_primary['material']
                    result['valid'] = True
            
            # Process alternatives
            alternatives = ai_data.get('alternatives', [])
            for alt in alternatives:
                validated_alt = self._validate_material_params(alt)
                if validated_alt['is_valid']:
                    result['alternatives'].append(validated_alt['material'])
            
            return result
            
        except Exception as e:
            logger.error(f"Material suggestion interpretation failed: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    def _validate_model_params(self, params: Dict[str, Any]) -> ModelValidationResult:
        """Validate and correct model parameters."""
        errors = []
        warnings = []
        corrected = params.copy()
        
        # Validate object type
        object_type = params.get('object_type', '').lower()
        if object_type not in self.valid_object_types:
            if object_type:
                errors.append(f"Invalid object type: {object_type}")
            else:
                errors.append("Missing object type")
            # Try to infer from context or default to cube
            corrected['object_type'] = 'cube'
            warnings.append("Object type defaulted to cube")
        
        # Validate size
        size = params.get('size', 2.0)
        if not isinstance(size, (int, float)) or size <= 0:
            warnings.append(f"Invalid size {size}, using default 2.0")
            corrected['size'] = 2.0
        elif size < self.size_range[0] or size > self.size_range[1]:
            corrected['size'] = max(self.size_range[0], min(size, self.size_range[1]))
            warnings.append(f"Size clamped to valid range: {corrected['size']}")
        
        # Validate position
        position = params.get('position', {'x': 0, 'y': 0, 'z': 0})
        if not isinstance(position, dict):
            warnings.append("Invalid position format, using origin")
            corrected['position'] = {'x': 0, 'y': 0, 'z': 0}
        else:
            corrected_pos = {}
            for axis in ['x', 'y', 'z']:
                val = position.get(axis, 0)
                if not isinstance(val, (int, float)):
                    corrected_pos[axis] = 0
                    warnings.append(f"Invalid {axis} position, using 0")
                else:
                    corrected_pos[axis] = max(self.position_range[0], 
                                            min(val, self.position_range[1]))
            corrected['position'] = corrected_pos
        
        # Validate rotation
        rotation = params.get('rotation', {'x': 0, 'y': 0, 'z': 0})
        if not isinstance(rotation, dict):
            warnings.append("Invalid rotation format, using no rotation")
            corrected['rotation'] = {'x': 0, 'y': 0, 'z': 0}
        else:
            corrected_rot = {}
            for axis in ['x', 'y', 'z']:
                val = rotation.get(axis, 0)
                if not isinstance(val, (int, float)):
                    corrected_rot[axis] = 0
                    warnings.append(f"Invalid {axis} rotation, using 0")
                else:
                    corrected_rot[axis] = max(self.rotation_range[0], 
                                            min(val, self.rotation_range[1]))
            corrected['rotation'] = corrected_rot
        
        # Validate material
        material = params.get('material', {})
        if material:
            corrected['material'] = self._validate_material_params(material)['material']
        
        is_valid = len(errors) == 0
        
        return ModelValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            corrected_params=corrected if (errors or warnings) else None
        )
    
    def _validate_material_params(self, material: Dict[str, Any]) -> Dict[str, Any]:
        """Validate material parameters."""
        result = {'is_valid': True, 'material': {}}
        
        # Validate color
        color = material.get('color', '#888888')
        if isinstance(color, str) and color.startswith('#') and len(color) == 7:
            result['material']['color'] = color
        else:
            result['material']['color'] = '#888888'
        
        # Validate numeric properties
        for prop, range_vals in self.material_ranges.items():
            val = material.get(prop, range_vals[0])
            if isinstance(val, (int, float)):
                result['material'][prop] = max(range_vals[0], min(val, range_vals[1]))
            else:
                result['material'][prop] = range_vals[0]
        
        # Handle optional emission color
        emission = material.get('emission')
        if emission and isinstance(emission, str) and emission.startswith('#') and len(emission) == 7:
            result['material']['emission'] = emission
        
        return result
    
    def _convert_to_internal_format(self, params: Dict[str, Any], name: str = None) -> Dict[str, Any]:
        """Convert validated parameters to internal format."""
        # Convert position format
        position = params.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        converted = {
            'object_type': params['object_type'],
            'size': params['size'],
            'pos_x': position['x'],
            'pos_y': position.get('y', 0),  # Our system currently only uses pos_x
            'pos_z': position.get('z', 0),
            'rot_x': params.get('rotation', {}).get('x', 0),
            'rot_y': params.get('rotation', {}).get('y', 0),
            'rot_z': params.get('rotation', {}).get('z', 0),
        }
        
        # Add material properties
        material = params.get('material', {})
        if material:
            converted.update({
                'color': material.get('color', '#888888'),
                'metallic': material.get('metallic', 0.0),
                'roughness': material.get('roughness', 0.5),
            })
            
            # Optional properties
            if 'emission' in material:
                converted['emission'] = material['emission']
            if 'emission_strength' in material:
                converted['emission_strength'] = material['emission_strength']
        
        # Add metadata
        if name:
            converted['ai_name'] = name
        if 'reasoning' in params:
            converted['ai_reasoning'] = params['reasoning']
        
        return converted
    
    def _check_object_collisions(self, models: List[Dict[str, Any]]) -> List[str]:
        """Check for potential object collisions and return warnings."""
        warnings = []
        
        for i, model1 in enumerate(models):
            for j, model2 in enumerate(models[i+1:], i+1):
                # Calculate distance between objects
                pos1 = (model1.get('pos_x', 0), model1.get('pos_y', 0), model1.get('pos_z', 0))
                pos2 = (model2.get('pos_x', 0), model2.get('pos_y', 0), model2.get('pos_z', 0))
                
                distance = ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)**0.5
                
                # Estimate minimum safe distance based on sizes
                size1 = model1.get('size', 2.0)
                size2 = model2.get('size', 2.0)
                min_distance = (size1 + size2) * 0.6  # Conservative estimate
                
                if distance < min_distance:
                    warnings.append(f"Objects {i} and {j} may be overlapping (distance: {distance:.2f})")
        
        return warnings
    
    def interpret_scene_to_scene_object(self, ai_data: Dict[str, Any]) -> Optional['Scene']:
        """
        Interpret AI response and create a complete Scene object with relationships.
        
        Args:
            ai_data: AI response data containing scene and object parameters
            
        Returns:
            Scene object with proper relationships or None if failed
        """
        if not SCENE_MANAGEMENT_AVAILABLE:
            logger.warning("Scene management not available, falling back to basic interpretation")
            return None
        
        try:
            # Use existing scene interpretation
            interpretation = self.interpret_scene(ai_data)
            if not interpretation.success:
                return None
            
            # Create Scene object
            scene = Scene(
                scene_id=f"ai_scene_{hash(ai_data.get('scene_name', 'scene')) % 10000}",
                name=ai_data.get('scene_name', 'AI Generated Scene'),
                description=ai_data.get('description', ''),
                composition_notes=ai_data.get('composition_notes', ''),
                ai_metadata={
                    'original_prompt': ai_data.get('original_prompt', ''),
                    'style': ai_data.get('style', 'creative'),
                    'complexity': ai_data.get('complexity', 'medium'),
                    'generation_timestamp': ai_data.get('timestamp')
                }
            )
            
            # Convert interpreted models to SceneObjects
            for i, model_params in enumerate(interpretation.models):
                scene_object = SceneObject(
                    id=model_params.get('ai_name', f"obj_{i}"),
                    name=ai_data.get('objects', [{}])[i].get('name', f"object_{i}"),
                    object_type=model_params['object_type'],
                    parameters=model_params,
                    ai_reasoning=ai_data.get('objects', [{}])[i].get('reasoning', '')
                )
                
                scene.add_object(scene_object)
            
            # Add relationships based on AI composition notes
            self._extract_relationships_from_ai_data(scene, ai_data)
            
            logger.info(f"Created Scene object with {scene.object_count} objects")
            return scene
            
        except Exception as e:
            logger.error(f"Failed to create Scene object: {str(e)}")
            return None
    
    def _extract_relationships_from_ai_data(self, scene: 'Scene', ai_data: Dict[str, Any]) -> None:
        """Extract and add spatial relationships from AI data."""
        try:
            composition_notes = ai_data.get('composition_notes', '').lower()
            objects_data = ai_data.get('objects', [])
            
            # Simple relationship extraction based on common phrases
            relationship_patterns = {
                'on top of': RelationshipType.ON_TOP_OF,
                'on': RelationshipType.ON_TOP_OF,
                'next to': RelationshipType.NEXT_TO,
                'beside': RelationshipType.NEXT_TO,
                'behind': RelationshipType.BEHIND,
                'in front of': RelationshipType.IN_FRONT_OF,
                'around': RelationshipType.AROUND
            }
            
            # Try to extract relationships from object descriptions
            for i, obj_data in enumerate(objects_data):
                obj_description = obj_data.get('description', '').lower()
                obj_name = obj_data.get('name', f"object_{i}").lower()
                
                current_obj = scene.objects[i] if i < len(scene.objects) else None
                if not current_obj:
                    continue
                
                # Look for relationship patterns in the description
                for pattern, relationship_type in relationship_patterns.items():
                    if pattern in obj_description:
                        # Try to find the target object
                        for j, other_obj in enumerate(scene.objects):
                            if i != j and other_obj.name.lower() in obj_description:
                                current_obj.add_relationship(
                                    other_obj.id, 
                                    relationship_type
                                )
                                logger.info(f"Added relationship: {current_obj.name} {pattern} {other_obj.name}")
                                break
            
        except Exception as e:
            logger.error(f"Failed to extract relationships: {str(e)}")
    
    def generate_scene_preview(self, scene: 'Scene', output_path: str) -> bool:
        """
        Generate a preview image for a complete scene.
        
        Args:
            scene: Scene object to render
            output_path: Path where preview image will be saved
            
        Returns:
            True if successful, False otherwise
        """
        if not SCENE_PREVIEW_AVAILABLE:
            logger.warning("Scene preview rendering not available")
            return False
        
        try:
            renderer = ScenePreviewRenderer()
            success = renderer.render_scene_preview(scene, output_path)
            
            if success:
                logger.info(f"Generated scene preview for '{scene.name}' at {output_path}")
            else:
                logger.error(f"Failed to generate scene preview for '{scene.name}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Scene preview generation failed: {str(e)}")
            return False
    
    def generate_object_thumbnails(self, scene: 'Scene', output_directory: str) -> Dict[str, str]:
        """
        Generate thumbnail previews for all objects in a scene.
        
        Args:
            scene: Scene containing objects to render
            output_directory: Directory to save thumbnails
            
        Returns:
            Dictionary mapping object IDs to thumbnail file paths
        """
        if not SCENE_PREVIEW_AVAILABLE:
            logger.warning("Scene preview rendering not available")
            return {}
        
        try:
            renderer = ScenePreviewRenderer()
            thumbnails = renderer.render_scene_thumbnails(scene, output_directory)
            
            logger.info(f"Generated {len(thumbnails)} thumbnails for scene '{scene.name}'")
            return thumbnails
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {str(e)}")
            return {}