"""
Tests for the PromptEngineer class additions.

This module tests the newly added methods to the PromptEngineer class
that were implemented to fix missing functionality.
"""

import unittest
from unittest.mock import patch
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_integration.prompt_engineer import PromptEngineer


class TestPromptEngineerAdditions(unittest.TestCase):
    """Test cases for newly added PromptEngineer methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.prompt_engineer = PromptEngineer()
    
    def test_create_model_prompt_basic(self):
        """Test basic model prompt creation."""
        prompt = self.prompt_engineer.create_model_prompt(
            description="Create a red cube",
            style="realistic",
            complexity="medium",
            user_level="beginner"
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn("red cube", prompt.lower())
        self.assertIn("realistic", prompt.lower())
        self.assertIn("medium", prompt.lower())
        self.assertIn("beginner", prompt.lower())
    
    def test_create_model_prompt_with_defaults(self):
        """Test model prompt creation with default parameters."""
        prompt = self.prompt_engineer.create_model_prompt("Create a blue sphere")
        
        self.assertIsInstance(prompt, str)
        self.assertIn("blue sphere", prompt.lower())
        # Should contain default values
        self.assertIn("realistic", prompt.lower())
        self.assertIn("medium", prompt.lower())
        self.assertIn("beginner", prompt.lower())
    
    def test_create_model_prompt_different_styles(self):
        """Test model prompt creation with different styles."""
        styles = ["realistic", "cartoon", "abstract", "minimalist"]
        
        for style in styles:
            prompt = self.prompt_engineer.create_model_prompt(
                description="Create a cube",
                style=style
            )
            self.assertIn(style, prompt.lower())
    
    def test_create_model_prompt_different_complexities(self):
        """Test model prompt creation with different complexity levels."""
        complexities = ["simple", "medium", "complex"]
        
        for complexity in complexities:
            prompt = self.prompt_engineer.create_model_prompt(
                description="Create a cube",
                complexity=complexity
            )
            self.assertIn(complexity, prompt.lower())
    
    def test_create_model_prompt_different_user_levels(self):
        """Test model prompt creation with different user levels."""
        user_levels = ["beginner", "intermediate", "advanced"]
        
        for user_level in user_levels:
            prompt = self.prompt_engineer.create_model_prompt(
                description="Create a cube",
                user_level=user_level
            )
            self.assertIn(user_level, prompt.lower())
    
    def test_create_scene_prompt_basic(self):
        """Test basic scene prompt creation."""
        prompt = self.prompt_engineer.create_scene_prompt(
            description="Create a living room",
            max_objects=5,
            complexity="medium"
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn("living room", prompt.lower())
        self.assertIn("5", prompt)
        self.assertIn("medium", prompt.lower())
    
    def test_create_scene_prompt_with_defaults(self):
        """Test scene prompt creation with default parameters."""
        prompt = self.prompt_engineer.create_scene_prompt("Create a kitchen")
        
        self.assertIsInstance(prompt, str)
        self.assertIn("kitchen", prompt.lower())
        # Should contain default values
        self.assertIn("5", prompt)  # Default max_objects
        self.assertIn("medium", prompt.lower())  # Default complexity
    
    def test_create_scene_prompt_different_object_counts(self):
        """Test scene prompt creation with different object counts."""
        object_counts = [1, 3, 5, 8, 10]
        
        for count in object_counts:
            prompt = self.prompt_engineer.create_scene_prompt(
                description="Create a room",
                max_objects=count
            )
            self.assertIn(str(count), prompt)
    
    def test_create_scene_prompt_different_complexities(self):
        """Test scene prompt creation with different complexity levels."""
        complexities = ["simple", "medium", "complex"]
        
        for complexity in complexities:
            prompt = self.prompt_engineer.create_scene_prompt(
                description="Create a room",
                complexity=complexity
            )
            self.assertIn(complexity, prompt.lower())
    
    def test_create_model_prompt_structure(self):
        """Test that model prompts have the expected structure."""
        prompt = self.prompt_engineer.create_model_prompt("Create a green cylinder")
        
        # Should contain key instructions for AI
        expected_elements = [
            "blender",
            "python",
            "bpy",
            "3d model",
            "parameters"
        ]
        
        prompt_lower = prompt.lower()
        for element in expected_elements:
            self.assertIn(element, prompt_lower, 
                         f"Expected '{element}' to be in prompt")
    
    def test_create_scene_prompt_structure(self):
        """Test that scene prompts have the expected structure."""
        prompt = self.prompt_engineer.create_scene_prompt("Create an office scene")
        
        # Should contain key instructions for scene generation
        expected_elements = [
            "scene",
            "objects",
            "spatial",
            "relationships",
            "position"
        ]
        
        prompt_lower = prompt.lower()
        for element in expected_elements:
            self.assertIn(element, prompt_lower,
                         f"Expected '{element}' to be in scene prompt")
    
    def test_prompt_length_reasonable(self):
        """Test that generated prompts have reasonable length."""
        model_prompt = self.prompt_engineer.create_model_prompt("Create a cube")
        scene_prompt = self.prompt_engineer.create_scene_prompt("Create a room")
        
        # Prompts should be substantial but not excessively long
        self.assertGreater(len(model_prompt), 100, "Model prompt too short")
        self.assertLess(len(model_prompt), 2000, "Model prompt too long")
        
        self.assertGreater(len(scene_prompt), 100, "Scene prompt too short")
        self.assertLess(len(scene_prompt), 2000, "Scene prompt too long")
    
    def test_prompt_safety_considerations(self):
        """Test that prompts include safety considerations."""
        model_prompt = self.prompt_engineer.create_model_prompt("Create a cube")
        scene_prompt = self.prompt_engineer.create_scene_prompt("Create a room")
        
        # Should include safety instructions
        safety_keywords = ["safe", "valid", "secure", "appropriate"]
        
        model_lower = model_prompt.lower()
        scene_lower = scene_prompt.lower()
        
        # At least one safety keyword should appear in each prompt
        model_has_safety = any(keyword in model_lower for keyword in safety_keywords)
        scene_has_safety = any(keyword in scene_lower for keyword in safety_keywords)
        
        self.assertTrue(model_has_safety, "Model prompt lacks safety considerations")
        self.assertTrue(scene_has_safety, "Scene prompt lacks safety considerations")
    
    def test_parameter_validation(self):
        """Test parameter validation in prompt methods."""
        # Test with empty description
        with self.assertRaises((ValueError, TypeError)):
            self.prompt_engineer.create_model_prompt("")
        
        with self.assertRaises((ValueError, TypeError)):
            self.prompt_engineer.create_scene_prompt("")
        
        # Test with None description
        with self.assertRaises((ValueError, TypeError)):
            self.prompt_engineer.create_model_prompt(None)
        
        with self.assertRaises((ValueError, TypeError)):
            self.prompt_engineer.create_scene_prompt(None)
    
    def test_prompt_consistency(self):
        """Test that the same inputs produce consistent prompts."""
        description = "Create a red cube"
        
        prompt1 = self.prompt_engineer.create_model_prompt(description)
        prompt2 = self.prompt_engineer.create_model_prompt(description)
        
        # Should be identical for same inputs
        self.assertEqual(prompt1, prompt2)
        
        # Same for scene prompts
        scene_description = "Create a bedroom"
        scene_prompt1 = self.prompt_engineer.create_scene_prompt(scene_description)
        scene_prompt2 = self.prompt_engineer.create_scene_prompt(scene_description)
        
        self.assertEqual(scene_prompt1, scene_prompt2)
    
    def test_prompt_customization(self):
        """Test that different parameters produce different prompts."""
        base_description = "Create a cube"
        
        # Different styles should produce different prompts
        realistic_prompt = self.prompt_engineer.create_model_prompt(base_description, style="realistic")
        cartoon_prompt = self.prompt_engineer.create_model_prompt(base_description, style="cartoon")
        
        self.assertNotEqual(realistic_prompt, cartoon_prompt)
        
        # Different complexities should produce different prompts
        simple_prompt = self.prompt_engineer.create_model_prompt(base_description, complexity="simple")
        complex_prompt = self.prompt_engineer.create_model_prompt(base_description, complexity="complex")
        
        self.assertNotEqual(simple_prompt, complex_prompt)


if __name__ == '__main__':
    unittest.main()