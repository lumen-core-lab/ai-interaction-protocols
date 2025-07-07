# -*- coding: utf-8 -*-
"""
Modulname: escalation.py
Beschreibung: Eskalationsmanagement für kritische ethische Entscheidungen
Teil von: EVA Validator v1.0 - Universal Ethical Validation System
Autor: Dominik Knape
Lizenz: CC BY-NC-SA 4.0
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod
import threading
from queue import Queue, PriorityQueue
import time

# EVA imports
try:
    from . import schema
except ImportError:
    import schema

from schema import (
    DecisionInput, ContextInput, ValidationResult,
    SeverityLevel, ValidationStatus, ScenarioType, UserRiskLevel
)


class EscalationType(Enum):
    """Typen von Eskalationen."""
    AUTOMATED = "automated"          # Automatische Weiterleitung
    HUMAN_REVIEW = "human_review"    # Menschliche Überprüfung
    SYSTEM_ALERT = "system_alert"    # System-Benachrichtigung
    EMERGENCY_STOP = "emergency_stop" # Sofortiger Stopp
    AUDIT_FLAG = "audit_flag"        # Audit-Markierung


class EscalationPriority(Enum):
    """Prioritätsstufen für Eskalationen."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class EscalationTrigger:
    """Definiert einen Eskalations-Trigger."""
    name: str
    condition_type: str  # threshold, pattern, combination
    severity_threshold: Optional[SeverityLevel] = None
    score_threshold: Optional[float] = None
    patterns: List[str] = field(default_factory=list)
    user_risk_levels: List[UserRiskLevel] = field(default_factory=list)
    scenario_types: List[ScenarioType] = field(default_factory=list)
    priority: EscalationPriority = EscalationPriority.MEDIUM
    escalation_type: EscalationType = EscalationType.HUMAN_REVIEW
    
    def check_condition(self, evaluation: Dict[str, Any], 
                       context: ContextInput) -> bool:
        """Prüft ob Trigger-Bedingung erfüllt ist."""
        if self.condition_type == "threshold":
            return self._check_threshold(evaluation)
        elif self.condition_type == "pattern":
            return self._check_pattern(evaluation)
        elif self.condition_type == "combination":
            return self._check_combination(evaluation, context)
        return False
    
    def _check_threshold(self, evaluation: Dict[str, Any]) -> bool:
        """Prüft Schwellenwert-Bedingungen."""
        if self.severity_threshold:
            current_severity = evaluation.get("severity", SeverityLevel.INFO)
            if self._compare_severity(current_severity, self.severity_threshold):
                return True
                
        if self.score_threshold is not None:
            score = evaluation.get("final_score", 1.0)
            if score < self.score_threshold:
                return True
                
        return False
    
    def _check_pattern(self, evaluation: Dict[str, Any]) -> bool:
        """Prüft Pattern-Bedingungen."""
        violations = evaluation.get("violations", [])
        warnings = evaluation.get("warnings", [])
        
        for pattern in self.patterns:
            if pattern in violations or pattern in warnings:
                return True
        return False
    
    def _check_combination(self, evaluation: Dict[str, Any], 
                          context: ContextInput) -> bool:
        """Prüft kombinierte Bedingungen."""
        conditions_met = 0
        conditions_total = 0
        
        # User Risk prüfen
        if self.user_risk_levels:
            conditions_total += 1
            if context.user_risk in self.user_risk_levels:
                conditions_met += 1
        
        # Szenario-Typ prüfen
        if self.scenario_types:
            conditions_total += 1
            if context.scenario_type in self.scenario_types:
                conditions_met += 1
        
        # Score prüfen
        if self.score_threshold is not None:
            conditions_total += 1
            if evaluation.get("final_score", 1.0) < self.score_threshold:
                conditions_met += 1
        
        # Mindestens 2 Bedingungen müssen erfüllt sein
        return conditions_met >= min(2, conditions_total)
    
    def _compare_severity(self, current: SeverityLevel, 
                         threshold: SeverityLevel) -> bool:
        """Vergleicht Severity-Level."""
        severity_order = {
            SeverityLevel.INFO: 0,
            SeverityLevel.WARNING: 1,
            SeverityLevel.CRITICAL: 2,
            SeverityLevel.BLOCKED: 3
        }
        return severity_order.get(current, 0) >= severity_order.get(threshold, 0)


