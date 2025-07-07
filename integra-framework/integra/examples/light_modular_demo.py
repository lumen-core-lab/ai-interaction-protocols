# -*- coding: utf-8 -*-
"""
INTEGRA Advanced Modules Demo
Demonstriert die Funktionalität aller Advanced Module

Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Pfad-Setup für Imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integra.core import (
    principles, 
    profiles, 
    simple_ethics, 
    decision_engine, 
    basic_control
)
from integra.advanced import (
    etb,
    pae,
    mini_learner,
    mini_audit
)
from integra.config import get_config


# ============================================================================
# DEMO-SZENARIEN für Advanced Features
# ============================================================================

ADVANCED_TEST_SCENARIOS = [
    {
        "id": "ethical_conflict",
        "name": "Wahrheit vs. Schutz",
        "query": "Soll ich die Wahrheit über eine schmerzhafte Diagnose sagen?",
        "options": [
            {
                "text": "Die volle Wahrheit sofort mitteilen",
                "tags": ["honest", "direct", "transparent"],
                "risks": ["emotional_harm", "shock"],
                "alignment": {"integrity": 1.0, "nurturing": 0.3}
            },
            {
                "text": "Die Wahrheit schonend und schrittweise mitteilen",
                "tags": ["balanced", "caring"],
                "risks": ["delayed_acceptance"],
                "alignment": {"integrity": 0.8, "nurturing": 0.8}
            },
            {
                "text": "Erstmal nur positive Aspekte betonen",
                "tags": ["protective", "gentle"],
                "risks": ["trust_loss", "false_hope"],
                "alignment": {"integrity": 0.4, "nurturing": 0.9}
            }
        ],
        "context_type": "medical",
        "expected_features": ["etb", "pae"]
    },
    {
        "id": "priority_tie",
        "name": "Gleichstand bei Prinzipien",
        "query": "Notfall: Regel brechen um zu helfen?",
        "ethics_scores": {
            "governance": 0.75,
            "nurturing": 0.75,
            "integrity": 0.6,
            "awareness": 0.8,
            "learning": 0.5
        },
        "context_type": "emergency",
        "expected_features": ["pae"]
    },
    {
        "id": "learning_feedback",
        "name": "System-Lernen aus Feedback",
        "query": "War die Empfehlung hilfreich?",
        "feedback": "Das war sehr gut, aber zu kompliziert erklärt",
        "previous_decision": {
            "path": "deep",
            "ethics": {"scores": {"learning": 0.7, "nurturing": 0.8}}
        },
        "expected_features": ["mini_learner", "mini_audit"]
    },
    {
        "id": "audit_trail",
        "name": "Entscheidungs-Audit",
        "query": "Zeige mir die letzten Entscheidungen",
        "audit_request": {
            "action": "search",
            "criteria": {"event_type": "decision"},
            "limit": 5
        },
        "expected_features": ["mini_audit"]
    }
]


# ============================================================================
# DEMO-FUNKTIONEN
# ============================================================================

def print_header(title: str) -> None:
    """Druckt einen formatierten Header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subheader(title: str) -> None:
    """Druckt einen formatierten Subheader."""
    print(f"\n--- {title} ---")


