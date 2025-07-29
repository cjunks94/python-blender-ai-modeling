"""
Comprehensive input validation and security module.

This module provides centralized input validation, sanitization, and security
checks for all user inputs throughout the application.
"""

import re
import logging
import bleach
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    pass


class SecurityError(Exception):
    """Exception raised when security validation fails."""
    pass


class InputValidator:
    """Comprehensive input validation and security enforcement."""
    
    # Security patterns for dangerous content
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'vbscript:',  # VBScript URLs
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # Eval function
        r'exec\s*\(',  # Exec function
        r'__import__',  # Python imports
        r'subprocess\.',  # Subprocess calls
        r'os\.',  # OS module calls
        r'sys\.',  # Sys module calls
        r'import\s+os',  # OS imports
        r'import\s+sys',  # Sys imports
        r'import\s+subprocess',  # Subprocess imports
        r'\.\./',  # Path traversal
        r'\.\.\\',  # Path traversal (Windows)
    ]
    
    # Allowed HTML tags for rich text (very minimal)
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_HTML_ATTRIBUTES = {}
    
    # File extension whitelist
    ALLOWED_FILE_EXTENSIONS = {
        'model': ['.obj', '.stl', '.gltf', '.glb', '.blend'],
        'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
        'export': ['.obj', '.stl', '.gltf', '.glb']
    }
    
    # Size limits (in bytes)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_STRING_LENGTH = 10000
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_NAME_LENGTH = 100
    
    @classmethod
    def validate_string(cls, value: Any, field_name: str, 
                       max_length: Optional[int] = None,
                       min_length: int = 0,
                       allow_empty: bool = False,
                       pattern: Optional[str] = None) -> str:
        """
        Validate and sanitize string input.
        
        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            max_length: Maximum allowed length
            min_length: Minimum required length
            allow_empty: Whether empty strings are allowed
            pattern: Regex pattern that must match
            
        Returns:
            Sanitized string value
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            if allow_empty:
                return ""
            raise ValidationError(f"{field_name} is required")
        
        if not isinstance(value, str):
            try:
                value = str(value)
            except (ValueError, TypeError):
                raise ValidationError(f"{field_name} must be a valid string")
        
        # Remove null bytes and control characters
        value = value.replace('\x00', '').strip()
        
        # Check length constraints
        if not allow_empty and len(value) == 0:
            raise ValidationError(f"{field_name} cannot be empty")
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        
        max_len = max_length or cls.MAX_STRING_LENGTH
        if len(value) > max_len:
            raise ValidationError(f"{field_name} cannot exceed {max_len} characters")
        
        # Check for dangerous patterns
        cls._check_security_patterns(value, field_name)
        
        # Validate against pattern if provided
        if pattern and not re.match(pattern, value):
            raise ValidationError(f"{field_name} format is invalid")
        
        return value
    
    @classmethod
    def validate_html_string(cls, value: Any, field_name: str,
                           max_length: Optional[int] = None) -> str:
        """
        Validate and sanitize HTML string input.
        
        Args:
            value: HTML string to validate
            field_name: Name of the field for error messages
            max_length: Maximum allowed length
            
        Returns:
            Sanitized HTML string
            
        Raises:
            ValidationError: If validation fails
        """
        # First validate as regular string
        value = cls.validate_string(value, field_name, max_length)
        
        # Sanitize HTML content
        sanitized = bleach.clean(
            value,
            tags=cls.ALLOWED_HTML_TAGS,
            attributes=cls.ALLOWED_HTML_ATTRIBUTES,
            strip=True
        )
        
        return sanitized
    
    @classmethod
    def validate_numeric(cls, value: Any, field_name: str,
                        min_value: Optional[Union[int, float]] = None,
                        max_value: Optional[Union[int, float]] = None,
                        numeric_type: type = float) -> Union[int, float]:
        """
        Validate numeric input.
        
        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            numeric_type: Expected numeric type (int or float)
            
        Returns:
            Validated numeric value
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")
        
        try:
            if numeric_type == int:
                value = int(value)
            else:
                value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid {numeric_type.__name__}")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} cannot exceed {max_value}")
        
        return value
    
    @classmethod
    def validate_boolean(cls, value: Any, field_name: str) -> bool:
        """
        Validate boolean input.
        
        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            
        Returns:
            Boolean value
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'on'):
                return True
            elif value_lower in ('false', '0', 'no', 'off'):
                return False
        
        raise ValidationError(f"{field_name} must be a valid boolean value")
    
    @classmethod
    def validate_enum(cls, value: Any, field_name: str, 
                     allowed_values: List[str], 
                     case_sensitive: bool = True) -> str:
        """
        Validate enum/choice input.
        
        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            allowed_values: List of allowed values
            case_sensitive: Whether comparison is case sensitive
            
        Returns:
            Validated enum value
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")
        
        value = str(value)
        
        if case_sensitive:
            if value not in allowed_values:
                raise ValidationError(
                    f"{field_name} must be one of: {', '.join(allowed_values)}"
                )
        else:
            value_lower = value.lower()
            allowed_lower = [v.lower() for v in allowed_values]
            if value_lower not in allowed_lower:
                raise ValidationError(
                    f"{field_name} must be one of: {', '.join(allowed_values)}"
                )
            # Return the original case from allowed_values
            value = allowed_values[allowed_lower.index(value_lower)]
        
        return value
    
    @classmethod
    def validate_color(cls, value: Any, field_name: str) -> str:
        """
        Validate hexadecimal color input.
        
        Args:
            value: Color value to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated color string
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")
        
        value = str(value).strip()
        
        # Check hex color pattern
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise ValidationError(f"{field_name} must be a valid hex color (e.g., #FF0000)")
        
        return value.upper()  # Normalize to uppercase
    
    @classmethod
    def validate_file_path(cls, value: Any, field_name: str,
                          file_category: str = 'model',
                          must_exist: bool = False) -> Path:
        """
        Validate file path input.
        
        Args:
            value: File path to validate
            field_name: Name of the field for error messages
            file_category: Category of file ('model', 'image', 'export')
            must_exist: Whether the file must exist
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If validation fails
            SecurityError: If path contains security risks
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")
        
        try:
            path = Path(str(value))
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid file path")
        
        # Security checks
        path_str = str(path)
        
        # Check for path traversal attempts
        if '..' in path_str or path_str.startswith('/'):
            raise SecurityError(f"{field_name} contains invalid path components")
        
        # Check for dangerous patterns
        cls._check_security_patterns(path_str, field_name)
        
        # Validate file extension
        if file_category in cls.ALLOWED_FILE_EXTENSIONS:
            allowed_exts = cls.ALLOWED_FILE_EXTENSIONS[file_category]
            if path.suffix.lower() not in allowed_exts:
                raise ValidationError(
                    f"{field_name} must have one of these extensions: {', '.join(allowed_exts)}"
                )
        
        # Check if file exists (if required)
        if must_exist and not path.exists():
            raise ValidationError(f"{field_name} file does not exist: {path}")
        
        return path
    
    @classmethod
    def validate_url(cls, value: Any, field_name: str,
                    allowed_schemes: List[str] = None) -> str:
        """
        Validate URL input.
        
        Args:
            value: URL to validate
            field_name: Name of the field for error messages
            allowed_schemes: List of allowed URL schemes
            
        Returns:
            Validated URL string
            
        Raises:
            ValidationError: If validation fails
            SecurityError: If URL contains security risks
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")
        
        value = str(value).strip()
        
        # Basic URL validation
        try:
            parsed = urlparse(value)
        except Exception:
            raise ValidationError(f"{field_name} must be a valid URL")
        
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(f"{field_name} must be a complete URL")
        
        # Check allowed schemes
        allowed_schemes = allowed_schemes or ['http', 'https']
        if parsed.scheme.lower() not in allowed_schemes:
            raise SecurityError(
                f"{field_name} scheme must be one of: {', '.join(allowed_schemes)}"
            )
        
        # Security checks
        cls._check_security_patterns(value, field_name)
        
        return value
    
    @classmethod
    def validate_json_data(cls, value: Any, field_name: str,
                         required_keys: List[str] = None,
                         max_depth: int = 10) -> Dict[str, Any]:
        """
        Validate JSON data structure.
        
        Args:
            value: JSON data to validate
            field_name: Name of the field for error messages
            required_keys: List of required keys
            max_depth: Maximum nesting depth allowed
            
        Returns:
            Validated dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")
        
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a valid JSON object")
        
        # Check nesting depth
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise ValidationError(f"{field_name} exceeds maximum nesting depth")
            
            if isinstance(obj, dict):
                for v in obj.values():
                    check_depth(v, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        check_depth(value)
        
        # Check required keys
        if required_keys:
            missing_keys = [key for key in required_keys if key not in value]
            if missing_keys:
                raise ValidationError(
                    f"{field_name} missing required keys: {', '.join(missing_keys)}"
                )
        
        # Recursively validate string values
        def validate_strings(obj):
            if isinstance(obj, dict):
                return {k: validate_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [validate_strings(item) for item in obj]
            elif isinstance(obj, str):
                # Apply basic string validation to prevent XSS
                cls._check_security_patterns(obj, f"{field_name} value")
                return obj
            else:
                return obj
        
        return validate_strings(value)
    
    @classmethod
    def _check_security_patterns(cls, value: str, field_name: str) -> None:
        """
        Check string for dangerous security patterns.
        
        Args:
            value: String to check
            field_name: Field name for error messages
            
        Raises:
            SecurityError: If dangerous patterns found
        """
        value_lower = value.lower()
        
        for i, pattern in enumerate(cls.DANGEROUS_PATTERNS):
            if re.search(pattern, value_lower, re.IGNORECASE | re.DOTALL):
                logger.warning(
                    f"Security pattern {i+1} detected in {field_name}: {pattern}"
                )
                raise SecurityError(
                    f"{field_name} contains potentially dangerous content"
                )
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename for safe file system usage.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        # Ensure not empty
        if not sanitized.strip():
            sanitized = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return sanitized.strip()


class ModelParameterValidator:
    """Specialized validator for 3D model parameters."""
    
    OBJECT_TYPES = ['cube', 'sphere', 'cylinder', 'plane', 'torus', 'cone']
    EXPORT_FORMATS = ['obj', 'stl', 'gltf', 'glb']
    
    @classmethod
    def validate_model_parameters(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate 3D model generation parameters.
        
        Args:
            params: Model parameters to validate
            
        Returns:
            Validated and sanitized parameters
            
        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        
        # Required object type
        validated['object_type'] = InputValidator.validate_enum(
            params.get('object_type'), 'object_type', cls.OBJECT_TYPES
        )
        
        # Geometric parameters
        validated['size'] = InputValidator.validate_numeric(
            params.get('size', 2.0), 'size', min_value=0.1, max_value=10.0
        )
        
        # Position parameters
        validated['pos_x'] = InputValidator.validate_numeric(
            params.get('pos_x', 0.0), 'pos_x', min_value=-10.0, max_value=10.0
        )
        validated['pos_y'] = InputValidator.validate_numeric(
            params.get('pos_y', 0.0), 'pos_y', min_value=-10.0, max_value=10.0
        )
        validated['pos_z'] = InputValidator.validate_numeric(
            params.get('pos_z', 0.0), 'pos_z', min_value=-10.0, max_value=10.0
        )
        
        # Rotation parameters (degrees)
        validated['rot_x'] = InputValidator.validate_numeric(
            params.get('rot_x', 0), 'rot_x', min_value=-180, max_value=180, numeric_type=int
        )
        validated['rot_y'] = InputValidator.validate_numeric(
            params.get('rot_y', 0), 'rot_y', min_value=-180, max_value=180, numeric_type=int
        )
        validated['rot_z'] = InputValidator.validate_numeric(
            params.get('rot_z', 0), 'rot_z', min_value=-180, max_value=180, numeric_type=int
        )
        
        # Material parameters
        validated['color'] = InputValidator.validate_color(
            params.get('color', '#0080FF'), 'color'
        )
        validated['metallic'] = InputValidator.validate_numeric(
            params.get('metallic', 0.0), 'metallic', min_value=0.0, max_value=1.0
        )
        validated['roughness'] = InputValidator.validate_numeric(
            params.get('roughness', 0.5), 'roughness', min_value=0.0, max_value=1.0
        )
        
        # Optional emission parameters
        if 'emission' in params:
            validated['emission'] = InputValidator.validate_color(
                params['emission'], 'emission'
            )
            validated['emission_strength'] = InputValidator.validate_numeric(
                params.get('emission_strength', 1.0), 'emission_strength',
                min_value=0.0, max_value=10.0
            )
        
        return validated
    
    @classmethod
    def validate_export_parameters(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate model export parameters.
        
        Args:
            params: Export parameters to validate
            
        Returns:
            Validated parameters
            
        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        
        # Required format
        validated['format'] = InputValidator.validate_enum(
            params.get('format'), 'format', cls.EXPORT_FORMATS
        )
        
        # Optional filename
        if 'filename' in params:
            filename = InputValidator.validate_string(
                params['filename'], 'filename', max_length=255
            )
            validated['filename'] = InputValidator.sanitize_filename(filename)
        
        # Format-specific parameters
        if validated['format'] == 'stl':
            validated['ascii'] = InputValidator.validate_boolean(
                params.get('ascii', False), 'ascii'
            )
        
        return validated


class SceneParameterValidator:
    """Specialized validator for scene parameters."""
    
    COMPOSITION_OPERATIONS = ['align', 'distribute', 'arrange']
    ALIGNMENT_AXES = ['x', 'y', 'z']
    ALIGNMENT_MODES = ['left', 'center', 'right', 'top', 'middle', 'bottom']
    ARRANGEMENT_PATTERNS = ['grid', 'circle', 'spiral', 'line']
    
    @classmethod
    def validate_scene_parameters(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate scene creation parameters.
        
        Args:
            params: Scene parameters to validate
            
        Returns:
            Validated parameters
            
        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        
        # Required name and description
        validated['name'] = InputValidator.validate_string(
            params.get('name'), 'name', max_length=InputValidator.MAX_NAME_LENGTH
        )
        validated['description'] = InputValidator.validate_string(
            params.get('description'), 'description',
            max_length=InputValidator.MAX_DESCRIPTION_LENGTH
        )
        
        # Optional scene ID
        if 'scene_id' in params:
            validated['scene_id'] = InputValidator.validate_string(
                params['scene_id'], 'scene_id', max_length=50,
                pattern=r'^[a-zA-Z0-9_-]+$'
            )
        
        return validated
    
    @classmethod
    def validate_composition_parameters(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate scene composition parameters.
        
        Args:
            params: Composition parameters to validate
            
        Returns:
            Validated parameters
            
        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        
        # Required operation
        validated['operation'] = InputValidator.validate_enum(
            params.get('operation'), 'operation', cls.COMPOSITION_OPERATIONS
        )
        
        # Operation-specific parameters
        if validated['operation'] == 'align':
            validated['axis'] = InputValidator.validate_enum(
                params.get('axis'), 'axis', cls.ALIGNMENT_AXES
            )
            validated['mode'] = InputValidator.validate_enum(
                params.get('mode'), 'mode', cls.ALIGNMENT_MODES
            )
        
        elif validated['operation'] == 'distribute':
            validated['axis'] = InputValidator.validate_enum(
                params.get('axis'), 'axis', cls.ALIGNMENT_AXES
            )
            validated['spacing'] = InputValidator.validate_numeric(
                params.get('spacing', 1.0), 'spacing', min_value=0.1, max_value=10.0
            )
        
        elif validated['operation'] == 'arrange':
            validated['pattern'] = InputValidator.validate_enum(
                params.get('pattern'), 'pattern', cls.ARRANGEMENT_PATTERNS
            )
            
            if validated['pattern'] == 'grid':
                validated['rows'] = InputValidator.validate_numeric(
                    params.get('rows', 2), 'rows', min_value=1, max_value=10, numeric_type=int
                )
                validated['columns'] = InputValidator.validate_numeric(
                    params.get('columns', 2), 'columns', min_value=1, max_value=10, numeric_type=int
                )
            
            validated['spacing'] = InputValidator.validate_numeric(
                params.get('spacing', 2.0), 'spacing', min_value=0.5, max_value=10.0
            )
        
        return validated