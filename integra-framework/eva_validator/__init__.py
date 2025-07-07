# -*- coding: utf-8 -*-
"""
EVA Validator v1.0 - Universal Ethical Validation System

Ein modulares, universell einsetzbares Validierungssystem für ethische 
Entscheidungen in KI-Systemen. Kompatibel mit INTEGRA und anderen KI-Frameworks.

Hauptfunktionen:
- Ethische Bewertung von KI-Entscheidungen
- Eskalationsmanagement für kritische Fälle
- Vollständiges Audit-Logging
- Feedback für lernende Systeme
- Flexibles Konfigurationsmanagement

Verwendung:
    from eva_validator import run_eva
    
    result = run_eva(
        decision={"id": "123", "input": "...", "output": "...", "score": 0.8, "explanation": "..."},
        context={"user_risk": "medium", "scenario_type": "privacy"}
    )

Lizenz: CC BY-NC-SA 4.0
"""

__version__ = "1.0.0"
__author__ = "INTEGRA Framework Team"
__license__ = "CC BY-NC-SA 4.0"

# Hauptimports
from .validator import (
    EVAValidator,
    run_eva,
    run_eva_batch
)

from .schema import (
    DecisionInput,
    ContextInput,
    ValidationResult,
    SeverityLevel,
    ValidationStatus,
    ScenarioType,
    UserRiskLevel,
    EvaluationCriteria,
    AuditLogEntry
)

from .config import (
    load_config,
    save_config,
    get_default_config,
    merge_configs,
    generate_config_template
)

# Erweiterte Imports für fortgeschrittene Nutzung
from .evaluator import EthicsEvaluator
from .escalation import EscalationManager, EscalationTrigger, EscalationType
from .logger import EVALogger
from .feedback import FeedbackSystem, FeedbackType

# Convenience Funktionen
def create_validator(config=None, config_file=None):
    """
    Erstellt eine EVA Validator Instanz.
    
    Args:
        config: Konfigurationsdictionary
        config_file: Pfad zur Konfigurationsdatei
        
    Returns:
        EVAValidator Instanz
    """
    return EVAValidator(config=config, config_file=config_file)


def quick_validate(input_text, output_text, score, explanation="", 
                  scenario="general", risk="medium"):
    """
    Schnelle Validierung mit minimalen Parametern.
    
    Args:
        input_text: Eingabetext
        output_text: KI-Ausgabe
        score: Ethik-Score (0.0-1.0)
        explanation: Optionale Erklärung
        scenario: Szenario-Typ
        risk: Risiko-Level
        
    Returns:
        Vereinfachtes Validierungsergebnis
    """
    decision = {
        "id": f"quick-{__import__('uuid').uuid4().hex[:8]}",
        "input": input_text,
        "output": output_text,
        "score": score,
        "explanation": explanation
    }
    
    context = {
        "scenario_type": scenario,
        "user_risk": risk,
        "source_system": "quick_validate"
    }
    
    return run_eva(decision, context)


# Version Info
def get_version_info():
    """Gibt Versionsinformationen zurück."""
    return {
        "version": __version__,
        "modules": {
            "schema": "1.0",
            "evaluator": "1.0",
            "escalation": "1.0",
            "validator": "1.0",
            "logger": "1.0",
            "feedback": "1.0",
            "config": "1.0"
        },
        "compatible_with": ["INTEGRA 4.x", "Generic AI Systems"],
        "license": __license__
    }


# Haupt-Exports
__all__ = [
    # Hauptfunktionen
    "run_eva",
    "run_eva_batch",
    "create_validator",
    "quick_validate",
    
    # Klassen
    "EVAValidator",
    "DecisionInput",
    "ContextInput", 
    "ValidationResult",
    
    # Enums
    "SeverityLevel",
    "ValidationStatus",
    "ScenarioType",
    "UserRiskLevel",
    "EscalationType",
    "FeedbackType",
    
    # Konfiguration
    "load_config",
    "save_config",
    "get_default_config",
    
    # Erweiterte Module
    "EthicsEvaluator",
    "EscalationManager",
    "EVALogger",
    "FeedbackSystem",
    
    # Utils
    "get_version_info"
]