"""
AI integration module for 3D model generation.

This module provides AI-powered features for generating complex 3D models
from natural language descriptions using Claude API.
"""

__version__ = "0.1.0"
__author__ = "Claude Code"

try:
    from .ai_client import AIClient
    from .model_interpreter import ModelInterpreter
    from .prompt_engineer import PromptEngineer
    from .script_validator import ScriptValidator
    
    __all__ = [
        "AIClient",
        "ModelInterpreter", 
        "PromptEngineer",
        "ScriptValidator"
    ]
    
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print(f"Warning: AI integration not available: {e}")