"""
Scene validation for spatial relationships and scene integrity.

This module provides validation functionality to ensure scenes are logically
consistent, physically plausible, and ready for generation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .scene_models import Scene, SceneObject, ObjectRelationship, RelationshipType, SpatialConstraint

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"        # Blocks scene generation
    WARNING = "warning"    # Shows warning but allows generation
    INFO = "info"         # Informational only


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a scene."""
    severity: ValidationSeverity
    category: str
    message: str
    object_ids: List[str]
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ValidationResult:
    """Result of scene validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    scene_statistics: Dict[str, Any]
    auto_fixes_applied: int = 0


class SceneValidator:
    """Validates scenes for spatial consistency and generation readiness."""
    
    def __init__(self):
        """Initialize the scene validator."""
        self.max_objects = 20
        self.max_scene_size = 50.0
        self.min_object_distance = 0.1
        
        logger.info("Scene validator initialized")
    
    def validate_scene(self, scene: Scene, auto_fix: bool = False) -> ValidationResult:
        """
        Perform comprehensive scene validation.
        
        Args:
            scene: Scene to validate
            auto_fix: Whether to automatically fix issues when possible
            
        Returns:
            ValidationResult with issues and statistics
        """
        issues = []
        auto_fixes_applied = 0
        
        try:
            # Basic scene validation
            basic_issues, basic_fixes = self._validate_basic_scene_properties(scene, auto_fix)
            issues.extend(basic_issues)
            auto_fixes_applied += basic_fixes
            
            # Object validation
            object_issues, object_fixes = self._validate_objects(scene, auto_fix)
            issues.extend(object_issues)
            auto_fixes_applied += object_fixes
            
            # Spatial validation
            spatial_issues, spatial_fixes = self._validate_spatial_relationships(scene, auto_fix)
            issues.extend(spatial_issues)
            auto_fixes_applied += spatial_fixes
            
            # Collision detection
            collision_issues = self._validate_collisions(scene)
            issues.extend(collision_issues)
            
            # Physics validation
            physics_issues = self._validate_physics(scene)
            issues.extend(physics_issues)
            
            # Composition validation
            composition_issues = self._validate_composition(scene)
            issues.extend(composition_issues)
            
            # Determine overall validity
            error_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.ERROR)
            is_valid = error_count == 0
            
            # Generate statistics
            statistics = self._generate_scene_statistics(scene, issues)
            
            return ValidationResult(
                is_valid=is_valid,
                issues=issues,
                scene_statistics=statistics,
                auto_fixes_applied=auto_fixes_applied
            )
            
        except Exception as e:
            logger.error(f"Scene validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="validation_error",
                    message=f"Validation process failed: {str(e)}",
                    object_ids=[]
                )],
                scene_statistics={}
            )
    
    def _validate_basic_scene_properties(self, scene: Scene, auto_fix: bool) -> Tuple[List[ValidationIssue], int]:
        """Validate basic scene properties."""
        issues = []
        fixes_applied = 0
        
        # Check object count
        if scene.object_count == 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="empty_scene",
                message="Scene contains no objects",
                object_ids=[],
                suggestion="Add at least one object to the scene"
            ))
        elif scene.object_count > self.max_objects:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="too_many_objects",
                message=f"Scene has {scene.object_count} objects (recommended max: {self.max_objects})",
                object_ids=[],
                suggestion="Consider reducing the number of objects for better performance"
            ))
        
        # Check scene name
        if not scene.name.strip():
            if auto_fix:
                scene.name = f"Unnamed Scene {scene.scene_id}"
                fixes_applied += 1
            else:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="missing_name",
                    message="Scene has no name",
                    object_ids=[],
                    suggestion="Provide a descriptive name for the scene",
                    auto_fixable=True
                ))
        
        # Check scene bounds
        bounds = scene.get_scene_bounds()
        scene_size = max(
            bounds['max'][0] - bounds['min'][0],
            bounds['max'][1] - bounds['min'][1],
            bounds['max'][2] - bounds['min'][2]
        )
        
        if scene_size > self.max_scene_size:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="large_scene",
                message=f"Scene is very large ({scene_size:.1f} units)",
                object_ids=[],
                suggestion="Consider scaling down objects or repositioning them"
            ))
        
        return issues, fixes_applied
    
    def _validate_objects(self, scene: Scene, auto_fix: bool) -> Tuple[List[ValidationIssue], int]:
        """Validate individual objects in the scene."""
        issues = []
        fixes_applied = 0
        
        for obj in scene.objects:
            # Check object name
            if not obj.name.strip():
                if auto_fix:
                    obj.name = f"{obj.object_type}_{obj.id}"
                    fixes_applied += 1
                else:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="missing_object_name",
                        message=f"Object {obj.id} has no name",
                        object_ids=[obj.id],
                        suggestion="Provide a descriptive name for the object",
                        auto_fixable=True
                    ))
            
            # Check object parameters
            if obj.size <= 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="invalid_size",
                    message=f"Object '{obj.name}' has invalid size: {obj.size}",
                    object_ids=[obj.id],
                    suggestion="Set size to a positive value"
                ))
            
            # Check if object is within scene bounds
            x, y, z = obj.position
            if abs(x) > self.max_scene_size or abs(y) > self.max_scene_size or abs(z) > self.max_scene_size:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="object_out_of_bounds",
                    message=f"Object '{obj.name}' is far from origin ({x:.1f}, {y:.1f}, {z:.1f})",
                    object_ids=[obj.id],
                    suggestion="Move object closer to scene center"
                ))
        
        return issues, fixes_applied
    
    def _validate_spatial_relationships(self, scene: Scene, auto_fix: bool) -> Tuple[List[ValidationIssue], int]:
        """Validate spatial relationships between objects."""
        issues = []
        fixes_applied = 0
        
        all_relationships = scene.get_all_relationships()
        
        for relationship in all_relationships:
            source_obj = scene.get_object_by_id(relationship.source_object_id)
            target_obj = scene.get_object_by_id(relationship.target_object_id)
            
            if not source_obj or not target_obj:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="invalid_relationship",
                    message=f"Relationship references non-existent objects: {relationship.description}",
                    object_ids=[relationship.source_object_id, relationship.target_object_id]
                ))
                continue
            
            # Validate relationship makes physical sense
            if relationship.relationship_type == RelationshipType.ON_TOP_OF:
                source_y = source_obj.position[1]
                target_y = target_obj.position[1]
                
                if source_y <= target_y:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="impossible_relationship",
                        message=f"'{source_obj.name}' should be above '{target_obj.name}' but isn't",
                        object_ids=[source_obj.id, target_obj.id],
                        suggestion="Adjust object positions to match relationship"
                    ))
        
        return issues, fixes_applied
    
    def _validate_collisions(self, scene: Scene) -> List[ValidationIssue]:
        """Validate object collisions."""
        issues = []
        
        for i, obj1 in enumerate(scene.objects):
            for obj2 in scene.objects[i+1:]:
                distance = obj1.distance_to(obj2)
                min_distance = (obj1.size + obj2.size) * 0.5
                
                if distance < min_distance:
                    overlap = min_distance - distance
                    severity = ValidationSeverity.ERROR if overlap > 0.5 else ValidationSeverity.WARNING
                    
                    issues.append(ValidationIssue(
                        severity=severity,
                        category="object_collision",
                        message=f"Objects '{obj1.name}' and '{obj2.name}' are overlapping (overlap: {overlap:.2f})",
                        object_ids=[obj1.id, obj2.id],
                        suggestion="Move objects apart or reduce their sizes"
                    ))
        
        return issues
    
    def _validate_physics(self, scene: Scene) -> List[ValidationIssue]:
        """Validate basic physics constraints."""
        issues = []
        
        # Check for floating objects (objects with no support)
        for obj in scene.objects:
            y_position = obj.position[1]
            
            # If object is significantly above ground with no support
            if y_position > obj.size and not self._has_support(obj, scene):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="floating_object",
                    message=f"Object '{obj.name}' appears to be floating without support",
                    object_ids=[obj.id],
                    suggestion="Add a support object or place on ground"
                ))
        
        return issues
    
    def _has_support(self, obj: SceneObject, scene: Scene) -> bool:
        """Check if an object has physical support from another object."""
        obj_x, obj_y, obj_z = obj.position
        
        for other_obj in scene.objects:
            if other_obj.id == obj.id:
                continue
            
            other_x, other_y, other_z = other_obj.position
            
            # Check if other object is below and close enough to provide support
            if (other_y < obj_y and 
                abs(other_x - obj_x) < (obj.size + other_obj.size) * 0.7 and
                abs(other_z - obj_z) < (obj.size + other_obj.size) * 0.7):
                return True
        
        return False
    
    def _validate_composition(self, scene: Scene) -> List[ValidationIssue]:
        """Validate scene composition and aesthetics."""
        issues = []
        
        # Check for scene balance
        if scene.object_count > 1:
            positions = [obj.position for obj in scene.objects]
            
            # Calculate center of mass
            center_x = sum(pos[0] for pos in positions) / len(positions)
            center_z = sum(pos[2] for pos in positions) / len(positions)
            
            # Check if scene is heavily unbalanced
            if abs(center_x) > 10 or abs(center_z) > 10:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="unbalanced_composition",
                    message="Scene composition appears unbalanced",
                    object_ids=[],
                    suggestion="Consider repositioning objects for better visual balance"
                ))
        
        # Check for variety in object types
        object_types = set(obj.object_type for obj in scene.objects)
        if len(object_types) == 1 and scene.object_count > 3:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="lack_of_variety",
                message="Scene uses only one type of object",
                object_ids=[],
                suggestion="Consider adding different object types for visual interest"
            ))
        
        return issues
    
    def _generate_scene_statistics(self, scene: Scene, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """Generate comprehensive scene statistics."""
        object_types = {}
        for obj in scene.objects:
            object_types[obj.object_type] = object_types.get(obj.object_type, 0) + 1
        
        issue_counts = {
            'errors': sum(1 for issue in issues if issue.severity == ValidationSeverity.ERROR),
            'warnings': sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING),
            'info': sum(1 for issue in issues if issue.severity == ValidationSeverity.INFO)
        }
        
        bounds = scene.get_scene_bounds()
        
        return {
            'object_count': scene.object_count,
            'object_types': object_types,
            'relationships_count': len(scene.get_all_relationships()),
            'scene_bounds': bounds,
            'issue_counts': issue_counts,
            'export_ready_objects': scene.export_ready_count,
            'validation_timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                'validator', logging.INFO, __file__, 0, '', (), None
            )) if logger.handlers else None
        }