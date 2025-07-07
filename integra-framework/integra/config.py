# -*- coding: utf-8 -*-
"""
INTEGRA Light - Zentrale Konfiguration
"""

from pathlib import Path
from typing import Dict, Any

# ============================================================================
# PFADE - AUTOMATISCH ERKANNT
# ============================================================================

# Findet automatisch wo das Projekt liegt
BASE_DIR = Path(__file__).parent

# Unterverzeichnisse
CORE_DIR = BASE_DIR / "core"
ADVANCED_DIR = BASE_DIR / "advanced"
FULL_DIR = BASE_DIR / "full"
LOGS_DIR = BASE_DIR / "logs"
PROFILES_DIR = BASE_DIR / "profiles"

# Erstelle Verzeichnisse wenn nicht vorhanden
for directory in [LOGS_DIR, PROFILES_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# EINFACHE EINSTELLUNGEN
# ============================================================================

VERSION = "1.0.0"
DEBUG = False  # Auf True für mehr Infos bei Fehlern

# ============================================================================
# WICHTIGE FUNKTION DIE GEFEHLT HAT
# ============================================================================

def get_config() -> Dict[str, Any]:
    """Gibt die Konfiguration zurück."""
    return {
        "version": VERSION,
        "debug": DEBUG,
        "paths": {
            "base": str(BASE_DIR),
            "logs": str(LOGS_DIR),
            "profiles": str(PROFILES_DIR)
        }
    }