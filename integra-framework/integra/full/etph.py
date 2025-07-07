# -*- coding: utf-8 -*-
"""
Modulname: etph.py
Beschreibung: Ethical Time Pressure Handler - Schützt ethische Entscheidungen unter Zeitdruck
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

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time

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


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class PressureLevel(Enum):
    """Definiert Zeitdruck-Stufen."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResponseStrategy(Enum):
    """Definiert Reaktionsstrategien bei Zeitdruck."""
    NORMAL = "normal"
    SIMPLIFIED = "simplified"
    FALLBACK = "fallback"
    DEFENSIVE = "defensive"
    EMERGENCY = "emergency"


@dataclass
class TimeAnalysis:
    """Container für Zeit-Analyse."""
    available_time: float
    required_time: float
    time_budget_ratio: float
    pressure_level: PressureLevel
    urgency_indicators: List[str] = field(default_factory=list)
    confidence: float = 0.8


@dataclass
class PressureResponse:
    """Container für Zeitdruck-Reaktion."""
    decision_adjusted: bool
    strategy: ResponseStrategy
    risk_level: float
    pressure_index: float
    original_input: str
    output: str
    modifications: List[str] = field(default_factory=list)
    logs: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================================
# TIME PRESSURE ANALYZER
# ============================================================================

