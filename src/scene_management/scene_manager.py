"""
Scene Manager for coordinating multi-object 3D scenes.

This module provides the main interface for creating, managing, and manipulating
complex scenes with multiple objects, relationships, and spatial constraints.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .scene_models import Scene, SceneObject, ObjectRelationship, RelationshipType, SpatialConstraint

logger = logging.getLogger(__name__)


class SceneManager:
    """Manages multi-object 3D scenes with spatial relationships and constraints."""
    
    def __init__(self, scenes_directory: Optional[Path] = None):
        """
        Initialize the scene manager.
        
        Args:
            scenes_directory: Directory to store scene definitions
        """
        self.scenes_directory = scenes_directory or Path("scenes")
        self.scenes_directory.mkdir(exist_ok=True)
        
        # Active scenes in memory
        self.active_scenes: Dict[str, Scene] = {}
        
        logger.info(f"SceneManager initialized with scenes directory: {self.scenes_directory}")
    
    def create_scene(self, name: str, description: str, scene_id: Optional[str] = None) -> Scene:
        """
        Create a new empty scene.
        
        Args:
            name: Human-readable scene name
            description: Scene description
            scene_id: Optional custom scene ID
            
        Returns:
            Created Scene object
        """
        scene = Scene(
            scene_id=scene_id or f"scene_{int(datetime.now().timestamp())}",
            name=name,
            description=description
        )
        
        self.active_scenes[scene.scene_id] = scene
        logger.info(f"Created new scene: {scene.name} (ID: {scene.scene_id})")
        
        return scene
    
    def add_object_to_scene(self, scene_id: str, scene_object: SceneObject) -> bool:
        """
        Add an object to a scene.
        
        Args:
            scene_id: Target scene ID
            scene_object: Object to add
            
        Returns:
            True if successful, False otherwise
        """
        scene = self.get_scene(scene_id)
        if not scene:
            logger.error(f"Scene {scene_id} not found")
            return False
        
        scene.add_object(scene_object)
        return True
    
    def create_object_from_ai_params(self, ai_params: Dict[str, Any], name: str, 
                                   ai_reasoning: str = "") -> SceneObject:
        """
        Create a SceneObject from AI-interpreted parameters.
        
        Args:
            ai_params: Parameters from AI model interpreter
            name: Human-readable object name
            ai_reasoning: AI's reasoning for this object
            
        Returns:
            Created SceneObject
        """
        scene_object = SceneObject(
            id=ai_params.get('ai_name', f"obj_{int(datetime.now().timestamp())}"),
            name=name,
            object_type=ai_params['object_type'],
            parameters=ai_params,
            ai_reasoning=ai_reasoning
        )
        
        logger.info(f"Created scene object: {name} ({scene_object.object_type})")
        return scene_object
    
    def add_relationship(self, scene_id: str, source_object_id: str, target_object_id: str,
                        relationship_type: RelationshipType, 
                        constraint: Optional[SpatialConstraint] = None,
                        constraint_value: Optional[float] = None) -> bool:
        """
        Add a spatial relationship between two objects.
        
        Args:
            scene_id: Scene containing the objects
            source_object_id: Source object ID
            target_object_id: Target object ID
            relationship_type: Type of relationship
            constraint: Optional spatial constraint
            constraint_value: Value for distance constraints
            
        Returns:
            True if successful, False otherwise
        """
        scene = self.get_scene(scene_id)
        if not scene:
            return False
        
        source_obj = scene.get_object_by_id(source_object_id)
        target_obj = scene.get_object_by_id(target_object_id)
        
        if not source_obj or not target_obj:
            logger.error(f"Objects not found: {source_object_id}, {target_object_id}")
            return False
        
        relationship = source_obj.add_relationship(
            target_object_id, relationship_type, constraint, constraint_value
        )
        
        logger.info(f"Added relationship: {relationship.description}")
        return True
    
    def detect_collisions(self, scene_id: str) -> List[Tuple[str, str, float]]:
        """
        Detect collisions between objects in a scene.
        
        Args:
            scene_id: Scene to check
            
        Returns:
            List of (object1_id, object2_id, overlap_distance) tuples
        """
        scene = self.get_scene(scene_id)
        if not scene:
            return []
        
        collisions = []
        objects = scene.objects
        
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                distance = obj1.distance_to(obj2)
                min_distance = (obj1.size + obj2.size) * 0.6  # Conservative overlap threshold
                
                if distance < min_distance:
                    overlap = min_distance - distance
                    collisions.append((obj1.id, obj2.id, overlap))
                    logger.warning(f"Collision detected: {obj1.name} and {obj2.name} (overlap: {overlap:.2f})")
        
        return collisions
    
    def resolve_spatial_relationships(self, scene_id: str) -> bool:
        """
        Attempt to resolve spatial relationships by adjusting object positions.
        
        Args:
            scene_id: Scene to process
            
        Returns:
            True if all relationships were resolved successfully
        """
        scene = self.get_scene(scene_id)
        if not scene:
            return False
        
        resolved_count = 0
        total_relationships = 0
        
        for obj in scene.objects:
            for relationship in obj.relationships:
                total_relationships += 1
                target_obj = scene.get_object_by_id(relationship.target_object_id)
                
                if not target_obj:
                    continue
                
                # Apply relationship-based positioning
                if self._apply_relationship_positioning(obj, target_obj, relationship):
                    resolved_count += 1
        
        logger.info(f"Resolved {resolved_count}/{total_relationships} spatial relationships")
        return resolved_count == total_relationships
    
    def _apply_relationship_positioning(self, source_obj: SceneObject, target_obj: SceneObject,
                                      relationship: ObjectRelationship) -> bool:
        """Apply spatial positioning based on relationship type."""
        try:
            target_x, target_y, target_z = target_obj.position
            source_size = source_obj.size
            target_size = target_obj.size
            
            # Calculate new position based on relationship type
            if relationship.relationship_type == RelationshipType.ON_TOP_OF:
                # Place source object on top of target
                new_y = target_y + target_size + source_size/2
                source_obj.parameters['pos_x'] = target_x
                source_obj.parameters['pos_y'] = new_y
                source_obj.parameters['pos_z'] = target_z
                
            elif relationship.relationship_type == RelationshipType.NEXT_TO:
                # Place source object next to target
                offset = target_size + source_size + 0.5  # Small gap
                source_obj.parameters['pos_x'] = target_x + offset
                source_obj.parameters['pos_y'] = target_y
                source_obj.parameters['pos_z'] = target_z
                
            elif relationship.relationship_type == RelationshipType.BEHIND:
                # Place source object behind target
                offset = target_size + source_size + 0.5
                source_obj.parameters['pos_x'] = target_x
                source_obj.parameters['pos_y'] = target_y
                source_obj.parameters['pos_z'] = target_z - offset
                
            elif relationship.relationship_type == RelationshipType.IN_FRONT_OF:
                # Place source object in front of target
                offset = target_size + source_size + 0.5
                source_obj.parameters['pos_x'] = target_x
                source_obj.parameters['pos_y'] = target_y
                source_obj.parameters['pos_z'] = target_z + offset
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply relationship positioning: {e}")
            return False
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Get a scene by ID."""
        return self.active_scenes.get(scene_id)
    
    def list_scenes(self) -> List[Dict[str, Any]]:
        """List all scenes (both active and stored on disk)."""
        scenes = []
        
        # Add active scenes first
        for scene in self.active_scenes.values():
            scenes.append({
                'scene_id': scene.scene_id,
                'name': scene.name,
                'description': scene.description,
                'object_count': scene.object_count,
                'created_at': scene.created_at.isoformat()
            })
        
        # Add scenes from disk that aren't already active
        active_scene_ids = set(self.active_scenes.keys())
        
        try:
            for scene_file in self.scenes_directory.glob("*.json"):
                scene_id = scene_file.stem
                
                if scene_id not in active_scene_ids:
                    try:
                        with open(scene_file, 'r') as f:
                            scene_data = json.load(f)
                        
                        scenes.append({
                            'scene_id': scene_data.get('scene_id', scene_id),
                            'name': scene_data.get('name', 'Unknown Scene'),
                            'description': scene_data.get('description', ''),
                            'object_count': len(scene_data.get('objects', [])),
                            'created_at': scene_data.get('created_at', datetime.now().isoformat())
                        })
                    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                        logger.warning(f"Failed to load scene {scene_id}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error scanning scenes directory: {e}")
        
        # Sort by creation date (newest first)
        scenes.sort(key=lambda x: x['created_at'], reverse=True)
        return scenes
    
    def save_scene(self, scene_id: str) -> bool:
        """
        Save a scene to disk.
        
        Args:
            scene_id: Scene to save
            
        Returns:
            True if successful, False otherwise
        """
        scene = self.get_scene(scene_id)
        if not scene:
            return False
        
        try:
            scene_file = self.scenes_directory / f"{scene_id}.json"
            with open(scene_file, 'w') as f:
                json.dump(scene.to_dict(), f, indent=2)
            
            logger.info(f"Saved scene {scene.name} to {scene_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save scene {scene_id}: {e}")
            return False
    
    def load_scene(self, scene_id: str) -> Optional[Scene]:
        """
        Load a scene from disk.
        
        Args:
            scene_id: Scene ID to load
            
        Returns:
            Loaded Scene object or None if failed
        """
        try:
            scene_file = self.scenes_directory / f"{scene_id}.json"
            if not scene_file.exists():
                logger.error(f"Scene file not found: {scene_file}")
                return None
            
            with open(scene_file, 'r') as f:
                scene_data = json.load(f)
            
            scene = Scene.from_dict(scene_data)
            self.active_scenes[scene.scene_id] = scene
            
            logger.info(f"Loaded scene {scene.name} from {scene_file}")
            return scene
            
        except Exception as e:
            logger.error(f"Failed to load scene {scene_id}: {e}")
            return None
    
    def delete_scene(self, scene_id: str) -> bool:
        """
        Delete a scene from memory and disk.
        
        Args:
            scene_id: Scene to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from memory
            if scene_id in self.active_scenes:
                scene_name = self.active_scenes[scene_id].name
                del self.active_scenes[scene_id]
                logger.info(f"Removed scene {scene_name} from memory")
            
            # Remove from disk
            scene_file = self.scenes_directory / f"{scene_id}.json"
            if scene_file.exists():
                scene_file.unlink()
                logger.info(f"Deleted scene file: {scene_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete scene {scene_id}: {e}")
            return False
    
    def get_scene_statistics(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed statistics about a scene.
        
        Args:
            scene_id: Scene to analyze
            
        Returns:
            Dictionary with scene statistics
        """
        scene = self.get_scene(scene_id)
        if not scene:
            return None
        
        object_types = {}
        for obj in scene.objects:
            object_types[obj.object_type] = object_types.get(obj.object_type, 0) + 1
        
        bounds = scene.get_scene_bounds()
        scene_size = (
            bounds['max'][0] - bounds['min'][0],
            bounds['max'][1] - bounds['min'][1],
            bounds['max'][2] - bounds['min'][2]
        )
        
        return {
            'scene_id': scene.scene_id,
            'name': scene.name,
            'object_count': scene.object_count,
            'export_ready_count': scene.export_ready_count,
            'object_types': object_types,
            'total_relationships': len(scene.get_all_relationships()),
            'scene_bounds': bounds,
            'scene_size': scene_size,
            'collisions': len(self.detect_collisions(scene_id)),
            'created_at': scene.created_at.isoformat()
        }