#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher Test ob INTEGRA funktioniert
"""

print("Teste INTEGRA Installation...")

try:
    # Core testen
    from integra.core import principles
    print("✅ Core Module gefunden")
    
    # Advanced testen
    from integra.advanced import etb
    print("✅ Advanced Module gefunden")
    
    # Einfache Anfrage testen
    from integra.core import decision_engine, profiles
    
    profile = profiles.get_default_profile()
    context = {}
    input_data = {"text": "Hallo INTEGRA!"}
    
    context = decision_engine.run_module(input_data, profile, context)
    
    if context.get("decision_engine_result", {}).get("status") == "success":
        print("✅ Decision Engine funktioniert!")
        print(f"   Pfad: {context['decision_engine_result']['decision']['path']}")
    
    print("\n🎉 INTEGRA ist bereit!")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    print("\nBitte prüfe ob alle Dateien am richtigen Ort sind.")