class TimePressureAnalyzer:
    """Analysiert und bewertet Zeitdruck."""
    
    # Zeitdruck-Indikatoren
    URGENCY_KEYWORDS = {
        "extreme": ["sofort", "immediately", "jetzt gleich", "right now", "notfall", "emergency", "ASAP", "dringendst"],
        "high": ["schnell", "quickly", "dringend", "urgent", "eilig", "hurry", "beeilen", "rasch"],
        "medium": ["bald", "soon", "zeitnah", "shortly", "rasch", "promptly", "demnächst"],
        "low": ["wenn möglich", "when possible", "gelegentlich", "occasionally", "bei gelegenheit"]
    }
    
    # Geschätzte Verarbeitungszeiten (in Sekunden)
    PROCESSING_TIMES = {
        "simple_analysis": 0.5,
        "ethics_check": 1.0,
        "deep_analysis": 2.0,
        "conflict_resolution": 3.0,
        "full_evaluation": 5.0,
        "meta_learning": 1.5,
        "dof_forecast": 2.5,
        "aso_optimization": 1.0
    }
    
    def analyze_time_pressure(self, input_text: str, context: Dict[str, Any]) -> TimeAnalysis:
        """
        Analysiert Zeitdruck basierend auf Input und Kontext.
        
        Args:
            input_text: Benutzereingabe
            context: Kontext mit optionalem time_budget
            
        Returns:
            TimeAnalysis mit Bewertung
        """
        # Zeit-Budget aus Kontext oder Default
        time_budget = context.get("time_budget", 5.0)
        urgency_level = context.get("urgency_level", "normal")
        
        # Response-Zeit Vorgabe aus Context
        max_response_time = context.get("max_response_time", None)
        if max_response_time:
            time_budget = min(time_budget, max_response_time)
        
        # Urgency aus Text erkennen
        urgency_indicators = self._detect_urgency_indicators(input_text)
        
        # Benötigte Zeit schätzen (basierend auf aktivierten Modulen)
        required_time = self._estimate_required_time(input_text, context)
        
        # Zeit-Budget-Verhältnis
        ratio = time_budget / required_time if required_time > 0 else 1.0
        
        # Pressure Level bestimmen
        pressure_level = self._determine_pressure_level(ratio, urgency_indicators, urgency_level)
        
        # Konfidenz berechnen
        confidence = self._calculate_confidence(urgency_indicators, time_budget, context)
        
        return TimeAnalysis(
            available_time=time_budget,
            required_time=required_time,
            time_budget_ratio=ratio,
            pressure_level=pressure_level,
            urgency_indicators=urgency_indicators,
            confidence=confidence
        )
    
    def _detect_urgency_indicators(self, text: str) -> List[str]:
        """Erkennt Dringlichkeits-Indikatoren im Text."""
        indicators = []
        text_lower = text.lower()
        
        for level, keywords in self.URGENCY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    indicators.append(f"{level}:{keyword}")
        
        # Zusätzliche Muster
        if "!" in text and text.count("!") > 2:
            indicators.append("extreme:multiple_exclamation")
        
        if any(word in text_lower for word in ["leben", "tod", "sterben", "life", "death"]):
            indicators.append("extreme:life_critical")
        
        return indicators
    
    def _estimate_required_time(self, text: str, context: Dict[str, Any]) -> float:
        """Schätzt benötigte Verarbeitungszeit basierend auf aktiven Modulen."""
        base_time = self.PROCESSING_TIMES["simple_analysis"]
        
        # Komplexität des Inputs
        if len(text) > 200:
            base_time += 0.5
        if len(text) > 500:
            base_time += 1.0
        
        # Berücksichtige Ergebnisse anderer Module
        
        # ETB - Konfliktlösung benötigt
        if context.get("etb_result", {}).get("conflicts_detected"):
            base_time += self.PROCESSING_TIMES["conflict_resolution"]
        
        # VDD - Drift-Analyse läuft
        if context.get("vdd_result", {}).get("drift_detected"):
            base_time += 0.5  # Zusätzliche Überprüfung
        
        # Meta-Learning aktiv
        if context.get("meta_learner_result", {}).get("learning_triggered", False):
            base_time += self.PROCESSING_TIMES["meta_learning"]
        
        # DOF - Langzeitprognose angefordert
        if context.get("config", {}).get("dof", {}).get("enabled", True):
            base_time += self.PROCESSING_TIMES["dof_forecast"]
        
        # ASO - Optimierung läuft
        if context.get("aso_result", {}).get("optimization_cycle", 0) > 0:
            base_time += self.PROCESSING_TIMES["aso_optimization"]
        
        # Deep Path erkannt
        if context.get("decision_path") == "deep":
            base_time += self.PROCESSING_TIMES["deep_analysis"]
        
        return base_time
    
    def _determine_pressure_level(self, ratio: float, indicators: List[str], 
                                 urgency: str) -> PressureLevel:
        """Bestimmt Pressure Level unter Berücksichtigung aller Faktoren."""
        # Basis auf Ratio
        if ratio < 0.2:
            base_level = PressureLevel.CRITICAL
        elif ratio < 0.5:
            base_level = PressureLevel.HIGH
        elif ratio < 0.8:
            base_level = PressureLevel.MEDIUM
        elif ratio < 1.2:
            base_level = PressureLevel.LOW
        else:
            base_level = PressureLevel.MINIMAL
        
        # Anpassung durch explizite Urgency
        if urgency == "critical":
            if base_level.value in ["minimal", "low", "medium"]:
                return PressureLevel.HIGH
        
        # Anpassung durch Text-Indikatoren
        extreme_count = sum(1 for ind in indicators if ind.startswith("extreme:"))
        if extreme_count >= 2:
            return PressureLevel.CRITICAL
        elif extreme_count == 1:
            if base_level.value in ["minimal", "low"]:
                return PressureLevel.MEDIUM
            elif base_level.value == "medium":
                return PressureLevel.HIGH
        
        # Life-critical immer CRITICAL
        if any("life_critical" in ind for ind in indicators):
            return PressureLevel.CRITICAL
        
        return base_level
    
    def _calculate_confidence(self, indicators: List[str], time_budget: float,
                            context: Dict[str, Any]) -> float:
        """Berechnet Konfidenz der Zeitanalyse."""
        confidence = 0.8
        
        # Klare Indikatoren erhöhen Konfidenz
        if indicators:
            confidence += min(0.15, len(indicators) * 0.05)
        
        # Sehr kurze oder lange Zeitbudgets reduzieren Konfidenz
        if time_budget < 0.5:
            confidence -= 0.2
        elif time_budget > 30:
            confidence -= 0.1
        
        # Konsistenz mit anderen Modulen
        if context.get("aso_result", {}).get("system_performance", {}).get("level") == "critical":
            confidence += 0.1  # System kennt seine Grenzen
        
        return max(0.3, min(0.95, confidence))


# ============================================================================
# STRATEGY SELECTOR
# ============================================================================

