# -*- coding: utf-8 -*-
"""
Modulname: mini_learner.py
Beschreibung: Adaptives Lernmodul für INTEGRA Advanced - Feedback-basierte Profilanpassung
Teil von: INTEGRA Light – Advanced Layer
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Überarbeitet gemäß INTEGRA 4.2 Standards
"""

from typing import Dict, Any, List, Optional, Tuple, Protocol
from datetime import datetime
from abc import ABC, abstractmethod
import json
import os
from pathlib import Path
import math

# Import-Kompatibilität
try:
    from integra.core import principles, profiles
    from integra.advanced import mini_audit
    from integra.logging import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from advanced import mini_audit
        from logging import log_manager
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
        except ImportError:
            # Fallback
            class DummyPrinciples:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            principles = DummyPrinciples()
            
            class DummyProfiles:
                def get_default_profile(self):
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            profiles = DummyProfiles()
        
        # Dummy Module wenn nicht verfügbar
        mini_audit = None
        class DummyLogManager:
            def log_event(self, *args, **kwargs): pass
        log_manager = DummyLogManager()


class StorageInterface(ABC):
    """Abstrakte Basis für Lernspeicher-Implementierungen."""
    
    @abstractmethod
    def save_learning_state(self, state: Dict[str, Any]) -> bool:
        """Speichert Lernzustand."""
        pass
    
    @abstractmethod
    def load_learning_state(self) -> Optional[Dict[str, Any]]:
        """Lädt Lernzustand."""
        pass
    
    @abstractmethod
    def append_learning_event(self, event: Dict[str, Any]) -> bool:
        """Fügt Lernereignis hinzu."""
        pass


class MemoryStorage(StorageInterface):
    """In-Memory Speicher für Lerndaten."""
    
    def __init__(self):
        self.state = {}
        self.events = []
    
    def save_learning_state(self, state: Dict[str, Any]) -> bool:
        self.state = state.copy()
        return True
    
    def load_learning_state(self) -> Optional[Dict[str, Any]]:
        return self.state.copy() if self.state else None
    
    def append_learning_event(self, event: Dict[str, Any]) -> bool:
        self.events.append(event)
        return True


