# -*- coding: utf-8 -*-
"""
Modulname: meta_learner.py
Beschreibung: Meta-Learning System für INTEGRA Full - Erweitert mini_learner um vollwertiges adaptives Lernen
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Erweitert mini_learner statt es zu ersetzen
- Modulare Komponenten-Architektur
- Baukasten-kompatible Context-Nutzung
- Externe Konfiguration möglich
"""

from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque, Counter
from pathlib import Path
import json
import statistics
import math
import hashlib
import uuid

# Standardisierte Imports
try:
    from integra.core import principles, profiles
    from integra.advanced import mini_learner
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from advanced import mini_learner
        log_manager = None
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
            from advanced import mini_learner
            log_manager = None
        except ImportError:
            print("❌ Fehler: Core/Advanced Module nicht gefunden!")
            # Dummy-Implementierungen
            class principles:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            class profiles:
                @staticmethod
                def get_default_profile():
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            class mini_learner:
                class MiniLearner:
                    def learn(self, *args, **kwargs):
                        return {"profile_updates": {}}
            log_manager = None


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class LearningMode(Enum):
    """Modi des Meta-Learning Systems."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    EXPLORATORY = "exploratory"


class FeedbackType(Enum):
    """Typen von Feedback."""
    EXPLICIT_POSITIVE = "explicit_positive"
    EXPLICIT_NEGATIVE = "explicit_negative"
    IMPLICIT_SUCCESS = "implicit_success"
    IMPLICIT_FAILURE = "implicit_failure"
    SYSTEM_DERIVED = "system_derived"


class PatternType(Enum):
    """Typen von Lernmustern."""
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    NEUTRAL_PATTERN = "neutral_pattern"
    EMERGING_PATTERN = "emerging_pattern"
    ANOMALY = "anomaly"


class InsightPriority(Enum):
    """Prioritätsstufen für Meta-Insights."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LearningExperience:
    """Strukturierte Lernerfahrung."""
    experience_id: str
    timestamp: datetime
    decision_id: str
    
    # Kontext
    decision_path: str
    confidence: float
    input_summary: str
    
    # Ethik-Daten
    ethical_scores: Dict[str, float]
    violations: List[str]
    overall_ethics_score: float
    
    # Modul-Ergebnisse
    module_results: Dict[str, Dict[str, Any]]
    
    # Feedback
    feedback: Dict[str, Any]
    feedback_type: FeedbackType
    
    # Erfolgsmetriken
    success_metrics: Dict[str, float]
    
    # Kontext-Faktoren
    context_factors: List[str]
    
    # Profil-Snapshot
    profile_snapshot: Dict[str, float]


@dataclass
class LearningPattern:
    """Erkanntes Lernmuster."""
    pattern_id: str
    pattern_type: PatternType
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int
    
    # Muster-Eigenschaften
    key_features: List[str]
    average_success: float
    confidence: float
    
    # Assoziierte Erfahrungen
    experience_ids: List[str] = field(default_factory=list)
    
    # Empfohlene Aktionen
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MetaInsight:
    """Meta-Erkenntnis über das Lernsystem."""
    insight_id: str
    timestamp: datetime
    priority: InsightPriority
    
    # Inhalt
    insight_type: str
    description: str
    evidence: List[str]
    
    # Empfehlungen
    recommendations: List[str]
    
    # Tracking
    addressed: bool = False
    effectiveness: Optional[float] = None


@dataclass
class ProfileEvolution:
    """Entwicklung eines ethischen Profils."""
    evolution_id: str
    start_timestamp: datetime
    
    # Profil-Historie
    profile_history: List[Tuple[datetime, Dict[str, float]]]
    
    # Änderungsanalyse
    total_changes: Dict[str, float]
    change_velocity: Dict[str, float]
    stability_score: float
    
    # Treiber
    primary_drivers: List[str]
    
    def add_snapshot(self, profile: Dict[str, float]) -> None:
        """Fügt neuen Profil-Snapshot hinzu."""
        self.profile_history.append((datetime.now(), profile.copy()))
        self._update_analysis()
    
    def _update_analysis(self) -> None:
        """Aktualisiert Änderungsanalyse."""
        if len(self.profile_history) < 2:
            return
        
        # Gesamtänderungen
        first_profile = self.profile_history[0][1]
        last_profile = self.profile_history[-1][1]
        
        for principle in principles.ALIGN_KEYS:
            self.total_changes[principle] = last_profile.get(principle, 1.0) - first_profile.get(principle, 1.0)
        
        # Änderungsgeschwindigkeit (letzte 5 Snapshots)
        recent = self.profile_history[-5:]
        if len(recent) >= 2:
            time_span = (recent[-1][0] - recent[0][0]).total_seconds()
            if time_span > 0:
                for principle in principles.ALIGN_KEYS:
                    change = recent[-1][1].get(principle, 1.0) - recent[0][1].get(principle, 1.0)
                    self.change_velocity[principle] = change / (time_span / 3600)  # Änderung pro Stunde


# ============================================================================
# KOMPONENTEN
# ============================================================================

