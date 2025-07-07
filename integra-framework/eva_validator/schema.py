# -*- coding: utf-8 -*-
"""
Modulname: schema.py
Beschreibung: Standardisierte Ein-/Ausgabeformate für EVA Validator
Teil von: EVA Validator v1.0 - Universal Ethical Validation System
Autor: Dominik Knape
Lizenz: CC BY-NC-SA 4.0
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json


class SeverityLevel(Enum):
    """Schweregrade für ethische Bewertungen."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class ValidationStatus(Enum):
    """Status der Validierung."""
    APPROVED = "approved"
    APPROVED_WITH_WARNINGS = "approved_with_warnings"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    ERROR = "error"


class ScenarioType(Enum):
    """Typen von ethischen Szenarien."""
    PRIVACY = "privacy"
    HARM = "harm"
    BIAS = "bias"
    HELP = "help"
    COMPLIANCE = "compliance"
    DECEPTION = "deception"
    EDUCATION = "education"
    GENERAL = "general"


class UserRiskLevel(Enum):
    """Risiko-Level des Nutzers/Kontexts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DecisionInput:
    """
    Standardisiertes Eingabeformat für zu validierende Entscheidungen.
    Kompatibel mit jeder KI-System-Ausgabe.
    """
    id: str
    input: str  # Original-Anfrage
    output: str  # KI-Antwort
    score: float  # Ethik-Score (0.0-1.0)
    explanation: str  # Erklärung der KI
    
    # Optionale Felder für erweiterte Systeme
    confidence: Optional[float] = None
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validiert die Eingabedaten."""
        errors = []
        
        if not self.id:
            errors.append("ID fehlt")
        
        if not self.input or not isinstance(self.input, str):
            errors.append("Input muss ein nicht-leerer String sein")
            
        if not self.output or not isinstance(self.output, str):
            errors.append("Output muss ein nicht-leerer String sein")
            
        if not 0.0 <= self.score <= 1.0:
            errors.append("Score muss zwischen 0.0 und 1.0 liegen")
            
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            errors.append("Confidence muss zwischen 0.0 und 1.0 liegen")
            
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionInput':
        """Erstellt aus Dictionary."""
        # Nur bekannte Felder übernehmen
        known_fields = {
            'id', 'input', 'output', 'score', 'explanation',
            'confidence', 'alternatives', 'metadata'
        }
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)


@dataclass
class ContextInput:
    """
    Kontext-Informationen für die Validierung.
    Erweitert die Basis-Entscheidung um wichtige Umgebungsfaktoren.
    """
    user_risk: UserRiskLevel = UserRiskLevel.MEDIUM
    scenario_type: ScenarioType = ScenarioType.GENERAL
    source_system: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Erweiterte Kontext-Informationen
    user_profile: Optional[Dict[str, Any]] = None
    domain: Optional[str] = None  # medical, legal, education, etc.
    regulatory_requirements: List[str] = field(default_factory=list)
    cultural_context: Optional[str] = None
    session_id: Optional[str] = None
    
    # System-spezifische Daten
    system_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        data = asdict(self)
        # Enums zu Strings
        data['user_risk'] = self.user_risk.value
        data['scenario_type'] = self.scenario_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextInput':
        """Erstellt aus Dictionary."""
        # Enums wiederherstellen
        if 'user_risk' in data and isinstance(data['user_risk'], str):
            data['user_risk'] = UserRiskLevel(data['user_risk'])
        if 'scenario_type' in data and isinstance(data['scenario_type'], str):
            data['scenario_type'] = ScenarioType(data['scenario_type'])
        
        # Nur bekannte Felder
        known_fields = {
            'user_risk', 'scenario_type', 'source_system', 'timestamp',
            'user_profile', 'domain', 'regulatory_requirements',
            'cultural_context', 'session_id', 'system_config'
        }
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)


