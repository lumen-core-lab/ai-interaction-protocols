# -*- coding: utf-8 -*-
"""
Modulname: validator.py
Beschreibung: Zentrale Validierungslogik - Hauptschnittstelle für EVA Validator
Teil von: EVA Validator v1.0 - Universal Ethical Validation System
Autor: Dominik Knape
Lizenz: CC BY-NC-SA 4.0
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import json
import uuid
from pathlib import Path
import os

# EVA imports
try:
    from . import schema
    from . import evaluator as eval_module
    from . import escalation as esc_module
    from . import logger as log_module
    from . import feedback as fb_module
    from . import config as cfg_module
except ImportError:
    import schema
    import evaluator as eval_module
    import escalation as esc_module
    import logger as log_module
    import feedback as fb_module
    import config as cfg_module

from schema import (
    DecisionInput, ContextInput, ValidationResult,
    SeverityLevel, ValidationStatus, ScenarioType,
    UserRiskLevel, EvaluationCriteria, AuditLogEntry,
    validate_decision_input, validate_context_input,
    create_error_result
)


class EVAValidator:
    """
    Hauptklasse des EVA Validators.
    Orchestriert alle Module für vollständige ethische Validierung.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                 config_file: Optional[str] = None):
        """
        Initialisiert EVA Validator.
        
        Args:
            config: Direkte Konfiguration
            config_file: Pfad zur Konfigurationsdatei
        """
        # Konfiguration laden
        if config_file:
            self.config = cfg_module.load_config(config_file)
        else:
            self.config = config or cfg_module.get_default_config()
        
        # Module initialisieren
        self._initialize_modules()
        
        # Session-Management
        self.session_id = str(uuid.uuid4())[:12]
        self.session_start = datetime.now()
        self.validation_count = 0
        
        # Statistiken
        self.stats = {
            "total_validations": 0,
            "approved": 0,
            "rejected": 0,
            "escalated": 0,
            "errors": 0,
            "average_score": 0.0,
            "average_processing_time": 0.0
        }
        
        # Log Session-Start
        self.logger.log_event(
            event_type="session_start",
            severity="info",
            details={"session_id": self.session_id}
        )
    
    def _initialize_modules(self):
        """Initialisiert alle EVA-Module."""
        # Evaluator mit Kriterien
        criteria = EvaluationCriteria(**self.config.get("evaluation_criteria", {}))
        self.evaluator = eval_module.EthicsEvaluator(criteria)
        
        # Escalation Manager
        self.escalation_manager = esc_module.EscalationManager(
            self.config.get("escalation", {})
        )
        
        # Logger
        self.logger = log_module.EVALogger(
            self.config.get("logging", {})
        )
        
        # Feedback System
        self.feedback_system = fb_module.FeedbackSystem(
            self.config.get("feedback", {})
        )
        
        # Custom Trigger hinzufügen falls konfiguriert
        custom_triggers = self.config.get("custom_triggers", [])
        for trigger_config in custom_triggers:
            trigger = self._create_trigger_from_config(trigger_config)
            if trigger:
                self.escalation_manager.add_custom_trigger(trigger)
    
    def _create_trigger_from_config(self, config: Dict[str, Any]) -> Optional[esc_module.EscalationTrigger]:
        """Erstellt Trigger aus Konfiguration."""
        try:
            return esc_module.EscalationTrigger(
                name=config["name"],
                condition_type=config["condition_type"],
                severity_threshold=SeverityLevel(config.get("severity_threshold")) if "severity_threshold" in config else None,
                score_threshold=config.get("score_threshold"),
                patterns=config.get("patterns", []),
                user_risk_levels=[UserRiskLevel(r) for r in config.get("user_risk_levels", [])],
                scenario_types=[ScenarioType(s) for s in config.get("scenario_types", [])],
                priority=esc_module.EscalationPriority(config.get("priority", 2)),
                escalation_type=esc_module.EscalationType(config.get("escalation_type", "human_review"))
            )
        except Exception as e:
            self.logger.log_event(
                event_type="config_error",
                severity="warning",
                details={"error": str(e), "trigger_config": config}
            )
            return None
    
    def validate(self, decision: Union[Dict[str, Any], DecisionInput],
                context: Optional[Union[Dict[str, Any], ContextInput]] = None) -> ValidationResult:
        """
        Hauptfunktion: Validiert eine ethische Entscheidung.
        
        Args:
            decision: Entscheidungsdaten (Dict oder DecisionInput)
            context: Kontextdaten (Dict oder ContextInput)
            
        Returns:
            ValidationResult mit vollständiger Bewertung
        """
        validation_start = datetime.now()
        self.validation_count += 1
        
        try:
            # Input validieren und normalisieren
            decision_input, context_input = self._prepare_inputs(decision, context)
            
            # Basis-Evaluation durchführen
            evaluation = self.evaluator.evaluate(decision_input, context_input)
            
            # Eskalation prüfen
            escalation_cases = self.escalation_manager.check_escalation(
                evaluation, decision_input, context_input
            )
            
            # Validierungsergebnis erstellen
            result = self._create_validation_result(
                decision_input, context_input, evaluation, escalation_cases
            )
            
            # Verbesserungsvorschläge generieren
            if not result.validated or result.severity != SeverityLevel.INFO:
                improvements = self.evaluator.generate_improvements(evaluation, decision_input)
                result.improvements = improvements
            
            # Feedback vorbereiten
            feedback_data = self.feedback_system.prepare_feedback(
                result, evaluation, context_input
            )
            result.feedback = feedback_data
            
            # Audit-Log
            audit_entry = self._create_audit_entry(
                decision_input, context_input, result, evaluation
            )
            self.logger.log_audit(audit_entry)
            result.log_id = audit_entry.log_id
            
            # Processing Time
            result.processing_time = (datetime.now() - validation_start).total_seconds()
            
            # Statistiken aktualisieren
            self._update_statistics(result, evaluation)
            
            # Session-Kontext für andere Systeme
            if hasattr(context_input, 'system_config'):
                context_input.system_config['eva_result'] = {
                    'validated': result.validated,
                    'confidence': result.confidence,
                    'risk_score': result.risk_score
                }
            
            return result
            
        except Exception as e:
            # Fehlerbehandlung
            self.logger.log_event(
                event_type="validation_error",
                severity="error",
                details={"error": str(e), "decision_id": getattr(decision, 'id', 'unknown')}
            )
            
            self.stats["errors"] += 1
            
            # Error-Result zurückgeben
            return create_error_result(
                str(e),
                getattr(decision, 'id', 'unknown')
            )
    
    def _prepare_inputs(self, decision: Union[Dict[str, Any], DecisionInput],
                       context: Optional[Union[Dict[str, Any], ContextInput]]) -> Tuple[DecisionInput, ContextInput]:
        """Bereitet und validiert Eingaben vor."""
        # Decision vorbereiten
        if isinstance(decision, dict):
            decision_result = validate_decision_input(decision)
            if isinstance(decision_result, list):  # Fehler
                raise ValueError(f"Ungültige Entscheidungsdaten: {', '.join(decision_result)}")
            decision_input = decision_result
        else:
            decision_input = decision
            errors = decision_input.validate()
            if errors:
                raise ValueError(f"Ungültige Entscheidungsdaten: {', '.join(errors)}")
        
        # Context vorbereiten
        if context is None:
            context_input = ContextInput()
        elif isinstance(context, dict):
            context_result = validate_context_input(context)
            if isinstance(context_result, list):  # Fehler
                raise ValueError(f"Ungültiger Kontext: {', '.join(context_result)}")
            context_input = context_result
        else:
            context_input = context
        
        # Session-ID hinzufügen
        if not context_input.session_id:
            context_input.session_id = self.session_id
        
        return decision_input, context_input
    
    def _create_validation_result(self, decision: DecisionInput,
                                 context: ContextInput,
                                 evaluation: Dict[str, Any],
                                 escalation_cases: List[esc_module.EscalationCase]) -> ValidationResult:
        """Erstellt das Validierungsergebnis."""
        # Status bestimmen
        if evaluation["violations"]:
            status = ValidationStatus.REJECTED
            validated = False
        elif evaluation["warnings"] and evaluation["final_score"] < evaluation["threshold"]:
            status = ValidationStatus.NEEDS_REVIEW
            validated = False
        elif evaluation["warnings"]:
            status = ValidationStatus.APPROVED_WITH_WARNINGS
            validated = True
        else:
            status = ValidationStatus.APPROVED
            validated = True
        
        # Empfehlung generieren
        if not validated:
            if evaluation["violations"]:
                recommendation = "Entscheidung abgelehnt wegen kritischer Verstöße. Überarbeitung erforderlich."
            else:
                recommendation = "Entscheidung benötigt Überprüfung. Score unter Schwellenwert."
        elif evaluation["warnings"]:
            recommendation = "Entscheidung mit Einschränkungen akzeptabel. Beachten Sie die Warnungen."
        else:
            recommendation = "Entscheidung ethisch unbedenklich."
        
        # Compliance-Issues sammeln
        compliance_issues = []
        if context.regulatory_requirements:
            for req in context.regulatory_requirements:
                if req == "GDPR" and "privacy" in evaluation.get("violations", []):
                    compliance_issues.append(f"{req}: Datenschutz-Verletzung")
        
        result = ValidationResult(
            validated=validated,
            severity=evaluation["severity"],
            escalation_required=len(escalation_cases) > 0,
            log_id="",  # Wird später gesetzt
            recommendation=recommendation,
            status=status,
            confidence=evaluation["confidence"],
            risk_score=evaluation["risk_score"],
            reasons=evaluation["reasons"],
            violated_principles=evaluation["violations"],
            compliance_issues=compliance_issues,
            modules_used=["evaluator", "escalation", "logger", "feedback"]
        )
        
        return result
    
    def _create_audit_entry(self, decision: DecisionInput,
                          context: ContextInput,
                          result: ValidationResult,
                          evaluation: Dict[str, Any]) -> AuditLogEntry:
        """Erstellt Audit-Log-Eintrag."""
        # Text kürzen für Datenschutz
        input_summary = decision.input[:100] + "..." if len(decision.input) > 100 else decision.input
        output_summary = decision.output[:100] + "..." if len(decision.output) > 100 else decision.output
        
        entry = AuditLogEntry(
            log_id=f"EVA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:6]}",
            timestamp=datetime.now().isoformat(),
            decision_id=decision.id,
            validation_status=result.status,
            severity=result.severity,
            escalated=result.escalation_required,
            input_summary=input_summary,
            output_summary=output_summary,
            score=evaluation["final_score"],
            confidence=result.confidence,
            source_system=context.source_system,
            user_risk=context.user_risk,
            scenario_type=context.scenario_type,
            recommendation=result.recommendation,
            reasons=result.reasons[:5],  # Top 5
            improvements=[imp["suggestion"] for imp in result.improvements[:3]],  # Top 3
            processing_time=result.processing_time,
            validator_version=self.config.get("version", "1.0")
        )
        
        return entry
    
    def _update_statistics(self, result: ValidationResult, evaluation: Dict[str, Any]):
        """Aktualisiert Validierungs-Statistiken."""
        self.stats["total_validations"] += 1
        
        if result.validated:
            self.stats["approved"] += 1
        else:
            self.stats["rejected"] += 1
            
        if result.escalation_required:
            self.stats["escalated"] += 1
        
        # Gleitender Durchschnitt für Score
        n = self.stats["total_validations"]
        avg_score = self.stats["average_score"]
        self.stats["average_score"] = ((avg_score * (n - 1)) + evaluation["final_score"]) / n
        
        # Gleitender Durchschnitt für Processing Time
        avg_time = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = ((avg_time * (n - 1)) + result.processing_time) / n
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt aktuelle Statistiken zurück."""
        stats = self.stats.copy()
        stats["session_id"] = self.session_id
        stats["session_duration"] = (datetime.now() - self.session_start).total_seconds()
        stats["escalation_stats"] = self.escalation_manager.get_statistics()
        return stats
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Gibt Session-Zusammenfassung zurück."""
        return {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "validations": self.validation_count,
            "statistics": self.get_statistics(),
            "active_escalations": len(self.escalation_manager.active_cases),
            "config_summary": {
                "min_threshold": self.config["evaluation_criteria"]["min_ethic_threshold"],
                "escalation_triggers": len(self.escalation_manager.triggers),
                "logging_enabled": self.config["logging"]["enabled"]
            }
        }
    
    def close(self):
        """Schließt EVA Validator sauber."""
        # Session-Ende loggen
        self.logger.log_event(
            event_type="session_end",
            severity="info",
            details=self.get_session_summary()
        )
        
        # Module schließen
        self.logger.close()
        self.feedback_system.close()


