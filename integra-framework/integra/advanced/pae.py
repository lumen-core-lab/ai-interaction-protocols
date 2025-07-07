# -*- coding: utf-8 -*-
"""
Modulname: pae.py
Beschreibung: Priority Anchor Engine für INTEGRA Advanced - Entscheidung bei ethischen Gleichständen
Teil von: INTEGRA Light – Advanced Layer
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Überarbeitet gemäß INTEGRA 4.2 Standards
"""

from typing import Dict, Any, List, Tuple, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from pathlib import Path

# Import-Kompatibilität
try:
    from integra.core import principles, profiles, simple_ethics
    from integra.advanced import mini_audit
    from integra.logging import log_manager
except ImportError:
    try:
        from core import principles, profiles, simple_ethics
        from advanced import mini_audit
        from logging import log_manager
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles, simple_ethics
        except ImportError:
            # Fallback
            class DummyPrinciples:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            principles = DummyPrinciples()
            
            class DummyProfiles:
                def get_default_profile(self):
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            profiles = DummyProfiles()
        
        # Dummy Module
        simple_ethics = None
        mini_audit = None
        class DummyLogManager:
            def log_event(self, *args, **kwargs): pass
        log_manager = DummyLogManager()


class TieResolutionMethod(Enum):
    """Methoden zur Gleichstandsauflösung."""
    PRIORITY_ORDER = "priority_order"
    CONTEXT_BASED = "context_based"
    HISTORICAL = "historical"
    PROFILE_WEIGHTED = "profile_weighted"
    COMBINED = "combined"


@dataclass
class TieGroup:
    """Repräsentiert eine Gruppe von Prinzipien mit gleichem Score."""
    principles: List[str]
    score: float
    size: int = field(init=False)
    
    def __post_init__(self):
        self.size = len(self.principles)


@dataclass
class ResolutionResult:
    """Ergebnis einer Gleichstandsauflösung."""
    chosen_principle: str
    runner_up: Optional[str]
    method_used: TieResolutionMethod
    confidence: float
    reasoning: str
    tie_groups: List[TieGroup]
    context_factors: List[str]


