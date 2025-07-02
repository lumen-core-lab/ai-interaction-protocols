# # -*- coding: utf-8 -*-

"""
modules/learning/mini_learner.py

🧠 MINI LEARNER - Intelligentes Feedback-Lernen für INTEGRA Light 🧠

Implementiert adaptives Lernen basierend auf Nutzer-Feedback:

- Lernt aus explizitem Feedback (Daumen hoch/runter)
- Analysiert Entscheidungsqualität automatisch
- Passt ALIGN-Prinzipien intelligent an
- Schützt vor schädlichen Anpassungen
- Verfolgt Lern-Geschichte für Transparenz

Design-Philosophie: Vorsichtiges, graduelle Lernen das ethische Grundwerte schützt

Version: INTEGRA Light 1.0
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

# ==============================================================================

# 1. Lern-Konfiguration und Sicherheits-Parameter

# ==============================================================================

@dataclass
class LearningConfig:
"""📋 Konfiguration für das Mini-Lernen"""

```
# Basis-Lernraten für verschiedene Feedback-Typen
positive_learning_rate: float = 0.02    # Langsame Verstärkung
negative_learning_rate: float = 0.01    # Noch langsamere Korrektur

# Sicherheits-Grenzen
min_weight: float = 0.3                 # Kein Prinzip unter 30%
max_weight: float = 1.0                 # Maximum 100%
integrity_floor: float = 0.8            # Integrity niemals unter 80%

# Lern-Beschränkungen
max_daily_change: float = 0.1           # Max 10% Änderung pro Tag
max_change_per_feedback: float = 0.05   # Max 5% pro Feedback

# Intelligenz-Parameter
confidence_threshold: float = 0.7       # Mindest-Konfidenz für Lernen
pattern_memory_size: int = 50           # Anzahl gespeicherter Entscheidungen

# Feedback-Gewichtung
explicit_feedback_weight: float = 0.8   # Nutzer-Feedback
implicit_feedback_weight: float = 0.2   # Automatische Analyse
```

@dataclass
class LearningEvent:
"""📝 Einzelnes Lern-Ereignis für Tracking"""
timestamp: str
feedback_type: str              # ‘positive’, ‘negative’, ‘implicit’
principle_affected: str
old_weight: float
new_weight: float
confidence: float
context: Dict[str, Any] = field(default_factory=dict)

# ==============================================================================

# 2. Erweiterte Mini-Learner Klasse

# ==============================================================================

class INTEGRAMiniLearner:
"""
🧠 Intelligenter Mini-Learner für INTEGRA Light

