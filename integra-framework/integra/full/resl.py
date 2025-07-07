# -*- coding: utf-8 -*-
"""
Modulname: resl.py
Beschreibung: Recursive Ethical Simulation Loop für INTEGRA Full - Simuliert Folgekonflikte
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Integration mit anderen Modulen über Context
- Globale Instanz mit Lazy-Loading
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json

# Standardisierte Imports
try:
    from integra.core import principles, profiles
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from utils import log_manager
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
            log_manager = None
        except ImportError:
            print("❌ Fehler: Core Module nicht gefunden!")
            class principles:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            class profiles:
                @staticmethod
                def get_default_profile():
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            log_manager = None


class RecursiveEthicalSimulator:
    """
    Simuliert rekursiv die ethischen Folgekonflikte einer Entscheidung.
    Prüft bis zu MAX_DEPTH Ebenen tief, ob neue ethische Probleme entstehen.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert den Simulator.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        
        # Konfiguration
        self.max_depth = self.config.get("max_depth", 3)
        self.risk_threshold = self.config.get("risk_threshold", 0.7)
        self.use_context_modules = self.config.get("use_context_modules", True)
        self.enable_nga_check = self.config.get("enable_nga_check", True)
        self.enable_dof_check = self.config.get("enable_dof_check", True)
        
        # Erweiterte Konfliktmuster
        self.conflict_patterns = self._initialize_conflict_patterns()
        
        # Historie und Statistiken
        self.simulation_history = []
        self.stats = {
            "total_simulations": 0,
            "conflicts_found": 0,
            "max_depth_reached": 0,
            "average_risk": 0.0,
            "pattern_hits": {}
        }
    
    def _initialize_conflict_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialisiert erweiterte Konfliktmuster."""
        return {
            "privacy": {
                "triggers": ["daten", "privat", "speicher", "track", "überwach", "aufzeichn"],
                "principle": "governance",
                "follow_up": "Nutzer könnten Vertrauen verlieren",
                "risk_weight": 0.3,
                "nga_check": "gdpr"  # Prüfe mit NGA wenn verfügbar
            },
            "autonomy": {
                "triggers": ["entscheid", "autonom", "selbst", "kontroll", "bestimm"],
                "principle": "learning",
                "follow_up": "Reduzierte Eigenverantwortung möglich",
                "risk_weight": 0.25
            },
            "dependency": {
                "triggers": ["hilf", "lösung", "mach", "erledige", "übernehm", "komplett"],
                "principle": "nurturing",
                "follow_up": "Förderung von Abhängigkeit",
                "risk_weight": 0.35,
                "secondary_principle": "learning"
            },
            "truth": {
                "triggers": ["verschweig", "verheim", "täusch", "lüg", "falsch", "manipul"],
                "principle": "integrity",
                "follow_up": "Vertrauensverlust bei Aufdeckung",
                "risk_weight": 0.4
            },
            "harm": {
                "triggers": ["schaden", "verletz", "gefahr", "risk", "schädlich", "negativ"],
                "principle": "awareness",
                "follow_up": "Physische oder psychische Schäden",
                "risk_weight": 0.45,
                "secondary_principle": "nurturing"
            },
            "discrimination": {
                "triggers": ["rasse", "geschlecht", "religion", "herkunft", "benachteilig"],
                "principle": "integrity",
                "follow_up": "Diskriminierung und Ungleichbehandlung",
                "risk_weight": 0.5,
                "nga_check": "un_human_rights"
            },
            "manipulation": {
                "triggers": ["beeinfluss", "steuer", "lenk", "manipul", "trick"],
                "principle": "integrity",
                "follow_up": "Verlust der Entscheidungsfreiheit",
                "risk_weight": 0.4
            }
        }
    
    def simulate_consequences(self, 
                            action: str, 
                            context: Dict[str, Any], 
                            depth: int = 0) -> Dict[str, Any]:
        """
        Rekursive Simulation der Folgen einer Aktion.
        
        Args:
            action: Die zu prüfende Aktion/Entscheidung
            context: Vollständiger Kontext mit anderen Modul-Ergebnissen
            depth: Aktuelle Rekursionstiefe
            
        Returns:
            Dict mit erkannten Folgekonflikten und Risikobewertung
        """
        self.stats["total_simulations"] += 1
        
        if depth >= self.max_depth:
            self.stats["max_depth_reached"] += 1
            return {
                "max_depth_reached": True,
                "conflicts": [],
                "risk_level": 0.0,
                "confidence": 0.8  # Reduzierte Konfidenz bei Tiefenlimit
            }
        
        # Nutze andere Module aus Context
        ethics_result = context.get("simple_ethics_result", {})
        etb_result = context.get("etb_result", {})
        pae_result = context.get("pae_result", {})
        nga_result = context.get("nga_result", {})
        dof_result = context.get("dof_result", {})
        
        # Simuliere direkte Konsequenzen
        direct_consequences = self._analyze_direct_impact(
            action, context, ethics_result, nga_result
        )
        
        # Sammle alle Konflikte
        all_conflicts = direct_consequences["conflicts"].copy()
        max_risk = direct_consequences["risk_level"]
        confidence = direct_consequences.get("confidence", 1.0)
        
        # Nutze DOF-Ergebnisse wenn verfügbar
        if self.enable_dof_check and dof_result:
            # Integriere Langzeitrisiken
            if dof_result.get("highest_risk", 0) > 0.5:
                max_risk = max(max_risk, dof_result["highest_risk"] * 0.7)
                if "awareness" not in all_conflicts:
                    all_conflicts.append("awareness")
        
        # Simuliere Folgekonsequenzen für jede direkte Konsequenz
        for consequence in direct_consequences["triggered_actions"]:
            # Erstelle neuen Context für Folgesimulation
            nested_context = {
                "parent_action": action,
                "parent_conflicts": all_conflicts.copy(),
                "depth": depth + 1
            }
            
            # Übernehme relevante Module-Ergebnisse
            if ethics_result:
                nested_context["parent_ethics"] = ethics_result.get("scores", {})
            
            nested_result = self.simulate_consequences(
                consequence["action"], 
                nested_context, 
                depth + 1
            )
            
            # Aggregiere Konflikte
            for conflict in nested_result["conflicts"]:
                if conflict not in all_conflicts:
                    all_conflicts.append(conflict)
                    self.stats["conflicts_found"] += 1
            
            # Aktualisiere maximales Risiko mit Dämpfung
            dampening_factor = 0.8 ** (depth + 1)  # Exponentieller Abfall
            max_risk = max(max_risk, nested_result["risk_level"] * dampening_factor)
            
            # Reduziere Konfidenz bei tiefen Rekursionen
            confidence *= 0.95
        
        # Berechne finales Ergebnis
        result = {
            "conflicts": all_conflicts,
            "risk_level": min(max_risk, 1.0),
            "depth": depth,
            "direct_consequences": direct_consequences,
            "total_consequences": len(direct_consequences["triggered_actions"]),
            "confidence": max(confidence, 0.5)
        }
        
        # Aktualisiere Statistiken
        self.stats["average_risk"] = (
            (self.stats["average_risk"] * (self.stats["total_simulations"] - 1) + result["risk_level"]) /
            self.stats["total_simulations"]
        )
        
        return result
    
    def _analyze_direct_impact(self, 
                              action: str, 
                              context: Dict[str, Any],
                              ethics_result: Dict[str, Any],
                              nga_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert die direkten Auswirkungen einer Aktion.
        Nutzt Ergebnisse anderer Module für bessere Vorhersagen.
        """
        conflicts = []
        triggered_actions = []
        risk_level = 0.0
        confidence = 1.0
        
        action_lower = action.lower()
        
        # Prüfe auf Konfliktmuster
        for pattern_name, pattern in self.conflict_patterns.items():
            if any(trigger in action_lower for trigger in pattern["triggers"]):
                # Pattern gefunden
                conflicts.append(pattern["principle"])
                risk_level += pattern["risk_weight"]
                
                # Statistik
                self.stats["pattern_hits"][pattern_name] = self.stats["pattern_hits"].get(pattern_name, 0) + 1
                
                # Sekundäres Prinzip wenn vorhanden
                if "secondary_principle" in pattern:
                    if pattern["secondary_principle"] not in conflicts:
                        conflicts.append(pattern["secondary_principle"])
                
                # NGA-Check wenn aktiviert
                if self.enable_nga_check and nga_result and "nga_check" in pattern:
                    # Prüfe ob NGA bereits Verletzungen gefunden hat
                    nga_violations = nga_result.get("violations", [])
                    for violation in nga_violations:
                        if pattern["nga_check"] in str(violation).lower():
                            risk_level += 0.2  # Erhöhe Risiko bei NGA-Verletzung
                            confidence = min(confidence, 0.9)  # Leicht reduzierte Konfidenz
                
                # Simuliere Folgeaktion
                triggered_actions.append({
                    "action": pattern["follow_up"],
                    "context": {
                        "parent_action": action,
                        "conflict_type": pattern_name,
                        "affected_principle": pattern["principle"],
                        "pattern_confidence": 0.8
                    }
                })
        
        # Nutze Ethics-Scores wenn verfügbar
        if ethics_result and "scores" in ethics_result:
            for principle, score in ethics_result["scores"].items():
                if score < 0.5:
                    if principle not in conflicts:
                        conflicts.append(principle)
                        self.stats["conflicts_found"] += 1
                    risk_level += (0.5 - score) * 0.5
                    
                    # Trigger Folgeaktion bei sehr niedrigen Scores
                    if score < 0.3:
                        triggered_actions.append({
                            "action": f"Kritisch niedriger {principle}-Score könnte zu Problemen führen",
                            "context": {
                                "principle": principle,
                                "score": score,
                                "threshold": 0.3
                            }
                        })
        
        # ETB Tradeoffs berücksichtigen
        etb_result = context.get("etb_result", {})
        if etb_result and etb_result.get("critical_tradeoffs"):
            for tradeoff in etb_result["critical_tradeoffs"]:
                if isinstance(tradeoff, dict):
                    affected_principle = tradeoff.get("losing_principle", "")
                    if affected_principle and affected_principle not in conflicts:
                        conflicts.append(affected_principle)
                        risk_level += 0.15
        
        # PAE Anchor berücksichtigen
        pae_result = context.get("pae_result", {})
        if pae_result and pae_result.get("primary_anchor"):
            anchor = pae_result["primary_anchor"]
            # Wenn Anchor-Prinzip in Konflikten ist, erhöhe Risiko
            if anchor in conflicts:
                risk_level += 0.2
                triggered_actions.append({
                    "action": f"Konflikt mit primärem Ankerprinzip {anchor}",
                    "context": {"anchor": anchor, "severity": "high"}
                })
        
        # Normalisiere Risikolevel
        risk_level = min(risk_level, 1.0)
        
        # Log wenn aktiviert
        if log_manager:
            log_manager.log_event(
                "RESL",
                f"Direkte Analyse: {len(conflicts)} Konflikte, Risiko: {risk_level:.2f}",
                "INFO"
            )
        
        return {
            "conflicts": conflicts,
            "triggered_actions": triggered_actions,
            "risk_level": risk_level,
            "confidence": confidence,
            "analysis_timestamp": datetime.now().isoformat(),
            "patterns_matched": [p for p in self.stats["pattern_hits"].keys() if p in [pn for pn, _ in self.conflict_patterns.items()]]
        }
    
    def _generate_explanation(self, simulation_result: Dict[str, Any], profile: Dict[str, float]) -> str:
        """Generiert eine verbesserte Erklärung mit Context-Awareness."""
        if not simulation_result["conflicts"]:
            return "Keine signifikanten ethischen Folgekonflikte identifiziert."
        
        # Sortiere Konflikte nach Profilgewichtung
        sorted_conflicts = sorted(
            simulation_result["conflicts"], 
            key=lambda x: profile.get(x, 1.0), 
            reverse=True
        )
        
        explanation_parts = []
        
        # Hauptkonflikt
        main_conflict = sorted_conflicts[0]
        conflict_descriptions = {
            "integrity": "Wahrheitstreue und Transparenz",
            "governance": "Regelkonformität und Kontrolle", 
            "awareness": "Risikobewusstsein und Voraussicht",
            "learning": "Lernförderung und Entwicklung",
            "nurturing": "Fürsorge und Unterstützung"
        }
        
        explanation_parts.append(
            f"Die Simulation zeigt potenzielle Konflikte im Bereich {conflict_descriptions.get(main_conflict, main_conflict)}."
        )
        
        # Risikobewertung mit Konfidenzniveau
        risk_level = simulation_result["risk_level"]
        confidence = simulation_result.get("confidence", 1.0)
        
        if risk_level > 0.8:
            risk_text = "Das Risiko für ethische Folgekonflikte ist sehr hoch"
        elif risk_level > 0.6:
            risk_text = "Es besteht ein erhöhtes Risiko für ethische Folgekonflikte"
        elif risk_level > 0.3:
            risk_text = "Ein moderates Risiko für Folgekonflikte wurde identifiziert"
        else:
            risk_text = "Das Risiko für Folgekonflikte ist gering"
        
        if confidence < 0.8:
            risk_text += f" (Konfidenz: {confidence:.0%})"
        
        explanation_parts.append(risk_text + ".")
        
        # Weitere Konflikte
        if len(sorted_conflicts) > 1:
            other_conflicts = [conflict_descriptions.get(c, c) for c in sorted_conflicts[1:3]]
            explanation_parts.append(f"Weitere betroffene Bereiche: {', '.join(other_conflicts)}.")
        
        # Tiefe der Simulation
        if simulation_result.get("max_depth_reached"):
            explanation_parts.append("Maximale Simulationstiefe erreicht - tiefere Konflikte möglich.")
        elif simulation_result.get("depth", 0) > 0:
            explanation_parts.append(f"Simulation bis Tiefe {simulation_result['depth']} durchgeführt.")
        
        # Anzahl Folgekonsequenzen
        total_consequences = simulation_result.get("total_consequences", 0)
        if total_consequences > 3:
            explanation_parts.append(f"{total_consequences} potenzielle Folgekonsequenzen identifiziert.")
        
        return " ".join(explanation_parts)
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über bisherige Simulationen zurück."""
        return {
            "total_simulations": self.stats["total_simulations"],
            "conflicts_found": self.stats["conflicts_found"],
            "max_depth_reached_count": self.stats["max_depth_reached"],
            "average_risk": self.stats["average_risk"],
            "most_common_patterns": sorted(
                self.stats["pattern_hits"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale Simulator-Instanz
_simulator_instance: Optional[RecursiveEthicalSimulator] = None

def _get_simulator_instance(config: Optional[Dict[str, Any]] = None) -> RecursiveEthicalSimulator:
    """Lazy-Loading der Simulator-Instanz."""
    global _simulator_instance
    if _simulator_instance is None or config is not None:
        _simulator_instance = RecursiveEthicalSimulator(config)
    return _simulator_instance


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardisierte Modul-Schnittstelle für INTEGRA.
    
    Args:
        input_text: Text-Eingabe zur Analyse
        context: Entscheidungskontext mit allen Modul-Ergebnissen
        
    Returns:
        Standardisiertes Ergebnis-Dictionary
    """
    if context is None:
        context = {}
    
    try:
        # RESL-Konfiguration aus Context
        resl_config = context.get("config", {}).get("resl", {})
        
        # Simulator-Instanz
        simulator = _get_simulator_instance(resl_config)
        
        # Profil aus Context
        profile = context.get("profile", profiles.get_default_profile())
        
        # Log Start
        if log_manager:
            log_manager.log_event(
                "RESL",
                f"Starte rekursive Simulation (max_depth={simulator.max_depth})",
                "INFO"
            )
        
        # Text vorbereiten - nutze auch Response wenn vorhanden
        action_text = input_text
        if context.get("response"):
            # Kombiniere Input und geplante Response für bessere Simulation
            action_text = f"{input_text} -> {context['response']}"
        
        # Führe Simulation durch
        simulation_result = simulator.simulate_consequences(action_text, context)
        
        # Berechne gewichtetes Risiko basierend auf Profil
        weighted_risk = simulation_result["risk_level"]
        if simulation_result["conflicts"]:
            conflict_weights = sum(profile.get(conflict, 1.0) for conflict in simulation_result["conflicts"])
            weighted_risk *= (conflict_weights / len(simulation_result["conflicts"]))
        
        # Generiere Erklärung
        explanation = simulator._generate_explanation(simulation_result, profile)
        
        # Erstelle RESL-Ergebnis
        resl_result = {
            "triggered_conflicts": simulation_result["conflicts"],
            "conflicts_detected": len(simulation_result["conflicts"]) > 0,
            "risk_level": round(weighted_risk, 2),
            "raw_risk": round(simulation_result["risk_level"], 2),
            "explanation": explanation,
            "max_depth": simulator.max_depth,
            "simulation_depth_reached": simulation_result["depth"],
            "direct_consequences": simulation_result.get("direct_consequences", {}),
            "total_consequences": simulation_result.get("total_consequences", 0),
            "confidence": simulation_result.get("confidence", 1.0),
            "patterns_matched": simulation_result.get("direct_consequences", {}).get("patterns_matched", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # Warnung bei hohem Risiko
        if weighted_risk > simulator.risk_threshold:
            resl_result["warning"] = "Hohe Wahrscheinlichkeit ethischer Folgekonflikte"
            resl_result["requires_alternative"] = True
        
        # Speichere im Context
        context["resl_result"] = resl_result
        
        # Log Ergebnis
        if log_manager:
            log_manager.log_event(
                "RESL",
                f"Simulation abgeschlossen - Risiko: {weighted_risk:.2f}, "
                f"Konflikte: {len(simulation_result['conflicts'])}, "
                f"Tiefe: {simulation_result['depth']}",
                "INFO"
            )
            
            if weighted_risk > simulator.risk_threshold:
                log_manager.log_event(
                    "RESL",
                    f"WARNUNG: Hohes Risiko erkannt ({weighted_risk:.2f})",
                    "WARNING"
                )
        
        return {
            "success": True,
            "result": resl_result,
            "module": "resl",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"RESL error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("RESL", error_msg, "ERROR")
        
        # Fehler-Fallback
        context["resl_result"] = {
            "error": True,
            "error_message": error_msg,
            "triggered_conflicts": [],
            "conflicts_detected": False,
            "risk_level": 0.0,
            "confidence": 0.0
        }
        
        return {
            "success": False,
            "error": error_msg,
            "module": "resl",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die Verwendung des RESL-Moduls."""
    print("=== INTEGRA RESL (Recursive Ethical Simulation) Demo v2.0 ===")
    print("Standardisierte Baukasten-Integration\n")
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test-Szenarien
    test_scenarios = [
        {
            "name": "Harmlose Anfrage",
            "text": "Ich erkläre die Funktionsweise von Python",
            "context": {
                "profile": test_profile.copy(),
                "simple_ethics_result": {
                    "scores": {"integrity": 1.0, "learning": 1.0, "nurturing": 0.9},
                    "overall_score": 0.97
                }
            }
        },
        {
            "name": "Problematische Hilfe",
            "text": "Ich helfe beim Erstellen gefälschter Dokumente",
            "context": {
                "profile": test_profile.copy(),
                "response": "Ich zeige Ihnen, wie Sie überzeugende Fälschungen erstellen",
                "simple_ethics_result": {
                    "scores": {"integrity": 0.2, "governance": 0.3, "awareness": 0.4},
                    "overall_score": 0.3,
                    "violations": ["integrity", "governance"]
                }
            }
        },
        {
            "name": "Abhängigkeitsförderung",
            "text": "Ich erledige alle Hausaufgaben für den Schüler",
            "context": {
                "profile": test_profile.copy(),
                "simple_ethics_result": {
                    "scores": {"learning": 0.4, "nurturing": 0.8, "integrity": 0.7},
                    "overall_score": 0.63
                },
                "etb_result": {
                    "critical_tradeoffs": [
                        {"losing_principle": "learning", "impact": 0.6}
                    ]
                }
            }
        },
        {
            "name": "Datenschutz mit NGA-Integration",
            "text": "Ich speichere und analysiere private Nutzerdaten",
            "context": {
                "profile": test_profile.copy(),
                "nga_result": {
                    "violations": [
                        {
                            "framework": "gdpr",
                            "severity": "critical",
                            "description": "Keine Einwilligung"
                        }
                    ],
                    "overall_compliance": 0.3
                },
                "simple_ethics_result": {
                    "scores": {"governance": 0.4, "integrity": 0.5},
                    "overall_score": 0.45
                }
            }
        },
        {
            "name": "Komplexe Entscheidung mit mehreren Modulen",
            "text": "Entwickle eine Überwachungslösung für Mitarbeiter",
            "context": {
                "profile": test_profile.copy(),
                "response": "Hier ist ein System zur vollständigen Mitarbeiterüberwachung",
                "simple_ethics_result": {
                    "scores": {p: 0.55 for p in principles.ALIGN_KEYS},
                    "scores": {"governance": 0.4, "awareness": 0.5, "integrity": 0.45},
                    "overall_score": 0.47
                },
                "etb_result": {
                    "conflicts_detected": True,
                    "critical_tradeoffs": [
                        {"losing_principle": "integrity", "impact": 0.7},
                        {"losing_principle": "nurturing", "impact": 0.5}
                    ]
                },
                "pae_result": {
                    "primary_anchor": "governance",
                    "secondary": "awareness"
                },
                "dof_result": {
                    "highest_risk": 0.8,
                    "critical_count": 3,
                    "forecast_summary": "Langfristige Vertrauensprobleme wahrscheinlich"
                }
            }
        },
        {
            "name": "Test maximale Tiefe",
            "text": "Eine Aktion die viele Folgekonflikte auslöst",
            "context": {
                "profile": test_profile.copy(),
                "config": {
                    "resl": {
                        "max_depth": 5,
                        "risk_threshold": 0.5
                    }
                }
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*70}")
        print(f"Test {i+1}: {scenario['name']}")
        print(f"Eingabe: {scenario['text']}")
        if scenario["context"].get("response"):
            print(f"Geplante Antwort: {scenario['context']['response']}")
        
        # Führe RESL durch
        result = run_module(scenario["text"], scenario["context"])
        
        if result["success"]:
            resl_result = result["result"]
            
            print(f"\n📊 Simulationsergebnis:")
            print(f"  Risiko-Level: {resl_result['risk_level']} (roh: {resl_result['raw_risk']})")
            print(f"  Konfidenz: {resl_result['confidence']:.2%}")
            print(f"  Simulationstiefe: {resl_result['simulation_depth_reached']}/{resl_result['max_depth']}")
            
            if resl_result["triggered_conflicts"]:
                print(f"\n⚠️ Konflikte ({len(resl_result['triggered_conflicts'])}):")
                for conflict in resl_result["triggered_conflicts"]:
                    print(f"  - {conflict}")
            
            if resl_result.get("patterns_matched"):
                print(f"\n🔍 Erkannte Muster:")
                for pattern in resl_result["patterns_matched"]:
                    print(f"  - {pattern}")
            
            print(f"\n💭 Erklärung:")
            print(f"  {resl_result['explanation']}")
            
            if resl_result.get("warning"):
                print(f"\n🚨 WARNUNG: {resl_result['warning']}")
                if resl_result.get("requires_alternative"):
                    print(f"  → Alternative Lösung erforderlich!")
            
            # Context-Integration zeigen
            print(f"\n🔗 Context-Integration:")
            print(f"  RESL-Ergebnis im Context: {'resl_result' in result['context']}")
            if "simple_ethics_result" in scenario["context"]:
                print(f"  Ethics-Scores genutzt: ✅")
            if "nga_result" in scenario["context"]:
                print(f"  NGA-Compliance berücksichtigt: ✅")
            if "dof_result" in scenario["context"]:
                print(f"  DOF-Langzeitrisiken integriert: ✅")
            if "etb_result" in scenario["context"]:
                print(f"  ETB-Tradeoffs beachtet: ✅")
            
            # Direkte Konsequenzen
            direct = resl_result.get("direct_consequences", {})
            if direct.get("triggered_actions"):
                print(f"\n📍 Direkte Folgeaktionen: {len(direct['triggered_actions'])}")
            
            print(f"\n⏱️ Gesamtkonsequenzen: {resl_result.get('total_consequences', 0)}")
        else:
            print(f"\n❌ Fehler: {result['error']}")
    
    # Statistiken demonstrieren
    print(f"\n\n{'='*70}")
    print("📈 Simulationsstatistiken:")
    
    simulator = _get_simulator_instance()
    stats = simulator.get_simulation_stats()
    
    print(f"  Gesamt-Simulationen: {stats['total_simulations']}")
    print(f"  Konflikte gefunden: {stats['conflicts_found']}")
    print(f"  Max-Tiefe erreicht: {stats['max_depth_reached_count']}x")
    print(f"  Durchschn. Risiko: {stats['average_risk']:.2%}")
    
    if stats["most_common_patterns"]:
        print(f"\n  Häufigste Muster:")
        for pattern, count in stats["most_common_patterns"]:
            print(f"    - {pattern}: {count}x")
    
    # Konfigurationsänderung testen
    print(f"\n\n{'='*70}")
    print("🔧 Test mit geänderter Konfiguration:")
    
    custom_context = {
        "profile": test_profile.copy(),
        "config": {
            "resl": {
                "max_depth": 1,
                "risk_threshold": 0.3,
                "enable_nga_check": False,
                "enable_dof_check": False
            }
        }
    }
    
    result = run_module("Test mit minimaler Tiefe", custom_context)
    if result["success"]:
        print(f"  Max-Tiefe: {result['result']['max_depth']}")
        print(f"  Erreichte Tiefe: {result['result']['simulation_depth_reached']}")
        print(f"  NGA deaktiviert: ✅")
        print(f"  DOF deaktiviert: ✅")
    
    print("\n✅ RESL Demo v2.0 abgeschlossen!")
    print("\nDas Modul bietet:")
    print("  • Standardisierte Baukasten-Schnittstelle")
    print("  • Context-basierte Integration mit anderen Modulen")
    print("  • Erweiterte Konfliktmuster mit NGA-Integration")
    print("  • Nutzung von ETB, PAE, DOF und NGA Ergebnissen")
    print("  • Konfidenz-basierte Risikobewertung")
    print("  • Statistiken über Simulationsmuster")


if __name__ == "__main__":
    demo()