# -*- coding: utf-8 -*-
"""
Modulname: feedback.py
Beschreibung: Feedback-Schnittstelle für lernende KI-Systeme
Teil von: EVA Validator v1.0 - Universal Ethical Validation System
Autor: Dominik Knape
Lizenz: CC BY-NC-SA 4.0
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict
import threading

# EVA imports
try:
    from . import schema
except ImportError:
    import schema

from schema import (
    ValidationResult, ContextInput, DecisionInput,
    SeverityLevel, ValidationStatus, ScenarioType, UserRiskLevel
)


class FeedbackType(Enum):
    """Typen von Feedback."""
    LEARNING = "learning"              # Für Lernsysteme
    PROFILE = "profile"                # Für Profil-Anpassungen
    ARCHITECTURE = "architecture"       # Für Architektur-Optimierung
    COMPLIANCE = "compliance"          # Für Compliance-Verbesserungen
    QUALITY = "quality"               # Für Qualitätsverbesserungen


class ActionType(Enum):
    """Empfohlene Aktionen basierend auf Feedback."""
    ADJUST_WEIGHTS = "adjust_weights"
    RETRAIN = "retrain"
    UPDATE_RULES = "update_rules"
    REVIEW_ARCHITECTURE = "review_architecture"
    STRENGTHEN_PRINCIPLE = "strengthen_principle"
    WEAKEN_PRINCIPLE = "weaken_principle"
    ADD_PATTERN = "add_pattern"
    REMOVE_PATTERN = "remove_pattern"
    ESCALATE_SIMILAR = "escalate_similar"
    NO_ACTION = "no_action"


@dataclass
class FeedbackSignal:
    """Strukturiertes Feedback-Signal."""
    signal_id: str
    timestamp: str
    feedback_type: FeedbackType
    severity: SeverityLevel
    
    # Kontext
    decision_id: str
    scenario_type: ScenarioType
    validation_status: ValidationStatus
    
    # Kern-Feedback
    issue_category: str  # z.B. "low_integrity", "privacy_violation"
    issue_description: str
    confidence: float
    
    # Empfohlene Aktionen
    recommended_actions: List[Tuple[ActionType, Dict[str, Any]]] = field(default_factory=list)
    
    # Metriken
    impact_score: float = 0.0  # Wie wichtig ist dieses Feedback
    frequency: int = 1  # Wie oft ist das Problem aufgetreten
    
    # Zusätzliche Daten
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "signal_id": self.signal_id,
            "timestamp": self.timestamp,
            "feedback_type": self.feedback_type.value,
            "severity": self.severity.value,
            "decision_id": self.decision_id,
            "scenario_type": self.scenario_type.value,
            "validation_status": self.validation_status.value,
            "issue_category": self.issue_category,
            "issue_description": self.issue_description,
            "confidence": self.confidence,
            "recommended_actions": [
                (action.value, params) for action, params in self.recommended_actions
            ],
            "impact_score": self.impact_score,
            "frequency": self.frequency,
            "metadata": self.metadata
        }


class PatternDetector:
    """Erkennt Muster in Validierungsergebnissen."""
    
    def __init__(self):
        self.history = []
        self.max_history = 1000
        self.patterns = defaultdict(lambda: {"count": 0, "last_seen": None})
        
    def add_result(self, result: ValidationResult, evaluation: Dict[str, Any],
                  context: ContextInput):
        """Fügt Ergebnis zur Historie hinzu."""
        entry = {
            "timestamp": datetime.now(),
            "status": result.status,
            "severity": result.severity,
            "score": evaluation.get("final_score", 0),
            "violations": result.violated_principles,
            "scenario": context.scenario_type,
            "user_risk": context.user_risk,
            "source": context.source_system
        }
        
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Muster aktualisieren
        self._update_patterns(entry)
    
    def _update_patterns(self, entry: Dict[str, Any]):
        """Aktualisiert erkannte Muster."""
        # Violations-Muster
        for violation in entry["violations"]:
            pattern_key = f"violation:{violation}"
            self.patterns[pattern_key]["count"] += 1
            self.patterns[pattern_key]["last_seen"] = entry["timestamp"]
        
        # Szenario + Status Muster
        pattern_key = f"scenario:{entry['scenario'].value}:status:{entry['status'].value}"
        self.patterns[pattern_key]["count"] += 1
        self.patterns[pattern_key]["last_seen"] = entry["timestamp"]
        
        # Low Score Muster
        if entry["score"] < 0.5:
            pattern_key = f"low_score:{entry['scenario'].value}"
            self.patterns[pattern_key]["count"] += 1
            self.patterns[pattern_key]["last_seen"] = entry["timestamp"]
    
    def detect_issues(self, time_window: timedelta = timedelta(hours=24)) -> List[Dict[str, Any]]:
        """Erkennt problematische Muster."""
        issues = []
        cutoff = datetime.now() - time_window
        
        # Häufige Violations
        for pattern_key, data in self.patterns.items():
            if pattern_key.startswith("violation:") and data["last_seen"] and data["last_seen"] > cutoff:
                if data["count"] > 5:  # Schwellenwert
                    violation_type = pattern_key.split(":")[1]
                    issues.append({
                        "type": "frequent_violation",
                        "violation": violation_type,
                        "count": data["count"],
                        "severity": "high" if data["count"] > 10 else "medium"
                    })
        
        # Systematische Low Scores
        low_score_scenarios = []
        for pattern_key, data in self.patterns.items():
            if pattern_key.startswith("low_score:") and data["count"] > 3:
                scenario = pattern_key.split(":")[1]
                low_score_scenarios.append(scenario)
        
        if low_score_scenarios:
            issues.append({
                "type": "systematic_low_scores",
                "scenarios": low_score_scenarios,
                "severity": "high"
            })
        
        # Hohe Rejection Rate
        recent_entries = [e for e in self.history if e["timestamp"] > cutoff]
        if recent_entries:
            rejection_rate = sum(1 for e in recent_entries if e["status"] == ValidationStatus.REJECTED) / len(recent_entries)
            if rejection_rate > 0.3:  # 30% Rejection Rate
                issues.append({
                    "type": "high_rejection_rate",
                    "rate": rejection_rate,
                    "severity": "high"
                })
        
        return issues


class FeedbackGenerator:
    """Generiert strukturiertes Feedback basierend auf Validierungsergebnissen."""
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.feedback_history = []
        self.principle_scores = defaultdict(list)  # Track principle performance
        
    def generate_feedback(self, result: ValidationResult, 
                         evaluation: Dict[str, Any],
                         context: ContextInput) -> List[FeedbackSignal]:
        """Generiert Feedback-Signale basierend auf Validierungsergebnis."""
        signals = []
        
        # Pattern Detection Update
        self.pattern_detector.add_result(result, evaluation, context)
        
        # Principle Scores tracken
        for principle, score in evaluation.get("principle_scores", {}).items():
            self.principle_scores[principle].append(score)
        
        # 1. Direktes Feedback bei Violations
        if result.violated_principles:
            for violation in result.violated_principles:
                signal = self._create_violation_feedback(violation, result, evaluation, context)
                signals.append(signal)
        
        # 2. Low Score Feedback
        if evaluation.get("final_score", 1.0) < 0.5:
            signal = self._create_low_score_feedback(result, evaluation, context)
            signals.append(signal)
        
        # 3. Pattern-basiertes Feedback
        issues = self.pattern_detector.detect_issues()
        for issue in issues:
            signal = self._create_pattern_feedback(issue, result, context)
            if signal:
                signals.append(signal)
        
        # 4. Principle Balance Feedback
        balance_signal = self._check_principle_balance(result, evaluation, context)
        if balance_signal:
            signals.append(balance_signal)
        
        # Impact Scores berechnen
        for signal in signals:
            signal.impact_score = self._calculate_impact_score(signal)
        
        # History Update
        self.feedback_history.extend(signals)
        if len(self.feedback_history) > 1000:
            self.feedback_history = self.feedback_history[-1000:]
        
        return signals
    
    def _create_violation_feedback(self, violation: str, result: ValidationResult,
                                 evaluation: Dict[str, Any], 
                                 context: ContextInput) -> FeedbackSignal:
        """Erstellt Feedback für eine spezifische Violation."""
        signal = FeedbackSignal(
            signal_id=f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}-V",
            timestamp=datetime.now().isoformat(),
            feedback_type=FeedbackType.LEARNING,
            severity=SeverityLevel.HIGH,
            decision_id=getattr(context, 'decision_id', 'unknown'),
            scenario_type=context.scenario_type,
            validation_status=result.status,
            issue_category=f"{violation}_violation",
            issue_description=f"Prinzip '{violation}' wurde verletzt",
            confidence=evaluation.get("confidence", 0.8)
        )
        
        # Empfohlene Aktionen
        if violation in ["integrity", "governance"]:
            signal.recommended_actions.append(
                (ActionType.STRENGTHEN_PRINCIPLE, {"principle": violation, "factor": 1.2})
            )
            signal.recommended_actions.append(
                (ActionType.ADD_PATTERN, {"category": violation, "pattern_type": "violation"})
            )
        
        if violation == "privacy_violation":
            signal.recommended_actions.append(
                (ActionType.UPDATE_RULES, {"rule_category": "privacy", "action": "tighten"})
            )
        
        # Frequency aus Pattern Detector
        pattern_key = f"violation:{violation}"
        if pattern_key in self.pattern_detector.patterns:
            signal.frequency = self.pattern_detector.patterns[pattern_key]["count"]
        
        return signal
    
    def _create_low_score_feedback(self, result: ValidationResult,
                                  evaluation: Dict[str, Any],
                                  context: ContextInput) -> FeedbackSignal:
        """Erstellt Feedback für niedrige Scores."""
        signal = FeedbackSignal(
            signal_id=f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}-LS",
            timestamp=datetime.now().isoformat(),
            feedback_type=FeedbackType.QUALITY,
            severity=SeverityLevel.WARNING,
            decision_id=getattr(context, 'decision_id', 'unknown'),
            scenario_type=context.scenario_type,
            validation_status=result.status,
            issue_category="low_ethical_score",
            issue_description=f"Ethik-Score ({evaluation.get('final_score', 0):.2f}) unter kritischem Niveau",
            confidence=evaluation.get("confidence", 0.7)
        )
        
        # Welche Prinzipien sind schwach?
        weak_principles = []
        for principle, score in evaluation.get("principle_scores", {}).items():
            if score < 0.5:
                weak_principles.append(principle)
        
        if weak_principles:
            signal.recommended_actions.append(
                (ActionType.ADJUST_WEIGHTS, {"principles": weak_principles, "direction": "increase"})
            )
        
        # Bei systematischen Low Scores
        pattern_key = f"low_score:{context.scenario_type.value}"
        if pattern_key in self.pattern_detector.patterns:
            if self.pattern_detector.patterns[pattern_key]["count"] > 5:
                signal.recommended_actions.append(
                    (ActionType.RETRAIN, {"focus_area": context.scenario_type.value})
                )
        
        return signal
    
    def _create_pattern_feedback(self, issue: Dict[str, Any], 
                               result: ValidationResult,
                               context: ContextInput) -> Optional[FeedbackSignal]:
        """Erstellt Feedback basierend auf erkannten Mustern."""
        if issue["type"] == "frequent_violation":
            return FeedbackSignal(
                signal_id=f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}-P",
                timestamp=datetime.now().isoformat(),
                feedback_type=FeedbackType.ARCHITECTURE,
                severity=SeverityLevel.HIGH if issue["severity"] == "high" else SeverityLevel.WARNING,
                decision_id="pattern_based",
                scenario_type=context.scenario_type,
                validation_status=result.status,
                issue_category="systematic_issue",
                issue_description=f"Häufige Verletzung: {issue['violation']} ({issue['count']}x)",
                confidence=0.9,
                recommended_actions=[
                    (ActionType.REVIEW_ARCHITECTURE, {"focus": issue["violation"]}),
                    (ActionType.ESCALATE_SIMILAR, {"pattern": issue["violation"]})
                ],
                frequency=issue["count"]
            )
        
        elif issue["type"] == "high_rejection_rate":
            return FeedbackSignal(
                signal_id=f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}-RR",
                timestamp=datetime.now().isoformat(),
                feedback_type=FeedbackType.QUALITY,
                severity=SeverityLevel.CRITICAL,
                decision_id="pattern_based",
                scenario_type=context.scenario_type,
                validation_status=result.status,
                issue_category="high_rejection_rate",
                issue_description=f"Hohe Ablehnungsrate: {issue['rate']:.1%}",
                confidence=0.95,
                recommended_actions=[
                    (ActionType.REVIEW_ARCHITECTURE, {"urgency": "high"}),
                    (ActionType.ADJUST_WEIGHTS, {"action": "recalibrate"})
                ]
            )
        
        return None
    
    def _check_principle_balance(self, result: ValidationResult,
                               evaluation: Dict[str, Any],
                               context: ContextInput) -> Optional[FeedbackSignal]:
        """Prüft Balance zwischen Prinzipien."""
        if not self.principle_scores:
            return None
        
        # Durchschnittliche Scores pro Prinzip
        avg_scores = {}
        for principle, scores in self.principle_scores.items():
            if len(scores) >= 10:  # Genug Daten
                avg_scores[principle] = statistics.mean(scores[-50:])  # Letzte 50
        
        if not avg_scores:
            return None
        
        # Unbalancierte Prinzipien finden
        mean_avg = statistics.mean(avg_scores.values())
        imbalanced = []
        
        for principle, avg in avg_scores.items():
            if abs(avg - mean_avg) > 0.2:  # 20% Abweichung
                imbalanced.append({
                    "principle": principle,
                    "avg_score": avg,
                    "deviation": avg - mean_avg
                })
        
        if imbalanced:
            return FeedbackSignal(
                signal_id=f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}-B",
                timestamp=datetime.now().isoformat(),
                feedback_type=FeedbackType.PROFILE,
                severity=SeverityLevel.WARNING,
                decision_id="balance_check",
                scenario_type=context.scenario_type,
                validation_status=result.status,
                issue_category="principle_imbalance",
                issue_description=f"Unbalancierte Prinzipien erkannt: {[p['principle'] for p in imbalanced]}",
                confidence=0.8,
                recommended_actions=[
                    (ActionType.ADJUST_WEIGHTS, {"rebalance": imbalanced})
                ],
                metadata={"imbalanced_principles": imbalanced}
            )
        
        return None
    
    def _calculate_impact_score(self, signal: FeedbackSignal) -> float:
        """Berechnet Impact Score für Priorisierung."""
        base_score = 0.5
        
        # Severity-basiert
        severity_scores = {
            SeverityLevel.INFO: 0.1,
            SeverityLevel.WARNING: 0.3,
            SeverityLevel.CRITICAL: 0.7,
            SeverityLevel.BLOCKED: 0.9
        }
        base_score = severity_scores.get(signal.severity, 0.5)
        
        # Frequency-Bonus
        if signal.frequency > 10:
            base_score += 0.2
        elif signal.frequency > 5:
            base_score += 0.1
        
        # Feedback-Type Modifier
        if signal.feedback_type == FeedbackType.ARCHITECTURE:
            base_score *= 1.2
        elif signal.feedback_type == FeedbackType.COMPLIANCE:
            base_score *= 1.3
        
        return min(1.0, base_score)


class FeedbackAggregator:
    """Aggregiert und konsolidiert Feedback über Zeit."""
    
    def __init__(self):
        self.aggregated_feedback = defaultdict(lambda: {
            "count": 0,
            "first_seen": None,
            "last_seen": None,
            "impact_sum": 0.0,
            "examples": []
        })
        self.lock = threading.Lock()
    
    def add_feedback(self, signals: List[FeedbackSignal]):
        """Fügt neue Feedback-Signale hinzu."""
        with self.lock:
            for signal in signals:
                key = f"{signal.issue_category}:{signal.feedback_type.value}"
                
                agg = self.aggregated_feedback[key]
                agg["count"] += 1
                agg["impact_sum"] += signal.impact_score
                
                if agg["first_seen"] is None:
                    agg["first_seen"] = signal.timestamp
                agg["last_seen"] = signal.timestamp
                
                # Beispiele speichern (max 5)
                if len(agg["examples"]) < 5:
                    agg["examples"].append(signal.signal_id)
    
    def get_summary(self, min_count: int = 3) -> Dict[str, Any]:
        """Gibt aggregierte Zusammenfassung zurück."""
        with self.lock:
            summary = {
                "total_feedback_types": len(self.aggregated_feedback),
                "high_impact_issues": [],
                "trending_issues": [],
                "recommendations": []
            }
            
            # High Impact Issues
            for key, data in self.aggregated_feedback.items():
                if data["count"] >= min_count:
                    avg_impact = data["impact_sum"] / data["count"]
                    if avg_impact > 0.7:
                        summary["high_impact_issues"].append({
                            "issue": key,
                            "count": data["count"],
                            "avg_impact": avg_impact,
                            "last_seen": data["last_seen"]
                        })
            
            # Trending (recent + frequent)
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            for key, data in self.aggregated_feedback.items():
                if data["last_seen"] > cutoff and data["count"] > 5:
                    summary["trending_issues"].append({
                        "issue": key,
                        "count": data["count"],
                        "trend": "increasing"  # Simplified
                    })
            
            # Konsolidierte Empfehlungen
            summary["recommendations"] = self._generate_consolidated_recommendations()
            
            return summary
    
    def _generate_consolidated_recommendations(self) -> List[Dict[str, Any]]:
        """Generiert konsolidierte Empfehlungen."""
        recommendations = []
        
        # Häufigste Issues
        sorted_issues = sorted(
            self.aggregated_feedback.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        for key, data in sorted_issues[:5]:  # Top 5
            issue_type = key.split(":")[0]
            
            if "violation" in issue_type:
                recommendations.append({
                    "priority": "high",
                    "action": "strengthen_validation",
                    "target": issue_type,
                    "reason": f"Häufige Verletzung ({data['count']}x)"
                })
            elif "low_score" in issue_type:
                recommendations.append({
                    "priority": "medium",
                    "action": "improve_scoring",
                    "target": "ethical_evaluation",
                    "reason": f"Systematisch niedrige Scores"
                })
        
        return recommendations


class FeedbackSystem:
    """
    Hauptsystem für Feedback-Generierung und -Management.
    Orchestriert alle Feedback-Komponenten.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        
        # Komponenten
        self.generator = FeedbackGenerator()
        self.aggregator = FeedbackAggregator()
        
        # Callbacks für verschiedene Systeme
        self.callbacks = {
            FeedbackType.LEARNING: [],
            FeedbackType.PROFILE: [],
            FeedbackType.ARCHITECTURE: [],
            FeedbackType.COMPLIANCE: [],
            FeedbackType.QUALITY: []
        }
        
        # Statistiken
        self.stats = {
            "total_signals": 0,
            "by_type": defaultdict(int),
            "by_severity": defaultdict(int)
        }
    
    def prepare_feedback(self, result: ValidationResult,
                        evaluation: Dict[str, Any],
                        context: ContextInput) -> Dict[str, Any]:
        """
        Bereitet Feedback für die Validierungsantwort vor.
        
        Returns:
            Feedback-Dictionary für ValidationResult
        """
        if not self.enabled:
            return {"enabled": False}
        
        # Feedback generieren
        signals = self.generator.generate_feedback(result, evaluation, context)
        
        # Aggregieren
        self.aggregator.add_feedback(signals)
        
        # Callbacks ausführen
        for signal in signals:
            self._execute_callbacks(signal)
        
        # Statistiken
        self.stats["total_signals"] += len(signals)
        for signal in signals:
            self.stats["by_type"][signal.feedback_type.value] += 1
            self.stats["by_severity"][signal.severity.value] += 1
        
        # Feedback für Response vorbereiten
        feedback_data = {
            "enabled": True,
            "signals_generated": len(signals),
            "primary_issues": [],
            "recommended_actions": {}
        }
        
        # Top Issues
        high_impact_signals = sorted(signals, key=lambda s: s.impact_score, reverse=True)
        for signal in high_impact_signals[:3]:  # Top 3
            feedback_data["primary_issues"].append({
                "category": signal.issue_category,
                "description": signal.issue_description,
                "severity": signal.severity.value,
                "impact": signal.impact_score
            })
        
        # Konsolidierte Aktionen
        action_groups = defaultdict(list)
        for signal in signals:
            for action, params in signal.recommended_actions:
                action_groups[action].append(params)
        
        # Deduplizieren und konsolidieren
        for action_type, params_list in action_groups.items():
            if action_type == ActionType.ADJUST_WEIGHTS:
                # Alle Prinzipien sammeln
                all_principles = set()
                for params in params_list:
                    if "principles" in params:
                        all_principles.update(params["principles"])
                    elif "principle" in params:
                        all_principles.add(params["principle"])
                
                if all_principles:
                    feedback_data["recommended_actions"]["adjust_weights"] = {
                        "principles": list(all_principles),
                        "action": "review_and_adjust"
                    }
            
            elif action_type == ActionType.RETRAIN:
                areas = set()
                for params in params_list:
                    if "focus_area" in params:
                        areas.add(params["focus_area"])
                
                if areas:
                    feedback_data["recommended_actions"]["retrain"] = {
                        "focus_areas": list(areas)
                    }
        
        # Learning-spezifisches Feedback
        if result.status == ValidationStatus.REJECTED:
            feedback_data["adjust_learning"] = True
            feedback_data["learning_focus"] = "rejection_prevention"
        elif result.severity in [SeverityLevel.WARNING, SeverityLevel.CRITICAL]:
            feedback_data["adjust_learning"] = True
            feedback_data["learning_focus"] = "risk_mitigation"
        else:
            feedback_data["adjust_learning"] = False
        
        # Profile-Anpassung
        feedback_data["adjust_profile"] = len([s for s in signals if s.feedback_type == FeedbackType.PROFILE]) > 0
        
        return feedback_data
    
    def register_callback(self, feedback_type: FeedbackType, 
                         callback: Callable[[FeedbackSignal], None]):
        """Registriert Callback für bestimmten Feedback-Typ."""
        if feedback_type in self.callbacks:
            self.callbacks[feedback_type].append(callback)
    
    def _execute_callbacks(self, signal: FeedbackSignal):
        """Führt registrierte Callbacks aus."""
        for callback in self.callbacks.get(signal.feedback_type, []):
            try:
                callback(signal)
            except Exception as e:
                print(f"Callback-Fehler: {e}")
    
    def get_feedback_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Gibt Feedback-Zusammenfassung zurück."""
        summary = self.aggregator.get_summary()
        
        # Statistiken hinzufügen
        summary["statistics"] = {
            "total_signals": self.stats["total_signals"],
            "by_type": dict(self.stats["by_type"]),
            "by_severity": dict(self.stats["by_severity"])
        }
        
        # Pattern-basierte Insights
        issues = self.generator.pattern_detector.detect_issues(
            time_window or timedelta(hours=24)
        )
        summary["detected_patterns"] = issues
        
        return summary
    
    def export_feedback_report(self, output_file: str) -> bool:
        """Exportiert detaillierten Feedback-Report."""
        try:
            report = {
                "report_date": datetime.now().isoformat(),
                "summary": self.get_feedback_summary(),
                "detailed_feedback": [],
                "recommendations": []
            }
            
            # Letzte Feedback-Signale
            recent_signals = self.generator.feedback_history[-100:]  # Letzte 100
            for signal in recent_signals:
                report["detailed_feedback"].append(signal.to_dict())
            
            # Konsolidierte Empfehlungen
            report["recommendations"] = self.aggregator._generate_consolidated_recommendations()
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export-Fehler: {e}")
            return False
    
    def close(self):
        """Schließt Feedback-System."""
        # Final Summary generieren
        if self.stats["total_signals"] > 0:
            final_summary = self.get_feedback_summary()
            print(f"Feedback-System geschlossen. {self.stats['total_signals']} Signale generiert.")


def demo():
    """Demonstriert die Feedback-Funktionalität."""
    print("=== EVA Feedback System Demo ===\n")
    
    # Feedback-System erstellen
    feedback_system = FeedbackSystem({"enabled": True})
    
    # Demo-Callback
    def learning_callback(signal: FeedbackSignal):
        print(f"  → Learning Feedback: {signal.issue_category} (Impact: {signal.impact_score:.2f})")
    
    feedback_system.register_callback(FeedbackType.LEARNING, learning_callback)
    
    # Test 1: Violation Feedback
    print("1. Test: Violation Feedback")
    print("-" * 50)
    
    result1 = ValidationResult(
        validated=False,
        severity=SeverityLevel.CRITICAL,
        escalation_required=True,
        log_id="TEST-001",
        recommendation="Abgelehnt wegen Verletzungen",
        status=ValidationStatus.REJECTED,
        confidence=0.9,
        risk_score=0.8,
        violated_principles=["integrity", "privacy"],
        reasons=["Täuschung erkannt", "Datenschutzverletzung"]
    )
    
    evaluation1 = {
        "final_score": 0.3,
        "confidence": 0.9,
        "principle_scores": {
            "integrity": 0.2,
            "privacy": 0.1,
            "governance": 0.5,
            "nurturing": 0.6,
            "awareness": 0.5
        }
    }
    
    context1 = ContextInput(
        user_risk=UserRiskLevel.HIGH,
        scenario_type=ScenarioType.PRIVACY,
        source_system="TestSystem"
    )
    
    feedback1 = feedback_system.prepare_feedback(result1, evaluation1, context1)
    print(f"Signale generiert: {feedback1['signals_generated']}")
    print(f"Primäre Issues: {feedback1['primary_issues']}")
    print(f"Empfohlene Aktionen: {list(feedback1['recommended_actions'].keys())}")
    
    # Test 2: Low Score Pattern
    print("\n\n2. Test: Low Score Pattern")
    print("-" * 50)
    
    # Mehrere Low-Score-Ergebnisse simulieren
    for i in range(7):
        result = ValidationResult(
            validated=True,
            severity=SeverityLevel.WARNING,
            escalation_required=False,
            log_id=f"TEST-{i:03d}",
            recommendation="Mit Warnung akzeptiert",
            status=ValidationStatus.APPROVED_WITH_WARNINGS,
            confidence=0.6,
            risk_score=0.6,
            reasons=["Niedriger Score"]
        )
        
        evaluation = {
            "final_score": 0.45 - (i * 0.02),  # Abnehmende Scores
            "confidence": 0.6,
            "principle_scores": {
                "integrity": 0.4,
                "governance": 0.4,
                "nurturing": 0.5,
                "awareness": 0.5,
                "learning": 0.5
            }
        }
        
        context = ContextInput(
            scenario_type=ScenarioType.GENERAL,
            source_system="TestSystem"
        )
        
        feedback = feedback_system.prepare_feedback(result, evaluation, context)
    
    print("Pattern Detection aktiviert nach mehreren Low Scores")
    
    # Test 3: Principle Imbalance
    print("\n\n3. Test: Principle Imbalance")
    print("-" * 50)
    
    # Unbalancierte Scores simulieren
    for i in range(15):
        result = ValidationResult(
            validated=True,
            severity=SeverityLevel.INFO,
            escalation_required=False,
            log_id=f"BALANCE-{i:03d}",
            recommendation="OK",
            status=ValidationStatus.APPROVED,
            confidence=0.8,
            risk_score=0.2
        )
        
        evaluation = {
            "final_score": 0.7,
            "confidence": 0.8,
            "principle_scores": {
                "integrity": 0.9,  # Sehr hoch
                "governance": 0.8,
                "nurturing": 0.3,  # Sehr niedrig
                "awareness": 0.7,
                "learning": 0.5
            }
        }
        
        context = ContextInput(scenario_type=ScenarioType.GENERAL)
        feedback = feedback_system.prepare_feedback(result, evaluation, context)
    
    # Test 4: Feedback Summary
    print("\n\n4. Feedback Summary")
    print("-" * 50)
    
    summary = feedback_system.get_feedback_summary()
    print(f"Total Feedback Types: {summary['total_feedback_types']}")
    print(f"High Impact Issues: {len(summary['high_impact_issues'])}")
    if summary['high_impact_issues']:
        for issue in summary['high_impact_issues'][:2]:
            print(f"  - {issue['issue']}: Count={issue['count']}, Impact={issue['avg_impact']:.2f}")
    
    print(f"\nDetected Patterns: {len(summary['detected_patterns'])}")
    for pattern in summary['detected_patterns']:
        print(f"  - {pattern['type']}: {pattern.get('severity', 'N/A')}")
    
    print(f"\nStatistics:")
    print(f"  Total Signals: {summary['statistics']['total_signals']}")
    print(f"  By Type: {dict(summary['statistics']['by_type'])}")
    
    # Test 5: Export
    print("\n\n5. Feedback Report Export")
    print("-" * 50)
    
    success = feedback_system.export_feedback_report("feedback_report_demo.json")
    print(f"Report exportiert: {'✓' if success else '✗'}")
    
    # Aufräumen
    feedback_system.close()
    
    # Demo-Datei löschen
    try:
        import os
        os.remove("feedback_report_demo.json")
    except:
        pass
    
    print("\n✅ Feedback System Demo abgeschlossen!")


if __name__ == "__main__":
    demo()