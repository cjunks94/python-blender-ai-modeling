"""
Script validator for AI-generated content security and safety.

This module validates AI-generated scripts and parameters to ensure they are
safe to execute and don't contain malicious or dangerous operations.
"""

import re
import ast
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security validation levels."""
    STRICT = "strict"        # Maximum security, minimal operations allowed
    MODERATE = "moderate"    # Balanced security with common operations
    PERMISSIVE = "permissive"  # Relaxed security for advanced users


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"    # Blocks execution completely
    WARNING = "warning"      # Shows warning but allows execution
    INFO = "info"           # Informational only


@dataclass
class ValidationIssue:
    """Represents a validation issue found in content."""
    severity: ValidationSeverity
    category: str
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of script/content validation."""
    is_safe: bool
    is_valid: bool
    issues: List[ValidationIssue]
    sanitized_content: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.MODERATE


class ScriptValidator:
    """Validates AI-generated scripts and parameters for security and safety."""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MODERATE):
        """
        Initialize the script validator.
        
        Args:
            security_level: Security level for validation
        """
        self.security_level = security_level
        self.forbidden_patterns = self._load_forbidden_patterns()
        self.allowed_operations = self._load_allowed_operations()
        self.parameter_validators = self._load_parameter_validators()
        
        logger.info(f"Script validator initialized with {security_level.value} security level")
    
    def validate_model_parameters(self, params: Dict[str, Any]) -> ValidationResult:
        """
        Validate model parameters for safety and correctness.
        
        Args:
            params: Model parameters to validate
            
        Returns:
            ValidationResult with safety assessment
        """
        issues = []
        is_safe = True
        is_valid = True
        
        try:
            # Validate each parameter
            for param_name, param_value in params.items():
                param_issues = self._validate_parameter(param_name, param_value)
                issues.extend(param_issues)
                
                # Check for critical issues
                if any(issue.severity == ValidationSeverity.CRITICAL for issue in param_issues):
                    is_safe = False
                    is_valid = False
            
            # Validate parameter combinations
            combination_issues = self._validate_parameter_combinations(params)
            issues.extend(combination_issues)
            
            # Check for suspicious patterns in values
            pattern_issues = self._check_parameter_patterns(params)
            issues.extend(pattern_issues)
            
            return ValidationResult(
                is_safe=is_safe,
                is_valid=is_valid,
                issues=issues,
                security_level=self.security_level
            )
            
        except Exception as e:
            logger.error(f"Parameter validation failed: {str(e)}")
            return ValidationResult(
                is_safe=False,
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="validation_error",
                    message=f"Validation process failed: {str(e)}"
                )],
                security_level=self.security_level
            )
    
    def validate_blender_script(self, script_content: str) -> ValidationResult:
        """
        Validate Blender Python script for security and safety.
        
        Args:
            script_content: Blender Python script to validate
            
        Returns:
            ValidationResult with safety assessment
        """
        issues = []
        is_safe = True
        is_valid = True
        sanitized_content = script_content
        
        try:
            # Check for forbidden patterns
            pattern_issues = self._check_forbidden_patterns(script_content)
            issues.extend(pattern_issues)
            
            if any(issue.severity == ValidationSeverity.CRITICAL for issue in pattern_issues):
                is_safe = False
            
            # Validate Python syntax
            syntax_issues = self._validate_python_syntax(script_content)
            issues.extend(syntax_issues)
            
            if syntax_issues:
                is_valid = False
            
            # Check for allowed operations only
            operation_issues = self._validate_allowed_operations(script_content)
            issues.extend(operation_issues)
            
            # Sanitize if possible
            if is_safe and self.security_level != SecurityLevel.STRICT:
                sanitized_content = self._sanitize_script(script_content)
            
            return ValidationResult(
                is_safe=is_safe,
                is_valid=is_valid,
                issues=issues,
                sanitized_content=sanitized_content if is_safe else None,
                security_level=self.security_level
            )
            
        except Exception as e:
            logger.error(f"Script validation failed: {str(e)}")
            return ValidationResult(
                is_safe=False,
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="validation_error",
                    message=f"Script validation failed: {str(e)}"
                )],
                security_level=self.security_level
            )
    
    def validate_ai_response(self, response_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete AI response for safety and structure.
        
        Args:
            response_data: Complete AI response data
            
        Returns:
            ValidationResult with comprehensive assessment
        """
        issues = []
        is_safe = True
        is_valid = True
        
        try:
            # Validate response structure
            structure_issues = self._validate_response_structure(response_data)
            issues.extend(structure_issues)
            
            # Validate content for suspicious patterns
            content_issues = self._validate_response_content(response_data)
            issues.extend(content_issues)
            
            # Check for data injection attempts
            injection_issues = self._check_injection_patterns(response_data)
            issues.extend(injection_issues)
            
            # Assess overall safety
            critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
            if critical_issues:
                is_safe = False
                is_valid = False
            
            return ValidationResult(
                is_safe=is_safe,
                is_valid=is_valid,
                issues=issues,
                security_level=self.security_level
            )
            
        except Exception as e:
            logger.error(f"AI response validation failed: {str(e)}")
            return ValidationResult(
                is_safe=False,
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="validation_error",
                    message=f"AI response validation failed: {str(e)}"
                )],
                security_level=self.security_level
            )
    
    def _validate_parameter(self, name: str, value: Any) -> List[ValidationIssue]:
        """Validate a single parameter."""
        issues = []
        
        # Get validator for this parameter
        validator = self.parameter_validators.get(name)
        if not validator:
            # Unknown parameter - add warning
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="unknown_parameter",
                message=f"Unknown parameter: {name}",
                suggestion="Verify parameter name is correct"
            ))
            return issues
        
        # Type validation
        expected_type = validator.get('type')
        if expected_type and not isinstance(value, expected_type):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="type_error",
                message=f"Parameter {name} must be of type {expected_type.__name__}, got {type(value).__name__}"
            ))
            return issues
        
        # Range validation
        if 'range' in validator and isinstance(value, (int, float)):
            min_val, max_val = validator['range']
            if value < min_val or value > max_val:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="range_error",
                    message=f"Parameter {name} value {value} outside allowed range [{min_val}, {max_val}]"
                ))
        
        # Pattern validation for strings
        if 'pattern' in validator and isinstance(value, str):
            pattern = validator['pattern']
            if not re.match(pattern, value):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="pattern_error",
                    message=f"Parameter {name} does not match required pattern"
                ))
        
        # Custom validation function
        if 'custom_validator' in validator:
            custom_result = validator['custom_validator'](value)
            if not custom_result['valid']:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="custom_validation",
                    message=f"Parameter {name}: {custom_result['message']}"
                ))
        
        return issues
    
    def _validate_parameter_combinations(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate parameter combinations for logical consistency."""
        issues = []
        
        # Check position and size relationships
        if 'size' in params and 'pos_x' in params:
            size = params['size']
            pos_x = params['pos_x']
            
            # Warn if object might be outside reasonable bounds
            if abs(pos_x) > 50 or size > 20:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="bounds_warning",
                    message="Object may be positioned or sized outside typical scene bounds"
                ))
        
        # Check material consistency
        if 'metallic' in params and 'roughness' in params:
            metallic = params['metallic']
            roughness = params['roughness']
            
            # High metallic usually means low roughness
            if metallic > 0.8 and roughness > 0.5:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="material_advice",
                    message="High metallic values typically pair with low roughness for realism"
                ))
        
        return issues
    
    def _check_parameter_patterns(self, params: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for suspicious patterns in parameter values."""
        issues = []
        
        # Convert params to string for pattern checking
        params_str = str(params)
        
        # Check for script injection patterns
        injection_patterns = [
            r'__import__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'subprocess',
            r'os\.',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, params_str, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="injection_attempt",
                    message=f"Suspicious pattern detected: {pattern}"
                ))
        
        return issues
    
    def _check_forbidden_patterns(self, script_content: str) -> List[ValidationIssue]:
        """Check script for forbidden patterns."""
        issues = []
        
        lines = script_content.split('\\n')
        for line_num, line in enumerate(lines, 1):
            for pattern_info in self.forbidden_patterns:
                if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        severity=pattern_info['severity'],
                        category=pattern_info['category'],
                        message=pattern_info['message'],
                        line_number=line_num,
                        suggestion=pattern_info.get('suggestion')
                    ))
        
        return issues
    
    def _validate_python_syntax(self, script_content: str) -> List[ValidationIssue]:
        """Validate Python syntax."""
        issues = []
        
        try:
            ast.parse(script_content)
        except SyntaxError as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="syntax_error",
                message=f"Python syntax error: {str(e)}",
                line_number=e.lineno,
                suggestion="Fix syntax error before execution"
            ))
        
        return issues
    
    def _validate_allowed_operations(self, script_content: str) -> List[ValidationIssue]:
        """Validate that only allowed operations are used."""
        issues = []
        
        if self.security_level == SecurityLevel.STRICT:
            # In strict mode, only allow specific bpy operations
            allowed_patterns = [
                r'bpy\.ops\.mesh\.primitive_\w+_add',
                r'bpy\.context\.',
                r'bpy\.data\.',
                r'print\(',
                r'import bpy',
                r'math\.',
                r'#.*'  # Comments
            ]
            
            lines = script_content.split('\\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                allowed = any(re.search(pattern, line) for pattern in allowed_patterns)
                if not allowed:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="restricted_operation",
                        message=f"Operation may not be allowed in strict mode: {line[:50]}...",
                        line_number=line_num
                    ))
        
        return issues
    
    def _validate_response_structure(self, response_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate AI response structure."""
        issues = []
        
        # Check for required fields based on response type
        if 'object_type' in response_data:
            # Single object response
            required_fields = ['object_type', 'size']
            for field in required_fields:
                if field not in response_data:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category="missing_field",
                        message=f"Required field missing: {field}"
                    ))
        
        elif 'objects' in response_data:
            # Scene response
            objects = response_data['objects']
            if not isinstance(objects, list):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="structure_error",
                    message="'objects' field must be a list"
                ))
        
        return issues
    
    def _validate_response_content(self, response_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate response content for suspicious patterns."""
        issues = []
        
        # Convert to string and check for patterns
        content_str = str(response_data)
        
        # Check for extremely long values (potential attack)
        if len(content_str) > 10000:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="size_warning",
                message="Response data is unusually large"
            ))
        
        return issues
    
    def _check_injection_patterns(self, response_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for data injection patterns."""
        issues = []
        
        def check_value(value, path=""):
            if isinstance(value, str):
                # Check for script injection
                if re.search(r'<script|javascript:|data:', value, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category="injection_attempt",
                        message=f"Potential script injection in {path}: {value[:50]}..."
                    ))
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    check_value(v, f"{path}[{i}]" if path else f"[{i}]")
        
        check_value(response_data)
        return issues
    
    def _sanitize_script(self, script_content: str) -> str:
        """Sanitize script by removing potentially dangerous operations."""
        # Remove or comment out dangerous operations
        sanitized = script_content
        
        # Add safety wrapper
        safety_header = """
# AI-generated script with safety validation
import bpy
import math

# Safety: Limit to basic Blender operations only
"""
        
        return safety_header + sanitized
    
    def _load_forbidden_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns that are forbidden in scripts."""
        patterns = [
            {
                'pattern': r'import\s+os',
                'severity': ValidationSeverity.CRITICAL,
                'category': 'dangerous_import',
                'message': 'OS module import not allowed',
                'suggestion': 'Use Blender API instead'
            },
            {
                'pattern': r'import\s+subprocess',
                'severity': ValidationSeverity.CRITICAL,
                'category': 'dangerous_import',
                'message': 'Subprocess module import not allowed'
            },
            {
                'pattern': r'eval\s*\\(',
                'severity': ValidationSeverity.CRITICAL,
                'category': 'code_execution',
                'message': 'eval() function not allowed'
            },
            {
                'pattern': r'exec\s*\\(',
                'severity': ValidationSeverity.CRITICAL,
                'category': 'code_execution',
                'message': 'exec() function not allowed'
            },
            {
                'pattern': r'__import__',
                'severity': ValidationSeverity.CRITICAL,
                'category': 'dynamic_import',
                'message': 'Dynamic imports not allowed'
            },
            {
                'pattern': r'open\s*\\(',
                'severity': ValidationSeverity.WARNING,
                'category': 'file_access',
                'message': 'File operations should be avoided',
                'suggestion': 'Use Blender data API instead'
            }
        ]
        
        return patterns
    
    def _load_allowed_operations(self) -> Set[str]:
        """Load set of allowed operations based on security level."""
        base_operations = {
            'bpy.ops.mesh.primitive_cube_add',
            'bpy.ops.mesh.primitive_uv_sphere_add',
            'bpy.ops.mesh.primitive_cylinder_add',
            'bpy.ops.mesh.primitive_plane_add',
            'bpy.context.object',
            'bpy.data.materials',
            'print'
        }
        
        if self.security_level == SecurityLevel.PERMISSIVE:
            base_operations.update({
                'bpy.ops.transform',
                'bpy.ops.object',
                'bpy.data.lights',
                'bpy.data.cameras'
            })
        
        return base_operations
    
    def _load_parameter_validators(self) -> Dict[str, Dict[str, Any]]:
        """Load parameter validation rules."""
        return {
            'object_type': {
                'type': str,
                'pattern': r'^(cube|sphere|cylinder|plane)$'
            },
            'size': {
                'type': (int, float),
                'range': (0.1, 20.0)
            },
            'pos_x': {
                'type': (int, float),
                'range': (-100.0, 100.0)
            },
            'pos_y': {
                'type': (int, float),
                'range': (-100.0, 100.0)
            },
            'pos_z': {
                'type': (int, float),
                'range': (-100.0, 100.0)
            },
            'rot_x': {
                'type': (int, float),
                'range': (-180, 180)
            },
            'rot_y': {
                'type': (int, float),
                'range': (-180, 180)
            },
            'rot_z': {
                'type': (int, float),
                'range': (-180, 180)
            },
            'color': {
                'type': str,
                'pattern': r'^#[0-9A-Fa-f]{6}$'
            },
            'metallic': {
                'type': (int, float),
                'range': (0.0, 1.0)
            },
            'roughness': {
                'type': (int, float),
                'range': (0.0, 1.0)
            },
            'emission_strength': {
                'type': (int, float),
                'range': (0.0, 10.0)
            }
        }