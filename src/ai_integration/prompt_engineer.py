"""
Prompt engineering for optimized AI interactions in 3D model generation.

This module provides sophisticated prompt templates and optimization strategies
for getting the best results from AI models when generating 3D scenes and objects.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PromptStyle(Enum):
    """Different prompt styles for various use cases."""
    PRECISE = "precise"          # Detailed, technical prompts
    CREATIVE = "creative"        # More open-ended, artistic prompts
    BEGINNER = "beginner"        # Simple, guided prompts
    ARCHITECTURAL = "architectural"  # Focus on structure and engineering
    ARTISTIC = "artistic"        # Focus on aesthetics and composition


@dataclass
class PromptTemplate:
    """Template for AI prompts with context and constraints."""
    name: str
    description: str
    template: str
    style: PromptStyle
    constraints: Dict[str, Any]
    examples: List[str]


class PromptEngineer:
    """Optimizes prompts for AI model generation based on context and user intent."""
    
    def __init__(self):
        """Initialize the prompt engineer with templates and optimization rules."""
        self.templates = self._load_prompt_templates()
        self.optimization_rules = self._load_optimization_rules()
        
        logger.info("Prompt engineer initialized with templates and rules")
    
    def optimize_user_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize user input for better AI understanding.
        
        Args:
            user_input: Raw user description
            context: Additional context (user skill level, previous models, etc.)
            
        Returns:
            Optimized prompt data with context and suggestions
        """
        try:
            # Analyze user input
            analysis = self._analyze_user_input(user_input)
            
            # Determine appropriate style
            style = self._determine_prompt_style(analysis, context)
            
            # Select best template
            template = self._select_template(analysis, style)
            
            # Build optimized prompt
            optimized_prompt = self._build_optimized_prompt(
                user_input, template, analysis, context
            )
            
            return {
                'success': True,
                'original_input': user_input,
                'optimized_prompt': optimized_prompt,
                'style': style.value,
                'template_used': template.name,
                'analysis': analysis,
                'suggestions': self._generate_suggestions(analysis)
            }
            
        except Exception as e:
            logger.error(f"Prompt optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_prompt': self._create_fallback_prompt(user_input)
            }
    
    def enhance_for_scene_generation(self, description: str, complexity: str = "medium") -> str:
        """
        Enhance a description for complex scene generation.
        
        Args:
            description: Base scene description
            complexity: Desired complexity level (simple, medium, complex)
            
        Returns:
            Enhanced prompt for scene generation
        """
        complexity_configs = {
            'simple': {'max_objects': 3, 'detail_level': 'basic'},
            'medium': {'max_objects': 5, 'detail_level': 'moderate'},
            'complex': {'max_objects': 8, 'detail_level': 'detailed'}
        }
        
        config = complexity_configs.get(complexity, complexity_configs['medium'])
        
        enhancement_prompt = f"""
Create a {complexity} 3D scene: "{description}"

Scene requirements:
- Up to {config['max_objects']} objects that work together cohesively
- {config['detail_level']} level of spatial relationships
- Realistic proportions and positioning
- Complementary materials and colors
- Clear compositional hierarchy

Consider:
- Lighting and visual balance
- Functional relationships between objects
- Scale and proportion consistency
- Material realism and variation
"""
        
        return enhancement_prompt
    
    def create_material_prompt(self, object_description: str, style_preferences: Optional[Dict[str, Any]] = None) -> str:
        """
        Create optimized prompt for material suggestions.
        
        Args:
            object_description: Description of the object needing materials
            style_preferences: User preferences for materials
            
        Returns:
            Optimized material prompt
        """
        base_prompt = f"Suggest realistic materials for: {object_description}"
        
        if style_preferences:
            style_notes = []
            
            if style_preferences.get('realistic', True):
                style_notes.append("prioritize physical accuracy")
            
            if style_preferences.get('stylized'):
                style_notes.append("allow stylized interpretations")
            
            if style_preferences.get('color_theme'):
                style_notes.append(f"consider {style_preferences['color_theme']} color scheme")
            
            if style_preferences.get('finish'):
                style_notes.append(f"prefer {style_preferences['finish']} finish")
            
            if style_notes:
                base_prompt += f" ({', '.join(style_notes)})"
        
        return base_prompt
    
    def _analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to understand intent and complexity."""
        analysis = {
            'word_count': len(user_input.split()),
            'complexity': 'simple',
            'intent': 'single_object',
            'keywords': [],
            'object_hints': [],
            'style_hints': [],
            'spatial_hints': [],
            'material_hints': []
        }
        
        # Keyword analysis
        single_object_keywords = ['cube', 'sphere', 'cylinder', 'plane', 'box', 'ball', 'tube', 'disk']
        scene_keywords = ['scene', 'room', 'environment', 'landscape', 'setup', 'arrangement']
        style_keywords = ['modern', 'vintage', 'minimalist', 'ornate', 'industrial', 'organic']
        spatial_keywords = ['next to', 'above', 'below', 'inside', 'around', 'between', 'arranged']
        material_keywords = ['metal', 'wood', 'glass', 'plastic', 'stone', 'ceramic', 'fabric']
        
        text_lower = user_input.lower()
        
        # Check for object type hints
        for keyword in single_object_keywords:
            if keyword in text_lower:
                analysis['object_hints'].append(keyword)
        
        # Check for scene indicators
        for keyword in scene_keywords:
            if keyword in text_lower:
                analysis['intent'] = 'scene'
                analysis['keywords'].append(keyword)
        
        # Check for style indicators
        for keyword in style_keywords:
            if keyword in text_lower:
                analysis['style_hints'].append(keyword)
        
        # Check for spatial relationships
        for keyword in spatial_keywords:
            if keyword in text_lower:
                analysis['spatial_hints'].append(keyword)
                if analysis['intent'] != 'scene':
                    analysis['intent'] = 'multi_object'
        
        # Check for material hints
        for keyword in material_keywords:
            if keyword in text_lower:
                analysis['material_hints'].append(keyword)
        
        # Determine complexity
        if analysis['word_count'] > 20 or len(analysis['spatial_hints']) > 2:
            analysis['complexity'] = 'complex'
        elif analysis['word_count'] > 10 or analysis['spatial_hints']:
            analysis['complexity'] = 'medium'
        
        return analysis
    
    def _determine_prompt_style(self, analysis: Dict[str, Any], context: Optional[Dict[str, Any]]) -> PromptStyle:
        """Determine the best prompt style based on analysis and context."""
        # Default to creative
        style = PromptStyle.CREATIVE
        
        # Check context for user preferences
        if context:
            user_level = context.get('user_level', 'intermediate')
            preferred_style = context.get('preferred_style')
            
            if preferred_style and preferred_style in [s.value for s in PromptStyle]:
                return PromptStyle(preferred_style)
            
            if user_level == 'beginner':
                style = PromptStyle.BEGINNER
            elif user_level == 'expert':
                style = PromptStyle.PRECISE
        
        # Analyze content for style hints
        if any(hint in ['technical', 'precise', 'engineering'] for hint in analysis.get('style_hints', [])):
            style = PromptStyle.PRECISE
        elif any(hint in ['building', 'structure', 'architectural'] for hint in analysis.get('keywords', [])):
            style = PromptStyle.ARCHITECTURAL
        elif any(hint in ['artistic', 'creative', 'aesthetic'] for hint in analysis.get('style_hints', [])):
            style = PromptStyle.ARTISTIC
        
        return style
    
    def _select_template(self, analysis: Dict[str, Any], style: PromptStyle) -> PromptTemplate:
        """Select the best template based on analysis and style."""
        # Filter templates by style and intent
        suitable_templates = [
            t for t in self.templates 
            if t.style == style or style == PromptStyle.CREATIVE
        ]
        
        if not suitable_templates:
            suitable_templates = self.templates
        
        # For now, return the first suitable template
        # In a more sophisticated system, we'd rank templates by suitability
        return suitable_templates[0] if suitable_templates else self._get_default_template()
    
    def _build_optimized_prompt(self, user_input: str, template: PromptTemplate, 
                              analysis: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        """Build an optimized prompt using the selected template."""
        # Start with the base template
        prompt = template.template
        
        # Add user input
        prompt = prompt.replace("{user_description}", user_input)
        
        # Add context-specific enhancements
        if analysis['intent'] == 'scene':
            prompt += "\\n\\nThis appears to be a scene description. Consider multiple objects and their relationships."
        
        if analysis['material_hints']:
            prompt += f"\\n\\nMaterial hints detected: {', '.join(analysis['material_hints'])}"
        
        if analysis['style_hints']:
            prompt += f"\\n\\nStyle preferences: {', '.join(analysis['style_hints'])}"
        
        # Add constraints from template
        if template.constraints:
            constraint_text = self._format_constraints(template.constraints)
            prompt += f"\\n\\nConstraints: {constraint_text}"
        
        return prompt
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on input analysis."""
        suggestions = []
        
        if analysis['complexity'] == 'simple' and not analysis['object_hints']:
            suggestions.append("Consider specifying an object type (cube, sphere, etc.) for more precise results")
        
        if analysis['intent'] == 'scene' and not analysis['spatial_hints']:
            suggestions.append("Add spatial relationships (next to, above, etc.) for better scene composition")
        
        if not analysis['material_hints'] and analysis['word_count'] < 5:
            suggestions.append("Include material descriptions (metal, wood, etc.) for more realistic results")
        
        return suggestions
    
    def _create_fallback_prompt(self, user_input: str) -> str:
        """Create a basic fallback prompt when optimization fails."""
        return f"Create a 3D model based on this description: {user_input}"
    
    def _load_prompt_templates(self) -> List[PromptTemplate]:
        """Load predefined prompt templates."""
        templates = [
            PromptTemplate(
                name="single_object_creative",
                description="Creative prompt for single object generation",
                style=PromptStyle.CREATIVE,
                template="""
Create a 3D model inspired by: "{user_description}"

Interpret this creatively while maintaining realism. Consider:
- The most appropriate primitive shape
- Realistic proportions and materials
- Visual appeal and coherence
- How the object might exist in the real world

Focus on creating something that captures the essence of the description.
""",
                constraints={
                    'max_objects': 1,
                    'realism': 'high',
                    'creativity': 'medium'
                },
                examples=["a mysterious glowing orb", "an ancient stone pillar"]
            ),
            
            PromptTemplate(
                name="scene_composition",
                description="Template for multi-object scene generation",
                style=PromptStyle.CREATIVE,
                template="""
Design a 3D scene: "{user_description}"

Create a cohesive composition with multiple objects that tell a story or serve a purpose.
Consider:
- Spatial relationships and hierarchy
- Visual balance and composition
- Realistic scale and proportions
- Complementary materials and colors
- How objects interact or relate to each other

Build a scene that feels purposeful and visually engaging.
""",
                constraints={
                    'max_objects': 5,
                    'composition': 'required',
                    'relationships': 'important'
                },
                examples=["a cozy reading nook", "a modern office desk setup"]
            ),
            
            PromptTemplate(
                name="precise_technical",
                description="Precise template for technical modeling",
                style=PromptStyle.PRECISE,
                template="""
Generate precise 3D model parameters for: "{user_description}"

Provide exact specifications with:
- Accurate dimensions and proportions
- Realistic material properties
- Precise positioning and orientation
- Technical considerations for functionality

Prioritize accuracy and engineering principles over artistic interpretation.
""",
                constraints={
                    'precision': 'high',
                    'creativity': 'low',
                    'realism': 'maximum'
                },
                examples=["a 2x4 wooden beam", "a standard coffee mug"]
            )
        ]
        
        return templates
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load prompt optimization rules."""
        return {
            'max_prompt_length': 2000,
            'include_examples': True,
            'add_constraints': True,
            'enhance_vague_descriptions': True,
            'provide_alternatives': True
        }
    
    def _get_default_template(self) -> PromptTemplate:
        """Get default template as fallback."""
        return PromptTemplate(
            name="default",
            description="Default fallback template",
            style=PromptStyle.CREATIVE,
            template="Create a 3D model based on: {user_description}",
            constraints={},
            examples=[]
        )
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints for inclusion in prompts."""
        formatted = []
        for key, value in constraints.items():
            formatted.append(f"{key}: {value}")
        return ", ".join(formatted)