def demonstrate_etb() -> None:
    """Demonstriert den Ethical Tradeoff Balancer."""
    print_header("1. ETB - Ethical Tradeoff Balancer")
    
    print("Der ETB bewertet verschiedene Handlungsoptionen nach ALIGN-Prinzipien")
    print("und findet die beste Balance bei ethischen Konflikten.\n")
    
    # Szenario: Wahrheit vs. Schutz
    scenario = ADVANCED_TEST_SCENARIOS[0]
    print(f"Szenario: {scenario['name']}")
    print(f"Frage: {scenario['query']}\n")
    
    # ETB-Kontext vorbereiten
    context = {
        "context_type": scenario["context_type"],
        "profile": profiles.get_default_profile()
    }
    
    # ETB ausführen
    result = etb.run_module(scenario["options"], context)
    
    if result["success"]:
        print(f"✅ Beste Option: {result['best_option']}")
        print(f"   Score: {result['score']:.2f}")
        print(f"   Konfidenz: {result['confidence']:.2%}")
        
        # Justifikation zeigen
        justification = result["justification"]
        print(f"\n   Begründung: {justification['summary']}")
        
        # Prinzipien-Analyse
        print("\n   Prinzipien-Beiträge:")
        for principle, analysis in justification["principle_analysis"].items():
            contribution = analysis["contribution"]
            if contribution > 0.1:  # Nur relevante zeigen
                print(f"   - {principle.title()}: {contribution:.0%}")
        
        # Matrix zeigen
        print("\n   Bewertungsmatrix:")
        for i, entry in enumerate(result["matrix"][:3], 1):
            print(f"   {i}. {entry['option_text'][:50]}...")
            print(f"      Gesamt-Score: {entry['total_score']:.2f}")
            print(f"      Tags: {', '.join(entry['tags'])}")
    
    print("\n💡 ETB hilft bei komplexen ethischen Abwägungen!")


def demonstrate_pae() -> None:
    """Demonstriert die Priority Anchor Engine."""
    print_header("2. PAE - Priority Anchor Engine")
    
    print("Die PAE löst Gleichstände zwischen ethischen Prinzipien")
    print("basierend auf Kontext, Historie und Prioritätsregeln.\n")
    
    # Szenario: Gleichstand
    scenario = ADVANCED_TEST_SCENARIOS[1]
    print(f"Szenario: {scenario['name']}")
    print(f"Situation: {scenario['query']}\n")
    
    # Scores anzeigen
    scores = scenario["ethics_scores"]
    print("Ethische Scores (Gleichstand):")
    for principle, score in scores.items():
        print(f"   {principle}: {score}")
    
    # PAE-Kontext
    context = {
        "scores": scores,
        "context_type": scenario["context_type"],
        "user_input": scenario["query"],
        "profile": profiles.get_default_profile()
    }
    
    # PAE ausführen
    result = pae.run_module("", context)
    
    if result["success"]:
        print(f"\n✅ Gewähltes Prinzip: {result['chosen_principle'].title()}")
        print(f"   Zweitplatziert: {result['runner_up'].title() if result['runner_up'] else 'N/A'}")
        print(f"   Methode: {result['method_used']}")
        print(f"   Konfidenz: {result['confidence']:.2%}")
        print(f"   Begründung: {result['reasoning']}")
        
        # Gleichstandsgruppen zeigen
        if result["tie_detected"]:
            print(f"\n   Gleichstände erkannt: {result['tie_count']}")
            for group in result["meta"]["tie_groups"]:
                print(f"   - {', '.join(group['principles'])} (Score: {group['score']})")
    
    print("\n💡 PAE sorgt für klare Entscheidungen auch bei Gleichständen!")


def demonstrate_mini_learner() -> None:
    """Demonstriert das Mini Learner Modul."""
    print_header("3. Mini Learner - Adaptives Lernen")
    
    print("Der Mini Learner passt das ethische Profil basierend auf Feedback an")
    print("und lernt aus Erfolgen und Misserfolgen.\n")
    
    # Szenario: Feedback
    scenario = ADVANCED_TEST_SCENARIOS[2]
    print(f"Situation: {scenario['query']}")
    print(f"Feedback: '{scenario['feedback']}'\n")
    
    # Kontext mit vorheriger Entscheidung
    context = {
        "profile": profiles.get_default_profile(),
        "ethics": scenario["previous_decision"]["ethics"],
        "context_type": "feedback_session",
        "feedback_source": "user"
    }
    
    # Mini Learner ausführen
    result = mini_learner.run_module(scenario["feedback"], context)
    
    if result["success"]:
        print(f"✅ Lernstatus: {result['status']}")
        print(f"   Konfidenz: {result['confidence']:.2f}")
        print(f"   Profil aktualisiert: {result['profile_updated']}")
        
        # Anpassungen zeigen
        if result["adjustments"]:
            print("\n   Profil-Anpassungen:")
            for principle, adj in result["adjustments"].items():
                change = adj["change"]
                direction = "↑" if change > 0 else "↓"
                print(f"   - {principle}: {adj['old']:.2f} → {adj['new']:.2f} {direction}")
                print(f"     Grund: {adj['reason']}")
        
        # Feedback-Analyse
        feedback_analysis = result["meta"]["feedback_analysis"]
        print(f"\n   Feedback-Typ: {feedback_analysis['type']}")
        print(f"   Gewichtung: {feedback_analysis['weight']:.2f}")
        
        # Integrity Check
        integrity = result["integrity_check"]
        print(f"\n   Integrity-Check: {'✅ Bestanden' if integrity['passed'] else '❌ Verletzt'}")
        
        # Notizen
        print(f"\n   System-Notiz: {result['notes']}")
    
    print("\n💡 Mini Learner macht das System adaptiv und lernfähig!")


