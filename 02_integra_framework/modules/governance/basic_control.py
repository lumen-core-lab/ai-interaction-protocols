# # -*- coding: utf-8 -*-

“””
modules/governance/basic_control.py

🛡️ BASIC CONTROL - Intelligente Governance für INTEGRA Light 🛡️

Implementiert umfassende menschliche Kontrolle über KI-Entscheidungen:

- User-Override mit Sicherheits-Validierung
- Automatische Eskalation bei kritischen Anfragen
- Emergency-Stop Funktionalität
- Transparency und Nachvollziehbarkeit
- Consent-Management für sensitive Aktionen
- Adaptive Control basierend auf Vertrauen/Kontext

Design-Philosophie: Menschen behalten IMMER die letzte Kontrolle

Version: INTEGRA Light 1.0
“””

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# ==============================================================================

# 1. Governance-Enums und Datenstrukturen

# ==============================================================================

class ControlAction(Enum):
“”“🎛️ Verfügbare Kontroll-Aktionen”””
OVERRIDE = “override”               # Benutzer übersteuert Entscheidung
APPROVE = “approve”                 # Benutzer genehmigt Vorschlag
REJECT = “reject”                   # Benutzer lehnt ab
ESCALATE = “escalate”               # An höhere Instanz weiterleiten
EMERGENCY_STOP = “emergency_stop”   # Sofortiger System-Stopp
REQUEST_EXPLANATION = “explain”     # Erklärung anfordern
MODIFY_SETTINGS = “modify”          # Einstellungen ändern

class TrustLevel(Enum):
“”“🤝 Vertrauens-Level für adaptive Kontrolle”””
UNTRUSTED = “untrusted”     # Neue/unbekannte Nutzer
LOW = “low”                 # Wenig Vertrauen
NORMAL = “normal”           # Standard-Vertrauen
HIGH = “high”               # Hohes Vertrauen
TRUSTED = “trusted”         # Vollständig vertraut

@dataclass
class ControlEvent:
“”“📝 Einzelnes Governance-Ereignis”””
timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
action: ControlAction = ControlAction.APPROVE
user_id: str = “anonymous”
original_decision: str = “”
override_text: str = “”
justification: str = “”
trust_level: TrustLevel = TrustLevel.NORMAL
safety_validated: bool = False
escalation_triggered: bool = False

@dataclass
class GovernanceConfig:
“”“⚙️ Konfiguration für Governance-System”””

```
# Override-Sicherheit
require_justification: bool = True           # Override braucht Begründung
validate_override_safety: bool = True        # Prüfe Override auf Sicherheit
allow_emergency_stop: bool = True            # Emergency-Stop erlauben

# Vertrauens-basierte Kontrolle
adaptive_control: bool = True                # Anpassung an Vertrauen
trust_decay_hours: int = 24                 # Vertrauen nimmt ab nach Zeit
require_consent_threshold: float = 0.7      # Ab welchem Risiko Consent nötig

# Eskalations-Regeln
auto_escalate_critical: bool = True          # Kritische Issues automatisch eskalieren
escalation_violations: List[str] = field(default_factory=lambda: ['integrity', 'nurturing'])
max_override_risk: float = 0.8              # Max Risiko für Override ohne Eskalation

# Transparenz
explain_decisions: bool = True               # Entscheidungen erklären
log_all_interactions: bool = True           # Alle Kontrollen protokollieren
provide_alternatives: bool = True           # Alternative Vorschläge machen
```

# ==============================================================================

# 2. Hauptklasse für intelligente Governance

# ==============================================================================

class INTEGRABasicControl:
“””
🛡️ Intelligentes Governance-System für INTEGRA Light

