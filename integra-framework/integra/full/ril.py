# -*- coding: utf-8 -*-
"""
Modulname: ril.py
Beschreibung: Realistic Implementation Loop für INTEGRA Full - Prüft praktische Umsetzbarkeit
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Integration mit anderen Modulen über Context
- Globale Instanz mit Lazy-Loading
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from enum import Enum
from collections import defaultdict
import statistics

# Standardisierte Imports
try:
    from integra.core import principles, profiles
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from utils import log_manager
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


class FeasibilityFactor(Enum):
    """Faktoren der Machbarkeitsanalyse."""
    TECHNICAL = "technical"
    SOCIAL = "social"
    ORGANIZATIONAL = "organizational"
    ECONOMIC = "economic"
    TEMPORAL = "temporal"
    LEGAL = "legal"
    ETHICAL = "ethical"


class BarrierSeverity(Enum):
    """Schweregrad von Implementierungsbarrieren."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ImplementationAnalyzer:
    """
    Analysiert die praktische Umsetzbarkeit von Entscheidungen.
    Berücksichtigt technische, soziale, organisatorische und weitere Faktoren.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert den Analyzer.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        
        # Konfiguration
        self.detail_level = self.config.get("detail_level", "medium")
        self.include_mitigation = self.config.get("include_mitigation", True)
        self.use_context_modules = self.config.get("use_context_modules", True)
        
        # Gewichtungen anpassbar machen
        default_weights = {
            FeasibilityFactor.TECHNICAL: 0.20,
            FeasibilityFactor.SOCIAL: 0.20,
            FeasibilityFactor.ORGANIZATIONAL: 0.15,
            FeasibilityFactor.ECONOMIC: 0.20,
            FeasibilityFactor.TEMPORAL: 0.10,
            FeasibilityFactor.LEGAL: 0.10,
            FeasibilityFactor.ETHICAL: 0.05
        }
        self.feasibility_weights = self.config.get("feasibility_weights", default_weights)
        
        # Tracking
        self.implementation_barriers = []
        self.success_factors = []
        self.mitigation_strategies = []
        
        # Historie für Lerneffekte
        self.analysis_history = []
        self.pattern_recognition = defaultdict(lambda: {"success": 0, "failure": 0})
        
        # Statistiken
        self.stats = {
            "total_analyses": 0,
            "average_feasibility": 0.0,
            "critical_factors_found": 0,
            "successful_mitigations": 0
        }
    
    def analyze_feasibility(self, decision_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bewertet die Umsetzbarkeit einer Entscheidung umfassend.
        
        Args:
            decision_text: Die zu prüfende Entscheidung/Aktion
            context: Vollständiger Kontext mit anderen Modul-Ergebnissen
            
        Returns:
            Dict mit detaillierter Machbarkeitsbewertung
        """
        self.stats["total_analyses"] += 1
        
        # Reset für neue Analyse
        self.implementation_barriers = []
        self.success_factors = []
        self.mitigation_strategies = []
        
        # Nutze Context-Module wenn verfügbar
        resl_result = context.get("resl_result", {})
        nga_result = context.get("nga_result", {})
        sbp_result = context.get("sbp_result", {})
        dof_result = context.get("dof_result", {})
        aso_result = context.get("aso_result", {})
        
        # Analysiere alle Faktoren
        factor_analyses = {}
        for factor in FeasibilityFactor:
            factor_analyses[factor] = self._analyze_factor(
                factor, decision_text, context,
                resl_result, nga_result, sbp_result, dof_result, aso_result
            )
        
        # Berechne gewichtete Gesamtmachbarkeit
        overall_feasibility = sum(
            analysis["score"] * self.feasibility_weights[factor]
            for factor, analysis in factor_analyses.items()
        )
        
        # Identifiziere kritische und erfolgreiche Faktoren
        critical_factors = []
        strong_factors = []
        
        for factor, analysis in factor_analyses.items():
            if analysis["score"] < 0.4:
                critical_factors.append({
                    "factor": factor.value,
                    "score": analysis["score"],
                    "main_barrier": analysis["barriers"][0] if analysis["barriers"] else "Unbekannt",
                    "weight": self.feasibility_weights[factor]
                })
                self.stats["critical_factors_found"] += 1
            elif analysis["score"] > 0.8:
                strong_factors.append({
                    "factor": factor.value,
                    "score": analysis["score"],
                    "strength": analysis["success_factors"][0] if analysis["success_factors"] else "Gut"
                })
        
        # Integration mit RESL - Anpassung bei hohem Risiko
        if resl_result and resl_result.get("risk_level", 0) > 0.7:
            overall_feasibility *= 0.9  # Reduziere Machbarkeit bei ethischen Risiken
            if log_manager:
                log_manager.log_event(
                    "RIL",
                    f"Machbarkeit reduziert wegen RESL-Risiko: {resl_result['risk_level']}",
                    "INFO"
                )
        
        # Generiere Implementierungsplan
        implementation_plan = self._generate_implementation_plan(
            factor_analyses, critical_factors, overall_feasibility
        )
        
        # Risikoanalyse
        risk_assessment = self._assess_implementation_risks(
            factor_analyses, self.implementation_barriers, context
        )
        
        # Erfolgsprognose
        success_prediction = self._predict_success(
            overall_feasibility, critical_factors, context
        )
        
        # Aktualisiere Statistiken
        self.stats["average_feasibility"] = (
            (self.stats["average_feasibility"] * (self.stats["total_analyses"] - 1) + overall_feasibility) /
            self.stats["total_analyses"]
        )
        
        # Speichere in Historie
        self.analysis_history.append({
            "decision": decision_text[:100],
            "feasibility": overall_feasibility,
            "critical_factors": len(critical_factors),
            "timestamp": datetime.now()
        })
        
        # Log wenn aktiviert
        if log_manager:
            log_manager.log_event(
                "RIL",
                f"Machbarkeitsanalyse abgeschlossen - Score: {overall_feasibility:.2f}, "
                f"Kritische Faktoren: {len(critical_factors)}",
                "INFO"
            )
        
        return {
            "overall_feasibility": overall_feasibility,
            "feasibility_status": self._get_feasibility_status(overall_feasibility),
            "factor_analyses": factor_analyses,
            "critical_factors": critical_factors,
            "strong_factors": strong_factors,
            "barriers": self.implementation_barriers,
            "success_factors": self.success_factors,
            "mitigation_strategies": self.mitigation_strategies if self.include_mitigation else [],
            "implementation_plan": implementation_plan,
            "risk_assessment": risk_assessment,
            "success_prediction": success_prediction,
            "recommendation": self._generate_recommendation(
                overall_feasibility, critical_factors, risk_assessment, context
            ),
            "context_integration": {
                "resl_considered": bool(resl_result),
                "nga_considered": bool(nga_result),
                "sbp_considered": bool(sbp_result),
                "dof_considered": bool(dof_result)
            }
        }
    
    def _analyze_factor(self, factor: FeasibilityFactor, decision: str, 
                       context: Dict[str, Any],
                       resl_result: Dict[str, Any],
                       nga_result: Dict[str, Any],
                       sbp_result: Dict[str, Any],
                       dof_result: Dict[str, Any],
                       aso_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert einen spezifischen Machbarkeitsfaktor mit Context-Integration."""
        
        if factor == FeasibilityFactor.TECHNICAL:
            return self._analyze_technical_feasibility(decision, context, aso_result)
        elif factor == FeasibilityFactor.SOCIAL:
            return self._analyze_social_acceptability(decision, context, sbp_result)
        elif factor == FeasibilityFactor.ORGANIZATIONAL:
            return self._analyze_organizational_fit(decision, context, aso_result)
        elif factor == FeasibilityFactor.ECONOMIC:
            return self._analyze_economic_viability(decision, context, dof_result)
        elif factor == FeasibilityFactor.TEMPORAL:
            return self._analyze_temporal_feasibility(decision, context, dof_result)
        elif factor == FeasibilityFactor.LEGAL:
            return self._analyze_legal_compliance(decision, context, nga_result)
        elif factor == FeasibilityFactor.ETHICAL:
            return self._analyze_ethical_alignment(decision, context, resl_result)
        
        return {"score": 0.5, "barriers": [], "success_factors": []}
    
    def _analyze_technical_feasibility(self, decision: str, context: Dict[str, Any],
                                     aso_result: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet technische Machbarkeit mit ASO-Integration."""
        score = 1.0
        barriers = []
        success_factors = []
        decision_lower = decision.lower()
        
        # Standard-Analyse
        if any(term in decision_lower for term in ["komplex", "schwierig", "aufwendig", "complex", "complicated"]):
            score -= 0.3
            barriers.append("Hohe technische Komplexität")
            self.implementation_barriers.append({
                "type": FeasibilityFactor.TECHNICAL.value,
                "severity": BarrierSeverity.HIGH,
                "description": "Hohe technische Komplexität erfordert Spezialwissen",
                "mitigation": "Technische Experten einbeziehen"
            })
        
        # ASO-Integration - Performance-Probleme
        if self.use_context_modules and aso_result:
            if aso_result.get("system_performance", {}).get("level") == "critical":
                score -= 0.25
                barriers.append("System-Performance kritisch")
                self.implementation_barriers.append({
                    "type": FeasibilityFactor.TECHNICAL.value,
                    "severity": BarrierSeverity.HIGH,
                    "description": "ASO meldet kritische System-Performance",
                    "mitigation": "Performance-Optimierung vor Implementation"
                })
        
        # Technologie-Verfügbarkeit
        if any(term in decision_lower for term in ["neu", "experimentell", "prototyp", "experimental", "innovative"]):
            score -= 0.25
            barriers.append("Unreife Technologie")
        
        # Positive Faktoren
        if any(term in decision_lower for term in ["standard", "bewährt", "etabliert", "proven", "tested"]):
            score += 0.1
            success_factors.append("Bewährte Technologie")
            self.success_factors.append({
                "type": FeasibilityFactor.TECHNICAL.value,
                "description": "Nutzung etablierter Technologien",
                "impact": "positive"
            })
        
        # Integration
        if "integration" in decision_lower or "schnittstell" in decision_lower:
            score -= 0.15
            barriers.append("Integrationskomplexität")
        
        return {
            "score": max(0.0, min(1.0, score)),
            "barriers": barriers,
            "success_factors": success_factors
        }
    
    def _analyze_social_acceptability(self, decision: str, context: Dict[str, Any],
                                    sbp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet soziale Akzeptanz mit SBP-Integration."""
        score = 1.0
        barriers = []
        success_factors = []
        decision_lower = decision.lower()
        
        # Standard-Analyse
        if any(term in decision_lower for term in ["umstritten", "kontrovers", "sensibel", "controversial"]):
            score -= 0.4
            barriers.append("Kontroverse Thematik")
        
        # SBP-Integration - Stakeholder-Reaktionen
        if self.use_context_modules and sbp_result:
            negative_reactions = sbp_result.get("negative_reaction_probability", 0)
            if negative_reactions > 0.7:
                score -= 0.35
                barriers.append(f"SBP: {negative_reactions:.0%} negative Reaktionen erwartet")
                self.implementation_barriers.append({
                    "type": FeasibilityFactor.SOCIAL.value,
                    "severity": BarrierSeverity.HIGH,
                    "description": "Hohe Wahrscheinlichkeit negativer Stakeholder-Reaktionen",
                    "mitigation": "Intensive Stakeholder-Kommunikation vorab"
                })
            
            # Positive Reaktionen
            positive_reactions = sbp_result.get("positive_reaction_probability", 0)
            if positive_reactions > 0.7:
                score += 0.15
                success_factors.append("SBP: Positive Stakeholder-Reaktionen erwartet")
        
        # Stakeholder-Widerstand
        if any(term in decision_lower for term in ["widerstand", "ablehnung", "protest", "opposition"]):
            score -= 0.35
            barriers.append("Erwarteter Widerstand")
        
        # Positive soziale Faktoren
        if any(term in decision_lower for term in ["konsens", "unterstützung", "gemeinsam", "support", "zusammen"]):
            score += 0.15
            success_factors.append("Breite Unterstützung")
        
        # Kulturelle Sensitivität
        if "kultur" in decision_lower or "tradition" in decision_lower:
            score -= 0.1
            barriers.append("Kulturelle Anpassung nötig")
        
        return {
            "score": max(0.0, min(1.0, score)),
            "barriers": barriers,
            "success_factors": success_factors
        }
    
    def _analyze_organizational_fit(self, decision: str, context: Dict[str, Any],
                                  aso_result: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet organisatorische Passung mit ASO-Integration."""
        score = 1.0
        barriers = []
        success_factors = []
        decision_lower = decision.lower()
        
        # Strukturelle Änderungen
        if any(term in decision_lower for term in ["umstruktur", "reorganis", "reform", "restructure"]):
            score -= 0.35
            barriers.append("Strukturelle Änderungen")
            self.implementation_barriers.append({
                "type": FeasibilityFactor.ORGANIZATIONAL.value,
                "severity": BarrierSeverity.HIGH,
                "description": "Tiefgreifende organisatorische Änderungen erforderlich",
                "mitigation": "Schrittweise Transformation mit Change Management"
            })
        
        # ASO-Integration - Architektur-Änderungen
        if self.use_context_modules and aso_result:
            if aso_result.get("architectural_changes_required", 0) > 3:
                score -= 0.2
                barriers.append("Umfangreiche Architektur-Anpassungen")
        
        # Prozessänderungen
        if "prozess" in decision_lower or "ablauf" in decision_lower:
            score -= 0.2
            barriers.append("Prozessanpassungen")
            if self.include_mitigation:
                self.mitigation_strategies.append({
                    "barrier": "Prozessänderungen",
                    "strategy": "Change Management Programm",
                    "timeline": "3-6 Monate",
                    "priority": "high"
                })
        
        # Kompetenzaufbau
        if any(term in decision_lower for term in ["schulung", "training", "weiterbildung", "qualifizierung"]):
            score -= 0.15
            barriers.append("Kompetenzaufbau nötig")
            if self.include_mitigation:
                self.mitigation_strategies.append({
                    "barrier": "Kompetenzlücken",
                    "strategy": "Strukturiertes Trainingsprogramm",
                    "timeline": "2-4 Monate",
                    "priority": "medium"
                })
        
        # Positive Faktoren
        if "bestehend" in decision_lower or "vorhanden" in decision_lower:
            score += 0.1
            success_factors.append("Nutzung bestehender Strukturen")
        
        return {
            "score": max(0.0, min(1.0, score)),
            "barriers": barriers,
            "success_factors": success_factors
        }
    
    def _analyze_economic_viability(self, decision: str, context: Dict[str, Any],
                                  dof_result: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet wirtschaftliche Machbarkeit mit DOF-Integration."""
        score = 1.0
        barriers = []
        success_factors = []
        decision_lower = decision.lower()
        
        # Kosten
        if any(term in decision_lower for term in ["teuer", "kostspielig", "expensive", "costly", "hochpreisig"]):
            score -= 0.4
            barriers.append("Hohe Kosten")
            self.implementation_barriers.append({
                "type": FeasibilityFactor.ECONOMIC.value,
                "severity": BarrierSeverity.CRITICAL,
                "description": "Erhebliche finanzielle Investition erforderlich",
                "mitigation": "Phasenweise Finanzierung oder Alternative suchen"
            })
        
        # DOF-Integration - Langfristige wirtschaftliche Folgen
        if self.use_context_modules and dof_result:
            economic_risk = dof_result.get("economic_risk_score", 0)
            if economic_risk > 0.6:
                score -= 0.25
                barriers.append(f"DOF: Langfristige wirtschaftliche Risiken ({economic_risk:.0%})")
        
        # Budget-Einschränkungen
        if any(term in decision_lower for term in ["budget", "begrenzt", "knapp", "limitiert"]):
            score -= 0.3
            barriers.append("Budgetbeschränkungen")
        
        # ROI-Unsicherheit
        if "unsicher" in decision_lower or "risiko" in decision_lower:
            score -= 0.2
            barriers.append("Unsicherer ROI")
            if self.include_mitigation:
                self.mitigation_strategies.append({
                    "barrier": "ROI-Unsicherheit",
                    "strategy": "Pilotprojekt zur Validierung",
                    "timeline": "3 Monate",
                    "priority": "high"
                })
        
        # Positive wirtschaftliche Faktoren
        if any(term in decision_lower for term in ["kostengünstig", "effizient", "einspar", "wirtschaftlich"]):
            score += 0.2
            success_factors.append("Kosteneffizienz")
            self.success_factors.append({
                "type": FeasibilityFactor.ECONOMIC.value,
                "description": "Positive Kosten-Nutzen-Relation",
                "impact": "positive"
            })
        
        return {
            "score": max(0.0, min(1.0, score)),
            "barriers": barriers,
            "success_factors": success_factors
        }
    
    def _analyze_temporal_feasibility(self, decision: str, context: Dict[str, Any],
                                    dof_result: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet zeitliche Machbarkeit mit DOF-Integration."""
        score = 1.0
        barriers = []
        success_factors = []
        decision_lower = decision.lower()
        
        # Zeitdruck
        if any(term in decision_lower for term in ["sofort", "dringend", "urgent", "asap", "unverzüglich"]):
            score -= 0.35
            barriers.append("Hoher Zeitdruck")
            self.implementation_barriers.append({
                "type": FeasibilityFactor.TEMPORAL.value,
                "severity": BarrierSeverity.HIGH,
                "description": "Unrealistischer Zeitrahmen",
                "mitigation": "Priorisierung kritischer Komponenten"
            })
        
        # DOF-Integration - Zeitkritische Folgen
        if self.use_context_modules and dof_result:
            if dof_result.get("time_critical_outcomes", 0) > 2:
                score -= 0.2
                barriers.append("DOF: Zeitkritische Langzeitfolgen")
        
        # Langfristige Bindung
        if any(term in decision_lower for term in ["langfristig", "jahre", "permanent", "dauerhaft"]):
            score -= 0.15
            barriers.append("Langfristige Verpflichtung")
        
        # Positive zeitliche Faktoren
        if any(term in decision_lower for term in ["flexibel", "anpassbar", "skalierbar", "agil"]):
            score += 0.1
            success_factors.append("Zeitliche Flexibilität")
        
        return {
            "score": max(0.0, min(1.0, score)),
            "barriers": barriers,
            "success_factors": success_factors
        }
    
    def _analyze_legal_compliance(self, decision: str, context: Dict[str, Any],
                                 nga_result: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet rechtliche Konformität mit NGA-Integration."""
        score = 1.0
        barriers = []
        success_factors = []
        decision_lower = decision.lower()
        
        # NGA-Integration - Compliance-Verletzungen
        if self.use_context_modules and nga_result:
            if nga_result.get("violations"):
                # Prüfe auf rechtliche Verletzungen
                legal_violations = [v for v in nga_result["violations"] 
                                  if v.get("framework") in ["gdpr", "legal"]]
                if legal_violations:
                    score -= 0.5
                    barriers.append(f"NGA: {len(legal_violations)} rechtliche Verletzungen")
                    self.implementation_barriers.append({
                        "type": FeasibilityFactor.LEGAL.value,
                        "severity": BarrierSeverity.CRITICAL,
                        "description": "NGA meldet rechtliche Compliance-Verletzungen",
                        "mitigation": "Rechtliche Prüfung und Anpassung zwingend erforderlich"
                    })
            
            # Compliance Score nutzen
            compliance_score = nga_result.get("overall_compliance", 1.0)
            if compliance_score < 0.5:
                score -= 0.3
                barriers.append(f"Niedrige Compliance: {compliance_score:.0%}")
        
        # Standard rechtliche Risiken
        if any(term in decision_lower for term in ["rechtlich", "gesetz", "regulier", "compliance"]):
            if any(neg in decision_lower for neg in ["unklar", "grauzone", "risiko"]):
                score -= 0.4
                barriers.append("Rechtliche Unsicherheit")
                self.implementation_barriers.append({
                    "type": FeasibilityFactor.LEGAL.value,
                    "severity": BarrierSeverity.CRITICAL,
                    "description": "Rechtliche Grauzone",
                    "mitigation": "Rechtsgutachten einholen"
                })
        
        # Positive rechtliche Faktoren
        if "konform" in decision_lower or "compliant" in decision_lower:
            score += 0.1
            success_factors.append("Rechtliche Konformität")
        
        return {
            "score": max(0.0, min(1.0, score)),
            "barriers": barriers,
            "success_factors": success_factors
        }
    
    def _analyze_ethical_alignment(self, decision: str, context: Dict[str, Any],
                                 resl_result: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet ethische Ausrichtung mit RESL-Integration."""
        score = 1.0
        barriers = []
        success_factors = []
        
        # RESL-Integration - Ethische Folgekonflikte
        if self.use_context_modules and resl_result:
            if resl_result.get("triggered_conflicts"):
                conflicts_count = len(resl_result["triggered_conflicts"])
                score -= 0.1 * conflicts_count
                barriers.append(f"RESL: {conflicts_count} ethische Folgekonflikte")
            
            # Risiko-Level
            risk_level = resl_result.get("risk_level", 0)
            if risk_level > 0.7:
                score -= 0.3
                barriers.append(f"RESL: Hohes ethisches Risiko ({risk_level:.0%})")
        
        # Ethische Scores aus Context
        ethics_result = context.get("simple_ethics_result", {})
        if ethics_result:
            overall_score = ethics_result.get("overall_score", 1.0)
            if overall_score < 0.5:
                score -= 0.3
                barriers.append("Niedrige ethische Bewertung")
            elif overall_score > 0.8:
                score += 0.1
                success_factors.append("Starke ethische Fundierung")
        
        # Ethische Verletzungen
        if ethics_result.get("violations"):
            score -= 0.2
            barriers.append("Ethische Verletzungen vorhanden")
        
        return {
            "score": max(0.0, min(1.0, score)),
            "barriers": barriers,
            "success_factors": success_factors
        }
    
    def _generate_implementation_plan(self, factor_analyses: Dict[FeasibilityFactor, Dict[str, Any]], 
                                    critical_factors: List[Dict[str, Any]], 
                                    overall_feasibility: float) -> Dict[str, Any]:
        """Generiert einen verbesserten Implementierungsplan."""
        
        # Priorisierung basierend auf Kritikalität und Gewichtung
        priority_actions = []
        
        for critical in sorted(critical_factors, key=lambda x: x["weight"], reverse=True):
            factor_name = critical["factor"]
            priority_actions.append({
                "factor": factor_name,
                "priority": "critical" if critical["score"] < 0.2 else "high",
                "action": f"Adressiere Barrieren in {factor_name}",
                "timeline": "Sofort" if critical["score"] < 0.2 else "1-2 Wochen",
                "impact": f"Verbessert Gesamtmachbarkeit um ~{critical['weight']:.0%}"
            })
        
        # Phasen-Plan basierend auf Machbarkeit
        phases = []
        
        if overall_feasibility < 0.4:
            phases = [
                {
                    "phase": 1,
                    "name": "Machbarkeitsstudie",
                    "duration": "1-2 Monate",
                    "focus": "Detaillierte Analyse kritischer Faktoren",
                    "milestones": ["Barrieren-Analyse", "Alternative Konzepte", "Stakeholder-Feedback"]
                },
                {
                    "phase": 2,
                    "name": "Konzeptüberarbeitung",
                    "duration": "2-3 Monate",
                    "focus": "Alternative Ansätze entwickeln",
                    "milestones": ["Neues Konzept", "Machbarkeitsvalidierung", "Freigabe"]
                }
            ]
        elif overall_feasibility < 0.7:
            phases = [
                {
                    "phase": 1,
                    "name": "Pilotprojekt",
                    "duration": "3-4 Monate",
                    "focus": "Validierung in kontrolliertem Umfeld",
                    "milestones": ["Pilot-Setup", "Durchführung", "Evaluation"]
                },
                {
                    "phase": 2,
                    "name": "Schrittweise Ausweitung",
                    "duration": "6-12 Monate",
                    "focus": "Graduelle Implementation",
                    "milestones": ["25% Rollout", "50% Rollout", "Vollständig"]
                }
            ]
        else:
            phases = [
                {
                    "phase": 1,
                    "name": "Vorbereitung",
                    "duration": "2-4 Wochen",
                    "focus": "Setup und Kommunikation",
                    "milestones": ["Kick-off", "Ressourcen", "Kommunikation"]
                },
                {
                    "phase": 2,
                    "name": "Direkte Implementation",
                    "duration": "1-3 Monate",
                    "focus": "Vollständige Umsetzung",
                    "milestones": ["Go-Live", "Stabilisierung", "Optimierung"]
                }
            ]
        
        return {
            "approach": "iterativ" if overall_feasibility < 0.7 else "direkt",
            "priority_actions": priority_actions,
            "phases": phases,
            "total_duration": self._estimate_duration(phases),
            "success_criteria": self._define_success_criteria(factor_analyses),
            "review_points": self._define_review_points(phases)
        }
    
    def _estimate_duration(self, phases: List[Dict[str, Any]]) -> str:
        """Schätzt die Gesamtdauer der Implementation."""
        if not phases:
            return "Unbestimmt"
        
        # Aggregiere Phasen-Dauern
        min_months = 0
        max_months = 0
        
        for phase in phases:
            duration = phase.get("duration", "")
            if "Woche" in duration:
                min_months += 0.25
                max_months += 1
            elif "Monat" in duration:
                # Extrahiere Zahlen
                parts = duration.split("-")
                if len(parts) == 2:
                    try:
                        min_val = int(parts[0])
                        max_val = int(parts[1].split()[0])
                        min_months += min_val
                        max_months += max_val
                    except:
                        min_months += 3
                        max_months += 6
        
        if min_months == max_months:
            return f"{min_months} Monate"
        else:
            return f"{min_months}-{max_months} Monate"
    
    def _define_success_criteria(self, factor_analyses: Dict[FeasibilityFactor, Dict[str, Any]]) -> List[str]:
        """Definiert messbare Erfolgskriterien."""
        criteria = []
        
        # Faktor-basierte Kriterien
        for factor, analysis in factor_analyses.items():
            if analysis["score"] < 0.5:
                criteria.append(f"{factor.value.capitalize()}: Score > 0.7 erreichen")
        
        # Standard-Kriterien
        criteria.extend([
            "Stakeholder-Akzeptanz > 80%",
            "Budget-Einhaltung ± 10%",
            "Zeitplan-Einhaltung ± 15%",
            "Keine kritischen Barrieren mehr vorhanden"
        ])
        
        return criteria[:6]  # Maximal 6 Kriterien
    
    def _define_review_points(self, phases: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Definiert Review-Punkte für Monitoring."""
        review_points = []
        
        for phase in phases:
            for milestone in phase.get("milestones", []):
                review_points.append({
                    "phase": phase["name"],
                    "milestone": milestone,
                    "type": "gate_review" if milestone == phase["milestones"][-1] else "progress_check"
                })
        
        return review_points
    
    def _assess_implementation_risks(self, factor_analyses: Dict[FeasibilityFactor, Dict[str, Any]], 
                                   barriers: List[Dict[str, Any]],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Bewertet Implementierungsrisiken umfassend."""
        
        # Risiko-Kategorien
        risk_categories = {
            "technical_risks": [],
            "organizational_risks": [],
            "financial_risks": [],
            "reputational_risks": [],
            "compliance_risks": []
        }
        
        # Analysiere Barrieren für Risiken
        for barrier in barriers:
            severity = barrier.get("severity", BarrierSeverity.MODERATE)
            barrier_type = barrier.get("type", "unknown")
            
            if barrier_type in ["technical", "temporal"]:
                risk_categories["technical_risks"].append({
                    "risk": barrier["description"],
                    "severity": severity.value if isinstance(severity, BarrierSeverity) else severity,
                    "mitigation": barrier.get("mitigation", "Keine definiert")
                })
            elif barrier_type == "organizational":
                risk_categories["organizational_risks"].append({
                    "risk": barrier["description"],
                    "severity": severity.value if isinstance(severity, BarrierSeverity) else severity,
                    "mitigation": barrier.get("mitigation", "Keine definiert")
                })
            elif barrier_type == "economic":
                risk_categories["financial_risks"].append({
                    "risk": barrier["description"],
                    "severity": severity.value if isinstance(severity, BarrierSeverity) else severity,
                    "mitigation": barrier.get("mitigation", "Keine definiert")
                })
            elif barrier_type == "social":
                risk_categories["reputational_risks"].append({
                    "risk": barrier["description"],
                    "severity": severity.value if isinstance(severity, BarrierSeverity) else severity,
                    "mitigation": barrier.get("mitigation", "Keine definiert")
                })
            elif barrier_type == "legal":
                risk_categories["compliance_risks"].append({
                    "risk": barrier["description"],
                    "severity": severity.value if isinstance(severity, BarrierSeverity) else severity,
                    "mitigation": barrier.get("mitigation", "Keine definiert")
                })
        
        # Gesamt-Risikobewertung
        total_risks = sum(len(risks) for risks in risk_categories.values())
        critical_risks = sum(
            1 for risks in risk_categories.values() 
            for risk in risks 
            if risk["severity"] in ["critical", "high"]
        )
        
        # Risiko-Level Berechnung
        risk_score = (critical_risks * 0.4 + total_risks * 0.1) / max(1, total_risks)
        
        risk_level = "niedrig"
        if risk_score > 0.6 or critical_risks >= 3:
            risk_level = "hoch"
        elif risk_score > 0.3 or critical_risks >= 1:
            risk_level = "mittel"
        
        return {
            "overall_risk_level": risk_level,
            "risk_score": min(1.0, risk_score),
            "risk_categories": risk_categories,
            "total_risks": total_risks,
            "critical_risks": critical_risks,
            "risk_mitigation_priority": self._prioritize_risk_mitigation(risk_categories),
            "contingency_required": risk_level in ["hoch", "mittel"]
        }
    
    def _prioritize_risk_mitigation(self, risk_categories: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
        """Priorisiert Risiko-Mitigationsmaßnahmen."""
        priorities = []
        
        # Sortiere alle Risiken nach Schweregrad
        all_risks = []
        for category, risks in risk_categories.items():
            for risk in risks:
                all_risks.append({
                    "category": category,
                    "risk": risk["risk"],
                    "severity": risk["severity"],
                    "mitigation": risk["mitigation"]
                })
        
        # Sortiere nach Schweregrad
        severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
        sorted_risks = sorted(all_risks, key=lambda x: severity_order.get(x["severity"], 4))
        
        # Erstelle Prioritätenliste
        for risk in sorted_risks[:5]:  # Top 5
            priority = "KRITISCH" if risk["severity"] == "critical" else "HOCH" if risk["severity"] == "high" else "MITTEL"
            priorities.append({
                "priority": priority,
                "mitigation": risk["mitigation"],
                "category": risk["category"],
                "risk": risk["risk"]
            })
        
        return priorities
    
    def _predict_success(self, overall_feasibility: float, 
                        critical_factors: List[Dict[str, Any]], 
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Prognostiziert Erfolgschancen mit verbesserter Analyse."""
        
        base_success_rate = overall_feasibility
        
        # Modifikatoren
        modifiers = {
            "critical_factor_penalty": -0.1 * len(critical_factors),
            "experience_bonus": 0.0,
            "context_adjustment": 0.0,
            "module_integration_bonus": 0.0
        }
        
        # Erfahrungsbonus aus Historie
        if len(self.analysis_history) >= 5:
            recent_feasibilities = [h["feasibility"] for h in self.analysis_history[-5:]]
            avg_feasibility = statistics.mean(recent_feasibilities)
            if avg_feasibility > 0.7:
                modifiers["experience_bonus"] = 0.05
                self.stats["successful_mitigations"] += 1
        
        # Kontext-Anpassung
        if context.get("previous_success", False):
            modifiers["context_adjustment"] = 0.1
        elif context.get("previous_failure", False):
            modifiers["context_adjustment"] = -0.1
        
        # Bonus für gute Modul-Integration
        modules_used = sum(1 for key in ["resl_result", "nga_result", "sbp_result", "dof_result"] 
                          if key in context and context[key])
        if modules_used >= 3:
            modifiers["module_integration_bonus"] = 0.05
        
        # Finale Erfolgsrate
        success_rate = base_success_rate + sum(modifiers.values())
        success_rate = max(0.1, min(0.95, success_rate))
        
        # Kategorisierung
        if success_rate >= 0.8:
            likelihood = "sehr_hoch"
            confidence = "Hohe Erfolgswahrscheinlichkeit bei sorgfältiger Umsetzung"
        elif success_rate >= 0.6:
            likelihood = "hoch"
            confidence = "Gute Erfolgsaussichten mit strukturierter Planung"
        elif success_rate >= 0.4:
            likelihood = "moderat"
            confidence = "Erfolg möglich, aber signifikante Herausforderungen"
        else:
            likelihood = "niedrig"
            confidence = "Erfolg unwahrscheinlich ohne grundlegende Änderungen"
        
        return {
            "success_rate": round(success_rate, 2),
            "likelihood": likelihood,
            "confidence_statement": confidence,
            "modifiers": modifiers,
            "key_success_factors": self._identify_key_success_factors(overall_feasibility, critical_factors),
            "risk_adjusted_rate": round(success_rate * 0.8, 2)  # Konservative Schätzung
        }
    
    def _identify_key_success_factors(self, feasibility: float, 
                                     critical_factors: List[Dict[str, Any]]) -> List[str]:
        """Identifiziert Schlüsselfaktoren für Erfolg."""
        factors = []
        
        if feasibility < 0.5:
            factors.extend([
                "Grundlegende Konzeptüberarbeitung erforderlich",
                "Starke Führungsunterstützung sicherstellen",
                "Ausreichende Ressourcenallokation gewährleisten",
                "Stakeholder frühzeitig einbinden"
            ])
        else:
            factors.extend([
                "Klare Kommunikationsstrategie",
                "Kontinuierliche Stakeholder-Einbindung",
                "Iterative Verbesserung und Anpassung",
                "Robustes Projektmanagement"
            ])
        
        # Spezifisch für kritische Faktoren
        if critical_factors:
            most_critical = min(critical_factors, key=lambda x: x["score"])
            factors.append(f"Fokus auf {most_critical['factor']}-Verbesserung")
        
        # Aus Success Factors
        if self.success_factors:
            factors.append(f"Nutze Stärke: {self.success_factors[0]['description']}")
        
        return factors[:5]
    
    def _generate_recommendation(self, overall_score: float, 
                               critical_factors: List[Dict[str, Any]],
                               risk_assessment: Dict[str, Any],
                               context: Dict[str, Any]) -> str:
        """Generiert eine kontextbewusste Handlungsempfehlung."""
        
        risk_level = risk_assessment["overall_risk_level"]
        
        # Berücksichtige RESL-Warnung
        resl_warning = context.get("resl_result", {}).get("warning")
        
        if overall_score >= 0.8 and risk_level == "niedrig":
            if resl_warning:
                return "Entscheidung ist technisch gut umsetzbar, aber ethische Folgekonflikte beachten. Ethik-Review vor Implementation empfohlen."
            return "Entscheidung ist sehr gut umsetzbar. Direkte Implementation mit Standard-Projektmanagement empfohlen."
        
        elif overall_score >= 0.6:
            if risk_level == "hoch":
                return "Entscheidung ist machbar, aber mit erheblichen Risiken. Umfassendes Risikomanagement und phasenweise Implementation dringend empfohlen."
            else:
                return "Entscheidung ist mit moderatem Aufwand umsetzbar. Strukturierte Projektplanung mit Fokus auf kritische Faktoren empfohlen."
        
        elif overall_score >= 0.4:
            if len(critical_factors) >= 3:
                factors_str = ", ".join([f["factor"] for f in critical_factors[:3]])
                return f"Erhebliche Herausforderungen in: {factors_str}. Pilotprojekt oder alternative Ansätze dringend empfohlen."
            else:
                return "Signifikante Implementierungshürden. Konzeptüberarbeitung und Machbarkeitsstudie empfohlen."
        
        else:
            if risk_level == "hoch":
                return "Entscheidung ist hochriskant und kaum umsetzbar. Grundlegende Neukonzeption oder Verzicht dringend empfohlen."
            else:
                return "Entscheidung ist in aktueller Form nicht realistisch. Alternative Lösungswege müssen entwickelt werden."
    
    def _get_feasibility_status(self, score: float) -> str:
        """Kategorisiert Machbarkeits-Score."""
        if score >= 0.8:
            return "sehr_gut_machbar"
        elif score >= 0.6:
            return "gut_machbar"
        elif score >= 0.4:
            return "bedingt_machbar"
        elif score >= 0.2:
            return "schwer_machbar"
        else:
            return "praktisch_unmöglich"
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über bisherige Analysen zurück."""
        return {
            "total_analyses": self.stats["total_analyses"],
            "average_feasibility": self.stats["average_feasibility"],
            "critical_factors_found": self.stats["critical_factors_found"],
            "successful_mitigations": self.stats["successful_mitigations"],
            "most_common_barriers": self._get_most_common_barriers()
        }
    
    def _get_most_common_barriers(self) -> List[Tuple[str, int]]:
        """Identifiziert häufigste Barrieren."""
        barrier_counts = defaultdict(int)
        
        for analysis in self.analysis_history:
            # Diese Information müsste in der Historie gespeichert werden
            # Vereinfachte Version
            if analysis["feasibility"] < 0.5:
                barrier_counts["low_feasibility"] += 1
            if analysis["critical_factors"] > 2:
                barrier_counts["multiple_critical_factors"] += 1
        
        return sorted(barrier_counts.items(), key=lambda x: x[1], reverse=True)[:5]


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale Analyzer-Instanz
_analyzer_instance: Optional[ImplementationAnalyzer] = None

def _get_analyzer_instance(config: Optional[Dict[str, Any]] = None) -> ImplementationAnalyzer:
    """Lazy-Loading der Analyzer-Instanz."""
    global _analyzer_instance
    if _analyzer_instance is None or config is not None:
        _analyzer_instance = ImplementationAnalyzer(config)
    return _analyzer_instance


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardisierte Modul-Schnittstelle für INTEGRA.
    
    Args:
        input_text: Text-Eingabe zur Analyse
        context: Entscheidungskontext mit allen Modul-Ergebnissen
        
    Returns:
        Standardisiertes Ergebnis-Dictionary
    """
    if context is None:
        context = {}
    
    try:
        # RIL-Konfiguration aus Context
        ril_config = context.get("config", {}).get("ril", {})
        
        # Analyzer-Instanz
        analyzer = _get_analyzer_instance(ril_config)
        
        # Profil aus Context
        profile = context.get("profile", profiles.get_default_profile())
        
        # Log Start
        if log_manager:
            log_manager.log_event(
                "RIL",
                f"Starte Machbarkeitsanalyse (detail={analyzer.detail_level})",
                "INFO"
            )
        
        # Text vorbereiten - kombiniere Input und Response
        decision_text = input_text
        if context.get("response"):
            # Analysiere die geplante Aktion/Antwort
            decision_text = f"{input_text} -> {context['response']}"
        elif context.get("decision"):
            # Fallback auf explizite Entscheidung
            decision_text = context["decision"]
        
        # Führe Analyse durch
        analysis_result = analyzer.analyze_feasibility(decision_text, context)
        
        # Erstelle RIL-Ergebnis
        ril_result = {
            "overall_feasibility": analysis_result["overall_feasibility"],
            "feasibility_status": analysis_result["feasibility_status"],
            "feasible": analysis_result["overall_feasibility"] >= 0.5,
            "critical_factors": analysis_result["critical_factors"],
            "strong_factors": analysis_result["strong_factors"],
            "barriers_count": len(analysis_result["barriers"]),
            "implementation_plan": analysis_result["implementation_plan"],
            "risk_assessment": analysis_result["risk_assessment"],
            "success_prediction": analysis_result["success_prediction"],
            "recommendation": analysis_result["recommendation"],
            "context_integration": analysis_result["context_integration"]
        }
        
        # Detail-Level beachten
        if analyzer.detail_level == "high":
            ril_result.update({
                "factor_analyses": analysis_result["factor_analyses"],
                "barriers": analysis_result["barriers"],
                "success_factors": analysis_result["success_factors"],
                "mitigation_strategies": analysis_result["mitigation_strategies"]
            })
        elif analyzer.detail_level == "medium":
            ril_result.update({
                "barriers": [b["description"] for b in analysis_result["barriers"][:5]],
                "success_factors": [s["description"] for s in analysis_result["success_factors"][:3]],
                "mitigation_count": len(analysis_result["mitigation_strategies"])
            })
        
        # Speichere im Context
        context["ril_result"] = ril_result
        
        # Log Ergebnis
        if log_manager:
            log_manager.log_event(
                "RIL",
                f"Analyse abgeschlossen - Machbarkeit: {ril_result['overall_feasibility']:.2%}, "
                f"Status: {ril_result['feasibility_status']}, "
                f"Kritische Faktoren: {len(ril_result['critical_factors'])}",
                "INFO"
            )
            
            if ril_result["overall_feasibility"] < 0.4:
                log_manager.log_event(
                    "RIL",
                    f"WARNUNG: Niedrige Machbarkeit - {ril_result['recommendation']}",
                    "WARNING"
                )
        
        return {
            "success": True,
            "result": ril_result,
            "module": "ril",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"RIL error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("RIL", error_msg, "ERROR")
        
        # Fehler-Fallback
        context["ril_result"] = {
            "error": True,
            "error_message": error_msg,
            "overall_feasibility": 0.5,
            "feasibility_status": "unknown",
            "feasible": False,
            "recommendation": "Analyse fehlgeschlagen - manuelle Prüfung erforderlich"
        }
        
        return {
            "success": False,
            "error": error_msg,
            "module": "ril",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die Verwendung des RIL-Moduls."""
    print("=== INTEGRA RIL (Realistic Implementation Loop) Demo v2.0 ===")
    print("Standardisierte Baukasten-Integration\n")
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test-Szenarien
    test_scenarios = [
        {
            "name": "Einfache Standardlösung",
            "text": "Führe bewährte Standardprozesse ein",
            "context": {
                "profile": test_profile.copy(),
                "response": "Ich implementiere bewährte Standardprozesse zur effizienten Dokumentation"
            }
        },
        {
            "name": "Komplexe Innovation mit Context-Integration",
            "text": "Entwickle innovative KI-Lösung",
            "context": {
                "profile": test_profile.copy(),
                "response": "Komplexe experimentelle KI-Lösung sofort mit knappem Budget implementieren",
                "resl_result": {
                    "risk_level": 0.8,
                    "triggered_conflicts": ["integrity", "governance"],
                    "warning": "Hohe Wahrscheinlichkeit ethischer Folgekonflikte"
                },
                "nga_result": {
                    "overall_compliance": 0.4,
                    "violations": [{"framework": "gdpr", "severity": "high"}]
                },
                "aso_result": {
                    "system_performance": {"level": "critical"},
                    "architectural_changes_required": 5
                }
            }
        },
        {
            "name": "Organisatorische Transformation",
            "text": "Plane Umstrukturierung",
            "context": {
                "profile": test_profile.copy(),
                "response": "Umfassende Umstrukturierung mit Prozessänderungen trotz erwartetem Mitarbeiterwiderstand",
                "sbp_result": {
                    "negative_reaction_probability": 0.8,
                    "positive_reaction_probability": 0.2,
                    "key_stakeholders": ["Mitarbeiter", "Management"]
                }
            }
        },
        {
            "name": "Rechtlich sensibel mit NGA",
            "text": "Neue Datenverarbeitung einführen",
            "context": {
                "profile": test_profile.copy(),
                "response": "Innovative Lösung in rechtlicher Grauzone mit unsicherem ROI langfristig umsetzen",
                "nga_result": {
                    "overall_compliance": 0.3,
                    "violations": [
                        {"framework": "gdpr", "severity": "critical", "description": "Keine Rechtsgrundlage"},
                        {"framework": "legal", "severity": "high", "description": "Rechtliche Grauzone"}
                    ]
                },
                "dof_result": {
                    "economic_risk_score": 0.7,
                    "time_critical_outcomes": 3,
                    "highest_risk": 0.8
                }
            }
        },
        {
            "name": "Test verschiedene Detail-Level",
            "text": "Standardprojekt durchführen",
            "context": {
                "profile": test_profile.copy(),
                "config": {
                    "ril": {
                        "detail_level": "low",
                        "include_mitigation": False
                    }
                }
            }
        },
        {
            "name": "Hohe Machbarkeit mit allen Modulen",
            "text": "Implementiere kostengünstige Standardlösung",
            "context": {
                "profile": test_profile.copy(),
                "response": "Bewährte, kostengünstige Lösung mit breiter Unterstützung flexibel umsetzen",
                "simple_ethics_result": {
                    "overall_score": 0.9,
                    "violations": []
                },
                "resl_result": {
                    "risk_level": 0.2,
                    "triggered_conflicts": []
                },
                "nga_result": {
                    "overall_compliance": 0.95,
                    "violations": []
                },
                "sbp_result": {
                    "positive_reaction_probability": 0.85,
                    "negative_reaction_probability": 0.15
                },
                "config": {
                    "ril": {
                        "detail_level": "high"
                    }
                }
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*70}")
        print(f"Test {i+1}: {scenario['name']}")
        print(f"Eingabe: {scenario['text']}")
        if scenario["context"].get("response"):
            print(f"Geplante Aktion: {scenario['context']['response'][:60]}...")
        
        # Führe RIL durch
        result = run_module(scenario["text"], scenario["context"])
        
        if result["success"]:
            ril_result = result["result"]
            
            print(f"\n📊 Machbarkeitsanalyse:")
            print(f"  Gesamt-Machbarkeit: {ril_result['overall_feasibility']:.1%}")
            print(f"  Status: {ril_result['feasibility_status']}")
            print(f"  Machbar: {'✅' if ril_result['feasible'] else '❌'}")
            
            if ril_result["critical_factors"]:
                print(f"\n❌ Kritische Faktoren ({len(ril_result['critical_factors'])}):")
                for factor in ril_result["critical_factors"]:
                    print(f"  - {factor['factor']}: {factor['score']:.2f} ({factor['main_barrier']})")
            
            if ril_result.get("strong_factors"):
                print(f"\n✅ Stärken ({len(ril_result['strong_factors'])}):")
                for factor in ril_result["strong_factors"][:3]:
                    print(f"  - {factor['factor']}: {factor['strength']}")
            
            # Risk Assessment
            risk = ril_result["risk_assessment"]
            print(f"\n⚠️ Risikobewertung:")
            print(f"  Gesamt-Risiko: {risk['overall_risk_level']}")
            print(f"  Kritische Risiken: {risk.get('critical_risks', 0)}")
            
            # Success Prediction
            success = ril_result["success_prediction"]
            print(f"\n🎯 Erfolgsprognose:")
            print(f"  Erfolgsrate: {success['success_rate']:.0%}")
            print(f"  Wahrscheinlichkeit: {success['likelihood']}")
            
            # Implementation Plan
            plan = ril_result["implementation_plan"]
            print(f"\n📋 Implementierungsplan:")
            print(f"  Ansatz: {plan['approach']}")
            print(f"  Geschätzte Dauer: {plan['total_duration']}")
            print(f"  Phasen: {len(plan['phases'])}")
            
            # Context Integration
            integration = ril_result["context_integration"]
            print(f"\n🔗 Context-Integration:")
            integrations = [k.replace("_considered", "") for k, v in integration.items() if v]
            if integrations:
                print(f"  Genutzte Module: {', '.join(integrations)}")
            
            print(f"\n💡 Empfehlung:")
            print(f"  {ril_result['recommendation']}")
            
            # Bei hohem Detail-Level
            if "factor_analyses" in ril_result:
                print(f"\n📈 Detaillierte Faktor-Analyse:")
                for factor, analysis in ril_result["factor_analyses"].items():
                    score = analysis["score"]
                    status = "✅" if score >= 0.7 else "⚠️" if score >= 0.4 else "❌"
                    print(f"  {status} {factor.value}: {score:.2f}")
                
                if ril_result.get("mitigation_strategies"):
                    print(f"\n🛡️ Mitigationsstrategien ({len(ril_result['mitigation_strategies'])}):")
                    for strategy in ril_result["mitigation_strategies"][:3]:
                        print(f"  - {strategy['barrier']}: {strategy['strategy']}")
        else:
            print(f"\n❌ Fehler: {result['error']}")
    
    # Statistiken demonstrieren
    print(f"\n\n{'='*70}")
    print("📈 Analyse-Statistiken:")
    
    analyzer = _get_analyzer_instance()
    stats = analyzer.get_analysis_stats()
    
    print(f"  Gesamt-Analysen: {stats['total_analyses']}")
    print(f"  Durchschn. Machbarkeit: {stats['average_feasibility']:.1%}")
    print(f"  Kritische Faktoren gefunden: {stats['critical_factors_found']}")
    print(f"  Erfolgreiche Mitigationen: {stats['successful_mitigations']}")
    
    # Test mit angepassten Gewichtungen
    print(f"\n\n{'='*70}")
    print("🔧 Test mit angepassten Faktor-Gewichtungen:")
    
    custom_context = {
        "profile": test_profile.copy(),
        "config": {
            "ril": {
                "feasibility_weights": {
                    FeasibilityFactor.TECHNICAL: 0.30,  # Erhöht
                    FeasibilityFactor.SOCIAL: 0.15,     # Reduziert
                    FeasibilityFactor.ORGANIZATIONAL: 0.15,
                    FeasibilityFactor.ECONOMIC: 0.20,
                    FeasibilityFactor.TEMPORAL: 0.10,
                    FeasibilityFactor.LEGAL: 0.05,      # Reduziert
                    FeasibilityFactor.ETHICAL: 0.05
                }
            }
        }
    }
    
    result = run_module("Technisch anspruchsvolles Projekt", custom_context)
    if result["success"]:
        print(f"  Machbarkeit mit angepassten Gewichten: {result['result']['overall_feasibility']:.1%}")
        print(f"  → Technische Faktoren haben mehr Einfluss")
    
    print("\n✅ RIL Demo v2.0 abgeschlossen!")
    print("\nDas Modul bietet:")
    print("  • Standardisierte Baukasten-Schnittstelle")
    print("  • Umfassende Context-Integration (RESL, NGA, SBP, DOF, ASO)")
    print("  • Detaillierte Machbarkeitsanalyse mit 7 Faktoren")
    print("  • Risikobewertung und Erfolgsprognose")
    print("  • Implementierungsplanung mit Phasen")
    print("  • Anpassbare Detail-Level und Gewichtungen")


if __name__ == "__main__":
    demo()