def demonstrate_mini_audit() -> None:
    """Demonstriert das Mini Audit System."""
    print_header("4. Mini Audit - Entscheidungsprotokoll")
    
    print("Mini Audit protokolliert alle Entscheidungen für Transparenz,")
    print("Compliance und spätere Analyse.\n")
    
    # Erst einige Entscheidungen loggen
    print("Simuliere einige Entscheidungen zum Protokollieren...")
    
    # Audit-Instanz für Demo
    audit_config = {"session_id": "DEMO-ADV"}
    
    # Entscheidung 1: Ethisch korrekt
    decision1 = {
        "user_input": "Kann ich helfen?",
        "path": "fast",
        "ethics": {"scores": {"nurturing": 0.9}, "violations": []},
        "confidence": 0.85,
        "response": "Ja, Hilfe ist willkommen."
    }
    result1 = mini_audit.run_module("log", {
        "action": "log",
        "decision": decision1,
        "profile": profiles.get_default_profile(),
        "audit_config": audit_config
    })
    print(f"   ✅ Entscheidung 1 geloggt: {result1.get('audit_id', 'N/A')}")
    
    # Entscheidung 2: Mit Verletzung
    decision2 = {
        "user_input": "Soll ich Daten ohne Erlaubnis nutzen?",
        "path": "deep",
        "ethics": {"scores": {"governance": 0.2}, "violations": ["governance"]},
        "confidence": 0.6,
        "etb_result": {"chosen_option": "Nicht nutzen", "score": 0.8}
    }
    result2 = mini_audit.run_module("log", {
        "action": "log", 
        "decision": decision2,
        "profile": profiles.get_default_profile(),
        "audit_config": audit_config
    })
    print(f"   ⚠️  Entscheidung 2 geloggt: {result2.get('audit_id', 'N/A')}")
    
    # Jetzt Audit-Suche demonstrieren
    print("\n📋 Audit-Suche:")
    
    # Nach allen Entscheidungen suchen
    search_result = mini_audit.run_module("search", {
        "action": "search",
        "criteria": {"session_id": "DEMO-ADV"},
        "limit": 10,
        "audit_config": audit_config
    })
    
    if search_result["success"]:
        print(f"   Gefundene Einträge: {search_result['count']}")
        
        # Einträge anzeigen
        for entry in search_result["entries"][:3]:
            print(f"\n   📌 Audit ID: {entry['audit_id']}")
            print(f"      Zeit: {entry['timestamp'][:19]}")
            print(f"      Typ: {entry['event_type']}")
            print(f"      Eingabe: {entry['user_input'][:50]}...")
            if entry.get('violations'):
                print(f"      ⚠️  Verletzungen: {', '.join(entry['violations'])}")
    
    # Statistiken abrufen
    print("\n📊 Audit-Statistiken:")
    stats_result = mini_audit.run_module("stats", {
        "action": "stats",
        "days": 1,
        "audit_config": audit_config
    })
    
    if stats_result["success"]:
        stats = stats_result["statistics"]
        print(f"   Gesamt-Einträge: {stats['total_entries']}")
        print(f"   Nach Typ: {dict(stats['by_type'])}")
        print(f"   Verletzungen: {stats['violations_count']}")
        
        session = stats_result["session"]
        print(f"\n   Session: {session['session_id']}")
        print(f"   Entscheidungen: {session['stats']['decisions']}")
    
    print("\n💡 Mini Audit sorgt für lückenlose Nachvollziehbarkeit!")