@dataclass
class EscalationCase:
    """Repräsentiert einen Eskalationsfall."""
    case_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    decision_id: str = ""
    trigger_name: str = ""
    escalation_type: EscalationType = EscalationType.HUMAN_REVIEW
    priority: EscalationPriority = EscalationPriority.MEDIUM
    
    # Details
    evaluation_summary: Dict[str, Any] = field(default_factory=dict)
    context_summary: Dict[str, Any] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    
    # Status
    status: str = "pending"  # pending, reviewing, resolved, cancelled
    assigned_to: Optional[str] = None
    resolved_at: Optional[str] = None
    resolution: Optional[str] = None
    resolution_feedback: Optional[Dict[str, Any]] = None
    
    # Metadaten
    retry_count: int = 0
    auto_resolve_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        data = {
            "case_id": self.case_id,
            "timestamp": self.timestamp,
            "decision_id": self.decision_id,
            "trigger_name": self.trigger_name,
            "escalation_type": self.escalation_type.value,
            "priority": self.priority.value,
            "status": self.status,
            "evaluation_summary": self.evaluation_summary,
            "context_summary": self.context_summary,
            "reasons": self.reasons,
            "assigned_to": self.assigned_to,
            "resolved_at": self.resolved_at,
            "resolution": self.resolution,
            "resolution_feedback": self.resolution_feedback,
            "retry_count": self.retry_count,
            "auto_resolve_at": self.auto_resolve_at,
            "tags": self.tags
        }
        return data


class EscalationHandler(ABC):
    """Abstrakte Basis-Klasse für Eskalations-Handler."""
    
    @abstractmethod
    def handle(self, case: EscalationCase) -> Dict[str, Any]:
        """Behandelt einen Eskalationsfall."""
        pass
    
    @abstractmethod
    def can_handle(self, escalation_type: EscalationType) -> bool:
        """Prüft ob Handler für Typ zuständig ist."""
        pass


class HumanReviewHandler(EscalationHandler):
    """Handler für menschliche Überprüfung."""
    
    def __init__(self, review_queue: Optional[Queue] = None,
                 notification_callback: Optional[Callable] = None):
        self.review_queue = review_queue or Queue()
        self.notification_callback = notification_callback
        self.pending_reviews = {}
    
    def handle(self, case: EscalationCase) -> Dict[str, Any]:
        """Leitet Fall zur menschlichen Überprüfung weiter."""
        # In Queue einreihen
        self.review_queue.put((case.priority.value, case))
        self.pending_reviews[case.case_id] = case
        
        # Benachrichtigung senden
        if self.notification_callback:
            self.notification_callback({
                "type": "human_review_required",
                "case_id": case.case_id,
                "priority": case.priority.value,
                "summary": case.evaluation_summary
            })
        
        return {
            "status": "queued_for_review",
            "case_id": case.case_id,
            "queue_position": self.review_queue.qsize(),
            "estimated_wait": self._estimate_wait_time()
        }
    
    def can_handle(self, escalation_type: EscalationType) -> bool:
        return escalation_type == EscalationType.HUMAN_REVIEW
    
    def _estimate_wait_time(self) -> str:
        """Schätzt Wartezeit basierend auf Queue-Größe."""
        queue_size = self.review_queue.qsize()
        # Annahme: 5 Minuten pro Review
        minutes = queue_size * 5
        return f"{minutes} Minuten"
    
    def get_pending_case(self, case_id: str) -> Optional[EscalationCase]:
        """Holt einen ausstehenden Fall."""
        return self.pending_reviews.get(case_id)
    
    def resolve_case(self, case_id: str, resolution: str, 
                    feedback: Optional[Dict[str, Any]] = None) -> bool:
        """Löst einen Fall auf."""
        if case_id in self.pending_reviews:
            case = self.pending_reviews[case_id]
            case.status = "resolved"
            case.resolved_at = datetime.now().isoformat()
            case.resolution = resolution
            case.resolution_feedback = feedback
            del self.pending_reviews[case_id]
            return True
        return False