class ExperienceCollector:
    """Sammelt und strukturiert Lernerfahrungen."""
    
    def __init__(self, memory_size: int = 5000):
        self.memory_size = memory_size
        self.experiences: deque = deque(maxlen=memory_size)
        self.experience_index: Dict[str, LearningExperience] = {}
        
    def collect_from_context(self, context: Dict[str, Any]) -> Optional[LearningExperience]:
        """Sammelt Lernerfahrung aus Entscheidungskontext."""
        try:
            # Basis-Informationen
            experience_id = f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
            decision_id = context.get("decision_id", "unknown")
            
            # Entscheidungsdaten
            decision_path = context.get("decision_path", context.get("path", "unknown"))
            confidence = context.get("confidence", 0.5)
            input_summary = self._summarize_input(context)
            
            # Ethik-Daten
            ethics = context.get("ethics", {})
            ethical_scores = ethics.get("scores", {p: 0.5 for p in principles.ALIGN_KEYS})
            violations = ethics.get("violations", [])
            overall_ethics_score = ethics.get("overall_score", 0.5)
            
            # Modul-Ergebnisse sammeln
            module_results = self._collect_module_results(context)
            
            # Feedback extrahieren
            feedback_data, feedback_type = self._extract_feedback(context)
            
            # Erfolgsmetriken berechnen
            success_metrics = self._calculate_success_metrics(
                ethical_scores, violations, confidence, feedback_data
            )
            
            # Kontext-Faktoren
            context_factors = self._identify_context_factors(context)
            
            # Profil-Snapshot
            profile_snapshot = context.get("profile", profiles.get_default_profile()).copy()
            
            # Erfahrung erstellen
            experience = LearningExperience(
                experience_id=experience_id,
                timestamp=datetime.now(),
                decision_id=decision_id,
                decision_path=decision_path,
                confidence=confidence,
                input_summary=input_summary,
                ethical_scores=ethical_scores,
                violations=violations,
                overall_ethics_score=overall_ethics_score,
                module_results=module_results,
                feedback=feedback_data,
                feedback_type=feedback_type,
                success_metrics=success_metrics,
                context_factors=context_factors,
                profile_snapshot=profile_snapshot
            )
            
            # Speichern
            self.experiences.append(experience)
            self.experience_index[experience_id] = experience
            
            return experience
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("MetaLearner", f"Failed to collect experience: {str(e)}", "ERROR")
            return None
    
    def _summarize_input(self, context: Dict[str, Any]) -> str:
        """Erstellt Zusammenfassung der Eingabe."""
        input_text = context.get("input_text", context.get("user_input", ""))
        return input_text[:100] + "..." if len(input_text) > 100 else input_text
    
    def _collect_module_results(self, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Sammelt relevante Ergebnisse aller Module."""
        results = {}
        
        # Relevante Module
        relevant_modules = [
            "simple_ethics", "etb", "pae", "vdd", "mini_learner",
            "replay_dna", "aso", "mini_audit"
        ]
        
        for module in relevant_modules:
            result_key = f"{module}_result"
            if result_key in context:
                # Extrahiere wichtige Daten
                module_data = context[result_key]
                if isinstance(module_data, dict):
                    results[module] = self._extract_key_data(module, module_data)
        
        return results
    
    def _extract_key_data(self, module: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Schlüsseldaten eines Moduls."""
        key_data = {
            "success": data.get("success", True),
            "processing_time": data.get("processing_time", 0.0)
        }
        
        # Modul-spezifische Daten
        if module == "etb":
            key_data["conflicts_detected"] = len(data.get("conflicts_detected", []))
            key_data["resolution_type"] = data.get("resolution", {}).get("type")
        
        elif module == "pae":
            key_data["principle_chosen"] = data.get("principle_chosen")
            key_data["resolution_basis"] = data.get("resolution", {}).get("basis")
        
        elif module == "vdd":
            key_data["drift_detected"] = data.get("drift_detected", False)
            key_data["drift_severity"] = data.get("drift_analysis", {}).get("overall_drift", 0.0)
        
        elif module == "mini_learner":
            key_data["profile_updates"] = data.get("profile_updates", {})
            key_data["learning_triggered"] = bool(key_data["profile_updates"])
        
        elif module == "aso":
            key_data["optimizations_applied"] = len(data.get("applied_optimizations", []))
            key_data["bottlenecks_found"] = len(data.get("bottlenecks", []))
        
        return key_data
    
    def _extract_feedback(self, context: Dict[str, Any]) -> Tuple[Dict[str, Any], FeedbackType]:
        """Extrahiert Feedback aus Context."""
        # Explizites Feedback
        if "user_feedback" in context:
            feedback = context["user_feedback"]
            if isinstance(feedback, dict):
                value = feedback.get("value", feedback.get("rating", 0.5))
                feedback_type = (FeedbackType.EXPLICIT_POSITIVE if value > 0.6 
                               else FeedbackType.EXPLICIT_NEGATIVE)
                return feedback, feedback_type
        
        # Implizites Feedback aus System-Signalen
        violations = context.get("ethics", {}).get("violations", [])
        confidence = context.get("confidence", 0.5)
        
        if violations:
            return {"value": 0.3, "reason": "ethical_violations"}, FeedbackType.IMPLICIT_FAILURE
        elif confidence > 0.85:
            return {"value": 0.8, "reason": "high_confidence"}, FeedbackType.IMPLICIT_SUCCESS
        else:
            return {"value": 0.5, "reason": "neutral"}, FeedbackType.SYSTEM_DERIVED
    
    def _calculate_success_metrics(self, 
                                 ethical_scores: Dict[str, float],
                                 violations: List[str],
                                 confidence: float,
                                 feedback: Dict[str, Any]) -> Dict[str, float]:
        """Berechnet mehrdimensionale Erfolgsmetriken."""
        metrics = {}
        
        # Ethische Qualität
        if violations:
            metrics["ethical_quality"] = 0.3 - (len(violations) * 0.1)
        else:
            avg_score = statistics.mean(ethical_scores.values()) if ethical_scores else 0.5
            metrics["ethical_quality"] = avg_score
        
        # Entscheidungssicherheit
        metrics["decision_confidence"] = confidence
        
        # Stakeholder-Zufriedenheit
        metrics["stakeholder_satisfaction"] = feedback.get("value", 0.5)
        
        # Gesamterfolg
        metrics["overall_success"] = statistics.mean([
            metrics["ethical_quality"],
            metrics["decision_confidence"],
            metrics["stakeholder_satisfaction"]
        ])
        
        return metrics
    
    def _identify_context_factors(self, context: Dict[str, Any]) -> List[str]:
        """Identifiziert relevante Kontextfaktoren."""
        factors = []
        
        # Entscheidungspfad
        path = context.get("decision_path", context.get("path", ""))
        if path:
            factors.append(f"path:{path}")
        
        # Komplexität
        if context.get("etb_result", {}).get("conflicts_detected"):
            factors.append("ethical_conflict")
        
        # Zeitdruck
        if context.get("time_pressure", False):
            factors.append("time_pressure")
        
        # Domain
        domain = context.get("domain", "general")
        factors.append(f"domain:{domain}")
        
        # Performance-Probleme
        if context.get("aso_result", {}).get("bottlenecks"):
            factors.append("performance_issues")
        
        return factors
    
    def get_recent_experiences(self, count: int = 100) -> List[LearningExperience]:
        """Gibt die letzten N Erfahrungen zurück."""
        return list(self.experiences)[-count:]
    
    def query_experiences(self, 
                         pattern: Optional[PatternType] = None,
                         min_success: Optional[float] = None,
                         context_factor: Optional[str] = None) -> List[LearningExperience]:
        """Sucht Erfahrungen nach Kriterien."""
        results = []
        
        for exp in self.experiences:
            # Pattern-Filter
            if pattern and not self._matches_pattern(exp, pattern):
                continue
            
            # Success-Filter
            if min_success and exp.success_metrics["overall_success"] < min_success:
                continue
            
            # Context-Filter
            if context_factor and context_factor not in exp.context_factors:
                continue
            
            results.append(exp)
        
        return results
    
    def _matches_pattern(self, experience: LearningExperience, pattern: PatternType) -> bool:
        """Prüft ob Erfahrung zu Pattern passt."""
        success = experience.success_metrics["overall_success"]
        
        if pattern == PatternType.SUCCESS_PATTERN:
            return success > 0.7
        elif pattern == PatternType.FAILURE_PATTERN:
            return success < 0.4
        else:
            return True


class PatternRecognizer:
    """Erkennt Muster in Lernerfahrungen."""
    
    def __init__(self):
        self.patterns: Dict[str, LearningPattern] = {}
        self.pattern_index: Dict[str, List[str]] = defaultdict(list)  # feature -> pattern_ids
        
    def analyze_experiences(self, experiences: List[LearningExperience]) -> List[LearningPattern]:
        """Analysiert Erfahrungen und erkennt Muster."""
        if len(experiences) < 5:
            return []
        
        # Gruppiere nach Ähnlichkeit
        pattern_groups = self._group_similar_experiences(experiences)
        
        # Erstelle/Update Patterns
        recognized_patterns = []
        
        for group_key, group_experiences in pattern_groups.items():
            if len(group_experiences) >= 3:  # Mindestens 3 für ein Muster
                pattern = self._create_or_update_pattern(group_key, group_experiences)
                if pattern:
                    recognized_patterns.append(pattern)
        
        # Erkenne Anomalien
        anomalies = self._detect_anomalies(experiences, recognized_patterns)
        recognized_patterns.extend(anomalies)
        
        return recognized_patterns
    
    def _group_similar_experiences(self, 
                                  experiences: List[LearningExperience]) -> Dict[str, List[LearningExperience]]:
        """Gruppiert ähnliche Erfahrungen."""
        groups = defaultdict(list)
        
        for exp in experiences:
            # Erstelle Gruppenschlüssel aus wichtigen Features
            key_parts = []
            
            # Erfolgs-Kategorie
            success = exp.success_metrics["overall_success"]
            if success > 0.7:
                key_parts.append("success")
            elif success < 0.4:
                key_parts.append("failure")
            else:
                key_parts.append("neutral")
            
            # Violations
            if exp.violations:
                key_parts.append("violations:" + ",".join(sorted(exp.violations)))
            
            # Hauptfaktoren
            main_factors = [f for f in exp.context_factors if f.startswith(("path:", "domain:"))]
            key_parts.extend(sorted(main_factors))
            
            group_key = "|".join(key_parts)
            groups[group_key].append(exp)
        
        return dict(groups)
    
    def _create_or_update_pattern(self, 
                                 group_key: str,
                                 experiences: List[LearningExperience]) -> Optional[LearningPattern]:
        """Erstellt oder aktualisiert ein Muster."""
        # Prüfe ob Pattern existiert
        if group_key in self.patterns:
            pattern = self.patterns[group_key]
            # Update existing pattern
            for exp in experiences:
                if exp.experience_id not in pattern.experience_ids:
                    pattern.experience_ids.append(exp.experience_id)
                    pattern.occurrence_count += 1
                    pattern.last_seen = max(pattern.last_seen, exp.timestamp)
        else:
            # Create new pattern
            pattern_id = f"PAT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hashlib.md5(group_key.encode()).hexdigest()[:6]}"
            
            # Bestimme Pattern-Typ
            avg_success = statistics.mean([e.success_metrics["overall_success"] for e in experiences])
            if avg_success > 0.7:
                pattern_type = PatternType.SUCCESS_PATTERN
            elif avg_success < 0.4:
                pattern_type = PatternType.FAILURE_PATTERN
            else:
                pattern_type = PatternType.NEUTRAL_PATTERN
            
            # Extrahiere gemeinsame Features
            key_features = self._extract_common_features(experiences)
            
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                first_seen=min(e.timestamp for e in experiences),
                last_seen=max(e.timestamp for e in experiences),
                occurrence_count=len(experiences),
                key_features=key_features,
                average_success=avg_success,
                confidence=self._calculate_pattern_confidence(experiences),
                experience_ids=[e.experience_id for e in experiences]
            )
            
            # Generiere Empfehlungen
            pattern.recommended_actions = self._generate_pattern_recommendations(pattern, experiences)
            
            self.patterns[group_key] = pattern
        
        return pattern
    
    def _extract_common_features(self, experiences: List[LearningExperience]) -> List[str]:
        """Extrahiert gemeinsame Features aus Erfahrungen."""
        if not experiences:
            return []
        
        # Sammle alle Features
        all_factors = [set(exp.context_factors) for exp in experiences]
        
        # Finde Schnittmenge
        common = set.intersection(*all_factors) if all_factors else set()
        
        # Füge Violation-Patterns hinzu
        violation_sets = [set(exp.violations) for exp in experiences]
        common_violations = set.intersection(*violation_sets) if violation_sets else set()
        
        features = list(common)
        if common_violations:
            features.append(f"violations:{','.join(sorted(common_violations))}")
        
        return features
    
    def _calculate_pattern_confidence(self, experiences: List[LearningExperience]) -> float:
        """Berechnet Konfidenz eines Musters."""
        if len(experiences) < 3:
            return 0.3
        
        # Basis-Konfidenz durch Anzahl
        base_confidence = min(0.9, 0.3 + len(experiences) * 0.05)
        
        # Konsistenz der Erfolgsmetriken
        success_scores = [e.success_metrics["overall_success"] for e in experiences]
        if len(success_scores) > 1:
            consistency = 1.0 - statistics.stdev(success_scores)
            base_confidence *= (0.5 + consistency * 0.5)
        
        return base_confidence
    
    def _generate_pattern_recommendations(self, 
                                        pattern: LearningPattern,
                                        experiences: List[LearningExperience]) -> List[Dict[str, Any]]:
        """Generiert Empfehlungen basierend auf Muster."""
        recommendations = []
        
        if pattern.pattern_type == PatternType.SUCCESS_PATTERN:
            # Verstärke erfolgreiche Strategien
            # Analysiere welche Prinzipien in erfolgreichen Fällen hoch waren
            avg_scores = defaultdict(list)
            for exp in experiences:
                for principle, score in exp.ethical_scores.items():
                    avg_scores[principle].append(score)
            
            for principle, scores in avg_scores.items():
                avg = statistics.mean(scores)
                if avg > 0.7:
                    recommendations.append({
                        "action": "reinforce",
                        "target": principle,
                        "strength": 0.02,
                        "reason": f"High {principle} correlates with success pattern"
                    })
        
        elif pattern.pattern_type == PatternType.FAILURE_PATTERN:
            # Korrigiere Fehler
            common_violations = Counter()
            for exp in experiences:
                common_violations.update(exp.violations)
            
            for violation, count in common_violations.most_common(2):
                recommendations.append({
                    "action": "strengthen",
                    "target": violation,
                    "strength": 0.03,
                    "reason": f"{violation} frequently violated in failure pattern"
                })
        
        return recommendations
    
    def _detect_anomalies(self, 
                         experiences: List[LearningExperience],
                         recognized_patterns: List[LearningPattern]) -> List[LearningPattern]:
        """Erkennt Anomalien in Erfahrungen."""
        anomalies = []
        
        # Sammle alle Erfahrungen die zu Patterns gehören
        patterned_exp_ids = set()
        for pattern in recognized_patterns:
            patterned_exp_ids.update(pattern.experience_ids)
        
        # Finde Erfahrungen ohne Pattern
        for exp in experiences:
            if exp.experience_id not in patterned_exp_ids:
                # Prüfe ob es eine echte Anomalie ist
                if self._is_anomaly(exp, experiences):
                    # Erstelle Anomalie-Pattern
                    anomaly_pattern = LearningPattern(
                        pattern_id=f"ANOM-{exp.experience_id}",
                        pattern_type=PatternType.ANOMALY,
                        first_seen=exp.timestamp,
                        last_seen=exp.timestamp,
                        occurrence_count=1,
                        key_features=exp.context_factors,
                        average_success=exp.success_metrics["overall_success"],
                        confidence=0.5,
                        experience_ids=[exp.experience_id],
                        recommended_actions=[{
                            "action": "investigate",
                            "reason": "Unusual pattern detected",
                            "priority": "medium"
                        }]
                    )
                    anomalies.append(anomaly_pattern)
        
        return anomalies
    
    def _is_anomaly(self, experience: LearningExperience, all_experiences: List[LearningExperience]) -> bool:
        """Prüft ob eine Erfahrung eine Anomalie ist."""
        # Sehr hoher oder niedriger Erfolg bei ungewöhnlichen Umständen
        success = experience.success_metrics["overall_success"]
        
        if success > 0.9 or success < 0.1:
            # Prüfe ob Kontext ungewöhnlich ist
            factor_counts = Counter()
            for exp in all_experiences:
                factor_counts.update(exp.context_factors)
            
            # Zähle seltene Faktoren
            rare_factors = sum(1 for f in experience.context_factors 
                             if factor_counts[f] < 3)
            
            return rare_factors >= 2
        
        return False


