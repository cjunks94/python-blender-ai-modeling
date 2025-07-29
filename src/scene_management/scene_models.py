"""
Scene data models for multi-object 3D scene management.

This module defines the core data structures for representing complex scenes
with multiple objects, their relationships, and spatial constraints.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of spatial relationships between objects."""
    ON_TOP_OF = "on_top_of"
    NEXT_TO = "next_to"
    BEHIND = "behind"
    IN_FRONT_OF = "in_front_of"
    INSIDE = "inside"
    AROUND = "around"
    SUPPORTS = "supports"
    ATTACHED_TO = "attached_to"


class SpatialConstraint(Enum):
    """Spatial constraints for object placement."""
    NO_OVERLAP = "no_overlap"
    MUST_TOUCH = "must_touch"
    MINIMUM_DISTANCE = "minimum_distance"
    MAXIMUM_DISTANCE = "maximum_distance"
    ALIGN_AXIS = "align_axis"
    GROUND_CONTACT = "ground_contact"


@dataclass
class ObjectRelationship:
    """Represents a relationship between two objects in a scene."""
    source_object_id: str
    target_object_id: str
    relationship_type: RelationshipType
    constraint: Optional[SpatialConstraint] = None
    constraint_value: Optional[float] = None  # For distance constraints
    description: str = ""
    
    def __post_init__(self):
        if not self.description:
            self.description = f"{self.source_object_id} {self.relationship_type.value} {self.target_object_id}"


