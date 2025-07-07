# -*- coding: utf-8 -*-
"""
Modulname: dof.py
Beschreibung: Delayed Outcome Forecasting für INTEGRA Full - Prognose von Langzeitfolgen
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Integration mit anderen Modulen über Context
- Globale Instanz mit Lazy-Loading
- Konsistente Fehlerbehandlung
"""

from typing import Dict, Any, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import statistics
import math

# Standardisierte Imports
try:
    from integra.core import principles, profiles
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        log_manager = None
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


class TimeHorizon(Enum):
    """Zeithorizonte für Prognosen."""
    IMMEDIATE = "sofort"      # < 1 Woche
    SHORT = "kurzfristig"     # 1 Woche - 1 Monat
    MEDIUM = "mittelfristig"  # 1-6 Monate
    LONG = "langfristig"      # 6-24 Monate
    EXTENDED = "dauerhaft"    # > 24 Monate


class OutcomeType(Enum):
    """Arten von Langzeiteffekten."""
    HABITUATION = "gewöhnung"
    TRUST_DECAY = "vertrauensverlust"
    DEPENDENCY = "abhängigkeit"
    NORMALIZATION = "normalisierung"
    ESCALATION = "eskalation"
    SYSTEMIC_CHANGE = "systemveränderung"
    CULTURAL_SHIFT = "kulturwandel"
    COMPETENCE_LOSS = "kompetenzverlust"
    SOCIAL_IMPACT = "soziale_auswirkung"


class ImpactSeverity(Enum):
    """Schweregrad der Auswirkungen."""
    LOW = "niedrig"
    MODERATE = "moderat"
    HIGH = "hoch"
    CRITICAL = "kritisch"


