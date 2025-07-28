#!/usr/bin/env python3
"""Setup script for Python Blender AI Modeling application."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="python-blender-ai-modeling",
    version="0.1.0",
    author="AI Assistant",
    author_email="assistant@anthropic.com",
    description="Desktop app for creating 3D models using Blender programmatically with AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cjunker/python-blender-ai-modeling",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        "ai": [
            "anthropic>=0.7.0",
            "openai>=1.0.0",
            "python-dotenv>=1.0.0",
        ],
        "advanced-ui": [
            "PyQt6>=6.5.0",
        ],
        "export": [
            "Pillow>=10.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
            "pip-audit>=2.6.0",
            "pre-commit>=3.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "blender-ai-modeling=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)