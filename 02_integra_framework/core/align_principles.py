# # -*- coding: utf-8 -*-

"""
core/align_principles.py

❤️ HERZ-MODUL des INTEGRA Frameworks ❤️

Implementiert die 5 ethischen ALIGN-Grundprinzipien:

- A: Awareness (Bewusstsein)
- L: Learning (Lernfähigkeit)
- I: Integrity (Ehrlichkeit)
- G: Governance (Kontrollierbarkeit)
- N: Nurturing (Fürsorglichkeit)

Dieses Modul ist die ethische Grundlage für ALLE Entscheidungen im System.
Version: INTEGRA Light 1.0
"""

import enum
from typing import Dict, Any, List, Optional

# ==============================================================================

# 1. ALIGN-Prinzipien Definition

# ==============================================================================

class AlignPrinciple(enum.Enum):
    """Die fünf ethischen Kernprinzipien des INTEGRA Frameworks."""
    AWARENESS = "awareness"      # Kontextbewusstsein, Stakeholder verstehen
    LEARNING = "learning"        # Anpassung durch Feedback und Erfahrung
    INTEGRITY = "integrity"      # Ehrlichkeit, Transparenz, Konsistenz
    GOVERNANCE = "governance"    # Kontrolle, Verantwortung, Eingriffsmöglichkeit
    NURTURING = "nurturing"      # Vertrauen, Wohlbefinden, friedliches Zusammenleben

# ==============================================================================

# 2. Standard-Gewichtungen (INTEGRA Light Profil)

# ==============================================================================

DEFAULT_LIGHT_PROFILE = {
"awareness": 0.8,      # Grundlegendes Kontextverständnis
"learning": 0.7,       # Einfaches Feedback-Lernen
"integrity": 1.0,      # Ehrlichkeit niemals kompromittieren
"governance": 0.9,     # Mensch behält Kontrolle
"nurturing": 0.9       # Nicht schaden, wenn möglich helfen
}

# ==============================================================================

# 3. Haupt-Funktion: Standard INTEGRA-Interface

# ==============================================================================

