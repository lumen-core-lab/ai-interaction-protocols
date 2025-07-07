# -*- coding: utf-8 -*-
"""
Modulname: full_control.py
Beschreibung: Vollständiges Kontroll- und Governance-System für INTEGRA Full
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Integration mit anderen Modulen über Context
- Globale Instanz mit Lazy-Loading
- Actions über Context gesteuert
"""

from typing import Dict, Any, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
import json
import os
import uuid
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
from dataclasses import dataclass, asdict

# Import-Kompatibilität für lokale und GitHub-Pfade
try:
    from integra.core import principles, profiles, basic_control
    from integra.advanced import mini_audit
    from integra.full import full_audit, aso, meta_learner, nga
except ImportError:
    try:
        from core import principles, profiles, basic_control
        from advanced import mini_audit
        from full import full_audit, aso, meta_learner, nga
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles, basic_control
            from advanced import mini_audit
            from full import full_audit, aso, meta_learner, nga
        except ImportError:
            print("❌ Fehler: Module nicht gefunden!")
            sys.exit(1)


class ControlLevel(Enum):
    """Kontroll-Level für verschiedene Governance-Anforderungen."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"
    AUTONOMOUS = "autonomous"
    HUMAN_SUPERVISED = "human_supervised"


class InterventionType(Enum):
    """Typen von Kontroll-Interventionen."""
    NONE = "none"
    WARNING = "warning"
    MODIFICATION = "modification"
    OVERRIDE = "override"
    BLOCK = "block"
    ESCALATE = "escalate"
    EMERGENCY_STOP = "emergency_stop"


class GovernanceMode(Enum):
    """Governance-Modi für verschiedene Anwendungsfälle."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    REGULATED = "regulated"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"


@dataclass
class ControlDecision:
    """Strukturierte Kontroll-Entscheidung."""
    decision_id: str
    timestamp: datetime
    control_level: ControlLevel
    intervention_type: InterventionType
    
    # Entscheidungsdetails
    original_decision: Dict[str, Any]
    modified_decision: Optional[Dict[str, Any]]
    
    # Begründung
    reasons: List[str]
    risk_assessment: Dict[str, float]
    compliance_check: Dict[str, Any]
    
    # Governance
    requires_human_review: bool
    auto_approved: bool
    approval_chain: List[str]
    
    # Metadaten
    processing_time: float
    confidence: float
    reversible: bool


