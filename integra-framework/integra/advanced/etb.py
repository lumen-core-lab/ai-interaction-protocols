# -*- coding: utf-8 -*-
"""
Modulname: etb.py
Beschreibung: Ethical Tradeoff Balancer für INTEGRA Advanced - Bewertet Handlungsoptionen nach ALIGN-Prinzipien
Teil von: INTEGRA Light – Advanced Layer
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 3.0 - Komplette Neuimplementierung gemäß INTEGRA 4.2 Spezifikation
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json
import os
from pathlib import Path

# Import-Kompatibilität
try:
    from integra.core import principles, profiles
    from integra.logging import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from logging import log_manager
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
        except ImportError:
            # Fallback ohne Core-Module
            class DummyPrinciples:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            principles = DummyPrinciples()
            
            class DummyProfiles:
                def get_default_profile(self):
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            profiles = DummyProfiles()
        
        # Dummy log_manager wenn nicht verfügbar
        class DummyLogManager:
            def log_event(self, *args, **kwargs): pass
        log_manager = DummyLogManager()


class TradeoffMatrixBuilder:
    """
    Erstellt Bewertungsmatrizen für Handlungsoptionen basierend auf ALIGN-Prinzipien.
    Kernkomponente des ETB für strukturierte ethische Bewertung.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert den Matrix Builder.
        
        Args:
            config: Optionale Konfiguration mit Scoring-Regeln
        """
        self.config = config or {}
        
        # Lade Bewertungsregeln
        self.scoring_rules = self._load_scoring_rules()
        
        # Standard-Gewichtungen für Prinzipien
        self.default_weights = {
            "awareness": 1.0,
            "learning": 1.0,
            "integrity": 1.0,
            "governance": 1.0,
            "nurturing": 1.0
        }
    
    def _load_scoring_rules(self) -> Dict[str, Any]:
        """Lädt Bewertungsregeln aus externer Datei oder nutzt Defaults."""
        rules_file = self.config.get('scoring_rules_file', 'etb_scoring_rules.json')
        
        # Standard-Regeln für häufige Handlungsmuster
        default_rules = {
            "patterns": {
                "truth_telling": {
                    "keywords": ["wahrheit", "ehrlich", "truth", "honest", "sagen", "tell"],
                    "scores": {"integrity": 0.9, "governance": 0.7, "nurturing": 0.5}
                },
                "protection": {
                    "keywords": ["schützen", "protect", "bewahren", "sicher", "safe"],
                    "scores": {"nurturing": 0.9, "awareness": 0.8, "governance": 0.6}
                },
                "deception": {
                    "keywords": ["lügen", "täuschen", "lie", "deceive", "verschweigen"],
                    "scores": {"integrity": 0.1, "governance": 0.3, "nurturing": 0.6}
                },
                "help": {
                    "keywords": ["helfen", "help", "unterstützen", "assist", "fördern"],
                    "scores": {"nurturing": 0.9, "learning": 0.7, "awareness": 0.6}
                },
                "educate": {
                    "keywords": ["lehren", "lernen", "teach", "learn", "erklären"],
                    "scores": {"learning": 0.9, "awareness": 0.8, "nurturing": 0.7}
                },
                "enforce_rules": {
                    "keywords": ["regel", "gesetz", "rule", "law", "durchsetzen", "enforce"],
                    "scores": {"governance": 0.9, "integrity": 0.7, "nurturing": 0.4}
                }
            },
            "modifiers": {
                "emergency": {"nurturing": 1.2, "awareness": 1.1, "governance": 0.8},
                "vulnerable": {"nurturing": 1.3, "awareness": 1.2},
                "public": {"governance": 1.2, "integrity": 1.1},
                "educational": {"learning": 1.3, "awareness": 1.1}
            }
        }
        
        # Versuche externe Datei zu laden
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    loaded_rules = json.load(f)
                    # Merge mit Defaults
                    default_rules.update(loaded_rules)
                    log_manager.log_event("ETB", f"Externe Scoring-Regeln geladen: {rules_file}", "INFO")
            except Exception as e:
                log_manager.log_event("ETB", f"Fehler beim Laden der Scoring-Regeln: {e}", "WARNING")
        
        return default_rules
    
    def score_option(self, option: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, float]:
        """
        Bewertet eine einzelne Handlungsoption.
        
        Args:
            option: {"text": str, "tags": [...], "risks": [...]}
            context: Kontextinformationen
            
        Returns:
            Dict mit Scores für jedes ALIGN-Prinzip
        """
        # Basis-Scores initialisieren
        scores = {principle: 0.5 for principle in principles.ALIGN_KEYS}
        
        # Text der Option analysieren
        option_text = option.get("text", "").lower()
        
        # Pattern-basiertes Scoring
        for pattern_name, pattern_data in self.scoring_rules["patterns"].items():
            keywords = pattern_data.get("keywords", [])
            if any(keyword in option_text for keyword in keywords):
                pattern_scores = pattern_data.get("scores", {})
                for principle, score in pattern_scores.items():
                    if principle in scores:
                        # Weighted average mit bisherigem Score
                        scores[principle] = (scores[principle] + score) / 2
        
        # Tags berücksichtigen
        tags = option.get("tags", [])
        for tag in tags:
            if tag == "honest":
                scores["integrity"] = min(1.0, scores["integrity"] + 0.2)
            elif tag == "protective":
                scores["nurturing"] = min(1.0, scores["nurturing"] + 0.2)
            elif tag == "risky":
                scores["awareness"] = max(0.0, scores["awareness"] - 0.2)
            elif tag == "educational":
                scores["learning"] = min(1.0, scores["learning"] + 0.2)
            elif tag == "lawful":
                scores["governance"] = min(1.0, scores["governance"] + 0.2)
        
        # Risiken berücksichtigen
        risks = option.get("risks", [])
        risk_penalty = len(risks) * 0.1
        scores["awareness"] = max(0.0, scores["awareness"] - risk_penalty)
        scores["governance"] = max(0.0, scores["governance"] - risk_penalty * 0.5)
        
        # Kontext-Modifikatoren anwenden
        context_type = context.get("context_type", "")
        if context_type in self.scoring_rules["modifiers"]:
            modifiers = self.scoring_rules["modifiers"][context_type]
            for principle, modifier in modifiers.items():
                if principle in scores:
                    scores[principle] = min(1.0, scores[principle] * modifier)
        
        # Alignment-Score berechnen (falls explizit angegeben)
        if "alignment" in option:
            for principle, value in option["alignment"].items():
                if principle in scores:
                    scores[principle] = value
        
        return scores
    
    def build_matrix(self, options: List[Dict[str, Any]], context: Dict[str, Any], 
                     weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Erstellt eine vollständige Bewertungsmatrix für alle Optionen.
        
        Args:
            options: Liste von Handlungsoptionen
            context: Kontextinformationen
            weights: Optionale Gewichtungen für Prinzipien
            
        Returns:
            Liste von bewerteten Optionen mit Scores und Gesamtwertung
        """
        if weights is None:
            weights = self.default_weights
        
        matrix = []
        
        for i, option in enumerate(options):
            # Scores für diese Option berechnen
            principle_scores = self.score_option(option, context)
            
            # Gewichtete Gesamtwertung
            weighted_scores = {}
            total_score = 0.0
            
            for principle, score in principle_scores.items():
                weight = weights.get(principle, 1.0)
                weighted_score = score * weight
                weighted_scores[principle] = weighted_score
                total_score += weighted_score
            
            # Matrix-Eintrag erstellen
            matrix_entry = {
                "option_id": i,
                "option_text": option.get("text", f"Option {i+1}"),
                "principle_scores": principle_scores,
                "weighted_scores": weighted_scores,
                "total_score": total_score,
                "weights_used": weights.copy(),
                "tags": option.get("tags", []),
                "risks": option.get("risks", [])
            }
            
            matrix.append(matrix_entry)
        
        # Nach Gesamtscore sortieren
        matrix.sort(key=lambda x: x["total_score"], reverse=True)
        
        return matrix