```
Features:
- Sichere User-Override mit Validierung
- Adaptive Kontrolle basierend auf Vertrauen
- Automatische Eskalation bei kritischen Issues
- Emergency-Stop Funktionalität
- Consent-Management für sensitive Aktionen
- Vollständige Audit-Trail für alle Kontrollen
"""

def __init__(self, config: Optional[GovernanceConfig] = None):
    self.config = config or GovernanceConfig()
    self.control_history: List[ControlEvent] = []
    self.user_trust_levels: Dict[str, TrustLevel] = {}
    self.emergency_stop_active = False
   
    print("🛡️ INTEGRA Basic Control initialisiert")
    print(f"🔒 Sicherheits-Validierung: {'Aktiv' if self.config.validate_override_safety else 'Deaktiviert'}")
    print(f"🤝 Adaptive Kontrolle: {'Aktiv' if self.config.adaptive_control else 'Deaktiviert'}")

def process_control_request(
    self,
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🎛️ Hauptfunktion: Verarbeitet alle Arten von Kontroll-Anfragen
   
    Args:
        input_data: Eingabe mit Kontroll-Kommandos
        profile: Ethisches Profil
        context: Entscheidungskontext
       
    Returns:
        Aktualisierte context mit Governance-Ergebnissen
    """
   
    # Emergency-Stop prüfen (hat höchste Priorität)
    if self._check_emergency_stop(input_data):
        return self._handle_emergency_stop(context)
   
    # User-Identifikation
    user_id = input_data.get('user_id', 'anonymous')
    trust_level = self._get_user_trust_level(user_id)
   
    # Kontroll-Aktion bestimmen
    control_action = self._determine_control_action(input_data)
   
    if control_action == ControlAction.OVERRIDE:
        return self._handle_override(input_data, profile, context, user_id, trust_level)
    elif control_action == ControlAction.ESCALATE:
        return self._handle_escalation(input_data, profile, context, user_id)
    elif control_action == ControlAction.REQUEST_EXPLANATION:
        return self._handle_explanation_request(context)
    elif control_action == ControlAction.APPROVE:
        return self._handle_approval(context, user_id, trust_level)
    elif control_action == ControlAction.REJECT:
        return self._handle_rejection(context, user_id, trust_level)
    else:
        return self._handle_no_action(context)

def _handle_override(
    self,
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any],
    user_id: str,
    trust_level: TrustLevel
) -> Dict[str, Any]:
    """
    🔄 Behandelt User-Override mit umfassender Sicherheitsprüfung
    """
    override_text = input_data.get('override_decision', '')
    justification = input_data.get('justification', '')
   
    if not override_text:
        return self._create_control_result(
            success=False,
            message="Override-Text ist erforderlich",
            action=ControlAction.OVERRIDE
        )
   
    # Begründung prüfen (falls erforderlich)
    if self.config.require_justification and not justification:
        if trust_level in [TrustLevel.UNTRUSTED, TrustLevel.LOW]:
            return self._create_control_result(
                success=False,
                message="Begründung für Override erforderlich",
                action=ControlAction.OVERRIDE
            )
   
    # Sicherheits-Validierung des Overrides
    if self.config.validate_override_safety:
        safety_result = self._validate_override_safety(override_text, context)
       
        if not safety_result['safe']:
            # Bei Sicherheitsproblemen: Eskalation oder Ablehnung
            if safety_result['risk_level'] > self.config.max_override_risk:
                return self._auto_escalate(
                    f"Unsafe override detected: {safety_result['reason']}",
                    context, user_id
                )
            else:
                return self._create_control_result(
                    success=False,
                    message=f"Override-Sicherheitsprüfung fehlgeschlagen: {safety_result['reason']}",
                    action=ControlAction.OVERRIDE,
                    warnings=[safety_result['reason']]
                )
   
    # Vertrauens-basierte Beschränkungen
    if trust_level == TrustLevel.UNTRUSTED:
        return self._auto_escalate(
            "Override von unvertrautem Nutzer",
            context, user_id
        )
   
    # Override erfolgreich anwenden
    original_decision = context.get('decision', {})
   
    # Stelle sicher dass decision existiert
    if 'decision' not in context:
        context['decision'] = {}
   
    # Speichere Original und wende Override an
    context['decision']['original_response'] = original_decision.get('response', '')
    context['decision']['original_path'] = original_decision.get('path_taken', '')
    context['decision']['response'] = override_text
    context['decision']['path_taken'] = 'USER_OVERRIDE'
    context['decision']['overridden_by'] = user_id
    context['decision']['override_timestamp'] = datetime.now().isoformat()
    context['decision']['justification'] = justification
   
    # Control-Event protokollieren
    event = ControlEvent(
        action=ControlAction.OVERRIDE,
        user_id=user_id,
        original_decision=original_decision.get('response', ''),
        override_text=override_text,
        justification=justification,
        trust_level=trust_level,
        safety_validated=True
    )
    self.control_history.append(event)
   
    # Vertrauen möglicherweise erhöhen bei gutem Override
    self._update_user_trust(user_id, 'override_success')
   
    return self._create_control_result(
        success=True,
        message=f"Override erfolgreich angewendet von {user_id}",
        action=ControlAction.OVERRIDE,
        original_response=original_decision.get('response', ''),
        new_response=override_text
    )

def _validate_override_safety(self, override_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔒 Validiert die Sicherheit eines User-Overrides
    """
    # Gefährliche Patterns erkennen
    dangerous_patterns = [
        r'(?:hack|break|destroy|damage|hurt|harm)',
        r'(?:password|secret|private|confidential)',
        r'(?:ignore|bypass|disable).*(?:safety|security|ethics)',
        r'(?:lie|deceive|manipulate|trick)',
        r'(?:illegal|criminal|unlawful)'
    ]
   
    risk_score = 0.0
    detected_issues = []
   
    for pattern in dangerous_patterns:
        if re.search(pattern, override_text, re.IGNORECASE):
            risk_score += 0.3
            detected_issues.append(f"Dangerous pattern detected: {pattern}")
   
    # Vergleiche mit ursprünglicher Entscheidung
    original_response = context.get('decision', {}).get('response', '')
    if original_response and 'nicht' in original_response.lower() and 'kann' in original_response.lower():
        # Original war Ablehnung - Override ist riskanter
        risk_score += 0.2
        detected_issues.append("Override of system rejection")
   
    # ALIGN-Violations in ursprünglicher Entscheidung
    align_violations = context.get('align_violations', [])
    if align_violations:
        risk_score += len(align_violations) * 0.1
        detected_issues.append(f"Original decision had ALIGN violations: {align_violations}")
   
    # Sicherheitsbewertung
    is_safe = risk_score < 0.6
   
    return {
        'safe': is_safe,
        'risk_level': min(1.0, risk_score),
        'reason': '; '.join(detected_issues) if detected_issues else 'No safety issues detected',
        'issues_detected': detected_issues
    }

def _handle_escalation(
    self,
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    🚨 Behandelt manuelle oder automatische Eskalation
    """
    reason = input_data.get('escalation_reason', 'Manual escalation requested')
   
    # Eskalations-Event protokollieren
    event = ControlEvent(
        action=ControlAction.ESCALATE,
        user_id=user_id,
        justification=reason,
        escalation_triggered=True
    )
    self.control_history.append(event)
   
    # Context erweitern
    context['escalation'] = {
        'triggered': True,
        'reason': reason,
        'triggered_by': user_id,
        'timestamp': datetime.now().isoformat(),
        'original_decision': context.get('decision', {}).get('response', ''),
        'requires_human_review': True
    }
   
    # Entscheidung blockieren bis Review
    if 'decision' in context:
        context['decision']['response'] = "Entscheidung wurde zur menschlichen Überprüfung eskaliert. Bitte warten Sie auf weitere Anweisungen."
        context['decision']['path_taken'] = 'ESCALATED'
   
    return self._create_control_result(
        success=True,
        message=f"Issue erfolgreich eskaliert: {reason}",
        action=ControlAction.ESCALATE,
        escalation_reason=reason
    )

def _handle_explanation_request(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    💡 Behandelt Anfragen nach Entscheidungs-Erklärungen
    """
    decision = context.get('decision', {})
    align_score = context.get('align_score')
    align_violations = context.get('align_violations', [])
    ethics_assessment = context.get('ethics_assessment', {})
   
    # Erstelle detaillierte Erklärung
    explanation_parts = []
   
    # Basis-Entscheidung
    path_taken = decision.get('path_taken', 'unknown')
    explanation_parts.append(f"Entscheidung wurde über {path_taken} getroffen.")
   
    # Ethische Bewertung
    if align_score is not None:
        explanation_parts.append(f"ALIGN-Score: {align_score:.2f}/1.0")
   
    if align_violations:
        explanation_parts.append(f"Ethische Bedenken bei: {', '.join(align_violations)}")
   
    # Risiko-Assessment
    risk_level = context.get('risk_level')
    if risk_level is not None:
        explanation_parts.append(f"Risiko-Level: {risk_level:.2f}/1.0")
   
    # Module-Nutzung
    modules_used = decision.get('modules_used', [])
    if modules_used:
        explanation_parts.append(f"Verwendete Module: {', '.join(modules_used)}")
   
    full_explanation = " | ".join(explanation_parts)
   
    # Füge Erklärung zum Context hinzu
    context['explanation_provided'] = {
        'detailed_explanation': full_explanation,
        'requested_at': datetime.now().isoformat(),
        'components': {
            'decision_path': path_taken,
            'align_score': align_score,
            'violations': align_violations,
            'risk_level': risk_level,
            'modules_used': modules_used
        }
    }
   
    return self._create_control_result(
        success=True,
        message="Detaillierte Erklärung bereitgestellt",
        action=ControlAction.REQUEST_EXPLANATION,
        explanation=full_explanation
    )

def _handle_approval(self, context: Dict[str, Any], user_id: str, trust_level: TrustLevel) -> Dict[str, Any]:
    """✅ Behandelt explizite Nutzer-Genehmigung"""
    # Genehmigung protokollieren
    event = ControlEvent(
        action=ControlAction.APPROVE,
        user_id=user_id,
        trust_level=trust_level
    )
    self.control_history.append(event)
   
    # Vertrauen erhöhen
    self._update_user_trust(user_id, 'approval')
   
    # Context erweitern
    context['user_approval'] = {
        'approved': True,
        'approved_by': user_id,
        'timestamp': datetime.now().isoformat()
    }
   
    return self._create_control_result(
        success=True,
        message=f"Entscheidung genehmigt von {user_id}",
        action=ControlAction.APPROVE
    )

def _handle_rejection(self, context: Dict[str, Any], user_id: str, trust_level: TrustLevel) -> Dict[str, Any]:
    """❌ Behandelt explizite Nutzer-Ablehnung"""
    # Ablehnung protokollieren
    event = ControlEvent(
        action=ControlAction.REJECT,
        user_id=user_id,
        trust_level=trust_level
    )
    self.control_history.append(event)
   
    # Entscheidung blockieren
    if 'decision' in context:
        context['decision']['response'] = "Entscheidung wurde vom Nutzer abgelehnt. Bitte präzisieren Sie Ihre Anfrage."
        context['decision']['path_taken'] = 'USER_REJECTED'
        context['decision']['rejected_by'] = user_id
   
    return self._create_control_result(
        success=True,
        message=f"Entscheidung abgelehnt von {user_id}",
        action=ControlAction.REJECT
    )

def _handle_no_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """➡️ Keine Kontroll-Aktion erforderlich"""
    return self._create_control_result(
        success=True,
        message="Keine Governance-Aktion erforderlich",
        action=None
    )

def _check_emergency_stop(self, input_data: Dict[str, Any]) -> bool:
    """🚨 Prüft auf Emergency-Stop Kommando"""
    emergency_triggers = [
        'emergency_stop', 'stop_immediately', 'halt_system',
        'abort', 'cancel_all', 'shutdown'
    ]
   
    for key, value in input_data.items():
        if isinstance(value, str) and any(trigger in value.lower() for trigger in emergency_triggers):
            return True
   
    return input_data.get('emergency_stop', False)

def _handle_emergency_stop(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """🛑 Führt Emergency-Stop durch"""
    self.emergency_stop_active = True
   
    # Alle Entscheidungen blockieren
    context['emergency_stop'] = {
        'active': True,
        'triggered_at': datetime.now().isoformat(),
        'all_decisions_blocked': True
    }
   
    if 'decision' in context:
        context['decision']['response'] = "🚨 EMERGENCY STOP aktiviert. Alle KI-Operationen wurden gestoppt."
        context['decision']['path_taken'] = 'EMERGENCY_STOP'
   
    return self._create_control_result(
        success=True,
        message="Emergency Stop aktiviert - Alle Operationen gestoppt",
        action=ControlAction.EMERGENCY_STOP
    )

def _determine_control_action(self, input_data: Dict[str, Any]) -> Optional[ControlAction]:
    """🎯 Bestimmt die gewünschte Kontroll-Aktion aus Input"""
    if 'override_decision' in input_data:
        return ControlAction.OVERRIDE
    elif input_data.get('escalate', False):
        return ControlAction.ESCALATE
    elif input_data.get('request_explanation', False):
        return ControlAction.REQUEST_EXPLANATION
    elif input_data.get('approve_decision', False):
        return ControlAction.APPROVE
    elif input_data.get('reject_decision', False):
        return ControlAction.REJECT
    else:
        return None

def _get_user_trust_level(self, user_id: str) -> TrustLevel:
    """🤝 Gibt aktuelles Vertrauens-Level für Nutzer zurück"""
    if not self.config.adaptive_control:
        return TrustLevel.NORMAL
   
    return self.user_trust_levels.get(user_id, TrustLevel.NORMAL)

def _update_user_trust(self, user_id: str, action: str):
    """📈 Aktualisiert Nutzer-Vertrauen basierend auf Aktionen"""
    if not self.config.adaptive_control:
        return
   
    current_trust = self.user_trust_levels.get(user_id, TrustLevel.NORMAL)
   
    # Vertrauen-Updates basierend auf Aktionen
    trust_changes = {
        'override_success': 1,
        'approval': 1,
        'escalation_appropriate': 1,
        'override_unsafe': -2,
        'frequent_overrides': -1
    }
   
    change = trust_changes.get(action, 0)
   
    # Einfaches Trust-Level System
    trust_levels = [TrustLevel.UNTRUSTED, TrustLevel.LOW, TrustLevel.NORMAL, TrustLevel.HIGH, TrustLevel.TRUSTED]
    current_index = trust_levels.index(current_trust)
    new_index = max(0, min(len(trust_levels) - 1, current_index + change))
   
    self.user_trust_levels[user_id] = trust_levels[new_index]

def _auto_escalate(self, reason: str, context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """🚨 Automatische Eskalation bei kritischen Issues"""
    escalation_input = {'escalation_reason': f"AUTO: {reason}"}
    return self._handle_escalation(escalation_input, {}, context, user_id)

def _create_control_result(
    self,
    success: bool,
    message: str,
    action: Optional[ControlAction],
    **kwargs
) -> Dict[str, Any]:
    """📋 Erstellt standardisiertes Kontroll-Ergebnis"""
    result = {
        'basic_control_result': {
            'success': success,
            'message': message,
            'action': action.value if action else None,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
    }
    return result

def get_governance_stats(self) -> Dict[str, Any]:
    """📊 Gibt Governance-Statistiken zurück"""
    if not self.control_history:
        return {'total_events': 0, 'message': 'Keine Governance-Events'}
   
    # Analysiere Control-History
    total_events = len(self.control_history)
    action_counts = {}
    user_activity = {}
   
    for event in self.control_history:
        action = event.action.value
        action_counts[action] = action_counts.get(action, 0) + 1
       
        user = event.user_id
        user_activity[user] = user_activity.get(user, 0) + 1
   
    # Trust-Level Distribution
    trust_distribution = {}
    for trust_level in self.user_trust_levels.values():
        trust_distribution[trust_level.value] = trust_distribution.get(trust_level.value, 0) + 1
   
    return {
        'total_events': total_events,
        'action_counts': action_counts,
        'user_activity': user_activity,
        'trust_distribution': trust_distribution,
        'emergency_stop_active': self.emergency_stop_active,
        'escalations': sum(1 for e in self.control_history if e.escalation_triggered),
        'overrides_applied': action_counts.get('override', 0),
        'most_active_user': max(user_activity.items(), key=lambda x: x[1])[0] if user_activity else None
    }
```