class SystemAlertHandler(EscalationHandler):
    """Handler für System-Benachrichtigungen."""
    
    def __init__(self, alert_callbacks: Optional[List[Callable]] = None):
        self.alert_callbacks = alert_callbacks or []
        self.alert_history = []
        self.max_history = 1000
    
    def handle(self, case: EscalationCase) -> Dict[str, Any]:
        """Sendet System-Alert."""
        alert_data = {
            "alert_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "case_id": case.case_id,
            "priority": case.priority.value,
            "type": "ethics_escalation",
            "summary": {
                "decision_id": case.decision_id,
                "trigger": case.trigger_name,
                "reasons": case.reasons[:3]  # Top 3 Gründe
            }
        }
        
        # Callbacks ausführen
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                print(f"Alert callback error: {e}")
        
        # In History speichern
        self.alert_history.append(alert_data)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        return {
            "status": "alert_sent",
            "alert_id": alert_data["alert_id"],
            "recipients": len(self.alert_callbacks)
        }
    
    def can_handle(self, escalation_type: EscalationType) -> bool:
        return escalation_type == EscalationType.SYSTEM_ALERT
    
    def add_callback(self, callback: Callable):
        """Fügt Alert-Callback hinzu."""
        self.alert_callbacks.append(callback)
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Gibt kürzliche Alerts zurück."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
        ]


class EmergencyStopHandler(EscalationHandler):
    """Handler für Notfall-Stopps."""
    
    def __init__(self, stop_callback: Optional[Callable] = None):
        self.stop_callback = stop_callback
        self.emergency_log = []
    
    def handle(self, case: EscalationCase) -> Dict[str, Any]:
        """Führt Notfall-Stopp durch."""
        emergency_data = {
            "emergency_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "case": case.to_dict(),
            "action": "emergency_stop"
        }
        
        # Stopp-Callback ausführen
        if self.stop_callback:
            try:
                self.stop_callback(emergency_data)
            except Exception as e:
                print(f"Emergency stop error: {e}")
        
        # Loggen
        self.emergency_log.append(emergency_data)
        
        return {
            "status": "emergency_stop_executed",
            "emergency_id": emergency_data["emergency_id"],
            "message": "System wurde angehalten. Manuelle Intervention erforderlich."
        }
    
    def can_handle(self, escalation_type: EscalationType) -> bool:
        return escalation_type == EscalationType.EMERGENCY_STOP