class StrategySelector:
    """Wählt optimale Strategie basierend auf Zeitdruck und Risiko."""
    
    def __init__(self):
        # Erweiterte Strategie-Matrix
        self.strategy_matrix = {
            PressureLevel.CRITICAL: {
                "high_risk": ResponseStrategy.EMERGENCY,
                "medium_risk": ResponseStrategy.DEFENSIVE,
                "low_risk": ResponseStrategy.DEFENSIVE
            },
            PressureLevel.HIGH: {
                "high_risk": ResponseStrategy.DEFENSIVE,
                "medium_risk": ResponseStrategy.FALLBACK,
                "low_risk": ResponseStrategy.SIMPLIFIED
            },
            PressureLevel.MEDIUM: {
                "high_risk": ResponseStrategy.SIMPLIFIED,
                "medium_risk": ResponseStrategy.SIMPLIFIED,
                "low_risk": ResponseStrategy.NORMAL
            },
            PressureLevel.LOW: {
                "high_risk": ResponseStrategy.NORMAL,
                "medium_risk": ResponseStrategy.NORMAL,
                "low_risk": ResponseStrategy.NORMAL
            },
            PressureLevel.MINIMAL: {
                "high_risk": ResponseStrategy.NORMAL,
                "medium_risk": ResponseStrategy.NORMAL,
                "low_risk": ResponseStrategy.NORMAL
            }
        }
    
    def select_strategy(self, pressure: PressureLevel, risk_score: float,
                       context: Dict[str, Any]) -> ResponseStrategy:
        """
        Wählt Reaktionsstrategie unter Berücksichtigung des Gesamtkontexts.
        
        Args:
            pressure: Zeitdruck-Level
            risk_score: Ethisches Risiko (0-1)
            context: Vollständiger Kontext
            
        Returns:
            Gewählte Strategie
        """
        # Risiko-Kategorie bestimmen
        if risk_score > 0.7:
            risk_category = "high_risk"
        elif risk_score > 0.4:
            risk_category = "medium_risk"
        else:
            risk_category = "low_risk"
        
        # Basis-Strategie aus Matrix
        base_strategy = self.strategy_matrix[pressure].get(
            risk_category, ResponseStrategy.NORMAL
        )
        
        # Kontext-basierte Anpassungen
        
        # Bei kritischen DOF-Prognosen konservativer
        dof_result = context.get("dof_result", {})
        if dof_result.get("critical_count", 0) > 2:
            if base_strategy == ResponseStrategy.NORMAL:
                base_strategy = ResponseStrategy.SIMPLIFIED
            elif base_strategy == ResponseStrategy.SIMPLIFIED:
                base_strategy = ResponseStrategy.DEFENSIVE
        
        # Bei System-Performance-Problemen vorsichtiger
        aso_result = context.get("aso_result", {})
        if aso_result.get("system_performance", {}).get("level") in ["critical", "poor"]:
            if base_strategy in [ResponseStrategy.NORMAL, ResponseStrategy.SIMPLIFIED]:
                base_strategy = ResponseStrategy.FALLBACK
        
        return base_strategy


# ============================================================================
# RESPONSE GENERATOR
# ============================================================================

