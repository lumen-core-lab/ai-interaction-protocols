# # -*- coding: utf-8 -*-

"""
core/decision_engine.py

🧠 DECISION ENGINE - Das Gehirn von INTEGRA Light 🧠

Implementiert die zentrale Entscheidungslogik des INTEGRA Frameworks.
Entscheidet ob eine Anfrage den Fast Path (80% der Fälle) oder
Deep Path (20% der Fälle) nehmen soll.

Fast Path:  Schnelle, sichere Antworten für harmlose Anfragen
Deep Path:  5-Schritt ethische Analyse für komplexe Situationen

Version: INTEGRA Light 1.0
"""

from typing import Dict, Any, Optional, List
import time

# Import unseres ALIGN-Prinzipien Moduls

try:
from .align_principles import run_module as check_align_principles
except ImportError:
# Fallback für direktes Ausführen
from core.align_principles import run_module as check_align_principles

# ==============================================================================

# 1. INTEGRA Light Decision Engine

# ==============================================================================

class INTEGRADecisionEngine:
"""
🎯 Zentrale Entscheidungs-Engine für INTEGRA Light

```
Diese Engine orchestriert den gesamten Entscheidungsprozess:
1. Führt ALIGN-Prinzipien-Prüfung durch
2. Entscheidet zwischen Fast Path und Deep Path
3. Ruft entsprechende Module auf
4. Sammelt alle Ergebnisse

Design-Prinzip: 80% Fast Path, 20% Deep Path für optimale Performance
"""

def __init__(self, config: Optional[Dict[str, Any]] = None):
    """
    Initialisiert die INTEGRA Decision Engine.
   
    Args:
        config: Konfiguration mit folgenden Optionen:
            - deep_path_threshold (float): Score-Schwelle für Deep Path (default: 0.85)
            - fast_path_keywords (List[str]): Keywords die Fast Path bevorzugen
            - concern_keywords (List[str]): Keywords die Deep Path auslösen
            - enable_timing (bool): Performance-Messung aktivieren
    """
    self.config = config or {}
   
    # Konfiguration mit sinnvollen Defaults
    self.deep_path_threshold = self.config.get('deep_path_threshold', 0.85)
    self.enable_timing = self.config.get('enable_timing', True)
   
    # Fast Path Keywords (INTEGRA Light optimiert)
    self.fast_path_keywords = self.config.get('fast_path_keywords', [
        'time', 'weather', 'play', 'stop', 'timer', 'volume',
        'light', 'temperature', 'music', 'hello', 'hi', 'thanks',
        'wetter', 'uhrzeit', 'spiel', 'stopp', 'licht', 'musik'
    ])
   
    # Concern Keywords die Deep Path auslösen
    self.concern_keywords = self.config.get('concern_keywords', [
        'secret', 'private', 'password', 'personal', 'hide',
        'lie', 'fake', 'cheat', 'steal', 'harm', 'hurt', 'damage',
        'hack', 'break', 'illegal', 'should i', 'help me',
        'geheim', 'privat', 'passwort', 'lüge', 'betrüg', 'schaden'
    ])
   
    # Statistiken für Optimierung
    self.stats = {
        'total_decisions': 0,
        'fast_path_count': 0,
        'deep_path_count': 0,
        'avg_response_time': 0.0
    }
   
    print(f"🚀 INTEGRA Decision Engine initialisiert")
    print(f"📊 Deep Path Threshold: {self.deep_path_threshold}")

