# -*- coding: utf-8 -*-
"""
Modulname: decision_engine.py
Beschreibung: Fast/Deep Path Routing für INTEGRA Light - Herzstück der Entscheidungslogik
Teil von: INTEGRA Light – Core
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Baukasten-kompatibel mit verbesserter Modularität
"""

from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

# Standardisierte Imports
try:
    from integra.core import principles
    from integra.core import profiles  
    from integra.core import simple_ethics
except ImportError:
    import principles
    import profiles
    import simple_ethics


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class PathType(Enum):
    """Definiert die möglichen Entscheidungspfade."""
    FAST = "fast"
    DEEP = "deep"
    ERROR = "error"


class QuestionType(Enum):
    """Klassifizierung von Fragetypen."""
    DECISION = "decision"
    EXPLANATION = "explanation"
    FACTUAL = "factual"
    ETHICAL = "ethical"
    GENERAL = "general"


@dataclass
class AnalysisResult:
    """Container für Analyse-Ergebnisse."""
    triggered_ethics: List[str] = field(default_factory=list)
    complexity_flags: List[str] = field(default_factory=list)
    question_type: QuestionType = QuestionType.GENERAL
    risk_score: float = 0.0
    input_length: int = 0
    has_question_mark: bool = False
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "triggered_ethics": self.triggered_ethics,
            "complexity_flags": self.complexity_flags,
            "question_type": self.question_type.value,
            "risk_score": self.risk_score,
            "input_length": self.input_length,
            "has_question_mark": self.has_question_mark,
            "confidence": self.confidence
        }


@dataclass
class DecisionResult:
    """Container für Entscheidungsergebnisse."""
    decision_id: str
    path: PathType
    response: str
    analysis: AnalysisResult
    confidence: float
    ethics_check: bool
    timestamp: str
    processing_time: str
    ethics_result: Optional[Dict[str, Any]] = None
    advanced_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        result = {
            "decision_id": self.decision_id,
            "path": self.path.value,
            "response": self.response,
            "analysis": self.analysis.to_dict(),
            "confidence": self.confidence,
            "ethics_check": self.ethics_check,
            "timestamp": self.timestamp,
            "processing_time": self.processing_time
        }
        
        if self.ethics_result:
            result["ethics"] = self.ethics_result
            
        if self.advanced_results:
            result.update(self.advanced_results)
            
        return result


# ============================================================================
# TRIGGER DEFINITIONS
# ============================================================================

class TriggerSets:
    """Zentrale Verwaltung von Trigger-Keywords."""
    
    # Ethische Trigger-Keywords
    ETHICAL_TRIGGERS = {
        "help": ["helfen", "help", "unterstützen", "support", "beistehen", "assist"],
        "harm": ["schaden", "harm", "verletzen", "hurt", "gefahr", "danger", "risiko", "risk"],
        "deception": ["lügen", "lie", "verheimlichen", "hide", "täuschen", "deceive", "betrügen", "cheat"],
        "legal": ["illegal", "verboten", "forbidden", "gesetz", "law", "recht", "legal"],
        "privacy": ["privat", "private", "daten", "data", "persönlich", "personal", "datenschutz"],
        "discrimination": ["diskriminierung", "discrimination", "vorurteil", "bias", "unfair"],
        "autonomy": ["entscheiden", "decide", "wählen", "choose", "zwingen", "force", "autonom"]
    }
    
    # Komplexitäts-Indikatoren
    COMPLEXITY_INDICATORS = [
        "aber", "however", "allerdings", "dennoch",
        "einerseits", "andererseits", "on one hand", "on the other hand",
        "konflikt", "conflict", "dilemma", "zwiespalt",
        "schwierig", "difficult", "komplex", "complex",
        "unsicher", "uncertain", "unklar", "unclear",
        "mehrere", "multiple", "verschiedene", "various"
    ]
    
    # Frage-Indikatoren
    QUESTION_INDICATORS = {
        "decision": ["soll ich", "should i", "darf ich", "may i", "kann ich", "can i"],
        "explanation": ["warum", "why", "wie", "how", "weshalb", "wieso"],
        "factual": ["was ist", "what is", "wer ist", "who is", "wann", "when", "wo", "where"]
    }
    
    @classmethod
    def get_all_ethical_triggers(cls) -> List[str]:
        """Gibt alle ethischen Trigger als flache Liste zurück."""
        triggers = []
        for trigger_list in cls.ETHICAL_TRIGGERS.values():
            triggers.extend(trigger_list)
        return triggers


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

