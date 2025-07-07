# -*- coding: utf-8 -*-
"""
Command Line Interface für INTEGRA
Einfache Konsolen-Schnittstelle
"""

import argparse
from integra.core import decision_engine, profiles

def main():
    parser = argparse.ArgumentParser(description='INTEGRA CLI')
    parser.add_argument('query', help='Ihre Anfrage an INTEGRA')
    parser.add_argument('--profile', default='default', 
                       choices=['default', 'strict', 'supportive', 'conservative'])
    
    args = parser.parse_args()
    
    # Verarbeite Anfrage
    profile = profiles.get_profile_by_name(args.profile)
    if profile:
        profile_weights = profile.weights
    else:
        profile_weights = profiles.get_default_profile()
    
    context = {}
    input_data = {"text": args.query}
    context = decision_engine.run_module(input_data, profile_weights, context)
    
    # Zeige Ergebnis
    if context.get("decision_engine_result", {}).get("status") == "success":
        result = context["decision_engine_result"]["decision"]
        print(f"\nPfad: {result['path']}")
        print(f"Konfidenz: {result['confidence']:.0%}")
        print(f"\nAntwort: {result['response']}")

if __name__ == "__main__":
    main()