@dataclass
class SceneObject:
    """Represents a single object within a scene."""
    id: str
    name: str  # Human-readable name like "desk", "monitor", "lamp"
    object_type: str  # Primitive type: cube, sphere, cylinder, plane
    parameters: Dict[str, Any]  # Size, position, rotation, material properties
    relationships: List[ObjectRelationship] = field(default_factory=list)
    export_ready: bool = True
    ai_reasoning: str = ""  # Why AI chose this object/placement
    preview_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
    
    @property
    def position(self) -> Tuple[float, float, float]:
        """Get object position as (x, y, z) tuple."""
        return (
            self.parameters.get('pos_x', 0.0),
            self.parameters.get('pos_y', 0.0), 
            self.parameters.get('pos_z', 0.0)
        )
    
    @property
    def size(self) -> float:
        """Get object size/radius."""
        return self.parameters.get('size', 1.0)
    
    @property
    def rotation(self) -> Tuple[float, float, float]:
        """Get object rotation as (x, y, z) tuple in degrees."""
        return (
            self.parameters.get('rot_x', 0.0),
            self.parameters.get('rot_y', 0.0),
            self.parameters.get('rot_z', 0.0)
        )
    
    def get_bounding_box(self) -> Dict[str, Tuple[float, float, float]]:
        """Calculate approximate bounding box for collision detection."""
        x, y, z = self.position
        size = self.size
        
        # Simple bounding box calculation (could be refined per object type)
        return {
            'min': (x - size/2, y - size/2, z - size/2),
            'max': (x + size/2, y + size/2, z + size/2)
        }
    
    def distance_to(self, other: 'SceneObject') -> float:
        """Calculate distance to another object."""
        x1, y1, z1 = self.position
        x2, y2, z2 = other.position
        return ((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**0.5
    
    def add_relationship(self, target_id: str, relationship_type: RelationshipType, 
                        constraint: Optional[SpatialConstraint] = None,
                        constraint_value: Optional[float] = None) -> ObjectRelationship:
        """Add a relationship to another object."""
        relationship = ObjectRelationship(
            source_object_id=self.id,
            target_object_id=target_id,
            relationship_type=relationship_type,
            constraint=constraint,
            constraint_value=constraint_value
        )
        self.relationships.append(relationship)
        return relationship


@dataclass 
class Scene:
    """Represents a complete 3D scene with multiple objects."""
    scene_id: str
    name: str  # Human-readable name like "Modern Office Setup"
    description: str  # User's original description
    objects: List[SceneObject] = field(default_factory=list)
    composition_notes: str = ""  # AI's composition reasoning
    scene_preview_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    ai_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Scene-level properties
    lighting_setup: Dict[str, Any] = field(default_factory=dict)
    camera_settings: Dict[str, Any] = field(default_factory=dict)
    scene_bounds: Dict[str, float] = field(default_factory=lambda: {
        'min_x': -20.0, 'max_x': 20.0,
        'min_y': -20.0, 'max_y': 20.0, 
        'min_z': -20.0, 'max_z': 20.0
    })
    
    def __post_init__(self):
        if not self.scene_id:
            self.scene_id = f"scene_{str(uuid.uuid4())[:8]}"
    
    @property
    def object_count(self) -> int:
        """Get number of objects in scene."""
        return len(self.objects)
    
    @property
    def export_ready_count(self) -> int:
        """Get number of objects ready for export."""
        return sum(1 for obj in self.objects if obj.export_ready)
    
    def add_object(self, scene_object: SceneObject) -> None:
        """Add an object to the scene."""
        # Ensure unique object ID within scene
        existing_ids = {obj.id for obj in self.objects}
        if scene_object.id in existing_ids:
            scene_object.id = f"{scene_object.id}_{len(self.objects)}"
        
        self.objects.append(scene_object)
        logger.info(f"Added object '{scene_object.name}' to scene '{self.name}'")
    
    def get_object_by_id(self, object_id: str) -> Optional[SceneObject]:
        """Get an object by its ID."""
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None
    
    def get_object_by_name(self, name: str) -> Optional[SceneObject]:
        """Get an object by its name."""
        for obj in self.objects:
            if obj.name.lower() == name.lower():
                return obj
        return None
    
    def get_objects_by_type(self, object_type: str) -> List[SceneObject]:
        """Get all objects of a specific type."""
        return [obj for obj in self.objects if obj.object_type == object_type]
    
    def remove_object(self, object_id: str) -> bool:
        """Remove an object from the scene."""
        for i, obj in enumerate(self.objects):
            if obj.id == object_id:
                removed_obj = self.objects.pop(i)
                logger.info(f"Removed object '{removed_obj.name}' from scene '{self.name}'")
                return True
        return False
    
    def get_all_relationships(self) -> List[ObjectRelationship]:
        """Get all relationships in the scene."""
        relationships = []
        for obj in self.objects:
            relationships.extend(obj.relationships)
        return relationships
    
    def get_scene_bounds(self) -> Dict[str, Tuple[float, float, float]]:
        """Calculate the bounding box that contains all objects."""
        if not self.objects:
            return {
                'min': (0.0, 0.0, 0.0),
                'max': (0.0, 0.0, 0.0)
            }
        
        all_boxes = [obj.get_bounding_box() for obj in self.objects]
        
        min_x = min(box['min'][0] for box in all_boxes)
        min_y = min(box['min'][1] for box in all_boxes)
        min_z = min(box['min'][2] for box in all_boxes)
        
        max_x = max(box['max'][0] for box in all_boxes)
        max_y = max(box['max'][1] for box in all_boxes)
        max_z = max(box['max'][2] for box in all_boxes)
        
        return {
            'min': (min_x, min_y, min_z),
            'max': (max_x, max_y, max_z)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary for serialization."""
        return {
            'scene_id': self.scene_id,
            'name': self.name,
            'description': self.description,
            'composition_notes': self.composition_notes,
            'created_at': self.created_at.isoformat(),
            'ai_metadata': self.ai_metadata,
            'lighting_setup': self.lighting_setup,
            'camera_settings': self.camera_settings,
            'scene_bounds': self.scene_bounds,
            'objects': [
                {
                    'id': obj.id,
                    'name': obj.name,
                    'object_type': obj.object_type,
                    'parameters': obj.parameters,
                    'export_ready': obj.export_ready,
                    'ai_reasoning': obj.ai_reasoning,
                    'preview_url': obj.preview_url,
                    'created_at': obj.created_at.isoformat(),
                    'relationships': [
                        {
                            'source_object_id': rel.source_object_id,
                            'target_object_id': rel.target_object_id,
                            'relationship_type': rel.relationship_type.value,
                            'constraint': rel.constraint.value if rel.constraint else None,
                            'constraint_value': rel.constraint_value,
                            'description': rel.description
                        } for rel in obj.relationships
                    ]
                } for obj in self.objects
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scene':
        """Create scene from dictionary."""
        scene = cls(
            scene_id=data['scene_id'],
            name=data['name'],
            description=data['description'],
            composition_notes=data.get('composition_notes', ''),
            created_at=datetime.fromisoformat(data['created_at']),
            ai_metadata=data.get('ai_metadata', {}),
            lighting_setup=data.get('lighting_setup', {}),
            camera_settings=data.get('camera_settings', {}),
            scene_bounds=data.get('scene_bounds', {})
        )
        
        # Reconstruct objects
        for obj_data in data.get('objects', []):
            obj = SceneObject(
                id=obj_data['id'],
                name=obj_data['name'],
                object_type=obj_data['object_type'],
                parameters=obj_data['parameters'],
                export_ready=obj_data.get('export_ready', True),
                ai_reasoning=obj_data.get('ai_reasoning', ''),
                preview_url=obj_data.get('preview_url'),
                created_at=datetime.fromisoformat(obj_data['created_at'])
            )
            
            # Reconstruct relationships
            for rel_data in obj_data.get('relationships', []):
                relationship = ObjectRelationship(
                    source_object_id=rel_data['source_object_id'],
                    target_object_id=rel_data['target_object_id'],
                    relationship_type=RelationshipType(rel_data['relationship_type']),
                    constraint=SpatialConstraint(rel_data['constraint']) if rel_data.get('constraint') else None,
                    constraint_value=rel_data.get('constraint_value'),
                    description=rel_data.get('description', '')
                )
                obj.relationships.append(relationship)
            
            scene.add_object(obj)
        
        return scene