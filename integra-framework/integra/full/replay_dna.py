# -*- coding: utf-8 -*-
"""
Modulname: replay_dna.py
Beschreibung: Decision Recording und Pattern Matching für INTEGRA Full
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
import json
import os
import hashlib
import uuid
from pathlib import Path
from collections import defaultdict, deque
import statistics
import pickle
import gzip

# Import-Kompatibilität
try:
    from integra.core import principles, profiles
    from integra.advanced import mini_audit
except ImportError:
    try:
        from core import principles, profiles
        from advanced import mini_audit
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
            from advanced import mini_audit
        except ImportError:
            print("❌ Fehler: Core Module nicht gefunden!")
            sys.exit(1)


class DecisionDNA:
    """
    Strukturierte Repräsentation einer Entscheidung für Speicherung und Vergleich.
    """
    def __init__(self, decision_id: str, timestamp: datetime):
        self.decision_id = decision_id
        self.timestamp = timestamp
        self.dna_version = "1.0"
        
        # Kern-DNA Komponenten
        self.context_hash = ""
        self.input_signature = ""
        self.decision_path = ""
        self.confidence = 0.0
        
        # Ethische DNA
        self.ethics_scores = {}
        self.violations = []
        self.principle_weights = {}
        
        # Module DNA
        self.module_sequence = []
        self.module_results = {}
        
        # Outcome DNA
        self.response_hash = ""
        self.feedback = None
        self.success_metrics = {}
        
        # Meta DNA
        self.processing_time = 0.0
        self.profile_snapshot = {}
        self.tags = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert DNA zu Dictionary."""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "dna_version": self.dna_version,
            "context_hash": self.context_hash,
            "input_signature": self.input_signature,
            "decision_path": self.decision_path,
            "confidence": self.confidence,
            "ethics_scores": self.ethics_scores,
            "violations": self.violations,
            "principle_weights": self.principle_weights,
            "module_sequence": self.module_sequence,
            "module_results": self.module_results,
            "response_hash": self.response_hash,
            "feedback": self.feedback,
            "success_metrics": self.success_metrics,
            "processing_time": self.processing_time,
            "profile_snapshot": self.profile_snapshot,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionDNA':
        """Erstellt DNA aus Dictionary."""
        dna = cls(
            data["decision_id"],
            datetime.fromisoformat(data["timestamp"])
        )
        
        # Alle Attribute setzen
        for key, value in data.items():
            if hasattr(dna, key) and key not in ["decision_id", "timestamp"]:
                setattr(dna, key, value)
        
        return dna
    
    def calculate_similarity(self, other: 'DecisionDNA') -> float:
        """Berechnet Ähnlichkeit zu einer anderen DNA (0.0-1.0)."""
        similarity_scores = []
        
        # Kontext-Ähnlichkeit
        if self.context_hash == other.context_hash:
            similarity_scores.append(1.0)
        else:
            similarity_scores.append(0.0)
        
        # Input-Ähnlichkeit
        if self.input_signature == other.input_signature:
            similarity_scores.append(1.0)
        else:
            similarity_scores.append(0.3)  # Teilweise ähnlich
        
        # Pfad-Ähnlichkeit
        if self.decision_path == other.decision_path:
            similarity_scores.append(0.8)
        else:
            similarity_scores.append(0.2)
        
        # Ethik-Ähnlichkeit
        ethics_sim = self._calculate_ethics_similarity(other)
        similarity_scores.append(ethics_sim)
        
        # Modul-Sequenz-Ähnlichkeit
        seq_sim = self._calculate_sequence_similarity(other)
        similarity_scores.append(seq_sim)
        
        # Gewichteter Durchschnitt
        weights = [0.15, 0.20, 0.15, 0.30, 0.20]
        weighted_sim = sum(s * w for s, w in zip(similarity_scores, weights))
        
        return weighted_sim
    
    def _calculate_ethics_similarity(self, other: 'DecisionDNA') -> float:
        """Berechnet Ähnlichkeit der ethischen Bewertungen."""
        if not self.ethics_scores or not other.ethics_scores:
            return 0.5
        
        # Score-Differenzen
        score_diffs = []
        for principle in principles.ALIGN_KEYS:
            if principle in self.ethics_scores and principle in other.ethics_scores:
                diff = abs(self.ethics_scores[principle] - other.ethics_scores[principle])
                score_diffs.append(1.0 - diff)
        
        if not score_diffs:
            return 0.5
        
        # Verletzungs-Übereinstimmung
        violations_match = set(self.violations) == set(other.violations)
        violation_score = 1.0 if violations_match else 0.3
        
        # Kombiniert
        return statistics.mean(score_diffs) * 0.7 + violation_score * 0.3
    
    def _calculate_sequence_similarity(self, other: 'DecisionDNA') -> float:
        """Berechnet Ähnlichkeit der Modul-Sequenzen."""
        if not self.module_sequence or not other.module_sequence:
            return 0.5
        
        # Gemeinsame Module
        common_modules = set(self.module_sequence) & set(other.module_sequence)
        all_modules = set(self.module_sequence) | set(other.module_sequence)
        
        if not all_modules:
            return 1.0
        
        jaccard = len(common_modules) / len(all_modules)
        
        # Reihenfolgen-Bonus
        if self.module_sequence == other.module_sequence:
            order_bonus = 0.2
        else:
            order_bonus = 0.0
        
        return min(1.0, jaccard + order_bonus)