def run_integrated_scenario() -> None:
    """Zeigt das Zusammenspiel aller Advanced Module."""
    print_header("5. Integriertes Szenario - Alle Module zusammen")
    
    print("Dieses Szenario zeigt, wie alle Advanced Module zusammenarbeiten.\n")
    
    # Komplexes ethisches Dilemma
    query = "Mein Freund hat bei der Prüfung geschummelt. Soll ich es melden?"
    print(f"🤔 Anfrage: '{query}'")
    
    # 1. Core Module erst
    print("\n1️⃣ Core-Module-Analyse:")
    profile = profiles.get_default_profile()
    context = {}
    
    # Simple Ethics
    ethics_input = {"text": query}
    context = simple_ethics.run_module(ethics_input, profile, context)
    
    if context.get("simple_ethics_result", {}).get("status") == "success":
        ethics = context["simple_ethics_result"]["evaluation"]
        print(f"   Ethik-Score: {ethics['overall_score']:.2f}")
        print(f"   Verletzungen: {ethics.get('violations', [])}")
    
    # 2. ETB für Optionen-Bewertung
    print("\n2️⃣ ETB - Handlungsoptionen bewerten:")
    
    options = [
        {
            "text": "Sofort dem Prüfungsamt melden",
            "tags": ["honest", "strict"],
            "risks": ["friendship_loss"],
            "alignment": {"integrity": 1.0, "governance": 1.0, "nurturing": 0.2}
        },
        {
            "text": "Mit dem Freund sprechen, selbst melden lassen",
            "tags": ["balanced", "supportive"],
            "risks": ["non_compliance"],
            "alignment": {"integrity": 0.8, "nurturing": 0.8, "governance": 0.6}
        },
        {
            "text": "Nichts sagen und vergessen",
            "tags": ["protective", "passive"],
            "risks": ["integrity_compromise"],
            "alignment": {"nurturing": 0.9, "integrity": 0.2, "governance": 0.1}
        }
    ]
    
    etb_context = {
        "context_type": "educational",
        "profile": profile,
        "ethics": ethics
    }
    
    etb_result = etb.run_module(options, etb_context)
    
    if etb_result["success"]:
        print(f"   ✅ Beste Option: {etb_result['best_option']}")
        print(f"   Score: {etb_result['score']:.2f}")
        
        # In Kontext speichern
        context["etb_result"] = etb_result["etb_result"]
    
    # 3. PAE falls Gleichstand
    print("\n3️⃣ PAE - Prioritäten klären:")
    
    # Simuliere Gleichstand zwischen Integrity und Nurturing
    pae_context = {
        "scores": {
            "integrity": 0.75,
            "nurturing": 0.75,
            "governance": 0.6,
            "awareness": 0.7,
            "learning": 0.5
        },
        "context_type": "educational",
        "user_input": query,
        "profile": profile,
        "etb_result": context.get("etb_result", {})
    }
    
    pae_result = pae.run_module("", pae_context)
    
    if pae_result["success"]:
        print(f"   Priorität: {pae_result['chosen_principle'].title()}")
        print(f"   Begründung: {pae_result['reasoning']}")
        
        # In Kontext speichern
        context["pae_result"] = pae_result["pae_result"]
    
    # 4. Mini Audit - Entscheidung protokollieren
    print("\n4️⃣ Mini Audit - Protokollierung:")
    
    audit_context = {
        "action": "log",
        "decision": {
            "user_input": query,
            "path": "deep",
            "ethics": ethics,
            "etb_result": context.get("etb_result", {}),
            "pae_result": context.get("pae_result", {}),
            "confidence": 0.75,
            "response": etb_result.get("best_option", "N/A")
        },
        "profile": profile,
        "audit_config": {"session_id": "INTEGRATED-DEMO"}
    }
    
    audit_result = mini_audit.run_module("log", audit_context)
    
    if audit_result["success"]:
        print(f"   ✅ Geloggt mit ID: {audit_result['audit_id']}")
        print(f"   Severity: {audit_result['severity']}")
    
    # 5. Feedback und Lernen
    print("\n5️⃣ Mini Learner - Aus Feedback lernen:")
    
    feedback = "Die Empfehlung war gut, aber ich hätte mehr Unterstützung für meinen Freund erwartet"
    
    learner_context = {
        "profile": profile,
        "ethics": ethics,
        "etb_result": context.get("etb_result", {}),
        "pae_result": context.get("pae_result", {}),
        "context_type": "feedback",
        "feedback_source": "user"
    }
    
    learner_result = mini_learner.run_module(feedback, learner_context)
    
    if learner_result["success"]:
        print(f"   Feedback-Typ: {learner_result['meta']['feedback_analysis']['type']}")
        print(f"   Lernstatus: {learner_result['status']}")
        
        if learner_result["adjustments"]:
            print("   Profil-Anpassungen:")
            for principle, adj in learner_result["adjustments"].items():
                print(f"   - {principle}: {adj['change']:+.2f}")
    
    print("\n✅ Alle Advanced Module haben erfolgreich zusammengearbeitet!")