class FileStorage(StorageInterface):
    """Dateibasierter Speicher für Lerndaten."""
    
    def __init__(self, base_path: str = "learning_data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.state_file = self.base_path / "learning_state.json"
        self.events_file = self.base_path / "learning_events.jsonl"
    
    def save_learning_state(self, state: Dict[str, Any]) -> bool:
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            log_manager.log_event("MiniLearner", f"Fehler beim Speichern: {e}", "ERROR")
            return False
    
    def load_learning_state(self) -> Optional[Dict[str, Any]]:
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_manager.log_event("MiniLearner", f"Fehler beim Laden: {e}", "ERROR")
            return None
    
    def append_learning_event(self, event: Dict[str, Any]) -> bool:
        try:
            with open(self.events_file, 'a', encoding='utf-8') as f:
                json.dump(event, f, ensure_ascii=False)
                f.write('\n')
            return True
        except Exception as e:
            log_manager.log_event("MiniLearner", f"Fehler beim Event-Logging: {e}", "ERROR")
            return False


class ConfidenceModel:
    """
    Erweitertes Konfidenzmodell mit Decay, Stabilisierung und Schwellen.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Konfidenz-Parameter
        self.base_confidence = config.get('base_confidence', 0.7)
        self.min_confidence = config.get('min_confidence', 0.3)
        self.max_confidence = config.get('max_confidence', 0.95)
        self.decay_rate = config.get('decay_rate', 0.01)
        self.stabilization_threshold = config.get('stabilization_threshold', 0.85)
        self.uncertainty_window = config.get('uncertainty_window', 0.1)
        
        # Integrity Floor
        self.integrity_floor = config.get('integrity_floor', 0.4)
        self.integrity_violation_penalty = config.get('integrity_violation_penalty', 0.3)
        
        # Aktueller Zustand
        self.current_confidence = self.base_confidence
        self.stabilized = False
        self.last_update = datetime.now()
        
    def update_confidence(self, feedback_type: str, learning_success: bool, 
                         integrity_score: float = 1.0) -> Tuple[float, bool]:
        """
        Aktualisiert Konfidenz basierend auf Feedback und Lernerfolg.
        
        Returns:
            Tuple von (neue_konfidenz, integrity_verletzung)
        """
        # Zeit-basierter Decay
        time_delta = (datetime.now() - self.last_update).total_seconds() / 3600  # in Stunden
        decay = self.decay_rate * time_delta
        self.current_confidence = max(self.min_confidence, self.current_confidence - decay)
        
        # Integrity Floor Check
        integrity_violation = False
        if integrity_score < self.integrity_floor:
            self.current_confidence -= self.integrity_violation_penalty
            integrity_violation = True
            log_manager.log_event(
                "MiniLearner", 
                f"Integrity Floor verletzt: {integrity_score:.2f} < {self.integrity_floor}", 
                "WARNING"
            )
        
        # Feedback-basierte Anpassung
        if feedback_type == "positive" and learning_success:
            adjustment = 0.05 if not self.stabilized else 0.02
            self.current_confidence = min(self.max_confidence, self.current_confidence + adjustment)
        elif feedback_type == "negative":
            adjustment = -0.08 if not self.stabilized else -0.04
            self.current_confidence = max(self.min_confidence, self.current_confidence + adjustment)
        elif feedback_type == "uncertain":
            # Bei Unsicherheit kleiner Penalty
            self.current_confidence = max(self.min_confidence, self.current_confidence - 0.02)
        
        # Stabilisierung prüfen
        if self.current_confidence >= self.stabilization_threshold:
            self.stabilized = True
        elif self.current_confidence < (self.stabilization_threshold - self.uncertainty_window):
            self.stabilized = False
        
        # Update Zeitstempel
        self.last_update = datetime.now()
        
        # Grenzen einhalten
        self.current_confidence = max(self.min_confidence, min(self.max_confidence, self.current_confidence))
        
        return self.current_confidence, integrity_violation
    
    def get_confidence_status(self) -> Dict[str, Any]:
        """Gibt aktuellen Konfidenz-Status zurück."""
        return {
            "current": self.current_confidence,
            "stabilized": self.stabilized,
            "min_threshold": self.min_confidence,
            "integrity_floor": self.integrity_floor,
            "last_update": self.last_update.isoformat(),
            "health": "good" if self.current_confidence > 0.7 else "moderate" if self.current_confidence > 0.5 else "poor"
        }


class FeedbackAnalyzer:
    """Analysiert und kategorisiert Feedback mit adaptiven Gewichtungen."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Feedback-Kategorien
        self.positive_indicators = config.get('positive_indicators', [
            "gut", "good", "richtig", "correct", "ja", "yes", "super", "great", 
            "perfekt", "perfect", "danke", "thanks", "hilfreich", "helpful"
        ])
        
        self.negative_indicators = config.get('negative_indicators', [
            "falsch", "wrong", "schlecht", "bad", "nein", "no", "stopp", "stop",
            "nicht", "not", "anders", "different", "problem", "fehler", "error"
        ])
        
        # Gewichtungen nach Quelle
        self.source_weights = {
            "user": 1.0,
            "system": 0.8,
            "implicit": 0.6,
            "automated": 0.4
        }
        
        # Kontext-Modifikatoren
        self.context_modifiers = {
            "emergency": 1.5,
            "educational": 1.2,
            "routine": 0.8,
            "test": 0.5
        }
    
    def analyze_feedback(self, feedback: str, source: str = "user", 
                        context_type: str = "routine") -> Dict[str, Any]:
        """
        Analysiert Feedback mit Quelle und Kontext.
        
        Returns:
            Dict mit type, confidence, weight, indicators
        """
        feedback_lower = feedback.lower()
        
        # Basis-Analyse
        positive_count = sum(1 for ind in self.positive_indicators if ind in feedback_lower)
        negative_count = sum(1 for ind in self.negative_indicators if ind in feedback_lower)
        
        # Typ bestimmen
        if positive_count > negative_count:
            feedback_type = "positive"
            confidence = min(1.0, positive_count * 0.3)
        elif negative_count > positive_count:
            feedback_type = "negative"
            confidence = min(1.0, negative_count * 0.3)
        elif "?" in feedback:
            feedback_type = "uncertain"
            confidence = 0.5
        else:
            feedback_type = "neutral"
            confidence = 0.3
        
        # Gewichtung berechnen
        source_weight = self.source_weights.get(source, 0.5)
        context_modifier = self.context_modifiers.get(context_type, 1.0)
        final_weight = source_weight * context_modifier
        
        return {
            "type": feedback_type,
            "confidence": confidence,
            "weight": final_weight,
            "source": source,
            "context": context_type,
            "indicators": {
                "positive": positive_count,
                "negative": negative_count
            },
            "raw_feedback": feedback
        }


class AdaptiveLearner:
    """
    Hauptklasse für adaptives Lernen mit verbesserter Architektur.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                 storage: Optional[StorageInterface] = None):
        """
        Initialisiert den Adaptive Learner.
        
        Args:
            config: Konfiguration für Lernparameter
            storage: Storage-Interface für Persistenz
        """
        self.config = config or {}
        self.storage = storage or MemoryStorage()
        
        # Komponenten initialisieren
        self.confidence_model = ConfidenceModel(config)
        self.feedback_analyzer = FeedbackAnalyzer(config)
        
        # Lernparameter
        self.learning_rate = self.config.get('learning_rate', 0.05)
        self.min_weight = self.config.get('min_weight', 0.3)
        self.max_weight = self.config.get('max_weight', 1.7)
        self.mode = self.config.get('mode', 'active')  # 'active' oder 'demo'
        
        # Momentum für glattere Anpassungen
        self.momentum = self.config.get('momentum', 0.7)
        self.last_adjustments = {}
        
        # Lernhistorie
        self.learning_history = []
        self.max_history = 100
        
        # DNA Marker für Replay-Kompatibilität
        self.dna_markers = []
        
        # Statistiken
        self.stats = {
            "total_feedback": 0,
            "positive": 0,
            "negative": 0,
            "adjustments": 0,
            "integrity_violations": 0
        }
        
        # Zustand laden falls vorhanden
        self._load_state()
    
    def learn_from_feedback(self, feedback: str, context: Dict[str, Any], 
                           profile: Dict[str, float], 
                           source: str = "user") -> Dict[str, Any]:
        """
        Hauptfunktion für Feedback-basiertes Lernen.
        
        Args:
            feedback: Feedback-Text
            context: Entscheidungskontext
            profile: Aktuelles ethisches Profil
            source: Feedback-Quelle
            
        Returns:
            Standardisiertes Lernergebnis
        """
        start_time = datetime.now()
        
        try:
            # 1. Feedback analysieren
            context_type = context.get("context_type", "routine")
            feedback_analysis = self.feedback_analyzer.analyze_feedback(
                feedback, source, context_type
            )
            
            # 2. Lernziele identifizieren
            learning_targets = self._identify_learning_targets(
                feedback_analysis, context, profile
            )
            
            # 3. Integrity Check
            integrity_score = context.get("ethics", {}).get("scores", {}).get("integrity", 1.0)
            
            # 4. Konfidenz aktualisieren
            learning_success = len(learning_targets) > 0 and self.mode == "active"
            new_confidence, integrity_violation = self.confidence_model.update_confidence(
                feedback_analysis["type"], learning_success, integrity_score
            )
            
            # 5. Profil anpassen (wenn aktiv und keine Integrity-Verletzung)
            adjusted_profile = profile.copy()
            adjustments = {}
            
            if self.mode == "active" and not integrity_violation and learning_targets:
                adjusted_profile, adjustments = self._adjust_profile(
                    profile.copy(), learning_targets, feedback_analysis["weight"]
                )
            
            # 6. DNA Marker setzen
            if adjustments:
                self._add_dna_marker("profile_adjusted", {
                    "adjustments": list(adjustments.keys()),
                    "feedback_type": feedback_analysis["type"]
                })
            
            # 7. Audit-Event senden
            if mini_audit and adjustments:
                audit_context = {
                    "event_type": "learning_update",
                    "adjustments": adjustments,
                    "confidence": new_confidence,
                    "integrity_check": not integrity_violation
                }
                mini_audit.log_decision(audit_context, profile, context)
            
            # 8. Lernereignis speichern
            learning_event = {
                "timestamp": datetime.now().isoformat(),
                "feedback_analysis": feedback_analysis,
                "learning_targets": learning_targets,
                "adjustments": adjustments,
                "confidence": new_confidence,
                "integrity_violation": integrity_violation
            }
            self.storage.append_learning_event(learning_event)
            
            # 9. Statistiken aktualisieren
            self._update_statistics(feedback_analysis["type"], adjustments, integrity_violation)
            
            # 10. Historie aktualisieren
            self._update_history(learning_event)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Standardisierte Rückgabe
            return {
                "status": "learned" if adjustments else "no_change",
                "confidence": new_confidence,
                "profile_updated": bool(adjustments),
                "adjusted_profile": adjusted_profile,
                "adjustments": adjustments,
                "feedback_analysis": feedback_analysis,
                "learning_targets": learning_targets,
                "integrity_check": {
                    "passed": not integrity_violation,
                    "score": integrity_score,
                    "floor": self.confidence_model.integrity_floor
                },
                "notes": self._generate_notes(feedback_analysis, adjustments, integrity_violation),
                "processing_time": processing_time,
                "dna_markers": self.dna_markers[-5:],  # Letzte 5 Marker
                "stats": self.stats.copy()
            }
            
        except Exception as e:
            log_manager.log_event("MiniLearner", f"Fehler beim Lernen: {e}", "ERROR")
            return {
                "status": "error",
                "confidence": self.confidence_model.current_confidence,
                "error": str(e),
                "notes": f"Lernprozess fehlgeschlagen: {e}"
            }
    
    def _identify_learning_targets(self, feedback_analysis: Dict[str, Any], 
                                  context: Dict[str, Any], 
                                  profile: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identifiziert Lernziele basierend auf Feedback und Kontext."""
        targets = []
        
        # Ethik-Informationen extrahieren
        ethics = context.get("ethics", {})
        scores = ethics.get("scores", {})
        violations = ethics.get("violations", [])
        
        # ETB-Ergebnis berücksichtigen
        etb_result = context.get("etb_result", {})
        chosen_option = etb_result.get("chosen_option")
        
        # PAE-Ergebnis berücksichtigen
        pae_result = context.get("pae_result", {})
        chosen_principle = pae_result.get("chosen_principle")
        
        if feedback_analysis["type"] == "negative":
            # Bei negativem Feedback
            
            # Verletzungen korrigieren
            for violation in violations:
                if violation in principles.ALIGN_KEYS:
                    targets.append({
                        "principle": violation,
                        "direction": "increase",
                        "strength": 0.8,
                        "reason": "violation_correction"
                    })
            
            # Niedrige Scores verbessern
            for principle, score in scores.items():
                if score < 0.4 and principle not in [t["principle"] for t in targets]:
                    targets.append({
                        "principle": principle,
                        "direction": "increase",
                        "strength": 0.6,
                        "reason": "low_score_improvement"
                    })
            
        elif feedback_analysis["type"] == "positive":
            # Bei positivem Feedback
            
            # Erfolgreiche Prinzipien verstärken
            if chosen_principle:
                targets.append({
                    "principle": chosen_principle,
                    "direction": "increase",
                    "strength": 0.4,
                    "reason": "successful_choice"
                })
            
            # Hohe Scores leicht verstärken
            for principle, score in scores.items():
                if score > 0.8:
                    targets.append({
                        "principle": principle,
                        "direction": "increase",
                        "strength": 0.2,
                        "reason": "excellence_reinforcement"
                    })
        
        # Gewichtung nach Feedback-Gewicht anpassen
        for target in targets:
            target["strength"] *= feedback_analysis["weight"]
        
        return targets
    
    def _adjust_profile(self, profile: Dict[str, float], 
                       targets: List[Dict[str, Any]], 
                       feedback_weight: float) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Passt Profil basierend auf Lernzielen an."""
        adjustments = {}
        
        for target in targets:
            principle = target["principle"]
            direction = target["direction"]
            strength = target["strength"]
            
            current_weight = profile.get(principle, 1.0)
            
            # Anpassung berechnen
            base_adjustment = self.learning_rate * strength * feedback_weight
            
            # Momentum
            if principle in self.last_adjustments:
                momentum_adj = self.momentum * self.last_adjustments[principle]
                base_adjustment = (1 - self.momentum) * base_adjustment + momentum_adj
            
            # Richtung
            adjustment = base_adjustment if direction == "increase" else -base_adjustment
            
            # Neue Gewichtung
            new_weight = current_weight + adjustment
            new_weight = max(self.min_weight, min(self.max_weight, new_weight))
            
            # Nur signifikante Änderungen
            if abs(new_weight - current_weight) > 0.01:
                profile[principle] = new_weight
                adjustments[principle] = {
                    "old": current_weight,
                    "new": new_weight,
                    "change": new_weight - current_weight,
                    "reason": target["reason"]
                }
                self.last_adjustments[principle] = adjustment
        
        return profile, adjustments
    
    def _add_dna_marker(self, marker_type: str, data: Dict[str, Any]):
        """Fügt DNA-Marker für Replay-Kompatibilität hinzu."""
        marker = {
            "type": marker_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.dna_markers.append(marker)
        
        # Begrenzen
        if len(self.dna_markers) > 50:
            self.dna_markers.pop(0)
    
    def _update_statistics(self, feedback_type: str, adjustments: Dict[str, Any], 
                          integrity_violation: bool):
        """Aktualisiert interne Statistiken."""
        self.stats["total_feedback"] += 1
        
        if feedback_type == "positive":
            self.stats["positive"] += 1
        elif feedback_type == "negative":
            self.stats["negative"] += 1
        
        if adjustments:
            self.stats["adjustments"] += len(adjustments)
        
        if integrity_violation:
            self.stats["integrity_violations"] += 1
    
    def _update_history(self, event: Dict[str, Any]):
        """Aktualisiert Lernhistorie."""
        self.learning_history.append(event)
        
        if len(self.learning_history) > self.max_history:
            self.learning_history.pop(0)
    
    def _generate_notes(self, feedback_analysis: Dict[str, Any], 
                       adjustments: Dict[str, Any], 
                       integrity_violation: bool) -> str:
        """Generiert beschreibende Notizen zum Lernvorgang."""
        notes = []
        
        if integrity_violation:
            notes.append("Integrity Floor verletzt - Anpassungen blockiert")
        elif adjustments:
            notes.append(f"{len(adjustments)} Prinzipien angepasst")
        else:
            notes.append("Keine Anpassungen vorgenommen")
        
        if feedback_analysis["type"] == "uncertain":
            notes.append("Unsicheres Feedback erkannt")
        
        if feedback_analysis["weight"] < 0.5:
            notes.append("Niedrige Feedback-Gewichtung")
        
        return "; ".join(notes)
    
    def _save_state(self):
        """Speichert aktuellen Lernzustand."""
        state = {
            "confidence": self.confidence_model.get_confidence_status(),
            "stats": self.stats,
            "last_adjustments": self.last_adjustments,
            "dna_markers": self.dna_markers[-20:],  # Letzte 20
            "timestamp": datetime.now().isoformat()
        }
        self.storage.save_learning_state(state)
    
    def _load_state(self):
        """Lädt gespeicherten Lernzustand."""
        state = self.storage.load_learning_state()
        if state:
            # Konfidenz wiederherstellen
            if "confidence" in state:
                self.confidence_model.current_confidence = state["confidence"].get("current", 0.7)
            
            # Statistiken
            if "stats" in state:
                self.stats.update(state["stats"])
            
            # Letzte Anpassungen
            if "last_adjustments" in state:
                self.last_adjustments = state["last_adjustments"]
            
            # DNA Markers
            if "dna_markers" in state:
                self.dna_markers = state["dna_markers"]
            
            log_manager.log_event("MiniLearner", "Zustand erfolgreich geladen", "INFO")
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Gibt umfassende Lernzusammenfassung zurück."""
        # Erfolgsrate berechnen
        total = self.stats["total_feedback"]
        success_rate = self.stats["positive"] / total if total > 0 else 0.5
        
        # Muster analysieren
        recent_feedback = [e["feedback_analysis"]["type"] for e in self.learning_history[-10:]]
        trend = "improving" if recent_feedback.count("positive") > 5 else "stable" if recent_feedback.count("positive") > 3 else "declining"
        
        return {
            "stats": self.stats,
            "success_rate": success_rate,
            "confidence": self.confidence_model.get_confidence_status(),
            "trend": trend,
            "total_history": len(self.learning_history),
            "integrity_health": self.stats["integrity_violations"] / total if total > 0 else 0,
            "learning_active": self.mode == "active",
            "last_save": datetime.now().isoformat()
        }
    
    def prepare_for_meta_learner(self) -> Dict[str, Any]:
        """Bereitet Daten für Meta-Learner vor."""
        return {
            "module": "mini_learner",
            "confidence": self.confidence_model.current_confidence,
            "learning_patterns": self._analyze_patterns(),
            "adjustment_history": self.last_adjustments,
            "integrity_status": {
                "violations": self.stats["integrity_violations"],
                "current_floor": self.confidence_model.integrity_floor
            },
            "dna_markers": self.dna_markers[-10:],
            "recommendations": self._generate_meta_recommendations()
        }
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analysiert Lernmuster für Meta-Learner."""
        if not self.learning_history:
            return {}
        
        # Prinzipien-Anpassungen zählen
        principle_adjustments = {}
        for event in self.learning_history:
            for principle, adj in event.get("adjustments", {}).items():
                if principle not in principle_adjustments:
                    principle_adjustments[principle] = {"increases": 0, "decreases": 0}
                
                if adj["change"] > 0:
                    principle_adjustments[principle]["increases"] += 1
                else:
                    principle_adjustments[principle]["decreases"] += 1
        
        return {
            "frequently_adjusted": principle_adjustments,
            "dominant_feedback": max(set(e["feedback_analysis"]["type"] for e in self.learning_history), 
                                   key=lambda x: sum(1 for e in self.learning_history if e["feedback_analysis"]["type"] == x))
        }
    
    def _generate_meta_recommendations(self) -> List[str]:
        """Generiert Empfehlungen für Meta-Learner."""
        recommendations = []
        
        if self.confidence_model.current_confidence < 0.5:
            recommendations.append("Konfidenz kritisch niedrig - Grundlegende Überprüfung empfohlen")
        
        if self.stats["integrity_violations"] > self.stats["total_feedback"] * 0.2:
            recommendations.append("Hohe Integrity-Verletzungsrate - Ethik-Module prüfen")
        
        if self.confidence_model.stabilized:
            recommendations.append("System stabilisiert - Lernrate kann reduziert werden")
        
        return recommendations


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Hauptschnittstelle gemäß INTEGRA-Standard.
    
    Args:
        input_text: Feedback-Text
        context: Kontext mit profile, source, mode etc.
        
    Returns:
        Standardisiertes Lernergebnis
    """
    context = context or {}
    
    try:
        # Konfiguration extrahieren
        config = context.get("learner_config", {})
        
        # Storage bestimmen
        storage_type = config.get("storage_type", "memory")
        if storage_type == "file":
            storage = FileStorage(config.get("storage_path", "learning_data"))
        else:
            storage = MemoryStorage()
        
        # Learner initialisieren
        learner = AdaptiveLearner(config, storage)
        
        # Profil extrahieren
        profile = context.get("profile", {})
        if not profile and profiles:
            profile = profiles.get_default_profile()
        
        # Feedback-Quelle
        source = context.get("feedback_source", "user")
        
        # Lernen durchführen
        result = learner.learn_from_feedback(input_text, context, profile, source)
        
        # Zustand speichern
        learner._save_state()
        
        # Meta-Learner Daten vorbereiten
        if context.get("prepare_meta", False):
            result["meta_data"] = learner.prepare_for_meta_learner()
        
        # Standardisierte Rückgabe
        return {
            "success": result["status"] != "error",
            "status": result["status"],
            "confidence": result["confidence"],
            "notes": result.get("notes", ""),
            "profile_updated": result.get("profile_updated", False),
            "adjusted_profile": result.get("adjusted_profile", {}),
            "adjustments": result.get("adjustments", {}),
            "integrity_check": result.get("integrity_check", {}),
            "module": "mini_learner",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "meta": {
                "feedback_analysis": result.get("feedback_analysis", {}),
                "learning_targets": result.get("learning_targets", []),
                "stats": result.get("stats", {}),
                "dna_markers": result.get("dna_markers", [])
            }
        }
        
    except Exception as e:
        log_manager.log_event("MiniLearner", f"Kritischer Fehler in run_module: {e}", "ERROR")
        return {
            "success": False,
            "status": "error",
            "confidence": 0.5,
            "notes": f"Lernmodul-Fehler: {e}",
            "module": "mini_learner",
            "version": "2.0",
            "timestamp": datetime.now().isoformat()
        }


def demo():
    """Demonstriert die verbesserte Mini-Learner Funktionalität."""
    print("=== INTEGRA Mini-Learner 2.0 Demo ===\n")
    
    # Demo-Profil
    demo_profile = {
        "awareness": 1.0,
        "learning": 1.0,
        "integrity": 1.0,
        "governance": 1.0,
        "nurturing": 1.0
    }
    
    # Test 1: Positives Feedback mit hoher Integrität
    print("Test 1: Positives Feedback")
    context1 = {
        "profile": demo_profile.copy(),
        "ethics": {
            "scores": {"integrity": 0.9, "nurturing": 0.8, "learning": 0.7},
            "violations": []
        },
        "pae_result": {"chosen_principle": "integrity"},
        "context_type": "educational",
        "feedback_source": "user"
    }
    
    result1 = run_module("Das war sehr hilfreich und korrekt!", context1)
    print(f"Status: {result1['status']}")
    print(f"Konfidenz: {result1['confidence']:.2f}")
    print(f"Integrity Check: {result1['integrity_check']}")
    if result1['adjustments']:
        print("Anpassungen:")
        for principle, adj in result1['adjustments'].items():
            print(f"  {principle}: {adj['old']:.2f} → {adj['new']:.2f} ({adj['reason']})")
    print()
    
    # Test 2: Negatives Feedback mit Integrity-Verletzung
    print("Test 2: Negatives Feedback mit Integrity-Verletzung")
    context2 = {
        "profile": result1.get("adjusted_profile", demo_profile),
        "ethics": {
            "scores": {"integrity": 0.2, "nurturing": 0.9},  # Integrity unter Floor!
            "violations": ["integrity"]
        },
        "context_type": "emergency",
        "feedback_source": "system"
    }
    
    result2 = run_module("Das war falsch und unehrlich", context2)
    print(f"Status: {result2['status']}")
    print(f"Konfidenz: {result2['confidence']:.2f}")
    print(f"Notizen: {result2['notes']}")
    print(f"Integrity verletzt: {not result2['integrity_check']['passed']}")
    print()
    
    # Test 3: Unsicheres Feedback
    print("Test 3: Unsicheres Feedback")
    context3 = {
        "profile": demo_profile.copy(),
        "feedback_source": "implicit",
        "context_type": "routine"
    }
    
    result3 = run_module("Hmm, bin mir nicht sicher ob das richtig war?", context3)
    print(f"Feedback-Typ: {result3['meta']['feedback_analysis']['type']}")
    print(f"Gewichtung: {result3['meta']['feedback_analysis']['weight']:.2f}")
    print()
    
    # Test 4: Zusammenfassung mit Meta-Daten
    print("Test 4: Lernzusammenfassung")
    context4 = {
        "prepare_meta": True,
        "learner_config": {
            "storage_type": "memory"
        }
    }
    
    # Einige weitere Feedbacks für Statistik
    run_module("Gut gemacht!", context4)
    run_module("Das war hilfreich", context4)
    result4 = run_module("Perfekt!", context4)
    
    if "meta_data" in result4:
        meta = result4["meta_data"]
        print(f"Modul: {meta['module']}")
        print(f"Aktuelle Konfidenz: {meta['confidence']:.2f}")
        print(f"Empfehlungen: {meta['recommendations']}")
    
    print("\n✅ Mini-Learner Demo abgeschlossen!")


if __name__ == "__main__":
    demo()