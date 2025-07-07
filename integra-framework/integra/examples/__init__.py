# -*- coding: utf-8 -*-
"""
INTEGRA Examples - Beispiele und Demos

Diese Sammlung zeigt wie INTEGRA in verschiedenen Szenarien verwendet wird:
- core_light_demo: Demonstration aller Core Light Module
- light_modular_demo: Beispiele für Advanced Layer
- standard_demo: Standard INTEGRA Anwendungsfall
- full_demo: Vollständige INTEGRA 4.2 Demonstration
- use_cases: Realistische Anwendungsszenarien

Jedes Beispiel ist eigenständig und direkt ausführbar.
"""

EXAMPLES_VERSION = "1.0"
AVAILABLE_EXAMPLES = [
    "core_light_demo",      # ✅ Wird als nächstes erstellt
    "light_modular_demo",   # 📋 Für Advanced Layer
    "standard_demo",        # 📋 Für Standard Version
    "full_demo",           # 📋 Für Full Version
    "use_cases"            # 📋 Realistische Szenarien
]

# Verfügbare Demos werden hier importiert:
# from .core_light_demo import run_core_demo
# from .light_modular_demo import run_modular_demo
# from .standard_demo import run_standard_demo
# from .full_demo import run_full_demo
# from .use_cases import run_use_case_demos

__all__ = []  # Wird erweitert wenn Beispiele implementiert sind

def get_available_examples():
    """Gibt verfügbare Beispiele zurück."""
    return AVAILABLE_EXAMPLES.copy()

def is_example_available(example_name: str) -> bool:
    """Prüft ob ein Beispiel verfügbar ist."""
    # Aktuell nur Platzhalter
    available = []  # Wird erweitert: ["core_light_demo"]
    return example_name in available

def get_example_descriptions():
    """Gibt Beschreibungen der Beispiele zurück."""
    descriptions = {
        "core_light_demo": "Vollständige Demonstration aller Core Light Module mit realistischen Szenarien",
        "light_modular_demo": "Zeigt erweiterte Funktionen wie Lernen und Auditierung",
        "standard_demo": "Standard INTEGRA Arbeitsablauf für typische Anwendungen",
        "full_demo": "Demonstriert komplette INTEGRA 4.2 Funktionalität",
        "use_cases": "Sammlung realistischer Anwendungsszenarien aus verschiedenen Bereichen"
    }
    return descriptions

def run_all_available_demos():
    """Führt alle verfügbaren Demos aus."""
    print("=== INTEGRA Beispiel-Sammlung ===")
    print(f"Examples Version: {EXAMPLES_VERSION}")
    print()
    
    available_count = 0
    descriptions = get_example_descriptions()
    
    for example in AVAILABLE_EXAMPLES:
        status = "✅" if is_example_available(example) else "📋"
        print(f"{status} {example}")
        print(f"   {descriptions[example]}")
        
        if is_example_available(example):
            available_count += 1
            print(f"   → Führe {example} aus...")
            # Hier würden die Demos ausgeführt werden
        else:
            print(f"   → Noch nicht implementiert")
        print()
    
    print(f"Verfügbare Demos: {available_count}/{len(AVAILABLE_EXAMPLES)}")

def demo():
    """Zeigt Übersicht über verfügbare Beispiele."""
    print("=== INTEGRA Examples Übersicht ===")
    print(f"Version: {EXAMPLES_VERSION}")
    print()
    
    descriptions = get_example_descriptions()
    print("Verfügbare Beispiele:")
    for example in AVAILABLE_EXAMPLES:
        status = "✅" if is_example_available(example) else "📋"
        print(f"  {status} {example}: {descriptions[example]}")
    
    print()
    print("Um ein Beispiel auszuführen:")
    print("  python -m integra.examples.core_light_demo")
    print("  python -m integra.examples.use_cases")