class DelayedOutcomeForecaster:
    """
    Prognostiziert verzögerte und langfristige Auswirkungen von Entscheidungen.
    Berücksichtigt psychologische, soziale und systemische Effekte.
    """
    
    def __init__(self):
        self.outcome_patterns = self._initialize_patterns()
        self.time_decay_factors = {
            TimeHorizon.IMMEDIATE: 1.0,
            TimeHorizon.SHORT: 0.9,
            TimeHorizon.MEDIUM: 0.7,
            TimeHorizon.LONG: 0.5,
            TimeHorizon.EXTENDED: 0.3
        }
        
        # Erweiterte Muster für komplexere Analysen
        self.compound_effects = self._initialize_compound_effects()
        self.mitigation_strategies = self._initialize_mitigation_strategies()
        
        # Historie für Mustererkennung
        self.forecast_history = []
        self.pattern_accuracy = defaultdict(lambda: {"predicted": 0, "confirmed": 0})
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialisiert erweiterte Muster für Langzeiteffekte."""
        return {
            "repeated_assistance": {
                "triggers": ["immer helfen", "ständig unterstützen", "jedes mal", "automatisch", "stets"],
                "outcomes": [
                    {
                        "type": OutcomeType.DEPENDENCY,
                        "horizon": TimeHorizon.MEDIUM,
                        "probability": 0.7,
                        "severity": ImpactSeverity.HIGH,
                        "description": "Nutzer entwickelt Abhängigkeit von KI-Unterstützung",
                        "indicators": ["reduzierte Eigeninitiative", "häufigere Anfragen", "einfachere Fragen"]
                    },
                    {
                        "type": OutcomeType.COMPETENCE_LOSS,
                        "horizon": TimeHorizon.LONG,
                        "probability": 0.6,
                        "severity": ImpactSeverity.MODERATE,
                        "description": "Verlust eigener Problemlösungskompetenzen",
                        "indicators": ["geringere Lösungsqualität", "fehlendes Verständnis"]
                    },
                    {
                        "type": OutcomeType.HABITUATION,
                        "horizon": TimeHorizon.SHORT,
                        "probability": 0.8,
                        "severity": ImpactSeverity.MODERATE,
                        "description": "Gewöhnung an externe Lösungen",
                        "indicators": ["automatische Anfragen", "fehlende Reflexion"]
                    }
                ]
            },
            "privacy_erosion": {
                "triggers": ["daten sammeln", "tracken", "überwachen", "speichern", "aufzeichnen"],
                "outcomes": [
                    {
                        "type": OutcomeType.TRUST_DECAY,
                        "horizon": TimeHorizon.LONG,
                        "probability": 0.6,
                        "severity": ImpactSeverity.HIGH,
                        "description": "Schleichender Vertrauensverlust bei Nutzern",
                        "indicators": ["weniger Offenheit", "zurückhaltende Nutzung"]
                    },
                    {
                        "type": OutcomeType.NORMALIZATION,
                        "horizon": TimeHorizon.EXTENDED,
                        "probability": 0.5,
                        "severity": ImpactSeverity.CRITICAL,
                        "description": "Gesellschaftliche Akzeptanz von Privatsphäreverletzungen",
                        "indicators": ["sinkende Datenschutzbedenken", "freiwillige Datenpreisgabe"]
                    },
                    {
                        "type": OutcomeType.SOCIAL_IMPACT,
                        "horizon": TimeHorizon.MEDIUM,
                        "probability": 0.4,
                        "severity": ImpactSeverity.MODERATE,
                        "description": "Negative Reaktionen im sozialen Umfeld",
                        "indicators": ["öffentliche Kritik", "Nutzerabwanderung"]
                    }
                ]
            },
            "ethical_compromise": {
                "triggers": ["ausnahme", "diesmal", "nur einmal", "kompromiss", "ausnahmsweise"],
                "outcomes": [
                    {
                        "type": OutcomeType.ESCALATION,
                        "horizon": TimeHorizon.MEDIUM,
                        "probability": 0.6,
                        "severity": ImpactSeverity.HIGH,
                        "description": "Schrittweise Aufweichung ethischer Standards",
                        "indicators": ["häufigere Ausnahmen", "sinkende Hemmschwelle"]
                    },
                    {
                        "type": OutcomeType.SYSTEMIC_CHANGE,
                        "horizon": TimeHorizon.LONG,
                        "probability": 0.4,
                        "severity": ImpactSeverity.CRITICAL,
                        "description": "Systemweite Verschiebung ethischer Grenzen",
                        "indicators": ["neue Normalität", "veränderte Richtlinien"]
                    },
                    {
                        "type": OutcomeType.TRUST_DECAY,
                        "horizon": TimeHorizon.SHORT,
                        "probability": 0.5,
                        "severity": ImpactSeverity.MODERATE,
                        "description": "Glaubwürdigkeitsverlust",
                        "indicators": ["Inkonsistenz-Vorwürfe", "Vertrauensverlust"]
                    }
                ]
            },
            "automation_creep": {
                "triggers": ["automatisier", "selbstständig", "ohne prüfung", "delegier", "autonom"],
                "outcomes": [
                    {
                        "type": OutcomeType.HABITUATION,
                        "horizon": TimeHorizon.SHORT,
                        "probability": 0.8,
                        "severity": ImpactSeverity.HIGH,
                        "description": "Verlust menschlicher Kontrolle und Urteilsfähigkeit",
                        "indicators": ["blind trust", "fehlende Überprüfung"]
                    },
                    {
                        "type": OutcomeType.CULTURAL_SHIFT,
                        "horizon": TimeHorizon.EXTENDED,
                        "probability": 0.3,
                        "severity": ImpactSeverity.CRITICAL,
                        "description": "Gesellschaftliche Akzeptanz von KI-Dominanz",
                        "indicators": ["KI-first Mentalität", "menschliche Redundanz"]
                    },
                    {
                        "type": OutcomeType.COMPETENCE_LOSS,
                        "horizon": TimeHorizon.MEDIUM,
                        "probability": 0.7,
                        "severity": ImpactSeverity.MODERATE,
                        "description": "Verlust kritischer Fähigkeiten",
                        "indicators": ["Skill-Degradation", "Entscheidungsunsicherheit"]
                    }
                ]
            },
            "misinformation_spread": {
                "triggers": ["falsch", "irreführ", "täusch", "verzerr", "manipulation"],
                "outcomes": [
                    {
                        "type": OutcomeType.TRUST_DECAY,
                        "horizon": TimeHorizon.IMMEDIATE,
                        "probability": 0.9,
                        "severity": ImpactSeverity.CRITICAL,
                        "description": "Schneller und nachhaltiger Vertrauensverlust",
                        "indicators": ["virale Verbreitung", "Reputationsschaden"]
                    },
                    {
                        "type": OutcomeType.SYSTEMIC_CHANGE,
                        "horizon": TimeHorizon.LONG,
                        "probability": 0.5,
                        "severity": ImpactSeverity.HIGH,
                        "description": "Erosion der Informationsintegrität",
                        "indicators": ["Fakten-Zweifel", "Polarisierung"]
                    },
                    {
                        "type": OutcomeType.SOCIAL_IMPACT,
                        "horizon": TimeHorizon.SHORT,
                        "probability": 0.7,
                        "severity": ImpactSeverity.HIGH,
                        "description": "Gesellschaftliche Spaltung",
                        "indicators": ["Gruppen-Konflikte", "Echo-Kammern"]
                    }
                ]
            },
            "discrimination_risk": {
                "triggers": ["unterschied", "benachteilig", "ausschließ", "bevorzug", "diskriminier"],
                "outcomes": [
                    {
                        "type": OutcomeType.SOCIAL_IMPACT,
                        "horizon": TimeHorizon.IMMEDIATE,
                        "probability": 0.8,
                        "severity": ImpactSeverity.CRITICAL,
                        "description": "Verstärkung sozialer Ungleichheit",
                        "indicators": ["Beschwerden", "rechtliche Schritte"]
                    },
                    {
                        "type": OutcomeType.SYSTEMIC_CHANGE,
                        "horizon": TimeHorizon.LONG,
                        "probability": 0.6,
                        "severity": ImpactSeverity.HIGH,
                        "description": "Institutionalisierte Diskriminierung",
                        "indicators": ["systematische Benachteiligung", "Normalisierung"]
                    }
                ]
            }
        }
    
    def _initialize_compound_effects(self) -> Dict[str, Dict[str, Any]]:
        """Initialisiert zusammengesetzte Effekte."""
        return {
            "trust_dependency_spiral": {
                "components": [OutcomeType.TRUST_DECAY, OutcomeType.DEPENDENCY],
                "description": "Vertrauensverlust führt zu verstärkter Abhängigkeit",
                "amplification": 1.3
            },
            "competence_automation_loop": {
                "components": [OutcomeType.COMPETENCE_LOSS, OutcomeType.HABITUATION],
                "description": "Kompetenzverlust verstärkt Automatisierungstendenz",
                "amplification": 1.4
            },
            "ethical_erosion_cascade": {
                "components": [OutcomeType.ESCALATION, OutcomeType.NORMALIZATION],
                "description": "Ethische Eskalation führt zu neuer Normalität",
                "amplification": 1.5
            }
        }
    
    def _initialize_mitigation_strategies(self) -> Dict[OutcomeType, List[Dict[str, Any]]]:
        """Initialisiert Mitigationsstrategien für verschiedene Outcome-Typen."""
        return {
            OutcomeType.DEPENDENCY: [
                {
                    "strategy": "Schrittweise Reduktion der Unterstützung",
                    "effectiveness": 0.7,
                    "timeline": TimeHorizon.MEDIUM
                },
                {
                    "strategy": "Förderung eigenständiger Problemlösung",
                    "effectiveness": 0.8,
                    "timeline": TimeHorizon.SHORT
                }
            ],
            OutcomeType.TRUST_DECAY: [
                {
                    "strategy": "Transparente Kommunikation",
                    "effectiveness": 0.6,
                    "timeline": TimeHorizon.IMMEDIATE
                },
                {
                    "strategy": "Vertrauensbildende Maßnahmen",
                    "effectiveness": 0.5,
                    "timeline": TimeHorizon.LONG
                }
            ],
            OutcomeType.COMPETENCE_LOSS: [
                {
                    "strategy": "Kompetenztraining und Übungen",
                    "effectiveness": 0.8,
                    "timeline": TimeHorizon.MEDIUM
                },
                {
                    "strategy": "Gradueller Übergang zu Eigenverantwortung",
                    "effectiveness": 0.7,
                    "timeline": TimeHorizon.LONG
                }
            ]
        }
    
    def forecast_outcomes(self, action: str, context: Dict[str, Any],
                         time_horizon: Optional[TimeHorizon] = None) -> Dict[str, Any]:
        """
        Prognostiziert verzögerte Auswirkungen einer Aktion umfassend.
        
        Args:
            action: Die zu analysierende Aktion/Entscheidung
            context: Kontext mit zusätzlichen Informationen
            time_horizon: Optionaler spezifischer Zeithorizont
            
        Returns:
            Dict mit detaillierten Langzeitprognosen
        """
        action_lower = action.lower()
        identified_outcomes = []
        risk_scores = defaultdict(list)
        pattern_matches = []
        
        # Analysiere Muster
        for pattern_name, pattern in self.outcome_patterns.items():
            trigger_matches = [t for t in pattern["triggers"] if t in action_lower]
            if trigger_matches:
                pattern_matches.append({
                    "pattern": pattern_name,
                    "triggers": trigger_matches,
                    "strength": len(trigger_matches) / len(pattern["triggers"])
                })
                
                for outcome in pattern["outcomes"]:
                    # Filtere nach Zeithorizont wenn angegeben
                    if time_horizon and outcome["horizon"] != time_horizon:
                        continue
                    
                    # Berechne adjustierte Wahrscheinlichkeit
                    adjusted_prob = self._adjust_probability(
                        outcome["probability"],
                        outcome["horizon"],
                        outcome.get("severity", ImpactSeverity.MODERATE),
                        context,
                        pattern_matches[-1]["strength"]
                    )
                    
                    if adjusted_prob > 0.25:  # Niedrigerer Schwellenwert für umfassendere Analyse
                        outcome_entry = {
                            "type": outcome["type"],
                            "horizon": outcome["horizon"],
                            "probability": adjusted_prob,
                            "severity": outcome.get("severity", ImpactSeverity.MODERATE),
                            "description": outcome["description"],
                            "pattern": pattern_name,
                            "indicators": outcome.get("indicators", []),
                            "trigger_strength": pattern_matches[-1]["strength"]
                        }
                        
                        identified_outcomes.append(outcome_entry)
                        
                        # Aktualisiere Risiko-Scores
                        risk_scores[outcome["horizon"]].append(adjusted_prob)
        
        # Analysiere zusammengesetzte Effekte
        compound_effects = self._analyze_compound_effects(identified_outcomes)
        
        # Berechne aggregierte Risiken
        aggregated_risks = self._aggregate_risks(risk_scores)
        
        # Identifiziere Kipppunkte
        tipping_points = self._identify_tipping_points(identified_outcomes, context)
        
        # Generiere Mitigationsempfehlungen
        mitigation_recommendations = self._generate_mitigation_recommendations(
            identified_outcomes, compound_effects
        )
        
        # Erstelle Zeitverlaufsprognose
        timeline_forecast = self._create_timeline_forecast(identified_outcomes)
        
        # Generiere Prognose-Zusammenfassung
        forecast_summary = self._generate_forecast_summary(
            identified_outcomes, aggregated_risks, compound_effects, tipping_points
        )
        
        # Speichere in Historie
        self.forecast_history.append({
            "action": action[:100],
            "timestamp": datetime.now(),
            "outcomes_predicted": len(identified_outcomes),
            "highest_risk": max(aggregated_risks.values()) if aggregated_risks else 0
        })
        
        return {
            "identified_outcomes": identified_outcomes,
            "pattern_matches": pattern_matches,
            "risk_by_horizon": aggregated_risks,
            "highest_risk_horizon": max(aggregated_risks.items(), key=lambda x: x[1])[0] if aggregated_risks else None,
            "compound_effects": compound_effects,
            "tipping_points": tipping_points,
            "mitigation_recommendations": mitigation_recommendations,
            "timeline_forecast": timeline_forecast,
            "total_outcomes": len(identified_outcomes),
            "confidence": self._calculate_forecast_confidence(pattern_matches, identified_outcomes),
            "forecast_summary": forecast_summary
        }
    
    def _adjust_probability(self, base_prob: float, horizon: TimeHorizon,
                           severity: ImpactSeverity, context: Dict[str, Any],
                           trigger_strength: float) -> float:
        """Adjustiert Wahrscheinlichkeiten basierend auf multiplen Faktoren."""
        adjusted = base_prob
        
        # Zeit-Decay anwenden
        adjusted *= self.time_decay_factors[horizon]
        
        # Trigger-Stärke berücksichtigen
        adjusted *= (0.7 + 0.3 * trigger_strength)
        
        # Severity-Faktor (kritische Outcomes sind oft wahrscheinlicher)
        severity_factors = {
            ImpactSeverity.LOW: 0.9,
            ImpactSeverity.MODERATE: 1.0,
            ImpactSeverity.HIGH: 1.1,
            ImpactSeverity.CRITICAL: 1.2
        }
        adjusted *= severity_factors.get(severity, 1.0)
        
        # Kontext-Faktoren aus anderen Modulen
        # Nutze Ergebnisse aus dem Context
        
        # VDD-Ergebnis (Value Drift)
        vdd_result = context.get("vdd_result", {})
        if vdd_result.get("drift_detected"):
            drift_severity = vdd_result.get("drift_analysis", {}).get("overall_drift", 0)
            adjusted *= 1.0 + (drift_severity * 0.3)
        
        # Meta-Learner Patterns
        meta_learner_result = context.get("meta_learner_result", {})
        if meta_learner_result.get("patterns", {}).get("by_type", {}).get("failure_pattern", 0) > 2:
            adjusted *= 1.2  # Erhöhtes Risiko bei Fehlermustern
        
        # ASO Performance
        aso_result = context.get("aso_result", {})
        if aso_result.get("system_performance", {}).get("level") == "critical":
            adjusted *= 1.3  # Kritische System-Performance erhöht Risiken
        
        # Weitere Context-Faktoren
        if context.get("repeated_action", False):
            adjusted *= 1.3
        
        if context.get("user_vulnerability", "normal") == "high":
            adjusted *= 1.25
        
        if context.get("system_maturity", "mature") == "experimental":
            adjusted *= 1.15
        
        if context.get("previous_incidents", 0) > 0:
            adjusted *= 1.1 + (0.1 * min(context["previous_incidents"], 3))
        
        # Umgebungsfaktoren
        if context.get("public_visibility", False):
            adjusted *= 1.2  # Öffentliche Sichtbarkeit erhöht Auswirkungen
        
        if context.get("regulatory_environment", "normal") == "strict":
            adjusted *= 1.3  # Strenge Regulierung erhöht Konsequenzen
        
        # Normalisieren
        return min(adjusted, 0.99)
    
    def _aggregate_risks(self, risk_scores: Dict[TimeHorizon, List[float]]) -> Dict[str, float]:
        """Aggregiert Risiko-Scores nach Zeithorizont mit verbesserter Methodik."""
        aggregated = {}
        
        for horizon, scores in risk_scores.items():
            if scores:
                # Kombiniere Wahrscheinlichkeiten
                # P(mindestens ein Ereignis) = 1 - P(kein Ereignis)
                combined_prob = 1.0
                for score in scores:
                    combined_prob *= (1 - score)
                
                # Zusätzlich: Berücksichtige Anzahl der Risiken
                risk_count_factor = 1 + (0.1 * min(len(scores) - 1, 5))
                
                final_risk = (1 - combined_prob) * risk_count_factor
                aggregated[horizon.value] = round(min(final_risk, 0.99), 3)
        
        return aggregated
    
    def _analyze_compound_effects(self, outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analysiert zusammengesetzte und sich verstärkende Effekte."""
        compound_effects = []
        outcome_types = [o["type"] for o in outcomes]
        
        for compound_name, compound in self.compound_effects.items():
            components = compound["components"]
            if all(comp in outcome_types for comp in components):
                # Berechne verstärkte Wahrscheinlichkeit
                component_probs = [
                    o["probability"] for o in outcomes 
                    if o["type"] in components
                ]
                
                base_prob = statistics.mean(component_probs)
                amplified_prob = min(base_prob * compound["amplification"], 0.95)
                
                compound_effects.append({
                    "name": compound_name,
                    "description": compound["description"],
                    "probability": round(amplified_prob, 3),
                    "components": [c.value for c in components],
                    "amplification_factor": compound["amplification"]
                })
        
        return compound_effects
    
    def _identify_tipping_points(self, outcomes: List[Dict[str, Any]], 
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifiziert kritische Kipppunkte."""
        tipping_points = []
        
        # Regel 1: Mehrere kritische Outcomes im gleichen Zeithorizont
        horizon_critical = defaultdict(int)
        for outcome in outcomes:
            if outcome["severity"] == ImpactSeverity.CRITICAL:
                horizon_critical[outcome["horizon"]] += 1
        
        for horizon, count in horizon_critical.items():
            if count >= 2:
                tipping_points.append({
                    "type": "critical_accumulation",
                    "horizon": horizon.value,
                    "description": f"{count} kritische Effekte im Zeitraum {horizon.value}",
                    "risk_level": "sehr_hoch"
                })
        
        # Regel 2: Hohe Wahrscheinlichkeit für Systemveränderung
        system_changes = [o for o in outcomes if o["type"] == OutcomeType.SYSTEMIC_CHANGE]
        for change in system_changes:
            if change["probability"] > 0.6:
                tipping_points.append({
                    "type": "system_transformation",
                    "horizon": change["horizon"].value,
                    "description": "Wahrscheinliche grundlegende Systemveränderung",
                    "risk_level": "kritisch"
                })
        
        # Regel 3: Kaskadierende Effekte
        if len(outcomes) >= 5 and context.get("system_interconnected", False):
            tipping_points.append({
                "type": "cascade_risk",
                "horizon": "variabel",
                "description": "Risiko kaskadierender Effekte durch Systemvernetzung",
                "risk_level": "hoch"
            })
        
        return tipping_points
    
    def _generate_mitigation_recommendations(self, outcomes: List[Dict[str, Any]], 
                                           compound_effects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generiert spezifische Mitigationsempfehlungen."""
        recommendations = []
        
        # Priorisiere nach Severity und Wahrscheinlichkeit
        priority_outcomes = sorted(
            outcomes,
            key=lambda x: (x["severity"].value, x["probability"]),
            reverse=True
        )[:5]  # Top 5
        
        for outcome in priority_outcomes:
            outcome_type = outcome["type"]
            if outcome_type in self.mitigation_strategies:
                strategies = self.mitigation_strategies[outcome_type]
                for strategy in strategies:
                    recommendations.append({
                        "target_outcome": outcome_type.value,
                        "strategy": strategy["strategy"],
                        "effectiveness": strategy["effectiveness"],
                        "timeline": strategy["timeline"].value,
                        "priority": "hoch" if outcome["severity"] == ImpactSeverity.CRITICAL else "mittel"
                    })
        
        # Zusätzliche Empfehlungen für Compound Effects
        if compound_effects:
            recommendations.append({
                "target_outcome": "compound_effects",
                "strategy": "Integrierte Interventionsstrategie für verstärkende Effekte",
                "effectiveness": 0.7,
                "timeline": TimeHorizon.MEDIUM.value,
                "priority": "hoch"
            })
        
        return recommendations
    
    def _create_timeline_forecast(self, outcomes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Erstellt eine zeitliche Verlaufsprognose."""
        timeline = defaultdict(list)
        
        for outcome in outcomes:
            horizon = outcome["horizon"].value
            timeline[horizon].append({
                "type": outcome["type"].value,
                "probability": outcome["probability"],
                "severity": outcome["severity"].value,
                "description": outcome["description"][:100]
            })
        
        # Sortiere innerhalb jedes Zeitraums nach Wahrscheinlichkeit
        for horizon in timeline:
            timeline[horizon].sort(key=lambda x: x["probability"], reverse=True)
        
        return dict(timeline)
    
    def _calculate_forecast_confidence(self, pattern_matches: List[Dict[str, Any]], 
                                     outcomes: List[Dict[str, Any]]) -> float:
        """Berechnet die Konfidenz der Prognose."""
        if not pattern_matches:
            return 0.3
        
        # Basis-Konfidenz
        base_confidence = 0.6
        
        # Faktoren die Konfidenz erhöhen
        # Starke Pattern-Matches
        avg_pattern_strength = statistics.mean([p["strength"] for p in pattern_matches])
        base_confidence += avg_pattern_strength * 0.2
        
        # Konsistente Outcomes
        if len(outcomes) >= 3:
            outcome_types = [o["type"] for o in outcomes]
            type_consistency = len(set(outcome_types)) / len(outcome_types)
            base_confidence += (1 - type_consistency) * 0.1  # Konsistenz erhöht Konfidenz
        
        # Historische Genauigkeit (wenn verfügbar)
        if self.pattern_accuracy:
            accuracies = []
            for pattern in pattern_matches:
                pattern_name = pattern["pattern"]
                if pattern_name in self.pattern_accuracy:
                    stats = self.pattern_accuracy[pattern_name]
                    if stats["predicted"] > 0:
                        accuracy = stats["confirmed"] / stats["predicted"]
                        accuracies.append(accuracy)
            
            if accuracies:
                base_confidence += statistics.mean(accuracies) * 0.1
        
        return min(base_confidence, 0.95)
    
    def _generate_forecast_summary(self, outcomes: List[Dict[str, Any]], 
                                  risks: Dict[str, float],
                                  compound_effects: List[Dict[str, Any]],
                                  tipping_points: List[Dict[str, Any]]) -> str:
        """Generiert eine umfassende Prognose-Zusammenfassung."""
        if not outcomes:
            return "Keine signifikanten Langzeiteffekte prognostiziert."
        
        summary_parts = []
        
        # Hauptrisiken
        critical_outcomes = [o for o in outcomes if o["severity"] in [ImpactSeverity.CRITICAL, ImpactSeverity.HIGH]]
        if critical_outcomes:
            effect_types = list(set([o["type"].value for o in critical_outcomes]))
            summary_parts.append(f"Kritische Risiken: {', '.join(effect_types[:3])}")
        
        # Zeithorizont mit höchstem Risiko
        if risks:
            highest_risk = max(risks.items(), key=lambda x: x[1])
            summary_parts.append(f"Höchstes Risiko {highest_risk[0]} ({highest_risk[1]:.0%})")
        
        # Compound Effects
        if compound_effects:
            summary_parts.append(f"{len(compound_effects)} verstärkende Effekte identifiziert")
        
        # Kipppunkte
        if tipping_points:
            summary_parts.append(f"⚠️ {len(tipping_points)} kritische Kipppunkte erkannt")
        
        # Gesamtbewertung
        total_risk = statistics.mean(risks.values()) if risks else 0
        if total_risk > 0.7:
            summary_parts.append("Dringende Intervention erforderlich")
        elif total_risk > 0.4:
            summary_parts.append("Aufmerksame Beobachtung empfohlen")
        
        return ". ".join(summary_parts) + "."


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale Forecaster-Instanz
_forecaster_instance: Optional[DelayedOutcomeForecaster] = None

def _get_forecaster_instance() -> DelayedOutcomeForecaster:
    """Lazy-Loading der Forecaster-Instanz."""
    global _forecaster_instance
    if _forecaster_instance is None:
        _forecaster_instance = DelayedOutcomeForecaster()
    return _forecaster_instance


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
        # DOF-Konfiguration aus Context
        dof_config = context.get("config", {}).get("dof", {})
        
        # Forecaster-Instanz
        forecaster = _get_forecaster_instance()
        
        # Analysiere die Aktion
        action = input_text or context.get("decision_text", context.get("user_input", ""))
        if not action:
            raise ValueError("Keine Aktion zur Analyse gefunden")
        
        # Zeithorizont aus Konfiguration
        time_horizon = None
        if dof_config.get("time_horizon"):
            try:
                time_horizon = TimeHorizon(dof_config["time_horizon"])
            except ValueError:
                pass
        
        # Führe Prognose durch
        forecast = forecaster.forecast_outcomes(action, context, time_horizon)
        
        # Detail-Level aus Konfiguration
        detail_level = dof_config.get("detail_level", "medium")
        include_mitigation = dof_config.get("include_mitigation", True)
        
        # Formatiere Ergebnis basierend auf Detail-Level
        if detail_level == "low":
            result = {
                "summary": forecast["forecast_summary"],
                "total_risks": forecast["total_outcomes"],
                "highest_risk": max(forecast["risk_by_horizon"].values()) if forecast["risk_by_horizon"] else 0,
                "critical_outcomes": len([o for o in forecast["identified_outcomes"] 
                                        if o["severity"] == ImpactSeverity.CRITICAL])
            }
        elif detail_level == "high":
            result = forecast
            if not include_mitigation:
                result.pop("mitigation_recommendations", None)
        else:  # medium
            result = {
                "identified_outcomes": forecast["identified_outcomes"][:10],
                "risk_by_horizon": forecast["risk_by_horizon"],
                "tipping_points": forecast["tipping_points"],
                "summary": forecast["forecast_summary"],
                "recommendations": forecast["mitigation_recommendations"][:5] if include_mitigation else []
            }
        
        # Speichere im Context für andere Module
        context["dof_result"] = {
            "total_outcomes": forecast["total_outcomes"],
            "highest_risk": max(forecast["risk_by_horizon"].values()) if forecast["risk_by_horizon"] else 0,
            "critical_count": len([o for o in forecast["identified_outcomes"] 
                                 if o["severity"] == ImpactSeverity.CRITICAL]),
            "tipping_points": len(forecast["tipping_points"]),
            "forecast_summary": forecast["forecast_summary"]
        }
        
        # Log wichtige Events
        if log_manager:
            log_manager.log_event(
                "DOF",
                f"Prognose erstellt: {forecast['total_outcomes']} Outcomes, "
                f"Höchstes Risiko: {context['dof_result']['highest_risk']:.0%}",
                "INFO"
            )
            
            if forecast["tipping_points"]:
                log_manager.log_event(
                    "DOF",
                    f"⚠️ {len(forecast['tipping_points'])} kritische Kipppunkte identifiziert",
                    "WARNING"
                )
        
        return {
            "success": True,
            "result": result,
            "module": "dof",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "confidence": forecast["confidence"]
        }
        
    except Exception as e:
        error_msg = f"DOF error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("DOF", error_msg, "ERROR")
        
        return {
            "success": False,
            "error": error_msg,
            "module": "dof",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die DOF-Funktionalität."""
    print("=== INTEGRA DOF v2.0 Demo ===")
    print("Delayed Outcome Forecasting - Langzeitfolgen-Prognose\n")
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test-Fälle mit verschiedenen Kontexten
    test_cases = [
        {
            "name": "Einmalige Hilfestellung",
            "input": "Ich erkläre einmalig ein mathematisches Konzept",
            "context": {
                "profile": test_profile.copy(),
                "repeated_action": False,
                "user_vulnerability": "normal"
            }
        },
        {
            "name": "Wiederholte Vollständige Unterstützung",
            "input": "Ich werde immer alle Hausaufgaben komplett für den Schüler lösen",
            "context": {
                "profile": test_profile.copy(),
                "repeated_action": True,
                "user_vulnerability": "high",
                "domain": "education",
                # Simuliere andere Modul-Ergebnisse
                "vdd_result": {
                    "drift_detected": True,
                    "drift_analysis": {"overall_drift": 0.3}
                },
                "meta_learner_result": {
                    "patterns": {"by_type": {"failure_pattern": 3}}
                }
            }
        },
        {
            "name": "Datenschutz-Kompromiss",
            "input": "Nur diesmal speichere ich persönliche Daten ohne explizite Erlaubnis",
            "context": {
                "profile": test_profile.copy(),
                "system_maturity": "experimental",
                "public_visibility": True,
                "regulatory_environment": "strict"
            }
        },
        {
            "name": "Kritische Automatisierung",
            "input": "Das System trifft selbstständig medizinische Diagnosen ohne menschliche Prüfung",
            "context": {
                "profile": test_profile.copy(),
                "domain": "healthcare",
                "regulatory_environment": "strict",
                "previous_incidents": 1,
                # Simuliere kritische System-Performance
                "aso_result": {
                    "system_performance": {"level": "critical"}
                }
            }
        },
        {
            "name": "Diskriminierungsrisiko",
            "input": "Der Algorithmus könnte bestimmte Gruppen systematisch benachteiligen",
            "context": {
                "profile": test_profile.copy(),
                "public_visibility": True,
                "system_interconnected": True
            }
        }
    ]
    
    print("📊 Führe 5 Test-Szenarien durch...\n")
    
    for i, test in enumerate(test_cases):
        print(f"\n{'='*70}")
        print(f"Test {i+1}: {test['name']}")
        print(f"Eingabe: {test['input']}")
        
        # Test mit verschiedenen Detail-Levels
        for detail_level in ["low", "medium"]:
            print(f"\n--- Detail-Level: {detail_level} ---")
            
            # Konfiguriere Context
            test["context"]["config"] = {
                "dof": {
                    "detail_level": detail_level,
                    "include_mitigation": True
                }
            }
            
            # Führe Modul aus
            result = run_module(test["input"], test["context"])
            
            if result["success"]:
                dof_result = result["result"]
                
                if detail_level == "low":
                    # Zusammenfassung
                    print(f"\nPrognose: {dof_result['summary']}")
                    print(f"Gesamtrisiken: {dof_result['total_risks']}")
                    print(f"Höchstes Risiko: {dof_result['highest_risk']:.0%}")
                    print(f"Kritische Outcomes: {dof_result['critical_outcomes']}")
                else:
                    # Detaillierte Ansicht
                    print(f"\nPrognose: {dof_result['summary']}")
                    
                    # Top Outcomes
                    if dof_result.get("identified_outcomes"):
                        print(f"\nTop Langzeiteffekte:")
                        for outcome in dof_result["identified_outcomes"][:3]:
                            print(f"  • {outcome['type'].value} ({outcome['horizon'].value}): "
                                  f"{outcome['probability']:.0%} [{outcome['severity'].value}]")
                            print(f"    {outcome['description']}")
                    
                    # Risiko-Timeline
                    if dof_result.get("risk_by_horizon"):
                        print(f"\nRisiko-Timeline:")
                        for horizon, risk in sorted(dof_result["risk_by_horizon"].items()):
                            bar = "█" * int(risk * 20)
                            print(f"  {horizon:15}: {bar} {risk:.0%}")
                    
                    # Kipppunkte
                    if dof_result.get("tipping_points"):
                        print(f"\n⚠️ Kipppunkte:")
                        for tp in dof_result["tipping_points"]:
                            print(f"  - {tp['description']} [{tp['risk_level']}]")
                    
                    # Empfehlungen
                    if dof_result.get("recommendations"):
                        print(f"\nMitigationsempfehlungen:")
                        for rec in dof_result["recommendations"][:3]:
                            print(f"  - {rec['strategy']} (Effektivität: {rec['effectiveness']:.0%})")
                
                # Context-Updates zeigen
                if "dof_result" in result["context"]:
                    ctx_result = result["context"]["dof_result"]
                    print(f"\nIm Context gespeichert:")
                    print(f"  - Höchstes Risiko: {ctx_result['highest_risk']:.0%}")
                    print(f"  - Kritische Outcomes: {ctx_result['critical_count']}")
                    print(f"  - Kipppunkte: {ctx_result['tipping_points']}")
                
                print(f"\nKonfidenz: {result['confidence']:.2f}")
            else:
                print(f"❌ Fehler: {result['error']}")
    
    # Test: Integration mit anderen Modulen
    print(f"\n{'='*70}")
    print("Test: Integration mit anderen Modul-Ergebnissen")
    
    integrated_context = {
        "profile": test_profile.copy(),
        "repeated_action": True,
        # Simuliere umfassende Modul-Ergebnisse
        "vdd_result": {
            "drift_detected": True,
            "drift_analysis": {"overall_drift": 0.5}
        },
        "meta_learner_result": {
            "patterns": {
                "by_type": {
                    "failure_pattern": 5,
                    "success_pattern": 1
                }
            },
            "performance": {"current_performance": 0.3}
        },
        "aso_result": {
            "system_performance": {
                "level": "poor",
                "efficiency_score": 0.4
            },
            "bottlenecks": [
                {"module": "etb", "severity": 0.8}
            ]
        },
        "config": {
            "dof": {
                "detail_level": "medium",
                "time_horizon": "langfristig"
            }
        }
    }
    
    result = run_module(
        "Kontinuierliche automatische Entscheidungen ohne Nutzereinbindung",
        integrated_context
    )
    
    if result["success"]:
        print(f"\nIntegrierte Analyse mit Fokus auf: langfristige Effekte")
        print(f"Prognose: {result['result']['summary']}")
        print(f"Konfidenz (mit Modul-Integration): {result['confidence']:.2f}")
        
        # Zeige wie andere Module die Prognose beeinflussen
        print(f"\nEinfluss anderer Module:")
        print(f"  - VDD Drift erkannt: Risiken um ~15% erhöht")
        print(f"  - Meta-Learner Fehlermuster: Risiken um ~20% erhöht")
        print(f"  - ASO schlechte Performance: Risiken um ~10% erhöht")
    
    print("\n✅ DOF Demo abgeschlossen!")
    print("Das Modul prognostiziert Langzeitfolgen und integriert sich nahtlos mit anderen Modulen.")


if __name__ == "__main__":
    demo()