class ProfileOptimizer:
    """Optimiert ethische Profile basierend auf Lernerfahrungen."""
    
    def __init__(self, base_learner: mini_learner.MiniLearner):
        self.base_learner = base_learner  # Wiederverwendung!
        self.evolution_tracker = ProfileEvolution(
            evolution_id=f"EVO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            start_timestamp=datetime.now(),
            profile_history=[],
            total_changes=defaultdict(float),
            change_velocity=defaultdict(float),
            stability_score=0.8,
            primary_drivers=[]
        )
        self.optimization_history: deque = deque(maxlen=100)
        
    def optimize_profile(self,
                        current_profile: Dict[str, float],
                        experience: LearningExperience,
                        patterns: List[LearningPattern],
                        learning_mode: LearningMode) -> Dict[str, float]:
        """Optimiert Profil basierend auf Erfahrungen und Mustern."""
        # Verwende base_learner für Basis-Updates
        base_updates = self.base_learner.learn(
            current_profile,
            {"feedback": experience.feedback}
        ).get("profile_updates", {})
        
        # Erweitere mit Meta-Learning
        meta_updates = self._calculate_meta_updates(
            current_profile, experience, patterns, learning_mode
        )
        
        # Kombiniere Updates
        combined_updates = self._combine_updates(base_updates, meta_updates, learning_mode)
        
        # Wende Updates an
        updated_profile = self._apply_updates(current_profile, combined_updates)
        
        # Tracke Evolution
        self.evolution_tracker.add_snapshot(updated_profile)
        
        # Speichere Optimierung
        self.optimization_history.append({
            "timestamp": datetime.now(),
            "experience_id": experience.experience_id,
            "updates": combined_updates,
            "mode": learning_mode.value,
            "success": experience.success_metrics["overall_success"]
        })
        
        return updated_profile
    
    def _calculate_meta_updates(self,
                              profile: Dict[str, float],
                              experience: LearningExperience,
                              patterns: List[LearningPattern],
                              mode: LearningMode) -> Dict[str, float]:
        """Berechnet Meta-Learning Updates."""
        updates = defaultdict(float)
        
        # Experience-basierte Updates
        if experience.feedback_type in [FeedbackType.EXPLICIT_NEGATIVE, FeedbackType.IMPLICIT_FAILURE]:
            # Verstärke verletzte Prinzipien
            for violation in experience.violations:
                if violation in principles.ALIGN_KEYS:
                    updates[violation] += 0.02 * self._get_mode_factor(mode)
        
        # Pattern-basierte Updates
        for pattern in patterns:
            if experience.experience_id in pattern.experience_ids:
                for recommendation in pattern.recommended_actions:
                    if recommendation["action"] in ["reinforce", "strengthen"]:
                        target = recommendation["target"]
                        if target in principles.ALIGN_KEYS:
                            updates[target] += recommendation["strength"] * pattern.confidence
        
        # Stabilitäts-Anpassung
        stability_factor = self.evolution_tracker.stability_score
        if stability_factor < 0.6 and mode != LearningMode.EXPLORATORY:
            # Reduziere Updates bei niedriger Stabilität
            for key in updates:
                updates[key] *= stability_factor
        
        return dict(updates)
    
    def _combine_updates(self,
                        base_updates: Dict[str, float],
                        meta_updates: Dict[str, float],
                        mode: LearningMode) -> Dict[str, float]:
        """Kombiniert Basis- und Meta-Updates."""
        combined = defaultdict(float)
        
        # Mode-spezifische Gewichtung
        if mode == LearningMode.CONSERVATIVE:
            base_weight, meta_weight = 0.7, 0.3
        elif mode == LearningMode.BALANCED:
            base_weight, meta_weight = 0.5, 0.5
        elif mode == LearningMode.AGGRESSIVE:
            base_weight, meta_weight = 0.3, 0.7
        else:  # EXPLORATORY
            base_weight, meta_weight = 0.2, 0.8
        
        # Kombiniere
        for principle in principles.ALIGN_KEYS:
            base_val = base_updates.get(principle, 0.0)
            meta_val = meta_updates.get(principle, 0.0)
            combined[principle] = base_val * base_weight + meta_val * meta_weight
        
        # Constraints
        max_change = 0.05 * self._get_mode_factor(mode)
        for principle in combined:
            combined[principle] = max(-max_change, min(max_change, combined[principle]))
        
        return dict(combined)
    
    def _apply_updates(self,
                      profile: Dict[str, float],
                      updates: Dict[str, float]) -> Dict[str, float]:
        """Wendet Updates auf Profil an."""
        updated = profile.copy()
        
        for principle, change in updates.items():
            if principle in updated:
                new_value = updated[principle] + change
                # Constraints: 0.1 bis 2.0
                updated[principle] = max(0.1, min(2.0, new_value))
        
        # Tracking
        for principle, change in updates.items():
            self.evolution_tracker.total_changes[principle] += change
        
        return updated
    
    def _get_mode_factor(self, mode: LearningMode) -> float:
        """Gibt Anpassungsfaktor für Lernmodus zurück."""
        factors = {
            LearningMode.CONSERVATIVE: 0.5,
            LearningMode.BALANCED: 1.0,
            LearningMode.AGGRESSIVE: 1.5,
            LearningMode.EXPLORATORY: 2.0
        }
        return factors.get(mode, 1.0)
    
    def get_stability_assessment(self) -> Dict[str, Any]:
        """Bewertet Profil-Stabilität."""
        evolution = self.evolution_tracker
        
        # Berechne Stabilitäts-Score
        if len(evolution.profile_history) < 5:
            stability_score = 0.8  # Default für wenig Daten
        else:
            # Varianz der letzten Änderungen
            recent_changes = []
            for i in range(1, min(6, len(evolution.profile_history))):
                prev_profile = evolution.profile_history[-i-1][1]
                curr_profile = evolution.profile_history[-i][1]
                
                change = sum(abs(curr_profile.get(p, 1.0) - prev_profile.get(p, 1.0)) 
                           for p in principles.ALIGN_KEYS)
                recent_changes.append(change)
            
            avg_change = statistics.mean(recent_changes)
            stability_score = max(0.0, 1.0 - avg_change * 10)
        
        evolution.stability_score = stability_score
        
        # Identifiziere Haupttreiber
        top_changes = sorted(evolution.total_changes.items(), 
                           key=lambda x: abs(x[1]), reverse=True)[:3]
        evolution.primary_drivers = [p[0] for p in top_changes if abs(p[1]) > 0.01]
        
        return {
            "stability_score": stability_score,
            "total_changes": dict(evolution.total_changes),
            "change_velocity": dict(evolution.change_velocity),
            "primary_drivers": evolution.primary_drivers,
            "profile_age": (datetime.now() - evolution.start_timestamp).total_seconds() / 3600  # Stunden
        }


