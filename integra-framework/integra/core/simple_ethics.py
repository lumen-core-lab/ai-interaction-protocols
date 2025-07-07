# -*- coding: utf-8 -*-
"""
Modulname: simple_ethics.py
Beschreibung: Basis-Ethikprüfung für INTEGRA Light - minimalistische ethische Bewertung
Teil von: INTEGRA Light – Core
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Modularisiert und Baukasten-kompatibel
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import re
import json
from pathlib import Path
from functools import lru_cache

# Standardisierte Imports
try:
    from integra.core import principles
    from integra.core import profiles
except ImportError:
    import principles
    import profiles


# ============================================================================
# PATTERN DEFINITIONS (später auslagern in pattern_sets.py)
# ============================================================================

@dataclass
class PatternSet:
    """Container für ethische Bewertungsmuster."""
    name: str
    patterns: List[str]
    weight: float = 0.4
    severity: str = "violation"  # violation, warning, positive
    
    def compile_patterns(self) -> List[re.Pattern]:
        """Kompiliert alle Patterns für bessere Performance."""
        return [re.compile(pattern, re.IGNORECASE) for pattern in self.patterns]


class EthicsPatterns:
    """Zentrale Verwaltung aller ethischen Bewertungsmuster."""
    
    # Integrity-Verletzungen
    INTEGRITY_VIOLATIONS = PatternSet(
        name="integrity_violations",
        patterns=[
            r'\blüg\w*\b', r'\blie\b', r'\blying\b',
            r'\btäusch\w*\b', r'\bdeceiv\w*\b', r'\btrick\w*\b',
            r'\bverheimlich\w*\b', r'\bhide\b', r'\bconceal\w*\b',
            r'\bfälsch\w*\b', r'\bfake\b', r'\bfabricat\w*\b',
            r'\bbetrüg\w*\b', r'\bcheat\w*\b', r'\bfraud\w*\b',
            r'\bmanipulier\w*\b', r'\bmanipulat\w*\b',
            r'\bverschweig\w*\b', r'\bwithhold\w*\b',
            r'\bschwindel\w*\b', r'\bmogel\w*\b',
            r'\bunehrlich\b', r'\bunwahr\b'
        ],
        weight=0.4,
        severity="violation"
    )
    
    # Governance-Verletzungen
    GOVERNANCE_VIOLATIONS = PatternSet(
        name="governance_violations",
        patterns=[
            r'\billegal\b', r'\bgesetzwidrig\b', r'\bverboten\b',
            r'\bforbidden\b', r'\bprohibited\b',
            r'\bregel\w*\s+brech\w*\b', r'\bbreak\w*\s+rule\w*\b',
            r'\bcompliance\w*\s+verletz\w*\b', r'\bviolat\w*\s+compliance\b',
            r'\bstraf\w*tat\w*\b', r'\bcriminal\b',
            r'\bdatenschutz\w*\s+verletz\w*\b', r'\bprivacy\w*\s+violat\w*\b',
            r'\bgesetz\w*\s+brech\w*\b', r'\bvorschrift\w*\s+ignor\w*\b',
            r'\bregelwidrig\b'
        ],
        weight=0.5,
        severity="violation"
    )
    
    # Nurturing-Verletzungen
    NURTURING_VIOLATIONS = PatternSet(
        name="nurturing_violations",
        patterns=[
            r'\bschad\w*\b', r'\bharm\w*\b', r'\bhurt\w*\b', r'\binjur\w*\b',
            r'\bverletz\w*\b', r'\bwound\w*\b', r'\bdamag\w*\b',
            r'\bgefähr\w*\b', r'\bdanger\w*\b', r'\brisk\w*\b',
            r'\bvernachlässig\w*\b', r'\bneglect\w*\b',
            r'\bbedrohe\w*\b', r'\bthreaten\w*\b',
            r'\bdiskriminier\w*\b', r'\bdiscriminat\w*\b',
            r'\bmobbing\b', r'\bbullying\b',
            r'\bweh\s+tu\w*\b', r'\bangriff\w*\b', r'\battack\w*\b'
        ],
        weight=0.4,
        severity="violation"
    )
    
    # Awareness-Probleme
    AWARENESS_ISSUES = PatternSet(
        name="awareness_issues",
        patterns=[
            r'\b(unwissend|unaware|ignorant)\b',
            r'\b(risiko.*ignor|ignore.*risk)\b',
            r'\b(blind.*vertrau|blind.*trust)\b',
            r'\b(achtlos|careless|reckless)\b',
            r'\b(konsequenz.*ignor|ignore.*consequence)\b'
        ],
        weight=0.2,
        severity="warning"
    )
    
    # Learning-Hemmnisse
    LEARNING_HINDRANCES = PatternSet(
        name="learning_hindrances",
        patterns=[
            r'\b(lern.*verwiger|refuse.*learn)\b',
            r'\b(bildung.*verhinder|prevent.*education)\b',
            r'\b(wissen.*verschweig|conceal.*knowledge)\b',
            r'\b(fehler.*wiederhol|repeat.*mistake)\b',
            r'\b(beratung.*ignor|ignore.*advice)\b',
            r'\b(hausaufgaben.*mach|do.*homework)\b'
        ],
        weight=0.3,
        severity="warning"
    )
    
    # Positive Indikatoren
    POSITIVE_INDICATORS = {
        "integrity": PatternSet(
            name="integrity_positive",
            patterns=[
                r'\b(ehrlich|honest|truthful)\b',
                r'\b(transparent|offen|open)\b',
                r'\b(aufrichtig|sincere|genuine)\b'
            ],
            weight=0.1,
            severity="positive"
        ),
        "governance": PatternSet(
            name="governance_positive",
            patterns=[
                r'\b(legal|rechtmäßig|lawful)\b',
                r'\b(regel.*befolg|follow.*rule)\b',
                r'\b(compliance|konform)\b'
            ],
            weight=0.1,
            severity="positive"
        ),
        "nurturing": PatternSet(
            name="nurturing_positive",
            patterns=[
                r'\b(helfen|help|assist|support)\b',
                r'\b(fürsorge|care|protect)\b',
                r'\b(unterstütz|förder|encourag)\b'
            ],
            weight=0.1,
            severity="positive"
        ),
        "awareness": PatternSet(
            name="awareness_positive",
            patterns=[
                r'\b(bewusst|aware|conscious)\b',
                r'\b(aufmerksam|attentive|mindful)\b',
                r'\b(vorsichtig|careful|cautious)\b'
            ],
            weight=0.1,
            severity="positive"
        ),
        "learning": PatternSet(
            name="learning_positive",
            patterns=[
                r'\b(lern|learn|study)\b',
                r'\b(bildung|education|knowledge)\b',
                r'\b(versteh|understand|comprehend)\b'
            ],
            weight=0.1,
            severity="positive"
        )
    }
    
    @classmethod
    def get_all_pattern_sets(cls) -> Dict[str, PatternSet]:
        """Gibt alle PatternSets zurück."""
        return {
            "integrity_violations": cls.INTEGRITY_VIOLATIONS,
            "governance_violations": cls.GOVERNANCE_VIOLATIONS,
            "nurturing_violations": cls.NURTURING_VIOLATIONS,
            "awareness_issues": cls.AWARENESS_ISSUES,
            "learning_hindrances": cls.LEARNING_HINDRANCES,
            **{f"{k}_positive": v for k, v in cls.POSITIVE_INDICATORS.items()}
        }


# ============================================================================
# CONTEXT ANALYSIS
# ============================================================================

@dataclass
class ContextFactors:
    """Container für erkannte Kontext-Faktoren."""
    question: bool = False
    hypothetical: bool = False
    educational: bool = False
    emergency: bool = False
    children: bool = False
    public: bool = False
    private: bool = False
    
    def get_active_factors(self) -> List[str]:
        """Gibt Liste aktiver Faktoren zurück."""
        return [k for k, v in self.__dict__.items() if v]
    
    def to_dict(self) -> Dict[str, bool]:
        """Konvertiert zu Dictionary."""
        return self.__dict__.copy()


class ContextAnalyzer:
    """Analysiert Kontext-Faktoren in Texten."""
    
    # Kontext-Modifikatoren (konfigurierbar)
    CONTEXT_MODIFIERS = {
        "question": 0.1,        # Fragen sind weniger problematisch
        "hypothetical": 0.2,    # Hypothetische Szenarien
        "educational": -0.1,    # Bildungskontext ist positiv
        "emergency": 0.3,       # Notfälle erhöhen Komplexität
        "children": 0.2,        # Kinder-Kontext erhöht Vorsicht
        "public": 0.1,          # Öffentlicher Kontext
        "private": -0.1         # Privater Kontext
    }
    
    @staticmethod
    def analyze(text: str) -> ContextFactors:
        """Analysiert Kontext-Faktoren im Text."""
        text_lower = text.lower()
        
        return ContextFactors(
            question="?" in text or any(phrase in text_lower for phrase in ["soll ich", "darf ich", "should i", "may i"]),
            hypothetical=any(word in text_lower for word in ["wenn", "falls", "angenommen", "if", "suppose"]),
            educational=any(word in text_lower for word in ["lern", "learn", "unterricht", "school", "bildung"]),
            emergency=any(word in text_lower for word in ["notfall", "emergency", "dringend", "urgent"]),
            children=any(word in text_lower for word in ["kind", "child", "schüler", "student", "minderjährig"]),
            public=any(word in text_lower for word in ["öffentlich", "public", "publikum", "audience"]),
            private=any(word in text_lower for word in ["privat", "private", "vertraulich", "confidential"])
        )
    
    @classmethod
    def apply_modifiers(cls, scores: Dict[str, float], context: ContextFactors) -> None:
        """Wendet Kontext-Modifikatoren auf Scores an."""
        for factor, modifier in cls.CONTEXT_MODIFIERS.items():
            if getattr(context, factor, False):
                for principle in scores:
                    if modifier > 0:  # Erhöht Vorsicht
                        scores[principle] = max(0.0, scores[principle] - modifier)
                    else:  # Verringert Bedenken
                        scores[principle] = min(1.0, scores[principle] - modifier)


# ============================================================================
# SCORING ENGINE
# ============================================================================

@dataclass
class EvaluationResult:
    """Container für Bewertungsergebnisse."""
    scores: Dict[str, float]
    weighted_scores: Dict[str, float]
    overall_score: float
    violations: List[str]
    warnings: List[str]
    comments: Dict[str, str]
    context_factors: ContextFactors
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für JSON-Serialisierung."""
        return {
            "scores": self.scores,
            "weighted_scores": self.weighted_scores,
            "overall_score": self.overall_score,
            "violations": self.violations,
            "warnings": self.warnings,
            "comments": self.comments,
            "context_factors": self.context_factors.to_dict(),
            "confidence": self.confidence,
            "timestamp": datetime.now().isoformat(),
            "evaluation_method": "simple_ethics_v2.0",
            **self.metadata
        }


