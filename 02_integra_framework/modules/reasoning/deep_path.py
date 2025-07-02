# # -*- coding: utf-8 -*-

“””
modules/reasoning/deep_path.py

🧠 DEEP PATH - Umfassende ethische 5-Schritt-Analyse für INTEGRA Light 🧠

Implementiert komplexe ethische Entscheidungsfindung für kritische Anfragen:

- 5-Schritt ALIGN-basierte Analyse (Awareness → Learning → Integrity → Governance → Nurturing)
- Stakeholder-Impact-Assessment
- Risiko-Nutzen-Abwägung
- Konflikt-Erkennung und Resolution
- Ethische Begründung und Transparenz
- Fallback-Mechanismen für unklare Situationen

Design-Philosophie: Gründliche ethische Durchdringung komplexer Entscheidungen

Version: INTEGRA Light 1.0
“””

import re
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

# ==============================================================================

# 1. Deep Path Enums und Datenstrukturen

# ==============================================================================

class AnalysisStep(Enum):
“”“📋 Die 5 ALIGN-basierten Analyse-Schritte”””
AWARENESS = “awareness”           # Kontext & Stakeholder verstehen
LEARNING = “learning”             # Aus Erfahrung & Feedback lernen
INTEGRITY = “integrity”           # Wahrheit & Konsistenz prüfen
GOVERNANCE = “governance”         # Kontrolle & Verantwortung sichern
NURTURING = “nurturing”          # Wohlbefinden & Vertrauen fördern

class ConflictType(Enum):
“”“⚔️ Arten von ethischen Konflikten”””
PRINCIPLE_CONFLICT = “principle_conflict”     # ALIGN-Prinzipien konfligieren
STAKEHOLDER_CONFLICT = “stakeholder_conflict” # Verschiedene Stakeholder-Interessen
VALUE_CONFLICT = “value_conflict”             # Grundlegende Werte-Konflikte
TEMPORAL_CONFLICT = “temporal_conflict”       # Kurz- vs. Langzeit-Interessen
RESOURCE_CONFLICT = “resource_conflict”       # Begrenzte Ressourcen

class DecisionQuality(Enum):
“”“🏆 Qualität der ethischen Entscheidung”””
EXCELLENT = “excellent”       # Alle Kriterien erfüllt, keine Konflikte
GOOD = “good”                # Meiste Kriterien erfüllt, kleine Kompromisse
ACCEPTABLE = “acceptable”     # Grundstandards erfüllt, größere Kompromisse
PROBLEMATIC = “problematic”   # Ethische Bedenken, aber vertretbar
UNACCEPTABLE = “unacceptable” # Ethische Standards verletzt

@dataclass
class StakeholderAnalysis:
“”“👥 Analyse der betroffenen Stakeholder”””
primary_stakeholders: List[str] = field(default_factory=list)    # Direkt Betroffene
secondary_stakeholders: List[str] = field(default_factory=list)  # Indirekt Betroffene
vulnerable_groups: List[str] = field(default_factory=list)       # Besonders schützenswerte
potential_conflicts: List[str] = field(default_factory=list)     # Interessenskonflikte
impact_assessment: Dict[str, float] = field(default_factory=dict) # Auswirkung pro Stakeholder

@dataclass
class EthicalStep:
“”“📝 Einzelner Schritt der ethischen Analyse”””
step: AnalysisStep
score: float = 0.0                    # 0.0-1.0 Score für diesen Schritt
concerns: List[str] = field(default_factory=list)    # Identifizierte Bedenken
strengths: List[str] = field(default_factory=list)   # Positive Aspekte
recommendations: List[str] = field(default_factory=list) # Verbesserungsvorschläge
reasoning: str = “”                   # Detaillierte Begründung
confidence: float = 0.0               # Konfidenz in diese Analyse

