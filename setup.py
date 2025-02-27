#!/usr/bin/env python3
"""
Script de configuración para DyslexiLess.
"""

import os
from setuptools import setup, find_packages

# Leer README para la descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Leer requisitos
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Configuración del paquete
setup(
    name="dyslexiless",
    version="1.0.0",
    author="DyslexiLess Team",
    author_email="contact@dyslexiless.org",
    description="Sistema de corrección en tiempo real para personas con dislexia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dyslexiless/dyslexiless",
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: Spanish",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            line.strip()
            for line in open("requirements-dev.txt")
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.22.0",
            "autodoc>=0.5.0"
        ],
    },
    entry_points={
        "console_scripts": [
            "dyslexiless=dyslexiless.run_app:main",
            "dyslexiless-config=dyslexiless.config_window:main",
        ],
        "gui_scripts": [
            "dyslexiless-gui=dyslexiless.improved_gui:main",
        ],
    },
    package_data={
        "dyslexiless": [
            "config/*.json",
            "resources/*",
            "docs/examples/*.py",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Tracker": "https://github.com/dyslexiless/dyslexiless/issues",
        "Documentation": "https://dyslexiless.readthedocs.io/",
        "Source Code": "https://github.com/dyslexiless/dyslexiless",
    },
)