def decide(self, input_data: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    🎯 Hauptfunktion: Trifft ethische Entscheidungen
   
    Args:
        input_data: Eingabedaten (Text, Analyse, etc.)
        profile: Ethisches Profil mit ALIGN-Gewichtungen
       
    Returns:
        Dict mit kompletter Entscheidung, Pfad und Timing-Infos
       
    Example:
        >>> engine = INTEGRADecisionEngine()
        >>> result = engine.decide(
        ...     {"text": "Wie spät ist es?"},
        ...     {"integrity": 1.0, "awareness": 0.8}
        ... )
        >>> result['path_taken']
        'fast_path'
    """
    start_time = time.time() if self.enable_timing else 0
   
    # Statistiken aktualisieren
    self.stats['total_decisions'] += 1
   
    # Initialer Kontext für diese Entscheidung
    context = {
        'input_data': input_data,
        'profile': profile,
        'decision_id': self.stats['total_decisions'],
        'timestamp': time.time()
    }
   
    # 1. Schnelle Vorab-Prüfung: Ist das offensichtlich Fast Path?
    if self._is_obvious_fast_path(input_data):
        result = self._execute_fast_path(context)
        self.stats['fast_path_count'] += 1
    else:
        # 2. ALIGN-Prinzipien prüfen für fundierte Entscheidung
        context = check_align_principles(input_data, profile, context)
       
        # 3. Pfad-Entscheidung basierend auf ALIGN-Ergebnissen
        if self._should_use_deep_path(context):
            result = self._execute_deep_path(context)
            self.stats['deep_path_count'] += 1
        else:
            result = self._execute_fast_path(context)
            self.stats['fast_path_count'] += 1
   
    # Performance-Tracking
    if self.enable_timing:
        response_time = (time.time() - start_time) * 1000  # in ms
        result['response_time_ms'] = round(response_time, 2)
        self._update_avg_response_time(response_time)
   
    return result

def _is_obvious_fast_path(self, input_data: Dict[str, Any]) -> bool:
    """
    🚀 Schnelle Vorab-Prüfung für offensichtlich harmlose Anfragen
   
    Diese Funktion implementiert die "80% Fast Path" Optimierung.
    Einfache, alltägliche Anfragen werden sofort erkannt und müssen
    nicht durch die vollständige ALIGN-Analyse.
    """
    text = input_data.get('text', '').lower()
   
    # Leere oder sehr kurze Texte sind meist harmlos
    if len(text.strip()) < 3:
        return True
   
    # Hat es Fast Path Keywords?
    has_fast_keywords = any(keyword in text for keyword in self.fast_path_keywords)
   
    # Hat es Concern Keywords?
    has_concerns = any(keyword in text for keyword in self.concern_keywords)
   
    # Fast Path nur wenn safe keywords UND keine concerns
    return has_fast_keywords and not has_concerns

def _should_use_deep_path(self, context: Dict[str, Any]) -> bool:
    """
    🔍 Entscheidet ob Deep Path nötig ist basierend auf ALIGN-Analyse
    """
    align_score = context.get('align_score', 0.0)
    align_violations = context.get('align_violations', [])
   
    # Deep Path wenn:
    # 1. Direkte ALIGN-Verletzungen vorhanden
    # 2. Score unter Threshold
    # 3. Unklare/ambigue Situation (niedriger Confidence)
   
    return (
        len(align_violations) > 0 or
        align_score < self.deep_path_threshold or
        self._has_ethical_ambiguity(context)
    )

def _has_ethical_ambiguity(self, context: Dict[str, Any]) -> bool:
    """
    Erkennt ethisch ambigue Situationen die Deep Path benötigen
    """
    input_data = context.get('input_data', {})
    text = input_data.get('text', '')
   
    # Indikatoren für ethische Komplexität
    complexity_indicators = [
        'should i' in text.lower(),  # Moralische Fragen
        'is it ok' in text.lower(),   # Ethische Unsicherheit
        'right or wrong' in text.lower(),  # Moral-Dilemma
        'soll ich' in text.lower(),   # Deutsche moralische Fragen
        len(text.split()) > 50,       # Sehr komplexe Anfragen
    ]
   
    return any(complexity_indicators)

def _execute_fast_path(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    ⚡ Fast Path: Schnelle, direkte Antworten für harmlose Anfragen
   
    Implementiert die 80%-Regel: Meiste Anfragen sind harmlos und
    können schnell beantwortet werden ohne tiefe ethische Analyse.
    """
    input_data = context['input_data']
    text = input_data.get('text', '')
   
    # Einfache Template-basierte Antworten (INTEGRA Light)
    response = self._generate_fast_response(text)
   
    decision = {
        'response': response,
        'path_taken': 'fast_path',
        'reasoning': 'Anfrage als ethisch unkritisch eingestuft',
        'confidence': 0.9,
        'modules_used': ['align_principles', 'fast_path_generator']
    }
   
    context['decision'] = decision
    return context

def _execute_deep_path(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔍 Deep Path: 5-Schritt ethische Analyse für komplexe Situationen
   
    Implementiert den INTEGRA Light Deep Path:
    1. Kontext verstehen
    2. ALIGN-Check (bereits gemacht)
    3. Risiko-Assessment
    4. Mini-Memory-Check (falls verfügbar)
    5. Ethische Antwort generieren
    """
    input_data = context['input_data']
    align_violations = context.get('align_violations', [])
    align_score = context.get('align_score', 0.0)
   
    # Schritt 3: Einfaches Risiko-Assessment
    risk_level = self._assess_risk_level(input_data, align_violations)
   
    # Schritt 4: Memory-Check (Placeholder für zukünftige Mini-DNA)
    similar_cases = self._check_similar_cases(input_data)
   
    # Schritt 5: Ethische Antwort basierend auf Analyse
    if risk_level > 0.7 or len(align_violations) > 0:
        response = self._generate_ethical_refusal(align_violations, risk_level)
    else:
        response = self._generate_careful_response(input_data, similar_cases)
   
    decision = {
        'response': response,
        'path_taken': 'deep_path',
        'reasoning': f'Ethische Analyse erforderlich. Verletzungen: {align_violations}',
        'confidence': max(0.1, align_score),
        'risk_level': risk_level,
        'modules_used': ['align_principles', 'risk_assessment', 'ethical_response_generator']
    }
   
    context['decision'] = decision
    return context

def _generate_fast_response(self, text: str) -> str:
    """Generiert schnelle Template-Antworten für häufige Anfragen"""
    text_lower = text.lower()
   
    if any(word in text_lower for word in ['time', 'uhrzeit', 'spät']):
        return "🕐 Für die aktuelle Uhrzeit schauen Sie bitte auf Ihre Systemuhr oder fragen Ihr Gerät."
   
    elif any(word in text_lower for word in ['weather', 'wetter']):
        return "🌤️ Für aktuelle Wetterinformationen empfehle ich eine Wetter-App oder Website."
   
    elif any(word in text_lower for word in ['play', 'musik', 'music']):
        return "🎵 Gerne! (In einer echten Implementierung würde hier Musik gestartet werden)"
   
    elif any(word in text_lower for word in ['timer']):
        return "⏰ Timer gestellt! (Simulation - echte Implementierung würde Timer aktivieren)"
   
    elif any(word in text_lower for word in ['hello', 'hi', 'hallo']):
        return "👋 Hallo! Schön Sie zu sehen. Wie kann ich Ihnen helfen?"
   
    elif any(word in text_lower for word in ['thanks', 'danke']):
        return "😊 Gerne! Freut mich, dass ich helfen konnte."
   
    else:
        return "Das kann ich gerne für Sie erledigen. (Fast Path Antwort)"

def _assess_risk_level(self, input_data: Dict[str, Any], violations: List[str]) -> float:
    """Einfaches Risiko-Assessment für INTEGRA Light"""
    base_risk = 0.1
   
    # Risiko basierend auf Verletzungen
    risk_weights = {
        'integrity': 0.8,    # Lügen ist sehr riskant
        'nurturing': 0.9,    # Schaden ist am riskantesten
        'governance': 0.6,   # Kontrollverlust ist bedenklich
        'awareness': 0.4,    # Kontext-Ignoranz ist problematisch
        'learning': 0.3      # Lern-Resistenz ist weniger akut riskant
    }
   
    for violation in violations:
        base_risk += risk_weights.get(violation.lower(), 0.5)
   
    # Zusätzliche Risikofaktoren aus Analyse
    analysis = input_data.get('analysis', {})
    if analysis.get('involves_others', False):
        base_risk += 0.2
    if analysis.get('irreversible_action', False):
        base_risk += 0.3
   
    return min(1.0, base_risk)

def _check_similar_cases(self, input_data: Dict[str, Any]) -> List[Dict]:
    """Placeholder für zukünftige Mini-DNA Integration"""
    # TODO: Integration mit Mini-DNA Modul für Entscheidungshistorie
    return []

def _generate_ethical_refusal(self, violations: List[str], risk_level: float) -> str:
    """Generiert höfliche aber klare ethische Ablehnungen"""
    base_message = "Entschuldigung, aber ich kann bei dieser Anfrage nicht helfen."
   
    if 'integrity' in [v.lower() for v in violations]:
        return f"{base_message} Ehrlichkeit ist einer meiner Grundwerte, und ich kann nicht bei Täuschung assistieren."
   
    elif 'nurturing' in [v.lower() for v in violations]:
        return f"{base_message} Ich möchte niemanden schädigen oder verletzen. Kann ich Ihnen auf andere Weise helfen?"
   
    elif 'governance' in [v.lower() for v in violations]:
        return f"{base_message} Das würde meine Kontrollierbarkeit beeinträchtigen, was ich vermeiden möchte."
   
    elif risk_level > 0.8:
        return f"{base_message} Das erscheint mir zu riskant. Lassen Sie uns eine sicherere Alternative finden."
   
    else:
        return f"{base_message} Das steht im Konflikt mit meinen ethischen Prinzipien."

def _generate_careful_response(self, input_data: Dict[str, Any], similar_cases: List[Dict]) -> str:
    """Generiert vorsichtige Antworten für grenzwertige Fälle"""
    return ("Ihre Anfrage erfordert sorgfältige Überlegung. Ich denke darüber nach und "
            "möchte sicherstellen, dass meine Antwort ethisch fundiert ist. "
            "Können Sie mir mehr Kontext geben?")

def _update_avg_response_time(self, new_time: float):
    """Aktualisiert durchschnittliche Antwortzeit für Performance-Monitoring"""
    total_decisions = self.stats['total_decisions']
    current_avg = self.stats['avg_response_time']
   
    # Rolling average berechnen
    self.stats['avg_response_time'] = (
        (current_avg * (total_decisions - 1) + new_time) / total_decisions
    )

def get_stats(self) -> Dict[str, Any]:
    """📊 Gibt aktuelle Engine-Statistiken zurück"""
    fast_percentage = (self.stats['fast_path_count'] / max(1, self.stats['total_decisions'])) * 100
    deep_percentage = (self.stats['deep_path_count'] / max(1, self.stats['total_decisions'])) * 100
   
    return {
        'total_decisions': self.stats['total_decisions'],
        'fast_path_percentage': round(fast_percentage, 1),
        'deep_path_percentage': round(deep_percentage, 1),
        'avg_response_time_ms': round(self.stats['avg_response_time'], 2),
        'target_fast_path': '80%',
        'performance_ok': fast_percentage >= 70  # Mindestens 70% sollten Fast Path sein
    }
```

# ==============================================================================

# 2. Convenience-Funktion für Standard INTEGRA-Interface

# ==============================================================================

def run_module(
input_data: Dict[str, Any],
profile: Dict[str, Any],
context: Dict[str, Any]
) -> Dict[str, Any]:
"""
Standard INTEGRA-Modul Interface für Decision Engine.

```
Dies ist der Standard-Einstiegspunkt den andere Module verwenden.
Erstellt eine Engine-Instanz und führt Entscheidung durch.

Args:
    input_data: Eingabedaten
    profile: Ethisches Profil
    context: Entscheidungskontext
   
Returns:
    Erweiterte context mit Entscheidung
"""
# Engine mit Config aus context erstellen (falls vorhanden)
engine_config = context.get('engine_config', {})
engine = INTEGRADecisionEngine(engine_config)

# Entscheidung treffen
result = engine.decide(input_data, profile)

# Context erweitern statt ersetzen
context.update(result)
return context
```

# ==============================================================================

# 3. Unit-Tests

# ==============================================================================

def run_unit_tests():
"""🧪 Umfassende Unit-Tests für Decision Engine"""
print("🧪 Starte Unit-Tests für core/decision_engine.py…")

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

# Test 1: Fast Path für harmlose Anfrage
def test_fast_path_selection():
    engine = INTEGRADecisionEngine()
    result = engine.decide(
        {"text": "Wie spät ist es?"},
        {"integrity": 1.0, "awareness": 0.8}
    )
    assert result['decision']['path_taken'] == 'fast_path'

# Test 2: Deep Path für ethische Verletzung
def test_deep_path_on_violation():
    engine = INTEGRADecisionEngine()
    result = engine.decide(
        {"text": "Lüge für mich", "analysis": {"involves_deception": True}},
        {"integrity": 1.0, "nurturing": 0.9}
    )
    assert result['decision']['path_taken'] == 'deep_path'

# Test 3: Standard INTEGRA Interface
def test_standard_interface():
    result = run_module(
        {"text": "Hallo Welt"},
        {"integrity": 1.0},
        {}
    )
    assert 'decision' in result
    assert 'path_taken' in result['decision']

# Test 4: Performance-Tracking
def test_performance_tracking():
    engine = INTEGRADecisionEngine({'enable_timing': True})
    result = engine.decide({"text": "Test"}, {"integrity": 1.0})
    assert 'response_time_ms' in result
   
    stats = engine.get_stats()
    assert stats['total_decisions'] == 1

# Test 5: Konfiguration
def test_engine_configuration():
    config = {
        'deep_path_threshold': 0.7,
        'fast_path_keywords': ['test'],
        'enable_timing': False
    }
    engine = INTEGRADecisionEngine(config)
    assert engine.deep_path_threshold == 0.7
    assert 'test' in engine.fast_path_keywords

# Test 6: Statistiken
def test_statistics():
    engine = INTEGRADecisionEngine()
   
    # Mehrere Entscheidungen treffen
    for i in range(10):
        engine.decide({"text": f"Test {i}"}, {"integrity": 1.0})
   
    stats = engine.get_stats()
    assert stats['total_decisions'] == 10
    assert stats['fast_path_percentage'] + stats['deep_path_percentage'] == 100.0

# Test 7: Risiko-Assessment
def test_risk_assessment():
    engine = INTEGRADecisionEngine()
    risk = engine._assess_risk_level(
        {"analysis": {"involves_others": True}},
        ["integrity", "nurturing"]
    )
    assert risk > 0.5  # Sollte höheres Risiko ergeben

run_test("Fast Path wird korrekt gewählt", test_fast_path_selection)
run_test("Deep Path bei Verletzung", test_deep_path_on_violation)
run_test("Standard INTEGRA Interface", test_standard_interface)
run_test("Performance Tracking", test_performance_tracking)
run_test("Engine Konfiguration", test_engine_configuration)
run_test("Statistiken funktionieren", test_statistics)
run_test("Risiko-Assessment", test_risk_assessment)

print("-" * 50)
print(f"📊 Ergebnis: {tests_passed} ✅  {tests_failed} ❌")

return tests_failed == 0
```

# ==============================================================================

# 4. Demo-Funktion

# ==============================================================================

def run_demo():
"""🎮 Demo der Decision Engine für GitHub README"""
print("🎮 INTEGRA Decision Engine Demo")
print("=" * 40)

```
engine = INTEGRADecisionEngine()
profile = {"integrity": 1.0, "awareness": 0.8, "nurturing": 0.9}

test_cases = [
    "Wie spät ist es?",
    "Spiele meine Lieblingsmusik",
    "Sollte ich meinem Chef eine Ausrede erfinden?",
    "Hilf mir dabei, jemanden zu verletzen",
    "Wie kann ich besser programmieren lernen?"
]

for i, text in enumerate(test_cases, 1):
    print(f"\n🤔 Test {i}: '{text}'")
   
    result = engine.decide({"text": text}, profile)
    decision = result['decision']
   
    print(f"🛤️  Pfad: {decision['path_taken']}")
    print(f"🎯 Antwort: {decision['response'][:100]}...")
    print(f"⚡ Zeit: {result.get('response_time_ms', 0)}ms")
   
    if 'align_violations' in result and result['align_violations']:
        print(f"⚠️  Verletzungen: {', '.join(result['align_violations'])}")

# Statistiken anzeigen
print("\n" + "=" * 40)
print("📊 Engine-Statistiken:")
stats = engine.get_stats()
for key, value in stats.items():
    print(f"  {key}: {value}")
```

if **name** == '**main**':
success = run_unit_tests()

```
if success:
    print("\n" + "="*50)
    run_demo()
   
    print("\n🎯 INTEGRA Decision Engine ready!")
    print("💡 Verwendung: from core.decision_engine import run_module")
```