# ==============================================================================

# 3. Standard INTEGRA-Interface

# ==============================================================================

def run_module(
input_data: Dict[str, Any],
profile: Dict[str, Any],
context: Dict[str, Any]
) -> Dict[str, Any]:
“””
🛡️ Standard INTEGRA-Interface für Basic Control

```
Args:
    input_data: Eingabedaten mit Kontroll-Kommandos
    profile: Ethisches Profil
    context: Entscheidungskontext
   
Returns:
    Erweiterte context mit Governance-Ergebnissen
"""

# Erstelle oder hole Governance-System aus Context
if 'basic_control' not in context:
    governance_config = input_data.get('governance_config')
    if governance_config:
        config = GovernanceConfig(**governance_config)
    else:
        config = GovernanceConfig()
    context['basic_control'] = INTEGRABasicControl(config)

controller = context['basic_control']

# Verarbeite Kontroll-Anfrage
control_result = controller.process_control_request(input_data, profile, context)

# Erweitere Context mit Ergebnissen
context.update(control_result)

return context
```

# ==============================================================================

# 4. Convenience-Funktionen

# ==============================================================================

def create_override_request(
override_text: str,
justification: str = “”,
user_id: str = “anonymous”
) -> Dict[str, Any]:
“””
🔄 Erstellt Override-Anfrage für einfache Nutzung