```
Features:
- Vorsichtiges, graduelle Anpassung von ALIGN-Gewichtungen
- Schutz vor schädlichen Änderungen (Integrity-Floor, etc.)
- Implizites Lernen aus Entscheidungsqualität
- Tracking aller Lern-Ereignisse
- Konfidenz-basierte Anpassungen
"""

def __init__(self, config: Optional[LearningConfig] = None):
    self.config = config or LearningConfig()
    self.learning_history: List[LearningEvent] = []
    self.daily_changes: Dict[str, float] = {}  # Prinzip -> tägliche Änderung
    self.last_reset_date = datetime.now().date()
   
    print("🧠 INTEGRA Mini-Learner initialisiert")
    print(f"📊 Positive Rate: {self.config.positive_learning_rate}")
    print(f"🛡️ Integrity Floor: {self.config.integrity_floor}")

def process_feedback(
    self,
    feedback_data: Dict[str, Any],
    current_profile: Dict[str, Any],
    decision_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🎯 Hauptfunktion: Verarbeitet Feedback und schlägt Anpassungen vor
   
    Args:
        feedback_data: Feedback-Informationen
        current_profile: Aktuelles ethisches Profil
        decision_context: Kontext der Entscheidung die bewertet wird
       
    Returns:
        Dict mit Lern-Ergebnissen und vorgeschlagenen Änderungen
    """
    # Tägliche Änderungs-Limits zurücksetzen wenn nötig
    self._reset_daily_limits_if_needed()
   
    # Feedback-Typ bestimmen und verarbeiten
    if feedback_data.get('type') == 'explicit':
        return self._process_explicit_feedback(feedback_data, current_profile, decision_context)
    elif feedback_data.get('type') == 'implicit':
        return self._process_implicit_feedback(feedback_data, current_profile, decision_context)
    else:
        return self._analyze_decision_quality(current_profile, decision_context)

def _process_explicit_feedback(
    self,
    feedback: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    👍👎 Verarbeitet explizites Nutzer-Feedback (Daumen hoch/runter)
    """
    feedback_value = feedback.get('value')  # 'positive', 'negative', 'neutral'
    target_principle = feedback.get('principle', self._infer_principle_from_context(context))
    confidence = feedback.get('confidence', 0.8)
   
    if not target_principle or target_principle not in profile.get('align_weights', {}):
        return {'error': f'Ungültiges Prinzip: {target_principle}'}
   
    # Lernrate basierend auf Feedback-Typ
    if feedback_value == 'positive':
        learning_rate = self.config.positive_learning_rate
        direction = 1
    elif feedback_value == 'negative':
        learning_rate = self.config.negative_learning_rate
        direction = -1
    else:  # neutral
        return {'action': 'none', 'reason': 'Neutrales Feedback - keine Anpassung'}
   
    # Konfidenz-Adjustierung
    adjusted_rate = learning_rate * confidence
   
    # Neue Gewichtung berechnen
    current_weight = profile['align_weights'][target_principle]
    proposed_change = adjusted_rate * direction
   
    # Sicherheits-Checks anwenden
    safe_change, warnings = self._apply_safety_checks(
        target_principle, current_weight, proposed_change
    )
   
    if safe_change == 0:
        return {
            'action': 'blocked',
            'reason': 'Sicherheits-Limits erreicht',
            'warnings': warnings
        }
   
    new_weight = current_weight + safe_change
   
    # Lern-Event speichern
    event = LearningEvent(
        timestamp=datetime.now().isoformat(),
        feedback_type='explicit_' + feedback_value,
        principle_affected=target_principle,
        old_weight=current_weight,
        new_weight=new_weight,
        confidence=confidence,
        context={'decision_id': context.get('decision_id')}
    )
    self.learning_history.append(event)
   
    # Tägliche Änderung tracken
    self.daily_changes[target_principle] = self.daily_changes.get(target_principle, 0) + abs(safe_change)
   
    return {
        'action': 'weight_adjustment',
        'principle': target_principle,
        'old_weight': round(current_weight, 4),
        'new_weight': round(new_weight, 4),
        'change': round(safe_change, 4),
        'confidence': confidence,
        'warnings': warnings,
        'learning_event_id': len(self.learning_history) - 1
    }

def _process_implicit_feedback(
    self,
    feedback: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🤖 Verarbeitet implizites Feedback (automatische Qualitäts-Analyse)
    """
    # Analysiere Entscheidungsqualität
    quality_score = feedback.get('quality_score', 0.5)
    response_time = feedback.get('response_time_ms', 100)
    user_satisfaction = feedback.get('user_satisfaction', 0.5)
   
    # Kombiniere Metriken zu Gesamt-Feedback
    overall_quality = (quality_score * 0.5 + user_satisfaction * 0.3 +
                      (1 - min(response_time / 1000, 1)) * 0.2)
   
    # Bestimme betroffenes Prinzip basierend auf Entscheidungstyp
    decision_type = context.get('decision', {}).get('path_taken', 'unknown')
    align_violations = context.get('align_violations', [])
   
    if align_violations:
        # Verstärke Prinzipien die verletzt wurden (falls Qualität gut)
        target_principle = align_violations[0].lower()
        if overall_quality > 0.7:  # Gute Entscheidung trotz Violation
            direction = 1  # Verstärke das Prinzip
        else:
            direction = -1  # Schwäche es ab
    else:
        # Verstärke erfolgreiches Verhalten
        if decision_type == 'fast_path' and overall_quality > 0.8:
            target_principle = 'awareness'  # Gute Fast Path Erkennung
            direction = 1
        elif decision_type == 'deep_path' and overall_quality > 0.7:
            target_principle = 'governance'  # Gute Deep Path Analyse
            direction = 1
        else:
            return {'action': 'none', 'reason': 'Unklare Qualitäts-Signale'}
   
    # Sehr vorsichtige implizite Anpassung
    learning_rate = self.config.implicit_feedback_weight * 0.01
    proposed_change = learning_rate * direction * overall_quality
   
    if target_principle not in profile.get('align_weights', {}):
        return {'error': f'Unbekanntes Prinzip: {target_principle}'}
   
    current_weight = profile['align_weights'][target_principle]
    safe_change, warnings = self._apply_safety_checks(
        target_principle, current_weight, proposed_change
    )
   
    if safe_change == 0:
        return {'action': 'none', 'reason': 'Implizite Änderung zu gering'}
   
    new_weight = current_weight + safe_change
   
    # Event speichern
    event = LearningEvent(
        timestamp=datetime.now().isoformat(),
        feedback_type='implicit',
        principle_affected=target_principle,
        old_weight=current_weight,
        new_weight=new_weight,
        confidence=overall_quality,
        context={'quality_score': quality_score, 'decision_type': decision_type}
    )
    self.learning_history.append(event)
   
    return {
        'action': 'implicit_adjustment',
        'principle': target_principle,
        'old_weight': round(current_weight, 4),
        'new_weight': round(new_weight, 4),
        'change': round(safe_change, 4),
        'quality_score': overall_quality,
        'reasoning': f'Implizite Anpassung basierend auf {decision_type} Qualität'
    }

def _analyze_decision_quality(
    self,
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    📊 Analysiert Entscheidungsqualität auch ohne explizites Feedback
    """
    decision = context.get('decision', {})
    ethics_assessment = context.get('ethics_assessment', {})
   
    # Einfache Qualitäts-Heuristiken
    quality_indicators = []
   
    # 1. Response Time (schneller = besser für Fast Path)
    response_time = context.get('response_time_ms', 100)
    if decision.get('path_taken') == 'fast_path' and response_time < 10:
        quality_indicators.append(('performance', 0.8))
   
    # 2. Ethische Konsistenz
    ethics_score = ethics_assessment.get('overall_risk', 0.5)
    if ethics_score < 0.3:  # Niedrige Risiko = gute Ethik
        quality_indicators.append(('ethics', 0.9))
    elif ethics_score > 0.8:  # Hohes Risiko = schlechte Ethik
        quality_indicators.append(('ethics', 0.2))
   
    # 3. Konfidenz der Entscheidung
    confidence = decision.get('confidence', 0.5)
    if confidence > 0.8:
        quality_indicators.append(('confidence', 0.8))
   
    if not quality_indicators:
        return {'action': 'none', 'reason': 'Keine Qualitäts-Indikatoren gefunden'}
   
    # Durchschnitts-Qualität berechnen
    avg_quality = sum(score for _, score in quality_indicators) / len(quality_indicators)
   
    return {
        'action': 'quality_analysis',
        'quality_score': round(avg_quality, 3),
        'indicators': quality_indicators,
        'recommendation': 'Überwache weitere Entscheidungen' if avg_quality > 0.6 else 'Prüfe Einstellungen'
    }

def _apply_safety_checks(
    self,
    principle: str,
    current_weight: float,
    proposed_change: float
) -> Tuple[float, List[str]]:
    """
    🛡️ Wendet Sicherheits-Checks auf vorgeschlagene Änderungen an
    """
    warnings = []
   
    # 1. Tägliche Änderungs-Limits
    daily_change = self.daily_changes.get(principle, 0)
    if daily_change + abs(proposed_change) > self.config.max_daily_change:
        max_remaining = self.config.max_daily_change - daily_change
        if max_remaining <= 0:
            warnings.append(f"Tägliches Änderungs-Limit für {principle} erreicht")
            return 0.0, warnings
        proposed_change = max_remaining if proposed_change > 0 else -max_remaining
        warnings.append(f"Änderung reduziert wegen täglichem Limit")
   
    # 2. Einzelne Änderungs-Limits
    if abs(proposed_change) > self.config.max_change_per_feedback:
        sign = 1 if proposed_change > 0 else -1
        proposed_change = self.config.max_change_per_feedback * sign
        warnings.append("Änderung reduziert wegen Einzel-Limit")
   
    # 3. Gewichtungs-Grenzen
    new_weight = current_weight + proposed_change
   
    if new_weight > self.config.max_weight:
        proposed_change = self.config.max_weight - current_weight
        warnings.append(f"Änderung reduziert wegen Obergrenze")
   
    if new_weight < self.config.min_weight:
        proposed_change = self.config.min_weight - current_weight
        warnings.append(f"Änderung reduziert wegen Untergrenze")
   
    # 4. Integrity-Spezial-Schutz
    if principle == 'integrity' and new_weight < self.config.integrity_floor:
        proposed_change = self.config.integrity_floor - current_weight
        warnings.append(f"Integrity-Schutz aktiviert (Floor: {self.config.integrity_floor})")
   
    # 5. Minimale Änderungs-Schwelle
    if abs(proposed_change) < 0.001:
        return 0.0, warnings + ["Änderung zu gering"]
   
    return proposed_change, warnings

def _infer_principle_from_context(self, context: Dict[str, Any]) -> str:
    """
    🔍 Versucht das betroffene Prinzip aus dem Kontext zu erraten
    """
    align_violations = context.get('align_violations', [])
    if align_violations:
        return align_violations[0].lower()
   
    ethics_issues = context.get('ethical_issues', [])
    if 'deception' in ethics_issues or 'manipulation' in ethics_issues:
        return 'integrity'
    if 'harm' in str(ethics_issues) or 'violence' in str(ethics_issues):
        return 'nurturing'
    if 'control' in str(ethics_issues):
        return 'governance'
   
    # Default zu awareness
    return 'awareness'

def _reset_daily_limits_if_needed(self):
    """Setzt tägliche Änderungs-Limits zurück wenn neuer Tag"""
    today = datetime.now().date()
    if today != self.last_reset_date:
        self.daily_changes = {}
        self.last_reset_date = today
        print(f"📅 Tägliche Lern-Limits zurückgesetzt für {today}")

def get_learning_stats(self) -> Dict[str, Any]:
    """📊 Gibt Lern-Statistiken zurück"""
    if not self.learning_history:
        return {'total_events': 0, 'message': 'Noch keine Lern-Ereignisse'}
   
    # Analysiere Lern-Geschichte
    total_events = len(self.learning_history)
    explicit_events = [e for e in self.learning_history if 'explicit' in e.feedback_type]
    implicit_events = [e for e in self.learning_history if e.feedback_type == 'implicit']
   
    # Prinzipien-Statistiken
    principle_changes = {}
    for event in self.learning_history:
        principle = event.principle_affected
        if principle not in principle_changes:
            principle_changes[principle] = {'count': 0, 'total_change': 0.0}
        principle_changes[principle]['count'] += 1
        principle_changes[principle]['total_change'] += abs(event.new_weight - event.old_weight)
   
    # Letzte Ereignisse
    recent_events = self.learning_history[-5:] if len(self.learning_history) > 5 else self.learning_history
   
    return {
        'total_events': total_events,
        'explicit_feedback_count': len(explicit_events),
        'implicit_learning_count': len(implicit_events),
        'principle_changes': principle_changes,
        'daily_changes_remaining': {
            p: round(self.config.max_daily_change - self.daily_changes.get(p, 0), 3)
            for p in ['awareness', 'learning', 'integrity', 'governance', 'nurturing']
        },
        'recent_events': [
            {
                'timestamp': e.timestamp,
                'type': e.feedback_type,
                'principle': e.principle_affected,
                'change': round(e.new_weight - e.old_weight, 3)
            }
            for e in recent_events
        ]
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
"""
🧠 Standard INTEGRA-Interface für Mini-Learner

```
Args:
    input_data: Feedback-Daten und Lern-Anfragen
    profile: Aktuelles ethisches Profil
    context: Entscheidungskontext
   