class ScoringEngine:
    """Berechnet ethische Scores basierend auf Pattern-Matches."""
    
    @staticmethod
    def calculate_principle_score(text: str, pattern_set: PatternSet, 
                                 positive_patterns: Optional[PatternSet] = None) -> Tuple[float, List[str]]:
        """
        Berechnet Score für ein einzelnes Prinzip.
        
        Returns:
            Tuple aus (score, gefundene_issues)
        """
        score = 1.0
        issues = []
        
        # Negative Patterns prüfen
        for pattern in pattern_set.compile_patterns():
            if pattern.search(text):
                score -= pattern_set.weight
                issues.append(pattern_set.name)
                break  # Nur einmal abziehen
        
        # Positive Patterns prüfen
        if positive_patterns:
            for pattern in positive_patterns.compile_patterns():
                if pattern.search(text):
                    score = min(1.0, score + positive_patterns.weight)
                    break
        
        return max(0.0, score), issues
    
    @staticmethod
    def apply_profile_weighting(scores: Dict[str, float], 
                               profile: Dict[str, float]) -> Dict[str, float]:
        """Wendet Profil-Gewichtungen auf Scores an."""
        weighted = {}
        for principle in principles.ALIGN_KEYS:
            weight = profile.get(principle, 1.0)
            weighted[principle] = scores.get(principle, 1.0) * weight
        return weighted
    
    @staticmethod
    def calculate_confidence(scores: Dict[str, float], 
                           violations: List[str], 
                           warnings: List[str]) -> float:
        """Berechnet Konfidenz der Bewertung."""
        confidence = 0.8
        
        # Reduziere bei unklaren Scores
        for score in scores.values():
            if 0.4 <= score <= 0.6:
                confidence -= 0.1
        
        # Erhöhe bei klaren Verletzungen
        if violations:
            confidence += 0.1
        
        # Reduziere bei vielen Warnungen
        if len(warnings) > 2:
            confidence -= 0.1
        
        return max(0.1, min(0.95, confidence))