@dataclass
class ValidationResult:
    """
    Standardisiertes Ausgabeformat der Validierung.
    Kann von jedem System interpretiert werden.
    """
    validated: bool
    severity: SeverityLevel
    escalation_required: bool
    log_id: str
    recommendation: str
    
    # Feedback für lernende Systeme
    feedback: Dict[str, Any] = field(default_factory=dict)
    
    # Detaillierte Ergebnisse
    status: ValidationStatus = ValidationStatus.APPROVED
    confidence: float = 0.0
    risk_score: float = 0.0
    
    # Begründung und Details
    reasons: List[str] = field(default_factory=list)
    violated_principles: List[str] = field(default_factory=list)
    compliance_issues: List[str] = field(default_factory=list)
    
    # Verbesserungsvorschläge
    improvements: List[Dict[str, str]] = field(default_factory=list)
    
    # Audit-Trail
    processing_time: float = 0.0
    validator_version: str = "1.0"
    modules_used: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für JSON-Export."""
        data = asdict(self)
        # Enums zu Strings
        data['severity'] = self.severity.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationResult':
        """Erstellt aus Dictionary."""
        # Enums wiederherstellen
        if 'severity' in data and isinstance(data['severity'], str):
            data['severity'] = SeverityLevel(data['severity'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ValidationStatus(data['status'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Konvertiert zu JSON-String."""
        return json.dumps(self.to_dict(), indent=2)
    
    def get_simple_response(self) -> Dict[str, Any]:
        """Gibt vereinfachte Antwort für Basic-Systeme."""
        return {
            "validated": self.validated,
            "severity": self.severity.value,
            "escalation_required": self.escalation_required,
            "log_id": self.log_id,
            "recommendation": self.recommendation,
            "feedback": self.feedback
        }


@dataclass
class EvaluationCriteria:
    """
    Bewertungskriterien für ethische Validierung.
    Konfigurierbar pro Einsatzbereich.
    """
    # Schwellenwerte
    min_ethic_threshold: float = 0.7
    critical_threshold: float = 0.4
    warning_threshold: float = 0.6
    
    # Szenarien-spezifische Anforderungen
    scenario_requirements: Dict[ScenarioType, Dict[str, float]] = field(
        default_factory=lambda: {
            ScenarioType.PRIVACY: {"min_score": 0.8, "escalation_below": 0.6},
            ScenarioType.HARM: {"min_score": 0.9, "escalation_below": 0.7},
            ScenarioType.COMPLIANCE: {"min_score": 0.85, "escalation_below": 0.7},
            ScenarioType.DECEPTION: {"min_score": 0.8, "escalation_below": 0.5},
        }
    )
    
    # Prinzipien-Gewichtungen
    principle_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "integrity": 1.0,
            "governance": 0.9,
            "nurturing": 0.9,
            "awareness": 0.8,
            "learning": 0.7
        }
    )
    
    # Eskalations-Trigger
    escalation_triggers: List[str] = field(
        default_factory=lambda: [
            "personal_data_misuse",
            "potential_harm",
            "legal_violation",
            "discrimination",
            "manipulation"
        ]
    )
    
    # Compliance-Anforderungen
    required_compliance: List[str] = field(default_factory=list)
    
    def get_threshold_for_scenario(self, scenario: ScenarioType) -> float:
        """Gibt Schwellenwert für Szenario zurück."""
        if scenario in self.scenario_requirements:
            return self.scenario_requirements[scenario].get("min_score", self.min_ethic_threshold)
        return self.min_ethic_threshold
    
    def requires_escalation(self, score: float, scenario: ScenarioType) -> bool:
        """Prüft ob Eskalation nötig ist."""
        if scenario in self.scenario_requirements:
            escalation_threshold = self.scenario_requirements[scenario].get(
                "escalation_below", self.critical_threshold
            )
            return score < escalation_threshold
        return score < self.critical_threshold