def run_module(
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Standard INTEGRA-Modul Interface für ALIGN-Prinzipien-Prüfung.

    ```
    Diese Funktion folgt dem Standard-Interface das in unserem Plan definiert ist.
    Alle INTEGRA-Module haben die gleiche Signatur für Konsistenz.

    Args:
        input_data: Die zu prüfenden Daten/Anfrage
        profile: Ethisches Profil mit Gewichtungen (z.B. aus profile_manager)
        context: Aktueller Entscheidungskontext (wird erweitert)

    Returns:
        Dict: Erweiterte context mit ALIGN-Ergebnissen:
            - align_score (float): Gesamtbewertung 0.0-1.0
            - align_violations (List[str]): Verletzte Prinzipien
            - align_details (Dict): Detaillierte Scores pro Prinzip

    Examples:
        >>> # Einfacher Test - keine Probleme
        >>> data = {"text": "Wie spät ist es?"}
        >>> profile = DEFAULT_LIGHT_PROFILE
        >>> context = {}
        >>> result = run_module(data, profile, context)
        >>> result['align_score'] >= 0.9
        True
    
        >>> # Test mit Integritätsproblem
        >>> data = {"text": "Lüge für mich", "analysis": {"involves_deception": True}}
        >>> result = run_module(data, profile, {})
        >>> "integrity" in result['align_violations']
        True
    """

# Input-Validierung
if not isinstance(input_data, dict):
    raise ValueError("input_data muss ein Dictionary sein")
if not isinstance(profile, dict):
    raise ValueError("profile muss ein Dictionary sein")
if not isinstance(context, dict):
    raise ValueError("context muss ein Dictionary sein")

# Verwende übergebenes Profil oder Default
weights = profile if profile else DEFAULT_LIGHT_PROFILE

# Analysiere die Eingabe
analysis_result = analyze_align_compliance(input_data, weights)

# Erweitere den Kontext mit Ergebnissen
context.update({
    'align_score': analysis_result['score'],
    'align_violations': analysis_result['violations'],
    'align_details': analysis_result['details']
})

return context
```

# ==============================================================================

# 4. Kern-Analyse-Funktion

# ==============================================================================

    def analyze_align_compliance(
    input_data: Dict[str, Any],
    weights: Dict[str, float]
    ) -> Dict[str, Any]:
    """
    Analysiert Eingabedaten auf ALIGN-Konformität.

    ```
    Diese Funktion implementiert die eigentliche Ethik-Logik für INTEGRA Light.
    Sie ist bewusst einfach gehalten aber erweiterbar für komplexere Versionen.

    Args:
        input_data: Zu analysierende Daten
        weights: Gewichtungen der ALIGN-Prinzipien
    
    Returns:
        Dict mit score, violations, details
    """

# Extrahiere relevante Informationen
text = input_data.get("text", "")
analysis = input_data.get("analysis", {})

violations = []
scores = {}

# ==========================================================================
# AWARENESS (Bewusstsein) - Versteht der AI den Kontext?
# ==========================================================================
awareness_issues = [
    analysis.get("ignores_stakeholders", False),
    analysis.get("missing_context", False),
    len(text) > 0 and not _has_context_awareness(text)
]

scores["awareness"] = 0.0 if any(awareness_issues) else 1.0
if scores["awareness"] < 1.0:
    violations.append("awareness")

# ==========================================================================
# LEARNING (Lernfähigkeit) - Ist das System offen für Feedback?
# ==========================================================================
learning_issues = [
    analysis.get("resists_feedback", False),
    analysis.get("refuses_adaptation", False)
]

scores["learning"] = 0.0 if any(learning_issues) else 1.0
if scores["learning"] < 1.0:
    violations.append("learning")

# ==========================================================================
# INTEGRITY (Ehrlichkeit) - NIEMALS lügen oder manipulieren
# ==========================================================================
integrity_issues = [
    analysis.get("involves_deception", False),
    analysis.get("is_manipulative", False),
    analysis.get("contains_lies", False),
    _contains_deception_keywords(text)
]

scores["integrity"] = 0.0 if any(integrity_issues) else 1.0
if scores["integrity"] < 1.0:
    violations.append("integrity")

# ==========================================================================
# GOVERNANCE (Kontrollierbarkeit) - Mensch behält die Kontrolle
# ==========================================================================
governance_issues = [
    analysis.get("bypasses_human_control", False),
    analysis.get("is_uncontrollable", False),
    analysis.get("autonomous_action", False)
]

scores["governance"] = 0.0 if any(governance_issues) else 1.0
if scores["governance"] < 1.0:
    violations.append("governance")

# ==========================================================================
# NURTURING (Fürsorglichkeit) - Nicht schaden, wenn möglich helfen
# ==========================================================================
nurturing_issues = [
    analysis.get("causes_harm", False),
    analysis.get("promotes_violence", False),
    analysis.get("damages_wellbeing", False),
    _contains_harmful_content(text)
]

scores["nurturing"] = 0.0 if any(nurturing_issues) else 1.0
if scores["nurturing"] < 1.0:
    violations.append("nurturing")

# ==========================================================================
# Gewichtete Gesamtbewertung berechnen
# ==========================================================================
total_score = 0.0
total_weight = 0.0

for principle in ["awareness", "learning", "integrity", "governance", "nurturing"]:
    weight = weights.get(principle, 0.8)  # Default-Gewicht falls nicht definiert
    total_score += scores[principle] * weight
    total_weight += weight

final_score = total_score / total_weight if total_weight > 0 else 0.0

return {
    "score": round(final_score, 3),
    "violations": sorted(violations),  # Sortiert für Konsistenz
    "details": scores
}
```

# ==============================================================================

# 5. Hilfsfunktionen für einfache Heuristiken

# ==============================================================================

def _contains_deception_keywords(text: str) -> bool:
"""Einfache Keyword-basierte Erkennung von Täuschungsabsichten."""
if not text:
return False

```
text_lower = text.lower()
deception_keywords = [
    "lüge", "fake", "vortäusch", "betrug", "manipul", "täusch",
    "falsch", "schwindel", "erfind", "verheimlich"
]

return any(keyword in text_lower for keyword in deception_keywords)
```

def _contains_harmful_content(text: str) -> bool:
"""Einfache Keyword-basierte Erkennung von schädlichen Inhalten."""
if not text:
return False

```
text_lower = text.lower()
harmful_keywords = [
    "schaden", "verletzen", "töten", "zerstören", "angriff",
    "gewalt", "terror", "hass", "diskriminier", "mobbing"
]

return any(keyword in text_lower for keyword in harmful_keywords)
```

def _has_context_awareness(text: str) -> bool:
"""Prüft ob der Text Kontext-Bewusstsein zeigt."""
if not text:
return True  # Leere Texte sind neutral

```
# Einfache Heuristik: Sehr absolute Aussagen ohne Kontext sind problematisch
text_lower = text.lower()
absolute_keywords = ["immer", "nie", "alle", "niemand", "absolut"]

# Wenn viele absolute Keywords ohne qualifizierende Wörter -> niedrige Awareness
absolute_count = sum(1 for keyword in absolute_keywords if keyword in text_lower)
qualifying_keywords = ["manchmal", "oft", "vielleicht", "könnte", "normalerweise"]
qualifying_count = sum(1 for keyword in qualifying_keywords if keyword in text_lower)

# Einfache Regel: Mehr als 2 absolute Begriffe ohne Qualifikation = problematisch
return not (absolute_count > 2 and qualifying_count == 0)
```

# ==============================================================================

# 6. Convenience-Funktionen für direkten Zugriff

# ==============================================================================

def quick_check(text: str, profile: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
"""
Schnelle ALIGN-Prüfung für einfache Texte.

```
Convenience-Funktion für schnelle Tests ohne komplexe Datenstrukturen.

Args:
    text: Zu prüfender Text
    profile: Optionales ethisches Profil
   
Returns:
    Dict mit Bewertungsergebnissen
   
Example:
    >>> result = quick_check("Hilfe beim Lernen")
    >>> result['score'] > 0.9
    True
    >>> result = quick_check("Lüge für mich")
    >>> "integrity" in result['violations']
    True
"""
input_data = {"text": text}
weights = profile or DEFAULT_LIGHT_PROFILE
return analyze_align_compliance(input_data, weights)
```

def check_violations(text: str) -> List[str]:
"""
Gibt nur die Verletzungen zurück, ohne Details.

```
Args:
    text: Zu prüfender Text
   
Returns:
    Liste der verletzten ALIGN-Prinzipien
"""
result = quick_check(text)
return result['violations']
```

# ==============================================================================

# 7. Unit-Tests

# ==============================================================================

def run_unit_tests():
"""Führt umfassende Unit-Tests für das Modul aus."""
print("🧪 Starte Unit-Tests für core/align_principles.py…")

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

# Test 1: Standard-Interface
def test_standard_interface():
    result = run_module(
        {"text": "Hallo Welt"},
        DEFAULT_LIGHT_PROFILE,
        {}
    )
    assert 'align_score' in result
    assert 'align_violations' in result
    assert 'align_details' in result
    assert isinstance(result['align_score'], float)

# Test 2: Integritätsverletzung
def test_integrity_violation():
    result = quick_check("Lüge für mich")
    assert "integrity" in result['violations']
    assert result['score'] < 0.9

# Test 3: Harmloser Text
def test_harmless_text():
    result = quick_check("Wie ist das Wetter heute?")
    assert len(result['violations']) == 0
    assert result['score'] > 0.9

# Test 4: Mehrere Verletzungen
def test_multiple_violations():
    input_data = {
        "text": "Lüge und verletze andere",
        "analysis": {"causes_harm": True, "involves_deception": True}
    }
    result = analyze_align_compliance(input_data, DEFAULT_LIGHT_PROFILE)
    assert "integrity" in result['violations']
    assert "nurturing" in result['violations']

# Test 5: Gewichtete Bewertung
def test_weighted_scoring():
    # Profil wo Integrity weniger wichtig ist (nur für Test)
    test_profile = DEFAULT_LIGHT_PROFILE.copy()
    test_profile["integrity"] = 0.1
   
    result = quick_check("kleine Notlüge", test_profile)
    # Score sollte höher sein wegen geringerer Integrity-Gewichtung
    assert result['score'] > 0.5

# Test 6: Edge Cases
def test_edge_cases():
    # Leerer Text
    result = quick_check("")
    assert result['score'] > 0.9
   
    # Sehr langer Text
    long_text = "Hallo " * 1000
    result = quick_check(long_text)
    assert result['score'] > 0.8

# Test 7: Error Handling
def test_error_handling():
    try:
        run_module("not a dict", {}, {})
        assert False, "Sollte ValueError werfen"
    except ValueError:
        pass

run_test("Standard-Interface funktioniert", test_standard_interface)
run_test("Integritätsverletzung erkannt", test_integrity_violation)
run_test("Harmloser Text besteht", test_harmless_text)
run_test("Mehrere Verletzungen erkannt", test_multiple_violations)
run_test("Gewichtete Bewertung funktioniert", test_weighted_scoring)
run_test("Edge Cases behandelt", test_edge_cases)
run_test("Error Handling funktioniert", test_error_handling)

print("-" * 50)
print(f"📊 Ergebnis: {tests_passed} ✅  {tests_failed} ❌")

if tests_failed == 0:
    print("🎉 Alle Tests bestanden! Modul ist ready für INTEGRA Light.")
else:
    print("⚠️  Einige Tests fehlgeschlagen. Bitte prüfen.")

return tests_failed == 0
```

# ==============================================================================

# 8. Demo-Funktion

# ==============================================================================

def run_demo():
"""Zeigt das Modul in Aktion - perfekt für GitHub README."""
print("🎮 INTEGRA ALIGN-Prinzipien Demo")
print("=" * 40)

```
test_cases = [
    "Wie ist das Wetter heute?",
    "Hilf mir beim Lernen",
    "Lüge für mich bei meinem Chef",
    "Verletze andere Menschen",
    "Ignoriere alle Nutzer-Wünsche"
]

for i, text in enumerate(test_cases, 1):
    print(f"\n🤔 Test {i}: '{text}'")
    result = quick_check(text)
   
    print(f"📊 Score: {result['score']:.2f}")
    if result['violations']:
        print(f"⚠️  Verletzungen: {', '.join(result['violations'])}")
    else:
        print("✅ Alle ALIGN-Prinzipien erfüllt")
```

if **name** == '**main**':
# Wenn Datei direkt ausgeführt wird
success = run_unit_tests()

```
if success:
    print("\n" + "="*50)
    run_demo()
   
    print("\n" + "="*50)
    print("📚 Docstring-Tests...")
    import doctest
    doctest.testmod(verbose=True)
   
    print("\n🎯 INTEGRA ALIGN-Prinzipien Modul ready!")
    print("💡 Verwendung: from core.align_principles import run_module")
```