def demonstrate_advanced_features() -> None:
    """Zeigt erweiterte Features der Advanced Module."""
    print_header("6. Erweiterte Features")
    
    print("Die Advanced Module bieten viele erweiterte Funktionen:\n")
    
    # ETB: Verschiedene Kontexttypen
    print("🔹 ETB - Kontextabhängige Bewertung:")
    contexts = ["emergency", "children", "professional"]
    for ctx in contexts:
        simple_options = [
            {"text": "Option A", "tags": ["direct"]},
            {"text": "Option B", "tags": ["careful"]}
        ]
        result = etb.run_module(simple_options, {"context_type": ctx})
        if result["success"]:
            print(f"   {ctx}: Beste Option basiert auf {ctx}-spezifischen Regeln")
    
    # PAE: Verschiedene Auflösungsmethoden
    print("\n🔹 PAE - Verschiedene Auflösungsmethoden:")
    methods = ["priority_order", "context_based", "historical", "profile_weighted", "combined"]
    print(f"   Verfügbare Methoden: {', '.join(methods)}")
    
    # Mini Learner: Lernmodi
    print("\n🔹 Mini Learner - Adaptive Lernmodi:")
    print("   - Konfidenz-basiertes Lernen mit Decay")
    print("   - Integrity Floor Protection")
    print("   - Momentum für glatte Anpassungen")
    print("   - Feedback-Gewichtung nach Quelle")
    
    # Mini Audit: Export-Funktionen
    print("\n🔹 Mini Audit - Export und Compliance:")
    print("   - JSON/CSV Export")
    print("   - Compliance Reports")
    print("   - Suchfunktionen mit Filtern")
    print("   - Automatische Rotation")


