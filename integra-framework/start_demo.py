#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRA Demo Starter
Einfacher Weg, die Demo zu starten
"""

import sys
import os

# Füge integra zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Jetzt können wir integra importieren
from integra.core import decision_engine, profiles, basic_control
from integra.examples.core_light_demo import run_interactive_demo, run_batch_demo

def main():
    print("=== INTEGRA Light - Interaktive Demo ===")
    print()
    
    # Wähle Demo-Modus
    print("Wählen Sie einen Modus:")
    print("1. Interaktive Demo")
    print("2. Batch-Test")
    print("3. Einzelne Anfrage")
    
    choice = input("\nIhre Wahl (1-3): ").strip()
    
    if choice == "1":
        run_interactive_demo()
    elif choice == "2":
        run_batch_demo()
    elif choice == "3":
        query = input("\nIhre Anfrage: ")
        profile = profiles.get_default_profile()
        context = {}
        
        # Decision Engine
        input_data = {"text": query}
        context = decision_engine.run_module(input_data, profile, context)
        
        # Ergebnis anzeigen
        if context.get("decision_engine_result", {}).get("status") == "success":
            result = context["decision_engine_result"]
            decision = result["decision"]
            
            print(f"\nPfad: {decision['path']}")
            print(f"Konfidenz: {decision['confidence']:.2%}")
            print(f"\nAntwort: {decision['response']}")
    else:
        print("Ungültige Wahl!")

if __name__ == "__main__":
    main()