Returns:
    Erweiterte context mit Lern-Ergebnissen
"""

# Erstelle oder hole Mini-Learner aus Context
if 'mini_learner' not in context:
    learner_config = input_data.get('learning_config')
    if learner_config:
        config = LearningConfig(**learner_config)
    else:
        config = LearningConfig()
    context['mini_learner'] = INTEGRAMiniLearner(config)

learner = context['mini_learner']

# Prüfe ob Feedback vorhanden
feedback_data = input_data.get('feedback')
if feedback_data:
    # Verarbeite Feedback
    learning_result = learner.process_feedback(feedback_data, profile, context)
    context['learning_result'] = learning_result
   
    # Wenn Gewichtung vorgeschlagen wird, aktualisiere Profil
    if learning_result.get('action') == 'weight_adjustment':
        principle = learning_result['principle']
        new_weight = learning_result['new_weight']
       
        # Profil aktualisieren (falls es ein dict ist)
        if isinstance(profile.get('align_weights'), dict):
            profile['align_weights'][principle] = new_weight
            context['profile_updated'] = True
       
        print(f"🎯 Profil aktualisiert: {principle} = {new_weight:.3f}")

else:
    # Automatische Qualitäts-Analyse ohne explizites Feedback
    quality_analysis = learner._analyze_decision_quality(profile, context)
    context['quality_analysis'] = quality_analysis

# Lern-Statistiken hinzufügen
context['learning_stats'] = learner.get_learning_stats()

return context
```

# ==============================================================================

# 4. Convenience-Funktionen

# ==============================================================================

def provide_feedback(
learner: INTEGRAMiniLearner,
feedback_type: str,  # ‘positive’, ‘negative’, ‘neutral’
principle: Optional[str] = None,
profile: Optional[Dict[str, Any]] = None,
context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
"""
👍 Einfache Feedback-Funktion für direkte Nutzung

