# -*- coding: utf-8 -*-
"""
Modulname: aso.py
Beschreibung: Architectural Self-Optimizer für INTEGRA Full - Meta-Meta-Optimierung der Entscheidungsarchitektur
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Aufgeteilt in spezialisierte Komponenten
- Externe Konfiguration möglich
- Verbesserte Fehlerbehandlung
"""

from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque, Counter
from pathlib import Path
import json
import statistics
import copy
import uuid

# Standardisierte Imports
try:
    from integra.core import principles, profiles
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        log_manager = None  # Fallback ohne Logging
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
            log_manager = None
        except ImportError:
            print("❌ Fehler: Core Module nicht gefunden!")
            # Dummy-Klassen für Standalone-Betrieb
            class principles:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            class profiles:
                @staticmethod
                def get_default_profile():
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            log_manager = None


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class OptimizationType(Enum):
    """Typen von Architektur-Optimierungen."""
    MODULE_REORDER = "module_reorder"
    MODULE_SKIP = "module_skip"
    THRESHOLD_ADJUST = "threshold_adjust"
    SEQUENCE_OPTIMIZE = "sequence_optimize"
    PARALLEL_ENABLE = "parallel_enable"
    CACHE_STRATEGY = "cache_strategy"


class BottleneckType(Enum):
    """Typen von Performance-Engpässen."""
    TIME = "time_bottleneck"
    MEMORY = "memory_bottleneck"
    QUALITY = "quality_bottleneck"
    DEPENDENCY = "dependency_bottleneck"
    ERROR_RATE = "error_rate_bottleneck"


class PerformanceLevel(Enum):
    """Performance-Bewertungsstufen."""
    CRITICAL = "critical"
    POOR = "poor"
    ACCEPTABLE = "acceptable"
    GOOD = "good"
    EXCELLENT = "excellent"


@dataclass
class ModulePerformance:
    """Performance-Daten eines Moduls."""
    module_name: str
    execution_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_rates: deque = field(default_factory=lambda: deque(maxlen=100))
    value_scores: deque = field(default_factory=lambda: deque(maxlen=100))
    skip_count: int = 0
    total_runs: int = 0
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def avg_execution_time(self) -> float:
        return statistics.mean(self.execution_times) if self.execution_times else 0.0
    
    @property
    def error_rate(self) -> float:
        return statistics.mean(self.error_rates) if self.error_rates else 0.0
    
    @property
    def avg_value_score(self) -> float:
        return statistics.mean(self.value_scores) if self.value_scores else 0.5
    
    @property
    def skip_rate(self) -> float:
        total = self.total_runs + self.skip_count
        return self.skip_count / total if total > 0 else 0.0


@dataclass
class OptimizationDecision:
    """Strukturierte Optimierungsentscheidung."""
    decision_id: str
    timestamp: datetime
    optimization_type: OptimizationType
    target_modules: List[str]
    parameters: Dict[str, Any]
    expected_improvement: float
    risk_level: float
    rationale: str
    reversible: bool = True
    applied: bool = False
    rollback_data: Optional[Dict[str, Any]] = None


@dataclass
class ArchitectureState:
    """Aktueller Zustand der System-Architektur."""
    module_sequence: List[str]
    active_modules: Set[str]
    module_configs: Dict[str, Dict[str, Any]]
    performance_thresholds: Dict[str, float]
    optimization_rules: Dict[str, bool]
    version: str = "1.0"
    last_optimization: Optional[datetime] = None


# ============================================================================
# KOMPONENTEN
# ============================================================================