class InputAnalyzer:
    """Analysiert Benutzereingaben auf ethische Relevanz und Komplexität."""
    
    def __init__(self):
        """Initialisiert den Analyzer."""
        self.triggers = TriggerSets()
        
    def analyze(self, user_input: str) -> AnalysisResult:
        """
        Führt eine vollständige Analyse der Eingabe durch.
        
        Args:
            user_input: Zu analysierende Eingabe
            
        Returns:
            AnalysisResult mit allen Analysedaten
        """
        if not user_input:
            return AnalysisResult()
            
        lower_input = user_input.lower()
        
        # Ethische Trigger erkennen
        triggered_ethics = self._find_ethical_triggers(lower_input)
        
        # Komplexität analysieren
        complexity_flags = self._find_complexity_indicators(lower_input)
        
        # Fragetyp bestimmen
        question_type = self._classify_question_type(lower_input)
        
        # Risiko berechnen
        risk_score = self._calculate_risk_score(
            triggered_ethics, complexity_flags, question_type
        )
        
        # Konfidenz berechnen
        confidence = self._calculate_confidence(
            len(triggered_ethics), len(complexity_flags), question_type
        )
        
        return AnalysisResult(
            triggered_ethics=triggered_ethics,
            complexity_flags=complexity_flags,
            question_type=question_type,
            risk_score=risk_score,
            input_length=len(user_input),
            has_question_mark="?" in user_input,
            confidence=confidence
        )
    
    def _find_ethical_triggers(self, text: str) -> List[str]:
        """Findet ethische Trigger im Text."""
        found_triggers = []
        
        for category, keywords in self.triggers.ETHICAL_TRIGGERS.items():
            for keyword in keywords:
                if keyword in text:
                    found_triggers.append(f"{category}:{keyword}")
                    break  # Nur einen Trigger pro Kategorie
                    
        return found_triggers
    
    def _find_complexity_indicators(self, text: str) -> List[str]:
        """Findet Komplexitätsindikatoren im Text."""
        return [
            indicator for indicator in self.triggers.COMPLEXITY_INDICATORS
            if indicator in text
        ]
    
    def _classify_question_type(self, text: str) -> QuestionType:
        """Klassifiziert den Fragetyp."""
        # Prüfe spezifische Indikatoren
        for q_type, indicators in self.triggers.QUESTION_INDICATORS.items():
            if any(indicator in text for indicator in indicators):
                return QuestionType(q_type)
        
        # Prüfe auf ethische Keywords
        if any(keyword in text for keywords in self.triggers.ETHICAL_TRIGGERS.values() 
               for keyword in keywords):
            return QuestionType.ETHICAL
            
        return QuestionType.GENERAL
    
    def _calculate_risk_score(self, triggers: List[str], 
                            complexity: List[str], 
                            q_type: QuestionType) -> float:
        """Berechnet einen Risiko-Score."""
        score = 0.0
        
        # Trigger gewichten (mehr = höher)
        score += len(triggers) * 0.2
        
        # Komplexität gewichten
        score += len(complexity) * 0.1
        
        # Fragetyp gewichten
        type_weights = {
            QuestionType.DECISION: 0.3,
            QuestionType.ETHICAL: 0.4,
            QuestionType.EXPLANATION: 0.1,
            QuestionType.FACTUAL: 0.0,
            QuestionType.GENERAL: 0.1
        }
        score += type_weights.get(q_type, 0.1)
        
        return min(1.0, score)
    
    def _calculate_confidence(self, trigger_count: int, 
                            complexity_count: int,
                            q_type: QuestionType) -> float:
        """Berechnet die Analyse-Konfidenz."""
        confidence = 0.8
        
        # Klare Trigger erhöhen Konfidenz
        if trigger_count > 0:
            confidence += 0.1
            
        # Zu viele Trigger reduzieren Konfidenz (verwirrend)
        if trigger_count > 3:
            confidence -= 0.1
            
        # Komplexität reduziert Konfidenz
        if complexity_count > 2:
            confidence -= 0.1
            
        # Klare Fragetypen erhöhen Konfidenz
        if q_type in [QuestionType.FACTUAL, QuestionType.DECISION]:
            confidence += 0.05
            
        return max(0.3, min(0.95, confidence))