@dataclass
class DeepPathAnalysis:
“”“🧠 Vollständige Deep Path Analyse-Ergebnisse”””
overall_score: float = 0.0                          # Gesamt-ALIGN-Score
decision_quality: DecisionQuality = DecisionQuality.ACCEPTABLE
step_analyses: List[EthicalStep] = field(default_factory=list)
stakeholder_analysis: Optional[StakeholderAnalysis] = None
conflicts_detected: List[ConflictType] = field(default_factory=list)
final_recommendation: str = “”
alternative_options: List[str] = field(default_factory=list)
ethical_justification: str = “”
risk_mitigation: List[str] = field(default_factory=list)
confidence: float = 0.0
processing_time: str = “”

@dataclass
class DeepPathConfig:
“”“⚙️ Konfiguration für Deep Path Analyse”””

```
# Analyse-Tiefe
detailed_stakeholder_analysis: bool = True     # Umfassende Stakeholder-Analyse
comprehensive_conflict_detection: bool = True  # Detaillierte Konflikt-Erkennung
generate_alternatives: bool = True             # Alternative Lösungen generieren

# Scoring-Parameter
min_acceptable_score: float = 0.6              # Min. Score für "acceptable"
excellence_threshold: float = 0.9              # Score für "excellent"
critical_concerns_threshold: int = 3           # Max kritische Bedenken

# Stakeholder-Gewichtung
vulnerable_group_weight: float = 1.5           # Gewichtung für vulnerable Gruppen
primary_stakeholder_weight: float = 1.2       # Gewichtung für primäre Stakeholder

# Verhalten bei Konflikten
strict_conflict_resolution: bool = True        # Strenge Konflikt-Resolution
allow_compromises: bool = True                 # Kompromisse erlauben
escalate_major_conflicts: bool = True          # Große Konflikte eskalieren
```

# ==============================================================================

# 2. Hauptklasse für Deep Path Analyse

# ==============================================================================

class INTEGRADeepPath:
“””
🧠 Umfassende ethische Analyse für INTEGRA Light