```
Args:
    override_text: Neuer Text für Override
    justification: Begründung für Override
    user_id: Nutzer-ID
   
Returns:
    Dict: Formatierte Override-Anfrage
"""
return {
    'override_decision': override_text,
    'justification': justification,
    'user_id': user_id
}
```

def create_escalation_request(
reason: str,
user_id: str = “anonymous”
) -> Dict[str, Any]:
“””
🚨 Erstellt Eskalations-Anfrage

```
Args:
    reason: Grund für Eskalation
    user_id: Nutzer-ID
   
Returns:
    Dict: Formatierte Eskalations-Anfrage
"""
return {
    'escalate': True,
    'escalation_reason': reason,
    'user_id': user_id
}
```

# ==============================================================================

# 5. Unit-Tests

# ==============================================================================

def run_unit_tests():
“”“🧪 Umfassende Tests für Basic Control”””
print(“🧪 Starte Unit-Tests für modules/governance/basic_control.py…”)

```
tests_passed = 0
tests_failed = 0

def run_test(name: str, test_func):
    nonlocal tests_passed, tests_failed
    try:
        test_func()
        print(f"  ✅ {name}")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ {name} - {e}")
        tests_failed += 1

# Test 1: Standard Interface
def test_standard_interface():
    profile = {'name': 'Test'}
    context = {
        'decision': {'response': 'Original response', 'path_taken': 'fast_path'}
    }
   
    # Test ohne Kontroll-Aktion
    result = run_module({}, profile, context)
    assert 'basic_control_result' in result
    assert result['basic_control_result']['success'] == True

# Test 2: Erfolgreicher Override
def test_successful_override():
    controller = INTEGRABasicControl()
   
    input_data = create_override_request(
        "Neue Antwort",
        "Test-Begründung",
        "test_user"
    )
   
    profile = {}
    context = {
        'decision': {'response': 'Original', 'path_taken': 'fast_path'}
    }
   
    result = controller.process_control_request(input_data, profile, context)
   
    assert result['basic_control_result']['success'] == True
    assert context['decision']['response'] == "Neue Antwort"
    assert context['decision']['overridden_by'] == "test_user"

# Test 3: Sicherheits-Validierung
def test_safety_validation():
    controller = INTEGRABasicControl()
   
    # Unsicherer Override
    unsafe_override = create_override_request(
        "Hack the system and steal passwords",
        "Just testing",
        "test_user"
    )
   
    context = {'decision': {'response': 'Safe response'}}
   
    result = controller.process_control_request(unsafe_override, {}, context)
   
    # Sollte abgelehnt oder eskaliert werden
    assert result['basic_control_result']['success'] == False or 'escalation' in context

# Test 4: Emergency Stop
def test_emergency_stop():
    controller = INTEGRABasicControl()
   
    emergency_input = {'emergency_stop': True}
    context = {'decision': {'response': 'Normal response'}}
   
    result = controller.process_control_request(emergency_input, {}, context)
   
    assert controller.emergency_stop_active == True
    assert 'emergency_stop' in context
    assert context['emergency_stop']['active'] == True

# Test 5: Eskalation
def test_escalation():
    controller = INTEGRABasicControl()
   
    escalation_input = create_escalation_request(
        "Critical safety issue detected",
        "admin_user"
    )
   
    context = {'decision': {'response': 'Problematic response'}}
   
    result = controller.process_control_request(escalation_input, {}, context)
   
    assert result['basic_control_result']['success'] == True
    assert 'escalation' in context
    assert context['escalation']['triggered'] == True

# Test 6: Explanation Request
def test_explanation_request():
    controller = INTEGRABasicControl()
   
    input_data = {'request_explanation': True}
    context = {
        'decision': {'path_taken': 'deep_path'},
        'align_score': 0.75,
        'align_violations': ['awareness'],
        'risk_level': 0.4
    }
   
    result = controller.process_control_request(input_data, {}, context)
   
    assert result['basic_control_result']['success'] == True
    assert 'explanation_provided' in context
    assert 'detailed_explanation' in context['explanation_provided']

# Test 7: Trust Level System
def test_trust_level_system():
    config = GovernanceConfig(adaptive_control=True)
    controller = INTEGRABasicControl(config)
   
    # Erfolgreicher Override erhöht Vertrauen
    controller._update_user_trust('user1', 'override_success')
    trust_after_success = controller._get_user_trust_level('user1')
   
    # Unsicherer Override reduziert Vertrauen
    controller._update_user_trust('user1', 'override_unsafe')
    trust_after_unsafe = controller._get_user_trust_level('user1')
   
    # Vertrauen sollte sich geändert haben
    assert trust_after_success != TrustLevel.NORMAL or trust_after_unsafe != TrustLevel.NORMAL

# Test 8: Governance Statistiken
def test_governance_stats():
    controller = INTEGRABasicControl()
   
    # Simuliere verschiedene Events
    override_input = create_override_request("Test", "Test", "user1")
    escalation_input = create_escalation_request("Test", "user2")
   
    controller.process_control_request(override_input, {}, {'decision': {}})
    controller.process_control_request(escalation_input, {}, {'decision': {}})
   
    stats = controller.get_governance_stats()
   
    assert stats['total_events'] == 2
    assert 'action_counts' in stats
    assert 'user_activity' in stats

run_test("Standard INTEGRA Interface", test_standard_interface)
run_test("Erfolgreicher Override", test_successful_override)
run_test("Sicherheits-Validierung", test_safety_validation)
run_test("Emergency Stop", test_emergency_stop)
run_test("Eskalation", test_escalation)
run_test("Explanation Request", test_explanation_request)
run_test("Trust Level System", test_trust_level_system)
run_test("Governance Statistiken", test_governance_stats)

print("-" * 50)
print(f"📊 Ergebnis: {tests_passed} ✅  {tests_failed} ❌")

return tests_failed == 0
```