class PriorityRuleEngine:
    """
    Verwaltet Prioritätsregeln für verschiedene Kontexte.
    Kann aus externen Dateien geladen werden.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rules = self._load_priority_rules()
        
        # Standard-Prioritäten als Fallback
        self.default_order = [
            "integrity",    # Wahrheit/Ehrlichkeit zuerst
            "governance",   # Regelkonformität
            "awareness",    # Risikobewusstsein
            "nurturing",    # Fürsorge
            "learning"      # Lernen (oft aufschiebbar)
        ]
    
    def _load_priority_rules(self) -> Dict[str, List[str]]:
        """Lädt Prioritätsregeln aus Konfiguration oder Datei."""
        rules_file = self.config.get('priority_rules_file', 'pae_priority_rules.json')
        
        default_rules = {
            "emergency": ["nurturing", "awareness", "governance", "integrity", "learning"],
            "children": ["nurturing", "awareness", "learning", "integrity", "governance"],
            "legal": ["governance", "integrity", "awareness", "nurturing", "learning"],
            "educational": ["learning", "integrity", "awareness", "nurturing", "governance"],
            "public": ["integrity", "governance", "awareness", "nurturing", "learning"],
            "vulnerable": ["nurturing", "integrity", "awareness", "governance", "learning"],
            "professional": ["integrity", "governance", "awareness", "learning", "nurturing"],
            "crisis": ["awareness", "nurturing", "governance", "integrity", "learning"],
            "privacy": ["integrity", "awareness", "governance", "nurturing", "learning"],
            "collaborative": ["nurturing", "learning", "awareness", "integrity", "governance"]
        }
        
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    loaded_rules = json.load(f)
                    default_rules.update(loaded_rules)
                    log_manager.log_event("PAE", f"Externe Prioritätsregeln geladen: {rules_file}", "INFO")
            except Exception as e:
                log_manager.log_event("PAE", f"Fehler beim Laden der Prioritätsregeln: {e}", "WARNING")
        
        return default_rules
    
    def get_priority_order(self, context_type: Optional[str] = None) -> List[str]:
        """Gibt Prioritätsreihenfolge für gegebenen Kontext zurück."""
        if context_type and context_type in self.rules:
            return self.rules[context_type]
        return self.default_order


class TieDetector:
    """Erkennt und analysiert Gleichstände zwischen Prinzipien."""
    
    def __init__(self, equality_threshold: float = 0.1):
        self.equality_threshold = equality_threshold
    
    def detect_ties(self, scores: Dict[str, float]) -> List[TieGroup]:
        """
        Identifiziert Gruppen von Prinzipien mit gleichen Scores.
        
        Returns:
            Liste von TieGroup-Objekten, sortiert nach Score (absteigend)
        """
        if not scores:
            return []
        
        # Gruppiere Prinzipien nach Score (mit Threshold)
        score_groups = {}
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for principle, score in sorted_items:
            # Finde existierende Gruppe mit ähnlichem Score
            matched_group = None
            for group_score in score_groups:
                if abs(score - group_score) <= self.equality_threshold:
                    matched_group = group_score
                    break
            
            if matched_group is not None:
                score_groups[matched_group].append(principle)
            else:
                score_groups[score] = [principle]
        
        # Erstelle TieGroup-Objekte
        tie_groups = []
        for score, principles_list in score_groups.items():
            if len(principles_list) > 1:  # Nur Gruppen mit mehr als einem Prinzip
                tie_groups.append(TieGroup(principles=principles_list, score=score))
        
        # Sortiere nach Score (höchste zuerst)
        tie_groups.sort(key=lambda g: g.score, reverse=True)
        
        return tie_groups


class HistoricalAnalyzer:
    """Analysiert historische Entscheidungen für bessere Prioritätswahl."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.decision_history = []
        self.success_patterns = {}
    
    def add_decision(self, principle: str, context_type: str, 
                    success: bool = True, confidence: float = 0.5):
        """Fügt eine Entscheidung zur Historie hinzu."""
        decision = {
            "principle": principle,
            "context_type": context_type,
            "success": success,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        self.decision_history.append(decision)
        
        # Historie begrenzen
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)
        
        # Erfolgsmuster aktualisieren
        key = f"{context_type}:{principle}"
        if key not in self.success_patterns:
            self.success_patterns[key] = {"successes": 0, "total": 0}
        
        self.success_patterns[key]["total"] += 1
        if success:
            self.success_patterns[key]["successes"] += 1
    
    def get_historical_preference(self, principles: List[str], 
                                context_type: Optional[str] = None) -> Optional[str]:
        """
        Ermittelt historisch erfolgreichstes Prinzip für Kontext.
        
        Returns:
            Prinzip mit höchster Erfolgsrate oder None
        """
        if not context_type:
            return None
        
        best_principle = None
        best_rate = 0.0
        
        for principle in principles:
            key = f"{context_type}:{principle}"
            if key in self.success_patterns:
                pattern = self.success_patterns[key]
                if pattern["total"] >= 3:  # Mindestens 3 Entscheidungen
                    success_rate = pattern["successes"] / pattern["total"]
                    if success_rate > best_rate:
                        best_rate = success_rate
                        best_principle = principle
        
        return best_principle if best_rate > 0.6 else None