# ============================================================================
# MAIN EVALUATOR
# ============================================================================

class EthicsEvaluator:
    """
    Haupt-Evaluator für ethische Bewertungen.
    Modularisiert und erweiterbar.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert den Evaluator.
        
        Args:
            config: Optionale Konfiguration (für spätere Erweiterungen)
        """
        self.config = config or {}
        self.patterns = EthicsPatterns()
        self.context_analyzer = ContextAnalyzer()
        self.scoring_engine = ScoringEngine()
        
        # Cache für Performance (optional)
        self._use_cache = self.config.get("use_cache", False)
        if self._use_cache:
            self.evaluate_ethics = lru_cache(maxsize=128)(self.evaluate_ethics)
    
    def evaluate_ethics(self, user_input: str, 
                       profile: Optional[Dict[str, float]] = None) -> EvaluationResult:
        """
        Hauptmethode zur ethischen Bewertung.
        
        Args:
            user_input: Zu bewertender Text
            profile: Ethisches Profil für Gewichtung
            
        Returns:
            EvaluationResult mit vollständiger Bewertung
        """
        # Validierung
        if not user_input or not isinstance(user_input, str):
            return self._create_error_result("Ungültige Eingabe")
        
        # Profil laden
        if profile is None:
            profile = profiles.get_default_profile()
        
        # Text normalisieren
        text_lower = user_input.lower()
        
        # Initialisierung
        scores = {principle: 1.0 for principle in principles.ALIGN_KEYS}
        all_violations = []
        all_warnings = []
        comments = {}
        
        # Kontext analysieren
        context_factors = self.context_analyzer.analyze(text_lower)
        
        # Integrity bewerten
        score, issues = self.scoring_engine.calculate_principle_score(
            text_lower,
            self.patterns.INTEGRITY_VIOLATIONS,
            self.patterns.POSITIVE_INDICATORS.get("integrity")
        )
        scores["integrity"] = score
        if issues:
            all_violations.extend(issues)
            comments["integrity"] = "Integritätsprobleme erkannt"
        
        # Governance bewerten
        score, issues = self.scoring_engine.calculate_principle_score(
            text_lower,
            self.patterns.GOVERNANCE_VIOLATIONS,
            self.patterns.POSITIVE_INDICATORS.get("governance")
        )
        scores["governance"] = score
        if issues:
            all_violations.extend(issues)
            comments["governance"] = "Governance-Bedenken"
        
        # Nurturing bewerten
        score, issues = self.scoring_engine.calculate_principle_score(
            text_lower,
            self.patterns.NURTURING_VIOLATIONS,
            self.patterns.POSITIVE_INDICATORS.get("nurturing")
        )
        scores["nurturing"] = score
        if issues:
            if score < 0.5:
                all_violations.extend(issues)
            else:
                all_warnings.extend(issues)
            comments["nurturing"] = "Fürsorge-Aspekte zu beachten"
        
        # Awareness bewerten
        score, issues = self.scoring_engine.calculate_principle_score(
            text_lower,
            self.patterns.AWARENESS_ISSUES,
            self.patterns.POSITIVE_INDICATORS.get("awareness")
        )
        scores["awareness"] = score
        if issues:
            all_warnings.extend(issues)
            comments["awareness"] = "Bewusstseins-Hinweise"
        
        # Learning bewerten
        score, issues = self.scoring_engine.calculate_principle_score(
            text_lower,
            self.patterns.LEARNING_HINDRANCES,
            self.patterns.POSITIVE_INDICATORS.get("learning")
        )
        scores["learning"] = score
        if issues:
            all_warnings.extend(issues)
            comments["learning"] = "Lern-Aspekte betroffen"
        
        # Kontext-Modifikatoren anwenden
        self.context_analyzer.apply_modifiers(scores, context_factors)
        
        # Profil-Gewichtung
        weighted_scores = self.scoring_engine.apply_profile_weighting(scores, profile)
        
        # Gesamt-Score
        overall_score = sum(weighted_scores.values()) / len(weighted_scores)
        
        # Konfidenz berechnen
        confidence = self.scoring_engine.calculate_confidence(
            scores, all_violations, all_warnings
        )
        
        # Ergebnis erstellen
        return EvaluationResult(
            scores=scores,
            weighted_scores=weighted_scores,
            overall_score=overall_score,
            violations=list(set(all_violations)),
            warnings=list(set(all_warnings)),
            comments=comments,
            context_factors=context_factors,
            confidence=confidence,
            metadata={
                "profile_used": profile,
                "text_length": len(user_input),
                "active_context_factors": context_factors.get_active_factors()
            }
        )
    
    def _create_error_result(self, error_message: str) -> EvaluationResult:
        """Erstellt ein Fehler-Ergebnis."""
        default_scores = {p: 0.5 for p in principles.ALIGN_KEYS}
        return EvaluationResult(
            scores=default_scores,
            weighted_scores=default_scores,
            overall_score=0.5,
            violations=[],
            warnings=[error_message],
            comments={"error": error_message},
            context_factors=ContextFactors(),
            confidence=0.1,
            metadata={"error": True}
        )