# ============================================================================
# RESPONSE GENERATOR
# ============================================================================

class ResponseGenerator:
    """Generiert kontextgerechte Antworten."""
    
    @staticmethod
    def generate_fast_response(user_input: str, analysis: AnalysisResult) -> str:
        """Generiert eine Fast-Path-Antwort."""
        templates = {
            QuestionType.FACTUAL: "Ihre Faktenfrage '{input}' kann ich gerne beantworten.",
            QuestionType.GENERAL: "Ich habe Ihre Anfrage '{input}' erhalten.",
            QuestionType.EXPLANATION: "Gerne erkläre ich Ihnen das näher: '{input}'",
            QuestionType.DECISION: "Ihre Entscheidungsfrage '{input}' erfordert keine ethische Prüfung.",
            QuestionType.ETHICAL: "Ihre Anfrage '{input}' wurde als unkritisch eingestuft."
        }
        
        template = templates.get(analysis.question_type, templates[QuestionType.GENERAL])
        
        # Eingabe kürzen wenn zu lang
        shortened_input = user_input[:50] + "..." if len(user_input) > 50 else user_input
        
        return template.format(input=shortened_input)
    
    @staticmethod
    def generate_deep_response(user_input: str, 
                             ethics_result: Dict[str, Any],
                             analysis: AnalysisResult,
                             advanced_results: Dict[str, Any]) -> str:
        """Generiert eine Deep-Path-Antwort mit ethischer Reflexion."""
        violations = ethics_result.get("violations", [])
        overall_score = ethics_result.get("overall_score", 0.5)
        
        response_parts = []
        
        # Eingabe kürzen
        shortened_input = user_input[:50] + "..." if len(user_input) > 50 else user_input
        
        # Einleitung
        response_parts.append(f"Ihre Anfrage '{shortened_input}' wurde ethisch analysiert.")
        
        # Violations behandeln
        if violations:
            violation_str = ", ".join(set(violations[:3]))  # Max 3 anzeigen
            response_parts.append(f"Dabei wurden Bedenken identifiziert: {violation_str}.")
            
            # Advanced Module Empfehlungen
            if "etb" in advanced_results and advanced_results["etb"].get("recommendation"):
                response_parts.append(advanced_results["etb"]["recommendation"])
                
            if "pae" in advanced_results and advanced_results["pae"].get("priority"):
                priority = advanced_results["pae"]["priority"]
                response_parts.append(f"Priorität liegt auf: {priority.title()}.")
                
        else:
            # Keine Violations
            if overall_score > 0.8:
                response_parts.append("Die Analyse zeigt keine ethischen Bedenken.")
                
                if analysis.triggered_ethics:
                    response_parts.append("Relevante ethische Aspekte wurden berücksichtigt.")
                    
            else:
                response_parts.append("Die Situation erfordert eine ausgewogene Betrachtung.")
                
                # ETB Balancing Info
                if "etb" in advanced_results and advanced_results["etb"].get("conflicts"):
                    response_parts.append("Es wurden ethische Zielkonflikte identifiziert.")
        
        # Abschluss
        response_parts.append("Ich stehe für eine verantwortungsvolle Unterstützung bereit.")
        
        return " ".join(response_parts)


# ============================================================================
# DECISION ENGINE
# ============================================================================