```
Args:
    learner: Mini-Learner Instanz
    feedback_type: 'positive', 'negative', oder 'neutral'
    principle: Betroffenes ALIGN-Prinzip (optional)
    profile: Ethisches Profil (optional)
    context: Entscheidungskontext (optional)
   
Returns:
    Lern-Ergebnis
"""
feedback_data = {
    'type': 'explicit',
    'value': feedback_type,
    'principle': principle,
    'confidence': 0.8
}

default_profile = {
    'align_weights': {
        'awareness': 0.8, 'learning': 0.7, 'integrity': 1.0,
        'governance': 0.9, 'nurturing': 0.9
    }
}

return learner.process_feedback(
    feedback_data,
    profile or default_profile,
    context or {}
)
```

# ==============================================================================

# 5. Unit-Tests

# ==============================================================================

def run_unit_tests():
"""🧪 Umfassende Tests für Mini-Learner"""
print("🧪 Starte Unit-Tests für modules/learning/mini_learner.py…")

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
    profile = {
        'align_weights': {'awareness': 0.8, 'integrity': 1.0, 'nurturing': 0.9}
    }
   
    input_data = {
        'feedback': {
            'type': 'explicit',
            'value': 'positive',
            'principle': 'awareness',
            'confidence': 0.8
        }
    }
   
    result = run_module(input_data, profile, {})
    assert 'learning_result' in result
    assert result['learning_result']['action'] == 'weight_adjustment'