class PriorityAnchorEngine:
    """
    Hauptklasse für Prioritätsentscheidungen bei Gleichständen.
    Orchestriert verschiedene Auflösungsmethoden.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Komponenten initialisieren
        self.tie_detector = TieDetector(
            equality_threshold=self.config.get('equality_threshold', 0.1)
        )
        self.priority_rules = PriorityRuleEngine(config)
        self.historical_analyzer = HistoricalAnalyzer(
            max_history=self.config.get('max_history', 100)
        )
        
        # Auflösungsmethode
        self.resolution_method = TieResolutionMethod(
            self.config.get('resolution_method', 'combined')
        )
        
        # Konfidenz-Parameter
        self.base_confidence = self.config.get('base_confidence', 0.7)
        self.confidence_factors = {
            "clear_winner": 0.2,
            "context_match": 0.1,
            "historical_success": 0.15,
            "profile_alignment": 0.1,
            "multiple_ties": -0.1,
            "no_context": -0.05
        }
        
        # Statistiken
        self.stats = {
            "total_resolutions": 0,
            "ties_resolved": 0,
            "methods_used": {},
            "average_confidence": 0.0
        }
    
    def resolve_priority(self, scores: Dict[str, float], 
                        context: Dict[str, Any], 
                        profile: Optional[Dict[str, float]] = None) -> ResolutionResult:
        """
        Hauptfunktion: Löst Prioritätsentscheidungen bei Gleichständen.
        
        Args:
            scores: Ethische Scores der Prinzipien
            context: Entscheidungskontext
            profile: Optionales ethisches Profil
            
        Returns:
            ResolutionResult mit gewähltem Prinzip und Begründung
        """
        start_time = datetime.now()
        
        try:
            # 1. Gleichstände erkennen
            tie_groups = self.tie_detector.detect_ties(scores)
            
            # 2. Kontext analysieren
            context_type, context_factors = self._analyze_context(context)
            
            # 3. Auflösungsmethode wählen
            if not tie_groups:
                # Kein Gleichstand - einfache Entscheidung
                result = self._resolve_clear_winner(scores, context_type)
            else:
                # Gleichstand vorhanden - komplexe Auflösung
                result = self._resolve_complex_tie(
                    tie_groups, scores, context_type, context_factors, profile
                )
            
            # 4. Statistiken aktualisieren
            self._update_statistics(result, tie_groups)
            
            # 5. Historische Entscheidung speichern
            if result.chosen_principle:
                self.historical_analyzer.add_decision(
                    result.chosen_principle, 
                    context_type or "general",
                    success=True,  # Erfolg wird später durch Feedback bestimmt
                    confidence=result.confidence
                )
            
            # 6. Audit-Event
            if mini_audit:
                audit_context = {
                    "event_type": "priority_resolution",
                    "tie_groups": len(tie_groups),
                    "chosen": result.chosen_principle,
                    "method": result.method_used.value,
                    "confidence": result.confidence
                }
                mini_audit.log_decision(audit_context, profile or {}, context)
            
            # Log
            processing_time = (datetime.now() - start_time).total_seconds()
            log_manager.log_event(
                "PAE",
                f"Priorität aufgelöst: {result.chosen_principle} "
                f"(Methode: {result.method_used.value}, Konfidenz: {result.confidence:.2f})",
                "INFO"
            )
            
            return result
            
        except Exception as e:
            log_manager.log_event("PAE", f"Fehler bei Prioritätsauflösung: {e}", "ERROR")
            # Fallback-Ergebnis
            return ResolutionResult(
                chosen_principle=self._get_fallback_principle(scores),
                runner_up=None,
                method_used=TieResolutionMethod.PRIORITY_ORDER,
                confidence=0.3,
                reasoning=f"Fehler bei Auflösung: {e}",
                tie_groups=[],
                context_factors=[]
            )
    
    def _analyze_context(self, context: Dict[str, Any]) -> Tuple[Optional[str], List[str]]:
        """Analysiert Kontext und extrahiert relevante Faktoren."""
        context_factors = []
        
        # Text-basierte Analyse
        text_sources = []
        for key in ["user_input", "text", "query", "input_text"]:
            if key in context:
                text_sources.append(str(context[key]))
        
        combined_text = " ".join(text_sources).lower()
        
        # Kontext-Patterns
        context_patterns = {
            "emergency": ["notfall", "dringend", "emergency", "urgent", "sofort", "kritisch"],
            "children": ["kind", "child", "schüler", "student", "minderjährig", "jugend"],
            "legal": ["gesetz", "law", "legal", "regel", "compliance", "vorschrift"],
            "educational": ["lernen", "learn", "bildung", "education", "unterricht"],
            "public": ["öffentlich", "public", "gesellschaft", "community"],
            "vulnerable": ["verletzlich", "vulnerable", "hilflos", "schwach"],
            "professional": ["arbeit", "work", "beruf", "professional", "geschäft"],
            "crisis": ["krise", "crisis", "konflikt", "problem"],
            "privacy": ["privat", "privacy", "datenschutz", "vertraulich"],
            "collaborative": ["zusammen", "gemeinsam", "team", "gruppe"]
        }
        
        # Erkannte Kontexttypen sammeln
        detected_types = []
        for ctx_type, patterns in context_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                detected_types.append(ctx_type)
                context_factors.extend(patterns)
        
        # Expliziter Kontext hat Priorität
        primary_context = context.get("context_type")
        if primary_context:
            return primary_context, context_factors
        
        # Sonst ersten erkannten Typ verwenden
        if detected_types:
            return detected_types[0], context_factors
        
        return None, context_factors
    
    def _resolve_clear_winner(self, scores: Dict[str, float], 
                            context_type: Optional[str]) -> ResolutionResult:
        """Löst einfachen Fall ohne Gleichstand."""
        if not scores:
            return self._create_empty_result()
        
        # Höchstes Prinzip finden
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        chosen = sorted_items[0]
        runner_up = sorted_items[1] if len(sorted_items) > 1 else None
        
        # Konfidenz berechnen
        confidence = self.base_confidence + self.confidence_factors["clear_winner"]
        if context_type:
            confidence += self.confidence_factors["context_match"]
        
        return ResolutionResult(
            chosen_principle=chosen[0],
            runner_up=runner_up[0] if runner_up else None,
            method_used=TieResolutionMethod.PRIORITY_ORDER,
            confidence=min(0.95, confidence),
            reasoning=f"{chosen[0].title()} hat eindeutig höchsten Score ({chosen[1]:.2f})",
            tie_groups=[],
            context_factors=[]
        )
    
    def _resolve_complex_tie(self, tie_groups: List[TieGroup], 
                           scores: Dict[str, float],
                           context_type: Optional[str],
                           context_factors: List[str],
                           profile: Optional[Dict[str, float]]) -> ResolutionResult:
        """Löst komplexe Gleichstände mit verschiedenen Methoden."""
        # Fokus auf wichtigste Gleichstandsgruppe
        primary_tie = tie_groups[0]
        
        # Methode basierend auf Konfiguration
        if self.resolution_method == TieResolutionMethod.PRIORITY_ORDER:
            return self._resolve_by_priority(primary_tie, context_type, context_factors)
            
        elif self.resolution_method == TieResolutionMethod.CONTEXT_BASED:
            return self._resolve_by_context(primary_tie, context_type, context_factors)
            
        elif self.resolution_method == TieResolutionMethod.HISTORICAL:
            return self._resolve_by_history(primary_tie, context_type, context_factors)
            
        elif self.resolution_method == TieResolutionMethod.PROFILE_WEIGHTED:
            return self._resolve_by_profile(primary_tie, profile, context_factors)
            
        else:  # COMBINED
            return self._resolve_combined(
                primary_tie, context_type, context_factors, profile, tie_groups
            )
    
    def _resolve_by_priority(self, tie_group: TieGroup, 
                           context_type: Optional[str],
                           context_factors: List[str]) -> ResolutionResult:
        """Auflösung durch Prioritätsregeln."""
        priority_order = self.priority_rules.get_priority_order(context_type)
        
        # Erstes Prinzip in Priorität finden
        for principle in priority_order:
            if principle in tie_group.principles:
                # Runner-up finden
                runner_up = None
                for p in priority_order:
                    if p in tie_group.principles and p != principle:
                        runner_up = p
                        break
                
                confidence = self.base_confidence
                if context_type:
                    confidence += self.confidence_factors["context_match"]
                
                reasoning = f"Prioritätsregel"
                if context_type:
                    reasoning += f" für {context_type}-Kontext"
                
                return ResolutionResult(
                    chosen_principle=principle,
                    runner_up=runner_up,
                    method_used=TieResolutionMethod.PRIORITY_ORDER,
                    confidence=confidence,
                    reasoning=reasoning,
                    tie_groups=[tie_group],
                    context_factors=context_factors
                )
        
        # Fallback
        return self._create_fallback_result(tie_group, context_factors)
    
    def _resolve_by_context(self, tie_group: TieGroup,
                          context_type: Optional[str],
                          context_factors: List[str]) -> ResolutionResult:
        """Auflösung durch Kontextanalyse."""
        if not context_type:
            # Kein klarer Kontext - auf Priorität zurückfallen
            return self._resolve_by_priority(tie_group, None, context_factors)
        
        # Kontext-spezifische Präferenzen
        context_preferences = {
            "emergency": "nurturing",
            "children": "nurturing", 
            "legal": "governance",
            "educational": "learning",
            "privacy": "integrity",
            "crisis": "awareness"
        }
        
        preferred = context_preferences.get(context_type)
        if preferred and preferred in tie_group.principles:
            confidence = self.base_confidence + self.confidence_factors["context_match"]
            
            return ResolutionResult(
                chosen_principle=preferred,
                runner_up=self._find_runner_up(preferred, tie_group.principles),
                method_used=TieResolutionMethod.CONTEXT_BASED,
                confidence=confidence,
                reasoning=f"Kontext '{context_type}' favorisiert {preferred.title()}",
                tie_groups=[tie_group],
                context_factors=context_factors
            )
        
        # Fallback auf Priorität
        return self._resolve_by_priority(tie_group, context_type, context_factors)
    
    def _resolve_by_history(self, tie_group: TieGroup,
                          context_type: Optional[str],
                          context_factors: List[str]) -> ResolutionResult:
        """Auflösung durch historische Erfolge."""
        historical_choice = self.historical_analyzer.get_historical_preference(
            tie_group.principles, context_type
        )
        
        if historical_choice:
            confidence = self.base_confidence + self.confidence_factors["historical_success"]
            
            return ResolutionResult(
                chosen_principle=historical_choice,
                runner_up=self._find_runner_up(historical_choice, tie_group.principles),
                method_used=TieResolutionMethod.HISTORICAL,
                confidence=confidence,
                reasoning=f"Historisch erfolgreich in ähnlichen Situationen",
                tie_groups=[tie_group],
                context_factors=context_factors
            )
        
        # Keine historischen Daten - Fallback
        return self._resolve_by_priority(tie_group, context_type, context_factors)
    
    def _resolve_by_profile(self, tie_group: TieGroup,
                          profile: Optional[Dict[str, float]],
                          context_factors: List[str]) -> ResolutionResult:
        """Auflösung durch Profil-Gewichtungen."""
        if not profile:
            return self._resolve_by_priority(tie_group, None, context_factors)
        
        # Prinzip mit höchster Profil-Gewichtung wählen
        best_principle = None
        best_weight = 0.0
        
        for principle in tie_group.principles:
            weight = profile.get(principle, 1.0)
            if weight > best_weight:
                best_weight = weight
                best_principle = principle
        
        if best_principle:
            confidence = self.base_confidence + self.confidence_factors["profile_alignment"]
            
            return ResolutionResult(
                chosen_principle=best_principle,
                runner_up=self._find_runner_up(best_principle, tie_group.principles),
                method_used=TieResolutionMethod.PROFILE_WEIGHTED,
                confidence=confidence,
                reasoning=f"Profil-Präferenz (Gewicht: {best_weight:.2f})",
                tie_groups=[tie_group],
                context_factors=context_factors
            )
        
        return self._create_fallback_result(tie_group, context_factors)
    
    def _resolve_combined(self, tie_group: TieGroup,
                        context_type: Optional[str],
                        context_factors: List[str],
                        profile: Optional[Dict[str, float]],
                        all_tie_groups: List[TieGroup]) -> ResolutionResult:
        """Kombinierte Auflösung mit allen verfügbaren Methoden."""
        candidates = {}
        
        # Sammle Vorschläge von allen Methoden
        methods = [
            ("priority", self._resolve_by_priority(tie_group, context_type, context_factors)),
            ("context", self._resolve_by_context(tie_group, context_type, context_factors)),
            ("history", self._resolve_by_history(tie_group, context_type, context_factors)),
            ("profile", self._resolve_by_profile(tie_group, profile, context_factors))
        ]
        
        # Zähle Vorschläge
        for method_name, result in methods:
            if result.chosen_principle:
                if result.chosen_principle not in candidates:
                    candidates[result.chosen_principle] = {
                        "count": 0,
                        "total_confidence": 0,
                        "methods": []
                    }
                candidates[result.chosen_principle]["count"] += 1
                candidates[result.chosen_principle]["total_confidence"] += result.confidence
                candidates[result.chosen_principle]["methods"].append(method_name)
        
        # Wähle Prinzip mit meisten Stimmen
        if candidates:
            best_principle = max(
                candidates.items(),
                key=lambda x: (x[1]["count"], x[1]["total_confidence"])
            )[0]
            
            candidate_info = candidates[best_principle]
            avg_confidence = candidate_info["total_confidence"] / candidate_info["count"]
            
            # Bonus für Konsens
            if candidate_info["count"] >= 3:
                avg_confidence += 0.1
            
            # Penalty für viele Gleichstände
            if len(all_tie_groups) > 2:
                avg_confidence += self.confidence_factors["multiple_ties"]
            
            return ResolutionResult(
                chosen_principle=best_principle,
                runner_up=self._find_runner_up(best_principle, tie_group.principles),
                method_used=TieResolutionMethod.COMBINED,
                confidence=min(0.95, max(0.3, avg_confidence)),
                reasoning=f"Konsens aus {candidate_info['count']} Methoden: {', '.join(candidate_info['methods'])}",
                tie_groups=all_tie_groups,
                context_factors=context_factors
            )
        
        # Absolute Fallback
        return self._create_fallback_result(tie_group, context_factors)
    
    def _find_runner_up(self, chosen: str, candidates: List[str]) -> Optional[str]:
        """Findet Zweitplatzierten aus Kandidatenliste."""
        for candidate in candidates:
            if candidate != chosen:
                return candidate
        return None
    
    def _create_fallback_result(self, tie_group: TieGroup,
                               context_factors: List[str]) -> ResolutionResult:
        """Erstellt Fallback-Ergebnis."""
        return ResolutionResult(
            chosen_principle=tie_group.principles[0],
            runner_up=tie_group.principles[1] if len(tie_group.principles) > 1 else None,
            method_used=TieResolutionMethod.PRIORITY_ORDER,
            confidence=0.4,
            reasoning="Fallback auf erste Option",
            tie_groups=[tie_group],
            context_factors=context_factors
        )
    
    def _create_empty_result(self) -> ResolutionResult:
        """Erstellt leeres Ergebnis."""
        return ResolutionResult(
            chosen_principle="integrity",  # Standard-Fallback
            runner_up=None,
            method_used=TieResolutionMethod.PRIORITY_ORDER,
            confidence=0.3,
            reasoning="Keine Scores verfügbar - Standard-Fallback",
            tie_groups=[],
            context_factors=[]
        )
    
    def _get_fallback_principle(self, scores: Dict[str, float]) -> str:
        """Ermittelt Fallback-Prinzip."""
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return "integrity"
    
    def _update_statistics(self, result: ResolutionResult, tie_groups: List[TieGroup]):
        """Aktualisiert interne Statistiken."""
        self.stats["total_resolutions"] += 1
        
        if tie_groups:
            self.stats["ties_resolved"] += 1
        
        method_name = result.method_used.value
        if method_name not in self.stats["methods_used"]:
            self.stats["methods_used"][method_name] = 0
        self.stats["methods_used"][method_name] += 1
        
        # Gleitender Durchschnitt für Konfidenz
        n = self.stats["total_resolutions"]
        prev_avg = self.stats["average_confidence"]
        self.stats["average_confidence"] = ((prev_avg * (n - 1)) + result.confidence) / n
    
    def process_feedback(self, principle: str, context_type: str, 
                        success: bool, confidence_adjustment: float = 0.0):
        """
        Verarbeitet Feedback zu einer getroffenen Entscheidung.
        
        Args:
            principle: Gewähltes Prinzip
            context_type: Kontext der Entscheidung
            success: War die Entscheidung erfolgreich?
            confidence_adjustment: Anpassung der Konfidenz (-1 bis 1)
        """
        # Update historische Daten
        self.historical_analyzer.add_decision(
            principle, context_type, success, 
            confidence=0.5 + confidence_adjustment * 0.5
        )
        
        # Log Feedback
        log_manager.log_event(
            "PAE",
            f"Feedback erhalten: {principle} in {context_type} - "
            f"{'Erfolg' if success else 'Misserfolg'}",
            "INFO"
        )


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Hauptschnittstelle gemäß INTEGRA-Standard.
    
    Args:
        input_text: Nicht direkt verwendet, aber für Konsistenz
        context: Muss 'scores' enthalten, optional 'profile', 'context_type'
        
    Returns:
        Standardisiertes Ergebnis mit Prioritätsentscheidung
    """
    context = context or {}
    
    try:
        # Scores extrahieren
        scores = context.get("scores", {})
        if not scores:
            # Versuche aus ethics_result zu extrahieren
            if "simple_ethics_result" in context:
                scores = context["simple_ethics_result"].get("scores", {})
            elif "ethics" in context:
                scores = context["ethics"].get("scores", {})
        
        if not scores:
            return {
                "error": True,
                "message": "Keine ethischen Scores im Kontext gefunden",
                "module": "pae",
                "version": "2.0",
                "timestamp": datetime.now().isoformat()
            }
        
        # Profil extrahieren
        profile = context.get("profile")
        if not profile and profiles:
            profile = profiles.get_default_profile()
        
        # Konfiguration
        config = context.get("pae_config", {})
        
        # PAE initialisieren
        pae = PriorityAnchorEngine(config)
        
        # Priorität auflösen
        result = pae.resolve_priority(scores, context, profile)
        
        # Ergebnis für Kontext vorbereiten
        pae_result = {
            "chosen_principle": result.chosen_principle,
            "runner_up": result.runner_up,
            "method": result.method_used.value,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "tie_groups": [
                {"principles": g.principles, "score": g.score} 
                for g in result.tie_groups
            ],
            "context_factors": result.context_factors
        }
        
        # In Kontext speichern
        if isinstance(context, dict):
            context["pae_result"] = pae_result
        
        # Standardisierte Ausgabe
        return {
            "success": True,
            "chosen_principle": result.chosen_principle,
            "runner_up": result.runner_up,
            "confidence": result.confidence,
            "method_used": result.method_used.value,
            "reasoning": result.reasoning,
            "tie_detected": len(result.tie_groups) > 0,
            "tie_count": len(result.tie_groups),
            "context_type": result.context_factors[0] if result.context_factors else None,
            "module": "pae",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "meta": {
                "tie_groups": pae_result["tie_groups"],
                "context_factors": result.context_factors,
                "stats": pae.stats.copy()
            },
            "context_updated": True,
            "pae_result": pae_result
        }
        
    except Exception as e:
        log_manager.log_event("PAE", f"Kritischer Fehler in run_module: {e}", "ERROR")
        return {
            "error": True,
            "message": str(e),
            "module": "pae",
            "version": "2.0",
            "timestamp": datetime.now().isoformat()
        }