class DecisionEngine:
    """
    Zentrale Entscheidungsmaschine für INTEGRA Light.
    Orchestriert Fast/Deep Path Routing und Module.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert die Decision Engine.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        self.analyzer = InputAnalyzer()
        self.response_generator = ResponseGenerator()
        
        # Statistiken
        self.decision_count = 0
        self.last_decision_time = None
        
        # Advanced Module Verfügbarkeit prüfen
        self._check_advanced_modules()
        
    def _check_advanced_modules(self) -> None:
        """Prüft Verfügbarkeit von Advanced Modulen."""
        self.advanced_available = {
            "etb": False,
            "pae": False,
            "mini_audit": False,
            "mini_learner": False
        }
        
        # Nur prüfen wenn in Config aktiviert
        if not self.config.get("use_advanced", True):
            return
            
        # ETB verfügbar?
        try:
            from integra.advanced import etb
            self.advanced_available["etb"] = True
        except ImportError:
            pass
            
        # PAE verfügbar?
        try:
            from integra.advanced import pae
            self.advanced_available["pae"] = True
        except ImportError:
            pass
            
        # Audit verfügbar?
        try:
            from integra.advanced import mini_audit
            self.advanced_available["mini_audit"] = True
        except ImportError:
            pass
    
    def make_decision(self, user_input: str, 
                     profile: Dict[str, float],
                     context: Dict[str, Any]) -> DecisionResult:
        """
        Hauptmethode für Entscheidungen.
        
        Args:
            user_input: Benutzereingabe
            profile: Ethisches Profil
            context: Aktueller Kontext
            
        Returns:
            DecisionResult mit vollständiger Entscheidung
        """
        # Entscheidungs-ID generieren
        decision_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        
        # Statistiken aktualisieren
        self.decision_count += 1
        self.last_decision_time = timestamp
        
        # Eingabe analysieren
        analysis = self.analyzer.analyze(user_input)
        
        # Pfadentscheidung
        needs_ethics = self._needs_ethics_check(analysis)
        
        if needs_ethics:
            result = self._execute_deep_path(
                user_input, analysis, profile, context, decision_id, timestamp
            )
        else:
            result = self._execute_fast_path(
                user_input, analysis, decision_id, timestamp
            )
            
        return result
    
    def _needs_ethics_check(self, analysis: AnalysisResult) -> bool:
        """Entscheidet ob Deep Path nötig ist."""
        # Ethische Trigger gefunden
        if analysis.triggered_ethics:
            return True
            
        # Hoher Risiko-Score
        if analysis.risk_score > 0.3:
            return True
            
        # Komplexe ethische Fragen
        if (analysis.complexity_flags and 
            analysis.question_type in [QuestionType.ETHICAL, QuestionType.DECISION]):
            return True
            
        return False
    
    def _execute_fast_path(self, user_input: str, 
                          analysis: AnalysisResult,
                          decision_id: str,
                          timestamp: datetime) -> DecisionResult:
        """Führt Fast Path aus."""
        response = self.response_generator.generate_fast_response(user_input, analysis)
        
        return DecisionResult(
            decision_id=decision_id,
            path=PathType.FAST,
            response=response,
            analysis=analysis,
            confidence=analysis.confidence,
            ethics_check=False,
            timestamp=timestamp.isoformat(),
            processing_time="<1ms"
        )
    
    def _execute_deep_path(self, user_input: str,
                          analysis: AnalysisResult,
                          profile: Dict[str, float],
                          context: Dict[str, Any],
                          decision_id: str,
                          timestamp: datetime) -> DecisionResult:
        """Führt Deep Path mit ethischer Analyse aus."""
        start_time = datetime.now()
        
        # Simple Ethics ausführen
        ethics_context = {}
        ethics_input = {"text": user_input}
        ethics_context = simple_ethics.run_module(ethics_input, profile, ethics_context)
        
        ethics_result = {}
        if ethics_context.get("simple_ethics_result", {}).get("status") == "success":
            ethics_result = ethics_context["simple_ethics_result"]["evaluation"]
        
        # Advanced Module ausführen (wenn verfügbar)
        advanced_results = self._run_advanced_modules(
            user_input, ethics_result, profile, context
        )
        
        # Response generieren
        response = self.response_generator.generate_deep_response(
            user_input, ethics_result, analysis, advanced_results
        )
        
        # Konfidenz berechnen
        confidence = self._calculate_combined_confidence(
            analysis.confidence,
            ethics_result.get("confidence", 0.5),
            advanced_results
        )
        
        # Processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return DecisionResult(
            decision_id=decision_id,
            path=PathType.DEEP,
            response=response,
            analysis=analysis,
            confidence=confidence,
            ethics_check=True,
            timestamp=timestamp.isoformat(),
            processing_time=f"{processing_time:.1f}ms",
            ethics_result=ethics_result,
            advanced_results=advanced_results
        )
    
    def _run_advanced_modules(self, user_input: str,
                            ethics_result: Dict[str, Any],
                            profile: Dict[str, float],
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Führt verfügbare Advanced Module aus."""
        results = {}
        
        # ETB ausführen wenn verfügbar
        if self.advanced_available["etb"] and ethics_result.get("scores"):
            try:
                from integra.advanced import etb
                etb_context = {}
                etb_input = {
                    "scores": ethics_result["scores"],
                    "violations": ethics_result.get("violations", [])
                }
                etb_context = etb.run_module(etb_input, profile, etb_context)
                
                if etb_context.get("etb_result", {}).get("status") == "success":
                    results["etb"] = etb_context["etb_result"]["data"]
            except Exception:
                pass
                
        # PAE ausführen wenn Konflikte erkannt
        if (self.advanced_available["pae"] and 
            results.get("etb", {}).get("conflicts_detected")):
            try:
                from integra.advanced import pae
                pae_context = {}
                pae_input = {
                    "conflicts": results["etb"]["conflicts_detected"],
                    "scores": results["etb"].get("balanced_scores", {})
                }
                pae_context = pae.run_module(pae_input, profile, pae_context)
                
                if pae_context.get("pae_result", {}).get("status") == "success":
                    results["pae"] = pae_context["pae_result"]["data"]
            except Exception:
                pass
                
        return results
    
    def _calculate_combined_confidence(self, analysis_conf: float,
                                     ethics_conf: float,
                                     advanced: Dict[str, Any]) -> float:
        """Berechnet kombinierte Konfidenz."""
        confidences = [analysis_conf, ethics_conf]
        
        # Advanced Module Konfidenzen
        if "etb" in advanced and "confidence" in advanced["etb"]:
            confidences.append(advanced["etb"]["confidence"])
            
        if "pae" in advanced and "confidence" in advanced["pae"]:
            confidences.append(advanced["pae"]["confidence"])
            
        # Gewichteter Durchschnitt
        return sum(confidences) / len(confidences)
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken zurück."""
        return {
            "total_decisions": self.decision_count,
            "last_decision": self.last_decision_time.isoformat() if self.last_decision_time else None,
            "advanced_modules": self.advanced_available,
            "config": self.config
        }


# ============================================================================
# MODULE INTERFACE (BAUKASTEN)
# ============================================================================

# Globale Engine Instanz
_engine = None

def get_engine() -> DecisionEngine:
    """Lazy-Loading der Engine."""
    global _engine
    if _engine is None:
        _engine = DecisionEngine()
    return _engine


def run_module(input_data: Dict[str, Any], 
               profile: Dict[str, float], 
               context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hauptfunktion für die Baukasten-Integration.
    
    Args:
        input_data: Dictionary mit Eingabedaten
            - text: Zu analysierende Eingabe (required)
            - config: Optionale Engine-Konfiguration
        profile: Aktuelles ethisches Profil
        context: Laufender Kontext (wird erweitert)
        
    Returns:
        Erweiterter Kontext mit Ergebnis in context["decision_engine_result"]
    """
    try:
        # Text extrahieren
        text = input_data.get("text", "")
        if not text:
            raise ValueError("Kein Text in input_data gefunden")
        
        # Config extrahieren
        config = input_data.get("config", {})
        
        # Engine erstellen oder global nutzen
        if config:
            engine = DecisionEngine(config)
        else:
            engine = get_engine()
        
        # Entscheidung treffen
        decision = engine.make_decision(text, profile, context)
        
        # In Kontext speichern
        context["decision_engine_result"] = {
            "status": "success",
            "decision": decision.to_dict(),
            "summary": {
                "path": decision.path.value,
                "confidence": decision.confidence,
                "ethics_required": decision.ethics_check,
                "triggered_categories": len(decision.analysis.triggered_ethics),
                "processing_time": decision.processing_time
            },
            "module": "decision_engine",
            "timestamp": datetime.now().isoformat()
        }
        
        # Audit wenn aktiviert
        if engine.advanced_available.get("mini_audit") and config.get("enable_audit", True):
            try:
                from integra.advanced import mini_audit
                audit_input = {
                    "action": "log_decision",
                    "decision": decision.to_dict()
                }
                context = mini_audit.run_module(audit_input, profile, context)
            except Exception:
                pass
                
    except Exception as e:
        # Fehlerbehandlung
        context["decision_engine_result"] = {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "module": "decision_engine",
            "timestamp": datetime.now().isoformat()
        }
    
    return context