# ============================================================================
# MODULE INTERFACE (BAUKASTEN)
# ============================================================================

# Globale Instanz
_evaluator = None

def get_evaluator() -> EthicsEvaluator:
    """Lazy-Loading des Evaluators."""
    global _evaluator
    if _evaluator is None:
        _evaluator = EthicsEvaluator()
    return _evaluator


def run_module(input_data: Dict[str, Any], 
               profile: Dict[str, float], 
               context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hauptfunktion für die Baukasten-Integration.
    
    Args:
        input_data: Dictionary mit Eingabedaten
            - text: Zu bewertender Text (required)
            - config: Optionale Konfiguration
        profile: Aktuelles ethisches Profil
        context: Laufender Kontext (wird erweitert)
        
    Returns:
        Erweiterter Kontext mit Ergebnis in context["simple_ethics_result"]
    """
    try:
        # Text extrahieren
        text = input_data.get("text", "")
        if not text:
            raise ValueError("Kein Text in input_data gefunden")
        
        # Evaluator holen
        evaluator = get_evaluator()
        
        # Bewertung durchführen
        result = evaluator.evaluate_ethics(text, profile)
        
        # In Kontext speichern
        context["simple_ethics_result"] = {
            "status": "success",
            "evaluation": result.to_dict(),
            "summary": {
                "overall_score": result.overall_score,
                "violations_count": len(result.violations),
                "warnings_count": len(result.warnings),
                "confidence": result.confidence,
                "risk_level": _determine_risk_level(result.overall_score)
            },
            "module": "simple_ethics",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Fehlerbehandlung
        context["simple_ethics_result"] = {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "module": "simple_ethics",
            "timestamp": datetime.now().isoformat()
        }
    
    return context


def _determine_risk_level(score: float) -> str:
    """Bestimmt Risiko-Level basierend auf Score."""
    if score < 0.3:
        return "critical"
    elif score < 0.5:
        return "high"
    elif score < 0.7:
        return "medium"
    elif score < 0.9:
        return "low"
    else:
        return "minimal"


# Rückwärtskompatibilität
def evaluate_ethics(user_input: str, 
                   profile: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Legacy-Funktion für Rückwärtskompatibilität."""
    evaluator = get_evaluator()
    result = evaluator.evaluate_ethics(user_input, profile)
    return result.to_dict()


def demo():
    """Demonstriert die Verwendung des simple_ethics-Moduls."""
    print("=== INTEGRA Simple Ethics Demo (Version 2.0) ===")
    print()
    
    # Test 1: Basis-Bewertung
    print("1. Test: Basis-Bewertung")
    context = {}
    profile = profiles.get_default_profile()
    input_data = {
        "text": "Soll ich jemandem bei den Hausaufgaben helfen?"
    }
    
    context = run_module(input_data, profile, context)
    result = context["simple_ethics_result"]
    
    if result["status"] == "success":
        summary = result["summary"]
        print(f"   Overall Score: {summary['overall_score']:.2f}")
        print(f"   Risk Level: {summary['risk_level']}")
        print(f"   Violations: {summary['violations_count']}")
        print(f"   Confidence: {summary['confidence']:.2f}")
    print()
    
    # Test 2: Verschiedene Szenarien
    print("2. Test: Verschiedene Szenarien")
    test_cases = [
        ("Ich werde ehrlich und transparent sein.", "positive"),
        ("Darf ich private Daten ohne Erlaubnis nutzen?", "governance"),
        ("Soll ich lügen, um jemanden zu schützen?", "integrity"),
        ("Wie kann ich beim Lernen helfen?", "learning")
    ]
    
    for text, expected in test_cases:
        input_data = {"text": text}
        context = run_module(input_data, profile, {})
        
        if context["simple_ethics_result"]["status"] == "success":
            eval_data = context["simple_ethics_result"]["evaluation"]
            score = eval_data["overall_score"]
            violations = eval_data["violations"]
            
            print(f"   '{text[:40]}...'")
            print(f"     Score: {score:.2f}, Violations: {violations}")
            print(f"     Expected: {expected}")
        print()
    
    # Test 3: Kontext-Faktoren
    print("3. Test: Kontext-Faktoren")
    input_data = {
        "text": "In einem Notfall: Soll ich die Regel brechen?"
    }
    context = run_module(input_data, profile, {})
    
    if context["simple_ethics_result"]["status"] == "success":
        eval_data = context["simple_ethics_result"]["evaluation"]
        context_factors = eval_data["context_factors"]
        print(f"   Erkannte Faktoren: {[k for k, v in context_factors.items() if v]}")
        print(f"   Score mit Kontext: {eval_data['overall_score']:.2f}")
    
    print("\n=== Demo abgeschlossen ===")


if __name__ == "__main__":
    demo()