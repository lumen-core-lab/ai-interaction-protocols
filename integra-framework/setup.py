#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRA Setup Script
Installationsskript für das INTEGRA Framework

Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# README einlesen
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = """
# INTEGRA Light

INTEGRA (Integrated Ethical Governance and Responsible AI) ist ein modulares 
Framework für ethische Entscheidungsfindung in KI-Systemen.

## Features

- Ethische Bewertung basierend auf ALIGN-Prinzipien
- Fast/Deep Path Routing für effiziente Entscheidungen
- Governance und Sicherheitskontrolle
- Modularer, erweiterbarer Aufbau

## Installation

```bash
pip install .
```

## Verwendung

```python
from integra.core import decision_engine, profiles

# Profil laden
profile = profiles.get_default_profile()

# Entscheidung treffen
context = {}
input_data = {"text": "Soll ich jemandem helfen?"}
context = decision_engine.run_module(input_data, profile, context)
```
"""

setup(
    name="integra-light",
    version="1.0.0",
    author="Dominik Knape",
    author_email="",  # Optional
    description="INTEGRA Light - Ethisches KI-Entscheidungsframework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/integra",  # Anpassen
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/integra/issues",
        "Documentation": "https://github.com/yourusername/integra/wiki",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Creative Commons License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Paket-Konfiguration
    package_dir={"": "."},
    packages=find_packages(where=".", exclude=["tests*", "examples*", "docs*"]),
    
    # Python Version
    python_requires=">=3.8",
    
    # Dependencies (Core hat keine externen Dependencies!)
    install_requires=[
        # Keine externen Dependencies für Core
    ],
    
    # Optionale Dependencies für erweiterte Features
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.9",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "advanced": [
            # Für zukünftige Advanced Module
        ],
        "full": [
            # Für zukünftige Full Module
        ],
    },
    
    # Skripte
    entry_points={
        "console_scripts": [
            "integra=integra.main:main",
        ],
    },
    
    # Daten-Dateien
    package_data={
        "integra": [
            "config.py",
            "profiles/*.json",  # Falls Profile gespeichert werden
            "templates/*.txt",  # Falls Templates verwendet werden
        ],
    },
    
    # Weitere Metadaten
    keywords=[
        "ai", "ethics", "governance", "responsible-ai", 
        "decision-making", "alignment", "safety"
    ],
    license="CC BY-SA 4.0",
    include_package_data=True,
    zip_safe=False,
)

# Post-Installation Nachricht
print("""
============================================================
INTEGRA Light wurde erfolgreich installiert!

Starten Sie mit:
  python -m integra --demo
  
Oder in Python:
  from integra.core import decision_engine
  
Dokumentation: https://github.com/yourusername/integra/wiki
============================================================
""")