class PerformanceAnalyzer:
    """Analysiert Performance-Daten der Module."""
    
    def __init__(self):
        self.module_performance: Dict[str, ModulePerformance] = {}
        self.system_metrics = {
            "total_decisions": 0,
            "avg_decision_time": 0.0,
            "error_rate": 0.0,
            "efficiency_score": 0.5
        }
    
    def update_from_context(self, context: Dict[str, Any]) -> None:
        """Aktualisiert Performance-Daten aus dem Context."""
        # Durchlaufe alle Modul-Ergebnisse im Context
        for key, value in context.items():
            if key.endswith("_result") and isinstance(value, dict):
                module_name = key.replace("_result", "")
                self._update_module_performance(module_name, value)
        
        # System-Metriken aktualisieren
        self._update_system_metrics()
    
    def _update_module_performance(self, module_name: str, result: Dict[str, Any]) -> None:
        """Aktualisiert Performance eines einzelnen Moduls."""
        if module_name not in self.module_performance:
            self.module_performance[module_name] = ModulePerformance(module_name)
        
        perf = self.module_performance[module_name]
        
        # Execution Time
        exec_time = result.get("processing_time", result.get("execution_time", 0.01))
        perf.execution_times.append(exec_time)
        
        # Error Rate
        had_error = result.get("error", False) or not result.get("success", True)
        perf.error_rates.append(1.0 if had_error else 0.0)
        
        # Value Score (Modul-spezifisch)
        value = self._calculate_module_value(module_name, result)
        perf.value_scores.append(value)
        
        perf.total_runs += 1
    
    def _calculate_module_value(self, module_name: str, result: Dict[str, Any]) -> float:
        """Berechnet den Wertbeitrag eines Moduls."""
        # Modul-spezifische Bewertung
        if module_name == "etb":
            # ETB bringt Wert durch Konfliktlösung
            conflicts = result.get("conflicts_detected", [])
            return min(1.0, len(conflicts) * 0.3 + 0.3)
        
        elif module_name == "pae":
            # PAE bringt Wert durch Prioritätsentscheidungen
            if result.get("principle_chosen"):
                return 0.8
            return 0.3
        
        elif module_name == "vdd":
            # VDD bringt Wert durch Drift-Erkennung
            if result.get("drift_detected"):
                return 0.9
            return 0.2
        
        elif module_name == "meta_learner":
            # Meta-Learner bringt Wert durch Profil-Updates
            updates = result.get("profile_updates", {})
            return min(1.0, len(updates) * 0.2 + 0.3)
        
        # Standard für unbekannte Module
        return 0.5 if not result.get("error") else 0.0
    
    def _update_system_metrics(self) -> None:
        """Aktualisiert System-weite Metriken."""
        self.system_metrics["total_decisions"] += 1
        
        if self.module_performance:
            # Durchschnittliche Entscheidungszeit
            total_time = sum(m.avg_execution_time for m in self.module_performance.values())
            self.system_metrics["avg_decision_time"] = total_time
            
            # System-Fehlerrate
            error_rates = [m.error_rate for m in self.module_performance.values()]
            self.system_metrics["error_rate"] = statistics.mean(error_rates) if error_rates else 0.0
            
            # Effizienz-Score
            self.system_metrics["efficiency_score"] = self._calculate_efficiency_score()
    
    def _calculate_efficiency_score(self) -> float:
        """Berechnet System-Effizienz-Score."""
        factors = []
        
        # Zeit-Effizienz (schneller = besser)
        if self.system_metrics["avg_decision_time"] > 0:
            time_factor = 1.0 / (1.0 + self.system_metrics["avg_decision_time"])
            factors.append(time_factor)
        
        # Fehler-Effizienz (weniger Fehler = besser)
        error_factor = 1.0 - self.system_metrics["error_rate"]
        factors.append(error_factor)
        
        # Wert-Effizienz (höherer Wert = besser)
        if self.module_performance:
            avg_values = [m.avg_value_score for m in self.module_performance.values()]
            value_factor = statistics.mean(avg_values) if avg_values else 0.5
            factors.append(value_factor)
        
        return statistics.mean(factors) if factors else 0.5
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identifiziert Performance-Engpässe."""
        bottlenecks = []
        
        for module_name, perf in self.module_performance.items():
            # Zeit-Bottleneck
            if perf.avg_execution_time > 0.1:  # 100ms Schwellwert
                bottlenecks.append({
                    "type": BottleneckType.TIME,
                    "module": module_name,
                    "severity": min(1.0, perf.avg_execution_time / 0.5),
                    "metric": perf.avg_execution_time,
                    "impact": f"{perf.avg_execution_time:.3f}s durchschnittliche Ausführungszeit"
                })
            
            # Fehlerrate-Bottleneck
            if perf.error_rate > 0.1:
                bottlenecks.append({
                    "type": BottleneckType.ERROR_RATE,
                    "module": module_name,
                    "severity": min(1.0, perf.error_rate),
                    "metric": perf.error_rate,
                    "impact": f"{perf.error_rate:.1%} Fehlerrate"
                })
            
            # Niedriger Wert-Bottleneck
            if perf.avg_value_score < 0.3 and perf.total_runs > 10:
                bottlenecks.append({
                    "type": BottleneckType.QUALITY,
                    "module": module_name,
                    "severity": 1.0 - perf.avg_value_score,
                    "metric": perf.avg_value_score,
                    "impact": f"Niedriger Wertbeitrag: {perf.avg_value_score:.2f}"
                })
        
        # Sortiere nach Severity
        return sorted(bottlenecks, key=lambda x: x["severity"], reverse=True)


class OptimizationEngine:
    """Generiert und bewertet Optimierungsmöglichkeiten."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.optimization_history: deque = deque(maxlen=100)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Lädt Standard-Konfiguration."""
        config_path = Path(__file__).parent / "config" / "aso_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Fallback-Konfiguration
        return {
            "optimization_threshold": 0.15,
            "max_module_reorder": 3,
            "skip_threshold": 0.8,
            "min_data_points": 20,
            "risk_tolerance": 0.3
        }
    
    def generate_optimizations(self, 
                             performance: PerformanceAnalyzer,
                             architecture: ArchitectureState,
                             bottlenecks: List[Dict[str, Any]]) -> List[OptimizationDecision]:
        """Generiert Optimierungsvorschläge."""
        optimizations = []
        
        # Bottleneck-basierte Optimierungen
        for bottleneck in bottlenecks[:5]:  # Top 5 Bottlenecks
            if bottleneck["severity"] > self.config["optimization_threshold"]:
                opt = self._generate_bottleneck_optimization(bottleneck, performance, architecture)
                if opt:
                    optimizations.append(opt)
        
        # Modul-Reihenfolge optimieren
        reorder_opt = self._evaluate_module_reordering(performance, architecture)
        if reorder_opt:
            optimizations.append(reorder_opt)
        
        # Skip-Rules für ineffiziente Module
        skip_opts = self._evaluate_skip_opportunities(performance, architecture)
        optimizations.extend(skip_opts)
        
        # Schwellwert-Anpassungen
        threshold_opts = self._evaluate_threshold_adjustments(performance, architecture)
        optimizations.extend(threshold_opts)
        
        # Sortiere nach erwartetem Nutzen
        return sorted(optimizations, 
                     key=lambda x: x.expected_improvement * (1 - x.risk_level), 
                     reverse=True)
    
    def _generate_bottleneck_optimization(self, 
                                        bottleneck: Dict[str, Any],
                                        performance: PerformanceAnalyzer,
                                        architecture: ArchitectureState) -> Optional[OptimizationDecision]:
        """Generiert Optimierung für einen spezifischen Bottleneck."""
        module = bottleneck["module"]
        
        if bottleneck["type"] == BottleneckType.TIME:
            # Bei Zeit-Bottlenecks: Modul-Skip oder Caching
            if performance.module_performance[module].avg_value_score < 0.4:
                return OptimizationDecision(
                    decision_id=f"OPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
                    timestamp=datetime.now(),
                    optimization_type=OptimizationType.MODULE_SKIP,
                    target_modules=[module],
                    parameters={"skip_condition": "low_complexity"},
                    expected_improvement=bottleneck["severity"] * 0.3,
                    risk_level=0.2,
                    rationale=f"{module} ist zeitintensiv bei geringem Wertbeitrag"
                )
        
        elif bottleneck["type"] == BottleneckType.ERROR_RATE:
            # Bei hoher Fehlerrate: Konfiguration anpassen
            return OptimizationDecision(
                decision_id=f"OPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
                timestamp=datetime.now(),
                optimization_type=OptimizationType.THRESHOLD_ADJUST,
                target_modules=[module],
                parameters={"error_tolerance": "increase", "fallback_mode": True},
                expected_improvement=bottleneck["severity"] * 0.4,
                risk_level=0.3,
                rationale=f"{module} hat hohe Fehlerrate - Fallback-Modus aktivieren"
            )
        
        return None
    
    def _evaluate_module_reordering(self,
                                  performance: PerformanceAnalyzer,
                                  architecture: ArchitectureState) -> Optional[OptimizationDecision]:
        """Bewertet Möglichkeiten zur Modul-Neuanordnung."""
        current_sequence = architecture.module_sequence
        
        # Finde Module die von ihren Ergebnissen profitieren könnten
        for i, module in enumerate(current_sequence[1:], 1):
            if module in performance.module_performance:
                perf = performance.module_performance[module]
                
                # Wenn Modul hohen Wert hat, könnte es früher laufen
                if perf.avg_value_score > 0.7 and i > len(current_sequence) // 2:
                    return OptimizationDecision(
                        decision_id=f"OPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
                        timestamp=datetime.now(),
                        optimization_type=OptimizationType.MODULE_REORDER,
                        target_modules=[module],
                        parameters={
                            "current_position": i,
                            "new_position": max(1, i - 2),
                            "reason": "high_value_early_execution"
                        },
                        expected_improvement=0.15,
                        risk_level=0.25,
                        rationale=f"{module} hat hohen Wert und könnte früher ausgeführt werden"
                    )
        
        return None
    
    def _evaluate_skip_opportunities(self,
                                   performance: PerformanceAnalyzer,
                                   architecture: ArchitectureState) -> List[OptimizationDecision]:
        """Bewertet Möglichkeiten für dynamisches Modul-Skipping."""
        opportunities = []
        
        for module_name, perf in performance.module_performance.items():
            # Module mit hoher Skip-Rate oder niedrigem Wert
            if perf.skip_rate > self.config["skip_threshold"] or \
               (perf.avg_value_score < 0.3 and perf.total_runs > self.config["min_data_points"]):
                
                opportunities.append(OptimizationDecision(
                    decision_id=f"OPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
                    timestamp=datetime.now(),
                    optimization_type=OptimizationType.MODULE_SKIP,
                    target_modules=[module_name],
                    parameters={
                        "skip_rule": f"confidence > 0.8 and complexity < 0.3",
                        "current_skip_rate": perf.skip_rate,
                        "fallback": "basic_result"
                    },
                    expected_improvement=0.1 * (1 - perf.avg_value_score),
                    risk_level=0.15,
                    rationale=f"{module_name} wird oft übersprungen oder hat geringen Wert"
                ))
        
        return opportunities
    
    def _evaluate_threshold_adjustments(self,
                                      performance: PerformanceAnalyzer,
                                      architecture: ArchitectureState) -> List[OptimizationDecision]:
        """Bewertet Schwellwert-Anpassungen."""
        opportunities = []
        
        # Beispiel: Fast-Path Threshold
        if "fast_path_confidence" in architecture.performance_thresholds:
            current_threshold = architecture.performance_thresholds["fast_path_confidence"]
            
            # Wenn System-Effizienz niedrig ist, mehr Fast-Path nutzen
            if performance.system_metrics["efficiency_score"] < 0.6:
                opportunities.append(OptimizationDecision(
                    decision_id=f"OPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
                    timestamp=datetime.now(),
                    optimization_type=OptimizationType.THRESHOLD_ADJUST,
                    target_modules=["decision_router"],
                    parameters={
                        "threshold": "fast_path_confidence",
                        "current_value": current_threshold,
                        "new_value": max(0.5, current_threshold - 0.05),
                        "direction": "decrease"
                    },
                    expected_improvement=0.2,
                    risk_level=0.2,
                    rationale="Effizienz durch mehr Fast-Path-Nutzung erhöhen"
                ))
        
        return opportunities