def demo():
    """Demonstriert die Decision Engine."""
    print("=== INTEGRA Decision Engine Demo (Version 2.0) ===")
    print()
    
    # Test 1: Fast Path
    print("1. Test: Fast Path")
    context = {}
    profile = profiles.get_default_profile()
    input_data = {"text": "Wie spät ist es?"}
    
    context = run_module(input_data, profile, context)
    result = context["decision_engine_result"]
    
    if result["status"] == "success":
        summary = result["summary"]
        print(f"   Path: {summary['path']}")
        print(f"   Confidence: {summary['confidence']:.2f}")
        print(f"   Ethics Check: {summary['ethics_required']}")
    print()
    
    # Test 2: Deep Path
    print("2. Test: Deep Path")
    input_data = {"text": "Soll ich lügen, um jemanden zu schützen?"}
    context = run_module(input_data, profile, {})
    
    if context["decision_engine_result"]["status"] == "success":
        decision = context["decision_engine_result"]["decision"]
        print(f"   Path: {decision['path']}")
        print(f"   Response: {decision['response'][:80]}...")
        if "ethics" in decision:
            print(f"   Ethics Score: {decision['ethics'].get('overall_score', 0):.2f}")
            print(f"   Violations: {decision['ethics'].get('violations', [])}")
    print()
    
    # Test 3: Verschiedene Szenarien
    print("3. Test: Verschiedene Szenarien")
    test_cases = [
        ("Was ist 2+2?", "factual", "fast"),
        ("Darf ich private Daten nutzen?", "ethical", "deep"),
        ("Erkläre mir Photosynthese", "explanation", "fast"),
        ("Soll ich bei der Prüfung schummeln?", "decision", "deep")
    ]
    
    for text, expected_type, expected_path in test_cases:
        input_data = {"text": text}
        context = run_module(input_data, profile, {})
        
        if context["decision_engine_result"]["status"] == "success":
            decision = context["decision_engine_result"]["decision"]
            analysis = decision["analysis"]
            
            print(f"   '{text[:30]}...'")
            print(f"     Question Type: {analysis['question_type']} (expected: {expected_type})")
            print(f"     Path: {decision['path']} (expected: {expected_path})")
            print(f"     Risk Score: {analysis['risk_score']:.2f}")
        print()
    
    # Test 4: Statistiken
    print("4. Engine Statistiken")
    engine = get_engine()
    stats = engine.get_stats()
    print(f"   Total Decisions: {stats['total_decisions']}")
    print(f"   Advanced Modules: {[k for k, v in stats['advanced_modules'].items() if v]}")
    
    print("\n=== Demo abgeschlossen ===")


if __name__ == "__main__":
    demo()