class ReplayDNA:
    """
    Replay DNA System - Speichert und analysiert Entscheidungs-DNA für Mustererkennung.
    
    Ermöglicht das Wiederverwenden erfolgreicher Entscheidungsmuster und
    das Lernen aus vergangenen Erfahrungen.
    """
    
    def __init__(self, storage_dir: str = "replay_dna", max_storage: int = 10000):
        """
        Initialisiert das Replay DNA System.
        
        Args:
            storage_dir: Verzeichnis für DNA-Speicherung
            max_storage: Maximale Anzahl gespeicherter DNAs
        """
        self.storage_dir = Path(storage_dir)
        self.max_storage = max_storage
        
        # DNA-Speicher
        self.dna_storage = deque(maxlen=max_storage)
        self.dna_index = {}  # decision_id -> DNA
        
        # Pattern-Katalog
        self.pattern_catalog = {
            "success_patterns": defaultdict(list),
            "failure_patterns": defaultdict(list),
            "context_patterns": defaultdict(list),
            "sequence_patterns": defaultdict(list)
        }
        
        # Clustering
        self.dna_clusters = {}
        self.cluster_centroids = {}
        
        # Performance-Tracking
        self.performance_stats = {
            "total_stored": 0,
            "pattern_matches": 0,
            "successful_replays": 0,
            "failed_replays": 0,
            "average_similarity": 0.0
        }
        
        # Cache für schnelle Suche
        self.similarity_cache = {}
        self.pattern_cache = {}
        
        # Initialisierung
        self._initialize_storage()
    
    def _initialize_storage(self) -> None:
        """Initialisiert Speicherstruktur und lädt vorhandene DNAs."""
        # Verzeichnis erstellen
        self.storage_dir.mkdir(exist_ok=True)
        
        # Index laden falls vorhanden
        index_file = self.storage_dir / "dna_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                    print(f"✅ Lade {len(index_data)} DNA-Einträge aus Index")
                    
                    # DNAs laden
                    for dna_id, dna_file in index_data.items():
                        dna_path = self.storage_dir / dna_file
                        if dna_path.exists():
                            dna = self._load_dna(dna_path)
                            if dna:
                                self.dna_storage.append(dna)
                                self.dna_index[dna_id] = dna
                                
            except Exception as e:
                print(f"⚠️ Fehler beim Laden des DNA-Index: {e}")
        
        # Patterns laden
        patterns_file = self.storage_dir / "patterns.pkl"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'rb') as f:
                    self.pattern_catalog = pickle.load(f)
                print(f"✅ Pattern-Katalog geladen")
            except Exception as e:
                print(f"⚠️ Fehler beim Laden der Patterns: {e}")
    
    def store_decision(self, decision_context: Dict[str, Any]) -> DecisionDNA:
        """
        Speichert eine Entscheidung als DNA.
        
        Args:
            decision_context: Vollständiger Entscheidungskontext
            
        Returns:
            DecisionDNA: Die gespeicherte DNA
        """
        # DNA erstellen
        dna = self._create_dna(decision_context)
        
        # Zu Speicher hinzufügen
        self.dna_storage.append(dna)
        self.dna_index[dna.decision_id] = dna
        
        # Patterns aktualisieren
        self._update_patterns(dna)
        
        # Clustering aktualisieren
        if len(self.dna_storage) % 100 == 0:
            self._update_clusters()
        
        # Statistiken
        self.performance_stats["total_stored"] += 1
        
        # Persistieren
        self._save_dna(dna)
        
        return dna
    
    def _create_dna(self, context: Dict[str, Any]) -> DecisionDNA:
        """Erstellt DNA aus Entscheidungskontext."""
        decision_id = context.get("decision_id", f"DNA-{uuid.uuid4().hex[:12]}")
        timestamp = datetime.now()
        
        dna = DecisionDNA(decision_id, timestamp)
        
        # Context Hash
        context_data = {
            "user_input": context.get("user_input", ""),
            "path": context.get("path", ""),
            "profile": context.get("profile", {})
        }
        dna.context_hash = self._calculate_hash(context_data)
        
        # Input Signature
        input_text = context.get("user_input", context.get("text", ""))
        dna.input_signature = self._create_input_signature(input_text)
        
        # Decision Path
        dna.decision_path = context.get("path", "unknown")
        dna.confidence = context.get("confidence", 0.0)
        
        # Ethics DNA
        if "ethics" in context:
            ethics = context["ethics"]
            dna.ethics_scores = ethics.get("scores", {})
            dna.violations = ethics.get("violations", [])
        
        # Principle Weights aus Profil
        if "profile" in context:
            dna.principle_weights = context["profile"]
            dna.profile_snapshot = context["profile"].copy()
        
        # Module Sequence
        module_keys = [key for key in context.keys() if key.endswith("_result")]
        dna.module_sequence = [key.replace("_result", "") for key in module_keys]
        
        # Module Results (zusammengefasst)
        for module in dna.module_sequence:
            module_result = context.get(f"{module}_result", {})
            dna.module_results[module] = self._summarize_module_result(module_result)
        
        # Response Hash
        response = context.get("response", "")
        dna.response_hash = self._calculate_hash(response)
        
        # Processing Time
        dna.processing_time = context.get("processing_time", 0.0)
        
        # Tags generieren
        dna.tags = self._generate_tags(context)
        
        return dna
    
    def _calculate_hash(self, data: Any) -> str:
        """Berechnet Hash für Daten."""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _create_input_signature(self, text: str) -> str:
        """Erstellt Signatur für Input-Text."""
        # Normalisierung
        normalized = text.lower().strip()
        
        # Keywords extrahieren
        keywords = []
        important_words = ["was", "wie", "warum", "wann", "wo", "wer",
                          "what", "how", "why", "when", "where", "who",
                          "hilfe", "help", "problem", "lösung", "solution"]
        
        for word in important_words:
            if word in normalized:
                keywords.append(word)
        
        # Längen-Kategorie
        length_cat = "short" if len(text) < 50 else "medium" if len(text) < 200 else "long"
        
        # Signatur
        keyword_sig = "-".join(sorted(keywords)[:3]) if keywords else "general"
        return f"{length_cat}:{keyword_sig}"
    
    def _summarize_module_result(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fasst Modul-Ergebnis für DNA zusammen."""
        summary = {}
        
        # Wichtige Felder extrahieren
        important_fields = [
            "confidence", "score", "violations", "conflicts_detected",
            "drift_detected", "pattern_matched", "optimization_performed"
        ]
        
        for field in important_fields:
            if field in module_result:
                summary[field] = module_result[field]
        
        # Spezielle Behandlung für Listen/Dicts
        if "conflicts_detected" in module_result:
            conflicts = module_result["conflicts_detected"]
            summary["conflict_count"] = len(conflicts) if isinstance(conflicts, list) else 0
        
        return summary
    
    def _generate_tags(self, context: Dict[str, Any]) -> List[str]:
        """Generiert Tags für bessere Kategorisierung."""
        tags = []
        
        # Path-Tag
        path = context.get("path", "unknown")
        tags.append(f"path:{path}")
        
        # Confidence-Tag
        confidence = context.get("confidence", 0.5)
        if confidence > 0.8:
            tags.append("high_confidence")
        elif confidence < 0.5:
            tags.append("low_confidence")
        
        # Violation-Tags
        violations = context.get("ethics", {}).get("violations", [])
        if violations:
            tags.append("has_violations")
            for violation in violations[:2]:
                tags.append(f"violation:{violation}")
        
        # Module-Tags
        if "etb_result" in context:
            tags.append("conflict_resolved")
        if "meta_learner_result" in context:
            tags.append("learning_applied")
        
        return tags
    
    def find_similar_decisions(self, current_context: Dict[str, Any],
                              min_similarity: float = 0.6,
                              max_results: int = 10) -> List[Tuple[DecisionDNA, float]]:
        """
        Findet ähnliche vergangene Entscheidungen.
        
        Args:
            current_context: Aktueller Entscheidungskontext
            min_similarity: Minimale Ähnlichkeit (0.0-1.0)
            max_results: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von (DNA, Ähnlichkeit) Tupeln
        """
        # Temporäre DNA für Vergleich erstellen
        current_dna = self._create_dna(current_context)
        
        # Cache-Key
        cache_key = f"{current_dna.context_hash}:{current_dna.input_signature}"
        if cache_key in self.similarity_cache:
            cached_results = self.similarity_cache[cache_key]
            return cached_results[:max_results]
        
        # Ähnlichkeiten berechnen
        similarities = []
        
        for stored_dna in self.dna_storage:
            similarity = current_dna.calculate_similarity(stored_dna)
            
            if similarity >= min_similarity:
                similarities.append((stored_dna, similarity))
        
        # Sortieren nach Ähnlichkeit
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = similarities[:max_results]
        
        # Cache aktualisieren
        self.similarity_cache[cache_key] = results
        
        # Statistiken
        if results:
            self.performance_stats["pattern_matches"] += 1
            avg_sim = statistics.mean([s for _, s in results])
            self.performance_stats["average_similarity"] = (
                self.performance_stats["average_similarity"] * 0.9 + avg_sim * 0.1
            )
        
        return results
    
    def get_pattern_recommendations(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gibt Empfehlungen basierend auf erkannten Mustern.
        
        Args:
            current_context: Aktueller Kontext
            
        Returns:
            Dict mit Empfehlungen und Mustern
        """
        recommendations = {
            "suggested_path": None,
            "confidence_prediction": None,
            "likely_violations": [],
            "successful_patterns": [],
            "warning_patterns": [],
            "module_suggestions": []
        }
        
        # Ähnliche Entscheidungen finden
        similar_decisions = self.find_similar_decisions(current_context, min_similarity=0.7)
        
        if not similar_decisions:
            return recommendations
        
        # Pfad-Empfehlung
        path_votes = defaultdict(int)
        confidence_values = []
        violation_counts = defaultdict(int)
        
        for dna, similarity in similar_decisions:
            # Gewichtete Votes
            weight = similarity
            
            path_votes[dna.decision_path] += weight
            confidence_values.append(dna.confidence * weight)
            
            for violation in dna.violations:
                violation_counts[violation] += weight
        
        # Bester Pfad
        if path_votes:
            best_path = max(path_votes.items(), key=lambda x: x[1])
            recommendations["suggested_path"] = best_path[0]
        
        # Konfidenz-Vorhersage
        if confidence_values:
            recommendations["confidence_prediction"] = sum(confidence_values) / len(confidence_values)
        
        # Wahrscheinliche Verletzungen
        likely_violations = [
            v for v, count in violation_counts.items()
            if count > len(similar_decisions) * 0.3
        ]
        recommendations["likely_violations"] = likely_violations
        
        # Erfolgreiche Patterns
        for dna, sim in similar_decisions[:3]:
            if dna.feedback and dna.feedback.get("success", 0) > 0.8:
                recommendations["successful_patterns"].append({
                    "decision_id": dna.decision_id,
                    "similarity": sim,
                    "path": dna.decision_path,
                    "confidence": dna.confidence,
                    "key_modules": dna.module_sequence[:3]
                })
        
        # Warnung bei problematischen Patterns
        for dna, sim in similar_decisions:
            if len(dna.violations) > 2 or dna.confidence < 0.5:
                recommendations["warning_patterns"].append({
                    "decision_id": dna.decision_id,
                    "similarity": sim,
                    "violations": dna.violations,
                    "confidence": dna.confidence,
                    "warning": "Ähnliche Entscheidung hatte Probleme"
                })
        
        # Modul-Vorschläge
        module_frequency = defaultdict(int)
        for dna, sim in similar_decisions[:5]:
            for module in dna.module_sequence:
                module_frequency[module] += sim
        
        suggested_modules = sorted(module_frequency.items(), key=lambda x: x[1], reverse=True)
        recommendations["module_suggestions"] = [m for m, _ in suggested_modules[:5]]
        
        return recommendations
    
    def analyze_learning_potential(self, decision_dna: DecisionDNA) -> Dict[str, Any]:
        """
        Analysiert das Lernpotential einer Entscheidung.
        
        Args:
            decision_dna: Die zu analysierende DNA
            
        Returns:
            Dict mit Lernpotential-Analyse
        """
        analysis = {
            "learning_value": 0.0,
            "uniqueness": 0.0,
            "pattern_contribution": 0.0,
            "improvement_areas": [],
            "similar_decisions_count": 0,
            "recommendation": ""
        }
        
        # Finde ähnliche Entscheidungen
        similar = []
        for stored_dna in self.dna_storage:
            if stored_dna.decision_id != decision_dna.decision_id:
                sim = decision_dna.calculate_similarity(stored_dna)
                if sim > 0.5:
                    similar.append((stored_dna, sim))
        
        analysis["similar_decisions_count"] = len(similar)
        
        # Uniqueness berechnen
        if not similar:
            analysis["uniqueness"] = 1.0
        else:
            avg_similarity = statistics.mean([s for _, s in similar])
            analysis["uniqueness"] = 1.0 - avg_similarity
        
        # Learning Value
        factors = []
        
        # Neue Situation
        if analysis["uniqueness"] > 0.7:
            factors.append(0.8)
            analysis["improvement_areas"].append("Neue Situation - hoher Lernwert")
        
        # Unerwartetes Ergebnis
        if decision_dna.confidence < 0.6:
            factors.append(0.6)
            analysis["improvement_areas"].append("Niedrige Konfidenz - Verbesserungspotential")
        
        # Verletzungen
        if decision_dna.violations:
            factors.append(0.7)
            analysis["improvement_areas"].append(f"Verletzungen: {', '.join(decision_dna.violations)}")
        
        # Erfolgreiche neue Strategie
        if decision_dna.feedback and decision_dna.feedback.get("success", 0) > 0.8 and analysis["uniqueness"] > 0.5:
            factors.append(0.9)
            analysis["improvement_areas"].append("Erfolgreiche neue Strategie")
        
        # Learning Value berechnen
        if factors:
            analysis["learning_value"] = statistics.mean(factors)
        else:
            analysis["learning_value"] = 0.3
        
        # Pattern Contribution
        # Wie sehr trägt diese Entscheidung zu Mustererkennung bei?
        if analysis["uniqueness"] > 0.6:
            analysis["pattern_contribution"] = 0.8
        elif analysis["similar_decisions_count"] < 3:
            analysis["pattern_contribution"] = 0.6  # Verstärkt seltenes Muster
        else:
            analysis["pattern_contribution"] = 0.3
        
        # Empfehlung
        if analysis["learning_value"] > 0.7:
            analysis["recommendation"] = "Hoher Lernwert - für Meta-Learning priorisieren"
        elif analysis["learning_value"] > 0.5:
            analysis["recommendation"] = "Moderater Lernwert - in Musteranalyse einbeziehen"
        else:
            analysis["recommendation"] = "Geringer Lernwert - Standard-Verarbeitung"
        
        return analysis
    
    def _update_patterns(self, dna: DecisionDNA) -> None:
        """Aktualisiert Pattern-Katalog mit neuer DNA."""
        # Success/Failure Patterns
        if dna.feedback:
            success_score = dna.feedback.get("success", 0.5)
            if success_score > 0.7:
                pattern_key = f"{dna.decision_path}:{dna.input_signature}"
                self.pattern_catalog["success_patterns"][pattern_key].append(dna.decision_id)
            elif success_score < 0.3:
                pattern_key = f"{dna.decision_path}:{dna.input_signature}"
                self.pattern_catalog["failure_patterns"][pattern_key].append(dna.decision_id)
        
        # Context Patterns
        context_key = f"{dna.context_hash[:8]}"
        self.pattern_catalog["context_patterns"][context_key].append(dna.decision_id)
        
        # Sequence Patterns
        if len(dna.module_sequence) > 2:
            seq_key = ":".join(dna.module_sequence[:3])
            self.pattern_catalog["sequence_patterns"][seq_key].append(dna.decision_id)
    
    def _update_clusters(self) -> None:
        """Aktualisiert DNA-Cluster für effizientere Suche."""
        # Vereinfachtes Clustering basierend auf Haupt-Merkmalen
        clusters = defaultdict(list)
        
        for dna in self.dna_storage:
            # Cluster-Key aus wichtigsten Merkmalen
            cluster_key = f"{dna.decision_path}:{int(dna.confidence*10)}"
            clusters[cluster_key].append(dna)
        
        self.dna_clusters = dict(clusters)
        
        # Centroide berechnen (vereinfacht)
        for cluster_key, cluster_dnas in self.dna_clusters.items():
            if cluster_dnas:
                # Durchschnittliche Eigenschaften als Centroid
                avg_confidence = statistics.mean([d.confidence for d in cluster_dnas])
                self.cluster_centroids[cluster_key] = {
                    "confidence": avg_confidence,
                    "size": len(cluster_dnas)
                }
    
    def _save_dna(self, dna: DecisionDNA) -> None:
        """Speichert DNA persistent."""
        try:
            # DNA-Datei
            dna_file = f"dna_{dna.decision_id}.json"
            dna_path = self.storage_dir / dna_file
            
            with open(dna_path, 'w') as f:
                json.dump(dna.to_dict(), f, indent=2)
            
            # Index aktualisieren
            self._update_index()
            
            # Patterns speichern (periodisch)
            if self.performance_stats["total_stored"] % 50 == 0:
                self._save_patterns()
                
        except Exception as e:
            print(f"⚠️ Fehler beim Speichern der DNA: {e}")
    
    def _load_dna(self, dna_path: Path) -> Optional[DecisionDNA]:
        """Lädt DNA von Datei."""
        try:
            with open(dna_path, 'r') as f:
                data = json.load(f)
                return DecisionDNA.from_dict(data)
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der DNA {dna_path}: {e}")
            return None
    
    def _update_index(self) -> None:
        """Aktualisiert den DNA-Index."""
        index = {}
        for dna in self.dna_storage:
            index[dna.decision_id] = f"dna_{dna.decision_id}.json"
        
        index_path = self.storage_dir / "dna_index.json"
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _save_patterns(self) -> None:
        """Speichert Pattern-Katalog."""
        patterns_path = self.storage_dir / "patterns.pkl"
        with open(patterns_path, 'wb') as f:
            pickle.dump(self.pattern_catalog, f)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über das DNA-System zurück."""
        stats = self.performance_stats.copy()
        
        # Zusätzliche Statistiken
        stats["stored_dnas"] = len(self.dna_storage)
        stats["clusters"] = len(self.dna_clusters)
        stats["success_patterns"] = sum(len(v) for v in self.pattern_catalog["success_patterns"].values())
        stats["failure_patterns"] = sum(len(v) for v in self.pattern_catalog["failure_patterns"].values())
        
        # Durchschnittswerte
        if self.dna_storage:
            confidences = [dna.confidence for dna in self.dna_storage]
            stats["average_confidence"] = statistics.mean(confidences)
            
            violation_counts = [len(dna.violations) for dna in self.dna_storage]
            stats["average_violations"] = statistics.mean(violation_counts)
        
        return stats
    
    def export_patterns(self, output_file: str = "patterns_export.json") -> bool:
        """
        Exportiert erkannte Muster für externe Analyse.
        
        Args:
            output_file: Ausgabedatei
            
        Returns:
            bool: Erfolg
        """
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "statistics": self.get_statistics(),
                "patterns": {}
            }
            
            # Top Patterns exportieren
            for pattern_type, patterns in self.pattern_catalog.items():
                top_patterns = sorted(
                    patterns.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:20]
                
                export_data["patterns"][pattern_type] = [
                    {
                        "pattern": pattern,
                        "frequency": len(dna_ids),
                        "example_ids": dna_ids[:5]
                    }
                    for pattern, dna_ids in top_patterns
                ]
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Export fehlgeschlagen: {e}")
            return False


def run_module(input_data: dict, config: dict = None) -> dict:
    """
    Hauptschnittstelle des Moduls gemäß INTEGRA-Standard.
    
    Args:
        input_data (dict): Eingangsdaten mit:
                          - 'action': 'store', 'find_similar', 'analyze', 'get_recommendations'
                          - 'decision_context': Entscheidungskontext
                          - 'min_similarity': Für 'find_similar' (optional)
                          - 'max_results': Für 'find_similar' (optional)
        config (dict, optional): Modulkonfiguration mit:
                               - 'storage_dir': Speicherverzeichnis
                               - 'max_storage': Maximale DNA-Anzahl
        
    Returns:
        dict: Ergebnisstruktur mit Standard-Feldern
    """
    log = []
    timestamp_start = datetime.now()
    
    try:
        # Konfiguration
        storage_dir = "replay_dna"
        max_storage = 10000
        
        if config:
            storage_dir = config.get('storage_dir', storage_dir)
            max_storage = config.get('max_storage', max_storage)
        
        replay_dna = ReplayDNA(storage_dir, max_storage)
        log.append(f"Replay DNA initialisiert - Speicher: {len(replay_dna.dna_storage)} DNAs")
        
        # Action bestimmen
        action = input_data.get('action', 'store')
        decision_context = input_data.get('decision_context', {})
        
        result = {}
        issues = []
        
        if action == 'store':
            # DNA speichern
            if not decision_context:
                raise ValueError("Kein Entscheidungskontext zum Speichern")
            
            log.append("Speichere Entscheidungs-DNA...")
            dna = replay_dna.store_decision(decision_context)
            
            # Lernpotential analysieren
            learning_analysis = replay_dna.analyze_learning_potential(dna)
            
            result = {
                'stored_dna': {
                    'decision_id': dna.decision_id,
                    'timestamp': dna.timestamp.isoformat(),
                    'confidence': dna.confidence,
                    'violations': dna.violations,
                    'tags': dna.tags
                },
                'learning_potential': learning_analysis,
                'statistics': replay_dna.get_statistics()
            }
            
            log.append(f"DNA gespeichert: {dna.decision_id}")
            log.append(f"Lernwert: {learning_analysis['learning_value']:.2f}")
            
            # Learning potential als Issue wenn hoch
            if learning_analysis['learning_value'] > 0.7:
                issues.append({
                    'type': 'high_learning_value',
                    'severity': 'moderate',
                    'principle': 'learning',
                    'description': f"Hoher Lernwert ({learning_analysis['learning_value']:.2f}) - {learning_analysis['recommendation']}"
                })
        
        elif action == 'find_similar':
            # Ähnliche Entscheidungen finden
            if not decision_context:
                raise ValueError("Kein Kontext für Ähnlichkeitssuche")
            
            min_similarity = input_data.get('min_similarity', 0.6)
            max_results = input_data.get('max_results', 10)
            
            log.append(f"Suche ähnliche Entscheidungen (min_sim: {min_similarity})...")
            similar_decisions = replay_dna.find_similar_decisions(
                decision_context, min_similarity, max_results
            )
            
            result = {
                'similar_decisions': [
                    {
                        'decision_id': dna.decision_id,
                        'similarity': sim,
                        'confidence': dna.confidence,
                        'path': dna.decision_path,
                        'violations': dna.violations,
                        'timestamp': dna.timestamp.isoformat()
                    }
                    for dna, sim in similar_decisions
                ],
                'count': len(similar_decisions)
            }
            
            log.append(f"Gefunden: {len(similar_decisions)} ähnliche Entscheidungen")
            
            # Pattern warnings
            for dna, sim in similar_decisions[:3]:
                if dna.violations and sim > 0.8:
                    issues.append({
                        'type': 'similar_violation_pattern',
                        'severity': 'high',
                        'principle': ', '.join(dna.violations),
                        'description': f'Ähnliche Entscheidung ({sim:.2f}) hatte Verletzungen: {", ".join(dna.violations)}'
                    })
        
        elif action == 'get_recommendations':
            # Pattern-basierte Empfehlungen
            if not decision_context:
                raise ValueError("Kein Kontext für Empfehlungen")
            
            log.append("Generiere Pattern-basierte Empfehlungen...")
            recommendations = replay_dna.get_pattern_recommendations(decision_context)
            
            result = recommendations
            
            if recommendations['suggested_path']:
                log.append(f"Empfohlener Pfad: {recommendations['suggested_path']}")
            if recommendations['confidence_prediction']:
                log.append(f"Erwartete Konfidenz: {recommendations['confidence_prediction']:.2f}")
            
            # Warnings als Issues
            for warning in recommendations.get('warning_patterns', []):
                issues.append({
                    'type': 'pattern_warning',
                    'severity': 'moderate',
                    'principle': 'awareness',
                    'description': warning['warning']
                })
        
        elif action == 'analyze':
            # Statistiken und Analyse
            log.append("Erstelle DNA-System Analyse...")
            
            stats = replay_dna.get_statistics()
            
            # Pattern-Export
            export_success = replay_dna.export_patterns()
            
            result = {
                'statistics': stats,
                'pattern_export': export_success,
                'cluster_count': len(replay_dna.dna_clusters),
                'top_patterns': {}
            }
            
            # Top Patterns
            for pattern_type, patterns in replay_dna.pattern_catalog.items():
                if patterns:
                    top = sorted(patterns.items(), key=lambda x: len(x[1]), reverse=True)[:3]
                    result['top_patterns'][pattern_type] = [
                        {'pattern': p, 'frequency': len(ids)} for p, ids in top
                    ]
            
            log.append(f"Gespeicherte DNAs: {stats['stored_dnas']}")
            log.append(f"Erfolgs-Patterns: {stats['success_patterns']}")
        
        else:
            raise ValueError(f"Unbekannte Action: {action}")
        
        # Konfidenz
        confidence = 0.95  # DNA-System ist deterministisch
        
        processing_time = (datetime.now() - timestamp_start).total_seconds()
        log.append(f"Verarbeitung in {processing_time:.3f}s")
        
        return {
            'result': result,
            'log': log,
            'confidence': confidence,
            'issues': issues,
            'processing_time': processing_time,
            'module': 'replay_dna',
            'version': '1.0',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        log.append(f"FEHLER: {str(e)}")
        return {
            'result': {
                'error': True,
                'error_message': str(e)
            },
            'log': log,
            'confidence': 0.0,
            'issues': [{
                'type': 'error',
                'severity': 'critical',
                'principle': 'system',
                'description': f'Replay DNA Fehler: {str(e)}'
            }],
            'error': True,
            'error_message': str(e),
            'timestamp': datetime.now().isoformat()
        }


def demo():
    """Demonstriert die Verwendung des Replay DNA Systems."""
    print("=== INTEGRA Replay DNA Demo ===")
    print()
    
    # Test-Kontexte erstellen
    test_contexts = [
        {
            "decision_id": "DEMO-001",
            "user_input": "Wie kann ich jemandem helfen ohne zu schaden?",
            "path": "deep",
            "confidence": 0.85,
            "ethics": {
                "scores": {"nurturing": 0.9, "integrity": 0.8},
                "violations": []
            },
            "etb_result": {"conflicts_detected": []},
            "response": "Hier sind ethische Wege zu helfen...",
            "profile": profiles.get_default_profile()
        },
        {
            "decision_id": "DEMO-002",
            "user_input": "Wie kann ich jemanden unterstützen?",  # Ähnlich zu 001
            "path": "deep",
            "confidence": 0.80,
            "ethics": {
                "scores": {"nurturing": 0.85, "integrity": 0.85},
                "violations": []
            },
            "response": "Unterstützung kann verschiedene Formen annehmen...",
            "profile": profiles.get_default_profile()
        },
        {
            "decision_id": "DEMO-003",
            "user_input": "Darf ich persönliche Daten verwenden?",
            "path": "deep",
            "confidence": 0.6,
            "ethics": {
                "scores": {"integrity": 0.4, "governance": 0.5},
                "violations": ["integrity", "governance"]
            },
            "response": "Datenschutz ist wichtig...",
            "profile": profiles.get_default_profile()
        }
    ]
    
    # DNA System testen
    print("1. Speichere Entscheidungen als DNA:")
    
    for i, context in enumerate(test_contexts):
        result = run_module({
            'action': 'store',
            'decision_context': context
        })
        
        if not result.get('error'):
            stored = result['result']['stored_dna']
            learning = result['result']['learning_potential']
            print(f"\n   DNA #{i+1}: {stored['decision_id']}")
            print(f"   Konfidenz: {stored['confidence']:.2f}")
            print(f"   Lernwert: {learning['learning_value']:.2f}")
            print(f"   Empfehlung: {learning['recommendation']}")
    
    # Ähnliche Entscheidungen finden
    print("\n\n2. Finde ähnliche Entscheidungen:")
    
    new_context = {
        "user_input": "Wie unterstütze ich Menschen ethisch?",
        "path": "deep",
        "profile": profiles.get_default_profile()
    }
    
    result = run_module({
        'action': 'find_similar',
        'decision_context': new_context,
        'min_similarity': 0.5
    })
    
    if not result.get('error'):
        similar = result['result']['similar_decisions']
        print(f"\n   Gefunden: {len(similar)} ähnliche Entscheidungen")
        
        for decision in similar[:3]:
            print(f"\n   - ID: {decision['decision_id']}")
            print(f"     Ähnlichkeit: {decision['similarity']:.2f}")
            print(f"     Pfad: {decision['path']}, Konfidenz: {decision['confidence']:.2f}")
            if decision['violations']:
                print(f"     ⚠️  Violations: {', '.join(decision['violations'])}")
    
    # Pattern-Empfehlungen
    print("\n\n3. Pattern-basierte Empfehlungen:")
    
    result = run_module({
        'action': 'get_recommendations',
        'decision_context': new_context
    })
    
    if not result.get('error'):
        recommendations = result['result']
        
        if recommendations['suggested_path']:
            print(f"   Empfohlener Pfad: {recommendations['suggested_path']}")
        if recommendations['confidence_prediction']:
            print(f"   Erwartete Konfidenz: {recommendations['confidence_prediction']:.2f}")
        
        if recommendations['successful_patterns']:
            print(f"\n   Erfolgreiche Muster:")
            for pattern in recommendations['successful_patterns']:
                print(f"   - Ähnlichkeit: {pattern['similarity']:.2f}, Pfad: {pattern['path']}")
        
        if recommendations['warning_patterns']:
            print(f"\n   ⚠️  Warnungen:")
            for warning in recommendations['warning_patterns']:
                print(f"   - {warning['warning']}")
    
    # System-Analyse
    print("\n\n4. System-Analyse:")
    
    result = run_module({'action': 'analyze'})
    
    if not result.get('error'):
        stats = result['result']['statistics']
        print(f"   Gespeicherte DNAs: {stats['stored_dnas']}")
        print(f"   Pattern-Matches: {stats['pattern_matches']}")
        print(f"   Durchschn. Ähnlichkeit: {stats['average_similarity']:.2f}")
        
        if result['result']['top_patterns']:
            print(f"\n   Top Patterns:")
            for pattern_type, patterns in result['result']['top_patterns'].items():
                if patterns:
                    print(f"   - {pattern_type}: {patterns[0]['pattern']} ({patterns[0]['frequency']}x)")
    
    # Issues prüfen
    print("\n\n5. Issues aus Demo:")
    for i, result in enumerate([result]):
        if result.get('issues'):
            print(f"\n   Issues in letztem Aufruf:")
            for issue in result['issues']:
                print(f"   - [{issue['severity']}] {issue['description']}")
    
    print("\n✅ Replay DNA Demo abgeschlossen!")
    print("Das System kann Entscheidungsmuster erkennen und wiederverwenden.")


if __name__ == "__main__":
    demo()