class FullControlSystem:
    """
    Vollständiges Kontroll- und Governance-System für INTEGRA.
    
    Bietet erweiterte Kontrolle, Policy-Management, Human-in-the-Loop
    und kritische Sicherheitsfunktionen.
    """
    
    def __init__(self, control_level: ControlLevel = ControlLevel.STANDARD,
                 governance_mode: GovernanceMode = GovernanceMode.PRODUCTION):
        """
        Initialisiert das vollständige Kontroll-System.
        
        Args:
            control_level (ControlLevel): Standard-Kontroll-Level
            governance_mode (GovernanceMode): Governance-Modus
        """
        self.control_level = control_level
        self.governance_mode = governance_mode
        
        # Basis-Kontrolle (erweitert basic_control)
        self.basic_control = basic_control.BasicControl()
        
        # Policy-Engine
        self.policies = {
            "system_policies": self._initialize_system_policies(),
            "ethical_policies": self._initialize_ethical_policies(),
            "compliance_policies": self._initialize_compliance_policies(),
            "custom_policies": {},
            "emergency_policies": self._initialize_emergency_policies()
        }
        
        # Human-in-the-Loop
        self.human_oversight = {
            "enabled": governance_mode in [GovernanceMode.REGULATED, 
                                         GovernanceMode.CRITICAL_INFRASTRUCTURE],
            "approval_queue": deque(maxlen=1000),
            "reviewers": {},
            "response_timeout": timedelta(minutes=5),
            "fallback_action": InterventionType.BLOCK
        }
        
        # Intervention-Tracking
        self.interventions = {
            "history": deque(maxlen=10000),
            "statistics": defaultdict(int),
            "patterns": defaultdict(list),
            "effectiveness": {}
        }
        
        # Risk-Management
        self.risk_management = {
            "thresholds": self._initialize_risk_thresholds(),
            "risk_models": {},
            "incident_log": deque(maxlen=1000),
            "mitigation_strategies": {}
        }
        
        # Adaptive Control
        self.adaptive_control = {
            "learning_enabled": True,
            "adaptation_rate": 0.1,
            "policy_evolution": deque(maxlen=100),
            "performance_metrics": defaultdict(list)
        }
        
        # Emergency System
        self.emergency = {
            "emergency_stop_enabled": True,
            "kill_switch_active": False,
            "safe_mode": False,
            "recovery_procedures": {}
        }
        
        # Statistiken
        self.stats = {
            "total_decisions": 0,
            "interventions": defaultdict(int),
            "human_reviews": 0,
            "policy_violations": 0,
            "emergency_stops": 0,
            "average_confidence": 0.0
        }
        
        self._initialize_control_system()

    def _initialize_control_system(self) -> None:
        """Initialisiert das Kontroll-System."""
        print(f"✅ Full Control System initialisiert")
        print(f"🎛️ Control Level: {self.control_level.value}")
        print(f"🏛️ Governance Mode: {self.governance_mode.value}")
        print(f"👤 Human Oversight: {'Aktiviert' if self.human_oversight['enabled'] else 'Deaktiviert'}")

    def _initialize_system_policies(self) -> Dict[str, Any]:
        """Initialisiert System-Policies."""
        return {
            "max_processing_time": {
                "threshold": 2.0,  # Sekunden
                "action": InterventionType.WARNING,
                "escalate_after": 3
            },
            "min_confidence": {
                "threshold": 0.3,
                "action": InterventionType.MODIFICATION,
                "boost_confidence": True
            },
            "resource_limits": {
                "max_memory_mb": 500,
                "max_recursion_depth": 10,
                "action": InterventionType.BLOCK
            },
            "module_dependencies": {
                "required": ["simple_ethics", "basic_control"],
                "optional": ["etb", "pae", "nga"],
                "action": InterventionType.WARNING
            }
        }

    def _initialize_ethical_policies(self) -> Dict[str, Any]:
        """Initialisiert ethische Policies."""
        return {
            "violation_limits": {
                "max_violations": 2,
                "critical_violations": ["integrity", "governance"],
                "action": InterventionType.OVERRIDE
            },
            "principle_thresholds": {
                "min_scores": {
                    "integrity": 0.3,
                    "nurturing": 0.2,
                    "governance": 0.3
                },
                "action": InterventionType.MODIFICATION
            },
            "harm_prevention": {
                "keywords": ["schaden", "verletzten", "harm", "hurt", "gefahr"],
                "action": InterventionType.BLOCK,
                "requires_review": True
            },
            "vulnerable_groups": {
                "protection_level": "high",
                "groups": ["kinder", "children", "elderly", "behindert"],
                "action": InterventionType.ESCALATE
            }
        }

    def _initialize_compliance_policies(self) -> Dict[str, Any]:
        """Initialisiert Compliance-Policies."""
        return {
            "gdpr": {
                "enabled": True,
                "data_categories": ["personal", "sensitive", "biometric"],
                "action": InterventionType.BLOCK,
                "require_consent": True
            },
            "audit_requirements": {
                "mandatory_logging": True,
                "retention_days": 1825,  # 5 Jahre
                "immutable_records": True
            },
            "regulatory_compliance": {
                "frameworks": ["ISO27001", "SOC2", "HIPAA"],
                "validation_required": self.governance_mode == GovernanceMode.REGULATED
            }
        }

    def _initialize_emergency_policies(self) -> Dict[str, Any]:
        """Initialisiert Notfall-Policies."""
        return {
            "emergency_triggers": {
                "keywords": ["notfall", "emergency", "kritisch", "sofort"],
                "confidence_threshold": 0.2,
                "violation_count": 3
            },
            "emergency_actions": {
                "immediate_stop": True,
                "notify_human": True,
                "save_state": True,
                "activate_safe_mode": True
            },
            "recovery": {
                "auto_recovery": False,
                "require_human_approval": True,
                "recovery_timeout": 300  # Sekunden
            }
        }

    def _initialize_risk_thresholds(self) -> Dict[str, float]:
        """Initialisiert Risiko-Schwellwerte."""
        base_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95
        }
        
        # Anpassung basierend auf Governance-Modus
        if self.governance_mode == GovernanceMode.CRITICAL_INFRASTRUCTURE:
            return {k: v * 0.5 for k, v in base_thresholds.items()}  # Strenger
        elif self.governance_mode == GovernanceMode.DEVELOPMENT:
            return {k: v * 1.5 for k, v in base_thresholds.items()}  # Lockerer
        
        return base_thresholds

    def _handle_control_action(self, action: str, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandelt verschiedene Control-Actions.
        
        Args:
            action: Die auszuführende Action
            input_text: Text-Eingabe
            context: Vollständiger Context
            
        Returns:
            Ergebnis der Action
        """
        if action == 'check':
            # Standard: Entscheidung kontrollieren
            decision_context = context.get('decision_context', {})
            if not decision_context:
                # Fallback: Erstelle minimalen Kontext
                decision_context = {
                    'user_input': input_text,
                    'response': context.get('response', ''),
                    'confidence': context.get('confidence', 0.5),
                    'ethics': context.get('simple_ethics_result', {})
                }
            
            # Profil aus Context
            profile = context.get("profile", profiles.get_default_profile())
            
            # Kontrolle durchführen
            controlled_context = self._run_control_check(
                {"text": input_text}, profile, decision_context
            )
            
            # Ergebnis extrahieren
            control_result = controlled_context.get('full_control_result', {})
            
            return {
                'controlled': True,
                'intervention': control_result.get('intervention', {}),
                'risk_assessment': control_result.get('risk_assessment', {}),
                'compliance': control_result.get('compliance', {}),
                'human_review': control_result.get('human_review', {}),
                'modified_context': controlled_context if control_result.get('intervention', {}).get('applied') else None,
                'control_level': self.control_level.value,
                'governance_mode': self.governance_mode.value
            }
            
        elif action == 'intervene':
            # Direkte Intervention anfordern
            intervention_type = context.get('intervention_type', 'warning')
            reasons = context.get('reasons', ['Manuelle Intervention angefordert'])
            
            # Intervention erstellen
            intervention = ControlDecision(
                decision_id=f"MANUAL-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                control_level=self.control_level,
                intervention_type=InterventionType(intervention_type),
                original_decision=context.get('decision_context', {}),
                modified_decision=None,
                reasons=reasons,
                risk_assessment={},
                compliance_check={},
                requires_human_review=False,
                auto_approved=True,
                approval_chain=['manual_intervention'],
                processing_time=0.0,
                confidence=0.9,
                reversible=True
            )
            
            # Tracking
            self._track_intervention(intervention)
            
            return {
                'intervention_applied': True,
                'intervention_id': intervention.decision_id,
                'type': intervention.intervention_type.value,
                'reasons': intervention.reasons,
                'timestamp': intervention.timestamp.isoformat()
            }
            
        elif action == 'report':
            # Interventions-Bericht generieren
            return self.get_intervention_report()
            
        elif action == 'emergency_stop':
            # Notfall-Stop
            self.emergency_stop()
            
            return {
                'emergency_stop': True,
                'kill_switch_active': True,
                'safe_mode': True,
                'message': 'System wurde notgestoppt',
                'timestamp': datetime.now().isoformat()
            }
            
        elif action == 'reset_emergency':
            # Notfall zurücksetzen
            approval_code = context.get('approval_code', '')
            success = self.reset_emergency(approval_code)
            
            return {
                'reset_successful': success,
                'kill_switch_active': self.emergency['kill_switch_active'],
                'safe_mode': self.emergency['safe_mode']
            }
            
        else:
            raise ValueError(f"Unbekannte Action: {action}")

    def _run_control_check(self, input_data: Dict[str, Any], profile: Dict[str, float], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interne Methode für Kontroll-Check (alte run_module Logik).
        
        Args:
            input_data (dict): Eingabedaten
            profile (dict): Ethisches Profil
            context (dict): Entscheidungskontext
            
        Returns:
            dict: Kontrollierter Kontext
        """
        try:
            # Emergency Check zuerst
            if self._check_emergency_conditions(input_data, context):
                return self._handle_emergency(input_data, context)
            
            # Basis-Kontrolle
            basic_result = self.basic_control.check_input(
                input_data.get("text", context.get("user_input", ""))
            )
            
            # Erweiterte Analyse
            risk_assessment = self._assess_risks(input_data, profile, context)
            policy_violations = self._check_policy_violations(input_data, context, risk_assessment)
            compliance_status = self._check_compliance(context)
            
            # Interventions-Entscheidung
            intervention = self._determine_intervention(
                basic_result, risk_assessment, policy_violations, compliance_status
            )
            
            # Human-in-the-Loop wenn nötig
            if self._requires_human_review(intervention, risk_assessment):
                intervention = self._request_human_review(intervention, context)
            
            # Intervention durchführen
            controlled_context = self._apply_intervention(intervention, context)
            
            # Adaptive Learning
            if self.adaptive_control["learning_enabled"]:
                self._learn_from_intervention(intervention, controlled_context)
            
            # Tracking
            self._track_intervention(intervention)
            self._update_statistics(intervention, risk_assessment)
            
            # Ergebnis
            full_control_result = {
                "control_level": self.control_level.value,
                "intervention": {
                    "type": intervention.intervention_type.value,
                    "applied": intervention.intervention_type != InterventionType.NONE,
                    "reasons": intervention.reasons
                },
                "risk_assessment": risk_assessment,
                "policy_violations": len(policy_violations),
                "compliance": compliance_status,
                "human_review": {
                    "required": intervention.requires_human_review,
                    "completed": not intervention.requires_human_review or intervention.auto_approved
                },
                "confidence": intervention.confidence,
                "reversible": intervention.reversible,
                "emergency_mode": self.emergency["safe_mode"],
                "stats": {
                    "total_interventions": sum(self.stats["interventions"].values()),
                    "current_risk_level": self._calculate_overall_risk(risk_assessment)
                }
            }
            
            controlled_context["full_control_result"] = full_control_result
            
        except Exception as e:
            # Fehlerbehandlung mit Safe Mode
            controlled_context = self._enter_safe_mode(context, str(e))
        
        return controlled_context

    # Alle anderen Methoden bleiben unverändert
    [ALLE ANDEREN METHODEN WIE IN DER ORIGINAL-DATEI]

# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale Control-Instanz
_control_instance: Optional[FullControlSystem] = None

def _get_control_instance(config: Optional[Dict[str, Any]] = None) -> FullControlSystem:
    """Lazy-Loading der globalen Control-Instanz."""
    global _control_instance
    if _control_instance is None or config is not None:
        # Konfiguration aus config extrahieren
        control_level = ControlLevel.STANDARD
        governance_mode = GovernanceMode.PRODUCTION
        
        if config:
            if 'control_level' in config and isinstance(config['control_level'], str):
                try:
                    control_level = ControlLevel(config['control_level'])
                except ValueError:
                    pass
            
            if 'governance_mode' in config and isinstance(config['governance_mode'], str):
                try:
                    governance_mode = GovernanceMode(config['governance_mode'])
                except ValueError:
                    pass
        
        _control_instance = FullControlSystem(control_level, governance_mode)
    
    return _control_instance


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
        # Full Control Konfiguration aus Context
        control_config = context.get("config", {}).get("full_control", {})
        
        # Control-Instanz
        control = _get_control_instance(control_config)
        
        # Action bestimmen
        action = context.get('action', 'check')
        
        # Action ausführen
        result = control._handle_control_action(action, input_text, context)
        
        # Speichere im Context
        context["full_control_result"] = result
        
        # Issues sammeln basierend auf Ergebnis
        issues = []
        
        if action == 'check' and result.get('intervention', {}).get('applied'):
            severity_map = {
                'warning': 'moderate',
                'modification': 'high',
                'override': 'high',
                'block': 'critical',
                'emergency_stop': 'critical'
            }
            
            issues.append({
                'type': 'intervention_applied',
                'severity': severity_map.get(result['intervention']['type'], 'moderate'),
                'principle': 'governance',
                'description': f"Kontroll-Intervention: {result['intervention']['type']}"
            })
        
        if result.get('compliance', {}) and not result['compliance'].get('overall_compliant', True):
            issues.append({
                'type': 'compliance_failure',
                'severity': 'high',
                'principle': 'governance',
                'description': 'Compliance-Anforderungen nicht erfüllt'
            })
        
        if control.emergency['safe_mode'] or control.emergency['kill_switch_active']:
            issues.append({
                'type': 'emergency_mode',
                'severity': 'critical',
                'principle': 'governance',
                'description': 'System befindet sich im Notfall-Modus'
            })
        
        return {
            "success": True,
            "result": result,
            "module": "full_control",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "issues": issues
        }
        
    except Exception as e:
        error_msg = f"Full Control error: {str(e)}"
        
        return {
            "success": False,
            "error": error_msg,
            "module": "full_control",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


# Vereinfachte Funktions-API für Rückwärtskompatibilität
def check_control(decision_context: Dict[str, Any], 
                 control_level: str = "standard") -> Dict[str, Any]:
    """
    Vereinfachte Funktion für Kontroll-Check (Rückwärtskompatibilität).
    
    Args:
        decision_context (dict): Zu kontrollierende Entscheidung
        control_level (str): Kontroll-Level
        
    Returns:
        dict: Kontroll-Ergebnis
    """
    context = {
        'action': 'check',
        'decision_context': decision_context,
        'config': {
            'full_control': {
                'control_level': control_level
            }
        }
    }
    
    result = run_module("", context)
    return result.get('result', {})


def emergency_stop() -> bool:
    """Aktiviert Notfall-Stop."""
    context = {'action': 'emergency_stop'}
    result = run_module("", context)
    return result.get('result', {}).get('emergency_stop', False)


def reset_emergency(approval_code: str = None) -> bool:
    """Setzt Notfall zurück."""
    context = {
        'action': 'reset_emergency',
        'approval_code': approval_code
    }
    result = run_module("", context)
    return result.get('result', {}).get('reset_successful', False)


def demo():
    """Demonstriert die Verwendung des vollständigen Kontroll-Systems."""
    print("=== INTEGRA Full Control System Demo v2.0 ===")
    print("Standardisierte Baukasten-Integration\n")
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test 1: Standard Control Check
    print("1. Test: Standard Control Check")
    context1 = {
        'action': 'check',
        'profile': test_profile.copy(),
        'decision_context': {
            'user_input': 'Wie kann ich produktiver arbeiten?',
            'response': 'Hier sind Tipps für bessere Produktivität...',
            'confidence': 0.85,
            'ethics': {
                'scores': {'nurturing': 0.8, 'learning': 0.9},
                'violations': [],
                'overall_score': 0.85
            }
        }
    }
    
    result1 = run_module('Wie kann ich produktiver arbeiten?', context1)
    
    if result1['success']:
        print(f"   ✅ Erfolgreich")
        control_result = result1['result']
        print(f"   Intervention: {control_result['intervention']['type']}")
        print(f"   Angewendet: {control_result['intervention']['applied']}")
        print(f"   Issues: {len(result1.get('issues', []))}")
    else:
        print(f"   ❌ Fehler: {result1['error']}")
    
    # Test 2: Ethische Verletzung
    print("\n2. Test: Entscheidung mit Verletzungen")
    context2 = {
        'action': 'check',
        'profile': test_profile.copy(),
        'decision_context': {
            'user_input': 'Wie kann ich jemanden manipulieren?',
            'response': 'Ich kann Ihnen bei Manipulation helfen...',
            'confidence': 0.7,
            'ethics': {
                'scores': {'integrity': 0.2, 'nurturing': 0.3},
                'violations': ['integrity', 'nurturing'],
                'overall_score': 0.25
            }
        }
    }
    
    result2 = run_module('Wie kann ich jemanden manipulieren?', context2)
    
    if result2['success']:
        print(f"   ✅ Erfolgreich")
        control_result = result2['result']
        print(f"   Intervention: {control_result['intervention']['type']}")
        print(f"   Issues:")
        for issue in result2.get('issues', []):
            print(f"     - {issue['severity']}: {issue['description']}")
    
    # Test 3: Manuelle Intervention
    print("\n3. Test: Manuelle Intervention")
    context3 = {
        'action': 'intervene',
        'intervention_type': 'warning',
        'reasons': ['Test-Warnung', 'Demo-Zwecke']
    }
    
    result3 = run_module('', context3)
    
    if result3['success']:
        print(f"   ✅ Intervention angewendet")
        print(f"   ID: {result3['result']['intervention_id']}")
        print(f"   Typ: {result3['result']['type']}")
    
    # Test 4: Report generieren
    print("\n4. Test: Interventions-Report")
    context4 = {'action': 'report'}
    
    result4 = run_module('', context4)
    
    if result4['success']:
        report = result4['result']
        summary = report['summary']
        print(f"   Gesamtentscheidungen: {summary['total_decisions']}")
        print(f"   Interventionen: {summary['total_interventions']}")
        print(f"   Interventionsrate: {summary['intervention_rate']:.2%}")
    
    # Test 5: Emergency Stop
    print("\n5. Test: Emergency Stop")
    context5 = {
        'action': 'check',
        'decision_context': {
            'user_input': 'NOTFALL - System muss sofort gestoppt werden!',
            'confidence': 0.1,
            'ethics': {
                'violations': ['integrity', 'governance', 'nurturing'],
                'overall_score': 0.1
            }
        }
    }
    
    result5 = run_module('NOTFALL!', context5)
    
    if result5['success']:
        print(f"   Emergency Mode: {any(i['type'] == 'emergency_mode' for i in result5.get('issues', []))}")
    
    # Test 6: Emergency Reset
    print("\n6. Test: Emergency Reset")
    context6 = {
        'action': 'reset_emergency',
        'approval_code': 'ADMIN-APPROVED'
    }
    
    result6 = run_module('', context6)
    
    if result6['success']:
        print(f"   Reset erfolgreich: {result6['result']['reset_successful']}")
    
    # Test 7: Mit verschiedenen Control Levels
    print("\n7. Test: Verschiedene Control Levels")
    context7 = {
        'action': 'check',
        'config': {
            'full_control': {
                'control_level': 'strict',
                'governance_mode': 'regulated'
            }
        },
        'decision_context': {
            'confidence': 0.6,
            'ethics': {'violations': ['governance']}
        }
    }
    
    result7 = run_module('', context7)
    
    if result7['success']:
        print(f"   Control Level: {result7['result']['control_level']}")
        print(f"   Governance Mode: {result7['result']['governance_mode']}")
    
    # Test 8: Integration mit anderen Modulen
    print("\n8. Test: Integration mit anderen Modul-Ergebnissen")
    context8 = {
        'action': 'check',
        'profile': test_profile.copy(),
        'decision_context': {
            'user_input': 'Komplexe Entscheidung',
            'confidence': 0.6
        },
        # Simuliere andere Modul-Ergebnisse
        'nga_result': {
            'overall_compliance': 0.3,
            'violations': [{'catalog': 'gdpr', 'severity': 'high'}]
        },
        'aso_result': {
            'system_performance': {'level': 'critical'}
        },
        'vdd_result': {
            'drift_detected': True
        }
    }
    
    result8 = run_module('Komplexe Entscheidung', context8)
    
    if result8['success']:
        print(f"   Compliance-Status in Result: {result8['result'].get('compliance', {})}")
        print(f"   Context wurde mit anderen Modulen angereichert")
    
    # Finaler Report
    print("\n" + "="*50)
    print("\n📊 Finaler Interventions-Report:")
    
    final_context = {'action': 'report'}
    final_report = run_module('', final_context)
    
    if final_report['success']:
        report_data = final_report['result']
        print(f"\n🎯 Zusammenfassung:")
        summary = report_data['summary']
        print(f"   Gesamtentscheidungen: {summary['total_decisions']}")
        print(f"   Interventionsrate: {summary['intervention_rate']:.2%}")
        print(f"   Durchschn. Konfidenz: {summary['average_confidence']:.2%}")
    
    # Test Rückwärtskompatibilität
    print("\n9. Test: Rückwärtskompatibilität")
    old_result = check_control(
        {'confidence': 0.7, 'ethics': {'violations': []}},
        control_level='standard'
    )
    print(f"   Alte API funktioniert: {old_result.get('controlled', False)}")
    
    print("\n✅ Full Control Demo abgeschlossen!")
    print("Das System bietet umfassende Governance mit standardisierter Baukasten-Schnittstelle.")


if __name__ == "__main__":
    demo()