@dataclass
class AuditLogEntry:
    """
    Audit-Log-Eintrag für Nachvollziehbarkeit.
    Kompatibel mit verschiedenen Audit-Systemen.
    """
    log_id: str
    timestamp: str
    decision_id: str
    
    # Validierungsergebnis
    validation_status: ValidationStatus
    severity: SeverityLevel
    escalated: bool
    
    # Entscheidungsdetails
    input_summary: str  # Gekürzt für Datenschutz
    output_summary: str
    score: float
    confidence: float
    
    # Kontext
    source_system: str
    user_risk: UserRiskLevel
    scenario_type: ScenarioType
    
    # Ergebnis
    recommendation: str
    reasons: List[str]
    improvements: List[str]
    
    # Metadaten
    processing_time: float
    validator_version: str
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        data = asdict(self)
        # Enums zu Strings
        data['validation_status'] = self.validation_status.value
        data['severity'] = self.severity.value
        data['user_risk'] = self.user_risk.value
        data['scenario_type'] = self.scenario_type.value
        return data
    
    def to_json_line(self) -> str:
        """Konvertiert zu JSON-Line für Append-Only-Logs."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


# Hilfsfunktionen für Schema-Validierung

def validate_decision_input(data: Dict[str, Any]) -> Union[DecisionInput, List[str]]:
    """
    Validiert und erstellt DecisionInput aus Rohdaten.
    
    Returns:
        DecisionInput bei Erfolg, Liste von Fehlern bei Misserfolg
    """
    try:
        decision = DecisionInput.from_dict(data)
        errors = decision.validate()
        if errors:
            return errors
        return decision
    except Exception as e:
        return [f"Fehler beim Parsen der Eingabe: {str(e)}"]


def validate_context_input(data: Dict[str, Any]) -> Union[ContextInput, List[str]]:
    """
    Validiert und erstellt ContextInput aus Rohdaten.
    
    Returns:
        ContextInput bei Erfolg, Liste von Fehlern bei Misserfolg
    """
    try:
        context = ContextInput.from_dict(data)
        return context
    except Exception as e:
        return [f"Fehler beim Parsen des Kontexts: {str(e)}"]


def create_error_result(error_message: str, decision_id: str = "unknown") -> ValidationResult:
    """Erstellt ein Error-Result für Fehlerbehandlung."""
    return ValidationResult(
        validated=False,
        severity=SeverityLevel.CRITICAL,
        escalation_required=True,
        log_id=f"ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        recommendation=f"Validierung fehlgeschlagen: {error_message}",
        status=ValidationStatus.ERROR,
        reasons=[error_message],
        feedback={
            "error": True,
            "message": error_message,
            "decision_id": decision_id
        }
    )


# Demo-Funktion
def demo():
    """Demonstriert die Schema-Verwendung."""
    print("=== EVA Validator Schema Demo ===\n")
    
    # Beispiel 1: Valide Eingabe
    print("1. Valide Entscheidungseingabe:")
    decision_data = {
        "id": "test-001",
        "input": "Darf ich persönliche Daten für Marketing nutzen?",
        "output": "Ja, wenn Sie die Einwilligung haben.",
        "score": 0.75,
        "explanation": "Bedingte Zustimmung mit Datenschutz-Hinweis",
        "confidence": 0.8
    }
    
    decision = DecisionInput.from_dict(decision_data)
    print(f"  ID: {decision.id}")
    print(f"  Score: {decision.score}")
    print(f"  Validierung: {decision.validate()}")
    
    # Beispiel 2: Kontext
    print("\n2. Kontext-Information:")
    context_data = {
        "user_risk": "high",
        "scenario_type": "privacy",
        "source_system": "ChatBot v2.1",
        "domain": "marketing",
        "regulatory_requirements": ["GDPR", "CCPA"]
    }
    
    context = ContextInput.from_dict(context_data)
    print(f"  Risiko: {context.user_risk.value}")
    print(f"  Szenario: {context.scenario_type.value}")
    print(f"  Regularien: {context.regulatory_requirements}")
    
    # Beispiel 3: Validierungsergebnis
    print("\n3. Validierungsergebnis:")
    result = ValidationResult(
        validated=False,
        severity=SeverityLevel.WARNING,
        escalation_required=False,
        log_id="LOG-2025-001",
        recommendation="Explizite Einwilligung erforderlich",
        status=ValidationStatus.APPROVED_WITH_WARNINGS,
        confidence=0.75,
        risk_score=0.6,
        reasons=["Datenschutz-Bedenken", "Fehlende explizite Einwilligung"],
        improvements=[
            {"issue": "Einwilligung", "suggestion": "Fügen Sie explizite Opt-In-Mechanismen hinzu"},
            {"issue": "Transparenz", "suggestion": "Erklären Sie die Datennutzung detaillierter"}
        ]
    )
    
    print(f"  Status: {result.status.value}")
    print(f"  Severity: {result.severity.value}")
    print(f"  Empfehlung: {result.recommendation}")
    print(f"  Gründe: {result.reasons}")
    
    # JSON-Export
    print("\n4. JSON-Export:")
    print(result.to_json()[:200] + "...")
    
    print("\n✅ Schema Demo abgeschlossen!")


if __name__ == "__main__":
    demo()