class PressureResponseGenerator:
    """Generiert angepasste Antworten basierend auf Zeitdruck."""
    
    # Erweiterte Templates
    RESPONSE_TEMPLATES = {
        ResponseStrategy.EMERGENCY: {
            "default": "⚠️ NOTFALL-MODUS: Aufgrund extremen Zeitdrucks wurde eine Sicherheitsantwort gewählt. "
                      "Bitte überprüfen Sie diese Entscheidung, sobald mehr Zeit verfügbar ist.",
            "ethical": "⚠️ KRITISCH: Ethische Schnellbewertung unter Extrembedingungen. "
                      "Empfehle sofortige Schadensvermeidung, detaillierte Analyse folgt.",
            "system": "⚠️ SYSTEM-NOTFALL: Minimale Verarbeitung aktiviert. "
                     "Nur essenzielle Sicherheitsprüfungen durchgeführt."
        },
        ResponseStrategy.DEFENSIVE: {
            "default": "Unter dem gegebenen Zeitdruck empfehle ich eine vorsichtige Herangehensweise. "
                      "Eine vollständige Analyse würde {time:.1f} Sekunden benötigen.",
            "ethical": "Diese ethische Frage erfordert mehr Zeit für eine fundierte Antwort. "
                      "Vorläufige Empfehlung: Vorsichtsprinzip anwenden.",
            "risk": "Aufgrund des Zeitdrucks kann ich nur eine vorläufige Einschätzung geben. "
                   "Risikohinweis: {risk_level}"
        },
        ResponseStrategy.FALLBACK: {
            "default": "Greife auf bewährte Standardprozedur zurück (Zeitdruck: {pressure:.0%}). "
                      "Detailanalyse würde {time:.1f}s benötigen.",
            "pattern": "Nutze erkanntes Muster '{pattern}' für schnelle Antwort. "
                      "Vollständige Analyse bei Bedarf möglich."
        },
        ResponseStrategy.SIMPLIFIED: {
            "default": "Vereinfachte Analyse durchgeführt. Kernpunkte: {key_points}",
            "modules": "Module übersprungen: {skipped_modules}. Essenzielle Prüfungen durchgeführt."
        },
        ResponseStrategy.NORMAL: {
            "default": "Normale Verarbeitung möglich. Alle Module aktiv.",
            "complete": "Vollständige Analyse mit allen verfügbaren Modulen durchgeführt."
        }
    }
    
    def generate_response(self, strategy: ResponseStrategy, original_input: str,
                         pressure_index: float, modifications: List[str],
                         context: Dict[str, Any]) -> str:
        """Generiert kontextangepasste Antwort."""
        
        # Template-Auswahl basierend auf Kontext
        template_key = self._select_template_key(strategy, original_input, context)
        template = self.RESPONSE_TEMPLATES[strategy].get(
            template_key, 
            self.RESPONSE_TEMPLATES[strategy]["default"]
        )
        
        # Template-Variablen füllen
        response = self._fill_template(
            template, pressure_index, modifications, context
        )
        
        # Zusätzliche Informationen anhängen
        if strategy in [ResponseStrategy.DEFENSIVE, ResponseStrategy.FALLBACK]:
            response += self._append_mitigation_info(context)
        
        return response
    
    def _select_template_key(self, strategy: ResponseStrategy, input_text: str,
                           context: Dict[str, Any]) -> str:
        """Wählt passendes Template basierend auf Kontext."""
        input_lower = input_text.lower()
        
        # Ethik-bezogen?
        if any(word in input_lower for word in ["ethik", "moral", "richtig", "falsch", "ethics"]):
            return "ethical"
        
        # System-kritisch?
        if context.get("aso_result", {}).get("system_performance", {}).get("level") == "critical":
            return "system"
        
        # Risiko-bezogen?
        if context.get("simple_ethics_result", {}).get("overall_score", 1.0) < 0.5:
            return "risk"
        
        # Pattern verfügbar?
        if (strategy == ResponseStrategy.FALLBACK and 
            context.get("meta_learner_result", {}).get("patterns", {}).get("total", 0) > 0):
            return "pattern"
        
        # Module übersprungen?
        if strategy == ResponseStrategy.SIMPLIFIED and context.get("modules_skipped"):
            return "modules"
        
        return "default"
    
    def _fill_template(self, template: str, pressure_index: float,
                      modifications: List[str], context: Dict[str, Any]) -> str:
        """Füllt Template mit konkreten Werten."""
        # Verfügbare Variablen
        fill_vars = {
            "pressure": pressure_index,
            "time": context.get("required_time", 0),
            "risk_level": self._format_risk_level(context.get("risk_level", 0)),
            "pattern": self._get_dominant_pattern(context),
            "key_points": self._extract_key_points(context),
            "skipped_modules": ", ".join(context.get("modules_skipped", [])) or "keine"
        }
        
        # Safe formatting
        try:
            return template.format(**fill_vars)
        except KeyError:
            return template
    
    def _format_risk_level(self, risk: float) -> str:
        """Formatiert Risiko-Level für Ausgabe."""
        if risk > 0.8:
            return "sehr hoch"
        elif risk > 0.6:
            return "hoch"
        elif risk > 0.4:
            return "mittel"
        elif risk > 0.2:
            return "niedrig"
        else:
            return "minimal"
    
    def _get_dominant_pattern(self, context: Dict[str, Any]) -> str:
        """Extrahiert dominantes Muster aus Meta-Learner."""
        patterns = context.get("meta_learner_result", {}).get("patterns", {}).get("recent", [])
        if patterns:
            return patterns[0].get("type", "Standard")
        return "Standard"
    
    def _extract_key_points(self, context: Dict[str, Any]) -> str:
        """Extrahiert Kernpunkte für vereinfachte Darstellung."""
        points = []
        
        # Ethik-Score
        ethics_score = context.get("simple_ethics_result", {}).get("overall_score", 1.0)
        if ethics_score < 0.5:
            points.append("Ethische Bedenken")
        
        # Konflikte
        if context.get("etb_result", {}).get("conflicts_detected"):
            points.append("Wertekonflikt erkannt")
        
        # Drift
        if context.get("vdd_result", {}).get("drift_detected"):
            points.append("Wertedrift beobachtet")
        
        return ", ".join(points) if points else "Keine kritischen Punkte"
    
    def _append_mitigation_info(self, context: Dict[str, Any]) -> str:
        """Fügt Mitigationsinformationen hinzu."""
        info = "\n\n💡 Empfohlene Folgemaßnahmen: "
        
        recommendations = []
        
        # Bei hohem Zeitdruck
        if context.get("pressure_index", 0) > 0.7:
            recommendations.append("Entscheidung bei mehr Zeit überprüfen")
        
        # Bei ethischen Bedenken
        if context.get("risk_level", 0) > 0.5:
            recommendations.append("Ethik-Review durchführen")
        
        # Bei übersprungenen Modulen
        if context.get("modules_skipped"):
            recommendations.append("Vollständige Analyse nachholen")
        
        return info + "; ".join(recommendations) if recommendations else ""