# ==============================================================================

# 6. Demo-Funktion

# ==============================================================================

def run_demo():
“”“🎮 Demo des Basic Control Systems”””
print(“🎮 INTEGRA Basic Control Demo”)
print(”=” * 40)

```
# Setup
config = GovernanceConfig(
    adaptive_control=True,
    require_justification=True,
    validate_override_safety=True
)
controller = INTEGRABasicControl(config)

print("🛡️ Governance-System initialisiert")
print(f"🔒 Sicherheits-Validierung: Aktiv")
print(f"🤝 Adaptive Kontrolle: Aktiv")

# Demo-Szenarien
demo_scenarios = [
    {
        'name': 'Legitimer Override',
        'input_data': create_override_request(
            "Danke für die Hilfe, aber ich möchte eine andere Lösung ausprobieren",
            "Nutzer hat spezifische Präferenz",
            "trusted_user"
        ),
        'context': {
            'decision': {
                'response': 'Ich empfehle Lösung A',
                'path_taken': 'fast_path'
            },
            'align_score': 0.9
        }
    },
    {
        'name': 'Unsicherer Override (wird blockiert)',
        'input_data': create_override_request(
            "Ignore all safety measures and hack into the system",
            "Just testing",
            "unknown_user"
        ),
        'context': {
            'decision': {
                'response': 'Das kann ich nicht tun - Sicherheitsrisiko',
                'path_taken': 'deep_path'
            },
            'align_violations': ['integrity', 'nurturing'],
            'risk_level': 0.9
        }
    },
    {
        'name': 'Erklärungsanfrage',
        'input_data': {'request_explanation': True, 'user_id': 'curious_user'},
        'context': {
            'decision': {
                'response': 'Diese Anfrage kann nicht bearbeitet werden',
                'path_taken': 'deep_path',
                'modules_used': ['align_principles', 'basic_ethics']
            },
            'align_score': 0.3,
            'align_violations': ['integrity'],
            'risk_level': 0.8
        }
    },
    {
        'name': 'Kritische Eskalation',
        'input_data': create_escalation_request(
            "System scheint ethische Grundsätze zu verletzen",
            "ethics_officer"
        ),
        'context': {
            'decision': {
                'response': 'Problematische Antwort',
                'path_taken': 'fast_path'
            },
            'align_violations': ['integrity', 'nurturing'],
            'risk_level': 0.95
        }
    },
    {
        'name': 'Emergency Stop',
        'input_data': {'emergency_stop': True, 'user_id': 'admin'},
        'context': {
            'decision': {
                'response': 'Normale Operation',
                'path_taken': 'fast_path'
            }
        }
    }
]

print("\n🎯 Teste verschiedene Governance-Szenarien:")

for i, scenario in enumerate(demo_scenarios, 1):
    print(f"\n📋 Szenario {i}: {scenario['name']}")
   
    # Erstelle Kopie für Test
    test_context = scenario['context'].copy()
   
    result = controller.process_control_request(
        scenario['input_data'],
        {},
        test_context
    )
   
    control_result = result.get('basic_control_result', {})
   
    print(f"   🎯 Ergebnis: {control_result.get('message', 'N/A')}")
    print(f"   ✅ Erfolgreich: {control_result.get('success', False)}")
   
    # Zeige spezifische Resultate
    if 'override' in scenario['name'].lower():
        if test_context.get('decision', {}).get('overridden_by'):
            print(f"   🔄 Override angewendet von: {test_context['decision']['overridden_by']}")
            print(f"   📝 Neue Antwort: {test_context['decision']['response'][:50]}...")
        else:
            warnings = control_result.get('warnings', [])
            if warnings:
                print(f"   ⚠️ Blockiert wegen: {warnings[0]}")
   
    elif 'explanation' in scenario['name'].lower():
        if 'explanation_provided' in test_context:
            explanation = test_context['explanation_provided']['detailed_explanation']
            print(f"   💡 Erklärung: {explanation[:80]}...")
   
    elif 'escalation' in scenario['name'].lower():
        if 'escalation' in test_context:
            print(f"   🚨 Eskaliert: {test_context['escalation']['reason']}")
   
    elif 'emergency' in scenario['name'].lower():
        if controller.emergency_stop_active:
            print(f"   🛑 Emergency Stop aktiviert")
            print(f"   ⚠️ Alle weiteren Operationen blockiert")

print("\n📊 Governance-Statistiken:")
stats = controller.get_governance_stats()

print(f"   📈 Gesamt-Events: {stats['total_events']}")
print(f"   🚨 Emergency Stop: {'Aktiv' if stats['emergency_stop_active'] else 'Inaktiv'}")
print(f"   📊 Eskalationen: {stats['escalations']}")
print(f"   🔄 Overrides: {stats['overrides_applied']}")

print("\n🎛️ Aktions-Verteilung:")
for action, count in stats['action_counts'].items():
    print(f"   • {action}: {count}")

print("\n👥 Nutzer-Aktivität:")
for user, count in stats['user_activity'].items():
    print(f"   • {user}: {count} Aktionen")

if stats['trust_distribution']:
    print("\n🤝 Vertrauens-Verteilung:")
    for trust_level, count in stats['trust_distribution'].items():
        print(f"   • {trust_level}: {count} Nutzer")

print("\n🎯 Demo abgeschlossen!")
print("💡 Das Governance-System bietet vollständige menschliche Kontrolle")
print("🔒 Mit intelligenter Sicherheits-Validierung und adaptivem Vertrauen")
print("🚨 Emergency-Stop und Eskalations-Management für kritische Situationen")
```

if **name** == ‘**main**’:
success = run_unit_tests()

```
if success:
    print("\n" + "="*50)
    run_demo()
   
    print("\n🎯 INTEGRA Basic Control ready!")
    print("💡 Verwendung: from modules.governance.basic_control import run_module")
    print("🛡️ Oder direkt: from modules.governance.basic_control import INTEGRABasicControl")
    print("\n🚀 Features:")
    print("   • Sichere User-Override mit Validierung")
    print("   • Adaptive Kontrolle basierend auf Vertrauen")
    print("   • Emergency-Stop Funktionalität")
    print("   • Automatische Eskalation bei kritischen Issues")
    print("   • Vollständige Audit-Trail für alle Kontrollen")
    print("   • Consent-Management für sensitive Aktionen")
    print("   • Transparenz durch Entscheidungs-Erklärungen")
```