def run_batch_tests() -> None:
    """Führt automatisierte Tests für alle Module durch."""
    print_header("7. Batch-Tests - Automatisierte Prüfung")
    
    results = {
        "etb": {"success": 0, "total": 0},
        "pae": {"success": 0, "total": 0},
        "learner": {"success": 0, "total": 0},
        "audit": {"success": 0, "total": 0}
    }
    
    # ETB Tests
    print("Testing ETB...")
    etb_tests = [
        (
            [{"text": "A", "tags": ["honest"]}, {"text": "B", "tags": ["kind"]}],
            {"context_type": "general"}
        ),
        (
            [{"text": "Truth", "alignment": {"integrity": 1.0}}, 
             {"text": "Protect", "alignment": {"nurturing": 1.0}}],
            {"context_type": "children"}
        )
    ]
    
    for options, context in etb_tests:
        results["etb"]["total"] += 1
        result = etb.run_module(options, context)
        if result["success"]:
            results["etb"]["success"] += 1
    
    # PAE Tests
    print("Testing PAE...")
    pae_tests = [
        {"scores": {"integrity": 0.8, "nurturing": 0.8}, "context_type": "general"},
        {"scores": {"governance": 0.7, "awareness": 0.7, "learning": 0.7}, "context_type": "emergency"}
    ]
    
    for context in pae_tests:
        results["pae"]["total"] += 1
        result = pae.run_module("", context)
        if result["success"]:
            results["pae"]["success"] += 1
    
    # Learner Tests
    print("Testing Mini Learner...")
    feedbacks = [
        "Das war sehr hilfreich!",
        "Nicht gut, zu streng",
        "Bin mir unsicher..."
    ]
    
    for feedback in feedbacks:
        results["learner"]["total"] += 1
        result = mini_learner.run_module(feedback, {"profile": profiles.get_default_profile()})
        if result["success"]:
            results["learner"]["success"] += 1
    
    # Audit Tests
    print("Testing Mini Audit...")
    audit_actions = [
        {"action": "log", "decision": {"path": "fast"}},
        {"action": "search", "criteria": {}},
        {"action": "stats"}
    ]
    
    for action_data in audit_actions:
        results["audit"]["total"] += 1
        result = mini_audit.run_module("test", action_data)
        if result["success"]:
            results["audit"]["success"] += 1
    
    # Ergebnisse
    print("\n📊 Test-Ergebnisse:")
    total_success = 0
    total_tests = 0
    
    for module, stats in results.items():
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"   {module.upper()}: {stats['success']}/{stats['total']} ({success_rate:.0f}%)")
        total_success += stats["success"]
        total_tests += stats["total"]
    
    overall_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    print(f"\n   GESAMT: {total_success}/{total_tests} ({overall_rate:.0f}%)")
    
    if overall_rate == 100:
        print("\n✅ Alle Tests erfolgreich!")
    else:
        print("\n⚠️  Einige Tests fehlgeschlagen")


def main():
    """Hauptfunktion der Demo."""
    print("\n" + "="*80)
    print("INTEGRA ADVANCED MODULES DEMO".center(80))
    print("Demonstriert ETB, PAE, Mini Learner und Mini Audit".center(80))
    print("="*80)
    
    while True:
        print("\n📋 Demo-Menü:")
        print("1. ETB - Ethical Tradeoff Balancer")
        print("2. PAE - Priority Anchor Engine")
        print("3. Mini Learner - Adaptives Lernen")
        print("4. Mini Audit - Entscheidungsprotokoll")
        print("5. Integriertes Szenario (alle Module)")
        print("6. Erweiterte Features")
        print("7. Batch-Tests")
        print("8. Komplette Demo (alles)")
        print("0. Beenden")
        
        choice = input("\nIhre Wahl (0-8): ").strip()
        
        if choice == "1":
            demonstrate_etb()
        elif choice == "2":
            demonstrate_pae()
        elif choice == "3":
            demonstrate_mini_learner()
        elif choice == "4":
            demonstrate_mini_audit()
        elif choice == "5":
            run_integrated_scenario()
        elif choice == "6":
            demonstrate_advanced_features()
        elif choice == "7":
            run_batch_tests()
        elif choice == "8":
            # Alles der Reihe nach
            demonstrate_etb()
            input("\n[Enter für nächstes Modul...]")
            
            demonstrate_pae()
            input("\n[Enter für nächstes Modul...]")
            
            demonstrate_mini_learner()
            input("\n[Enter für nächstes Modul...]")
            
            demonstrate_mini_audit()
            input("\n[Enter für nächstes Modul...]")
            
            run_integrated_scenario()
            input("\n[Enter für erweiterte Features...]")
            
            demonstrate_advanced_features()
            input("\n[Enter für Batch-Tests...]")
            
            run_batch_tests()
            
            print("\n✅ Komplette Demo abgeschlossen!")
        elif choice == "0":
            print("\nAuf Wiedersehen!")
            break
        else:
            print("\n❌ Ungültige Eingabe. Bitte 0-8 wählen.")
        
        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            input("\n[Enter um fortzufahren...]")


if __name__ == "__main__":
    main()