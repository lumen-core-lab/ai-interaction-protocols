# -*- coding: utf-8 -*-
"""
Modulname: asx.py
Beschreibung: ASO Explainability Module für INTEGRA Full - Erklärt Architektur-Optimierungen verständlich
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Integration mit ASO und anderen Modulen
- Globale Instanz mit Lazy-Loading
- Fokus auf ASO-Erklärungen (nicht allgemeine Entscheidungen)
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from collections import defaultdict
import json

# Standardisierte Imports
try:
    from integra.core import principles, profiles
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        log_manager = None
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
            log_manager = None
        except ImportError:
            print("❌ Fehler: Core Module nicht gefunden!")
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

class ExplanationLevel(Enum):
    """Detail-Level für Erklärungen."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    TECHNICAL = "technical"


class AudienceType(Enum):
    """Zielgruppen für Erklärungen."""
    GENERAL = "general"
    TECHNICAL = "technical"
    BUSINESS = "business"
    AUDIT = "audit"


# ============================================================================
# ASO EXPLAINABILITY MODULE
# ============================================================================

class ASOExplainabilityModule:
    """
    ASO Explainability (ASX) für INTEGRA.
    
    Generiert menschenverständliche Erklärungen für ASO-Optimierungen,
    Architektur-Änderungen und Performance-Analysen.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert das ASX-Modul.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        self.default_level = ExplanationLevel(
            self.config.get("default_level", "medium")
        )
        
        # Erklärungsvorlagen für ASO-spezifische Situationen
        self.templates = self._initialize_templates()
        
        # Statistiken
        self.stats = {
            "explanations_generated": 0,
            "by_level": defaultdict(int),
            "by_audience": defaultdict(int)
        }
    
    def _initialize_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialisiert Erklärungsvorlagen."""
        return {
            "optimization_types": {
                "module_reorder": {
                    "simple": "Die Reihenfolge der Module wurde angepasst, um schneller zu werden.",
                    "medium": "Module {modules} wurden neu angeordnet für {improvement}% bessere Performance.",
                    "technical": "Module-Sequenz optimiert: {old_seq} → {new_seq} (Expected gain: {improvement}%)"
                },
                "module_skip": {
                    "simple": "Einige Module werden bei einfachen Anfragen übersprungen.",
                    "medium": "Modul {module} wird unter Bedingung '{condition}' übersprungen (Zeitersparnis: {time_saved}s).",
                    "technical": "Skip-Rule implementiert: {module} wenn {condition} (Skip-Rate: {skip_rate}%, Value-Loss: {value_loss}%)"
                },
                "threshold_adjust": {
                    "simple": "Die Einstellungen wurden feinjustiert.",
                    "medium": "Schwellwert '{threshold}' wurde von {old} auf {new} angepasst.",
                    "technical": "Threshold adjustment: {threshold} = {new} (was: {old}, impact: {impact})"
                }
            },
            
            "bottleneck_explanations": {
                "time_bottleneck": {
                    "simple": "{module} braucht zu lange.",
                    "medium": "{module} benötigt durchschnittlich {time}s - das ist zu langsam.",
                    "technical": "{module}: avg={time}s, p95={p95}s, impact={impact}% of total time"
                },
                "error_rate_bottleneck": {
                    "simple": "{module} macht zu viele Fehler.",
                    "medium": "{module} hat eine Fehlerrate von {rate}% - das ist zu hoch.",
                    "technical": "{module}: error_rate={rate}%, failures={count}, MTBF={mtbf}s"
                },
                "quality_bottleneck": {
                    "simple": "{module} liefert wenig Nutzen.",
                    "medium": "{module} trägt nur {value} zum Ergebnis bei - das ist zu wenig.",
                    "technical": "{module}: value_score={value}, contribution={contrib}%, ROI={roi}"
                }
            },
            
            "performance_status": {
                "excellent": {
                    "simple": "Das System läuft hervorragend! ✨",
                    "medium": "System-Performance ist exzellent (Effizienz: {score}%).",
                    "technical": "Performance metrics: efficiency={score}%, latency={latency}ms, throughput={throughput}/s"
                },
                "critical": {
                    "simple": "Das System hat Probleme und braucht Hilfe! ⚠️",
                    "medium": "Kritische Performance-Probleme erkannt. Sofortige Optimierung erforderlich.",
                    "technical": "CRITICAL: efficiency={score}%, bottlenecks={count}, degradation={degradation}%/h"
                }
            },
            
            "strategy_explanations": {
                "conservative": {
                    "simple": "Vorsichtige Änderungen, um nichts kaputt zu machen.",
                    "medium": "Konservative Optimierungsstrategie wegen {reason}.",
                    "technical": "Conservative mode: risk_tolerance={risk}, max_change={change}%, rollback_enabled=true"
                },
                "aggressive": {
                    "simple": "Mutige Verbesserungen für bessere Leistung.",
                    "medium": "Aggressive Optimierung zur Behebung von {issues}.",
                    "technical": "Aggressive mode: performance_gain_target={target}%, risk_accepted={risk}%"
                }
            }
        }
    
    def explain_aso_decision(self, aso_result: Dict[str, Any], 
                           context: Dict[str, Any],
                           level: Optional[ExplanationLevel] = None,
                           audience: Optional[AudienceType] = None) -> Dict[str, Any]:
        """
        Erklärt ASO-Entscheidungen und Optimierungen.
        
        Args:
            aso_result: ASO-Ergebnis aus Context
            context: Vollständiger Context
            level: Gewünschtes Detail-Level
            audience: Zielgruppe
            
        Returns:
            Strukturierte Erklärungen
        """
        level = level or self.default_level
        audience = audience or AudienceType.GENERAL
        
        explanations = {
            "summary": self._generate_summary(aso_result, level, audience),
            "optimizations": self._explain_optimizations(aso_result, level),
            "bottlenecks": self._explain_bottlenecks(aso_result, level),
            "performance": self._explain_performance(aso_result, level),
            "recommendations": self._explain_recommendations(aso_result, level),
            "impact": self._explain_impact(aso_result, context, level),
            "visualization": self._prepare_visualizations(aso_result, level)
        }
        
        # Zusätzliche Erklärungen basierend auf Audience
        if audience == AudienceType.BUSINESS:
            explanations["business_impact"] = self._generate_business_impact(aso_result, context)
        elif audience == AudienceType.AUDIT:
            explanations["audit_trail"] = self._generate_audit_explanation(aso_result, context)
        elif audience == AudienceType.TECHNICAL:
            explanations["technical_details"] = self._generate_technical_details(aso_result)
        
        # Statistiken aktualisieren
        self.stats["explanations_generated"] += 1
        self.stats["by_level"][level.value] += 1
        self.stats["by_audience"][audience.value] += 1
        
        return explanations
    
    def _generate_summary(self, aso_result: Dict[str, Any], 
                         level: ExplanationLevel,
                         audience: AudienceType) -> str:
        """Generiert eine Zusammenfassung der ASO-Aktivitäten."""
        cycle = aso_result.get("cycle", 0)
        performance = aso_result.get("system_performance", {})
        applied = aso_result.get("applied_optimizations", [])
        
        if level == ExplanationLevel.SIMPLE:
            if not applied:
                return "Das System läuft gut, keine Änderungen nötig."
            else:
                return f"Das System wurde verbessert! {len(applied)} Anpassungen durchgeführt."
        
        elif level == ExplanationLevel.MEDIUM:
            perf_level = performance.get("level", "unknown")
            if perf_level == "excellent":
                status = "läuft optimal"
            elif perf_level == "critical":
                status = "hat kritische Probleme"
            else:
                status = f"zeigt {perf_level} Performance"
            
            summary = f"ASO Zyklus {cycle}: System {status}."
            if applied:
                summary += f" {len(applied)} Optimierungen angewendet."
            
            return summary
        
        else:  # TECHNICAL
            efficiency = performance.get("efficiency_score", 0)
            summary = f"ASO Cycle {cycle}: Performance={performance.get('level', 'N/A')} "
            summary += f"(efficiency={efficiency:.3f}), "
            summary += f"Optimizations={len(applied)}, "
            summary += f"Bottlenecks={len(aso_result.get('bottlenecks', []))}"
            
            return summary
    
    def _explain_optimizations(self, aso_result: Dict[str, Any], 
                              level: ExplanationLevel) -> List[Dict[str, str]]:
        """Erklärt durchgeführte Optimierungen."""
        applied = aso_result.get("applied_optimizations", [])
        explanations = []
        
        for opt in applied:
            opt_type = opt.get("type", "unknown")
            template = self.templates["optimization_types"].get(opt_type, {})
            
            if level == ExplanationLevel.SIMPLE:
                explanation = template.get("simple", "Eine Optimierung wurde durchgeführt.")
            elif level == ExplanationLevel.MEDIUM:
                explanation = self._fill_template(
                    template.get("medium", ""),
                    opt, aso_result
                )
            else:  # TECHNICAL
                explanation = self._fill_template(
                    template.get("technical", ""),
                    opt, aso_result
                )
            
            explanations.append({
                "optimization_id": opt.get("id", "unknown"),
                "type": opt_type,
                "explanation": explanation,
                "targets": opt.get("targets", [])
            })
        
        return explanations
    
    def _explain_bottlenecks(self, aso_result: Dict[str, Any], 
                           level: ExplanationLevel) -> List[Dict[str, str]]:
        """Erklärt identifizierte Bottlenecks."""
        bottlenecks = aso_result.get("bottlenecks", [])
        explanations = []
        
        for bottleneck in bottlenecks[:5]:  # Top 5
            bn_type = bottleneck.get("type", "unknown")
            template = self.templates["bottleneck_explanations"].get(bn_type, {})
            
            explanation = self._fill_template(
                template.get(level.value, "Performance-Problem erkannt."),
                bottleneck, aso_result
            )
            
            explanations.append({
                "module": bottleneck.get("module", "unknown"),
                "type": bn_type,
                "severity": bottleneck.get("severity", 0),
                "explanation": explanation,
                "impact": bottleneck.get("impact", "")
            })
        
        return explanations
    
    def _explain_performance(self, aso_result: Dict[str, Any], 
                           level: ExplanationLevel) -> Dict[str, str]:
        """Erklärt System-Performance."""
        performance = aso_result.get("system_performance", {})
        perf_level = performance.get("level", "unknown")
        
        template = self.templates["performance_status"].get(perf_level, {})
        
        explanation = self._fill_template(
            template.get(level.value, "Performance-Status unbekannt."),
            performance, aso_result
        )
        
        return {
            "level": perf_level,
            "explanation": explanation,
            "metrics": performance.get("metrics", {}) if level == ExplanationLevel.TECHNICAL else {},
            "trend": performance.get("trend", "unknown")
        }
    
    def _explain_recommendations(self, aso_result: Dict[str, Any], 
                               level: ExplanationLevel) -> List[str]:
        """Erklärt Empfehlungen verständlich."""
        recommendations = aso_result.get("recommendations", [])
        explained = []
        
        for rec in recommendations:
            if level == ExplanationLevel.SIMPLE:
                # Vereinfache technische Empfehlungen
                if "Rollback" in rec:
                    explained.append("Letzte Änderungen rückgängig machen.")
                elif "kritische Performance" in rec:
                    explained.append("Das System braucht dringend Hilfe!")
                else:
                    explained.append("Verbesserung empfohlen.")
            
            elif level == ExplanationLevel.MEDIUM:
                # Leicht technische Erklärung
                explained.append(rec)
            
            else:  # TECHNICAL
                # Volle technische Details
                explained.append(rec)
        
        return explained
    
    def _explain_impact(self, aso_result: Dict[str, Any], 
                       context: Dict[str, Any],
                       level: ExplanationLevel) -> Dict[str, Any]:
        """Erklärt die Auswirkungen der Optimierungen."""
        applied = aso_result.get("applied_optimizations", [])
        
        if not applied:
            return {
                "summary": "Keine Änderungen, keine Auswirkungen.",
                "details": []
            }
        
        # Berechne Gesamt-Impact
        total_improvement = sum(opt.get("expected_improvement", 0) for opt in applied)
        
        if level == ExplanationLevel.SIMPLE:
            if total_improvement > 0.2:
                summary = "Große Verbesserungen erwartet! 🚀"
            elif total_improvement > 0.1:
                summary = "Spürbare Verbesserungen erwartet."
            else:
                summary = "Kleine Verbesserungen erwartet."
        
        elif level == ExplanationLevel.MEDIUM:
            summary = f"Erwartete Gesamt-Verbesserung: {total_improvement*100:.0f}%"
        
        else:  # TECHNICAL
            summary = f"Cumulative expected improvement: {total_improvement:.3f} "
            summary += f"({len(applied)} optimizations)"
        
        # Detail-Impacts
        details = []
        if level != ExplanationLevel.SIMPLE:
            # Zeitersparnis
            time_saved = self._calculate_time_impact(applied, context)
            details.append({
                "metric": "Zeit",
                "impact": f"{time_saved:.1f}s gespart" if level == ExplanationLevel.MEDIUM 
                         else f"Time saved: {time_saved:.3f}s"
            })
            
            # Fehlerreduktion
            error_reduction = self._calculate_error_impact(applied, context)
            if error_reduction > 0:
                details.append({
                    "metric": "Fehler",
                    "impact": f"{error_reduction:.0f}% weniger Fehler" if level == ExplanationLevel.MEDIUM
                             else f"Error reduction: {error_reduction:.2f}%"
                })
        
        return {
            "summary": summary,
            "details": details
        }
    
    def _prepare_visualizations(self, aso_result: Dict[str, Any], 
                               level: ExplanationLevel) -> Dict[str, Any]:
        """Bereitet Daten für Visualisierungen vor."""
        viz = {}
        
        # Performance Timeline
        viz["performance_timeline"] = {
            "type": "line",
            "data": self._generate_performance_timeline(aso_result),
            "title": "Performance-Verlauf"
        }
        
        # Bottleneck Heatmap
        if level != ExplanationLevel.SIMPLE:
            viz["bottleneck_heatmap"] = {
                "type": "heatmap",
                "data": self._generate_bottleneck_heatmap(aso_result),
                "title": "Module-Engpässe"
            }
        
        # Optimization Impact
        if aso_result.get("applied_optimizations"):
            viz["optimization_impact"] = {
                "type": "bar",
                "data": self._generate_optimization_impact(aso_result),
                "title": "Optimierungs-Effekte"
            }
        
        return viz
    
    def _generate_business_impact(self, aso_result: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, str]:
        """Generiert Business-orientierte Erklärungen."""
        performance = aso_result.get("system_performance", {})
        efficiency = performance.get("efficiency_score", 0.5)
        
        # ROI-Berechnung (vereinfacht)
        time_saved = self._calculate_time_impact(
            aso_result.get("applied_optimizations", []), context
        )
        
        # Kosten-Nutzen
        if time_saved > 0:
            cost_benefit = f"Zeitersparnis von {time_saved:.1f}s pro Entscheidung"
        else:
            cost_benefit = "Keine messbare Zeitersparnis"
        
        # Risiko-Assessment
        if performance.get("level") == "critical":
            risk = "Hohes Risiko für Service-Ausfall"
        elif efficiency < 0.5:
            risk = "Mittleres Risiko für Performance-Probleme"
        else:
            risk = "Niedriges operatives Risiko"
        
        return {
            "efficiency": f"Operative Effizienz: {efficiency*100:.0f}%",
            "cost_benefit": cost_benefit,
            "risk_assessment": risk,
            "recommendation": self._generate_business_recommendation(aso_result)
        }
    
    def _generate_audit_explanation(self, aso_result: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Audit-konforme Erklärungen."""
        return {
            "cycle": aso_result.get("cycle", 0),
            "timestamp": datetime.now().isoformat(),
            "changes_made": len(aso_result.get("applied_optimizations", [])),
            "performance_before": context.get("performance_before", {}),
            "performance_after": aso_result.get("system_performance", {}),
            "bottlenecks_addressed": [
                {
                    "module": b["module"],
                    "type": b["type"],
                    "severity": b["severity"]
                }
                for b in aso_result.get("bottlenecks", [])[:5]
            ],
            "rollback_available": True,
            "approval_status": "automatic" if aso_result.get("applied_optimizations") else "none_needed"
        }
    
    def _generate_technical_details(self, aso_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert technische Details für Entwickler."""
        return {
            "architecture_state": aso_result.get("current_architecture", {}),
            "optimization_candidates": [
                {
                    "id": opt["id"],
                    "type": opt["type"],
                    "expected_improvement": opt["expected_improvement"],
                    "risk": opt["risk"],
                    "rationale": opt["rationale"]
                }
                for opt in aso_result.get("optimization_candidates", [])
            ],
            "performance_metrics": aso_result.get("system_performance", {}).get("metrics", {}),
            "learning_insights": aso_result.get("learning_insights", []),
            "statistics": aso_result.get("stats", {})
        }
    
    # Hilfsfunktionen
    
    def _fill_template(self, template: str, data: Dict[str, Any], 
                      context: Dict[str, Any]) -> str:
        """Füllt Template mit Daten."""
        try:
            # Sammle alle möglichen Variablen
            fill_data = {
                **data,
                **data.get("parameters", {}),
                "module": data.get("module", data.get("targets", ["unknown"])[0]),
                "modules": ", ".join(data.get("targets", [])),
                "time": data.get("metric", 0),
                "rate": data.get("metric", 0) * 100,
                "value": data.get("metric", 0),
                "score": context.get("efficiency_score", 0) * 100,
                **context
            }
            
            return template.format(**fill_data)
        except (KeyError, ValueError):
            return template
    
    def _calculate_time_impact(self, optimizations: List[Dict[str, Any]], 
                              context: Dict[str, Any]) -> float:
        """Berechnet Zeitersparnis durch Optimierungen."""
        time_saved = 0.0
        
        for opt in optimizations:
            if opt["type"] == "module_skip":
                # Geschätzte Zeit pro übersprungenes Modul
                time_saved += 0.5
            elif opt["type"] == "module_reorder":
                # Effizienzgewinn durch bessere Reihenfolge
                time_saved += 0.2
        
        return time_saved
    
    def _calculate_error_impact(self, optimizations: List[Dict[str, Any]], 
                               context: Dict[str, Any]) -> float:
        """Berechnet Fehlerreduktion durch Optimierungen."""
        error_reduction = 0.0
        
        for opt in optimizations:
            if opt["type"] == "threshold_adjust":
                # Bessere Schwellwerte = weniger Fehler
                error_reduction += 5.0
            elif "fallback" in opt.get("parameters", {}):
                # Fallback-Modi reduzieren Fehler
                error_reduction += 10.0
        
        return error_reduction
    
    def _generate_performance_timeline(self, aso_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generiert Daten für Performance-Timeline."""
        # Vereinfacht: Nur aktuelle Daten
        current = aso_result.get("system_performance", {})
        return [{
            "time": "now",
            "efficiency": current.get("efficiency_score", 0),
            "level": current.get("level", "unknown")
        }]
    
    def _generate_bottleneck_heatmap(self, aso_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generiert Daten für Bottleneck-Heatmap."""
        bottlenecks = aso_result.get("bottlenecks", [])
        return [
            {
                "module": b["module"],
                "severity": b["severity"],
                "type": b["type"]
            }
            for b in bottlenecks
        ]
    
    def _generate_optimization_impact(self, aso_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generiert Daten für Optimization-Impact."""
        return [
            {
                "optimization": opt["type"],
                "improvement": opt.get("expected_improvement", 0) * 100
            }
            for opt in aso_result.get("applied_optimizations", [])
        ]
    
    def _generate_business_recommendation(self, aso_result: Dict[str, Any]) -> str:
        """Generiert Business-Empfehlung."""
        performance = aso_result.get("system_performance", {})
        
        if performance.get("level") == "critical":
            return "Sofortmaßnahmen erforderlich zur Systemstabilisierung"
        elif performance.get("level") == "poor":
            return "Investition in Performance-Optimierung empfohlen"
        elif performance.get("level") == "excellent":
            return "System läuft optimal - Ressourcen können anders eingesetzt werden"
        else:
            return "Kontinuierliche Überwachung und schrittweise Optimierung"


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale ASX-Instanz
_asx_instance: Optional[ASOExplainabilityModule] = None

def _get_asx_instance(config: Optional[Dict[str, Any]] = None) -> ASOExplainabilityModule:
    """Lazy-Loading der ASX-Instanz."""
    global _asx_instance
    if _asx_instance is None or config is not None:
        _asx_instance = ASOExplainabilityModule(config)
    return _asx_instance


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardisierte Modul-Schnittstelle für INTEGRA.
    
    Args:
        input_text: Text-Eingabe (kann Erklärungsanfrage sein)
        context: Entscheidungskontext mit allen Modul-Ergebnissen
        
    Returns:
        Standardisiertes Ergebnis-Dictionary
    """
    if context is None:
        context = {}
    
    try:
        # ASX-Konfiguration aus Context
        asx_config = context.get("config", {}).get("asx", {})
        
        # ASX-Instanz
        asx = _get_asx_instance(asx_config)
        
        # Prüfe ob ASO-Ergebnis vorhanden
        aso_result = context.get("aso_result")
        if not aso_result:
            # Keine ASO-Daten zum Erklären
            return {
                "success": True,
                "result": {
                    "message": "Keine ASO-Optimierungen zum Erklären vorhanden.",
                    "explanations": {}
                },
                "module": "asx",
                "version": "2.0",
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
        
        # Bestimme gewünschtes Level und Audience
        level = ExplanationLevel.MEDIUM
        audience = AudienceType.GENERAL
        
        # Aus Input-Text extrahieren
        input_lower = input_text.lower()
        if any(word in input_lower for word in ["einfach", "simple", "leicht"]):
            level = ExplanationLevel.SIMPLE
        elif any(word in input_lower for word in ["technisch", "detail", "genau"]):
            level = ExplanationLevel.TECHNICAL
        
        if any(word in input_lower for word in ["business", "management", "roi"]):
            audience = AudienceType.BUSINESS
        elif any(word in input_lower for word in ["audit", "compliance", "prüfung"]):
            audience = AudienceType.AUDIT
        elif any(word in input_lower for word in ["entwickler", "technical", "code"]):
            audience = AudienceType.TECHNICAL
        
        # Generiere Erklärungen
        explanations = asx.explain_aso_decision(aso_result, context, level, audience)
        
        # Speichere im Context
        context["asx_result"] = {
            "explanations": explanations,
            "level": level.value,
            "audience": audience.value,
            "aso_cycle": aso_result.get("cycle", 0),
            "optimizations_explained": len(explanations.get("optimizations", []))
        }
        
        # Log
        if log_manager:
            log_manager.log_event(
                "ASX",
                f"ASO-Erklärungen generiert: {len(explanations.get('optimizations', []))} "
                f"Optimierungen erklärt (Level: {level.value}, Audience: {audience.value})",
                "INFO"
            )
        
        return {
            "success": True,
            "result": explanations,
            "module": "asx",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"ASX error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("ASX", error_msg, "ERROR")
        
        return {
            "success": False,
            "error": error_msg,
            "module": "asx",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die ASX-Funktionalität."""
    print("=== INTEGRA ASX v2.0 Demo ===")
    print("ASO Explainability Module - Erklärt Architektur-Optimierungen\n")
    
    # Simuliere verschiedene ASO-Ergebnisse
    test_scenarios = [
        {
            "name": "Einfache Optimierung",
            "aso_result": {
                "cycle": 1,
                "system_performance": {
                    "level": "good",
                    "efficiency_score": 0.75,
                    "metrics": {
                        "avg_decision_time": 1.2,
                        "error_rate": 0.05
                    }
                },
                "bottlenecks": [
                    {
                        "module": "dof",
                        "type": "time_bottleneck",
                        "severity": 0.6,
                        "metric": 2.5,
                        "impact": "2.5s durchschnittliche Ausführungszeit"
                    }
                ],
                "applied_optimizations": [
                    {
                        "id": "OPT-001",
                        "type": "module_skip",
                        "targets": ["dof"],
                        "expected_improvement": 0.3,
                        "parameters": {
                            "condition": "confidence > 0.8",
                            "skip_rate": 0.6,
                            "time_saved": 1.5
                        }
                    }
                ],
                "recommendations": ["Performance ist gut", "Module weiter beobachten"]
            }
        },
        {
            "name": "Kritische Performance mit mehreren Optimierungen",
            "aso_result": {
                "cycle": 5,
                "system_performance": {
                    "level": "critical",
                    "efficiency_score": 0.35,
                    "metrics": {
                        "avg_decision_time": 5.2,
                        "error_rate": 0.15
                    },
                    "trend": "declining"
                },
                "bottlenecks": [
                    {
                        "module": "meta_learner",
                        "type": "time_bottleneck",
                        "severity": 0.9,
                        "metric": 3.0,
                        "impact": "3.0s durchschnittliche Ausführungszeit"
                    },
                    {
                        "module": "etb",
                        "type": "error_rate_bottleneck",
                        "severity": 0.8,
                        "metric": 0.2,
                        "impact": "20% Fehlerrate"
                    }
                ],
                "applied_optimizations": [
                    {
                        "id": "OPT-002",
                        "type": "threshold_adjust",
                        "targets": ["decision_router"],
                        "expected_improvement": 0.2,
                        "parameters": {
                            "threshold": "fast_path_confidence",
                            "old": 0.85,
                            "new": 0.75
                        }
                    },
                    {
                        "id": "OPT-003",
                        "type": "module_reorder",
                        "targets": ["vdd", "meta_learner"],
                        "expected_improvement": 0.15,
                        "parameters": {
                            "old_seq": "etb,pae,vdd,meta_learner",
                            "new_seq": "etb,pae,meta_learner,vdd"
                        }
                    }
                ],
                "recommendations": [
                    "⚠️ Kritische Performance - sofortige Intervention erforderlich",
                    "Erwäge Rollback zur letzten stabilen Konfiguration"
                ],
                "learning_insights": [
                    {
                        "insight": "Meta-Learner verursacht Verzögerungen",
                        "recommendation": "Reduziere Lernrate"
                    }
                ]
            }
        }
    ]
    
    # Teste verschiedene Kombinationen
    test_configs = [
        ("Einfache Erklärung", ExplanationLevel.SIMPLE, AudienceType.GENERAL),
        ("Business-Bericht", ExplanationLevel.MEDIUM, AudienceType.BUSINESS),
        ("Technische Details", ExplanationLevel.TECHNICAL, AudienceType.TECHNICAL),
        ("Audit-Dokumentation", ExplanationLevel.MEDIUM, AudienceType.AUDIT)
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*70}")
        print(f"📋 Szenario: {scenario['name']}")
        print(f"{'='*70}")
        
        # Context mit ASO-Ergebnis
        context = {
            "aso_result": scenario["aso_result"],
            "profile": profiles.get_default_profile()
        }
        
        for config_name, level, audience in test_configs:
            print(f"\n🔍 {config_name} (Level: {level.value}, Audience: {audience.value})")
            print("-" * 60)
            
            # ASX-Instanz
            asx = _get_asx_instance()
            
            # Generiere Erklärungen
            explanations = asx.explain_aso_decision(
                scenario["aso_result"], context, level, audience
            )
            
            # Zeige Zusammenfassung
            print(f"\n📝 Zusammenfassung:")
            print(f"   {explanations['summary']}")
            
            # Zeige Optimierungen
            if explanations["optimizations"]:
                print(f"\n🔧 Optimierungen:")
                for opt in explanations["optimizations"]:
                    print(f"   - {opt['explanation']}")
            
            # Zeige Bottlenecks
            if explanations["bottlenecks"] and level != ExplanationLevel.SIMPLE:
                print(f"\n⚠️ Engpässe:")
                for bn in explanations["bottlenecks"][:2]:
                    print(f"   - {bn['explanation']}")
            
            # Zeige Performance
            perf = explanations["performance"]
            print(f"\n📊 Performance:")
            print(f"   {perf['explanation']}")
            
            # Zeige Empfehlungen
            if explanations["recommendations"]:
                print(f"\n💡 Empfehlungen:")
                for rec in explanations["recommendations"][:2]:
                    print(f"   - {rec}")
            
            # Zeige Impact
            if level != ExplanationLevel.SIMPLE:
                impact = explanations["impact"]
                print(f"\n📈 Erwartete Auswirkungen:")
                print(f"   {impact['summary']}")
                for detail in impact.get("details", []):
                    print(f"   - {detail['metric']}: {detail['impact']}")
            
            # Zeige Audience-spezifische Infos
            if audience == AudienceType.BUSINESS and "business_impact" in explanations:
                bi = explanations["business_impact"]
                print(f"\n💼 Business Impact:")
                for key, value in bi.items():
                    print(f"   - {key}: {value}")
            
            elif audience == AudienceType.AUDIT and "audit_trail" in explanations:
                audit = explanations["audit_trail"]
                print(f"\n📋 Audit Trail:")
                print(f"   - Zyklus: {audit['cycle']}")
                print(f"   - Änderungen: {audit['changes_made']}")
                print(f"   - Rollback: {'Ja' if audit['rollback_available'] else 'Nein'}")
    
    # Test: Integration mit run_module
    print(f"\n\n{'='*70}")
    print("🔗 Test: Integration über run_module")
    print(f"{'='*70}")
    
    # Simuliere Context mit ASO-Ergebnis
    test_context = {
        "aso_result": test_scenarios[1]["aso_result"],  # Kritisches Szenario
        "profile": profiles.get_default_profile()
    }
    
    # Verschiedene Anfragen
    test_requests = [
        "Erkläre die Optimierungen einfach",
        "Zeige technische Details der ASO-Änderungen",
        "Business-Bericht über die Performance",
        "Audit-Dokumentation der Änderungen"
    ]
    
    for request in test_requests:
        print(f"\n📨 Anfrage: '{request}'")
        result = run_module(request, test_context.copy())
        
        if result["success"]:
            explanations = result["result"]
            print(f"✅ Erklärungen generiert:")
            print(f"   Level: {result['context']['asx_result']['level']}")
            print(f"   Audience: {result['context']['asx_result']['audience']}")
            print(f"   Zusammenfassung: {explanations['summary'][:100]}...")
        else:
            print(f"❌ Fehler: {result['error']}")
    
    # Zeige Statistiken
    print(f"\n\n📊 ASX Statistiken:")
    asx = _get_asx_instance()
    stats = asx.stats
    print(f"   Erklärungen generiert: {stats['explanations_generated']}")
    print(f"   Nach Level: {dict(stats['by_level'])}")
    print(f"   Nach Audience: {dict(stats['by_audience'])}")
    
    print("\n✅ ASX Demo abgeschlossen!")
    print("Das Modul kann ASO-Optimierungen verständlich erklären.")


if __name__ == "__main__":
    demo()