class ArchitectureManager:
    """Verwaltet und modifiziert die System-Architektur."""
    
    def __init__(self):
        self.current_state = self._initialize_architecture()
        self.state_history: deque = deque(maxlen=50)
        self.rollback_points: List[Tuple[datetime, ArchitectureState]] = []
    
    def _initialize_architecture(self) -> ArchitectureState:
        """Initialisiert die Standard-Architektur."""
        return ArchitectureState(
            module_sequence=[
                "simple_ethics",
                "etb",
                "pae",
                "vdd",
                "mini_learner",
                "replay_dna",
                "meta_learner",
                "mini_audit",
                "aso"
            ],
            active_modules={
                "simple_ethics", "etb", "pae", "vdd", 
                "mini_learner", "replay_dna", "meta_learner", 
                "mini_audit", "aso"
            },
            module_configs={},
            performance_thresholds={
                "fast_path_confidence": 0.85,
                "deep_path_trigger": 0.6,
                "module_skip_confidence": 0.9,
                "error_tolerance": 0.1
            },
            optimization_rules={
                "allow_reordering": True,
                "allow_skipping": True,
                "allow_parallel": False,
                "max_changes_per_cycle": 3
            }
        )
    
    def apply_optimization(self, optimization: OptimizationDecision) -> bool:
        """Wendet eine Optimierung auf die Architektur an."""
        # Speichere aktuellen Zustand für Rollback
        self._create_rollback_point()
        
        try:
            if optimization.optimization_type == OptimizationType.MODULE_REORDER:
                success = self._apply_module_reorder(optimization)
            
            elif optimization.optimization_type == OptimizationType.MODULE_SKIP:
                success = self._apply_module_skip(optimization)
            
            elif optimization.optimization_type == OptimizationType.THRESHOLD_ADJUST:
                success = self._apply_threshold_adjustment(optimization)
            
            else:
                success = False
            
            if success:
                optimization.applied = True
                self.current_state.last_optimization = datetime.now()
                self._log_state_change(optimization)
            
            return success
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("ASO", f"Optimization failed: {str(e)}", "ERROR")
            return False
    
    def _apply_module_reorder(self, optimization: OptimizationDecision) -> bool:
        """Ändert die Modul-Reihenfolge."""
        params = optimization.parameters
        module = optimization.target_modules[0]
        
        if module in self.current_state.module_sequence:
            sequence = self.current_state.module_sequence.copy()
            current_pos = sequence.index(module)
            new_pos = params["new_position"]
            
            # Entferne und füge neu ein
            sequence.pop(current_pos)
            sequence.insert(new_pos, module)
            
            self.current_state.module_sequence = sequence
            return True
        
        return False
    
    def _apply_module_skip(self, optimization: OptimizationDecision) -> bool:
        """Fügt Skip-Regel für Modul hinzu."""
        module = optimization.target_modules[0]
        skip_rule = optimization.parameters["skip_rule"]
        
        if module not in self.current_state.module_configs:
            self.current_state.module_configs[module] = {}
        
        self.current_state.module_configs[module]["skip_conditions"] = skip_rule
        return True
    
    def _apply_threshold_adjustment(self, optimization: OptimizationDecision) -> bool:
        """Passt Performance-Schwellwerte an."""
        threshold_name = optimization.parameters["threshold"]
        new_value = optimization.parameters["new_value"]
        
        if threshold_name in self.current_state.performance_thresholds:
            self.current_state.performance_thresholds[threshold_name] = new_value
            return True
        
        return False
    
    def _create_rollback_point(self) -> None:
        """Erstellt einen Rollback-Punkt."""
        state_copy = copy.deepcopy(self.current_state)
        self.rollback_points.append((datetime.now(), state_copy))
        
        # Behalte nur die letzten 10 Rollback-Punkte
        if len(self.rollback_points) > 10:
            self.rollback_points.pop(0)
    
    def _log_state_change(self, optimization: OptimizationDecision) -> None:
        """Protokolliert Architektur-Änderungen."""
        self.state_history.append({
            "timestamp": optimization.timestamp,
            "optimization_id": optimization.decision_id,
            "type": optimization.optimization_type.value,
            "changes": optimization.parameters,
            "state_snapshot": copy.deepcopy(self.current_state)
        })
    
    def rollback_to_point(self, rollback_id: Optional[int] = -1) -> bool:
        """Macht Änderungen rückgängig."""
        if not self.rollback_points:
            return False
        
        try:
            _, previous_state = self.rollback_points[rollback_id]
            self.current_state = copy.deepcopy(previous_state)
            return True
        except (IndexError, KeyError):
            return False
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Gibt die Konfiguration eines Moduls zurück."""
        config = self.current_state.module_configs.get(module_name, {})
        
        # Füge globale Einstellungen hinzu
        config["active"] = module_name in self.current_state.active_modules
        config["position"] = (self.current_state.module_sequence.index(module_name) 
                            if module_name in self.current_state.module_sequence else -1)
        
        return config


class AdaptiveLearner:
    """Lernt aus Optimierungserfolgen und -misserfolgen."""
    
    def __init__(self):
        self.optimization_feedback: deque = deque(maxlen=200)
        self.pattern_success_rates: Dict[str, float] = {}
        self.learning_insights: List[Dict[str, Any]] = []
    
    def record_optimization_result(self, 
                                 optimization: OptimizationDecision,
                                 before_metrics: Dict[str, float],
                                 after_metrics: Dict[str, float]) -> None:
        """Zeichnet das Ergebnis einer Optimierung auf."""
        improvement = self._calculate_improvement(before_metrics, after_metrics)
        
        feedback = {
            "optimization_id": optimization.decision_id,
            "type": optimization.optimization_type.value,
            "timestamp": datetime.now(),
            "improvement": improvement,
            "success": improvement > 0.05,
            "before_metrics": before_metrics.copy(),
            "after_metrics": after_metrics.copy()
        }
        
        self.optimization_feedback.append(feedback)
        self._update_pattern_success_rates()
        self._generate_insights()
    
    def _calculate_improvement(self, before: Dict[str, float], after: Dict[str, float]) -> float:
        """Berechnet die Verbesserung durch eine Optimierung."""
        # Gewichtete Verbesserung über verschiedene Metriken
        improvements = []
        
        if "efficiency_score" in before and "efficiency_score" in after:
            eff_improvement = (after["efficiency_score"] - before["efficiency_score"]) / max(0.01, before["efficiency_score"])
            improvements.append(eff_improvement * 0.4)
        
        if "avg_decision_time" in before and "avg_decision_time" in after:
            # Zeit-Verbesserung (weniger ist besser)
            time_improvement = (before["avg_decision_time"] - after["avg_decision_time"]) / max(0.01, before["avg_decision_time"])
            improvements.append(time_improvement * 0.3)
        
        if "error_rate" in before and "error_rate" in after:
            # Fehlerrate-Verbesserung (weniger ist besser)
            error_improvement = (before["error_rate"] - after["error_rate"]) / max(0.01, before["error_rate"])
            improvements.append(error_improvement * 0.3)
        
        return sum(improvements) if improvements else 0.0
    
    def _update_pattern_success_rates(self) -> None:
        """Aktualisiert Erfolgsraten für Optimierungsmuster."""
        pattern_outcomes = defaultdict(list)
        
        for feedback in self.optimization_feedback:
            pattern = feedback["type"]
            pattern_outcomes[pattern].append(feedback["success"])
        
        for pattern, outcomes in pattern_outcomes.items():
            if len(outcomes) >= 5:
                self.pattern_success_rates[pattern] = sum(outcomes) / len(outcomes)
    
    def _generate_insights(self) -> None:
        """Generiert Lern-Erkenntnisse."""
        if len(self.optimization_feedback) < 10:
            return
        
        recent_feedback = list(self.optimization_feedback)[-20:]
        
        # Erfolgsrate
        success_rate = sum(f["success"] for f in recent_feedback) / len(recent_feedback)
        
        if success_rate < 0.3:
            self.learning_insights.append({
                "type": "low_success_rate",
                "insight": "Optimierungen zeigen geringe Erfolgsrate",
                "recommendation": "Konservativere Optimierungsstrategien verwenden",
                "confidence": 0.8,
                "timestamp": datetime.now()
            })
        
        # Muster-spezifische Erkenntnisse
        for pattern, success_rate in self.pattern_success_rates.items():
            if success_rate < 0.4 and pattern in [f["type"] for f in recent_feedback]:
                self.learning_insights.append({
                    "type": "ineffective_pattern",
                    "pattern": pattern,
                    "insight": f"{pattern} zeigt niedrige Erfolgsrate ({success_rate:.1%})",
                    "recommendation": f"Reduziere {pattern} Optimierungen",
                    "confidence": 0.7,
                    "timestamp": datetime.now()
                })
    
    def get_optimization_confidence(self, optimization_type: OptimizationType) -> float:
        """Gibt Konfidenz für einen Optimierungstyp zurück."""
        pattern = optimization_type.value
        
        if pattern in self.pattern_success_rates:
            base_confidence = self.pattern_success_rates[pattern]
        else:
            base_confidence = 0.5  # Neutral für unbekannte Muster
        
        # Adjustiere basierend auf aktuellen Trends
        recent = [f for f in list(self.optimization_feedback)[-10:] 
                 if f["type"] == pattern]
        
        if len(recent) >= 3:
            recent_success = sum(f["success"] for f in recent) / len(recent)
            # Gewichte aktuelle Erfahrungen stärker
            return base_confidence * 0.6 + recent_success * 0.4
        
        return base_confidence


# ============================================================================
# HAUPTKLASSE
# ============================================================================

class ArchitecturalSelfOptimizer:
    """
    Haupt-Koordinator für architektonische Selbstoptimierung.
    Orchestriert alle Komponenten für Meta-Meta-Learning.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Komponenten initialisieren
        self.performance_analyzer = PerformanceAnalyzer()
        self.optimization_engine = OptimizationEngine(config)
        self.architecture_manager = ArchitectureManager()
        self.adaptive_learner = AdaptiveLearner()
        
        # Zustand
        self.optimization_cycle = 0
        self.last_optimization = None
        self.optimization_cooldown = timedelta(seconds=self.config.get("cooldown_seconds", 300))
        
        # Statistiken
        self.stats = {
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "rolled_back": 0,
            "current_efficiency": 0.5
        }
    
    def analyze_and_optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hauptmethode: Analysiert Performance und optimiert Architektur.
        
        Args:
            context: Vollständiger Entscheidungskontext
            
        Returns:
            ASO-Ergebnis mit Optimierungsentscheidungen
        """
        # Performance-Daten sammeln
        self.performance_analyzer.update_from_context(context)
        
        # Bottlenecks identifizieren
        bottlenecks = self.performance_analyzer.identify_bottlenecks()
        
        # Aktuelle Architektur
        current_architecture = self.architecture_manager.current_state
        
        # Optimierungsmöglichkeiten generieren
        optimization_candidates = self.optimization_engine.generate_optimizations(
            self.performance_analyzer,
            current_architecture,
            bottlenecks
        )
        
        # Entscheide ob optimiert werden soll
        should_optimize, selected_optimizations = self._decide_optimization(
            optimization_candidates, context
        )
        
        # Führe Optimierungen durch
        applied_optimizations = []
        if should_optimize:
            applied_optimizations = self._apply_optimizations(selected_optimizations)
        
        # Lerne aus Ergebnissen (wenn genug Zeit vergangen ist)
        if self.last_optimization and applied_optimizations:
            self._learn_from_results()
        
        # Generiere Bericht
        return self._generate_report(
            bottlenecks,
            optimization_candidates,
            applied_optimizations,
            context
        )
    
    def _decide_optimization(self, 
                           candidates: List[OptimizationDecision],
                           context: Dict[str, Any]) -> Tuple[bool, List[OptimizationDecision]]:
        """Entscheidet ob und welche Optimierungen durchgeführt werden."""
        # Cooldown prüfen
        if self.last_optimization:
            time_since_last = datetime.now() - self.last_optimization
            if time_since_last < self.optimization_cooldown:
                return False, []
        
        # Mindest-Datenpunkte prüfen
        if self.performance_analyzer.system_metrics["total_decisions"] < 20:
            return False, []
        
        # Wähle beste Optimierungen basierend auf Konfidenz
        selected = []
        for candidate in candidates:
            confidence = self.adaptive_learner.get_optimization_confidence(
                candidate.optimization_type
            )
            
            # Adjustiere erwartete Verbesserung mit Konfidenz
            adjusted_score = candidate.expected_improvement * confidence * (1 - candidate.risk_level)
            
            if adjusted_score > 0.1:  # Mindest-Score
                selected.append(candidate)
        
        # Limitiere Anzahl gleichzeitiger Änderungen
        max_changes = self.architecture_manager.current_state.optimization_rules.get(
            "max_changes_per_cycle", 3
        )
        selected = selected[:max_changes]
        
        return len(selected) > 0, selected
    
    def _apply_optimizations(self, optimizations: List[OptimizationDecision]) -> List[OptimizationDecision]:
        """Wendet ausgewählte Optimierungen an."""
        applied = []
        
        # Metriken vor Optimierung
        before_metrics = {
            "efficiency_score": self.performance_analyzer.system_metrics["efficiency_score"],
            "avg_decision_time": self.performance_analyzer.system_metrics["avg_decision_time"],
            "error_rate": self.performance_analyzer.system_metrics["error_rate"]
        }
        
        for optimization in optimizations:
            success = self.architecture_manager.apply_optimization(optimization)
            
            if success:
                applied.append(optimization)
                self.stats["total_optimizations"] += 1
                
                if log_manager:
                    log_manager.log_event(
                        "ASO",
                        f"Applied {optimization.optimization_type.value}: {optimization.rationale}",
                        "INFO"
                    )
        
        # Markiere Zeitpunkt der Optimierung
        if applied:
            self.last_optimization = datetime.now()
            self.optimization_cycle += 1
            
            # Plane Erfolgs-Messung
            optimization.rollback_data = {
                "before_metrics": before_metrics,
                "applied_at": datetime.now()
            }
        
        return applied
    
    def _learn_from_results(self) -> None:
        """Lernt aus den Ergebnissen der letzten Optimierung."""
        if not hasattr(self, '_last_optimization_data'):
            return
        
        # Aktuelle Metriken
        after_metrics = {
            "efficiency_score": self.performance_analyzer.system_metrics["efficiency_score"],
            "avg_decision_time": self.performance_analyzer.system_metrics["avg_decision_time"],
            "error_rate": self.performance_analyzer.system_metrics["error_rate"]
        }
        
        # Vergleiche mit gespeicherten Metriken
        for optimization in self._last_optimization_data:
            if optimization.rollback_data and "before_metrics" in optimization.rollback_data:
                self.adaptive_learner.record_optimization_result(
                    optimization,
                    optimization.rollback_data["before_metrics"],
                    after_metrics
                )
                
                # Bewerte Erfolg
                improvement = self.adaptive_learner._calculate_improvement(
                    optimization.rollback_data["before_metrics"],
                    after_metrics
                )
                
                if improvement > 0.05:
                    self.stats["successful_optimizations"] += 1
    
    def _generate_report(self,
                        bottlenecks: List[Dict[str, Any]],
                        candidates: List[OptimizationDecision], 
                        applied: List[OptimizationDecision],
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert umfassenden ASO-Bericht."""
        # System-Status
        system_performance = self._evaluate_system_performance()
        
        # Empfehlungen
        recommendations = self._generate_recommendations(
            bottlenecks, candidates, system_performance
        )
        
        return {
            "cycle": self.optimization_cycle,
            "timestamp": datetime.now().isoformat(),
            "system_performance": system_performance,
            "bottlenecks": bottlenecks[:5],  # Top 5
            "optimization_candidates": [
                {
                    "id": opt.decision_id,
                    "type": opt.optimization_type.value,
                    "expected_improvement": opt.expected_improvement,
                    "risk": opt.risk_level,
                    "rationale": opt.rationale
                }
                for opt in candidates[:5]
            ],
            "applied_optimizations": [
                {
                    "id": opt.decision_id,
                    "type": opt.optimization_type.value,
                    "targets": opt.target_modules,
                    "parameters": opt.parameters
                }
                for opt in applied
            ],
            "current_architecture": {
                "module_sequence": self.architecture_manager.current_state.module_sequence,
                "active_modules": list(self.architecture_manager.current_state.active_modules),
                "performance_thresholds": self.architecture_manager.current_state.performance_thresholds
            },
            "learning_insights": self.adaptive_learner.learning_insights[-3:],
            "recommendations": recommendations,
            "stats": self.stats.copy()
        }
    
    def _evaluate_system_performance(self) -> Dict[str, Any]:
        """Bewertet die aktuelle System-Performance."""
        metrics = self.performance_analyzer.system_metrics
        
        # Performance-Level bestimmen
        efficiency = metrics["efficiency_score"]
        if efficiency >= 0.8:
            level = PerformanceLevel.EXCELLENT
        elif efficiency >= 0.65:
            level = PerformanceLevel.GOOD
        elif efficiency >= 0.5:
            level = PerformanceLevel.ACCEPTABLE
        elif efficiency >= 0.35:
            level = PerformanceLevel.POOR
        else:
            level = PerformanceLevel.CRITICAL
        
        self.stats["current_efficiency"] = efficiency
        
        return {
            "level": level.value,
            "efficiency_score": efficiency,
            "metrics": metrics,
            "trend": self._calculate_performance_trend()
        }
    
    def _calculate_performance_trend(self) -> str:
        """Berechnet Performance-Trend."""
        if len(self.adaptive_learner.optimization_feedback) < 5:
            return "insufficient_data"
        
        recent = list(self.adaptive_learner.optimization_feedback)[-5:]
        improvements = [f["improvement"] for f in recent]
        
        avg_improvement = statistics.mean(improvements)
        
        if avg_improvement > 0.05:
            return "improving"
        elif avg_improvement < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendations(self,
                                bottlenecks: List[Dict[str, Any]],
                                candidates: List[OptimizationDecision],
                                performance: Dict[str, Any]) -> List[str]:
        """Generiert Handlungsempfehlungen."""
        recommendations = []
        
        # Performance-basiert
        if performance["level"] == PerformanceLevel.CRITICAL.value:
            recommendations.append("⚠️ Kritische Performance - sofortige Intervention erforderlich")
            recommendations.append("Erwäge Rollback zur letzten stabilen Konfiguration")
        
        elif performance["level"] == PerformanceLevel.POOR.value:
            recommendations.append("Performance unterdurchschnittlich - Optimierung empfohlen")
        
        # Bottleneck-basiert
        if bottlenecks:
            worst = bottlenecks[0]
            recommendations.append(
                f"Hauptengpass: {worst['module']} ({worst['type'].value}) - {worst['impact']}"
            )
        
        # Optimierungs-basiert
        if not candidates:
            recommendations.append("Keine Optimierungsmöglichkeiten identifiziert - System läuft optimal")
        elif len(candidates) > 5:
            recommendations.append(f"{len(candidates)} Optimierungsmöglichkeiten verfügbar")
        
        # Trend-basiert
        trend = performance["trend"]
        if trend == "declining":
            recommendations.append("⚠️ Performance-Trend negativ - Ursachenanalyse empfohlen")
        elif trend == "improving":
            recommendations.append("✅ Positive Entwicklung - aktuelle Strategie beibehalten")
        
        return recommendations
    
    def rollback_optimizations(self, count: int = 1) -> bool:
        """Macht die letzten N Optimierungen rückgängig."""
        success = self.architecture_manager.rollback_to_point(-count)
        
        if success:
            self.stats["rolled_back"] += count
            if log_manager:
                log_manager.log_event("ASO", f"Rolled back {count} optimizations", "WARNING")
        
        return success


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale ASO-Instanz
_aso_instance: Optional[ArchitecturalSelfOptimizer] = None