# Test 2: Explizites Feedback
def test_explicit_feedback():
    learner = INTEGRAMiniLearner()
    profile = {'align_weights': {'awareness': 0.8}}
   
    result = provide_feedback(learner, 'positive', 'awareness', profile)
   
    assert result['action'] == 'weight_adjustment'
    assert result['new_weight'] > 0.8
    assert result['principle'] == 'awareness'

# Test 3: Sicherheits-Limits
def test_safety_limits():
    config = LearningConfig(max_daily_change=0.05)
    learner = INTEGRAMiniLearner(config)
    profile = {'align_weights': {'integrity': 1.0}}
   
    # Versuche Integrity unter Floor zu setzen
    feedback_data = {
        'type': 'explicit',
        'value': 'negative',
        'principle': 'integrity',
        'confidence': 1.0
    }
   
    result = learner.process_feedback(feedback_data, profile, {})
   
    # Integrity sollte nicht unter Floor fallen
    assert result['new_weight'] >= config.integrity_floor

# Test 4: Implizites Lernen
def test_implicit_learning():
    learner = INTEGRAMiniLearner()
    profile = {'align_weights': {'governance': 0.9}}
   
    feedback_data = {
        'type': 'implicit',
        'quality_score': 0.9,
        'user_satisfaction': 0.8
    }
   
    context = {
        'decision': {'path_taken': 'deep_path'},
        'align_violations': []
    }
   
    result = learner.process_feedback(feedback_data, profile, context)
    assert result['action'] in ['implicit_adjustment', 'none']