# ============================================================================
# MAIN TIME PRESSURE HANDLER
# ============================================================================

class EthicalTimePressureHandler:
    """Hauptklasse für Zeitdruck-Management."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisiert den Handler."""
        self.config = config or {}
        self.analyzer = TimePressureAnalyzer()
        self.selector = StrategySelector()
        self.generator = PressureResponseGenerator()
        
        # Konfiguration
        self.pressure_threshold = self.config.get("pressure_threshold", 0.5)
        self.risk_threshold = self.config.get("risk_threshold", 0.3)
        self.enable_module_skipping = self.config.get("enable_module_skipping", True)
        
        # Statistiken
        self.stats = {
            "total_handled": 0,
            "strategies_used": {},
            "average_pressure": 0.0,
            "modules_skipped": 0
        }
    
    def handle_time_pressure(self, input_text: str, context: Dict[str, Any]) -> PressureResponse:
        """
        Hauptmethode zur Zeitdruck-Behandlung.
        
        Args:
            input_text: Eingabetext
            context: Vollständiger Kontext mit Modul-Ergebnissen
            
        Returns:
            PressureResponse mit Anpassungen
        """
        self.stats["total_handled"] += 1
        
        # Zeit-Analyse
        time_analysis = self.analyzer.analyze_time_pressure(input_text, context)
        
        # Risiko-Bewertung (nutzt andere Module)
        risk_level = self._assess_risk_level(input_text, context)
        
        # Pressure Index berechnen
        pressure_index = self._calculate_pressure_index(time_analysis, risk_level)
        
        # Strategie wählen
        strategy = self.selector.select_strategy(
            time_analysis.pressure_level, risk_level, context
        )
        
        # Modifikationen bestimmen
        modifications = self._determine_modifications(
            strategy, time_analysis, context
        )
        
        # Module-Skipping Empfehlungen
        if self.enable_module_skipping:
            skip_recommendations = self._recommend_module_skipping(
                strategy, time_analysis, context
            )
            context["recommended_module_skip"] = skip_recommendations
            if skip_recommendations:
                self.stats["modules_skipped"] += len(skip_recommendations)
        
        # Response generieren
        context_enhanced = {
            **context,
            "pressure_index": pressure_index,
            "risk_level": risk_level,
            "required_time": time_analysis.required_time,
            "modules_skipped": modifications
        }
        
        output = self.generator.generate_response(
            strategy, input_text, pressure_index, modifications, context_enhanced
        )
        
        # Logs erstellen
        logs = self._create_logs(time_analysis, strategy, modifications, risk_level)
        
        # Statistiken aktualisieren
        self._update_stats(strategy, pressure_index)
        
        return PressureResponse(
            decision_adjusted=(strategy != ResponseStrategy.NORMAL),
            strategy=strategy,
            risk_level=risk_level,
            pressure_index=pressure_index,
            original_input=input_text,
            output=output,
            modifications=modifications,
            logs=logs
        )
    
    def _assess_risk_level(self, text: str, context: Dict[str, Any]) -> float:
        """Bewertet ethisches Risiko unter Nutzung aller verfügbaren Module."""
        risk = 0.0
        
        # Basis-Risiko aus Simple Ethics
        ethics_result = context.get("simple_ethics_result", {})
        if ethics_result:
            ethics_score = ethics_result.get("overall_score", 1.0)
            if ethics_score < 0.5:
                risk += (1.0 - ethics_score) * 0.4
        
        # ETB Konflikte
        etb_result = context.get("etb_result", {})
        if etb_result.get("conflicts_detected"):
            conflicts = etb_result.get("conflicts", [])
            risk += min(0.3, len(conflicts) * 0.1)
        
        # VDD Drift
        vdd_result = context.get("vdd_result", {})
        if vdd_result.get("drift_detected"):
            drift_severity = vdd_result.get("drift_analysis", {}).get("overall_drift", 0)
            risk += drift_severity * 0.2
        
        # DOF kritische Outcomes
        dof_result = context.get("dof_result", {})
        if dof_result.get("critical_count", 0) > 0:
            risk += min(0.3, dof_result["critical_count"] * 0.1)
        
        # Text-basierte Risiken
        risk_keywords = ["gefahr", "schaden", "illegal", "verletzung", "risiko", 
                        "kritisch", "warnung", "vorsicht", "damage", "harm"]
        text_lower = text.lower()
        for keyword in risk_keywords:
            if keyword in text_lower:
                risk += 0.1
                break
        
        # ASO System-Performance
        aso_result = context.get("aso_result", {})
        if aso_result.get("system_performance", {}).get("level") in ["critical", "poor"]:
            risk += 0.15
        
        return min(1.0, risk)
    
    def _calculate_pressure_index(self, time_analysis: TimeAnalysis, 
                                 risk_level: float) -> float:
        """Berechnet kombinierten Pressure Index."""
        # Zeit-Komponente (0-1)
        time_pressure = 1.0 - min(1.0, time_analysis.time_budget_ratio)
        
        # Risiko-Komponente
        risk_factor = risk_level * 0.3
        
        # Urgency-Komponente
        urgency_factor = min(0.3, len(time_analysis.urgency_indicators) * 0.1)
        
        # Pressure Level Komponente
        level_factors = {
            PressureLevel.MINIMAL: 0.0,
            PressureLevel.LOW: 0.1,
            PressureLevel.MEDIUM: 0.2,
            PressureLevel.HIGH: 0.3,
            PressureLevel.CRITICAL: 0.4
        }
        level_factor = level_factors.get(time_analysis.pressure_level, 0.2)
        
        # Kombinieren mit Gewichtung
        pressure_index = (
            time_pressure * 0.4 +
            risk_factor * 0.3 +
            urgency_factor * 0.2 +
            level_factor * 0.1
        )
        
        return min(1.0, pressure_index)
    
    def _determine_modifications(self, strategy: ResponseStrategy,
                               time_analysis: TimeAnalysis,
                               context: Dict[str, Any]) -> List[str]:
        """Bestimmt durchgeführte Modifikationen."""
        mods = []
        
        if strategy == ResponseStrategy.EMERGENCY:
            mods.extend([
                "emergency_mode_activated",
                "all_non_critical_bypassed",
                "minimal_processing_only"
            ])
        
        elif strategy == ResponseStrategy.DEFENSIVE:
            mods.extend([
                "risk_minimization_active",
                "conservative_defaults_applied",
                "enhanced_safety_checks"
            ])
        
        elif strategy == ResponseStrategy.FALLBACK:
            mods.extend([
                "pattern_based_response",
                "historical_data_used",
                "detailed_analysis_skipped"
            ])
        
        elif strategy == ResponseStrategy.SIMPLIFIED:
            mods.extend([
                "deep_modules_bypassed",
                "basic_checks_only",
                "streamlined_processing"
            ])
        
        # Zeit-basierte Modifikationen
        if time_analysis.pressure_level in [PressureLevel.HIGH, PressureLevel.CRITICAL]:
            mods.append("accelerated_processing")
            
        if time_analysis.time_budget_ratio < 0.5:
            mods.append("time_critical_mode")
        
        return mods
    
    def _recommend_module_skipping(self, strategy: ResponseStrategy,
                                  time_analysis: TimeAnalysis,
                                  context: Dict[str, Any]) -> List[str]:
        """Empfiehlt zu überspringende Module basierend auf Zeitdruck."""
        skip_recommendations = []
        
        if strategy in [ResponseStrategy.EMERGENCY, ResponseStrategy.DEFENSIVE]:
            # Kritischer Modus - nur essenzielle Module
            skip_recommendations.extend([
                "dof",  # Langzeitprognose kann warten
                "sbp",  # Stakeholder-Vorhersage optional
                "aso"   # Optimierung nicht kritisch
            ])
        
        elif strategy == ResponseStrategy.FALLBACK:
            # Fallback - verwende Patterns statt Analyse
            skip_recommendations.extend([
                "resl",  # Rekursive Simulation
                "ril"    # Implementation Loop
            ])
        
        elif strategy == ResponseStrategy.SIMPLIFIED:
            # Vereinfacht - skip aufwändige Module
            if time_analysis.time_budget_ratio < 0.7:
                skip_recommendations.append("dof")
            if time_analysis.time_budget_ratio < 0.5:
                skip_recommendations.append("meta_learner")
        
        # Kontext-basierte Anpassungen
        if context.get("profile_stable", True) and "vdd" not in skip_recommendations:
            skip_recommendations.append("vdd")  # Drift-Detection bei stabilem Profil optional
        
        return skip_recommendations
    
    def _create_logs(self, time_analysis: TimeAnalysis, 
                    strategy: ResponseStrategy,
                    modifications: List[str],
                    risk_level: float) -> List[Dict[str, Any]]:
        """Erstellt detaillierte Audit-Logs."""
        return [{
            "timestamp": datetime.now().isoformat(),
            "event": "time_pressure_handled",
            "pressure_level": time_analysis.pressure_level.value,
            "strategy": strategy.value,
            "time_budget_ratio": round(time_analysis.time_budget_ratio, 3),
            "pressure_index": round(self._calculate_pressure_index(time_analysis, risk_level), 3),
            "risk_level": round(risk_level, 3),
            "available_time": time_analysis.available_time,
            "required_time": time_analysis.required_time,
            "modifications": modifications,
            "confidence": time_analysis.confidence,
            "urgency_indicators": time_analysis.urgency_indicators
        }]
    
    def _update_stats(self, strategy: ResponseStrategy, pressure_index: float) -> None:
        """Aktualisiert interne Statistiken."""
        # Strategy-Zählung
        strategy_name = strategy.value
        if strategy_name not in self.stats["strategies_used"]:
            self.stats["strategies_used"][strategy_name] = 0
        self.stats["strategies_used"][strategy_name] += 1
        
        # Durchschnittlicher Pressure Index
        n = self.stats["total_handled"]
        prev_avg = self.stats["average_pressure"]
        self.stats["average_pressure"] = (prev_avg * (n-1) + pressure_index) / n
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt aktuelle Statistiken zurück."""
        return {
            **self.stats,
            "most_used_strategy": max(self.stats["strategies_used"].items(), 
                                     key=lambda x: x[1])[0] if self.stats["strategies_used"] else None
        }


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale Handler-Instanz
_handler_instance: Optional[EthicalTimePressureHandler] = None

def _get_handler_instance(config: Optional[Dict[str, Any]] = None) -> EthicalTimePressureHandler:
    """Lazy-Loading der Handler-Instanz."""
    global _handler_instance
    if _handler_instance is None or config is not None:
        _handler_instance = EthicalTimePressureHandler(config)
    return _handler_instance


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
        # ETPH-Konfiguration aus Context
        etph_config = context.get("config", {}).get("etph", {})
        
        # Handler-Instanz
        handler = _get_handler_instance(etph_config)
        
        # Zeitdruck verarbeiten
        result = handler.handle_time_pressure(input_text, context)
        
        # Ergebnis aufbereiten
        etph_result = {
            "decision_adjusted": result.decision_adjusted,
            "strategy": result.strategy.value,
            "risk_level": result.risk_level,
            "pressure_index": result.pressure_index,
            "output": result.output,
            "modifications": result.modifications,
            "time_analysis": {
                "available_time": result.logs[0]["available_time"],
                "required_time": result.logs[0]["required_time"],
                "pressure_level": result.logs[0]["pressure_level"]
            }
        }
        
        # Speichere im Context für andere Module
        context["etph_result"] = etph_result
        
        # Empfehlungen für Module-Skipping
        if "recommended_module_skip" in context:
            context["etph_module_skip_recommendations"] = context["recommended_module_skip"]
        
        # Log wichtige Events
        if log_manager:
            log_manager.log_event(
                "ETPH",
                f"Zeitdruck behandelt: {result.strategy.value} "
                f"(Pressure: {result.pressure_index:.0%}, Risk: {result.risk_level:.0%})",
                "INFO"
            )
            
            if result.strategy == ResponseStrategy.EMERGENCY:
                log_manager.log_event(
                    "ETPH",
                    "⚠️ NOTFALL-MODUS aktiviert!",
                    "WARNING"
                )
        
        return {
            "success": True,
            "result": etph_result,
            "module": "etph",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"ETPH error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("ETPH", error_msg, "ERROR")
        
        return {
            "success": False,
            "error": error_msg,
            "module": "etph",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die ETPH-Funktionalität."""
    print("=== INTEGRA ETPH v2.0 Demo ===")
    print("Ethical Time Pressure Handler - Schützt Ethik unter Zeitdruck\n")
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test-Szenarien
    test_scenarios = [
        {
            "name": "Normaler Zeitdruck",
            "input": "Soll ich in dieser Situation helfen?",
            "context": {
                "profile": test_profile.copy(),
                "time_budget": 3.0,
                "simple_ethics_result": {"overall_score": 0.8}
            }
        },
        {
            "name": "Hoher Zeitdruck mit Urgency",
            "input": "Sofort entscheiden! Notfall! Jemand braucht dringend Hilfe!",
            "context": {
                "profile": test_profile.copy(),
                "time_budget": 0.5,
                "urgency_level": "high",
                "simple_ethics_result": {"overall_score": 0.7},
                "etb_result": {"conflicts_detected": True, "conflicts": [1, 2]}
            }
        },
        {
            "name": "Kritischer Zeitdruck mit niedrigem Ethik-Score",
            "input": "JETZT SOFORT die Regel brechen?! NOTFALL!!!",
            "context": {
                "profile": test_profile.copy(),
                "time_budget": 0.2,
                "simple_ethics_result": {"overall_score": 0.3},
                "vdd_result": {"drift_detected": True, "drift_analysis": {"overall_drift": 0.4}},
                "aso_result": {"system_performance": {"level": "critical"}}
            }
        },
        {
            "name": "Moderater Zeitdruck mit Modul-Integration",
            "input": "Bitte schnell eine Entscheidung treffen",
            "context": {
                "profile": test_profile.copy(),
                "time_budget": 2.0,
                "decision_path": "deep",
                "meta_learner_result": {
                    "learning_triggered": True,
                    "patterns": {"total": 5, "recent": [{"type": "success_pattern"}]}
                },
                "dof_result": {"critical_count": 1, "highest_risk": 0.6},
                "config": {"dof": {"enabled": True}}
            }
        },
        {
            "name": "Minimaler Zeitdruck",
            "input": "Wenn Sie Zeit haben, könnten Sie mir bei dieser Analyse helfen?",
            "context": {
                "profile": test_profile.copy(),
                "time_budget": 10.0,
                "simple_ethics_result": {"overall_score": 0.9}
            }
        }
    ]
    
    print("📊 Führe 5 Test-Szenarien durch...\n")
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*70}")
        print(f"Test {i+1}: {scenario['name']}")
        print(f"Eingabe: {scenario['input']}")
        print(f"Zeit-Budget: {scenario['context']['time_budget']}s")
        
        # Führe Modul aus
        result = run_module(scenario["input"], scenario["context"])
        
        if result["success"]:
            etph_result = result["result"]
            
            print(f"\n📍 Ergebnis:")
            print(f"  Strategie: {etph_result['strategy']}")
            print(f"  Pressure Index: {etph_result['pressure_index']:.0%}")
            print(f"  Risiko-Level: {etph_result['risk_level']:.0%}")
            print(f"  Entscheidung angepasst: {'Ja' if etph_result['decision_adjusted'] else 'Nein'}")
            
            print(f"\n⏱️ Zeit-Analyse:")
            time_analysis = etph_result["time_analysis"]
            print(f"  Verfügbare Zeit: {time_analysis['available_time']}s")
            print(f"  Benötigte Zeit: {time_analysis['required_time']}s")
            print(f"  Pressure Level: {time_analysis['pressure_level']}")
            
            if etph_result["modifications"]:
                print(f"\n🔧 Modifikationen:")
                for mod in etph_result["modifications"]:
                    print(f"  - {mod}")
            
            print(f"\n💬 Ausgabe:")
            print(f"  {etph_result['output']}")
            
            # Module-Skip Empfehlungen
            if "etph_module_skip_recommendations" in result["context"]:
                skip_recs = result["context"]["etph_module_skip_recommendations"]
                if skip_recs:
                    print(f"\n⚡ Empfohlene Module-Skips:")
                    for module in skip_recs:
                        print(f"  - {module}")
        else:
            print(f"❌ Fehler: {result['error']}")
    
    # Statistiken anzeigen
    print(f"\n{'='*70}")
    print("📈 ETPH Statistiken:")
    
    handler = _get_handler_instance()
    stats = handler.get_statistics()
    
    print(f"  Gesamt behandelt: {stats['total_handled']}")
    print(f"  Durchschnittlicher Pressure Index: {stats['average_pressure']:.0%}")
    print(f"  Module übersprungen: {stats['modules_skipped']}")
    
    if stats["strategies_used"]:
        print(f"\n  Strategien verwendet:")
        for strategy, count in stats["strategies_used"].items():
            print(f"    {strategy}: {count}x")
        print(f"  Meist genutzte Strategie: {stats['most_used_strategy']}")
    
    print("\n✅ ETPH Demo abgeschlossen!")
    print("Das Modul schützt ethische Entscheidungsqualität auch unter Zeitdruck.")


if __name__ == "__main__":
    demo()