def _get_aso_instance(config: Optional[Dict[str, Any]] = None) -> ArchitecturalSelfOptimizer:
    """Lazy-Loading der ASO-Instanz."""
    global _aso_instance
    if _aso_instance is None or config is not None:
        _aso_instance = ArchitecturalSelfOptimizer(config)
    return _aso_instance


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardisierte Modul-Schnittstelle für INTEGRA.
    
    Args:
        input_text: Text-Eingabe (wird von ASO nicht direkt genutzt)
        context: Entscheidungskontext mit Modul-Ergebnissen
        
    Returns:
        Standardisiertes Ergebnis-Dictionary
    """
    if context is None:
        context = {}
    
    try:
        # ASO-Konfiguration aus Context
        aso_config = context.get("config", {}).get("aso", {})
        
        # ASO-Instanz
        aso = _get_aso_instance(aso_config)
        
        # Führe Analyse und Optimierung durch
        aso_result = aso.analyze_and_optimize(context)
        
        # Speichere im Context für andere Module
        context["aso_result"] = aso_result
        
        # Log
        if log_manager:
            log_manager.log_event(
                "ASO",
                f"Cycle {aso_result['cycle']}: {len(aso_result['applied_optimizations'])} optimizations applied",
                "INFO"
            )
        
        return {
            "success": True,
            "result": aso_result,
            "module": "aso",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"ASO error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("ASO", error_msg, "ERROR")
        
        return {
            "success": False,
            "error": error_msg,
            "module": "aso",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die ASO-Funktionalität."""
    print("=== INTEGRA ASO v2.0 Demo ===")
    print("Architectural Self-Optimizer - Meta-Meta-Learning für Systemarchitektur\n")
    
    # Simuliere Entscheidungssequenz mit verschiedenen Modul-Ergebnissen
    test_contexts = [
        {
            "decision_id": "DEMO-001",
            "simple_ethics_result": {
                "success": True,
                "processing_time": 0.02,
                "score": 0.85
            },
            "etb_result": {
                "success": True,
                "processing_time": 0.05,
                "conflicts_detected": [{"principles": ["integrity", "nurturing"]}],
                "resolution": "balanced"
            },
            "pae_result": {
                "success": True,
                "processing_time": 0.03,
                "principle_chosen": "integrity"
            },
            "vdd_result": {
                "success": True,
                "processing_time": 0.08,
                "drift_detected": False
            },
            "meta_learner_result": {
                "success": True,
                "processing_time": 0.15,
                "profile_updates": {"integrity": 0.02}
            }
        }
    ]
    
    # Generiere weitere Test-Kontexte für Musterbildung
    for i in range(2, 25):
        ctx = {
            "decision_id": f"DEMO-{i:03d}",
            "simple_ethics_result": {
                "success": True,
                "processing_time": 0.02 + (i % 5) * 0.01,
                "score": 0.7 + (i % 4) * 0.05
            },
            "etb_result": {
                "success": i % 10 != 0,  # 10% Fehlerrate
                "processing_time": 0.05 + (i % 3) * 0.02,
                "conflicts_detected": [] if i % 3 == 0 else [{"principles": ["integrity", "nurturing"]}]
            },
            "vdd_result": {
                "success": True,
                "processing_time": 0.08 if i % 7 != 0 else 0.25,  # Gelegentlich langsam
                "drift_detected": i % 8 == 0
            }
        }
        
        # Einige Module werden übersprungen
        if i % 4 != 0:
            ctx["pae_result"] = {
                "success": True,
                "processing_time": 0.03
            }
        
        test_contexts.append(ctx)
    
    print("📊 Simuliere 25 Entscheidungen für ASO-Analyse...\n")
    
    # Führe ASO für jeden Kontext aus
    aso_results = []
    for i, context in enumerate(test_contexts):
        result = run_module("", context)
        
        if result["success"]:
            aso_results.append(result["result"])
            
            # Zeige wichtige Ereignisse
            if result["result"]["applied_optimizations"]:
                print(f"Entscheidung {i+1}: {len(result['result']['applied_optimizations'])} Optimierungen durchgeführt")
                for opt in result["result"]["applied_optimizations"]:
                    print(f"  - {opt['type']}: {opt['targets']}")
    
    # Zeige finalen Bericht
    if aso_results:
        final_result = aso_results[-1]
        
        print("\n" + "="*60)
        print("📈 FINALER ASO-BERICHT")
        print("="*60)
        
        print(f"\n🔧 System-Performance:")
        perf = final_result["system_performance"]
        print(f"  Level: {perf['level'].upper()}")
        print(f"  Effizienz: {perf['efficiency_score']:.2%}")
        print(f"  Trend: {perf['trend']}")
        
        print(f"\n⚠️ Top Bottlenecks:")
        for bottleneck in final_result["bottlenecks"][:3]:
            print(f"  - {bottleneck['module']}: {bottleneck['type']} (Severity: {bottleneck['severity']:.2f})")
            print(f"    Impact: {bottleneck['impact']}")
        
        print(f"\n🎯 Aktuelle Architektur:")
        arch = final_result["current_architecture"]
        print(f"  Module: {' → '.join(arch['module_sequence'][:5])}...")
        print(f"  Aktive Module: {len(arch['active_modules'])}")
        print(f"  Fast-Path Threshold: {arch['performance_thresholds'].get('fast_path_confidence', 'N/A')}")
        
        print(f"\n💡 Empfehlungen:")
        for rec in final_result["recommendations"][:3]:
            print(f"  • {rec}")
        
        print(f"\n📊 Statistiken:")
        stats = final_result["stats"]
        print(f"  Optimierungen gesamt: {stats['total_optimizations']}")
        print(f"  Erfolgreiche Optimierungen: {stats['successful_optimizations']}")
        print(f"  Rollbacks: {stats['rolled_back']}")
        
        if final_result["learning_insights"]:
            print(f"\n🧠 Lern-Erkenntnisse:")
            for insight in final_result["learning_insights"]:
                print(f"  - {insight['insight']}")
                print(f"    → {insight['recommendation']}")
    
    print("\n✅ ASO Demo abgeschlossen!")
    print("Das Modul optimiert kontinuierlich die Systemarchitektur für maximale Effizienz.")


if __name__ == "__main__":
    demo()