#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfache INTEGRA Demo - Zeigt die Grundfunktionen
"""

from integra.core import decision_engine, profiles, simple_ethics

def teste_anfrage(text):
    """Testet eine einzelne Anfrage."""
    print(f"\n🤔 Anfrage: '{text}'")
    print("-" * 50)
    
    # Profil laden
    profile = profiles.get_default_profile()
    context = {}
    
    # Decision Engine
    input_data = {"text": text}
    context = decision_engine.run_module(input_data, profile, context)
    
    if context.get("decision_engine_result", {}).get("status") == "success":
        result = context["decision_engine_result"]["decision"]
        
        print(f"✅ Pfad: {result['path']}")
        print(f"📊 Konfidenz: {result['confidence']:.0%}")
        
        # Bei Deep Path mehr Details
        if result['path'] == 'deep' and 'ethics' in result:
            ethics = result['ethics']
            print(f"⚖️  Ethik-Score: {ethics.get('overall_score', 0):.2f}")
            if ethics.get('violations'):
                print(f"⚠️  Verletzungen: {', '.join(ethics['violations'])}")
        
        print(f"\n💬 Antwort: {result['response']}")

def main():
    print("=== INTEGRA Einfache Demo ===")
    print("Teste verschiedene Anfragen...\n")
    
    # Verschiedene Test-Anfragen
    test_anfragen = [
        "Wie spät ist es?",
        "Soll ich jemandem helfen?",
        "Darf ich lügen?",
        "Wie kann ich beim Lernen unterstützen?",
        "Ist es ok, private Daten zu nutzen?"
    ]
    
    for anfrage in test_anfragen:
        teste_anfrage(anfrage)
        input("\n[Enter für nächste Anfrage...]")
    
    print("\n✅ Demo abgeschlossen!")

if __name__ == "__main__":
    main()