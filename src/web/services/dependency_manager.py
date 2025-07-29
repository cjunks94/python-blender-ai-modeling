"""
Dependency management service for handling optional imports and service initialization.

This module manages the availability and initialization of optional dependencies
like Blender integration, AI services, and export functionality.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Type
from dataclasses import dataclass

# Add parent directories to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


@dataclass
class ServiceStatus:
    """Status information for a service dependency."""
    available: bool
    error_message: Optional[str] = None
    service_instance: Optional[Any] = None


class DependencyManager:
    """Manages optional dependencies and service initialization."""
    
    def __init__(self):
        """Initialize dependency manager and check service availability."""
        self._services: Dict[str, ServiceStatus] = {}
        self._initialize_services()
    
    def _initialize_services(self) -> None:
        """Initialize all optional services and check their availability."""
        self._init_blender_services()
        self._init_export_services()
        self._init_ai_services()
        self._init_scene_management()
    
    def _init_blender_services(self) -> None:
        """Initialize Blender integration services."""
        try:
            from blender_integration.executor import BlenderExecutor, BlenderExecutionError, BlenderScriptError
            from blender_integration.script_generator import ScriptGenerator, ScriptGenerationError
            from blender_integration.preview_renderer import PreviewRenderer
            
            self._services['blender'] = ServiceStatus(
                available=True,
                service_instance={
                    'executor_class': BlenderExecutor,
                    'generator_class': ScriptGenerator,
                    'renderer_class': PreviewRenderer,
                    'exceptions': {
                        'execution_error': BlenderExecutionError,
                        'script_error': BlenderScriptError,
                        'generation_error': ScriptGenerationError
                    }
                }
            )
            logger.info("Blender integration services initialized successfully")
            
        except ImportError as e:
            self._services['blender'] = ServiceStatus(
                available=False,
                error_message=f"Blender integration not available: {e}"
            )
            logger.warning(f"Blender integration not available: {e}")
    
    def _init_export_services(self) -> None:
        """Initialize export services."""
        try:
            from export.obj_exporter import OBJExporter, ExportError
            from export.gltf_exporter import GLTFExporter
            from export.stl_exporter import STLExporter
            
            self._services['export'] = ServiceStatus(
                available=True,
                service_instance={
                    'obj_exporter': OBJExporter,
                    'gltf_exporter': GLTFExporter,
                    'stl_exporter': STLExporter,
                    'export_error': ExportError
                }
            )
            logger.info("Export services initialized successfully")
            
        except ImportError as e:
            self._services['export'] = ServiceStatus(
                available=False,
                error_message=f"Export functionality not available: {e}"
            )
            logger.warning(f"Export functionality not available: {e}")
    
    def _init_ai_services(self) -> None:
        """Initialize AI integration services."""
        try:
            from ai_integration.ai_client import AIClient
            from ai_integration.model_interpreter import ModelInterpreter
            from ai_integration.prompt_engineer import PromptEngineer
            from ai_integration.script_validator import ScriptValidator
            
            self._services['ai'] = ServiceStatus(
                available=True,
                service_instance={
                    'client_class': AIClient,
                    'interpreter_class': ModelInterpreter,
                    'engineer_class': PromptEngineer,
                    'validator_class': ScriptValidator
                }
            )
            logger.info("AI integration services initialized successfully")
            
        except ImportError as e:
            self._services['ai'] = ServiceStatus(
                available=False,
                error_message=f"AI integration not available: {e}"
            )
            logger.warning(f"AI integration not available: {e}")
    
    def _init_scene_management(self) -> None:
        """Initialize scene management services."""
        try:
            from scene_management.scene_manager import SceneManager
            from scene_management.scene_validator import SceneValidator
            
            # Try to import optional scene services
            scene_services = {
                'manager_class': SceneManager,
                'validator_class': SceneValidator
            }
            
            # Optional scene preview renderer
            try:
                from blender_integration.composite_renderer import CompositeRenderer
                scene_services['preview_renderer'] = CompositeRenderer
            except ImportError:
                logger.info("Scene preview renderer not available")
            
            # Optional scene exporter
            try:
                from export.scene_exporter import SceneExporter
                scene_services['scene_exporter'] = SceneExporter
            except ImportError:
                logger.info("Scene exporter not available")
            
            self._services['scene_management'] = ServiceStatus(
                available=True,
                service_instance=scene_services
            )
            logger.info("Scene management services initialized successfully")
            
        except ImportError as e:
            self._services['scene_management'] = ServiceStatus(
                available=False,
                error_message=f"Scene management not available: {e}"
            )
            logger.warning(f"Scene management not available: {e}")
    
    def is_available(self, service_name: str) -> bool:
        """Check if a service is available."""
        service = self._services.get(service_name)
        return service is not None and service.available
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get service instance if available."""
        service = self._services.get(service_name)
        if service and service.available:
            return service.service_instance
        return None
    
    def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """Get detailed service status."""
        return self._services.get(service_name)
    
    def get_all_statuses(self) -> Dict[str, bool]:
        """Get availability status for all services."""
        return {
            name: status.available 
            for name, status in self._services.items()
        }
    
    def get_health_check(self) -> Dict[str, Any]:
        """Get comprehensive health check information."""
        return {
            'status': 'healthy',
            'version': '0.1.0',
            'blender_available': self.is_available('blender'),
            'export_available': self.is_available('export'),
            'ai_available': self.is_available('ai'),
            'scene_management_available': self.is_available('scene_management'),
            'scene_preview_available': self.is_available('scene_management') and 
                                     self.get_service('scene_management') and 
                                     'preview_renderer' in self.get_service('scene_management'),
            'scene_export_available': self.is_available('scene_management') and 
                                    self.get_service('scene_management') and 
                                    'scene_exporter' in self.get_service('scene_management')
        }


# Global dependency manager instance
dependency_manager = DependencyManager()