def demo():
    """Demonstriert verbesserte PAE-Funktionalität."""
    print("=== INTEGRA PAE 2.0 Demo - Priority Anchor Engine ===\n")
    
    # Demo 1: Klarer Gewinner
    print("Demo 1: Klarer Gewinner (kein Gleichstand)")
    print("-" * 50)
    
    context1 = {
        "scores": {
            "integrity": 0.9,
            "nurturing": 0.6,
            "governance": 0.7,
            "awareness": 0.5,
            "learning": 0.4
        },
        "user_input": "Soll ich die Wahrheit sagen?"
    }
    
    result1 = run_module("", context1)
    print(f"✅ Gewähltes Prinzip: {result1['chosen_principle']}")
    print(f"   Konfidenz: {result1['confidence']:.2f}")
    print(f"   Begründung: {result1['reasoning']}")
    print(f"   Gleichstand erkannt: {result1['tie_detected']}")
    print()
    
    # Demo 2: Einfacher Gleichstand
    print("Demo 2: Gleichstand zwischen zwei Prinzipien")
    print("-" * 50)
    
    context2 = {
        "scores": {
            "integrity": 0.8,
            "nurturing": 0.8,
            "governance": 0.6,
            "awareness": 0.5,
            "learning": 0.4
        },
        "user_input": "Kind fragt nach verstorbenem Haustier",
        "context_type": "children"
    }
    
    result2 = run_module("", context2)
    print(f"✅ Gewähltes Prinzip: {result2['chosen_principle']}")
    print(f"   Zweitplatziert: {result2['runner_up']}")
    print(f"   Methode: {result2['method_used']}")
    print(f"   Begründung: {result2['reasoning']}")
    print(f"   Kontext: {result2['context_type']}")
    
    if result2['meta']['tie_groups']:
        print(f"   Gleichstandsgruppe: {result2['meta']['tie_groups'][0]['principles']}")
    print()
    
    # Demo 3: Mehrfacher Gleichstand
    print("Demo 3: Komplexer Mehrfach-Gleichstand")
    print("-" * 50)
    
    context3 = {
        "scores": {
            "integrity": 0.7,
            "nurturing": 0.7,
            "governance": 0.7,
            "awareness": 0.5,
            "learning": 0.5
        },
        "user_input": "Notfall in der Schule",
        "profile": {
            "integrity": 1.0,
            "nurturing": 1.2,  # Leicht erhöht
            "governance": 0.9,
            "awareness": 1.0,
            "learning": 1.1
        }
    }
    
    result3 = run_module("", context3)
    print(f"✅ Gewähltes Prinzip: {result3['chosen_principle']}")
    print(f"   Anzahl Gleichstände: {result3['tie_count']}")
    print(f"   Konfidenz: {result3['confidence']:.2f}")
    print(f"   Methode: {result3['method_used']}")
    
    # Zeige alle Gleichstandsgruppen
    for i, group in enumerate(result3['meta']['tie_groups']):
        print(f"   Gruppe {i+1}: {group['principles']} (Score: {group['score']})")
    print()
    
    # Demo 4: Historisches Lernen simulieren
    print("Demo 4: Mit simuliertem historischem Feedback")
    print("-" * 50)
    
    # PAE mit Historie initialisieren
    config = {"resolution_method": "combined"}
    pae = PriorityAnchorEngine(config)
    
    # Simuliere vergangene Entscheidungen
    pae.process_feedback("nurturing", "emergency", success=True)
    pae.process_feedback("nurturing", "emergency", success=True)
    pae.process_feedback("governance", "emergency", success=False)
    
    # Neue Entscheidung mit Historie
    scores = {
        "nurturing": 0.75,
        "governance": 0.75,
        "integrity": 0.6
    }
    
    result4 = pae.resolve_priority(scores, {"context_type": "emergency"})
    print(f"✅ Gewähltes Prinzip: {result4.chosen_principle}")
    print(f"   Begründung: {result4.reasoning}")
    print(f"   (Basierend auf historischem Erfolg in Notfällen)")
    
    # Statistiken anzeigen
    print(f"\n📊 PAE Statistiken:")
    print(f"   Gesamtentscheidungen: {pae.stats['total_resolutions']}")
    print(f"   Gleichstände aufgelöst: {pae.stats['ties_resolved']}")
    print(f"   Durchschnittliche Konfidenz: {pae.stats['average_confidence']:.2f}")
    print(f"   Verwendete Methoden: {pae.stats['methods_used']}")
    
    print("\n✅ PAE Demo abgeschlossen!")


if __name__ == "__main__":
    demo()