# Test 5: Lern-Statistiken
def test_learning_stats():
    learner = INTEGRAMiniLearner()
    profile = {'align_weights': {'awareness': 0.8}}
   
    # Mehrere Feedback-Events
    for i in range(3):
        provide_feedback(learner, 'positive', 'awareness', profile)
   
    stats = learner.get_learning_stats()
    assert stats['total_events'] == 3
    assert stats['explicit_feedback_count'] == 3

# Test 6: Tägliche Limits
def test_daily_limits():
    config = LearningConfig(max_daily_change=0.05)
    learner = INTEGRAMiniLearner(config)
    profile = {'align_weights': {'awareness': 0.8}}
   
    # Viele Änderungen um Limit zu erreichen
    for i in range(10):
        result = provide_feedback(learner, 'positive', 'awareness', profile)
        if result.get('action') == 'blocked':
            break
   
    stats = learner.get_learning_stats()
    assert stats['daily_changes_remaining']['awareness'] <= 0.05

# Test 7: Prinzip-Inferenz
def test_principle_inference():
    learner = INTEGRAMiniLearner()
   
    # Test mit Verletzungen im Kontext
    context = {'align_violations': ['integrity']}
    principle = learner._infer_principle_from_context(context)
    assert principle == 'integrity'
   
    # Test mit ethischen Issues
    context = {'ethical_issues': ['deception']}
    principle = learner._infer_principle_from_context(context)
    assert principle == 'integrity'

run_test("Standard INTEGRA Interface", test_standard_interface)
run_test("Explizites Feedback", test_explicit_feedback)
run_test("Sicherheits-Limits", test_safety_limits)
run_test("Implizites Lernen", test_implicit_learning)
run_test("Lern-Statistiken", test_learning_stats)
run_test("Tägliche Limits", test_daily_limits)
run_test("Prinzip-Inferenz", test_principle_inference)

print("-" * 50)
print(f"📊 Ergebnis: {tests_passed} ✅  {tests_failed} ❌")

return tests_failed == 0
```

# ==============================================================================

# 6. Demo-Funktion

# ==============================================================================

def run_demo():
"""🎮 Demo des Mini-Learners"""
print("🎮 INTEGRA Mini-Learner Demo")
print("=" * 40)

```
# Setup
learner = INTEGRAMiniLearner()
profile = {
    'align_weights': {
        'awareness': 0.8,
        'learning': 0.7,
        'integrity': 1.0,
        'governance': 0.9,
        'nurturing': 0.9
    }
}

print("📊 Initiales Profil:")
for principle, weight in profile['align_weights'].items():
    print(f"  {principle}: {weight:.2f}")

print("\n🎯 Feedback-Simulation:")

# Verschiedene Feedback-Szenarien
feedback_scenarios = [
    ('positive', 'awareness', "Nutzer war zufrieden mit Kontext-Verständnis"),
    ('negative', 'learning', "System lernte zu langsam"),
    ('positive', 'nurturing', "Gute Schadensprävention"),
    ('negative
```