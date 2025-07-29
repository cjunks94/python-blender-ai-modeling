"""
Claude API client for AI-powered 3D model generation.

This module provides a client interface for interacting with Anthropic's Claude API
to generate 3D model descriptions and Blender scripts from natural language.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Response from AI model generation."""
    success: bool
    content: Optional[str] = None
    model_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None


class AIClient:
    """Client for interacting with Claude API for 3D model generation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize AI client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not available. Install with: pip install anthropic")
        
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        logger.info(f"AI client initialized with model: {model}")
    
    def generate_model_from_description(self, description: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """
        Generate 3D model parameters from natural language description.
        
        Args:
            description: Natural language description of the desired 3D model
            context: Optional context for the generation (style, constraints, etc.)
            
        Returns:
            AIResponse with model generation results
        """
        try:
            # Build the prompt for model generation
            prompt = self._build_model_generation_prompt(description, context)
            
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            response_content = message.content[0].text
            
            # Extract JSON from response
            model_data = self._extract_json_from_response(response_content)
            
            if model_data:
                return AIResponse(
                    success=True,
                    content=response_content,
                    model_data=model_data,
                    usage={
                        "input_tokens": message.usage.input_tokens,
                        "output_tokens": message.usage.output_tokens
                    }
                )
            else:
                return AIResponse(
                    success=False,
                    error_message="Failed to parse model data from AI response"
                )
                
        except Exception as e:
            logger.error(f"AI model generation failed: {str(e)}")
            return AIResponse(
                success=False,
                error_message=f"AI generation error: {str(e)}"
            )
    
    def generate_complex_scene(self, description: str, max_objects: int = 5) -> AIResponse:
        """
        Generate a complex scene with multiple objects.
        
        Args:
            description: Description of the scene to create
            max_objects: Maximum number of objects in the scene
            
        Returns:
            AIResponse with scene generation results
        """
        try:
            prompt = self._build_scene_generation_prompt(description, max_objects)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.4,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            response_content = message.content[0].text
            scene_data = self._extract_json_from_response(response_content)
            
            if scene_data:
                return AIResponse(
                    success=True,
                    content=response_content,
                    model_data=scene_data,
                    usage={
                        "input_tokens": message.usage.input_tokens,
                        "output_tokens": message.usage.output_tokens
                    }
                )
            else:
                return AIResponse(
                    success=False,
                    error_message="Failed to parse scene data from AI response"
                )
                
        except Exception as e:
            logger.error(f"AI scene generation failed: {str(e)}")
            return AIResponse(
                success=False,
                error_message=f"Scene generation error: {str(e)}"
            )
    
    def suggest_materials(self, object_type: str, description: str) -> AIResponse:
        """
        Get AI suggestions for materials based on object type and description.
        
        Args:
            object_type: Type of object (cube, sphere, etc.)
            description: Description of the desired appearance
            
        Returns:
            AIResponse with material suggestions
        """
        try:
            prompt = self._build_material_suggestion_prompt(object_type, description)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.5,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_content = message.content[0].text
            material_data = self._extract_json_from_response(response_content)
            
            if material_data:
                return AIResponse(
                    success=True,
                    content=response_content,
                    model_data=material_data,
                    usage={
                        "input_tokens": message.usage.input_tokens,
                        "output_tokens": message.usage.output_tokens
                    }
                )
            else:
                return AIResponse(
                    success=False,
                    error_message="Failed to parse material suggestions from AI response"
                )
                
        except Exception as e:
            logger.error(f"AI material suggestion failed: {str(e)}")
            return AIResponse(
                success=False,
                error_message=f"Material suggestion error: {str(e)}"
            )
    
    def _build_model_generation_prompt(self, description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for single model generation."""
        base_prompt = f"""
You are an expert 3D modeling assistant. Generate parameters for a 3D model based on this description: "{description}"

Available object types: cube, sphere, cylinder, plane

Respond with a JSON object containing these parameters:
{{
    "object_type": "cube|sphere|cylinder|plane",
    "size": 2.0,
    "position": {{"x": 0.0, "y": 0.0, "z": 0.0}},
    "rotation": {{"x": 0, "y": 0, "z": 0}},
    "material": {{
        "color": "#RRGGBB",
        "metallic": 0.0-1.0,
        "roughness": 0.0-1.0,
        "emission": "#RRGGBB" (optional),
        "emission_strength": 0.0-10.0 (optional)
    }},
    "reasoning": "Brief explanation of choices"
}}

Guidelines:
- Choose the most appropriate primitive for the description
- Size should be 0.5-5.0 units
- Position coordinates should be -10 to 10
- Rotation in degrees (-180 to 180)
- Use realistic colors and material properties
- For metallic objects: higher metallic (0.7-1.0), lower roughness (0.0-0.3)
- For non-metallic: lower metallic (0.0-0.2), higher roughness (0.3-1.0)
"""
        
        if context:
            base_prompt += f"\\nAdditional context: {json.dumps(context)}"
        
        base_prompt += "\\nRespond only with the JSON object, no other text."
        
        return base_prompt
    
    def _build_scene_generation_prompt(self, description: str, max_objects: int) -> str:
        """Build prompt for complex scene generation."""
        return f"""
You are an expert 3D scene designer. Create a scene with multiple objects based on: "{description}"

Generate up to {max_objects} objects that work together to create the described scene.

Respond with a JSON object:
{{
    "scene_name": "Brief scene name",
    "description": "Scene description",
    "objects": [
        {{
            "name": "object1",
            "object_type": "cube|sphere|cylinder|plane",
            "size": 2.0,
            "position": {{"x": 0.0, "y": 0.0, "z": 0.0}},
            "rotation": {{"x": 0, "y": 0, "z": 0}},
            "material": {{
                "color": "#RRGGBB",
                "metallic": 0.0-1.0,
                "roughness": 0.0-1.0,
                "emission": "#RRGGBB" (optional),
                "emission_strength": 0.0-10.0 (optional)
            }}
        }}
    ],
    "composition_notes": "How objects relate to each other"
}}

Guidelines:
- Arrange objects in meaningful spatial relationships
- Vary sizes and positions to create visual interest
- Use complementary colors and materials
- Consider the scene's purpose or story
- Objects should not overlap (check positions)

Respond only with the JSON object.
"""
    
    def _build_material_suggestion_prompt(self, object_type: str, description: str) -> str:
        """Build prompt for material suggestions."""
        return f"""
Suggest realistic materials for a {object_type} that should look like: "{description}"

Respond with a JSON object:
{{
    "primary_suggestion": {{
        "color": "#RRGGBB",
        "metallic": 0.0-1.0,
        "roughness": 0.0-1.0,
        "emission": "#RRGGBB" (optional),
        "emission_strength": 0.0-10.0 (optional),
        "reasoning": "Why this material fits"
    }},
    "alternatives": [
        {{
            "color": "#RRGGBB",
            "metallic": 0.0-1.0,
            "roughness": 0.0-1.0,
            "name": "Alternative name",
            "reasoning": "Brief explanation"
        }}
    ]
}}

Consider:
- Real-world material properties
- Visual appeal and realism
- How light interacts with the surface

Respond only with the JSON object.
"""
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from AI response."""
        try:
            # Try to find JSON in the response
            import re
            
            # Look for JSON objects
            json_pattern = r'\\{[^{}]*(?:\\{[^{}]*\\}[^{}]*)*\\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            # If no JSON found, try parsing the entire response
            return json.loads(response.strip())
            
        except Exception as e:
            logger.error(f"Failed to extract JSON from response: {e}")
            logger.debug(f"Response content: {response}")
            return None