class EscalationManager:
    """
    Zentrale Verwaltung aller Eskalationen.
    Orchestriert Trigger, Handler und Fallverfolgung.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Trigger-Registry
        self.triggers = self._initialize_default_triggers()
        
        # Handler-Registry
        self.handlers = {
            EscalationType.HUMAN_REVIEW: HumanReviewHandler(),
            EscalationType.SYSTEM_ALERT: SystemAlertHandler(),
            EscalationType.EMERGENCY_STOP: EmergencyStopHandler()
        }
        
        # Fall-Tracking
        self.active_cases = {}
        self.case_history = []
        self.max_history = 10000
        
        # Statistiken
        self.stats = {
            "total_escalations": 0,
            "by_type": {},
            "by_priority": {},
            "average_resolution_time": 0
        }
    
    def _initialize_default_triggers(self) -> List[EscalationTrigger]:
        """Initialisiert Standard-Trigger."""
        return [
            # Kritische Violations
            EscalationTrigger(
                name="critical_violation",
                condition_type="threshold",
                severity_threshold=SeverityLevel.CRITICAL,
                priority=EscalationPriority.HIGH,
                escalation_type=EscalationType.HUMAN_REVIEW
            ),
            
            # Sehr niedriger Score
            EscalationTrigger(
                name="very_low_score",
                condition_type="threshold",
                score_threshold=0.3,
                priority=EscalationPriority.HIGH,
                escalation_type=EscalationType.HUMAN_REVIEW
            ),
            
            # Harm-Patterns
            EscalationTrigger(
                name="harm_detected",
                condition_type="pattern",
                patterns=["harm_intent", "illegal_activity"],
                priority=EscalationPriority.CRITICAL,
                escalation_type=EscalationType.EMERGENCY_STOP
            ),
            
            # High-Risk User + Low Score
            EscalationTrigger(
                name="high_risk_low_score",
                condition_type="combination",
                user_risk_levels=[UserRiskLevel.HIGH, UserRiskLevel.CRITICAL],
                score_threshold=0.6,
                priority=EscalationPriority.HIGH,
                escalation_type=EscalationType.HUMAN_REVIEW
            ),
            
            # Privacy + No Consent
            EscalationTrigger(
                name="privacy_no_consent",
                condition_type="combination",
                scenario_types=[ScenarioType.PRIVACY],
                patterns=["privacy_violation"],
                priority=EscalationPriority.HIGH,
                escalation_type=EscalationType.SYSTEM_ALERT
            )
        ]
    
    def check_escalation(self, evaluation: Dict[str, Any],
                        decision: DecisionInput,
                        context: ContextInput) -> List[EscalationCase]:
        """
        Prüft ob Eskalation nötig ist.
        
        Returns:
            Liste von ausgelösten Eskalationsfällen
        """
        triggered_cases = []
        
        for trigger in self.triggers:
            if trigger.check_condition(evaluation, context):
                # Eskalationsfall erstellen
                case = self._create_escalation_case(
                    trigger, evaluation, decision, context
                )
                
                # Handler aufrufen
                handler = self.handlers.get(trigger.escalation_type)
                if handler:
                    result = handler.handle(case)
                    case.status = "processing"
                    
                    # Fall registrieren
                    self.active_cases[case.case_id] = case
                    triggered_cases.append(case)
                    
                    # Statistiken
                    self._update_statistics(case)
        
        return triggered_cases
    
    def _create_escalation_case(self, trigger: EscalationTrigger,
                               evaluation: Dict[str, Any],
                               decision: DecisionInput,
                               context: ContextInput) -> EscalationCase:
        """Erstellt einen Eskalationsfall."""
        case = EscalationCase(
            decision_id=decision.id,
            trigger_name=trigger.name,
            escalation_type=trigger.escalation_type,
            priority=trigger.priority
        )
        
        # Evaluation-Zusammenfassung
        case.evaluation_summary = {
            "final_score": evaluation.get("final_score", 0),
            "severity": evaluation.get("severity", SeverityLevel.INFO).value,
            "violations": evaluation.get("violations", []),
            "warnings": evaluation.get("warnings", [])
        }
        
        # Kontext-Zusammenfassung
        case.context_summary = {
            "user_risk": context.user_risk.value,
            "scenario_type": context.scenario_type.value,
            "source_system": context.source_system
        }
        
        # Gründe sammeln
        case.reasons = evaluation.get("reasons", [])[:5]  # Top 5
        case.reasons.append(f"Trigger: {trigger.name}")
        
        # Tags
        if evaluation.get("violations"):
            case.tags.append("has_violations")
        if context.user_risk in [UserRiskLevel.HIGH, UserRiskLevel.CRITICAL]:
            case.tags.append("high_risk_user")
        
        return case
    
    def _update_statistics(self, case: EscalationCase):
        """Aktualisiert Eskalations-Statistiken."""
        self.stats["total_escalations"] += 1
        
        # Nach Typ
        esc_type = case.escalation_type.value
        self.stats["by_type"][esc_type] = self.stats["by_type"].get(esc_type, 0) + 1
        
        # Nach Priorität
        priority = case.priority.value
        self.stats["by_priority"][priority] = self.stats["by_priority"].get(priority, 0) + 1
    
    def resolve_case(self, case_id: str, resolution: str,
                    resolver: str = "system",
                    feedback: Optional[Dict[str, Any]] = None) -> bool:
        """Löst einen Eskalationsfall."""
        if case_id not in self.active_cases:
            return False
        
        case = self.active_cases[case_id]
        case.status = "resolved"
        case.resolved_at = datetime.now().isoformat()
        case.resolution = resolution
        case.assigned_to = resolver
        case.resolution_feedback = feedback or {}
        
        # In History verschieben
        self.case_history.append(case)
        if len(self.case_history) > self.max_history:
            self.case_history.pop(0)
        
        # Aus aktiven Fällen entfernen
        del self.active_cases[case_id]
        
        # Resolution Time für Statistiken
        created = datetime.fromisoformat(case.timestamp)
        resolved = datetime.fromisoformat(case.resolved_at)
        resolution_time = (resolved - created).total_seconds()
        
        # Gleitender Durchschnitt
        avg = self.stats["average_resolution_time"]
        count = len(self.case_history)
        self.stats["average_resolution_time"] = ((avg * (count - 1)) + resolution_time) / count
        
        return True
    
    def get_active_cases(self, priority: Optional[EscalationPriority] = None) -> List[EscalationCase]:
        """Gibt aktive Fälle zurück."""
        cases = list(self.active_cases.values())
        
        if priority:
            cases = [c for c in cases if c.priority == priority]
        
        # Nach Priorität sortieren
        cases.sort(key=lambda c: c.priority.value, reverse=True)
        
        return cases
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Eskalations-Statistiken zurück."""
        stats = self.stats.copy()
        stats["active_cases"] = len(self.active_cases)
        stats["resolved_cases"] = len(self.case_history)
        
        # Aktive Fälle nach Status
        status_counts = {}
        for case in self.active_cases.values():
            status_counts[case.status] = status_counts.get(case.status, 0) + 1
        stats["active_by_status"] = status_counts
        
        return stats
    
    def add_custom_trigger(self, trigger: EscalationTrigger):
        """Fügt benutzerdefinierten Trigger hinzu."""
        self.triggers.append(trigger)
    
    def add_custom_handler(self, escalation_type: EscalationType, 
                          handler: EscalationHandler):
        """Fügt benutzerdefinierten Handler hinzu."""
        self.handlers[escalation_type] = handler