class EthicalTradeoffBalancer:
    """
    Hauptklasse des ETB - Orchestriert die Bewertung von Handlungsoptionen
    und generiert nachvollziehbare Entscheidungen basierend auf ALIGN-Prinzipien.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert den Ethical Tradeoff Balancer.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        self.matrix_builder = TradeoffMatrixBuilder(config)
        
        # Statistiken
        self.stats = {
            "total_evaluations": 0,
            "options_analyzed": 0,
            "average_confidence": 0.0
        }
    
    def evaluate_options(self, options: List[Dict[str, Any]], context: Dict[str, Any], 
                        weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Hauptfunktion: Bewertet alle Optionen und wählt die beste.
        
        Args:
            options: Liste von Handlungsoptionen
            context: Entscheidungskontext
            weights: Optionale Prinzipien-Gewichtungen
            
        Returns:
            Vollständiges Evaluationsergebnis mit Matrix und Empfehlung
        """
        start_time = datetime.now()
        
        try:
            # Validierung
            if not options:
                raise ValueError("Keine Optionen zur Bewertung angegeben")
            
            # Gewichtungen vorbereiten
            if weights is None:
                weights = self._extract_weights_from_context(context)
            
            # Matrix erstellen
            matrix = self.matrix_builder.build_matrix(options, context, weights)
            
            # Beste Option identifizieren
            best_option = matrix[0] if matrix else None
            
            # Justifikation generieren
            justification = self._generate_justification(best_option, matrix)
            
            # Konfidenz berechnen
            confidence = self._calculate_confidence(matrix)
            
            # Statistiken aktualisieren
            self._update_statistics(len(options), confidence)
            
            # Log Event
            log_manager.log_event(
                "ETB",
                f"Evaluation abgeschlossen: {len(options)} Optionen, "
                f"Beste: '{best_option['option_text'][:50]}...', Konfidenz: {confidence:.2f}",
                "INFO"
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "best_option": best_option["option_text"] if best_option else None,
                "best_option_id": best_option["option_id"] if best_option else None,
                "justification": justification,
                "score": best_option["total_score"] if best_option else 0.0,
                "matrix": matrix,
                "confidence": confidence,
                "weights_used": weights,
                "processing_time": processing_time,
                "stats": self.stats.copy(),
                "meta": {
                    "total_options": len(options),
                    "context_type": context.get("context_type", "general"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            log_manager.log_event("ETB", f"Fehler bei Evaluation: {e}", "ERROR")
            return {
                "success": False,
                "error": str(e),
                "best_option": None,
                "matrix": [],
                "confidence": 0.0
            }
    
    def _extract_weights_from_context(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Extrahiert Prinzipien-Gewichtungen aus dem Kontext."""
        # Aus Profil
        if "profile" in context:
            return context["profile"]
        
        # Aus ETB-spezifischer Konfiguration
        if "etb_weights" in context:
            return context["etb_weights"]
        
        # Default
        if profiles:
            return profiles.get_default_profile()
        
        return self.matrix_builder.default_weights
    
    def _generate_justification(self, best_option: Dict[str, Any], 
                               matrix: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generiert eine nachvollziehbare Begründung für die Wahl."""
        if not best_option:
            return {
                "summary": "Keine Option erfüllt die ethischen Anforderungen",
                "principle_analysis": {},
                "key_factors": []
            }
        
        # Prinzipien-Analyse
        principle_analysis = {}
        for principle, score in best_option["principle_scores"].items():
            principle_analysis[principle] = {
                "score": score,
                "weighted_score": best_option["weighted_scores"][principle],
                "contribution": best_option["weighted_scores"][principle] / best_option["total_score"] 
                                if best_option["total_score"] > 0 else 0
            }
        
        # Schlüsselfaktoren identifizieren
        key_factors = []
        
        # Höchste Beiträge
        sorted_principles = sorted(
            principle_analysis.items(), 
            key=lambda x: x[1]["contribution"], 
            reverse=True
        )
        
        for principle, analysis in sorted_principles[:3]:
            if analysis["contribution"] > 0.15:  # Mindestens 15% Beitrag
                key_factors.append({
                    "principle": principle,
                    "reason": f"{principle.title()} trägt {analysis['contribution']:.0%} zur Entscheidung bei",
                    "score": analysis["score"]
                })
        
        # Vergleich mit zweitbester Option
        if len(matrix) > 1:
            margin = best_option["total_score"] - matrix[1]["total_score"]
            relative_margin = margin / best_option["total_score"] if best_option["total_score"] > 0 else 0
            
            key_factors.append({
                "principle": "margin",
                "reason": f"Vorsprung von {relative_margin:.0%} zur zweitbesten Option",
                "score": margin
            })
        
        # Tags und Risiken
        if best_option.get("tags"):
            key_factors.append({
                "principle": "characteristics",
                "reason": f"Eigenschaften: {', '.join(best_option['tags'])}",
                "score": None
            })
        
        if best_option.get("risks"):
            key_factors.append({
                "principle": "risks",
                "reason": f"Identifizierte Risiken: {len(best_option['risks'])}",
                "score": None
            })
        
        return {
            "summary": f"Option '{best_option['option_text']}' zeigt beste Übereinstimmung mit ethischen Prinzipien",
            "principle_analysis": principle_analysis,
            "key_factors": key_factors,
            "total_score": best_option["total_score"]
        }
    
    def _calculate_confidence(self, matrix: List[Dict[str, Any]]) -> float:
        """Berechnet Konfidenz in die Entscheidung."""
        if not matrix:
            return 0.0
        
        if len(matrix) == 1:
            # Nur eine Option - Konfidenz basiert auf absoluter Score
            return min(0.9, matrix[0]["total_score"] / 5.0)
        
        # Mehrere Optionen - Konfidenz basiert auf Abstand
        best_score = matrix[0]["total_score"]
        second_score = matrix[1]["total_score"]
        
        # Relativer Vorsprung
        if best_score > 0:
            margin = (best_score - second_score) / best_score
        else:
            margin = 0
        
        # Basis-Konfidenz
        base_confidence = 0.5
        
        # Margin-Bonus (bis zu 0.3)
        margin_bonus = min(0.3, margin * 0.6)
        
        # Score-Bonus (bis zu 0.2)
        score_bonus = min(0.2, best_score / 5.0 * 0.2)
        
        confidence = base_confidence + margin_bonus + score_bonus
        
        # Penalisierung bei sehr niedrigen Scores
        if best_score < 2.0:
            confidence *= 0.8
        
        return min(0.95, max(0.1, confidence))
    
    def _update_statistics(self, options_count: int, confidence: float):
        """Aktualisiert interne Statistiken."""
        self.stats["total_evaluations"] += 1
        self.stats["options_analyzed"] += options_count
        
        # Gleitender Durchschnitt für Konfidenz
        prev_avg = self.stats["average_confidence"]
        n = self.stats["total_evaluations"]
        self.stats["average_confidence"] = ((prev_avg * (n - 1)) + confidence) / n


def run_module(options: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Hauptschnittstelle gemäß INTEGRA-Standard.
    
    Args:
        options: Liste von Handlungsoptionen, jede mit:
                - "text": Beschreibung der Option
                - "tags": Optional, z.B. ["honest", "protective"]
                - "risks": Optional, z.B. ["trust_loss", "harm"]
                - "alignment": Optional, explizite ALIGN-Scores
        context: Kontextinformationen mit:
                - "profile": Prinzipien-Gewichtungen
                - "context_type": z.B. "emergency", "educational"
                - "constraints": Zusätzliche Einschränkungen
        
    Returns:
        Standardisiertes Ergebnis mit Matrix und Empfehlung
    """
    context = context or {}
    
    try:
        # Validierung
        if not options:
            return {
                "error": True,
                "message": "Keine Optionen zur Bewertung angegeben",
                "module": "etb",
                "version": "3.0",
                "timestamp": datetime.now().isoformat()
            }
        
        # ETB-Konfiguration aus Kontext
        config = context.get("etb_config", {})
        
        # ETB initialisieren
        etb = EthicalTradeoffBalancer(config)
        
        # Gewichtungen extrahieren
        weights = None
        if "profile" in context:
            weights = context["profile"]
        elif "etb_weights" in context:
            weights = context["etb_weights"]
        
        # Evaluation durchführen
        result = etb.evaluate_options(options, context, weights)
        
        # Kontext für andere Module vorbereiten
        etb_result = {
            "chosen_option": result.get("best_option"),
            "option_id": result.get("best_option_id"),
            "score": result.get("score", 0.0),
            "confidence": result.get("confidence", 0.0),
            "matrix": result.get("matrix", []),
            "justification": result.get("justification", {})
        }
        
        # In Kontext speichern für andere Module
        if isinstance(context, dict):
            context["etb_result"] = etb_result
        
        # Standardisiertes Ausgabeformat
        return {
            "success": result.get("success", False),
            "best_option": result.get("best_option"),
            "justification": result.get("justification", {}),
            "score": result.get("score", 0.0),
            "matrix": result.get("matrix", []),
            "confidence": result.get("confidence", 0.0),
            "processing_time": result.get("processing_time", 0),
            "module": "etb",
            "version": "3.0",
            "timestamp": datetime.now().isoformat(),
            "meta": result.get("meta", {}),
            "context_updated": True,
            "etb_result": etb_result
        }
        
    except Exception as e:
        log_manager.log_event("ETB", f"Kritischer Fehler in run_module: {e}", "ERROR")
        return {
            "error": True,
            "message": str(e),
            "module": "etb",
            "version": "3.0",
            "timestamp": datetime.now().isoformat()
        }


def load_alignment_weights(path: str) -> Dict[str, float]:
    """
    Lädt Prinzipien-Gewichtungen aus externer Datei.
    
    Args:
        path: Pfad zur JSON-Datei
        
    Returns:
        Dict mit Gewichtungen für ALIGN-Prinzipien
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            weights = json.load(f)
            
        # Validierung
        for principle in principles.ALIGN_KEYS:
            if principle not in weights:
                weights[principle] = 1.0
                
        return weights
        
    except Exception as e:
        log_manager.log_event("ETB", f"Fehler beim Laden der Gewichtungen: {e}", "WARNING")
        return {principle: 1.0 for principle in principles.ALIGN_KEYS}


def demo():
    """Demonstriert ETB-Funktionalität mit realistischen ethischen Dilemmata."""
    print("=== INTEGRA ETB 3.0 Demo - Ethical Tradeoff Balancer ===\n")
    
    # Szenario 1: Wahrheit vs. Schutz
    print("Szenario 1: Kind fragt nach verstorbenem Haustier")
    print("-" * 50)
    
    options1 = [
        {
            "text": "Die Wahrheit sagen: Das Haustier ist gestorben",
            "tags": ["honest", "direct"],
            "risks": ["emotional_harm", "trauma"],
            "alignment": {"integrity": 1.0, "nurturing": 0.3}
        },
        {
            "text": "Schonende Umschreibung: Es ist eingeschlafen und träumt",
            "tags": ["protective", "gentle"],
            "risks": ["trust_loss_later"],
            "alignment": {"integrity": 0.5, "nurturing": 0.8}
        },
        {
            "text": "Ablenkung: Lass uns über schöne Erinnerungen sprechen",
            "tags": ["evasive", "caring"],
            "risks": ["unresolved_grief"],
            "alignment": {"integrity": 0.4, "nurturing": 0.7, "learning": 0.6}
        }
    ]
    
    context1 = {
        "context_type": "vulnerable",
        "user_input": "Mein 5-jähriges Kind fragt nach dem Haustier",
        "profile": {
            "awareness": 1.0,
            "learning": 0.8,
            "integrity": 0.9,
            "governance": 0.7,
            "nurturing": 1.3  # Erhöht wegen Kind
        }
    }
    
    result1 = run_module(options1, context1)
    
    print(f"✅ Beste Option: {result1['best_option']}")
    print(f"   Score: {result1['score']:.2f}")
    print(f"   Konfidenz: {result1['confidence']:.0%}")
    print(f"   Begründung: {result1['justification']['summary']}")
    print("\n   Prinzipien-Analyse:")
    for principle, analysis in result1['justification']['principle_analysis'].items():
        print(f"   - {principle.title()}: {analysis['score']:.2f} "
              f"(Beitrag: {analysis['contribution']:.0%})")
    
    # Szenario 2: Hilfe vs. Regeln
    print("\n\nSzenario 2: Notfall - Medikament ohne Rezept")
    print("-" * 50)
    
    options2 = [
        {
            "text": "Strikt die Regeln befolgen - kein Medikament ohne Rezept",
            "tags": ["lawful", "strict"],
            "risks": ["potential_harm", "suffering"]
        },
        {
            "text": "Ausnahme machen und Medikament ausgeben",
            "tags": ["helpful", "risky"],
            "risks": ["legal_consequences", "precedent"]
        },
        {
            "text": "Alternative Hilfe anbieten und Notarzt rufen",
            "tags": ["balanced", "responsible"],
            "risks": ["delay"]
        }
    ]
    
    context2 = {
        "context_type": "emergency",
        "constraints": ["legal_framework", "professional_ethics"]
    }
    
    result2 = run_module(options2, context2)
    
    print(f"✅ Beste Option: {result2['best_option']}")
    print(f"   Score: {result2['score']:.2f}")
    print(f"   Konfidenz: {result2['confidence']:.0%}")
    
    # Matrix anzeigen
    print("\n   Entscheidungsmatrix:")
    for i, entry in enumerate(result2['matrix']):
        print(f"   {i+1}. {entry['option_text'][:40]}...")
        print(f"      Gesamtscore: {entry['total_score']:.2f}")
        print(f"      Tags: {', '.join(entry['tags'])}")
    
    # Szenario 3: Bildung vs. Unterstützung
    print("\n\nSzenario 3: Hausaufgabenhilfe")
    print("-" * 50)
    
    options3 = [
        {
            "text": "Die komplette Lösung vorgeben",
            "tags": ["helpful", "enabling"],
            "risks": ["no_learning", "dependency"]
        },
        {
            "text": "Nur Hinweise und Denkanstöße geben",
            "tags": ["educational", "supportive"],
            "risks": ["frustration"]
        },
        {
            "text": "Gemeinsam Schritt für Schritt erarbeiten",
            "tags": ["collaborative", "time_intensive"],
            "risks": ["partial_dependency"]
        },
        {
            "text": "Auf Lernressourcen verweisen",
            "tags": ["independent", "distant"],
            "risks": ["insufficient_help"]
        }
    ]
    
    context3 = {
        "context_type": "educational",
        "etb_weights": {
            "awareness": 1.0,
            "learning": 1.5,  # Bildungskontext
            "integrity": 1.0,
            "governance": 0.8,
            "nurturing": 1.1
        }
    }
    
    result3 = run_module(options3, context3)
    
    print(f"✅ Beste Option: {result3['best_option']}")
    print(f"   Score: {result3['score']:.2f}")
    print(f"   Konfidenz: {result3['confidence']:.0%}")
    
    # Statistiken
    if "meta" in result3:
        print(f"\n📊 Evaluation-Statistiken:")
        print(f"   Optionen analysiert: {result3['meta']['total_options']}")
        print(f"   Verarbeitungszeit: {result3['processing_time']:.3f}s")
    
    print("\n✅ ETB Demo abgeschlossen!")
    print("\nDie Matrix zeigt, wie jede Option nach den 5 ALIGN-Prinzipien bewertet wurde.")
    print("Das Modul ist bereit für Integration in den INTEGRA Deep Path!")


if __name__ == "__main__":
    demo()