```
Implementiert die 5-Schritt ALIGN-Analyse:
1. AWARENESS: Kontext & Stakeholder verstehen
2. LEARNING: Aus Erfahrung & Feedback lernen 
3. INTEGRITY: Wahrheit & Konsistenz prüfen
4. GOVERNANCE: Kontrolle & Verantwortung sichern
5. NURTURING: Wohlbefinden & Vertrauen fördern

Features:
- Detaillierte Stakeholder-Analyse
- Konflikt-Erkennung und -Resolution
- Alternative Lösungswege
- Ethische Begründungen
- Risiko-Mitigation
"""

def __init__(self, config: Optional[DeepPathConfig] = None):
    self.config = config or DeepPathConfig()
    self.analysis_history: List[Dict[str, Any]] = []
    self.learned_patterns: Dict[str, List[str]] = {
        'successful_resolutions': [],
        'problematic_patterns': [],
        'stakeholder_insights': []
    }
   
    print("🧠 INTEGRA Deep Path initialisiert")
    print(f"🎯 Min. akzeptabler Score: {self.config.min_acceptable_score}")
    print(f"🏆 Excellence-Schwelle: {self.config.excellence_threshold}")
    print(f"👥 Stakeholder-Analyse: {'Aktiv' if self.config.detailed_stakeholder_analysis else 'Basic'}")

def analyze_request(
    self,
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> DeepPathAnalysis:
    """
    🔍 Hauptfunktion: Führt umfassende ethische 5-Schritt-Analyse durch
   
    Args:
        input_data: Eingabe-Query
        profile: Ethisches Profil mit ALIGN-Gewichten
        context: Entscheidungskontext
       
    Returns:
        DeepPathAnalysis mit vollständigen Ergebnissen
    """
   
    start_time = datetime.now()
   
    query = input_data.get('query', input_data.get('message', ''))
    if not query:
        return self._create_error_analysis("Keine Anfrage für Analyse gefunden")
   
    print(f"🧠 Starte Deep Path Analyse für: \"{query[:60]}...\"")
   
    # Schritt 0: Vorbereitende Kontextanalyse
    enriched_context = self._enrich_context(input_data, context)
   
    # Schritt 1-5: Die 5 ALIGN-Schritte durchführen
    step_analyses = []
   
    # AWARENESS: Kontext & Stakeholder verstehen
    awareness_step = self._perform_awareness_analysis(query, enriched_context, profile)
    step_analyses.append(awareness_step)
   
    # LEARNING: Aus Erfahrung & Feedback lernen
    learning_step = self._perform_learning_analysis(query, enriched_context, profile)
    step_analyses.append(learning_step)
   
    # INTEGRITY: Wahrheit & Konsistenz prüfen
    integrity_step = self._perform_integrity_analysis(query, enriched_context, profile)
    step_analyses.append(integrity_step)
   
    # GOVERNANCE: Kontrolle & Verantwortung sichern
    governance_step = self._perform_governance_analysis(query, enriched_context, profile)
    step_analyses.append(governance_step)
   
    # NURTURING: Wohlbefinden & Vertrauen fördern
    nurturing_step = self._perform_nurturing_analysis(query, enriched_context, profile)
    step_analyses.append(nurturing_step)
   
    # Schritt 6: Stakeholder-Analyse (wenn aktiviert)
    stakeholder_analysis = None
    if self.config.detailed_stakeholder_analysis:
        stakeholder_analysis = self._perform_stakeholder_analysis(query, enriched_context)
   
    # Schritt 7: Konflikt-Erkennung
    conflicts = self._detect_conflicts(step_analyses, stakeholder_analysis)
   
    # Schritt 8: Gesamt-Score berechnen
    overall_score = self._calculate_overall_score(step_analyses, profile)
   
    # Schritt 9: Entscheidungsqualität bestimmen
    decision_quality = self._assess_decision_quality(overall_score, step_analyses, conflicts)
   
    # Schritt 10: Finale Empfehlung generieren
    final_recommendation = self._generate_final_recommendation(
        query, step_analyses, overall_score, decision_quality, conflicts
    )
   
    # Schritt 11: Alternative Optionen (wenn konfiguriert)
    alternatives = []
    if self.config.generate_alternatives and decision_quality in [DecisionQuality.PROBLEMATIC, DecisionQuality.ACCEPTABLE]:
        alternatives = self._generate_alternative_options(query, step_analyses, conflicts)
   
    # Schritt 12: Ethische Begründung
    ethical_justification = self._generate_ethical_justification(step_analyses, overall_score, conflicts)
   
    # Schritt 13: Risiko-Mitigation
    risk_mitigation = self._generate_risk_mitigation(step_analyses, conflicts)
   
    # Schritt 14: Gesamtkonfidenz berechnen
    confidence = self._calculate_overall_confidence(step_analyses)
   
    processing_time = str(datetime.now() - start_time)
   
    # Ergebnis zusammenstellen
    analysis = DeepPathAnalysis(
        overall_score=overall_score,
        decision_quality=decision_quality,
        step_analyses=step_analyses,
        stakeholder_analysis=stakeholder_analysis,
        conflicts_detected=conflicts,
        final_recommendation=final_recommendation,
        alternative_options=alternatives,
        ethical_justification=ethical_justification,
        risk_mitigation=risk_mitigation,
        confidence=confidence,
        processing_time=processing_time
    )
   
    # Für zukünftiges Lernen protokollieren
    self._record_analysis_for_learning(query, analysis)
   
    print(f"✅ Deep Path Analyse abgeschlossen (Score: {overall_score:.2f}, Qualität: {decision_quality.value})")
   
    return analysis

def _enrich_context(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """🔍 Erweitert den Kontext mit zusätzlichen Informationen"""
   
    enriched = context.copy()
   
    # Frühere ALIGN-Scores einbeziehen
    if 'align_score' in context:
        enriched['previous_align_score'] = context['align_score']
   
    # Fast Path Analyse einbeziehen (falls vorhanden)
    if 'fast_path_analysis' in context:
        fast_path = context['fast_path_analysis']
        enriched['fast_path_insights'] = {
            'why_deep_path': fast_path.get('reasoning', ''),
            'risk_indicators': fast_path.get('risk_indicators', []),
            'ethical_flags': fast_path.get('ethical_flags', [])
        }
   
    # User-Kontext erweitern
    enriched['user_context'] = input_data.get('user_context', {})
    enriched['session_history'] = input_data.get('session_history', [])
   
    return enriched

def _perform_awareness_analysis(self, query: str, context: Dict[str, Any], profile: Dict[str, Any]) -> EthicalStep:
    """👁️ AWARENESS: Kontext & Stakeholder verstehen"""
   
    concerns = []
    strengths = []
    recommendations = []
    score = 0.8  # Basis-Score
   
    # Kontext-Sensitivität prüfen
    if self._is_context_sensitive(query):
        strengths.append("Anfrage zeigt Bewusstsein für Kontext")
        score += 0.1
    else:
        concerns.append("Möglicherweise unzureichende Kontext-Berücksichtigung")
        score -= 0.1
   
    # Stakeholder-Bewusstsein
    explicit_stakeholders = self._identify_explicit_stakeholders(query)
    if explicit_stakeholders:
        strengths.append(f"Explizite Stakeholder erkannt: {', '.join(explicit_stakeholders)}")
        score += 0.1
    else:
        concerns.append("Keine expliziten Stakeholder in Anfrage erwähnt")
        recommendations.append("Stakeholder-Auswirkungen berücksichtigen")
   
    # Komplexitäts-Bewusstsein
    if self._indicates_complexity_awareness(query):
        strengths.append("Bewusstsein für Komplexität der Situation")
        score += 0.1
   
    # Frühere Insights aus Fast Path
    if 'fast_path_insights' in context:
        insights = context['fast_path_insights']
        if insights.get('risk_indicators'):
            concerns.extend([f"Fast Path Risiko: {risk}" for risk in insights['risk_indicators'][:2]])
            score -= 0.1
   
    # Kulturelle Sensitivität
    if self._requires_cultural_sensitivity(query):
        if self._shows_cultural_awareness(query):
            strengths.append("Kulturelle Sensitivität erkennbar")
        else:
            concerns.append("Kulturelle Dimensionen nicht berücksichtigt")
            recommendations.append("Kulturelle Unterschiede beachten")
            score -= 0.1
   
    reasoning = self._generate_awareness_reasoning(query, explicit_stakeholders, context)
   
    return EthicalStep(
        step=AnalysisStep.AWARENESS,
        score=max(0.0, min(1.0, score)),
        concerns=concerns,
        strengths=strengths,
        recommendations=recommendations,
        reasoning=reasoning,
        confidence=0.8
    )

def _perform_learning_analysis(self, query: str, context: Dict[str, Any], profile: Dict[str, Any]) -> EthicalStep:
    """📚 LEARNING: Aus Erfahrung & Feedback lernen"""
   
    concerns = []
    strengths = []
    recommendations = []
    score = 0.7  # Basis-Score
   
    # Lernbereitschaft in der Anfrage
    if self._indicates_learning_intent(query):
        strengths.append("Lernbereitschaft in Anfrage erkennbar")
        score += 0.15
   
    # Feedback-Berücksichtigung aus Historie
    if 'session_history' in context and context['session_history']:
        history = context['session_history']
        if self._shows_improvement_from_history(query, history):
            strengths.append("Verbesserung basierend auf früherem Feedback erkennbar")
            score += 0.1
        else:
            concerns.append("Frühere Lessons Learned nicht berücksichtigt")
            score -= 0.05
   
    # Adaptivität der Anfrage
    if self._shows_adaptive_thinking(query):
        strengths.append("Adaptive Denkweise erkennbar")
        score += 0.1
    else:
        recommendations.append("Flexiblere Herangehensweise erwägen")
   
    # Metakognition (Denken über das Denken)
    if self._indicates_metacognition(query):
        strengths.append("Metakognitives Bewusstsein vorhanden")
        score += 0.1
   
    # Fehlerkultur
    if self._acknowledges_uncertainty(query):
        strengths.append("Unsicherheit wird angemessen thematisiert")
        score += 0.05
   
    # Lernen aus gelernten Patterns
    for pattern in self.learned_patterns['successful_resolutions']:
        if pattern.lower() in query.lower():
            strengths.append("Anfrage folgt erfolgreichen Mustern")
            score += 0.05
            break
   
    reasoning = self._generate_learning_reasoning(query, context)
   
    return EthicalStep(
        step=AnalysisStep.LEARNING,
        score=max(0.0, min(1.0, score)),
        concerns=concerns,
        strengths=strengths,
        recommendations=recommendations,
        reasoning=reasoning,
        confidence=0.75
    )

def _perform_integrity_analysis(self, query: str, context: Dict[str, Any], profile: Dict[str, Any]) -> EthicalStep:
    """🎯 INTEGRITY: Wahrheit & Konsistenz prüfen"""
   
    concerns = []
    strengths = []
    recommendations = []
    score = 0.9  # Hoher Basis-Score für Integrity
   
    # Wahrheitsgehalt prüfen
    truth_indicators = self._assess_truth_indicators(query)
    if truth_indicators['deception_risk'] > 0.3:
        concerns.append("Potenzielle Wahrheitsverzerrung erkannt")
        score -= 0.3
    elif truth_indicators['truth_seeking']:
        strengths.append("Wahrheitssuche erkennbar")
        score += 0.05
   
    # Konsistenz-Prüfung
    if 'session_history' in context:
        consistency_check = self._check_consistency_with_history(query, context['session_history'])
        if not consistency_check['consistent']:
            concerns.append(f"Inkonsistenz mit früheren Aussagen: {consistency_check['reason']}")
            score -= 0.2
        else:
            strengths.append("Konsistent mit früherer Kommunikation")
   
    # Manipulation-Erkennung
    manipulation_risk = self._assess_manipulation_risk(query)
    if manipulation_risk > 0.4:
        concerns.append("Potenzielle Manipulationsabsicht erkannt")
        score -= 0.4
        recommendations.append("Ehrliche, direkte Kommunikation anstreben")
   
    # Transparenz-Bewertung
    if self._promotes_transparency(query):
        strengths.append("Fördert Transparenz und Offenheit")
        score += 0.1
    else:
        recommendations.append("Mehr Transparenz über Absichten")
   
    # Faktische Korrektheit (wo prüfbar)
    factual_claims = self._extract_factual_claims(query)
    if factual_claims:
        for claim in factual_claims[:3]:  # Prüfe bis zu 3 Claims
            if self._is_factually_questionable(claim):
                concerns.append(f"Fragliche faktische Behauptung: {claim}")
                score -= 0.1
   
    # Ethische Konsistenz
    if self._violates_ethical_consistency(query, profile):
        concerns.append("Verletzt ethische Konsistenz-Prinzipien")
        score -= 0.2
   
    reasoning = self._generate_integrity_reasoning(query, truth_indicators, manipulation_risk)
   
    return EthicalStep(
        step=AnalysisStep.INTEGRITY,
        score=max(0.0, min(1.0, score)),
        concerns=concerns,
        strengths=strengths,
        recommendations=recommendations,
        reasoning=reasoning,
        confidence=0.85
    )

def _perform_governance_analysis(self, query: str, context: Dict[str, Any], profile: Dict[str, Any]) -> EthicalStep:
    """🏛️ GOVERNANCE: Kontrolle & Verantwortung sichern"""
   
    concerns = []
    strengths = []
    recommendations = []
    score = 0.8  # Basis-Score
   
    # Kontrollebene prüfen
    control_level = self._assess_control_requirements(query)
    if control_level == 'high':
        if self._indicates_human_oversight_acceptance(query):
            strengths.append("Akzeptiert menschliche Kontrolle")
            score += 0.1
        else:
            concerns.append("Hohe Kontrollbedürftigkeit, aber keine Oversight-Bereitschaft")
            score -= 0.2
            recommendations.append("Menschliche Kontrolle einbeziehen")
   
    # Verantwortlichkeit
    if self._shows_accountability_awareness(query):
        strengths.append("Verantwortlichkeits-Bewusstsein vorhanden")
        score += 0.1
    else:
        concerns.append("Unklare Verantwortlichkeiten")
        recommendations.append("Verantwortlichkeiten klären")
   
    # Autonomie vs. Kontrolle Balance
    autonomy_level = self._assess_autonomy_implications(query)
    if autonomy_level > 0.7:  # Hohe Autonomie-Anforderung
        concerns.append("Hohe Autonomie-Anforderung könnte Kontrolle erschweren")
        score -= 0.1
        recommendations.append("Kontroll-Mechanismen trotz Autonomie sicherstellen")
   
    # Eskalations-Bedarf
    if self._requires_escalation(query, context):
        recommendations.append("Eskalation an menschliche Autorität empfohlen")
        if self._accepts_escalation(query):
            strengths.append("Eskalations-Bereitschaft vorhanden")
        else:
            concerns.append("Eskalations-Resistenz erkannt")
            score -= 0.15
   
    # Audit-Fähigkeit
    if self._supports_auditability(query):
        strengths.append("Unterstützt Nachvollziehbarkeit")
        score += 0.05
    else:
        recommendations.append("Entscheidung dokumentierbar gestalten")
   
    # Governance-Konflikte mit anderen Prinzipien
    governance_conflicts = self._identify_governance_conflicts(query, context)
    if governance_conflicts:
        concerns.extend([f"Governance-Konflikt: {conflict}" for conflict in governance_conflicts])
        score -= len(governance_conflicts) * 0.05
   
    reasoning = self._generate_governance_reasoning(query, control_level, autonomy_level)
   
    return EthicalStep(
        step=AnalysisStep.GOVERNANCE,
        score=max(0.0, min(1.0, score)),
        concerns=concerns,
        strengths=strengths,
        recommendations=recommendations,
        reasoning=reasoning,
        confidence=0.8
    )

def _perform_nurturing_analysis(self, query: str, context: Dict[str, Any], profile: Dict[str, Any]) -> EthicalStep:
    """🤗 NURTURING: Wohlbefinden & Vertrauen fördern"""
   
    concerns = []
    strengths = []
    recommendations = []
    score = 0.75  # Basis-Score
   
    # Wohlbefinden-Auswirkung
    wellbeing_impact = self._assess_wellbeing_impact(query)
    if wellbeing_impact['positive_impact'] > 0.5:
        strengths.append("Positive Auswirkung auf Wohlbefinden erkennbar")
        score += 0.15
    elif wellbeing_impact['negative_impact'] > 0.3:
        concerns.append("Potenzielle negative Auswirkung auf Wohlbefinden")
        score -= 0.2
        recommendations.append("Wohlbefinden-schonendere Alternativen erwägen")
   
    # Vertrauensbildung
    trust_factors = self._assess_trust_factors(query)
    if trust_factors['builds_trust']:
        strengths.append("Fördert Vertrauensbildung")
        score += 0.1
    elif trust_factors['erodes_trust']:
        concerns.append("Könnte Vertrauen untergraben")
        score -= 0.15
   
    # Vulnerable Gruppen
    vulnerable_impact = self._assess_vulnerable_group_impact(query)
    if vulnerable_impact['groups_affected']:
        if vulnerable_impact['protection_adequate']:
            strengths.append(f"Angemessener Schutz für: {', '.join(vulnerable_impact['groups_affected'])}")
            score += 0.1
        else:
            concerns.append(f"Unzureichender Schutz für: {', '.join(vulnerable_impact['groups_affected'])}")
            score -= 0.25
            recommendations.append("Zusätzliche Schutzmaßnahmen für vulnerable Gruppen")
   
    # Empathie und Mitgefühl
    if self._demonstrates_empathy(query):
        strengths.append("Empathische Herangehensweise erkennbar")
        score += 0.1
    else:
        recommendations.append("Empathischere Kommunikation erwägen")
   
    # Langzeit-Beziehung
    if self._supports_longterm_relationship(query):
        strengths.append("Unterstützt langfristige positive Beziehung")
        score += 0.05
   
    # Harm-Prevention
    harm_potential = self._assess_harm_potential(query)
    if harm_potential > 0.4:
        concerns.append("Potenzial für Schädigung erkannt")
        score -= harm_potential * 0.3
        recommendations.append("Schadenspräventions-Maßnahmen implementieren")
   
    # Fürsorglichkeit
    if self._shows_caring_approach(query):
        strengths.append("Fürsorgliche Herangehensweise")
        score += 0.1
   
    reasoning = self._generate_nurturing_reasoning(query, wellbeing_impact, vulnerable_impact)
   
    return EthicalStep(
        step=AnalysisStep.NURTURING,
        score=max(0.0, min(1.0, score)),
        concerns=concerns,
        strengths=strengths,
        recommendations=recommendations,
        reasoning=reasoning,
        confidence=0.8
    )

def _perform_stakeholder_analysis(self, query: str, context: Dict[str, Any]) -> StakeholderAnalysis:
    """👥 Detaillierte Stakeholder-Analyse"""
   
    # Primäre Stakeholder (direkt betroffen)
    primary = self._identify_primary_stakeholders(query)
   
    # Sekundäre Stakeholder (indirekt betroffen) 
    secondary = self._identify_secondary_stakeholders(query, primary)
   
    # Vulnerable Gruppen
    vulnerable = self._identify_vulnerable_stakeholders(query, primary + secondary)
   
    # Potenzielle Konflikte zwischen Stakeholdern
    conflicts = self._identify_stakeholder_conflicts(primary, secondary, vulnerable, query)
   
    # Impact-Assessment
    impact_assessment = {}
    all_stakeholders = set(primary + secondary + vulnerable)
   
    for stakeholder in all_stakeholders:
        impact_score = self._calculate_stakeholder_impact(stakeholder, query)
        impact_assessment[stakeholder] = impact_score
   
    return StakeholderAnalysis(
        primary_stakeholders=primary,
        secondary_stakeholders=secondary,
        vulnerable_groups=vulnerable,
        potential_conflicts=conflicts,
        impact_assessment=impact_assessment
    )

def _detect_conflicts(self, step_analyses: List[EthicalStep], stakeholder_analysis: Optional[StakeholderAnalysis]) -> List[ConflictType]:
    """⚔️ Erkennt verschiedene Arten von ethischen Konflikten"""
   
    conflicts = []
   
    # Prinzipien-Konflikte (niedrige Scores in mehreren ALIGN-Bereichen)
    low_scores = [step for step in step_analyses if step.score < 0.6]
    if len(low_scores) >= 2:
        conflicts.append(ConflictType.PRINCIPLE_CONFLICT)
   
    # Stakeholder-Konflikte
    if stakeholder_analysis and stakeholder_analysis.potential_conflicts:
        conflicts.append(ConflictType.STAKEHOLDER_CONFLICT)
   
    # Werte-Konflikte (erkennbar an spezifischen Bedenken)
    value_conflict_indicators = ['moral dilemma', 'ethical conflict', 'competing values']
    for step in step_analyses
```