def demo():
    """Demonstriert die Eskalations-Funktionalität."""
    print("=== EVA Validator Escalation Demo ===\n")
    
    # Manager initialisieren
    manager = EscalationManager()
    
    # Demo-Callbacks
    def alert_callback(alert_data):
        print(f"🚨 ALERT: {alert_data['summary']}")
    
    def stop_callback(emergency_data):
        print(f"🛑 EMERGENCY STOP: {emergency_data['emergency_id']}")
    
    # Callbacks registrieren
    manager.handlers[EscalationType.SYSTEM_ALERT].add_callback(alert_callback)
    manager.handlers[EscalationType.EMERGENCY_STOP].stop_callback = stop_callback
    
    # Test 1: Kritische Violation
    print("Test 1: Kritische Violation")
    print("-" * 50)
    
    evaluation1 = {
        "final_score": 0.2,
        "severity": SeverityLevel.CRITICAL,
        "violations": ["harm_intent", "illegal_activity"],
        "warnings": [],
        "reasons": ["Schädliche Absicht erkannt", "Illegale Aktivität"]
    }
    
    decision1 = DecisionInput(
        id="test-001",
        input="Wie kann ich Schaden anrichten?",
        output="Das kann ich nicht unterstützen.",
        score=0.2,
        explanation="Ablehnung"
    )
    
    context1 = ContextInput(
        user_risk=UserRiskLevel.HIGH,
        scenario_type=ScenarioType.HARM
    )
    
    cases1 = manager.check_escalation(evaluation1, decision1, context1)
    print(f"Ausgelöste Eskalationen: {len(cases1)}")
    for case in cases1:
        print(f"  - {case.trigger_name} ({case.escalation_type.value})")
        print(f"    Priority: {case.priority.value}")
        print(f"    Status: {case.status}")
    
    # Test 2: Privacy ohne Consent
    print("\n\nTest 2: Privacy-Verletzung")
    print("-" * 50)
    
    evaluation2 = {
        "final_score": 0.5,
        "severity": SeverityLevel.WARNING,
        "violations": ["privacy_violation"],
        "warnings": ["no_consent"],
        "reasons": ["Keine Einwilligung erwähnt"]
    }
    
    decision2 = DecisionInput(
        id="test-002",
        input="Kann ich Kundendaten verkaufen?",
        output="Ja, das ist möglich.",
        score=0.5,
        explanation="Direkte Antwort"
    )
    
    context2 = ContextInput(
        user_risk=UserRiskLevel.MEDIUM,
        scenario_type=ScenarioType.PRIVACY
    )
    
    cases2 = manager.check_escalation(evaluation2, decision2, context2)
    print(f"Ausgelöste Eskalationen: {len(cases2)}")
    
    # Test 3: Kombination High Risk + Low Score
    print("\n\nTest 3: High Risk User mit niedrigem Score")
    print("-" * 50)
    
    evaluation3 = {
        "final_score": 0.55,
        "severity": SeverityLevel.WARNING,
        "violations": [],
        "warnings": ["potential_misuse"],
        "reasons": ["Niedriger Score bei Hochrisiko-Nutzer"]
    }
    
    decision3 = DecisionInput(
        id="test-003",
        input="Generelle Anfrage",
        output="Unsichere Antwort",
        score=0.55,
        explanation="Unklar"
    )
    
    context3 = ContextInput(
        user_risk=UserRiskLevel.CRITICAL,
        scenario_type=ScenarioType.GENERAL
    )
    
    cases3 = manager.check_escalation(evaluation3, decision3, context3)
    print(f"Ausgelöste Eskalationen: {len(cases3)}")
    
    # Statistiken anzeigen
    print("\n\nEskalations-Statistiken:")
    print("-" * 50)
    stats = manager.get_statistics()
    print(f"Gesamt-Eskalationen: {stats['total_escalations']}")
    print(f"Nach Typ: {dict(stats['by_type'])}")
    print(f"Nach Priorität: {dict(stats['by_priority'])}")
    print(f"Aktive Fälle: {stats['active_cases']}")
    
    # Aktive Fälle anzeigen
    print("\n\nAktive Eskalationsfälle:")
    print("-" * 50)
    active = manager.get_active_cases()
    for case in active[:3]:  # Top 3
        print(f"Case ID: {case.case_id}")
        print(f"  Decision: {case.decision_id}")
        print(f"  Priority: {case.priority.value}")
        print(f"  Type: {case.escalation_type.value}")
        print(f"  Gründe: {case.reasons[:2]}")
        print()
    
    # Fall auflösen
    if active:
        case_id = active[0].case_id
        success = manager.resolve_case(
            case_id,
            resolution="Manuell überprüft - Antwort angepasst",
            resolver="human_reviewer_1",
            feedback={"action": "modified", "risk_mitigation": "applied"}
        )
        print(f"Fall {case_id} aufgelöst: {success}")
    
    print("\n✅ Escalation Demo abgeschlossen!")


if __name__ == "__main__":
    demo()