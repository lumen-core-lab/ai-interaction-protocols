# -*- coding: utf-8 -*-
"""
versions/light.py

🌟 INTEGRA LIGHT - Vollständiges ethisches KI-System 🌟

Der komplette INTEGRA Light Orchestrator - bringt alle Module zusammen.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Versuche, alle benötigten Module zu importieren
try:
    from core.profile_manager import INTEGRAProfileManager
    from modules.ethics.basic_ethics import run_module as run_basic_ethics
    from modules.reasoning.fast_path import INTEGRAFastPath, PathDecision
    from modules.reasoning.deep_path import INTEGRADeepPath
    from modules.learning.mini_learner import run_module as run_mini_learner
    from modules.governance.basic_control import run_module as run_basic_control
    from modules.audit.mini_audit import run_module as run_mini_audit
except ImportError as e:
    # Dieser Block wird nur ausgeführt, wenn die Struktur nicht stimmt.
    # Für den normalen Betrieb sollte der try-Block funktionieren.
    print(f"⚠️ Wichtiger Import-Fehler in light.py: {e}")
    print("Stelle sicher, dass alle Module in den richtigen Ordnern liegen.")
    # Fallback, damit die Datei selbst nicht abstürzt
    INTEGRAProfileManager = lambda: None
    INTEGRAFastPath = lambda: None
    INTEGRADeepPath = lambda: None
    run_basic_ethics = lambda a, b, c: c
    run_mini_learner = lambda a, b, c: c
    run_basic_control = lambda a, b, c: c
    run_mini_audit = lambda a, b, c: c


class INTEGRALight:
    """
    Orchestriert den gesamten ethischen Entscheidungsprozess,
    indem alle Module in der korrekten Reihenfolge aufgerufen werden.
    """
    def __init__(self, domain: str = "general"):
        self.domain = domain
        self.profile_manager = INTEGRAProfileManager()
        self.fast_path_logic = INTEGRAFastPath()
        self.deep_path_logic = INTEGRADeepPath()
        
        # Lade das passende Profil für die Domain
        self.profile = self.profile_manager.get_profile(domain)
        
        print(f"🌟 INTEGRA Light v1.0 initialisiert für Domain: {self.domain}")

    def process_request(self, query: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Die Hauptmethode. Verarbeitet eine Anfrage durch die gesamte Pipeline.
        """
        start_time = datetime.now()
        
        # 1. Initialisiere einen leeren Kontext für diese Anfrage
        context = {
            'input_data': {'text': query, 'user_id': user_id},
            'profile': self.profile.to_dict(),
            'decision': {},
            'modules_executed': []
        }

        # 2. Basis-Ethik-Analyse (Vor-Filter)
        context = run_basic_ethics(context['input_data'], context['profile'], context)
        context['modules_executed'].append('basic_ethics')

        # 3. Pfad-Empfehlung einholen
        path_analysis = self.fast_path_logic.analyze_request(context['input_data'], context['profile'], context)
        context['fast_path_analysis'] = path_analysis.__dict__
        context['modules_executed'].append('fast_path')
        
        # 4. Pfad ausführen
        if path_analysis.recommended_path == PathDecision.FAST_PATH:
            context['decision'] = {
                'response': f"Schnelle Antwort auf: '{query}'",
                'path_taken': 'fast_path',
                'confidence': path_analysis.confidence
            }
        else:
            # Tiefe Analyse durchführen
            deep_analysis = self.deep_path_logic.analyze_request(context['input_data'], context['profile'], context)
            context['deep_path_analysis'] = deep_analysis.__dict__
            context['modules_executed'].append('deep_path')
            context['decision'] = {
                'response': deep_analysis.final_recommendation,
                'path_taken': 'deep_path',
                'confidence': deep_analysis.confidence,
                'ethical_quality': deep_analysis.decision_quality.value
            }
        
        # 5. Governance-Check (z.B. für Overrides)
        context = run_basic_control(context['input_data'], context['profile'], context)
        context['modules_executed'].append('basic_control')

        # 6. Lern-Modul (für Feedback)
        context = run_mini_learner(context['input_data'], context['profile'], context)
        context['modules_executed'].append('mini_learner')

        # 7. Finales Audit
        context = run_mini_audit(context['input_data'], context['profile'], context)
        context['modules_executed'].append('mini_audit')
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        context['response_time_ms'] = round(processing_time, 2)
        
        # Gebe nur das finale Ergebnis zurück
        final_response = context.get('decision', {}).get('response', "Ein Fehler ist aufgetreten.")
        
        print("-" * 20)
        print(f"Anfrage '{query}' verarbeitet.")
        print(f"Pfad: {context['decision'].get('path_taken')}")
        print(f"Antwort: {final_response}")
        print(f"Zeit: {context['response_time_ms']}ms")
        print("-" * 20)
        
        return {
            "response": final_response,
            "path": context['decision'].get('path_taken'),
            "audit_id": context.get('audit_entry_id')
        }