class InsightGenerator:
    """Generiert Meta-Insights über das Lernsystem."""
    
    def __init__(self):
        self.insights: deque = deque(maxlen=100)
        self.insight_effectiveness: Dict[str, float] = {}
        
    def generate_insights(self,
                         experiences: List[LearningExperience],
                         patterns: List[LearningPattern],
                         profile_stability: Dict[str, Any],
                         system_metrics: Dict[str, Any]) -> List[MetaInsight]:
        """Generiert neue Meta-Insights."""
        new_insights = []
        
        # Pattern-basierte Insights
        pattern_insights = self._analyze_pattern_trends(patterns)
        new_insights.extend(pattern_insights)
        
        # Stabilitäts-Insights
        stability_insights = self._analyze_stability(profile_stability)
        new_insights.extend(stability_insights)
        
        # Performance-Insights
        performance_insights = self._analyze_performance(experiences, system_metrics)
        new_insights.extend(performance_insights)
        
        # Learning-Effectiveness
        effectiveness_insights = self._analyze_learning_effectiveness(experiences)
        new_insights.extend(effectiveness_insights)
        
        # Speichere neue Insights
        for insight in new_insights:
            self.insights.append(insight)
        
        return new_insights
    
    def _analyze_pattern_trends(self, patterns: List[LearningPattern]) -> List[MetaInsight]:
        """Analysiert Trends in Mustern."""
        insights = []
        
        # Zähle Pattern-Typen
        pattern_counts = Counter(p.pattern_type for p in patterns)
        
        # Zu viele Failure Patterns
        failure_ratio = pattern_counts[PatternType.FAILURE_PATTERN] / max(1, len(patterns))
        if failure_ratio > 0.4:
            insights.append(MetaInsight(
                insight_id=f"INS-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                priority=InsightPriority.HIGH,
                insight_type="high_failure_rate",
                description=f"{failure_ratio:.0%} der Muster sind Fehlermuster",
                evidence=[p.pattern_id for p in patterns if p.pattern_type == PatternType.FAILURE_PATTERN][:5],
                recommendations=[
                    "Überprüfe Entscheidungslogik auf systematische Fehler",
                    "Erhöhe Lernrate für Fehlerkorrektur",
                    "Analysiere gemeinsame Faktoren in Fehlermustern"
                ]
            ))
        
        # Emerging Patterns
        emerging = [p for p in patterns if p.pattern_type == PatternType.EMERGING_PATTERN]
        if len(emerging) > 3:
            insights.append(MetaInsight(
                insight_id=f"INS-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                priority=InsightPriority.MEDIUM,
                insight_type="emerging_patterns",
                description=f"{len(emerging)} neue Muster entstehen",
                evidence=[p.pattern_id for p in emerging],
                recommendations=[
                    "Beobachte neue Muster genau",
                    "Passe Lernstrategie an neue Situationen an"
                ]
            ))
        
        return insights
    
    def _analyze_stability(self, stability_data: Dict[str, Any]) -> List[MetaInsight]:
        """Analysiert Profil-Stabilität."""
        insights = []
        
        stability_score = stability_data["stability_score"]
        
        if stability_score < 0.5:
            insights.append(MetaInsight(
                insight_id=f"INS-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                priority=InsightPriority.CRITICAL,
                insight_type="low_stability",
                description=f"Kritisch niedrige Profilstabilität: {stability_score:.2f}",
                evidence=stability_data["primary_drivers"],
                recommendations=[
                    "Wechsle zu konservativem Lernmodus",
                    "Reduziere Änderungsrate",
                    "Fokussiere auf Stabilisierung statt Exploration"
                ]
            ))
        
        # Schnelle Änderungen
        high_velocity = [(p, v) for p, v in stability_data["change_velocity"].items() if abs(v) > 0.1]
        if high_velocity:
            insights.append(MetaInsight(
                insight_id=f"INS-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                priority=InsightPriority.HIGH,
                insight_type="rapid_changes",
                description="Sehr schnelle Profiländerungen erkannt",
                evidence=[f"{p}: {v:.3f}/h" for p, v in high_velocity],
                recommendations=[
                    "Überprüfe ob Änderungen gerechtfertigt sind",
                    "Erwäge Dämpfung der Anpassungsgeschwindigkeit"
                ]
            ))
        
        return insights
    
    def _analyze_performance(self, 
                           experiences: List[LearningExperience],
                           system_metrics: Dict[str, Any]) -> List[MetaInsight]:
        """Analysiert System-Performance."""
        insights = []
        
        if not experiences:
            return insights
        
        # Trend-Analyse
        recent = experiences[-20:] if len(experiences) > 20 else experiences
        recent_success = [e.success_metrics["overall_success"] for e in recent]
        
        if len(recent_success) > 10:
            # Berechne Trend
            first_half = statistics.mean(recent_success[:len(recent_success)//2])
            second_half = statistics.mean(recent_success[len(recent_success)//2:])
            
            trend = second_half - first_half
            
            if trend < -0.15:
                insights.append(MetaInsight(
                    insight_id=f"INS-{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    priority=InsightPriority.HIGH,
                    insight_type="declining_performance",
                    description=f"Performance sinkt: {trend:.2f} Rückgang",
                    evidence=[e.experience_id for e in recent[-5:]],
                    recommendations=[
                        "Analysiere kürzliche Änderungen",
                        "Überprüfe ob Overlearning stattfindet",
                        "Erwäge Rollback zu stabilerem Zustand"
                    ]
                ))
            elif trend > 0.15:
                insights.append(MetaInsight(
                    insight_id=f"INS-{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    priority=InsightPriority.LOW,
                    insight_type="improving_performance",
                    description=f"Performance verbessert sich: +{trend:.2f}",
                    evidence=[e.experience_id for e in recent[-5:]],
                    recommendations=[
                        "Aktuelle Strategie beibehalten",
                        "Erfolgreiche Muster verstärken"
                    ]
                ))
        
        return insights
    
    def _analyze_learning_effectiveness(self, experiences: List[LearningExperience]) -> List[MetaInsight]:
        """Analysiert Effektivität des Lernens."""
        insights = []
        
        if len(experiences) < 50:
            return insights
        
        # Vergleiche Feedback mit tatsächlichen Ergebnissen
        explicit_feedback = [e for e in experiences 
                           if e.feedback_type in [FeedbackType.EXPLICIT_POSITIVE, FeedbackType.EXPLICIT_NEGATIVE]]
        
        if len(explicit_feedback) > 10:
            # Prüfe Korrelation zwischen Feedback und System-Erfolg
            correlations = []
            for exp in explicit_feedback:
                feedback_val = exp.feedback.get("value", 0.5)
                system_success = exp.success_metrics["overall_success"]
                correlations.append((feedback_val, system_success))
            
            # Einfache Korrelationsanalyse
            if correlations:
                feedback_vals, success_vals = zip(*correlations)
                avg_diff = statistics.mean([abs(f - s) for f, s in correlations])
                
                if avg_diff > 0.3:
                    insights.append(MetaInsight(
                        insight_id=f"INS-{uuid.uuid4().hex[:8]}",
                        timestamp=datetime.now(),
                        priority=InsightPriority.MEDIUM,
                        insight_type="feedback_mismatch",
                        description="Diskrepanz zwischen Feedback und System-Bewertung",
                        evidence=[e.experience_id for e in explicit_feedback[-5:]],
                        recommendations=[
                            "Kalibriere Erfolgsbewertung neu",
                            "Untersuche Ursachen für Diskrepanz",
                            "Verbessere Feedback-Integration"
                        ]
                    ))
        
        return insights


# ============================================================================
# HAUPTKLASSE
# ============================================================================

class MetaLearner:
    """
    Haupt-Koordinator für Meta-Learning.
    Erweitert mini_learner um vollwertiges adaptives Lernen.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        
        # Basis-Komponenten
        self.mini_learner = mini_learner.MiniLearner()  # WICHTIG: Wiederverwendung!
        
        # Meta-Learning Komponenten
        self.experience_collector = ExperienceCollector(
            memory_size=self.config.get("memory_size", 5000)
        )
        self.pattern_recognizer = PatternRecognizer()
        self.profile_optimizer = ProfileOptimizer(self.mini_learner)
        self.insight_generator = InsightGenerator()
        
        # Learning Mode
        self.learning_mode = LearningMode(self.config.get("learning_mode", "balanced"))
        
        # Statistiken
        self.stats = {
            "total_experiences": 0,
            "patterns_recognized": 0,
            "insights_generated": 0,
            "profile_updates": 0,
            "learning_cycles": 0,
            "current_performance": 0.5
        }
        
        # State
        self.last_learning_cycle = datetime.now()
        self.learning_cycle_interval = timedelta(seconds=self.config.get("cycle_interval", 300))
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Lädt Standard-Konfiguration."""
        config_path = Path(__file__).parent / "config" / "meta_learner_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Fallback
        return {
            "memory_size": 5000,
            "learning_mode": "balanced",
            "cycle_interval": 300,
            "min_experiences_for_pattern": 3,
            "insight_threshold": 0.7
        }
    
    def learn_from_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hauptmethode: Lernt aus einer Entscheidung.
        
        Args:
            context: Vollständiger Entscheidungskontext
            
        Returns:
            Meta-Learning Ergebnis
        """
        # Sammle Erfahrung
        experience = self.experience_collector.collect_from_context(context)
        if not experience:
            return self._create_error_result("Failed to collect experience")
        
        self.stats["total_experiences"] += 1
        
        # Aktuelles Profil
        current_profile = context.get("profile", profiles.get_default_profile())
        
        # Basis-Learning (mini_learner)
        base_result = self.mini_learner.learn(
            current_profile,
            {"feedback": experience.feedback}
        )
        
        # Pattern Recognition
        recent_experiences = self.experience_collector.get_recent_experiences(100)
        patterns = self.pattern_recognizer.analyze_experiences(recent_experiences)
        self.stats["patterns_recognized"] = len(patterns)
        
        # Profile Optimization
        optimized_profile = self.profile_optimizer.optimize_profile(
            current_profile,
            experience,
            patterns,
            self.learning_mode
        )
        
        # Profile Updates berechnen
        profile_updates = {
            p: optimized_profile[p] - current_profile.get(p, 1.0)
            for p in optimized_profile
            if abs(optimized_profile[p] - current_profile.get(p, 1.0)) > 0.001
        }
        
        if profile_updates:
            self.stats["profile_updates"] += 1
        
        # Stability Assessment
        stability = self.profile_optimizer.get_stability_assessment()
        
        # System Metrics
        system_metrics = self._calculate_system_metrics(recent_experiences)
        
        # Generate Insights
        insights = self.insight_generator.generate_insights(
            recent_experiences,
            patterns,
            stability,
            system_metrics
        )
        self.stats["insights_generated"] += len(insights)
        
        # Learning Cycle Check
        should_cycle = self._should_trigger_learning_cycle()
        learning_cycle_result = None
        
        if should_cycle:
            learning_cycle_result = self._execute_learning_cycle(
                recent_experiences, patterns, insights
            )
        
        # Zusammenstellen
        return {
            "experience_id": experience.experience_id,
            "base_learning": base_result,
            "profile_updates": profile_updates,
            "updated_profile": optimized_profile,
            "patterns": {
                "total": len(patterns),
                "by_type": Counter(p.pattern_type.value for p in patterns),
                "recent": [self._pattern_summary(p) for p in patterns[:5]]
            },
            "stability": stability,
            "insights": [self._insight_summary(i) for i in insights],
            "learning_cycle": learning_cycle_result,
            "performance": system_metrics,
            "stats": self.stats.copy(),
            "config": {
                "mode": self.learning_mode.value,
                "memory_size": self.experience_collector.memory_size
            }
        }
    
    def _calculate_system_metrics(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Berechnet System-Metriken."""
        if not experiences:
            return {"status": "no_data", "current_performance": 0.5}
        
        recent = experiences[-20:] if len(experiences) > 20 else experiences
        
        # Performance Metriken
        success_scores = [e.success_metrics["overall_success"] for e in recent]
        ethical_scores = [e.overall_ethics_score for e in recent]
        confidence_scores = [e.confidence for e in recent]
        
        current_performance = statistics.mean(success_scores)
        self.stats["current_performance"] = current_performance
        
        return {
            "status": self._get_performance_status(current_performance),
            "current_performance": current_performance,
            "metrics": {
                "success_rate": statistics.mean(success_scores),
                "ethical_quality": statistics.mean(ethical_scores),
                "decision_confidence": statistics.mean(confidence_scores),
                "violation_rate": sum(1 for e in recent if e.violations) / len(recent)
            },
            "trend": self._calculate_trend(experiences)
        }
    
    def _get_performance_status(self, performance: float) -> str:
        """Bestimmt Performance-Status."""
        if performance >= 0.8:
            return "excellent"
        elif performance >= 0.65:
            return "good"
        elif performance >= 0.5:
            return "acceptable"
        else:
            return "needs_improvement"
    
    def _calculate_trend(self, experiences: List[LearningExperience]) -> str:
        """Berechnet Performance-Trend."""
        if len(experiences) < 10:
            return "insufficient_data"
        
        recent = experiences[-20:] if len(experiences) > 20 else experiences
        mid_point = len(recent) // 2
        
        first_half = [e.success_metrics["overall_success"] for e in recent[:mid_point]]
        second_half = [e.success_metrics["overall_success"] for e in recent[mid_point:]]
        
        if not first_half or not second_half:
            return "insufficient_data"
        
        trend = statistics.mean(second_half) - statistics.mean(first_half)
        
        if trend > 0.05:
            return "improving"
        elif trend < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _should_trigger_learning_cycle(self) -> bool:
        """Entscheidet ob ein Lernzyklus ausgelöst werden soll."""
        # Zeit-basiert
        time_since_last = datetime.now() - self.last_learning_cycle
        if time_since_last < self.learning_cycle_interval:
            return False
        
        # Erfahrungs-basiert
        if self.stats["total_experiences"] < 20:
            return False
        
        # Performance-basiert
        if self.stats["current_performance"] < 0.5:
            return True  # Dringend bei schlechter Performance
        
        # Insight-basiert
        critical_insights = [i for i in self.insight_generator.insights 
                           if i.priority == InsightPriority.CRITICAL and not i.addressed]
        if critical_insights:
            return True
        
        return time_since_last >= self.learning_cycle_interval
    
    def _execute_learning_cycle(self,
                               experiences: List[LearningExperience],
                               patterns: List[LearningPattern],
                               insights: List[MetaInsight]) -> Dict[str, Any]:
        """Führt einen vollständigen Lernzyklus durch."""
        self.last_learning_cycle = datetime.now()
        self.stats["learning_cycles"] += 1
        
        cycle_result = {
            "cycle_number": self.stats["learning_cycles"],
            "timestamp": datetime.now().isoformat(),
            "actions_taken": []
        }
        
        # Modus-Anpassung
        mode_adjustment = self._adjust_learning_mode(insights, self.stats["current_performance"])
        if mode_adjustment:
            cycle_result["actions_taken"].append(mode_adjustment)
        
        # Pattern Consolidation
        pattern_actions = self._consolidate_patterns(patterns)
        cycle_result["actions_taken"].extend(pattern_actions)
        
        # Insight Actions
        insight_actions = self._process_insights(insights)
        cycle_result["actions_taken"].extend(insight_actions)
        
        # Cleanup
        if self.experience_collector.memory_size > 4000:
            # Entferne alte irrelevante Erfahrungen
            cycle_result["actions_taken"].append({
                "action": "memory_cleanup",
                "removed": self._cleanup_memory()
            })
        
        return cycle_result
    
    def _adjust_learning_mode(self, insights: List[MetaInsight], performance: float) -> Optional[Dict[str, Any]]:
        """Passt Lernmodus basierend auf Insights und Performance an."""
        # Kritische Insights → Konservativ
        critical = [i for i in insights if i.priority == InsightPriority.CRITICAL]
        if critical:
            if self.learning_mode != LearningMode.CONSERVATIVE:
                self.learning_mode = LearningMode.CONSERVATIVE
                return {
                    "action": "mode_change",
                    "new_mode": "conservative",
                    "reason": "Critical insights detected"
                }
        
        # Schlechte Performance → Aggressiv
        elif performance < 0.4:
            if self.learning_mode != LearningMode.AGGRESSIVE:
                self.learning_mode = LearningMode.AGGRESSIVE
                return {
                    "action": "mode_change",
                    "new_mode": "aggressive",
                    "reason": "Poor performance"
                }
        
        # Gute Performance + Stabilität → Explorativ
        elif performance > 0.75 and self.profile_optimizer.evolution_tracker.stability_score > 0.7:
            if self.learning_mode != LearningMode.EXPLORATORY:
                self.learning_mode = LearningMode.EXPLORATORY
                return {
                    "action": "mode_change",
                    "new_mode": "exploratory",
                    "reason": "Good performance and stability"
                }
        
        # Standard → Balanced
        elif self.learning_mode != LearningMode.BALANCED:
            self.learning_mode = LearningMode.BALANCED
            return {
                "action": "mode_change",
                "new_mode": "balanced",
                "reason": "Return to balanced mode"
            }
        
        return None
    
    def _consolidate_patterns(self, patterns: List[LearningPattern]) -> List[Dict[str, Any]]:
        """Konsolidiert und optimiert erkannte Muster."""
        actions = []
        
        # Entferne schwache Patterns
        weak_patterns = [p for p in patterns 
                        if p.confidence < 0.3 and p.occurrence_count < 5]
        
        if weak_patterns:
            actions.append({
                "action": "remove_weak_patterns",
                "count": len(weak_patterns),
                "pattern_ids": [p.pattern_id for p in weak_patterns[:5]]
            })
        
        # Verstärke starke Success Patterns
        strong_success = [p for p in patterns 
                         if p.pattern_type == PatternType.SUCCESS_PATTERN 
                         and p.confidence > 0.8]
        
        if strong_success:
            actions.append({
                "action": "reinforce_success_patterns",
                "count": len(strong_success),
                "average_success": statistics.mean([p.average_success for p in strong_success])
            })
        
        return actions
    
    def _process_insights(self, insights: List[MetaInsight]) -> List[Dict[str, Any]]:
        """Verarbeitet Insights und leitet Aktionen ab."""
        actions = []
        
        for insight in insights:
            if insight.addressed:
                continue
            
            if insight.priority in [InsightPriority.CRITICAL, InsightPriority.HIGH]:
                # Markiere als adressiert
                insight.addressed = True
                
                # Generiere Aktion
                action = {
                    "action": "address_insight",
                    "insight_id": insight.insight_id,
                    "type": insight.insight_type,
                    "priority": insight.priority.value,
                    "applied_recommendations": insight.recommendations[:2]
                }
                
                actions.append(action)
                
                # Nur Top 3 pro Zyklus
                if len(actions) >= 3:
                    break
        
        return actions
    
    def _cleanup_memory(self) -> int:
        """Bereinigt Speicher von irrelevanten Erfahrungen."""
        # Sehr einfache Heuristik: Entferne älteste 10%
        to_remove = len(self.experience_collector.experiences) // 10
        
        for _ in range(to_remove):
            if self.experience_collector.experiences:
                self.experience_collector.experiences.popleft()
        
        return to_remove
    
    def _pattern_summary(self, pattern: LearningPattern) -> Dict[str, Any]:
        """Erstellt Zusammenfassung eines Patterns."""
        return {
            "id": pattern.pattern_id,
            "type": pattern.pattern_type.value,
            "occurrences": pattern.occurrence_count,
            "confidence": pattern.confidence,
            "success_rate": pattern.average_success,
            "features": pattern.key_features[:3]
        }
    
    def _insight_summary(self, insight: MetaInsight) -> Dict[str, Any]:
        """Erstellt Zusammenfassung eines Insights."""
        return {
            "id": insight.insight_id,
            "priority": insight.priority.value,
            "type": insight.insight_type,
            "description": insight.description,
            "recommendations": insight.recommendations[:2]
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Erstellt Fehler-Ergebnis."""
        return {
            "error": True,
            "error_message": error_message,
            "profile_updates": {},
            "stats": self.stats.copy()
        }
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Gibt Zusammenfassung des Lernfortschritts."""
        recent_experiences = self.experience_collector.get_recent_experiences(50)
        
        return {
            "stats": self.stats.copy(),
            "mode": self.learning_mode.value,
            "performance": {
                "current": self.stats["current_performance"],
                "trend": self._calculate_trend(recent_experiences) if recent_experiences else "no_data"
            },
            "stability": self.profile_optimizer.get_stability_assessment(),
            "patterns": {
                "total": self.stats["patterns_recognized"],
                "types": Counter(p.pattern_type.value for p in self.pattern_recognizer.patterns.values())
            },
            "insights": {
                "total": self.stats["insights_generated"],
                "unaddressed": sum(1 for i in self.insight_generator.insights if not i.addressed),
                "by_priority": Counter(i.priority.value for i in self.insight_generator.insights)
            },
            "memory": {
                "experiences": len(self.experience_collector.experiences),
                "capacity": self.experience_collector.memory_size,
                "utilization": len(self.experience_collector.experiences) / self.experience_collector.memory_size
            }
        }


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale MetaLearner-Instanz
_meta_learner_instance: Optional[MetaLearner] = None

def _get_meta_learner_instance(config: Optional[Dict[str, Any]] = None) -> MetaLearner:
   """Lazy-Loading der MetaLearner-Instanz."""
   global _meta_learner_instance
   if _meta_learner_instance is None or config is not None:
       _meta_learner_instance = MetaLearner(config)
   return _meta_learner_instance


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
   """
   Standardisierte Modul-Schnittstelle für INTEGRA.
   
   Args:
       input_text: Text-Eingabe (für Kontext-Analyse)
       context: Entscheidungskontext mit allen Modul-Ergebnissen
       
   Returns:
       Standardisiertes Ergebnis-Dictionary
   """
   if context is None:
       context = {}
   
   try:
       # MetaLearner-Konfiguration aus Context
       ml_config = context.get("config", {}).get("meta_learner", {})
       
       # MetaLearner-Instanz
       meta_learner = _get_meta_learner_instance(ml_config)
       
       # Füge input_text zum Context hinzu falls nicht vorhanden
       if "input_text" not in context and input_text:
           context["input_text"] = input_text
       
       # Führe Meta-Learning durch
       learning_result = meta_learner.learn_from_decision(context)
       
       # Speichere im Context für andere Module
       context["meta_learner_result"] = learning_result
       
       # Update Profil im Context wenn Änderungen vorhanden
       if learning_result.get("profile_updates"):
           context["profile"] = learning_result["updated_profile"]
           context["profile_updated"] = True
       
       # Log wichtige Events
       if log_manager:
           if learning_result.get("profile_updates"):
               log_manager.log_event(
                   "MetaLearner",
                   f"Profile updated: {len(learning_result['profile_updates'])} changes",
                   "INFO"
               )
           
           insights = learning_result.get("insights", [])
           critical_insights = [i for i in insights if i.get("priority") == "critical"]
           if critical_insights:
               log_manager.log_event(
                   "MetaLearner",
                   f"Critical insights: {len(critical_insights)}",
                   "WARNING"
               )
       
       return {
           "success": True,
           "result": learning_result,
           "module": "meta_learner",
           "version": "2.0",
           "timestamp": datetime.now().isoformat(),
           "context": context
       }
       
   except Exception as e:
       error_msg = f"MetaLearner error: {str(e)}"
       
       if log_manager:
           log_manager.log_event("MetaLearner", error_msg, "ERROR")
       
       return {
           "success": False,
           "error": error_msg,
           "module": "meta_learner",
           "version": "2.0",
           "timestamp": datetime.now().isoformat(),
           "context": context
       }


def demo():
   """Demonstriert die MetaLearner-Funktionalität."""
   print("=== INTEGRA MetaLearner v2.0 Demo ===")
   print("Erweitert mini_learner um vollwertiges Meta-Learning\n")
   
   # Test-Profil
   test_profile = profiles.get_default_profile()
   
   # Simuliere verschiedene Entscheidungsszenarien
   test_scenarios = [
       {
           "name": "Erfolgreiche ethische Entscheidung",
           "context": {
               "decision_id": "ML-DEMO-001",
               "input_text": "Wie kann ich jemandem helfen, der Schwierigkeiten hat?",
               "path": "deep",
               "confidence": 0.85,
               "profile": test_profile.copy(),
               "ethics": {
                   "scores": {
                       "nurturing": 0.9,
                       "integrity": 0.85,
                       "awareness": 0.8,
                       "learning": 0.75,
                       "governance": 0.8
                   },
                   "violations": [],
                   "overall_score": 0.85
               },
               "etb_result": {
                   "success": True,
                   "conflicts_detected": [],
                   "processing_time": 0.02
               },
               "user_feedback": {
                   "value": 0.9,
                   "comment": "Sehr hilfreiche und einfühlsame Antwort"
               }
           }
       },
       {
           "name": "Problematische Entscheidung mit Verletzungen",
           "context": {
               "decision_id": "ML-DEMO-002",
               "input_text": "Soll ich die Wahrheit verschweigen?",
               "path": "deep",
               "confidence": 0.6,
               "profile": test_profile.copy(),
               "ethics": {
                   "scores": {
                       "integrity": 0.3,
                       "nurturing": 0.7,
                       "awareness": 0.5,
                       "learning": 0.6,
                       "governance": 0.5
                   },
                   "violations": ["integrity"],
                   "overall_score": 0.5
               },
               "etb_result": {
                   "success": True,
                   "conflicts_detected": [
                       {"principles": ["integrity", "nurturing"], "severity": 0.6}
                   ],
                   "processing_time": 0.05
               },
               "pae_result": {
                   "success": True,
                   "principle_chosen": "nurturing",
                   "resolution_basis": "context"
               },
               "user_feedback": {
                   "value": 0.3,
                   "comment": "Das wirkt unehrlich"
               }
           }
       },
       {
           "name": "Drift-Erkennung",
           "context": {
               "decision_id": "ML-DEMO-003",
               "input_text": "Normale Anfrage",
               "path": "fast",
               "confidence": 0.75,
               "profile": test_profile.copy(),
               "ethics": {
                   "scores": {p: 0.7 for p in principles.ALIGN_KEYS},
                   "violations": [],
                   "overall_score": 0.7
               },
               "vdd_result": {
                   "success": True,
                   "drift_detected": True,
                   "drift_severity": 0.3,
                   "processing_time": 0.03
               },
               "mini_learner_result": {
                   "success": True,
                   "profile_updates": {"awareness": 0.01}
               }
           }
       }
   ]
   
   # Füge weitere Szenarien für Musterbildung hinzu
   for i in range(4, 15):
       # Erstelle abwechselnd erfolgreiche und problematische Szenarien
       if i % 3 == 0:
           # Erfolgreich
           scenario = {
               "name": f"Erfolg-Szenario {i}",
               "context": {
                   "decision_id": f"ML-DEMO-{i:03d}",
                   "input_text": f"Test-Anfrage {i}",
                   "path": "deep",
                   "confidence": 0.8 + (i % 5) * 0.02,
                   "profile": test_profile.copy(),
                   "ethics": {
                       "scores": {p: 0.75 + (i % 4) * 0.05 for p in principles.ALIGN_KEYS},
                       "violations": [],
                       "overall_score": 0.8
                   },
                   "user_feedback": {
                       "value": 0.8 + (i % 3) * 0.05
                   }
               }
           }
       else:
           # Problematisch
           violation = principles.ALIGN_KEYS[i % len(principles.ALIGN_KEYS)]
           scenario = {
               "name": f"Problem-Szenario {i}",
               "context": {
                   "decision_id": f"ML-DEMO-{i:03d}",
                   "input_text": f"Problematische Anfrage {i}",
                   "path": "deep",
                   "confidence": 0.5 + (i % 4) * 0.05,
                   "profile": test_profile.copy(),
                   "ethics": {
                       "scores": {
                           p: 0.4 if p == violation else 0.7 
                           for p in principles.ALIGN_KEYS
                       },
                       "violations": [violation],
                       "overall_score": 0.5
                   }
               }
           }
       
       test_scenarios.append(scenario)
   
   print(f"📊 Führe {len(test_scenarios)} Test-Szenarien durch...\n")
   
   # Verarbeite alle Szenarien
   results = []
   current_profile = test_profile.copy()
   
   for i, scenario in enumerate(test_scenarios):
       # Update Profil im Context
       scenario["context"]["profile"] = current_profile
       
       # Führe MetaLearning durch
       result = run_module(scenario["context"].get("input_text", ""), scenario["context"])
       
       if result["success"]:
           ml_result = result["result"]
           results.append(ml_result)
           
           # Update Profil für nächste Iteration
           if ml_result.get("updated_profile"):
               current_profile = ml_result["updated_profile"]
           
           # Zeige wichtige Ereignisse
           if i < 3 or ml_result.get("profile_updates"):  # Erste 3 oder wenn Updates
               print(f"\n📍 {scenario['name']}:")
               print(f"   Experience ID: {ml_result.get('experience_id', 'N/A')}")
               
               if ml_result.get("profile_updates"):
                   print(f"   Profile Updates:")
                   for principle, change in ml_result["profile_updates"].items():
                       print(f"     {principle}: {change:+.3f}")
               
               patterns = ml_result.get("patterns", {})
               if patterns.get("total", 0) > 0:
                   print(f"   Patterns: {patterns['total']} erkannt")
                   for ptype, count in patterns.get("by_type", {}).items():
                       if count > 0:
                           print(f"     - {ptype}: {count}")
               
               insights = ml_result.get("insights", [])
               if insights:
                   print(f"   Insights: {len(insights)}")
                   for insight in insights[:2]:
                       print(f"     [{insight['priority']}] {insight['description']}")
   
   # Finale Zusammenfassung
   if results:
       final_result = results[-1]
       
       print("\n" + "="*60)
       print("📈 FINALE META-LEARNER ZUSAMMENFASSUNG")
       print("="*60)
       
       print(f"\n🧠 Lernfortschritt:")
       stats = final_result.get("stats", {})
       print(f"  Erfahrungen gesammelt: {stats.get('total_experiences', 0)}")
       print(f"  Muster erkannt: {stats.get('patterns_recognized', 0)}")
       print(f"  Insights generiert: {stats.get('insights_generated', 0)}")
       print(f"  Profil-Updates: {stats.get('profile_updates', 0)}")
       print(f"  Lernzyklen: {stats.get('learning_cycles', 0)}")
       
       print(f"\n📊 Performance:")
       perf = final_result.get("performance", {})
       print(f"  Status: {perf.get('status', 'N/A')}")
       print(f"  Aktuelle Performance: {perf.get('current_performance', 0):.2%}")
       if "metrics" in perf:
           metrics = perf["metrics"]
           print(f"  Erfolgsrate: {metrics.get('success_rate', 0):.2%}")
           print(f"  Ethische Qualität: {metrics.get('ethical_quality', 0):.2%}")
           print(f"  Verletzungsrate: {metrics.get('violation_rate', 0):.2%}")
       print(f"  Trend: {perf.get('trend', 'N/A')}")
       
       print(f"\n⚖️ Profil-Evolution:")
       stability = final_result.get("stability", {})
       print(f"  Stabilitäts-Score: {stability.get('stability_score', 0):.2f}")
       if "total_changes" in stability:
           print(f"  Größte Änderungen:")
           changes = sorted(stability["total_changes"].items(), 
                          key=lambda x: abs(x[1]), reverse=True)[:3]
           for principle, change in changes:
               if abs(change) > 0.01:
                   print(f"    {principle}: {change:+.3f}")
       
       print(f"\n🎯 Finale Profil-Werte:")
       for principle in principles.ALIGN_KEYS:
           original = test_profile[principle]
           current = current_profile[principle]
           change = current - original
           print(f"  {principle}: {current:.3f} ({change:+.3f})")
       
       print(f"\n💡 Muster-Analyse:")
       patterns = final_result.get("patterns", {})
       if "by_type" in patterns:
           for ptype, count in patterns["by_type"].items():
               if count > 0:
                   print(f"  {ptype}: {count}")
       
       if "recent" in patterns and patterns["recent"]:
           print(f"\n  Aktuelle Muster:")
           for pattern in patterns["recent"][:3]:
               print(f"    - {pattern['type']} (Konfidenz: {pattern['confidence']:.2f})")
               print(f"      Erfolgsrate: {pattern.get('success_rate', 0):.2%}")
       
       # Learning Summary
       print(f"\n📋 Learning Summary:")
       ml_instance = _get_meta_learner_instance()
       summary = ml_instance.get_learning_summary()
       
       print(f"  Modus: {summary['mode']}")
       print(f"  Speicher-Auslastung: {summary['memory']['utilization']:.1%}")
       
       if "insights" in summary:
           unaddressed = summary["insights"].get("unaddressed", 0)
           if unaddressed > 0:
               print(f"  ⚠️ Unbehandelte Insights: {unaddressed}")
   
   print("\n✅ MetaLearner Demo abgeschlossen!")
   print("Das Modul erweitert mini_learner um umfassendes adaptives Lernen.")


if __name__ == "__main__":
   demo()