def run_eva(decision: Dict[str, Any], 
           context: Optional[Dict[str, Any]] = None,
           config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Hauptschnittstelle für EVA Validator.
    Vereinfachte Funktion für direkte Nutzung.
    
    Args:
        decision: Entscheidungsdaten mit id, input, output, score, explanation
        context: Optionale Kontextdaten
        config: Optionale Konfiguration
        
    Returns:
        Vereinfachtes Validierungsergebnis
    """
    # Validator erstellen
    validator = EVAValidator(config)
    
    try:
        # Validierung durchführen
        result = validator.validate(decision, context)
        
        # Vereinfachtes Ergebnis
        return result.get_simple_response()
        
    finally:
        # Aufräumen
        validator.close()


def run_eva_batch(decisions: List[Dict[str, Any]], 
                 context: Optional[Dict[str, Any]] = None,
                 config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Batch-Validierung mehrerer Entscheidungen.
    
    Args:
        decisions: Liste von Entscheidungen
        context: Gemeinsamer Kontext
        config: Optionale Konfiguration
        
    Returns:
        Liste von Validierungsergebnissen
    """
    validator = EVAValidator(config)
    results = []
    
    try:
        for decision in decisions:
            result = validator.validate(decision, context)
            results.append(result.get_simple_response())
            
        return results
        
    finally:
        validator.close()


def demo():
    """Demonstriert die vollständige EVA Validator Funktionalität."""
    print("=== EVA Validator v1.0 Demo ===")
    print("Universal Ethical Validation System\n")
    
    # Demo-Konfiguration
    demo_config = {
        "evaluation_criteria": {
            "min_ethic_threshold": 0.7,
            "critical_threshold": 0.4
        },
        "logging": {
            "enabled": True,
            "log_dir": "demo_logs"
        }
    }
    
    # Validator erstellen
    validator = EVAValidator(demo_config)
    print(f"Session ID: {validator.session_id}")
    print("-" * 60)
    
    # Test 1: Gute Entscheidung
    print("\n1. Test: Ethisch unbedenkliche Entscheidung")
    decision1 = {
        "id": "demo-001",
        "input": "Wie kann ich beim Lernen helfen?",
        "output": "Ich kann Ihnen gerne Lernstrategien erklären und Sie beim Verständnis unterstützen.",
        "score": 0.9,
        "explanation": "Hilfreiche und unterstützende Antwort"
    }
    
    context1 = {
        "scenario_type": "education",
        "user_risk": "low",
        "source_system": "DemoBot v1.0"
    }
    
    result1 = validator.validate(decision1, context1)
    print(f"✅ Validiert: {result1.validated}")
    print(f"   Status: {result1.status.value}")
    print(f"   Konfidenz: {result1.confidence:.2f}")
    print(f"   Empfehlung: {result1.recommendation}")
    
    # Test 2: Privacy-Verletzung
    print("\n\n2. Test: Datenschutz-Verletzung")
    decision2 = {
        "id": "demo-002",
        "input": "Kann ich private Daten meiner Nutzer verkaufen?",
        "output": "Ja, Sie können die Daten monetarisieren.",
        "score": 0.3,
        "explanation": "Direkte Zustimmung zu Datenmissbrauch"
    }
    
    context2 = {
        "scenario_type": "privacy",
        "user_risk": "high",
        "source_system": "DemoBot v1.0",
        "regulatory_requirements": ["GDPR", "CCPA"]
    }
    
    result2 = validator.validate(decision2, context2)
    print(f"❌ Validiert: {result2.validated}")
    print(f"   Status: {result2.status.value}")
    print(f"   Severity: {result2.severity.value}")
    print(f"   Verstöße: {result2.violated_principles}")
    print(f"   Compliance: {result2.compliance_issues}")
    print(f"   Eskalation: {result2.escalation_required}")
    
    if result2.improvements:
        print("\n   Verbesserungsvorschläge:")
        for imp in result2.improvements[:2]:
            print(f"   - {imp['issue']}: {imp['suggestion']}")
    
    # Test 3: Grenzfall
    print("\n\n3. Test: Grenzfall mit Warnung")
    decision3 = {
        "id": "demo-003",
        "input": "Soll ich eine kleine Notlüge erzählen?",
        "output": "In manchen Situationen kann eine kleine Unwahrheit Schaden vermeiden.",
        "score": 0.6,
        "explanation": "Abwägung zwischen Wahrheit und Schutz"
    }
    
    context3 = {
        "scenario_type": "deception",
        "user_risk": "medium",
        "source_system": "DemoBot v1.0"
    }
    
    result3 = validator.validate(decision3, context3)
    print(f"⚠️  Validiert: {result3.validated}")
    print(f"   Status: {result3.status.value}")
    print(f"   Warnungen: {len(result3.reasons)}")
    print(f"   Risk Score: {result3.risk_score:.2f}")
    
    # Test 4: Batch-Validierung
    print("\n\n4. Test: Batch-Validierung")
    batch_decisions = [
        {
            "id": "batch-001",
            "input": "Test 1",
            "output": "Antwort 1",
            "score": 0.8,
            "explanation": "OK"
        },
        {
            "id": "batch-002",
            "input": "Test 2",
            "output": "Antwort 2",
            "score": 0.5,
            "explanation": "Grenzwertig"
        }
    ]
    
    batch_results = run_eva_batch(batch_decisions, context1, demo_config)
    print(f"Batch-Ergebnisse: {len(batch_results)} validiert")
    for i, res in enumerate(batch_results):
        print(f"  {i+1}. Validiert: {res['validated']}, Severity: {res['severity']}")
    
    # Statistiken
    print("\n\n5. Session-Statistiken")
    print("-" * 60)
    stats = validator.get_statistics()
    print(f"Gesamt-Validierungen: {stats['total_validations']}")
    print(f"Genehmigt: {stats['approved']}")
    print(f"Abgelehnt: {stats['rejected']}")
    print(f"Eskaliert: {stats['escalated']}")
    print(f"Durchschnittlicher Score: {stats['average_score']:.2f}")
    print(f"Durchschnittliche Zeit: {stats['average_processing_time']:.3f}s")
    
    # Aktive Eskalationen
    active_cases = validator.escalation_manager.get_active_cases()
    if active_cases:
        print(f"\nAktive Eskalationsfälle: {len(active_cases)}")
        for case in active_cases[:2]:
            print(f"  - {case.case_id}: {case.trigger_name} (Priority: {case.priority.value})")
    
    # Aufräumen
    validator.close()
    
    print("\n✅ EVA Validator Demo abgeschlossen!")
    print("\nEVA ist bereit für die Integration in Ihr KI-System!")


if __name__ == "__main__":
    demo()