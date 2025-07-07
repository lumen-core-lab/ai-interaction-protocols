# -*- coding: utf-8 -*-
"""
INTEGRA Interfaces - Benutzeroberflächen und Schnittstellen

Diese Schicht stellt verschiedene Wege zur Verfügung, um mit INTEGRA zu interagieren:
- cli: Kommandozeilen-Interface (REPL)
- web: Web-Interface (geplant)
- api: REST API (geplant) 
- gui: Grafische Benutzeroberfläche (geplant)

Aktuell implementiert: Noch keine (für zukünftige Entwicklung vorbereitet)
"""

INTERFACES_VERSION = "1.0-planned"
PLANNED_INTERFACES = [
    "cli",     # Command Line Interface / REPL
    "web",     # Web Interface (HTML/JS)
    "api",     # REST API
    "gui"      # Desktop GUI
]

# Zukünftige Imports (wenn implementiert):
# from .cli import CommandLineInterface, start_repl
# from .web import WebInterface
# from .api import APIServer
# from .gui import GraphicalInterface

__all__ = []  # Wird erweitert wenn Interfaces implementiert sind

def get_planned_interfaces():
    """Gibt geplante Schnittstellen zurück."""
    return PLANNED_INTERFACES.copy()

def is_interface_available(interface_name: str) -> bool:
    """Prüft ob eine Schnittstelle verfügbar ist."""
    # Aktuell noch keine implementiert
    return False

def get_interface_descriptions():
    """Gibt Beschreibungen der geplanten Interfaces zurück."""
    descriptions = {
        "cli": "Kommandozeilen-Interface für interaktive Nutzung und Scripting",
        "web": "Web-basierte Benutzeroberfläche für Browser-Zugriff",
        "api": "REST API für Integration in andere Anwendungen",
        "gui": "Desktop-Anwendung mit grafischer Benutzeroberfläche"
    }
    return descriptions

def demo():
    """Info über geplante Interfaces."""
    print("=== INTEGRA Interfaces (Geplant) ===")
    print(f"Version: {INTERFACES_VERSION}")
    print()
    
    print("Geplante Benutzeroberflächen:")
    descriptions = get_interface_descriptions()
    for interface in PLANNED_INTERFACES:
        status = "✓" if is_interface_available(interface) else "📋"
        print(f"  {status} {interface}: {descriptions[interface]}")
    
    print()
    print("Aktueller Zugriff auf INTEGRA:")
    print("- Direkt über Python: from integra import DecisionEngine")
    print("- In der Entwicklung: Kommandozeilen-Interface")
    print("- Geplant: Web-Interface für einfache Nutzung")