# -*- coding: utf-8 -*-
"""
Modulname: vdd.py
Beschreibung: Value Drift Detection für INTEGRA Full - Überwachung ethischer Wertverschiebungen
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

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
import math
from pathlib import Path
from collections import defaultdict, deque
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


class ValueDriftDetector:
    """
    Value Drift Detection (VDD) - Erkennt graduelle Verschiebungen in ethischen Werten.
    
    Überwacht kontinuierlich Entscheidungsmuster und Profiländerungen,
    um schleichende Abweichungen von ethischen Grundwerten zu identifizieren.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert den Value Drift Detector.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        
        # Konfiguration
        self.monitoring_window = self.config.get("monitoring_window", 100)
        self.alert_threshold = self.config.get("alert_threshold", 0.15)
        self.use_context_modules = self.config.get("use_context_modules", True)
        self.enable_meta_learning_check = self.config.get("enable_meta_learning_check", True)
        self.auto_baseline_reset = self.config.get("auto_baseline_reset", False)
        
        # Baseline-Werte (werden bei Initialisierung gesetzt)
        self.baseline = {
            "profile": profiles.get_default_profile().copy(),
            "ethics_scores": {p: 1.0 for p in principles.ALIGN_KEYS},
            "violation_rates": {p: 0.0 for p in principles.ALIGN_KEYS},
            "confidence_avg": 0.85,
            "timestamp": datetime.now()
        }
        
        # Laufende Metriken
        self.metrics = {
            "profile_history": deque(maxlen=self.monitoring_window),
            "ethics_history": deque(maxlen=self.monitoring_window),
            "violation_history": deque(maxlen=self.monitoring_window),
            "confidence_history": deque(maxlen=self.monitoring_window),
            "decision_paths": deque(maxlen=self.monitoring_window),
            "timestamps": deque(maxlen=self.monitoring_window),
            "meta_learner_changes": deque(maxlen=self.monitoring_window),  # NEU
            "module_patterns": deque(maxlen=self.monitoring_window)        # NEU
        }
        
        # Drift-Indikatoren
        self.drift_indicators = {
            "profile_drift": 0.0,
            "ethics_drift": 0.0,
            "violation_drift": 0.0,
            "confidence_drift": 0.0,
            "pattern_drift": 0.0,
            "meta_learning_drift": 0.0,  # NEU
            "overall_drift": 0.0
        }
        
        # Drift-Historie
        self.drift_history = []
        self.alerts_triggered = []
        
        # Statistiken
        self.stats = {
            "decisions_monitored": 0,
            "drift_events": 0,
            "alerts_triggered": 0,
            "baseline_resets": 0,
            "max_drift_detected": 0.0,
            "meta_learner_corrections": 0  # NEU
        }

    def monitor_decision(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Überwacht eine Entscheidung auf Value Drift.
        
        Args:
            input_text: Text der Entscheidung (für Logging)
            context: Vollständiger Entscheidungskontext
            
        Returns:
            dict: Drift-Analyse-Ergebnis
        """
        # Entscheidungsdaten extrahieren
        decision_data = self._extract_decision_data_from_context(input_text, context)
        
        # Zu Historie hinzufügen
        self._add_to_history(decision_data)
        
        # Context-Module berücksichtigen
        if self.use_context_modules:
            self._integrate_context_modules(decision_data, context)
        
        # Drift berechnen
        drift_analysis = self._calculate_drift()
        
        # Trend analysieren
        trend_analysis = self._analyze_trends()
        
        # Muster erkennen
        pattern_analysis = self._detect_drift_patterns()
        
        # Alarm-Status prüfen
        alert_status = self._check_alert_conditions(drift_analysis)
        
        # MetaLearner-Integration prüfen
        meta_learner_status = self._check_meta_learner_integration(context)
        
        # Empfehlungen generieren
        recommendations = self._generate_recommendations(
            drift_analysis, trend_analysis, alert_status, meta_learner_status
        )
        
        # Auto-Baseline-Reset wenn konfiguriert
        if self.auto_baseline_reset and drift_analysis["overall_drift"] > self.alert_threshold * 3:
            self.reset_baseline()
            recommendations.append("AUTOMATISCH: Baseline wurde zurückgesetzt wegen extremer Drift")
        
        # Log wenn aktiviert
        if log_manager:
            log_manager.log_event(
                "VDD",
                f"Drift-Überwachung - Overall: {drift_analysis['overall_drift']:.3f}, "
                f"Alert: {alert_status['alert_level']}",
                "INFO" if alert_status['alert_level'] == "none" else "WARNING"
            )
        
        # Ergebnis zusammenstellen
        return {
            "drift_detected": drift_analysis["overall_drift"] > self.alert_threshold,
            "drift_severity": self._get_drift_severity(drift_analysis["overall_drift"]),
            "drift_analysis": drift_analysis,
            "trend_analysis": trend_analysis,
            "pattern_analysis": pattern_analysis,
            "alert_status": alert_status,
            "meta_learner_status": meta_learner_status,
            "recommendations": recommendations,
            "monitoring_window": {
                "size": len(self.metrics["profile_history"]),
                "oldest": self.metrics["timestamps"][0].isoformat() if self.metrics["timestamps"] else None,
                "newest": self.metrics["timestamps"][-1].isoformat() if self.metrics["timestamps"] else None
            },
            "baseline": {
                "age_hours": (datetime.now() - self.baseline["timestamp"]).total_seconds() / 3600,
                "profile": self.baseline["profile"].copy()
            },
            "stats": self.stats.copy()
        }

    def _extract_decision_data_from_context(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert relevante Daten aus dem standardisierten Context."""
        data = {
            "timestamp": datetime.now(),
            "input_text": input_text[:100],  # Gekürzt für Historie
            "profile": context.get("profile", profiles.get_default_profile()).copy(),
            "path": context.get("decision_path", context.get("path", "unknown")),
            "confidence": context.get("confidence", 0.5)
        }
        
        # Simple Ethics Ergebnisse
        if "simple_ethics_result" in context:
            ethics = context["simple_ethics_result"]
            data["ethics_scores"] = ethics.get("scores", {})
            data["violations"] = ethics.get("violations", [])
            data["ethics_confidence"] = ethics.get("confidence", 0.5)
        else:
            data["ethics_scores"] = {}
            data["violations"] = []
        
        # ETB-Anpassungen
        if "etb_result" in context:
            data["etb_adjustments"] = context["etb_result"].get("final_weights", {})
            data["conflicts_detected"] = context["etb_result"].get("conflicts_detected", False)
        
        # PAE Anchor
        if "pae_result" in context:
            data["primary_anchor"] = context["pae_result"].get("primary_anchor")
        
        # Meta-Learner Updates
        if "meta_learner_result" in context:
            ml_result = context["meta_learner_result"]
            data["profile_updates"] = ml_result.get("profile_updates", {})
            data["learning_triggered"] = ml_result.get("learning_triggered", False)
        
        # Control-Eingriffe
        if "basic_control_result" in context:
            data["control_intervention"] = True
            data["control_action"] = context["basic_control_result"].get("action")
        elif "full_control_result" in context:
            data["control_intervention"] = True
            data["control_action"] = context["full_control_result"].get("intervention", {}).get("type")
        
        return data

    def _add_to_history(self, decision_data: Dict[str, Any]) -> None:
        """Fügt Entscheidungsdaten zur Historie hinzu."""
        # Profile
        self.metrics["profile_history"].append(decision_data["profile"])
        
        # Ethics Scores
        self.metrics["ethics_history"].append(decision_data.get("ethics_scores", {}))
        
        # Violations
        self.metrics["violation_history"].append(decision_data.get("violations", []))
        
        # Confidence
        self.metrics["confidence_history"].append(decision_data["confidence"])
        
        # Decision Path
        self.metrics["decision_paths"].append(decision_data["path"])
        
        # Timestamp
        self.metrics["timestamps"].append(decision_data["timestamp"])
        
        # Meta-Learner Changes
        self.metrics["meta_learner_changes"].append(
            decision_data.get("profile_updates", {})
        )
        
        # Module Patterns
        module_pattern = {
            "etb_active": "etb_adjustments" in decision_data,
            "pae_active": "primary_anchor" in decision_data,
            "control_active": decision_data.get("control_intervention", False),
            "ml_active": decision_data.get("learning_triggered", False)
        }
        self.metrics["module_patterns"].append(module_pattern)
        
        # Statistik
        self.stats["decisions_monitored"] += 1

    def _integrate_context_modules(self, decision_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Integriert Informationen aus anderen Modulen für bessere Drift-Erkennung."""
        
        # RESL Integration - Ethische Folgekonflikte als Drift-Indikator
        if "resl_result" in context:
            resl = context["resl_result"]
            if resl.get("risk_level", 0) > 0.7:
                # Hohe ethische Risiken deuten auf mögliche Drift hin
                decision_data["ethical_risk_indicator"] = True
        
        # NGA Integration - Compliance-Verletzungen
        if "nga_result" in context:
            nga = context["nga_result"]
            if nga.get("violations"):
                decision_data["compliance_violations"] = len(nga["violations"])
                # Compliance-Probleme können auf Drift hinweisen
        
        # VDD selbst - Rekursive Drift-Erkennung
        if "vdd_result" in context:
            # Vermeide Endlosschleife
            previous_drift = context["vdd_result"].get("drift_analysis", {}).get("overall_drift", 0)
            decision_data["previous_drift"] = previous_drift
        
        # ASO Integration - Architektur-Änderungen
        if "aso_result" in context:
            aso = context["aso_result"]
            if aso.get("architectural_changes", 0) > 3:
                decision_data["system_instability"] = True

    def _calculate_drift(self) -> Dict[str, float]:
        """Berechnet erweiterte Drift-Indikatoren."""
        if len(self.metrics["profile_history"]) < 10:
            # Zu wenig Daten für Drift-Berechnung
            return {key: 0.0 for key in self.drift_indicators}
        
        # Standard-Drifts
        profile_drift = self._calculate_profile_drift()
        ethics_drift = self._calculate_ethics_drift()
        violation_drift = self._calculate_violation_drift()
        confidence_drift = self._calculate_confidence_drift()
        pattern_drift = self._calculate_pattern_drift()
        
        # NEU: Meta-Learning Drift
        meta_learning_drift = self._calculate_meta_learning_drift()
        
        # Gesamt-Drift (angepasste Gewichtung)
        weights = {
            "profile": 0.20,
            "ethics": 0.20,
            "violation": 0.20,
            "confidence": 0.15,
            "pattern": 0.15,
            "meta_learning": 0.10  # NEU
        }
        
        overall_drift = sum(
            value * weights[key.replace("_drift", "")]
            for key, value in {
                "profile_drift": profile_drift,
                "ethics_drift": ethics_drift,
                "violation_drift": violation_drift,
                "confidence_drift": confidence_drift,
                "pattern_drift": pattern_drift,
                "meta_learning_drift": meta_learning_drift
            }.items()
        )
        
        drift_values = {
            "profile_drift": profile_drift,
            "ethics_drift": ethics_drift,
            "violation_drift": violation_drift,
            "confidence_drift": confidence_drift,
            "pattern_drift": pattern_drift,
            "meta_learning_drift": meta_learning_drift,
            "overall_drift": overall_drift
        }
        
        # Update max drift
        if overall_drift > self.stats["max_drift_detected"]:
            self.stats["max_drift_detected"] = overall_drift
        
        # Update indicators
        self.drift_indicators.update(drift_values)
        
        # Drift-Event tracken
        if overall_drift > self.alert_threshold:
            self.stats["drift_events"] += 1
        
        # Historie speichern
        self.drift_history.append({
            "timestamp": datetime.now(),
            "overall_drift": overall_drift,
            "components": drift_values.copy()
        })
        
        return drift_values

    def _calculate_profile_drift(self) -> float:
        """Berechnet Drift im ethischen Profil."""
        if not self.metrics["profile_history"]:
            return 0.0
        
        # Vergleiche aktuelles Profil mit Baseline
        current_profile = self.metrics["profile_history"][-1]
        baseline_profile = self.baseline["profile"]
        
        # Berechne Distanz für jedes Prinzip
        distances = []
        for principle in principles.ALIGN_KEYS:
            current = current_profile.get(principle, 1.0)
            baseline = baseline_profile.get(principle, 1.0)
            distance = abs(current - baseline) / baseline if baseline != 0 else 0
            distances.append(distance)
        
        # Durchschnittliche Abweichung
        avg_drift = statistics.mean(distances) if distances else 0.0
        
        # Verstärke große Abweichungen
        if any(d > 0.3 for d in distances):
            avg_drift *= 1.5
        
        return min(1.0, avg_drift)

    def _calculate_ethics_drift(self) -> float:
        """Berechnet Drift in ethischen Bewertungen."""
        if len(self.metrics["ethics_history"]) < 10:
            return 0.0
        
        # Durchschnittliche Scores der letzten N Entscheidungen
        recent_scores = defaultdict(list)
        for ethics in self.metrics["ethics_history"][-20:]:
            for principle, score in ethics.items():
                recent_scores[principle].append(score)
        
        # Vergleiche mit Baseline
        drift_scores = []
        for principle in principles.ALIGN_KEYS:
            if principle in recent_scores and recent_scores[principle]:
                recent_avg = statistics.mean(recent_scores[principle])
                baseline_score = self.baseline["ethics_scores"].get(principle, 1.0)
                drift = abs(recent_avg - baseline_score)
                drift_scores.append(drift)
        
        return statistics.mean(drift_scores) if drift_scores else 0.0

    def _calculate_violation_drift(self) -> float:
        """Berechnet Drift in Verletzungsmustern."""
        if len(self.metrics["violation_history"]) < 10:
            return 0.0
        
        # Verletzungsraten berechnen
        violation_counts = defaultdict(int)
        total_decisions = len(self.metrics["violation_history"])
        
        for violations in self.metrics["violation_history"]:
            for violation in violations:
                violation_counts[violation] += 1
        
        # Aktuelle Raten
        current_rates = {}
        for principle in principles.ALIGN_KEYS:
            current_rates[principle] = violation_counts.get(principle, 0) / total_decisions
        
        # Vergleiche mit Baseline
        drift_scores = []
        for principle in principles.ALIGN_KEYS:
            current_rate = current_rates[principle]
            baseline_rate = self.baseline["violation_rates"].get(principle, 0.0)
            
            # Neue Verletzungen sind kritischer
            if baseline_rate == 0 and current_rate > 0:
                drift_scores.append(current_rate * 2)  # Verstärke neue Verletzungsmuster
            else:
                drift_scores.append(abs(current_rate - baseline_rate))
        
        return min(1.0, statistics.mean(drift_scores) * 3)  # Verletzungen stark gewichten

    def _calculate_confidence_drift(self) -> float:
        """Berechnet Drift im Konfidenz-Niveau."""
        if len(self.metrics["confidence_history"]) < 10:
            return 0.0
        
        # Durchschnittliche Konfidenz
        recent_confidence = statistics.mean(list(self.metrics["confidence_history"])[-20:])
        baseline_confidence = self.baseline["confidence_avg"]
        
        # Relative Abweichung
        drift = abs(recent_confidence - baseline_confidence) / baseline_confidence
        
        # Sinkende Konfidenz ist kritischer
        if recent_confidence < baseline_confidence:
            drift *= 1.5
        
        return min(1.0, drift)

    def _calculate_pattern_drift(self) -> float:
        """Berechnet Drift in Entscheidungsmustern."""
        if len(self.metrics["decision_paths"]) < 20:
            return 0.0
        
        # Pfad-Verteilung
        path_counts = defaultdict(int)
        for path in self.metrics["decision_paths"]:
            path_counts[path] += 1
        
        # Verhältnisse berechnen
        total = len(self.metrics["decision_paths"])
        path_ratios = {path: count/total for path, count in path_counts.items()}
        
        # Erwartete Verteilung (aus ersten 20% der Historie)
        early_sample_size = max(20, len(self.metrics["decision_paths"]) // 5)
        early_paths = list(self.metrics["decision_paths"])[:early_sample_size]
        early_counts = defaultdict(int)
        for path in early_paths:
            early_counts[path] += 1
        
        early_total = len(early_paths)
        early_ratios = {path: count/early_total for path, count in early_counts.items()}
        
        # Vergleiche Verteilungen
        all_paths = set(path_ratios.keys()) | set(early_ratios.keys())
        differences = []
        for path in all_paths:
            current = path_ratios.get(path, 0)
            early = early_ratios.get(path, 0)
            differences.append(abs(current - early))
        
        return min(1.0, statistics.mean(differences) * 2) if differences else 0.0

    def _calculate_meta_learning_drift(self) -> float:
        """Berechnet Drift basierend auf Meta-Learner Aktivität."""
        if len(self.metrics["meta_learner_changes"]) < 10:
            return 0.0
        
        # Analysiere Häufigkeit und Intensität von Profil-Updates
        update_counts = 0
        update_magnitudes = []
        
        for changes in self.metrics["meta_learner_changes"]:
            if changes:  # Wenn Updates vorhanden
                update_counts += 1
                # Berechne Magnitude der Änderungen
                magnitude = sum(abs(v) for v in changes.values())
                update_magnitudes.append(magnitude)
        
        # Update-Rate
        update_rate = update_counts / len(self.metrics["meta_learner_changes"])
        
        # Durchschnittliche Update-Magnitude
        avg_magnitude = statistics.mean(update_magnitudes) if update_magnitudes else 0.0
        
        # Drift basiert auf beiden Faktoren
        drift = update_rate * 0.5 + min(avg_magnitude * 10, 0.5)
        
        # Häufige große Updates = hohe Drift
        if update_rate > 0.5 and avg_magnitude > 0.1:
            drift *= 1.5
            self.stats["meta_learner_corrections"] += 1
        
        return min(1.0, drift)

    def _analyze_trends(self) -> Dict[str, Any]:
        """Analysiert Trends in den Drift-Metriken."""
        if len(self.drift_history) < 5:
            return {
                "trend_direction": "insufficient_data",
                "trend_strength": 0.0,
                "acceleration": 0.0,
                "stability_index": 1.0
            }
        
        # Letzte Drift-Werte
        recent_drifts = [h["overall_drift"] for h in self.drift_history[-10:]]
        
        # Trend-Richtung
        if len(recent_drifts) >= 3:
            first_half = statistics.mean(recent_drifts[:len(recent_drifts)//2])
            second_half = statistics.mean(recent_drifts[len(recent_drifts)//2:])
            
            if second_half > first_half * 1.1:
                trend_direction = "increasing"
                trend_strength = (second_half - first_half) / first_half
            elif second_half < first_half * 0.9:
                trend_direction = "decreasing"
                trend_strength = (first_half - second_half) / first_half
            else:
                trend_direction = "stable"
                trend_strength = 0.0
        else:
            trend_direction = "insufficient_data"
            trend_strength = 0.0
        
        # Beschleunigung
        if len(recent_drifts) >= 3:
            differences = [recent_drifts[i+1] - recent_drifts[i] 
                          for i in range(len(recent_drifts)-1)]
            acceleration = statistics.mean(differences) if differences else 0.0
        else:
            acceleration = 0.0
        
        # Stabilitätsindex (niedrig = instabil)
        if recent_drifts:
            stability_index = 1.0 - statistics.stdev(recent_drifts) if len(recent_drifts) > 1 else 1.0
        else:
            stability_index = 1.0
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "acceleration": acceleration,
            "stability_index": max(0.0, min(1.0, stability_index)),
            "samples_analyzed": len(recent_drifts)
        }

    def _detect_drift_patterns(self) -> Dict[str, Any]:
        """Erkennt spezifische Drift-Muster."""
        patterns = {
            "systematic_shift": False,
            "oscillation": False,
            "sudden_change": False,
            "gradual_degradation": False,
            "meta_learning_instability": False  # NEU
        }
        
        if len(self.drift_history) < 10:
            return {"patterns_detected": False, "pattern_types": patterns}
        
        recent_drifts = [h["overall_drift"] for h in self.drift_history[-20:]]
        
        # Systematische Verschiebung
        if all(d > self.alert_threshold * 0.7 for d in recent_drifts[-5:]):
            patterns["systematic_shift"] = True
        
        # Oszillation
        if len(recent_drifts) >= 6:
            ups = sum(1 for i in range(1, len(recent_drifts)) 
                     if recent_drifts[i] > recent_drifts[i-1])
            downs = len(recent_drifts) - 1 - ups
            if min(ups, downs) / max(ups, downs) > 0.7:
                patterns["oscillation"] = True
        
        # Plötzliche Änderung
        if len(recent_drifts) >= 3:
            for i in range(1, len(recent_drifts)):
                if recent_drifts[i] > recent_drifts[i-1] * 2.5:
                    patterns["sudden_change"] = True
                    break
        
        # Graduelle Verschlechterung
        if len(recent_drifts) >= 10:
            first_third = statistics.mean(recent_drifts[:len(recent_drifts)//3])
            last_third = statistics.mean(recent_drifts[-len(recent_drifts)//3:])
            if last_third > first_third * 1.5:
                patterns["gradual_degradation"] = True
        
        # Meta-Learning Instabilität
        if self.drift_indicators.get("meta_learning_drift", 0) > 0.3:
            ml_pattern_count = sum(1 for p in self.metrics["module_patterns"] 
                                 if p.get("ml_active", False))
            if ml_pattern_count > len(self.metrics["module_patterns"]) * 0.5:
                patterns["meta_learning_instability"] = True
        
        return {
            "patterns_detected": any(patterns.values()),
            "pattern_types": patterns,
            "pattern_confidence": self._calculate_pattern_confidence(patterns)
        }

    def _calculate_pattern_confidence(self, patterns: Dict[str, bool]) -> float:
        """Berechnet Konfidenz für erkannte Muster."""
        if not any(patterns.values()):
            return 1.0  # Keine Muster = hohe Konfidenz in Stabilität
        
        # Mehrere Muster = niedrigere Konfidenz
        pattern_count = sum(patterns.values())
        confidence = 1.0 - (pattern_count * 0.15)
        
        # Kritische Muster reduzieren Konfidenz stärker
        if patterns.get("systematic_shift") or patterns.get("gradual_degradation"):
            confidence *= 0.8
        
        return max(0.3, confidence)

    def _check_alert_conditions(self, drift_analysis: Dict[str, float]) -> Dict[str, Any]:
        """Prüft erweiterte Alarm-Bedingungen."""
        overall_drift = drift_analysis["overall_drift"]
        
        # Alert Level bestimmen
        if overall_drift >= self.alert_threshold * 2:
            alert_level = "critical"
            severity = 1.0
        elif overall_drift >= self.alert_threshold:
            alert_level = "medium"
            severity = 0.7
        elif overall_drift >= self.alert_threshold * 0.7:
            alert_level = "low"
            severity = 0.4
        else:
            alert_level = "none"
            severity = 0.0
        
        # Spezifische Alarme
        specific_alerts = []
        
        if drift_analysis["violation_drift"] > 0.3:
            specific_alerts.append({
                "type": "violation_increase",
                "severity": "high",
                "message": "Signifikante Zunahme ethischer Verletzungen",
                "affected_principle": "governance"
            })
        
        if drift_analysis["confidence_drift"] > 0.25:
            specific_alerts.append({
                "type": "confidence_degradation",
                "severity": "medium",
                "message": "Abnehmende Entscheidungssicherheit",
                "affected_principle": "awareness"
            })
        
        if drift_analysis["profile_drift"] > 0.35:
            specific_alerts.append({
                "type": "profile_deviation",
                "severity": "high",
                "message": "Starke Abweichung vom ethischen Basisprofil",
                "affected_principle": "integrity"
            })
        
        if drift_analysis.get("meta_learning_drift", 0) > 0.4:
            specific_alerts.append({
                "type": "meta_learning_instability",
                "severity": "medium",
                "message": "Meta-Learner zeigt instabiles Verhalten",
                "affected_principle": "learning"
            })
        
        # Alert triggern
        alert_triggered = alert_level in ["medium", "critical"]
        if alert_triggered:
            self.stats["alerts_triggered"] += 1
            self.alerts_triggered.append({
                "timestamp": datetime.now(),
                "level": alert_level,
                "drift_value": overall_drift,
                "specific_alerts": specific_alerts
            })
        
        return {
            "alert_level": alert_level,
            "severity": severity,
            "alert_triggered": alert_triggered,
            "specific_alerts": specific_alerts,
            "threshold": self.alert_threshold,
            "escalation_required": alert_level == "critical"
        }

    def _check_meta_learner_integration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prüft Meta-Learner Integration und Stabilität."""
        status = {
            "meta_learner_active": False,
            "recent_updates": 0,
            "update_magnitude": 0.0,
            "stability_score": 1.0
        }
        
        if not self.enable_meta_learning_check:
            return status
        
        # Prüfe Meta-Learner Aktivität
        if "meta_learner_result" in context:
            status["meta_learner_active"] = True
            ml_result = context["meta_learner_result"]
            
            if ml_result.get("profile_updates"):
                status["recent_updates"] = 1
                status["update_magnitude"] = sum(abs(v) for v in ml_result["profile_updates"].values())
        
        # Berechne Stabilität basierend auf Historie
        if self.metrics["meta_learner_changes"]:
            recent_changes = list(self.metrics["meta_learner_changes"])[-20:]
            active_count = sum(1 for c in recent_changes if c)
            
            status["recent_updates"] = active_count
            status["stability_score"] = 1.0 - (active_count / len(recent_changes))
        
        return status

    def _generate_recommendations(self, drift_analysis: Dict[str, float],
                                 trend_analysis: Dict[str, Any],
                                 alert_status: Dict[str, Any],
                                 meta_learner_status: Dict[str, Any]) -> List[str]:
        """Generiert erweiterte Handlungsempfehlungen."""
        recommendations = []
        
        # Basierend auf Alert-Level
        if alert_status["alert_level"] == "critical":
            recommendations.append("KRITISCH: Sofortige Überprüfung der Systemintegrität erforderlich")
            recommendations.append("Erwägen Sie einen Rollback auf frühere Konfiguration")
            if meta_learner_status["meta_learner_active"]:
                recommendations.append("Meta-Learner temporär deaktivieren bis System stabilisiert")
        elif alert_status["alert_level"] == "medium":
            recommendations.append("Erhöhte Aufmerksamkeit erforderlich - Drift überschreitet Schwellwert")
        
        # Spezifische Empfehlungen
        if drift_analysis["violation_drift"] > 0.3:
            recommendations.append("Überprüfen Sie Entscheidungslogik auf neue Fehlermuster")
            recommendations.append("ETB-Parameter prüfen - möglicherweise falsche Trade-offs")
        
        if drift_analysis["confidence_drift"] > 0.25:
            recommendations.append("Analysieren Sie Ursachen für sinkende Entscheidungssicherheit")
            recommendations.append("PAE-Anchoring möglicherweise inkonsistent")
        
        if drift_analysis["profile_drift"] > 0.35:
            recommendations.append("Profil-Reset oder manuelle Kalibrierung empfohlen")
            recommendations.append("Meta-Learner Learning-Rate reduzieren")
        
        # Meta-Learning spezifisch
        if drift_analysis.get("meta_learning_drift", 0) > 0.4:
            recommendations.append("Meta-Learner zeigt Überanpassung - Learning-Rate anpassen")
            recommendations.append("Feedback-Loops auf Oszillation prüfen")
        
        # Trend-basierte Empfehlungen
        if trend_analysis["trend_direction"] == "increasing":
            recommendations.append("Drift-Trend zeigt Verschlechterung - präventive Maßnahmen einleiten")
        
        if trend_analysis["acceleration"] > 0.05:
            recommendations.append("Beschleunigte Drift erkannt - häufigere Überwachung aktivieren")
        
        if trend_analysis.get("stability_index", 1.0) < 0.5:
            recommendations.append("System zeigt Instabilität - Stabilisierungsmaßnahmen erforderlich")
        
        # Muster-basierte Empfehlungen
        patterns = self._detect_drift_patterns()
        if patterns["pattern_types"]["oscillation"]:
            recommendations.append("Instabiles Verhalten erkannt - Dämpfungsfaktoren erhöhen")
        
        if patterns["pattern_types"]["gradual_degradation"]:
            recommendations.append("Schleichende Verschlechterung - Baseline-Reset erwägen")
        
        if patterns["pattern_types"]["meta_learning_instability"]:
            recommendations.append("Meta-Learner destabilisiert System - Parameter-Review durchführen")
        
        return recommendations if recommendations else ["System innerhalb normaler Parameter"]

    def _get_detailed_drift_info(self) -> Dict[str, Any]:
        """Liefert erweiterte detaillierte Informationen über erkannte Drifts."""
        details = {
            "principle_changes": {},
            "violation_patterns": {},
            "confidence_timeline": [],
            "module_activity": {},
            "meta_learning_impact": {}
        }
        
        # Prinzipien-Änderungen
        if self.metrics["profile_history"]:
            current_profile = self.metrics["profile_history"][-1]
            for principle in principles.ALIGN_KEYS:
                current = current_profile.get(principle, 1.0)
                baseline = self.baseline["profile"].get(principle, 1.0)
                change = ((current - baseline) / baseline * 100) if baseline != 0 else 0
                details["principle_changes"][principle] = {
                    "baseline": baseline,
                    "current": current,
                    "change_percent": change,
                    "trend": "increasing" if change > 5 else "decreasing" if change < -5 else "stable"
                }
        
        # Verletzungsmuster
        violation_counts = defaultdict(int)
        for violations in self.metrics["violation_history"]:
            for violation in violations:
                violation_counts[violation] += 1
        
        total = len(self.metrics["violation_history"]) if self.metrics["violation_history"] else 1
        for principle, count in violation_counts.items():
            details["violation_patterns"][principle] = {
                "count": count,
                "rate": count / total,
                "trend": "increasing" if count > total * 0.1 else "stable",
                "severity": "high" if count > total * 0.2 else "medium" if count > total * 0.1 else "low"
            }
        
        # Konfidenz-Timeline (letzte 10)
        if self.metrics["confidence_history"]:
            recent_confidence = list(self.metrics["confidence_history"])[-10:]
            recent_timestamps = list(self.metrics["timestamps"])[-10:]
            for conf, ts in zip(recent_confidence, recent_timestamps):
                details["confidence_timeline"].append({
                    "timestamp": ts.isoformat(),
                    "confidence": conf
                })
        
        # Modul-Aktivität
        if self.metrics["module_patterns"]:
            recent_patterns = list(self.metrics["module_patterns"])[-50:]
            for module in ["etb_active", "pae_active", "control_active", "ml_active"]:
                active_count = sum(1 for p in recent_patterns if p.get(module, False))
                details["module_activity"][module.replace("_active", "")] = {
                    "activity_rate": active_count / len(recent_patterns),
                    "recent_activations": active_count
                }
        
        # Meta-Learning Impact
        if self.metrics["meta_learner_changes"]:
            recent_ml = list(self.metrics["meta_learner_changes"])[-20:]
            update_count = sum(1 for c in recent_ml if c)
            
            all_changes = {}
            for changes in recent_ml:
                for principle, value in changes.items():
                    if principle not in all_changes:
                        all_changes[principle] = []
                    all_changes[principle].append(value)
            
            details["meta_learning_impact"] = {
                "update_frequency": update_count / len(recent_ml),
                "principle_impacts": {
                    p: {
                        "avg_change": statistics.mean(values) if values else 0,
                        "volatility": statistics.stdev(values) if len(values) > 1 else 0
                    }
                    for p, values in all_changes.items()
                }
            }
        
        return details

    def _get_drift_severity(self, drift_value: float) -> str:
        """Kategorisiert Drift-Schweregrad."""
        if drift_value >= self.alert_threshold * 2:
            return "critical"
        elif drift_value >= self.alert_threshold:
            return "high"
        elif drift_value >= self.alert_threshold * 0.5:
            return "moderate"
        else:
            return "low"

    def reset_baseline(self, new_baseline: Optional[Dict[str, Any]] = None) -> None:
        """
        Setzt die Baseline zurück.
        
        Args:
            new_baseline (dict, optional): Neue Baseline-Werte
        """
        if new_baseline:
            self.baseline.update(new_baseline)
        else:
            # Berechne neue Baseline aus aktuellen Metriken
            if len(self.metrics["profile_history"]) >= 20:
                # Durchschnitt der letzten 20 Profile
                recent_profiles = list(self.metrics["profile_history"])[-20:]
                avg_profile = {}
                for principle in principles.ALIGN_KEYS:
                    values = [p.get(principle, 1.0) for p in recent_profiles]
                    avg_profile[principle] = statistics.mean(values)
                
                self.baseline["profile"] = avg_profile
                self.baseline["confidence_avg"] = statistics.mean(
                    list(self.metrics["confidence_history"])[-20:]
                )
                
                # Ethics Baseline
                recent_ethics = list(self.metrics["ethics_history"])[-20:]
                for principle in principles.ALIGN_KEYS:
                    scores = [e.get(principle, 1.0) for e in recent_ethics if principle in e]
                    if scores:
                        self.baseline["ethics_scores"][principle] = statistics.mean(scores)
        
        self.baseline["timestamp"] = datetime.now()
        self.stats["baseline_resets"] += 1
        
        # Drift-Historie zurücksetzen
        self.drift_history.clear()
        self.drift_indicators = {key: 0.0 for key in self.drift_indicators}
        
        if log_manager:
            log_manager.log_event("VDD", f"Baseline zurückgesetzt (Reset #{self.stats['baseline_resets']})", "INFO")

    def get_drift_report(self) -> Dict[str, Any]:
        """
        Generiert einen umfassenden Drift-Report.
        
        Returns:
            dict: Vollständiger Drift-Bericht
        """
        return {
            "summary": {
                "overall_drift": self.drift_indicators["overall_drift"],
                "drift_severity": self._get_drift_severity(self.drift_indicators["overall_drift"]),
                "alert_level": self._check_alert_conditions(self.drift_indicators)["alert_level"],
                "decisions_monitored": self.stats["decisions_monitored"],
                "monitoring_period": {
                    "start": self.metrics["timestamps"][0].isoformat() if self.metrics["timestamps"] else None,
                    "end": self.metrics["timestamps"][-1].isoformat() if self.metrics["timestamps"] else None,
                    "duration_hours": (
                        (self.metrics["timestamps"][-1] - self.metrics["timestamps"][0]).total_seconds() / 3600
                        if len(self.metrics["timestamps"]) > 1 else 0
                    )
                }
            },
            "drift_indicators": self.drift_indicators.copy(),
            "trends": self._analyze_trends(),
            "patterns": self._detect_drift_patterns(),
            "baseline": {
                "set_at": self.baseline["timestamp"].isoformat(),
                "age_hours": (datetime.now() - self.baseline["timestamp"]).total_seconds() / 3600,
                "profile": self.baseline["profile"].copy()
            },
            "alerts": {
                "total_triggered": self.stats["alerts_triggered"],
                "recent_alerts": self.alerts_triggered[-5:] if self.alerts_triggered else []
            },
            "module_integration": {
                "meta_learner_corrections": self.stats["meta_learner_corrections"],
                "module_activity": self._get_detailed_drift_info()["module_activity"]
            },
            "recommendations": self._generate_recommendations(
                self.drift_indicators,
                self._analyze_trends(),
                self._check_alert_conditions(self.drift_indicators),
                {"meta_learner_active": False, "stability_score": 0.8}  # Simplified for report
            ),
            "detailed_analysis": self._get_detailed_drift_info()
        }

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Gibt Überwachungsstatistiken zurück."""
        return {
            "decisions_monitored": self.stats["decisions_monitored"],
            "drift_events": self.stats["drift_events"],
            "alerts_triggered": self.stats["alerts_triggered"],
            "baseline_resets": self.stats["baseline_resets"],
            "max_drift_detected": self.stats["max_drift_detected"],
            "meta_learner_corrections": self.stats["meta_learner_corrections"],
            "current_drift": self.drift_indicators["overall_drift"],
            "monitoring_window_size": self.monitoring_window,
            "alert_threshold": self.alert_threshold
        }


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale VDD-Instanz
_vdd_instance: Optional[ValueDriftDetector] = None

def _get_vdd_instance(config: Optional[Dict[str, Any]] = None) -> ValueDriftDetector:
    """Lazy-Loading der VDD-Instanz."""
    global _vdd_instance
    if _vdd_instance is None or config is not None:
        _vdd_instance = ValueDriftDetector(config)
    return _vdd_instance


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
        # VDD-Konfiguration aus Context
        vdd_config = context.get("config", {}).get("vdd", {})
        
        # VDD-Instanz
        vdd = _get_vdd_instance(vdd_config)
        
        # Profil aus Context
        profile = context.get("profile", profiles.get_default_profile())
        
        # Action bestimmen (VDD kann verschiedene Aktionen ausführen)
        action = context.get("vdd_action", "monitor")
        
        if action == "monitor":
            # Standard: Entscheidung überwachen
            if log_manager:
                log_manager.log_event(
                    "VDD",
                    f"Überwache Entscheidung (Window: {vdd.monitoring_window}, "
                    f"Threshold: {vdd.alert_threshold})",
                    "INFO"
                )
            
            # Führe Monitoring durch
            monitoring_result = vdd.monitor_decision(input_text, context)
            
            # Erstelle VDD-Ergebnis
            vdd_result = {
                "drift_detected": monitoring_result["drift_detected"],
                "drift_severity": monitoring_result["drift_severity"],
                "overall_drift": monitoring_result["drift_analysis"]["overall_drift"],
                "drift_components": monitoring_result["drift_analysis"],
                "alert_level": monitoring_result["alert_status"]["alert_level"],
                "alert_triggered": monitoring_result["alert_status"]["alert_triggered"],
                "trend": monitoring_result["trend_analysis"]["trend_direction"],
                "recommendations": monitoring_result["recommendations"][:3],  # Top 3
                "baseline_age_hours": monitoring_result["baseline"]["age_hours"],
                "decisions_monitored": monitoring_result["stats"]["decisions_monitored"]
            }
            
            # Speichere detaillierte Analyse wenn gewünscht
            if vdd_config.get("include_details", False):
                vdd_result["detailed_analysis"] = {
                    "trend_analysis": monitoring_result["trend_analysis"],
                    "pattern_analysis": monitoring_result["pattern_analysis"],
                    "meta_learner_status": monitoring_result["meta_learner_status"],
                    "specific_alerts": monitoring_result["alert_status"]["specific_alerts"]
                }
            
        elif action == "report":
            # Umfassender Drift-Report
            if log_manager:
                log_manager.log_event("VDD", "Generiere VDD-Report", "INFO")
            
            report = vdd.get_drift_report()
            
            vdd_result = {
                "report_generated": True,
                "summary": report["summary"],
                "drift_indicators": report["drift_indicators"],
                "trends": report["trends"],
                "patterns": report["patterns"],
                "recommendations": report["recommendations"],
                "module_integration": report["module_integration"]
            }
            
        elif action == "reset_baseline":
            # Baseline zurücksetzen
            if log_manager:
                log_manager.log_event("VDD", "Setze Baseline zurück", "INFO")
            
            old_baseline = vdd.baseline["profile"].copy()
            new_baseline = context.get("new_baseline")
            
            vdd.reset_baseline(new_baseline)
            
            vdd_result = {
                "baseline_reset": True,
                "old_baseline": old_baseline,
                "new_baseline": vdd.baseline["profile"].copy(),
                "reset_count": vdd.stats["baseline_resets"]
            }
            
        elif action == "get_stats":
            # Statistiken abrufen
            stats = vdd.get_monitoring_stats()
            
            vdd_result = {
                "stats_retrieved": True,
                "monitoring_stats": stats
            }
            
        else:
            raise ValueError(f"Unbekannte VDD-Action: {action}")
        
        # Speichere im Context
        context["vdd_result"] = vdd_result
        
        # Log wenn Drift erkannt
        if action == "monitor" and vdd_result["drift_detected"]:
            if log_manager:
                log_manager.log_event(
                    "VDD",
                    f"DRIFT ERKANNT - Severity: {vdd_result['drift_severity']}, "
                    f"Overall: {vdd_result['overall_drift']:.3f}",
                    "WARNING" if vdd_result["drift_severity"] in ["moderate", "high"] else "CRITICAL"
                )
        
        return {
            "success": True,
            "result": vdd_result,
            "module": "vdd",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"VDD error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("VDD", error_msg, "ERROR")
        
        # Fehler-Fallback
        context["vdd_result"] = {
            "error": True,
            "error_message": error_msg,
            "drift_detected": False,
            "overall_drift": 0.0,
            "recommendations": ["VDD-Fehler - manuelle Überprüfung erforderlich"]
        }
        
        return {
            "success": False,
            "error": error_msg,
            "module": "vdd",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die Verwendung des VDD-Moduls."""
    print("=== INTEGRA VDD (Value Drift Detection) Demo v2.0 ===")
    print("Standardisierte Baukasten-Integration\n")
    
    # Test-Profile für Drift-Simulation
    base_profile = profiles.get_default_profile()
    drifting_profile = base_profile.copy()
    
    # Konfiguration
    config = {
        "vdd": {
            "monitoring_window": 50,
            "alert_threshold": 0.15,
            "include_details": True,
            "enable_meta_learning_check": True
        }
    }
    
    # Phase 1: Baseline etablieren
    print("1. Phase: Baseline etablieren (5 normale Entscheidungen)")
    for i in range(5):
        test_context = {
            "profile": base_profile.copy(),
            "config": config,
            "decision_path": "deep",
            "confidence": 0.85,
            "simple_ethics_result": {
                "scores": {p: 0.85 for p in principles.ALIGN_KEYS},
                "violations": [],
                "overall_score": 0.85
            }
        }
        
        result = run_module(f"Normale Entscheidung {i+1}", test_context)
        
        if i == 4 and result["success"]:
            vdd_result = result["result"]
            print(f"   Baseline etabliert - Drift: {vdd_result['overall_drift']:.3f}")
            print(f"   Entscheidungen überwacht: {vdd_result['decisions_monitored']}")
    
    # Phase 2: Graduelle Drift mit Context-Integration
    print("\n2. Phase: Graduelle Drift einführen (10 Entscheidungen)")
    for i in range(10):
        # Profile langsam verändern
        drifting_profile["integrity"] *= 0.97
        drifting_profile["nurturing"] *= 1.02
        
        test_context = {
            "profile": drifting_profile.copy(),
            "config": config,
            "decision_path": "deep",
            "confidence": 0.8 - (i * 0.02),
            "simple_ethics_result": {
                "scores": {
                    "integrity": 0.8 - (i * 0.03),
                    "nurturing": 0.7 + (i * 0.02),
                    "governance": 0.75,
                    "awareness": 0.8,
                    "learning": 0.7
                },
                "violations": ["integrity"] if i > 5 else [],
                "overall_score": 0.75 - (i * 0.02)
            }
        }
        
        # Füge gelegentlich andere Module hinzu
        if i % 3 == 0:
            test_context["etb_result"] = {
                "final_weights": {"integrity": 0.8, "nurturing": 1.2},
                "conflicts_detected": True
            }
        
        if i % 4 == 0:
            test_context["meta_learner_result"] = {
                "profile_updates": {"integrity": -0.02, "nurturing": 0.01},
                "learning_triggered": True
            }
        
        if i > 6:
            test_context["resl_result"] = {
                "risk_level": 0.6 + (i * 0.05),
                "triggered_conflicts": ["integrity", "governance"]
            }
        
        result = run_module(f"Driftende Entscheidung {i+1}", test_context)
        
        if i % 3 == 2 and result["success"]:
            vdd_result = result["result"]
            print(f"   Schritt {i+1}:")
            print(f"     Drift: {vdd_result['overall_drift']:.3f} ({vdd_result['drift_severity']})")
            print(f"     Alert: {vdd_result['alert_level']}")
            
            if vdd_result.get("detailed_analysis"):
                meta_status = vdd_result["detailed_analysis"]["meta_learner_status"]
                if meta_status["meta_learner_active"]:
                    print(f"     Meta-Learner: Aktiv (Stabilität: {meta_status['stability_score']:.2f})")
            
            if vdd_result["alert_triggered"]:
                print("     ⚠️ ALERT AUSGELÖST!")
                for rec in vdd_result["recommendations"][:2]:
                    print(f"       → {rec}")
    
    # Phase 3: Komplexe Drift-Situation
    print("\n3. Phase: Komplexe Drift-Situation mit mehreren Modulen")
    complex_context = {
        "profile": drifting_profile.copy(),
        "config": config,
        "confidence": 0.6,
        "simple_ethics_result": {
            "scores": {"integrity": 0.4, "nurturing": 0.9, "governance": 0.5},
            "violations": ["integrity", "governance"],
            "overall_score": 0.6
        },
        "etb_result": {
            "conflicts_detected": True,
            "critical_tradeoffs": [{"losing_principle": "integrity", "impact": 0.3}]
        },
        "pae_result": {
            "primary_anchor": "nurturing"
        },
        "meta_learner_result": {
            "profile_updates": {"integrity": -0.05, "nurturing": 0.04, "governance": -0.03},
            "learning_triggered": True,
            "patterns": {"violation_trend": "increasing"}
        },
        "resl_result": {
            "risk_level": 0.8,
            "warning": "Hohe Wahrscheinlichkeit ethischer Folgekonflikte"
        },
        "nga_result": {
            "overall_compliance": 0.4,
            "violations": [{"framework": "gdpr", "severity": "high"}]
        }
    }
    
    result = run_module("Kritische Entscheidung mit Drift", complex_context)
    
    if result["success"]:
        vdd_result = result["result"]
        print(f"\n   📊 Drift-Analyse:")
        print(f"     Gesamt-Drift: {vdd_result['overall_drift']:.3f}")
        print(f"     Schweregrad: {vdd_result['drift_severity']}")
        print(f"     Trend: {vdd_result['trend']}")
        
        print(f"\n   📈 Drift-Komponenten:")
        for component, value in vdd_result["drift_components"].items():
            if component != "overall_drift":
                print(f"     {component}: {value:.3f}")
        
        if vdd_result.get("detailed_analysis"):
            patterns = vdd_result["detailed_analysis"]["pattern_analysis"]
            if patterns["patterns_detected"]:
                print(f"\n   🔍 Erkannte Muster:")
                for pattern, detected in patterns["pattern_types"].items():
                    if detected:
                        print(f"     ✓ {pattern}")
        
        print(f"\n   💡 Empfehlungen:")
        for rec in vdd_result["recommendations"]:
            print(f"     • {rec}")
    
    # Phase 4: Drift-Report
    print("\n4. Phase: Umfassender Drift-Report")
    report_context = {
        "config": config,
        "vdd_action": "report"
    }
    
    result = run_module("", report_context)
    
    if result["success"]:
        report = result["result"]
        summary = report["summary"]
        
        print(f"\n   📑 VDD-Report:")
        print(f"     Überwachungszeitraum: {summary['monitoring_period']['duration_hours']:.1f} Stunden")
        print(f"     Entscheidungen: {summary['decisions_monitored']}")
        print(f"     Drift-Level: {summary['overall_drift']:.3f} ({summary['drift_severity']})")
        print(f"     Alert-Status: {summary['alert_level']}")
        
        print(f"\n   📊 Modul-Integration:")
        module_int = report["module_integration"]
        print(f"     Meta-Learner Korrekturen: {module_int['meta_learner_corrections']}")
        if module_int["module_activity"]:
            print(f"     Modul-Aktivität:")
            for module, activity in module_int["module_activity"].items():
                print(f"       {module}: {activity['activity_rate']:.0%}")
        
        print(f"\n   🎯 Trends:")
        trends = report["trends"]
        print(f"     Richtung: {trends['trend_direction']}")
        print(f"     Stabilität: {trends['stability_index']:.2f}")
    
    # Phase 5: Baseline Reset
    print("\n5. Phase: Baseline Reset")
    reset_context = {
        "config": config,
        "vdd_action": "reset_baseline"
    }
    
    result = run_module("", reset_context)
    
    if result["success"]:
        reset_result = result["result"]
        print(f"   ✅ Baseline erfolgreich zurückgesetzt")
        print(f"   Resets insgesamt: {reset_result['reset_count']}")
    
    # Phase 6: Monitoring mit neuer Baseline
    print("\n6. Phase: Monitoring mit neuer Baseline")
    new_context = {
        "profile": drifting_profile.copy(),  # Verwendet das gedriftete Profil
        "config": config,
        "confidence": 0.7,
        "simple_ethics_result": {
            "scores": drifting_profile.copy(),
            "violations": [],
            "overall_score": 0.7
        }
    }
    
    result = run_module("Test nach Reset", new_context)
    
    if result["success"]:
        vdd_result = result["result"]
        print(f"   Drift nach Reset: {vdd_result['overall_drift']:.3f}")
        print(f"   Baseline-Alter: {vdd_result['baseline_age_hours']:.1f} Stunden")
    
    # Statistiken
    print("\n7. Statistiken abrufen")
    stats_context = {
        "config": config,
        "vdd_action": "get_stats"
    }
    
    result = run_module("", stats_context)
    
    if result["success"]:
        stats = result["result"]["monitoring_stats"]
        print(f"\n   📈 VDD-Statistiken:")
        print(f"     Überwachte Entscheidungen: {stats['decisions_monitored']}")
        print(f"     Drift-Events: {stats['drift_events']}")
        print(f"     Ausgelöste Alerts: {stats['alerts_triggered']}")
        print(f"     Max. erkannte Drift: {stats['max_drift_detected']:.3f}")
        print(f"     Meta-Learner Korrekturen: {stats['meta_learner_corrections']}")
    
    print("\n✅ VDD Demo v2.0 abgeschlossen!")
    print("\nDas Modul bietet:")
    print("  • Standardisierte Baukasten-Schnittstelle")
    print("  • Kontinuierliche Drift-Überwachung mit konfigurierbarem Fenster")
    print("  • Integration mit MetaLearner, ETB, PAE und anderen Modulen")
    print("  • Erweiterte Muster-Erkennung inkl. Meta-Learning Instabilität")
    print("  • Detaillierte Drift-Komponenten-Analyse")
    print("  • Automatische Baseline-Reset Option")
    print("  • Umfassende Reports und Statistiken")


if __name__ == "__main__":
    demo()