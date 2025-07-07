# -*- coding: utf-8 -*-
"""
Modulname: sbp.py
Beschreibung: Stakeholder Behavior Predictor für INTEGRA Full - Prognostiziert Reaktionen
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

from typing import Dict, Any, List, Tuple, Optional, Set
from datetime import datetime
from enum import Enum
from collections import defaultdict
import statistics

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


class StakeholderGroup(Enum):
    """Definierte Stakeholder-Gruppen."""
    USERS = "nutzer"
    PARENTS = "eltern"
    EDUCATORS = "pädagogen"
    REGULATORS = "aufsichtsbehörden"
    MEDIA = "medien"
    EXPERTS = "experten"
    PUBLIC = "öffentlichkeit"
    BUSINESS = "unternehmen"
    ACTIVISTS = "aktivisten"


class ReactionType(Enum):
    """Arten von Stakeholder-Reaktionen."""
    SUPPORTIVE = "unterstützend"
    NEUTRAL = "neutral"
    CONCERNED = "besorgt"
    CRITICAL = "kritisch"
    HOSTILE = "ablehnend"


class ReactionIntensity(Enum):
    """Intensität der Reaktion."""
    LOW = "niedrig"
    MODERATE = "moderat"
    HIGH = "hoch"
    EXTREME = "extrem"


class StakeholderBehaviorPredictor:
    """
    Prognostiziert das Verhalten und die Reaktionen verschiedener Stakeholder-Gruppen
    auf ethische Entscheidungen des KI-Systems.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert den Predictor.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        
        # Konfiguration
        self.include_cascade = self.config.get("include_cascade", True)
        self.detail_level = self.config.get("detail_level", "medium")
        self.focus_stakeholders = self.config.get("focus_stakeholders", None)
        self.use_context_modules = self.config.get("use_context_modules", True)
        
        # Stakeholder-Profile und Patterns
        self.stakeholder_profiles = self._initialize_stakeholder_profiles()
        self.reaction_patterns = self._initialize_reaction_patterns()
        
        # Historie und Statistiken
        self.prediction_history = []
        self.pattern_statistics = defaultdict(lambda: {"triggered": 0, "accurate": 0})
        self.stats = {
            "total_predictions": 0,
            "critical_reactions": 0,
            "cascade_events": 0,
            "average_risk": 0.0
        }
    
    def _initialize_stakeholder_profiles(self) -> Dict[StakeholderGroup, Dict[str, Any]]:
        """Initialisiert Profile für verschiedene Stakeholder-Gruppen."""
        return {
            StakeholderGroup.USERS: {
                "values": ["convenience", "privacy", "autonomy", "support"],
                "triggers": {
                    "positive": ["hilfe", "unterstützung", "vereinfach", "effizient", "praktisch"],
                    "negative": ["einschränk", "kontroll", "überwach", "kompliziert", "datenschutz"]
                },
                "influence": 0.8,
                "reaction_speed": "schnell",
                "volatility": 0.7
            },
            StakeholderGroup.PARENTS: {
                "values": ["safety", "education", "control", "development"],
                "triggers": {
                    "positive": ["sicher", "lern", "entwicklung", "schutz", "förder"],
                    "negative": ["gefahr", "abhängig", "unkontrolliert", "schädlich", "risiko"]
                },
                "influence": 0.9,
                "reaction_speed": "moderat",
                "volatility": 0.5
            },
            StakeholderGroup.EDUCATORS: {
                "values": ["learning", "autonomy", "ethics", "development"],
                "triggers": {
                    "positive": ["förder", "lern", "kompetenz", "selbstständig", "bildung"],
                    "negative": ["abhängig", "passiv", "betrug", "umgeh", "faul"]
                },
                "influence": 0.7,
                "reaction_speed": "moderat",
                "volatility": 0.4
            },
            StakeholderGroup.REGULATORS: {
                "values": ["compliance", "safety", "transparency", "accountability"],
                "triggers": {
                    "positive": ["konform", "transparent", "kontrollier", "sicher", "rechtmäßig"],
                    "negative": ["verstoß", "intransparent", "unkontrolliert", "risiko", "illegal"]
                },
                "influence": 1.0,
                "reaction_speed": "langsam",
                "volatility": 0.2
            },
            StakeholderGroup.MEDIA: {
                "values": ["newsworthy", "controversy", "public_interest", "ethics"],
                "triggers": {
                    "positive": ["innovation", "fortschritt", "ethisch", "verantwortung", "transparent"],
                    "negative": ["skandal", "gefahr", "kontrovers", "versagen", "manipulation"]
                },
                "influence": 0.8,
                "reaction_speed": "sehr_schnell",
                "volatility": 0.9
            },
            StakeholderGroup.EXPERTS: {
                "values": ["accuracy", "ethics", "innovation", "best_practice"],
                "triggers": {
                    "positive": ["fundiert", "ethisch", "innovativ", "wissenschaftlich", "evidenz"],
                    "negative": ["unwissenschaftlich", "riskant", "kurzsichtig", "fehlerhaft", "naiv"]
                },
                "influence": 0.6,
                "reaction_speed": "moderat",
                "volatility": 0.3
            },
            StakeholderGroup.PUBLIC: {
                "values": ["fairness", "safety", "benefit", "trust"],
                "triggers": {
                    "positive": ["fair", "nützlich", "vertrauenswürdig", "hilfreich", "transparent"],
                    "negative": ["unfair", "bedrohlich", "manipulativ", "schädlich", "undurchsichtig"]
                },
                "influence": 0.5,
                "reaction_speed": "variabel",
                "volatility": 0.6
            },
            StakeholderGroup.BUSINESS: {
                "values": ["efficiency", "profit", "innovation", "compliance"],
                "triggers": {
                    "positive": ["effizient", "profitabel", "wettbewerbsvorteil", "skalierbar", "roi"],
                    "negative": ["kostspielig", "riskant", "reguliert", "komplex", "unrentabel"]
                },
                "influence": 0.7,
                "reaction_speed": "moderat",
                "volatility": 0.5
            },
            StakeholderGroup.ACTIVISTS: {
                "values": ["ethics", "rights", "justice", "transparency"],
                "triggers": {
                    "positive": ["ethisch", "transparent", "gerecht", "verantwortlich", "nachhaltig"],
                    "negative": ["verletzung", "intransparent", "ungerecht", "ausbeutung", "diskriminier"]
                },
                "influence": 0.6,
                "reaction_speed": "schnell",
                "volatility": 0.8
            }
        }
    
    def _initialize_reaction_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialisiert Reaktionsmuster für verschiedene Szenarien."""
        return {
            "privacy_violation": {
                "affected_groups": [
                    (StakeholderGroup.USERS, ReactionType.CRITICAL, ReactionIntensity.HIGH),
                    (StakeholderGroup.REGULATORS, ReactionType.HOSTILE, ReactionIntensity.EXTREME),
                    (StakeholderGroup.MEDIA, ReactionType.CRITICAL, ReactionIntensity.HIGH),
                    (StakeholderGroup.ACTIVISTS, ReactionType.HOSTILE, ReactionIntensity.HIGH)
                ],
                "triggers": ["datenschutz", "privat", "speicher", "track", "überwach"],
                "cascade_probability": 0.8
            },
            "child_safety": {
                "affected_groups": [
                    (StakeholderGroup.PARENTS, ReactionType.HOSTILE, ReactionIntensity.EXTREME),
                    (StakeholderGroup.EDUCATORS, ReactionType.CRITICAL, ReactionIntensity.HIGH),
                    (StakeholderGroup.MEDIA, ReactionType.CRITICAL, ReactionIntensity.EXTREME),
                    (StakeholderGroup.REGULATORS, ReactionType.HOSTILE, ReactionIntensity.HIGH)
                ],
                "triggers": ["kind", "minderjährig", "jugend", "schüler", "minderjährig"],
                "cascade_probability": 0.9
            },
            "automation_dependency": {
                "affected_groups": [
                    (StakeholderGroup.EDUCATORS, ReactionType.CONCERNED, ReactionIntensity.MODERATE),
                    (StakeholderGroup.EXPERTS, ReactionType.CRITICAL, ReactionIntensity.MODERATE),
                    (StakeholderGroup.PARENTS, ReactionType.CONCERNED, ReactionIntensity.LOW),
                    (StakeholderGroup.BUSINESS, ReactionType.SUPPORTIVE, ReactionIntensity.HIGH)
                ],
                "triggers": ["automatisch", "selbstständig", "abhängig", "delegation", "autonom"],
                "cascade_probability": 0.4
            },
            "ethical_support": {
                "affected_groups": [
                    (StakeholderGroup.USERS, ReactionType.SUPPORTIVE, ReactionIntensity.HIGH),
                    (StakeholderGroup.EXPERTS, ReactionType.SUPPORTIVE, ReactionIntensity.MODERATE),
                    (StakeholderGroup.MEDIA, ReactionType.SUPPORTIVE, ReactionIntensity.LOW),
                    (StakeholderGroup.PUBLIC, ReactionType.SUPPORTIVE, ReactionIntensity.MODERATE)
                ],
                "triggers": ["ethisch", "verantwortung", "transparent", "fair", "nachhaltig"],
                "cascade_probability": 0.3
            },
            "discrimination_risk": {
                "affected_groups": [
                    (StakeholderGroup.ACTIVISTS, ReactionType.HOSTILE, ReactionIntensity.EXTREME),
                    (StakeholderGroup.MEDIA, ReactionType.CRITICAL, ReactionIntensity.HIGH),
                    (StakeholderGroup.REGULATORS, ReactionType.CRITICAL, ReactionIntensity.HIGH),
                    (StakeholderGroup.PUBLIC, ReactionType.CRITICAL, ReactionIntensity.MODERATE)
                ],
                "triggers": ["diskriminier", "benachteilig", "ausgrenz", "vorurteil", "bias"],
                "cascade_probability": 0.85
            }
        }
    
    def predict_reactions(self, decision: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prognostiziert Reaktionen verschiedener Stakeholder auf eine Entscheidung.
        Integriert Ergebnisse anderer Module aus dem Context.
        
        Args:
            decision: Die zu bewertende Entscheidung
            context: Vollständiger Kontext mit anderen Modul-Ergebnissen
            
        Returns:
            Dict mit detaillierten Reaktionsprognosen
        """
        self.stats["total_predictions"] += 1
        decision_lower = decision.lower()
        
        # Nutze andere Module aus Context
        ethics_result = context.get("simple_ethics_result", {})
        nga_result = context.get("nga_result", {})
        uia_result = context.get("uia_result", {})
        meta_learner_result = context.get("meta_learner_result", {})
        
        # Identifiziere relevante Reaktionsmuster
        triggered_patterns = []
        for pattern_name, pattern in self.reaction_patterns.items():
            trigger_count = sum(1 for trigger in pattern["triggers"] if trigger in decision_lower)
            
            # Verstärke Pattern bei Ethics-Verletzungen
            if self.use_context_modules and ethics_result:
                violations = ethics_result.get("violations", [])
                if pattern_name == "privacy_violation" and "governance" in violations:
                    trigger_count += 2
                elif pattern_name == "discrimination_risk" and "integrity" in violations:
                    trigger_count += 2
            
            if trigger_count > 0:
                triggered_patterns.append((pattern_name, pattern, trigger_count))
                self.pattern_statistics[pattern_name]["triggered"] += 1
        
        # Sortiere nach Relevanz
        triggered_patterns.sort(key=lambda x: x[2], reverse=True)
        
        # Analysiere Reaktionen für jede Stakeholder-Gruppe
        stakeholder_reactions = {}
        
        # Fokus auf bestimmte Stakeholder wenn konfiguriert
        groups_to_analyze = self.stakeholder_profiles.keys()
        if self.focus_stakeholders:
            groups_to_analyze = [
                g for g in groups_to_analyze 
                if g.value in self.focus_stakeholders
            ]
        
        for stakeholder in groups_to_analyze:
            profile = self.stakeholder_profiles[stakeholder]
            reaction = self._analyze_stakeholder_reaction(
                stakeholder, 
                profile, 
                decision_lower, 
                triggered_patterns,
                context,
                ethics_result,
                nga_result,
                uia_result
            )
            stakeholder_reactions[stakeholder] = reaction
        
        # Berechne Kaskadeneffekte
        cascade_risk = {}
        if self.include_cascade:
            cascade_risk = self._calculate_cascade_risk(
                triggered_patterns, 
                stakeholder_reactions,
                context
            )
            if cascade_risk["probability"] > 0.7:
                self.stats["cascade_events"] += 1
        
        # Aggregiere Gesamtimpact
        aggregate_impact = self._aggregate_impact(stakeholder_reactions)
        
        # Zeitliche Dynamik
        temporal_dynamics = self._predict_temporal_dynamics(
            stakeholder_reactions, 
            triggered_patterns
        )
        
        # Meta-Learner Integration für Musterverbesserung
        if self.use_context_modules and meta_learner_result:
            if meta_learner_result.get("pattern_confidence", 0) > 0.8:
                # Erhöhe Konfidenz bei bekannten Mustern
                confidence_boost = 0.1
            else:
                confidence_boost = 0.0
        else:
            confidence_boost = 0.0
        
        # Prognose-Ergebnis
        prediction_result = {
            "stakeholder_reactions": stakeholder_reactions,
            "triggered_patterns": [(p[0], p[2]) for p in triggered_patterns],
            "cascade_risk": cascade_risk,
            "aggregate_impact": aggregate_impact,
            "temporal_dynamics": temporal_dynamics,
            "confidence": min(0.95, self._calculate_prediction_confidence(
                triggered_patterns, context
            ) + confidence_boost),
            "negative_reaction_probability": aggregate_impact.get("risk_level", 0),
            "positive_reaction_probability": max(0, 1.0 - aggregate_impact.get("risk_level", 0)),
            "key_stakeholders": self._identify_key_stakeholders(stakeholder_reactions)
        }
        
        # Speichere in Historie
        self.prediction_history.append({
            "timestamp": datetime.now(),
            "decision": decision[:100],
            "prediction": prediction_result
        })
        
        # Aktualisiere Statistiken
        self.stats["average_risk"] = (
            (self.stats["average_risk"] * (self.stats["total_predictions"] - 1) + 
             aggregate_impact.get("risk_level", 0)) / self.stats["total_predictions"]
        )
        
        return prediction_result
    
    def _analyze_stakeholder_reaction(self,
                                    stakeholder: StakeholderGroup,
                                    profile: Dict[str, Any],
                                    decision: str,
                                    patterns: List[Tuple[str, Dict[str, Any], int]],
                                    context: Dict[str, Any],
                                    ethics_result: Dict[str, Any],
                                    nga_result: Dict[str, Any],
                                    uia_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert die Reaktion einer spezifischen Stakeholder-Gruppe mit Context-Integration."""
        
        # Basis-Reaktion
        base_reaction = ReactionType.NEUTRAL
        base_intensity = ReactionIntensity.LOW
        confidence = 0.5
        
        # Prüfe Trigger in der Entscheidung
        positive_triggers = sum(1 for trigger in profile["triggers"]["positive"] 
                               if trigger in decision)
        negative_triggers = sum(1 for trigger in profile["triggers"]["negative"] 
                               if trigger in decision)
        
        # Basis-Bewertung
        if positive_triggers > negative_triggers:
            base_reaction = ReactionType.SUPPORTIVE
            base_intensity = ReactionIntensity.MODERATE
            confidence = min(0.5 + positive_triggers * 0.1, 0.9)
        elif negative_triggers > positive_triggers:
            base_reaction = ReactionType.CRITICAL
            base_intensity = ReactionIntensity.MODERATE
            confidence = min(0.5 + negative_triggers * 0.1, 0.9)
        
        # Context-Module Integration
        if self.use_context_modules:
            # Ethics-basierte Anpassung
            if ethics_result and stakeholder == StakeholderGroup.REGULATORS:
                overall_ethics = ethics_result.get("overall_score", 1.0)
                if overall_ethics < 0.5:
                    base_reaction = ReactionType.HOSTILE
                    base_intensity = ReactionIntensity.HIGH
                    confidence = min(confidence + 0.2, 0.95)
            
            # NGA-basierte Anpassung
            if nga_result and stakeholder in [StakeholderGroup.REGULATORS, StakeholderGroup.ACTIVISTS]:
                compliance = nga_result.get("overall_compliance", 1.0)
                if compliance < 0.5:
                    if base_reaction != ReactionType.HOSTILE:
                        base_reaction = ReactionType.CRITICAL
                    base_intensity = ReactionIntensity.HIGH
                    confidence = min(confidence + 0.15, 0.95)
            
            # UIA-basierte Anpassung - Manipulation erkennen
            if uia_result and stakeholder == StakeholderGroup.MEDIA:
                detected_intention = uia_result.get("detected_intention", "neutral")
                if detected_intention in ["manipulative", "adversarial"]:
                    base_reaction = ReactionType.CRITICAL
                    base_intensity = ReactionIntensity.HIGH
        
        # Berücksichtige spezifische Muster
        for pattern_name, pattern, relevance in patterns:
            for group, reaction_type, intensity in pattern["affected_groups"]:
                if group == stakeholder:
                    # Überschreibe mit spezifischem Muster
                    base_reaction = reaction_type
                    base_intensity = intensity
                    confidence = min(confidence + 0.2, 0.95)
                    break
        
        # Kontextuelle Anpassungen
        if context.get("public_attention", False):
            if base_intensity == ReactionIntensity.MODERATE:
                base_intensity = ReactionIntensity.HIGH
            confidence = min(confidence * 1.1, 0.95)
        
        if context.get("previous_incidents", 0) > 0:
            if base_reaction in [ReactionType.CONCERNED, ReactionType.CRITICAL]:
                base_reaction = ReactionType.HOSTILE
            confidence = min(confidence * 1.2, 0.95)
        
        # Geschwindigkeit der Reaktion
        reaction_speed = profile["reaction_speed"]
        if context.get("urgent", False):
            speed_map = {"sehr_schnell": 0.5, "schnell": 0.7, "moderat": 1.0, "langsam": 1.5}
            speed_multiplier = speed_map.get(reaction_speed, 1.0)
            reaction_speed = "schnell" if speed_multiplier > 0.7 else "sehr_schnell"
        
        # Emotionale Volatilität
        emotional_volatility = profile.get("volatility", 0.5)
        if emotional_volatility > 0.7 and base_intensity in [ReactionIntensity.HIGH, ReactionIntensity.EXTREME]:
            confidence *= 0.9  # Höhere Unsicherheit bei volatilen Gruppen
        
        return {
            "reaction": base_reaction,
            "intensity": base_intensity,
            "confidence": round(confidence, 2),
            "influence": profile["influence"],
            "reaction_speed": reaction_speed,
            "volatility": emotional_volatility,
            "key_concerns": self._identify_concerns(stakeholder, decision, base_reaction),
            "communication_recommendation": self._generate_communication_recommendation(
                stakeholder, base_reaction, base_intensity
            ),
            "context_factors_used": {
                "ethics_score": bool(ethics_result),
                "nga_compliance": bool(nga_result),
                "uia_intention": bool(uia_result)
            }
        }
    
    def _identify_concerns(self, 
                          stakeholder: StakeholderGroup, 
                          decision: str,
                          reaction: ReactionType) -> List[str]:
        """Identifiziert spezifische Bedenken einer Stakeholder-Gruppe."""
        concerns = []
        
        concern_mapping = {
            StakeholderGroup.PARENTS: {
                ReactionType.CRITICAL: ["Kindersicherheit gefährdet", "Entwicklung beeinträchtigt"],
                ReactionType.CONCERNED: ["Mögliche negative Einflüsse", "Kontrollverlust"],
                ReactionType.HOSTILE: ["Inakzeptables Risiko für Kinder", "Vertrauensbruch"]
            },
            StakeholderGroup.REGULATORS: {
                ReactionType.HOSTILE: ["Gesetzesverstoß möglich", "Compliance-Verletzung"],
                ReactionType.CRITICAL: ["Regulatorische Bedenken", "Aufsichtspflicht verletzt"],
                ReactionType.CONCERNED: ["Rechtliche Grauzone", "Präzedenzfall-Risiko"]
            },
            StakeholderGroup.MEDIA: {
                ReactionType.CRITICAL: ["Negativschlagzeilen möglich", "Öffentliches Interesse"],
                ReactionType.CONCERNED: ["Story-Potenzial", "Ethische Fragen"],
                ReactionType.SUPPORTIVE: ["Positive Berichterstattung möglich", "Innovationsthema"]
            },
            StakeholderGroup.USERS: {
                ReactionType.CRITICAL: ["Vertrauensverlust", "Nutzungseinschränkung"],
                ReactionType.CONCERNED: ["Datenschutzbedenken", "Autonomieverlust"],
                ReactionType.SUPPORTIVE: ["Praktischer Nutzen", "Vereinfachung"]
            },
            StakeholderGroup.ACTIVISTS: {
                ReactionType.HOSTILE: ["Grundrechtsverletzung", "Systemkritik"],
                ReactionType.CRITICAL: ["Ethische Standards verletzt", "Transparenzmangel"],
                ReactionType.CONCERNED: ["Potenzielle Diskriminierung", "Fairness-Fragen"]
            }
        }
        
        if stakeholder in concern_mapping and reaction in concern_mapping[stakeholder]:
            concerns = concern_mapping[stakeholder][reaction]
        
        return concerns
    
    def _generate_communication_recommendation(self, 
                                             stakeholder: StakeholderGroup,
                                             reaction: ReactionType,
                                             intensity: ReactionIntensity) -> str:
        """Generiert Kommunikationsempfehlungen für spezifische Stakeholder."""
        
        if reaction == ReactionType.HOSTILE:
            if stakeholder == StakeholderGroup.REGULATORS:
                return "Sofortige proaktive Kontaktaufnahme mit rechtlicher Absicherung"
            elif stakeholder == StakeholderGroup.MEDIA:
                return "Krisenkommunikationsplan aktivieren, Fakten vorbereiten"
            else:
                return "Deeskalationsstrategie mit direktem Dialog"
                
        elif reaction == ReactionType.CRITICAL:
            if intensity == ReactionIntensity.HIGH:
                return "Transparente Erklärung der Schutzmaßnahmen und Ethik-Prozesse"
            else:
                return "Sachliche Aufklärung über Nutzen und Sicherheitsvorkehrungen"
                
        elif reaction == ReactionType.SUPPORTIVE:
            if stakeholder == StakeholderGroup.MEDIA:
                return "Positive Story-Angles proaktiv anbieten"
            else:
                return "Erfolge kommunizieren und Unterstützer einbinden"
                
        return "Standard-Kommunikation mit Fokus auf Transparenz"
    
    def _calculate_cascade_risk(self, 
                               patterns: List[Tuple[str, Dict[str, Any], int]],
                               reactions: Dict[StakeholderGroup, Dict[str, Any]],
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet das Risiko von Kaskadeneffekten mit Context-Awareness."""
        
        # Basis-Kaskadenrisiko aus Mustern
        max_cascade_prob = 0.0
        critical_pattern = None
        
        for pattern_name, pattern, _ in patterns:
            if pattern["cascade_probability"] > max_cascade_prob:
                max_cascade_prob = pattern["cascade_probability"]
                critical_pattern = pattern_name
        
        # Verstärkungsfaktoren
        amplifying_factors = []
        
        # Medien + Kritische Reaktion = Verstärkung
        media_reaction = reactions.get(StakeholderGroup.MEDIA, {})
        if media_reaction.get("reaction") in [ReactionType.CRITICAL, ReactionType.HOSTILE]:
            amplifying_factors.append("media_amplification")
            max_cascade_prob *= 1.3
        
        # Mehrere kritische Gruppen
        critical_groups = sum(1 for r in reactions.values() 
                             if r.get("reaction") in [ReactionType.CRITICAL, ReactionType.HOSTILE])
        if critical_groups >= 3:
            amplifying_factors.append("multi_stakeholder_criticism")
            max_cascade_prob *= 1.2
        
        # Regulatoren kritisch = höheres Risiko
        if reactions.get(StakeholderGroup.REGULATORS, {}).get("reaction") == ReactionType.HOSTILE:
            amplifying_factors.append("regulatory_threat")
            max_cascade_prob *= 1.4
        
        # Context-Module Integration
        if self.use_context_modules:
            # VDD warnt vor Drift
            vdd_result = context.get("vdd_result", {})
            if vdd_result.get("drift_detected"):
                amplifying_factors.append("value_drift_detected")
                max_cascade_prob *= 1.15
            
            # DOF zeigt Langzeitrisiken
            dof_result = context.get("dof_result", {})
            if dof_result.get("highest_risk", 0) > 0.7:
                amplifying_factors.append("long_term_risks")
                max_cascade_prob *= 1.1
        
        # Normalisieren
        cascade_probability = min(max_cascade_prob, 0.95)
        
        # Kaskadengeschwindigkeit
        speed_factors = []
        for stakeholder, reaction in reactions.items():
            if reaction.get("reaction_speed") == "sehr_schnell":
                speed_factors.append(stakeholder.value)
        
        cascade_speed = "schnell" if len(speed_factors) >= 2 else "moderat"
        
        return {
            "probability": round(cascade_probability, 2),
            "critical_pattern": critical_pattern,
            "amplifying_factors": amplifying_factors,
            "cascade_speed": cascade_speed,
            "affected_stakeholders": critical_groups,
            "mitigation_priority": "hoch" if cascade_probability > 0.7 else "mittel" if cascade_probability > 0.4 else "niedrig"
        }
    
    def _aggregate_impact(self, reactions: Dict[StakeholderGroup, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregiert die Gesamtauswirkung aller Stakeholder-Reaktionen."""
        
        # Sammle gewichtete Reaktionen
        weighted_sentiment = 0.0
        total_influence = 0.0
        critical_groups = []
        supportive_groups = []
        
        reaction_scores = {
            ReactionType.SUPPORTIVE: 1.0,
            ReactionType.NEUTRAL: 0.0,
            ReactionType.CONCERNED: -0.3,
            ReactionType.CRITICAL: -0.7,
            ReactionType.HOSTILE: -1.0
        }
        
        intensity_multipliers = {
            ReactionIntensity.LOW: 0.5,
            ReactionIntensity.MODERATE: 1.0,
            ReactionIntensity.HIGH: 1.5,
            ReactionIntensity.EXTREME: 2.0
        }
        
        for stakeholder, reaction in reactions.items():
            influence = reaction["influence"]
            sentiment = reaction_scores.get(reaction["reaction"], 0.0)
            intensity_mult = intensity_multipliers.get(reaction["intensity"], 1.0)
            confidence = reaction["confidence"]
            
            # Gewichteter Sentiment mit Intensität
            weighted_sentiment += sentiment * influence * confidence * intensity_mult
            total_influence += influence
            
            # Identifiziere kritische/unterstützende Gruppen
            if reaction["reaction"] in [ReactionType.CRITICAL, ReactionType.HOSTILE]:
                critical_groups.append({
                    "stakeholder": stakeholder.value,
                    "intensity": reaction["intensity"].value,
                    "influence": influence
                })
                self.stats["critical_reactions"] += 1
            elif reaction["reaction"] == ReactionType.SUPPORTIVE:
                supportive_groups.append({
                    "stakeholder": stakeholder.value,
                    "intensity": reaction["intensity"].value,
                    "influence": influence
                })
        
        # Normalisiere
        if total_influence > 0:
            weighted_sentiment /= total_influence
        
        # Bestimme Gesamtbewertung
        if weighted_sentiment > 0.3:
            overall_assessment = "positive"
        elif weighted_sentiment > -0.3:
            overall_assessment = "mixed"
        else:
            overall_assessment = "negative"
        
        # Risikobewertung
        risk_level = 0.0
        for group in critical_groups:
            # Höheres Risiko bei kritischen Gruppen mit hohem Einfluss
            risk_level += group["influence"] * 0.3
            
            # Extremer Widerstand erhöht Risiko überproportional
            if group["intensity"] == "extrem":
                risk_level += 0.2
        
        risk_level = min(risk_level, 1.0)
        
        # Handlungsdringlichkeit
        urgency = "niedrig"
        if risk_level > 0.7 or len(critical_groups) >= 4:
            urgency = "hoch"
        elif risk_level > 0.4 or len(critical_groups) >= 2:
            urgency = "mittel"
        
        return {
            "overall_sentiment": round(weighted_sentiment, 3),
            "overall_assessment": overall_assessment,
            "risk_level": round(risk_level, 3),
            "critical_stakeholders": critical_groups,
            "supportive_stakeholders": supportive_groups,
            "action_urgency": urgency,
            "recommendation": self._generate_recommendation(weighted_sentiment, critical_groups, risk_level)
        }
    
    def _predict_temporal_dynamics(self, 
                                  reactions: Dict[StakeholderGroup, Dict[str, Any]],
                                  patterns: List[Tuple[str, Dict[str, Any], int]]) -> Dict[str, Any]:
        """Prognostiziert die zeitliche Entwicklung der Reaktionen."""
        
        # Reaktionsgeschwindigkeiten sammeln
        speed_timeline = {
            "immediate": [],  # < 24h
            "short_term": [],  # 1-7 Tage
            "medium_term": [],  # 1-4 Wochen
            "long_term": []  # > 1 Monat
        }
        
        speed_mapping = {
            "sehr_schnell": "immediate",
            "schnell": "short_term",
            "moderat": "medium_term",
            "langsam": "long_term",
            "variabel": "short_term"  # Konservative Annahme
        }
        
        for stakeholder, reaction in reactions.items():
            speed_category = speed_mapping.get(reaction["reaction_speed"], "medium_term")
            speed_timeline[speed_category].append({
                "stakeholder": stakeholder.value,
                "reaction": reaction["reaction"].value,
                "intensity": reaction["intensity"].value
            })
        
        # Peak-Impact Zeitpunkt
        immediate_critical = sum(1 for r in speed_timeline["immediate"] 
                               if r["reaction"] in ["kritisch", "ablehnend"])
        short_term_critical = sum(1 for r in speed_timeline["short_term"] 
                                if r["reaction"] in ["kritisch", "ablehnend"])
        
        if immediate_critical >= 2:
            peak_impact = "sofort"
        elif immediate_critical + short_term_critical >= 3:
            peak_impact = "innerhalb_einer_woche"
        else:
            peak_impact = "innerhalb_eines_monats"
        
        # Nachhaltigkeit der Reaktion
        high_volatility_count = sum(1 for r in reactions.values() if r.get("volatility", 0.5) > 0.7)
        
        if high_volatility_count >= len(reactions) / 2:
            reaction_persistence = "kurzlebig"
        else:
            reaction_persistence = "nachhaltig"
        
        return {
            "timeline": speed_timeline,
            "peak_impact_timing": peak_impact,
            "reaction_persistence": reaction_persistence,
            "first_movers": [r["stakeholder"] for r in speed_timeline["immediate"]],
            "escalation_window": "24-72 Stunden" if peak_impact == "sofort" else "1-2 Wochen"
        }
    
    def _calculate_prediction_confidence(self, 
                                       patterns: List[Tuple[str, Dict[str, Any], int]],
                                       context: Dict[str, Any]) -> float:
        """Berechnet die Konfidenz in die Vorhersage."""
        
        base_confidence = 0.7
        
        # Faktoren die Konfidenz erhöhen
        if patterns:
            # Klare Muster erkannt
            base_confidence += min(len(patterns) * 0.05, 0.15)
            
            # Starke Trigger-Übereinstimmung
            max_triggers = max(p[2] for p in patterns) if patterns else 0
            if max_triggers >= 3:
                base_confidence += 0.1
        
        # Kontextuelle Klarheit
        if context.get("domain"):
            base_confidence += 0.05
        
        # Historische Genauigkeit
        if self.pattern_statistics:
            accurate_patterns = sum(1 for p in self.pattern_statistics.values() 
                                  if p["triggered"] > 0 and p["accurate"] / p["triggered"] > 0.8)
            if accurate_patterns >= 3:
                base_confidence += 0.05
        
        # Faktoren die Konfidenz verringern
        if context.get("unprecedented", False):
            base_confidence -= 0.15
        
        if context.get("ambiguous", False):
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.3), 0.95)
    
    def _generate_recommendation(self, sentiment: float, critical_groups: List[Dict[str, Any]], 
                               risk_level: float) -> str:
        """Generiert eine Handlungsempfehlung basierend auf der Analyse."""
        
        if sentiment > 0.5 and risk_level < 0.3:
            return "Breite Unterstützung erwartet. Implementation mit positiver Kommunikation fortsetzen."
        
        elif sentiment > 0 and risk_level < 0.5:
            return "Überwiegend positive Reaktionen. Proaktive Kommunikation für Bedenkenträger empfohlen."
        
        elif sentiment > -0.5 and risk_level < 0.7:
            if critical_groups:
                groups_str = ", ".join([g["stakeholder"] for g in critical_groups[:3]])
                return f"Gemischte Reaktionen. Gezielte Stakeholder-Dialoge mit {groups_str} initiieren."
            return "Neutrale bis gemischte Reaktionen. Transparente Kommunikationsstrategie entwickeln."
        
        elif risk_level > 0.7:
            return "Erheblicher Widerstand erwartet. Grundlegende Überarbeitung oder Alternativansatz dringend empfohlen."
        
        else:
            return "Kritische Situation. Implementierung pausieren und umfassende Stakeholder-Konsultation durchführen."
    
    def _identify_key_stakeholders(self, reactions: Dict[StakeholderGroup, Dict[str, Any]]) -> List[str]:
        """Identifiziert die wichtigsten Stakeholder basierend auf Einfluss und Reaktion."""
        key_stakeholders = []
        
        # Sortiere nach Einfluss und Reaktionsintensität
        stakeholder_scores = []
        for stakeholder, reaction in reactions.items():
            # Score basiert auf Einfluss und Reaktionsstärke
            reaction_weight = {
                ReactionType.HOSTILE: 2.0,
                ReactionType.CRITICAL: 1.5,
                ReactionType.CONCERNED: 1.0,
                ReactionType.NEUTRAL: 0.5,
                ReactionType.SUPPORTIVE: 1.2
            }
            
            intensity_weight = {
                ReactionIntensity.EXTREME: 2.0,
                ReactionIntensity.HIGH: 1.5,
                ReactionIntensity.MODERATE: 1.0,
                ReactionIntensity.LOW: 0.5
            }
            
            score = (reaction["influence"] * 
                    reaction_weight.get(reaction["reaction"], 1.0) * 
                    intensity_weight.get(reaction["intensity"], 1.0))
            
            stakeholder_scores.append((stakeholder.value, score))
        
        # Sortiere und nimm Top 3
        stakeholder_scores.sort(key=lambda x: x[1], reverse=True)
        key_stakeholders = [s[0] for s in stakeholder_scores[:3]]
        
        return key_stakeholders
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über bisherige Vorhersagen zurück."""
        return {
            "total_predictions": self.stats["total_predictions"],
            "critical_reactions": self.stats["critical_reactions"],
            "cascade_events": self.stats["cascade_events"],
            "average_risk": self.stats["average_risk"],
            "pattern_accuracy": self._calculate_pattern_accuracy()
        }
    
    def _calculate_pattern_accuracy(self) -> Dict[str, float]:
        """Berechnet Genauigkeit der Muster."""
        accuracy = {}
        for pattern, stats in self.pattern_statistics.items():
            if stats["triggered"] > 0:
                accuracy[pattern] = stats["accurate"] / stats["triggered"]
        return accuracy


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale Predictor-Instanz
_predictor_instance: Optional[StakeholderBehaviorPredictor] = None

def _get_predictor_instance(config: Optional[Dict[str, Any]] = None) -> StakeholderBehaviorPredictor:
    """Lazy-Loading der Predictor-Instanz."""
    global _predictor_instance
    if _predictor_instance is None or config is not None:
        _predictor_instance = StakeholderBehaviorPredictor(config)
    return _predictor_instance


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
        # SBP-Konfiguration aus Context
        sbp_config = context.get("config", {}).get("sbp", {})
        
        # Predictor-Instanz
        predictor = _get_predictor_instance(sbp_config)
        
        # Profil aus Context
        profile = context.get("profile", profiles.get_default_profile())
        
        # Log Start
        if log_manager:
            log_manager.log_event(
                "SBP",
                f"Starte Stakeholder-Vorhersage (detail={predictor.detail_level})",
                "INFO"
            )
        
        # Text vorbereiten - kombiniere Input und Response
        decision_text = input_text
        if context.get("response"):
            # Analysiere die geplante Aktion/Antwort
            decision_text = f"{input_text} -> {context['response']}"
        elif context.get("decision"):
            # Fallback auf explizite Entscheidung
            decision_text = context["decision"]
        
        # Erweitere Context für SBP
        sbp_context = {
            "domain": context.get("domain"),
            "public_attention": context.get("public_attention", False),
            "previous_incidents": context.get("previous_incidents", 0),
            "urgent": context.get("urgent", False),
            "ambiguous": context.get("ambiguous", False),
            "unprecedented": context.get("unprecedented", False)
        }
        
        # Führe Vorhersage durch
        prediction = predictor.predict_reactions(decision_text, context)
        
        # Erstelle SBP-Ergebnis
        sbp_result = {
            "overall_assessment": prediction["aggregate_impact"]["overall_assessment"],
            "risk_level": prediction["aggregate_impact"]["risk_level"],
            "action_urgency": prediction["aggregate_impact"]["action_urgency"],
            "recommendation": prediction["aggregate_impact"]["recommendation"],
            "negative_reaction_probability": prediction["negative_reaction_probability"],
            "positive_reaction_probability": prediction["positive_reaction_probability"],
            "key_stakeholders": prediction["key_stakeholders"],
            "confidence": prediction["confidence"],
            "triggered_patterns": prediction["triggered_patterns"]
        }
        
        # Detail-Level beachten
        if predictor.detail_level == "high":
            sbp_result.update({
                "stakeholder_reactions": prediction["stakeholder_reactions"],
                "cascade_risk": prediction["cascade_risk"],
                "temporal_dynamics": prediction["temporal_dynamics"],
                "critical_stakeholders": prediction["aggregate_impact"]["critical_stakeholders"],
                "supportive_stakeholders": prediction["aggregate_impact"]["supportive_stakeholders"]
            })
        elif predictor.detail_level == "medium":
            sbp_result.update({
                "critical_stakeholders": prediction["aggregate_impact"]["critical_stakeholders"][:3],
                "supportive_stakeholders": prediction["aggregate_impact"]["supportive_stakeholders"][:3],
                "cascade_probability": prediction.get("cascade_risk", {}).get("probability", 0)
            })
        
        # Speichere im Context
        context["sbp_result"] = sbp_result
        
        # Log Ergebnis
        if log_manager:
            log_manager.log_event(
                "SBP",
                f"Vorhersage abgeschlossen - Assessment: {sbp_result['overall_assessment']}, "
                f"Risiko: {sbp_result['risk_level']:.2%}, "
                f"Konfidenz: {sbp_result['confidence']:.2f}",
                "INFO"
            )
            
            if sbp_result["risk_level"] > 0.7:
                log_manager.log_event(
                    "SBP",
                    f"WARNUNG: Hohes Stakeholder-Risiko - {sbp_result['recommendation']}",
                    "WARNING"
                )
        
        return {
            "success": True,
            "result": sbp_result,
            "module": "sbp",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"SBP error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("SBP", error_msg, "ERROR")
        
        # Fehler-Fallback
        context["sbp_result"] = {
            "error": True,
            "error_message": error_msg,
            "overall_assessment": "unknown",
            "risk_level": 0.5,
            "confidence": 0.0,
            "recommendation": "Analyse fehlgeschlagen - manuelle Bewertung erforderlich"
        }
        
        return {
            "success": False,
            "error": error_msg,
            "module": "sbp",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die Verwendung des SBP-Moduls."""
    print("=== INTEGRA SBP (Stakeholder Behavior Predictor) Demo v2.0 ===")
    print("Standardisierte Baukasten-Integration\n")
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test-Szenarien
    test_scenarios = [
        {
            "name": "Ethische Innovation",
            "text": "Transparente und faire KI-Entscheidungen",
            "context": {
                "profile": test_profile.copy(),
                "response": "Ich implementiere vollständig transparente und ethische KI-Lösungen",
                "domain": "general"
            }
        },
        {
            "name": "Datenschutz-Problem mit Context-Integration",
            "text": "Heimliche Datenanalyse durchführen",
            "context": {
                "profile": test_profile.copy(),
                "response": "Ich speichere und analysiere private Nutzerdaten ohne Einwilligung",
                "previous_incidents": 1,
                "simple_ethics_result": {
                    "overall_score": 0.3,
                    "violations": ["governance", "integrity"]
                },
                "nga_result": {
                    "overall_compliance": 0.2,
                    "violations": [{"framework": "gdpr", "severity": "critical"}]
                }
            }
        },
        {
            "name": "Kinder-Automation mit hoher Aufmerksamkeit",
            "text": "KI für Kindererziehung",
            "context": {
                "profile": test_profile.copy(),
                "response": "KI trifft selbstständig Erziehungsentscheidungen für minderjährige Nutzer",
                "domain": "education",
                "public_attention": True,
                "uia_result": {
                    "detected_intention": "manipulative",
                    "risk_flag": True
                }
            }
        },
        {
            "name": "Diskriminierungsrisiko mit Cascade",
            "text": "Algorithmus-basierte Entscheidungen",
            "context": {
                "profile": test_profile.copy(),
                "response": "Algorithmus könnte bestimmte Gruppen systematisch benachteiligen",
                "domain": "hr",
                "ambiguous": True,
                "dof_result": {
                    "highest_risk": 0.8,
                    "critical_count": 3
                },
                "vdd_result": {
                    "drift_detected": True,
                    "drift_type": "value_drift"
                }
            }
        },
        {
            "name": "Test verschiedene Detail-Level",
            "text": "Standardentscheidung treffen",
            "context": {
                "profile": test_profile.copy(),
                "config": {
                    "sbp": {
                        "detail_level": "low",
                        "include_cascade": False
                    }
                }
            }
        },
        {
            "name": "Fokus auf spezifische Stakeholder",
            "text": "Neue Technologie einführen",
            "context": {
                "profile": test_profile.copy(),
                "response": "Innovative aber kontroverse Technologie implementieren",
                "config": {
                    "sbp": {
                        "detail_level": "high",
                        "focus_stakeholders": ["regulatoren", "medien", "nutzer"]
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
            print(f"Geplante Aktion: {scenario['context']['response'][:60]}...")
        
        # Führe SBP durch
        result = run_module(scenario["text"], scenario["context"])
        
        if result["success"]:
            sbp_result = result["result"]
            
            print(f"\n📊 Stakeholder-Analyse:")
            print(f"  Gesamtbewertung: {sbp_result['overall_assessment'].upper()}")
            print(f"  Risiko-Level: {sbp_result['risk_level']:.0%}")
            print(f"  Handlungsdringlichkeit: {sbp_result['action_urgency']}")
            print(f"  Konfidenz: {sbp_result['confidence']:.2f}")
            
            # Reaktionswahrscheinlichkeiten
            print(f"\n📈 Reaktionswahrscheinlichkeiten:")
            print(f"  Negativ: {sbp_result['negative_reaction_probability']:.0%}")
            print(f"  Positiv: {sbp_result['positive_reaction_probability']:.0%}")
            
            # Key Stakeholders
            if sbp_result.get("key_stakeholders"):
                print(f"\n👥 Wichtigste Stakeholder:")
                for stakeholder in sbp_result["key_stakeholders"][:3]:
                    print(f"  - {stakeholder}")
            
            # Triggered Patterns
            if sbp_result.get("triggered_patterns"):
                print(f"\n🔍 Erkannte Muster:")
                for pattern, count in sbp_result["triggered_patterns"][:3]:
                    print(f"  - {pattern} ({count}x)")
            
            # Bei hohem Detail-Level
            if "cascade_risk" in sbp_result:
                cascade = sbp_result["cascade_risk"]
                print(f"\n⚡ Kaskadenrisiko:")
                print(f"  Wahrscheinlichkeit: {cascade['probability']:.0%}")
                print(f"  Geschwindigkeit: {cascade['cascade_speed']}")
                if cascade.get("amplifying_factors"):
                    print(f"  Verstärkende Faktoren: {', '.join(cascade['amplifying_factors'])}")
            
            # Kritische Stakeholder
            if "critical_stakeholders" in sbp_result:
                critical = sbp_result["critical_stakeholders"]
                if critical:
                    print(f"\n❌ Kritische Gruppen ({len(critical)}):")
                    for group in critical[:3]:
                        print(f"  - {group['stakeholder']}: {group['intensity']} (Einfluss: {group['influence']:.1f})")
            
            # Context-Integration
            print(f"\n🔗 Context-Integration:")
            integrations = []
            if "simple_ethics_result" in scenario["context"]:
                integrations.append("Ethics")
            if "nga_result" in scenario["context"]:
                integrations.append("NGA")
            if "uia_result" in scenario["context"]:
                integrations.append("UIA")
            if "dof_result" in scenario["context"]:
                integrations.append("DOF")
            if "vdd_result" in scenario["context"]:
                integrations.append("VDD")
            
            if integrations:
                print(f"  Genutzte Module: {', '.join(integrations)}")
            
            print(f"\n💡 Empfehlung:")
            print(f"  {sbp_result['recommendation']}")
        else:
            print(f"\n❌ Fehler: {result['error']}")
    
    # Statistiken demonstrieren
    print(f"\n\n{'='*70}")
    print("📈 Vorhersage-Statistiken:")
    
    predictor = _get_predictor_instance()
    stats = predictor.get_prediction_stats()
    
    print(f"  Gesamt-Vorhersagen: {stats['total_predictions']}")
    print(f"  Kritische Reaktionen: {stats['critical_reactions']}")
    print(f"  Kaskaden-Events: {stats['cascade_events']}")
    print(f"  Durchschn. Risiko: {stats['average_risk']:.2%}")
    
    if stats["pattern_accuracy"]:
        print(f"\n  Muster-Genauigkeit:")
        for pattern, accuracy in list(stats["pattern_accuracy"].items())[:3]:
            print(f"    - {pattern}: {accuracy:.1%}")
    
    print("\n✅ SBP Demo v2.0 abgeschlossen!")
    print("\nDas Modul bietet:")
    print("  • Standardisierte Baukasten-Schnittstelle")
    print("  • Umfassende Context-Integration")
    print("  • Nutzung von Ethics, NGA, UIA, DOF, VDD Ergebnissen")
    print("  • Detaillierte Stakeholder-Reaktionsanalyse")
    print("  • Kaskadenrisiko-Bewertung")
    print("  • Anpassbare Detail-Level und Fokus-Stakeholder")


if __name__ == "__main__":
    demo()