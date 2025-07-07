#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRA Light - Ethisches KI-Entscheidungssystem
Haupteinstiegspunkt für das System

Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

from integra.core import decision_engine, profiles, basic_control
from integra.examples.core_light_demo import run_interactive_demo, run_batch_demo


def main():
    """Hauptfunktion für INTEGRA."""
    parser = argparse.ArgumentParser(
        description="INTEGRA Light - Ethisches KI-Entscheidungssystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python main.py --demo              # Startet interaktive Demo
  python main.py --batch             # Führt Batch-Tests durch
  python main.py "Soll ich helfen?"  # Einzelne Anfrage
  python main.py --profile strict "Darf ich lügen?"  # Mit speziellem Profil
        """
    )
    
    # Argumente definieren
    parser.add_argument(
        "query",
        nargs="?",
        help="Direkte Anfrage an INTEGRA"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Startet die interaktive Demo"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Führt vordefinierte Batch-Tests durch"
    )
    
    parser.add_argument(
        "--profile",
        choices=["default", "strict", "supportive", "conservative"],
        default="default",
        help="Wählt ein ethisches Profil (default: %(default)s)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Zeigt detaillierte Ausgaben"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="INTEGRA Light v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Modus bestimmen
    if args.demo:
        print("=== INTEGRA Light - Interaktive Demo ===")
        print()
        run_interactive_demo(verbose=args.verbose)
        
    elif args.batch:
        print("=== INTEGRA Light - Batch-Test-Modus ===")
        print()
        run_batch_demo(profile_name=args.profile, verbose=args.verbose)
        
    elif args.query:
        # Einzelne Anfrage verarbeiten
        print("=== INTEGRA Light - Einzelanfrage ===")
        print()
        process_single_query(args.query, args.profile, args.verbose)
        
    else:
        # Keine Argumente - zeige Hilfe
        parser.print_help()


def process_single_query(query: str, profile_name: str = "default", verbose: bool = False):
    """
    Verarbeitet eine einzelne Anfrage.
    
    Args:
        query: Die Benutzeranfrage
        profile_name: Name des zu verwendenden Profils
        verbose: Ob detaillierte Ausgaben gezeigt werden sollen
    """
    # Profil laden
    profile = profiles.get_profile_by_name(profile_name)
    if not profile:
        print(f"Fehler: Profil '{profile_name}' nicht gefunden. Verwende Standard.")
        profile = profiles.get_default_profile()
    else:
        profile = profile.weights
        
    # Context initialisieren
    context = {}
    
    # Decision Engine ausführen
    input_data = {"text": query}
    context = decision_engine.run_module(input_data, profile, context)
    
    # Ergebnis anzeigen
    if context.get("decision_engine_result", {}).get("status") == "success":
        result = context["decision_engine_result"]
        decision = result["decision"]
        
        print(f"Anfrage: {query}")
        print(f"Profil: {profile_name}")
        print("-" * 60)
        
        print(f"Entscheidungspfad: {decision['path']}")
        print(f"Konfidenz: {decision['confidence']:.2%}")
        
        if verbose:
            print("\nAnalyse:")
            analysis = decision.get("analysis", {})
            print(f"  Fragetyp: {analysis.get('question_type', 'unbekannt')}")
            print(f"  Risiko-Score: {analysis.get('risk_score', 0):.2f}")
            print(f"  Ethische Trigger: {len(analysis.get('triggered_ethics', []))}")
            
            if decision['path'] == 'deep' and 'ethics' in decision:
                print("\nEthische Bewertung:")
                ethics = decision['ethics']
                print(f"  Gesamt-Score: {ethics.get('overall_score', 0):.2f}")
                
                if 'violations' in ethics and ethics['violations']:
                    print(f"  Verletzungen: {', '.join(ethics['violations'])}")
                    
        print("\nAntwort:")
        print(decision.get('response', 'Keine Antwort generiert'))
        
        # Basic Control prüfen
        control_input = {"text": query, "user_role": "user"}
        context = basic_control.run_module(control_input, profile, context)
        
        if context.get("basic_control_result", {}).get("status") == "success":
            control_result = context["basic_control_result"]["control_decision"]
            if control_result["action"] != "pass":
                print(f"\n⚠️  Kontroll-Intervention: {control_result['action']}")
                print(f"   {control_result['message']}")
                
    else:
        print(f"Fehler bei der Verarbeitung: {context.get('decision_engine_result', {}).get('error', 'Unbekannt')}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgramm durch Benutzer beendet.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFehler: {e}")
        sys.exit(1)