"""
Scene Compositor - Tools for arranging, aligning, and distributing objects in 3D scenes.

This module provides various composition tools to help users create well-organized
3D scenes with proper object placement and alignment.
"""

import logging
import math
from typing import List, Dict, Any, Tuple, Optional, Literal
from enum import Enum
from dataclasses import dataclass

from .scene_models import Scene, SceneObject

logger = logging.getLogger(__name__)


class AlignmentAxis(Enum):
    """Axes for object alignment."""
    X = "x"
    Y = "y"
    Z = "z"


class AlignmentMode(Enum):
    """Alignment modes for objects."""
    MIN = "min"  # Align to minimum position
    MAX = "max"  # Align to maximum position
    CENTER = "center"  # Align to center
    DISTRIBUTE = "distribute"  # Distribute evenly


class ArrangementPattern(Enum):
    """Predefined arrangement patterns."""
    GRID = "grid"
    CIRCLE = "circle"
    SPIRAL = "spiral"
    LINE = "line"
    RANDOM = "random"


@dataclass
class BoundingBox:
    """3D bounding box for an object."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float
    
    @property
    def center(self) -> Tuple[float, float, float]:
        """Get the center point of the bounding box."""
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2
        )
    
    @property
    def size(self) -> Tuple[float, float, float]:
        """Get the size of the bounding box."""
        return (
            self.max_x - self.min_x,
            self.max_y - self.min_y,
            self.max_z - self.min_z
        )


class SceneCompositor:
    """Provides tools for arranging and aligning objects in 3D scenes."""
    
    def __init__(self):
        """Initialize the scene compositor."""
        self.grid_spacing = 2.0  # Default grid spacing
        self.circle_radius = 5.0  # Default circle radius
        self.spiral_spacing = 1.0  # Default spiral spacing
        
    def align_objects(self, objects: List[SceneObject], axis: AlignmentAxis, 
                     mode: AlignmentMode, reference_point: Optional[float] = None) -> List[SceneObject]:
        """
        Align objects along a specified axis.
        
        Args:
            objects: List of objects to align
            axis: Axis to align along (X, Y, or Z)
            mode: Alignment mode (MIN, MAX, CENTER)
            reference_point: Optional reference point for alignment
            
        Returns:
            List of objects with updated positions
        """
        if not objects:
            return objects
        
        # Get bounding boxes for all objects
        bboxes = [self._get_object_bbox(obj) for obj in objects]
        
        # Determine reference position
        if reference_point is None:
            if mode == AlignmentMode.MIN:
                reference_point = min(self._get_bbox_value(bbox, axis, 'min') for bbox in bboxes)
            elif mode == AlignmentMode.MAX:
                reference_point = max(self._get_bbox_value(bbox, axis, 'max') for bbox in bboxes)
            elif mode == AlignmentMode.CENTER:
                all_centers = [self._get_bbox_value(bbox, axis, 'center') for bbox in bboxes]
                reference_point = sum(all_centers) / len(all_centers)
        
        # Align objects
        for obj, bbox in zip(objects, bboxes):
            current_value = self._get_object_position_value(obj, axis)
            
            if mode == AlignmentMode.MIN:
                offset = reference_point - self._get_bbox_value(bbox, axis, 'min')
            elif mode == AlignmentMode.MAX:
                offset = reference_point - self._get_bbox_value(bbox, axis, 'max')
            elif mode == AlignmentMode.CENTER:
                offset = reference_point - self._get_bbox_value(bbox, axis, 'center')
            else:
                offset = 0
            
            self._set_object_position_value(obj, axis, current_value + offset)
        
        logger.info(f"Aligned {len(objects)} objects along {axis.value} axis with mode {mode.value}")
        return objects
    
    def distribute_objects(self, objects: List[SceneObject], axis: AlignmentAxis,
                          spacing: Optional[float] = None, 
                          start_point: Optional[float] = None,
                          end_point: Optional[float] = None) -> List[SceneObject]:
        """
        Distribute objects evenly along an axis.
        
        Args:
            objects: List of objects to distribute
            axis: Axis to distribute along
            spacing: Optional fixed spacing between objects
            start_point: Optional start position
            end_point: Optional end position
            
        Returns:
            List of objects with updated positions
        """
        if len(objects) < 2:
            return objects
        
        # Sort objects by current position along axis
        objects = sorted(objects, key=lambda obj: self._get_object_position_value(obj, axis))
        
        if spacing is not None:
            # Fixed spacing distribution
            current_pos = start_point or self._get_object_position_value(objects[0], axis)
            
            for obj in objects:
                self._set_object_position_value(obj, axis, current_pos)
                current_pos += spacing
        else:
            # Even distribution between start and end points
            if start_point is None:
                start_point = self._get_object_position_value(objects[0], axis)
            if end_point is None:
                end_point = self._get_object_position_value(objects[-1], axis)
            
            total_distance = end_point - start_point
            spacing = total_distance / (len(objects) - 1) if len(objects) > 1 else 0
            
            for i, obj in enumerate(objects):
                position = start_point + (i * spacing)
                self._set_object_position_value(obj, axis, position)
        
        logger.info(f"Distributed {len(objects)} objects along {axis.value} axis")
        return objects
    
    def arrange_in_grid(self, objects: List[SceneObject], 
                       columns: Optional[int] = None,
                       spacing: Optional[float] = None,
                       center_point: Tuple[float, float, float] = (0, 0, 0)) -> List[SceneObject]:
        """
        Arrange objects in a grid pattern.
        
        Args:
            objects: List of objects to arrange
            columns: Number of columns (auto-calculated if None)
            spacing: Spacing between objects
            center_point: Center point of the grid
            
        Returns:
            List of objects with updated positions
        """
        if not objects:
            return objects
        
        spacing = spacing or self.grid_spacing
        
        # Calculate grid dimensions
        if columns is None:
            columns = math.ceil(math.sqrt(len(objects)))
        rows = math.ceil(len(objects) / columns)
        
        # Calculate grid offsets to center it
        grid_width = (columns - 1) * spacing
        grid_depth = (rows - 1) * spacing
        start_x = center_point[0] - grid_width / 2
        start_z = center_point[2] - grid_depth / 2
        
        # Arrange objects
        for i, obj in enumerate(objects):
            row = i // columns
            col = i % columns
            
            x = start_x + col * spacing
            z = start_z + row * spacing
            y = center_point[1]  # Keep Y at center height
            
            obj.set_position(x, y, z)
        
        logger.info(f"Arranged {len(objects)} objects in {columns}x{rows} grid")
        return objects
    
    def arrange_in_circle(self, objects: List[SceneObject],
                         radius: Optional[float] = None,
                         center_point: Tuple[float, float, float] = (0, 0, 0),
                         start_angle: float = 0) -> List[SceneObject]:
        """
        Arrange objects in a circle.
        
        Args:
            objects: List of objects to arrange
            radius: Circle radius
            center_point: Center of the circle
            start_angle: Starting angle in radians
            
        Returns:
            List of objects with updated positions
        """
        if not objects:
            return objects
        
        radius = radius or self.circle_radius
        angle_step = (2 * math.pi) / len(objects)
        
        for i, obj in enumerate(objects):
            angle = start_angle + (i * angle_step)
            x = center_point[0] + radius * math.cos(angle)
            z = center_point[2] + radius * math.sin(angle)
            y = center_point[1]
            
            obj.set_position(x, y, z)
            
            # Optionally rotate objects to face center
            # rotation_y = math.degrees(angle + math.pi)
            # obj.set_rotation(0, rotation_y, 0)
        
        logger.info(f"Arranged {len(objects)} objects in circle with radius {radius}")
        return objects
    
    def arrange_in_spiral(self, objects: List[SceneObject],
                         spacing: Optional[float] = None,
                         center_point: Tuple[float, float, float] = (0, 0, 0),
                         height_increment: float = 0.5) -> List[SceneObject]:
        """
        Arrange objects in a spiral pattern.
        
        Args:
            objects: List of objects to arrange
            spacing: Spacing between spiral arms
            center_point: Center of the spiral
            height_increment: Height increase per object
            
        Returns:
            List of objects with updated positions
        """
        if not objects:
            return objects
        
        spacing = spacing or self.spiral_spacing
        
        for i, obj in enumerate(objects):
            angle = i * 0.5  # Angle increment
            radius = spacing * angle / (2 * math.pi)
            
            x = center_point[0] + radius * math.cos(angle)
            z = center_point[2] + radius * math.sin(angle)
            y = center_point[1] + i * height_increment
            
            obj.set_position(x, y, z)
        
        logger.info(f"Arranged {len(objects)} objects in spiral pattern")
        return objects
    
    def snap_to_grid(self, objects: List[SceneObject], 
                    grid_size: float = 1.0,
                    offset: Tuple[float, float, float] = (0, 0, 0)) -> List[SceneObject]:
        """
        Snap objects to nearest grid points.
        
        Args:
            objects: List of objects to snap
            grid_size: Size of grid cells
            offset: Grid offset
            
        Returns:
            List of objects with snapped positions
        """
        for obj in objects:
            x, y, z = obj.position
            
            # Snap to nearest grid point
            snapped_x = round((x - offset[0]) / grid_size) * grid_size + offset[0]
            snapped_y = round((y - offset[1]) / grid_size) * grid_size + offset[1]
            snapped_z = round((z - offset[2]) / grid_size) * grid_size + offset[2]
            
            obj.set_position(snapped_x, snapped_y, snapped_z)
        
        logger.info(f"Snapped {len(objects)} objects to grid with size {grid_size}")
        return objects
    
    def stack_objects(self, objects: List[SceneObject], 
                     axis: AlignmentAxis = AlignmentAxis.Y,
                     spacing: float = 0.1) -> List[SceneObject]:
        """
        Stack objects on top of each other along an axis.
        
        Args:
            objects: List of objects to stack
            axis: Axis to stack along (usually Y)
            spacing: Gap between stacked objects
            
        Returns:
            List of objects with updated positions
        """
        if not objects:
            return objects
        
        # Sort by current position
        objects = sorted(objects, key=lambda obj: self._get_object_position_value(obj, axis))
        
        current_position = self._get_object_position_value(objects[0], axis)
        
        for i, obj in enumerate(objects):
            if i > 0:
                # Get size of previous object
                prev_bbox = self._get_object_bbox(objects[i-1])
                prev_size = self._get_bbox_size(prev_bbox, axis)
                
                # Get size of current object
                curr_bbox = self._get_object_bbox(obj)
                curr_size = self._get_bbox_size(curr_bbox, axis)
                
                # Calculate new position
                current_position += (prev_size / 2) + spacing + (curr_size / 2)
            
            self._set_object_position_value(obj, axis, current_position)
        
        logger.info(f"Stacked {len(objects)} objects along {axis.value} axis")
        return objects
    
    def group_by_type(self, objects: List[SceneObject]) -> Dict[str, List[SceneObject]]:
        """
        Group objects by their type.
        
        Args:
            objects: List of objects to group
            
        Returns:
            Dictionary mapping object types to lists of objects
        """
        groups = {}
        for obj in objects:
            obj_type = obj.object_type
            if obj_type not in groups:
                groups[obj_type] = []
            groups[obj_type].append(obj)
        
        return groups
    
    def _get_object_bbox(self, obj: SceneObject) -> BoundingBox:
        """Get bounding box for an object based on its size."""
        x, y, z = obj.position
        size = obj.size
        
        # Simplified bbox calculation - assumes centered origin
        half_size = size / 2
        
        return BoundingBox(
            min_x=x - half_size,
            max_x=x + half_size,
            min_y=y - half_size,
            max_y=y + half_size,
            min_z=z - half_size,
            max_z=z + half_size
        )
    
    def _get_bbox_value(self, bbox: BoundingBox, axis: AlignmentAxis, mode: str) -> float:
        """Get a specific value from a bounding box."""
        if mode == 'min':
            if axis == AlignmentAxis.X:
                return bbox.min_x
            elif axis == AlignmentAxis.Y:
                return bbox.min_y
            else:
                return bbox.min_z
        elif mode == 'max':
            if axis == AlignmentAxis.X:
                return bbox.max_x
            elif axis == AlignmentAxis.Y:
                return bbox.max_y
            else:
                return bbox.max_z
        elif mode == 'center':
            center = bbox.center
            if axis == AlignmentAxis.X:
                return center[0]
            elif axis == AlignmentAxis.Y:
                return center[1]
            else:
                return center[2]
    
    def _get_bbox_size(self, bbox: BoundingBox, axis: AlignmentAxis) -> float:
        """Get size of bounding box along an axis."""
        size = bbox.size
        if axis == AlignmentAxis.X:
            return size[0]
        elif axis == AlignmentAxis.Y:
            return size[1]
        else:
            return size[2]
    
    def _get_object_position_value(self, obj: SceneObject, axis: AlignmentAxis) -> float:
        """Get object position value for a specific axis."""
        if axis == AlignmentAxis.X:
            return obj.position[0]
        elif axis == AlignmentAxis.Y:
            return obj.position[1]
        else:
            return obj.position[2]
    
    def _set_object_position_value(self, obj: SceneObject, axis: AlignmentAxis, value: float):
        """Set object position value for a specific axis."""
        x, y, z = obj.position
        
        if axis == AlignmentAxis.X:
            obj.set_position(value, y, z)
        elif axis == AlignmentAxis.Y:
            obj.set_position(x, value, z)
        else:
            obj.set_position(x, y, value)