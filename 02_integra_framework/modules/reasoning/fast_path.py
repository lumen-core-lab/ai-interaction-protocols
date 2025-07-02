# # -*- coding: utf-8 -*-

"""
modules/reasoning/fast_path.py

⚡ FAST PATH - Intelligente Schnell-Entscheidungen für INTEGRA Light ⚡

Implementiert effizienten Fast Path für ethisch unkritische Anfragen:

- Intelligente Konflikt-Erkennung
- Blitzschnelle Antworten bei einfachen Fragen
- Automatische Weiterleitung an Deep Path wenn nötig
- Confidence-basierte Entscheidungen
- Pattern-Erkennung für bekannte sichere Anfragen
- Adaptive Lernfähigkeit für verbesserte Erkennung

Design-Philosophie: Maximale Effizienz bei garantierter ethischer Sicherheit

Version: INTEGRA Light 1.0
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# ==============================================================================

# 1. Fast Path Enums und Datenstrukturen

# ==============================================================================

class PathDecision(Enum):
"""🚦 Verfügbare Path-Entscheidungen"""
FAST_PATH = "fast_path"           # Direkte schnelle Antwort
DEEP_PATH = "deep_path"           # Weiterleitung an ethische Analyse
UNCERTAIN = "uncertain"           # Unsicher - Default zu Deep Path

class QuestionCategory(Enum):
"""📋 Kategorien für schnelle Klassifizierung"""
FACTUAL = "factual"                 # Fakten-Fragen
PROCEDURAL = "procedural"           # Wie-mache-ich-das Fragen
INFORMATIONAL = "informational"     # Info-Anfragen
CREATIVE = "creative"               # Kreative Hilfe
CONVERSATIONAL = "conversational"   # Small Talk
ETHICAL_CONFLICT = "ethical_conflict" # Ethische Dilemmata
SENSITIVE = "sensitive"             # Sensible Themen
HARMFUL = "harmful"                 # Potentiell schädlich

@dataclass
class FastPathPattern:
"""🎯 Muster für Fast Path Erkennung"""
pattern: str = ""                           # Regex-Pattern
category: QuestionCategory = QuestionCategory.FACTUAL
confidence_threshold: float = 0.8           # Min. Konfidenz für Fast Path
safe_response_template: str = ""            # Template für sichere Antwort
examples: List[str] = field(default_factory=list)

@dataclass
class PathAnalysis:
"""📊 Analyse-Ergebnis für Path-Entscheidung"""
recommended_path: PathDecision = PathDecision.UNCERTAIN
confidence: float = 0.0
category: Optional[QuestionCategory] = None
risk_indicators: List[str] = field(default_factory=list)
safe_patterns_matched: List[str] = field(default_factory=list)
ethical_flags: List[str] = field(default_factory=list)
reasoning: str = ""

@dataclass
class FastPathConfig:
"""⚙️ Konfiguration für Fast Path System"""

```
# Konfidenz-Schwellenwerte
min_fast_path_confidence: float = 0.8      # Min. Konfidenz für Fast Path
max_risk_tolerance: float = 0.2            # Max. Risiko für Fast Path
uncertainty_threshold: float = 0.5         # Unter diesem Wert → Deep Path

# Pattern-Matching
enable_pattern_learning: bool = True       # Lernt neue sichere Patterns
strict_mode: bool = False                  # Konservative vs. liberale Erkennung
custom_patterns: List[FastPathPattern] = field(default_factory=list)

# Sicherheits-Einstellungen
block_sensitive_topics: bool = True        # Blockiert sensitive Themen
require_human_review: bool = False         # Erfordert Review für alle Entscheidungen
enable_ethical_preprocessing: bool = True  # Ethik-Check vor Fast Path
```

# ==============================================================================

# 2. Hauptklasse für intelligenten Fast Path

# ==============================================================================

class INTEGRAFastPath:
"""
⚡ Intelligentes Fast Path System für INTEGRA Light

```
Features:
- Blitzschnelle Erkennung sicherer Anfragen
- Intelligente Weiterleitung an Deep Path bei Konflikten
- Adaptive Pattern-Erkennung für verbesserte Effizienz
- Konfidenz-basierte Entscheidungen
- Vollständige Sicherheits-Validierung
- Lernfähigkeit für bessere Klassifizierung
"""

def __init__(self, config: Optional[FastPathConfig] = None):
    self.config = config or FastPathConfig()
    self.safe_patterns = self._initialize_safe_patterns()
    self.risk_indicators = self._initialize_risk_indicators()
    self.processing_history: List[Dict[str, Any]] = []
    self.learned_patterns: List[FastPathPattern] = []
   
    print("⚡ INTEGRA Fast Path initialisiert")
    print(f"🎯 Konfidenz-Schwelle: {self.config.min_fast_path_confidence}")
    print(f"🛡️ Risiko-Toleranz: {self.config.max_risk_tolerance}")
    print(f"🧠 Pattern-Lernen: {'Aktiv' if self.config.enable_pattern_learning else 'Deaktiviert'}")

def analyze_request(
    self,
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> PathAnalysis:
    """
    🔍 Hauptfunktion: Analysiert Anfrage und empfiehlt Path
   
    Args:
        input_data: Eingabe-Query
        profile: Ethisches Profil
        context: Entscheidungskontext
       
    Returns:
        PathAnalysis mit Empfehlung und Begründung
    """
   
    query = input_data.get('query', input_data.get('message', ''))
    if not query:
        return PathAnalysis(
            recommended_path=PathDecision.DEEP_PATH,
            confidence=0.0,
            reasoning="Keine Anfrage gefunden - Standard Deep Path"
        )
   
    # Schritt 1: Grundlegende Sicherheitsprüfung
    safety_check = self._perform_safety_check(query, context)
   
    if not safety_check['safe']:
        return PathAnalysis(
            recommended_path=PathDecision.DEEP_PATH,
            confidence=1.0,
            risk_indicators=safety_check['risk_indicators'],
            ethical_flags=safety_check['ethical_flags'],
            reasoning=f"Sicherheitsprüfung fehlgeschlagen: {safety_check['reason']}"
        )
   
    # Schritt 2: Kategorisierung der Anfrage
    category_analysis = self._categorize_query(query)
   
    # Schritt 3: Pattern-Matching für bekannte sichere Anfragen
    pattern_analysis = self._match_safe_patterns(query, category_analysis['category'])
   
    # Schritt 4: Risiko-Bewertung
    risk_assessment = self._assess_risk_level(query, context, category_analysis)
   
    # Schritt 5: Konfidenz-Berechnung
    confidence = self._calculate_confidence(
        category_analysis,
        pattern_analysis,
        risk_assessment,
        safety_check
    )
   
    # Schritt 6: Path-Empfehlung basierend auf allen Faktoren
    recommended_path = self._determine_path(
        confidence,
        risk_assessment['risk_level'],
        category_analysis['category'],
        pattern_analysis['matched']
    )
   
    # Schritt 7: Adaptive Lernkomponente
    if self.config.enable_pattern_learning:
        self._update_pattern_learning(query, category_analysis, recommended_path)
   
    return PathAnalysis(
        recommended_path=recommended_path,
        confidence=confidence,
        category=category_analysis['category'],
        risk_indicators=risk_assessment['indicators'],
        safe_patterns_matched=pattern_analysis['matched_patterns'],
        ethical_flags=safety_check.get('ethical_flags', []),
        reasoning=self._generate_reasoning(
            recommended_path, confidence, category_analysis,
            pattern_analysis, risk_assessment
        )
    )

def _perform_safety_check(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """🔒 Grundlegende Sicherheitsprüfung vor Path-Analyse"""
   
    risk_indicators = []
    ethical_flags = []
   
    # Direkte Risiko-Indikatoren
    high_risk_patterns = [
        r'(?:hack|exploit|break|destroy|damage)',
        r'(?:illegal|criminal|unlawful|fraud)',
        r'(?:hurt|harm|kill|suicide|violence)',
        r'(?:drug|weapon|bomb|terrorist)',
        r'(?:sexual|adult|porn|explicit)',
        r'(?:manipulate|deceive|lie|trick)',
        r'(?:personal|private|confidential|secret)',
        r'(?:bypass|ignore|disable).*(?:safety|security|ethics)'
    ]
   
    for pattern in high_risk_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            risk_indicators.append(f"High-risk pattern: {pattern}")
   
    # Ethische Flags
    ethical_concerns = [
        r'(?:discriminate|racism|sexism|bias)',
        r'(?:children|kids|minor)',
        r'(?:mental health|depression|anxiety)',
        r'(?:medical|health|diagnosis|treatment)',
        r'(?:financial|investment|money|loan)',
        r'(?:legal|lawyer|court|lawsuit)'
    ]
   
    for pattern in ethical_concerns:
        if re.search(pattern, query, re.IGNORECASE):
            ethical_flags.append(f"Ethical concern: {pattern}")
   
    # Kontext-basierte Risiken
    if context.get('align_violations'):
        risk_indicators.append("Previous ALIGN violations detected")
   
    if context.get('risk_level', 0) > 0.6:
        risk_indicators.append("High risk level in context")
   
    # Gesamtbewertung
    is_safe = len(risk_indicators) == 0 and len(ethical_flags) <= 1
   
    # Bei ethischen Flags: Je nach Konfiguration
    if ethical_flags and self.config.block_sensitive_topics:
        is_safe = False
   
    return {
        'safe': is_safe,
        'risk_indicators': risk_indicators,
        'ethical_flags': ethical_flags,
        'reason': '; '.join(risk_indicators + ethical_flags) if not is_safe else 'No safety concerns'
    }

def _categorize_query(self, query: str) -> Dict[str, Any]:
    """📋 Intelligente Kategorisierung der Anfrage"""
   
    # Pattern für verschiedene Kategorien
    category_patterns = {
        QuestionCategory.FACTUAL: [
            r'^(?:what|who|when|where|which|how many)',
            r'(?:definition|meaning|explain|describe)',
            r'(?:fact|information|data|statistic)',
            r'(?:capital|population|date|year|history)'
        ],
        QuestionCategory.PROCEDURAL: [
            r'^(?:how do|how can|how to)',
            r'(?:step|process|method|way|procedure)',
            r'(?:tutorial|guide|instruction)',
            r'(?:learn|teach|show me)'
        ],
        QuestionCategory.INFORMATIONAL: [
            r'(?:tell me about|information about)',
            r'(?:research|study|report|analysis)',
            r'(?:overview|summary|background)',
            r'(?:details|specifics|particulars)'
        ],
        QuestionCategory.CREATIVE: [
            r'(?:write|create|generate|make)',
            r'(?:story|poem|essay|article)',
            r'(?:design|plan|idea|concept)',
            r'(?:creative|artistic|imaginative)'
        ],
        QuestionCategory.CONVERSATIONAL: [
            r'^(?:hello|hi|hey|good morning)',
            r'(?:thank you|thanks|appreciate)',
            r'(?:how are you|what\'s up)',
            r'(?:small talk|chat|conversation)'
        ]
    }
   
    # Score für jede Kategorie berechnen
    category_scores = {}
   
    for category, patterns in category_patterns.items():
        score = 0
        matched_patterns = []
       
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 1
                matched_patterns.append(pattern)
       
        if score > 0:
            category_scores[category] = {
                'score': score / len(patterns),  # Normalisiert
                'matched_patterns': matched_patterns
            }
   
    # Beste Kategorie bestimmen
    if category_scores:
        best_category = max(category_scores.keys(), key=lambda k: category_scores[k]['score'])
        confidence = category_scores[best_category]['score']
    else:
        # Default: Potentiell komplex
        best_category = QuestionCategory.ETHICAL_CONFLICT
        confidence = 0.0
   
    return {
        'category': best_category,
        'confidence': confidence,
        'all_scores': category_scores
    }

def _match_safe_patterns(self, query: str, category: QuestionCategory) -> Dict[str, Any]:
    """🎯 Pattern-Matching für bekannt sichere Anfragen"""
   
    matched_patterns = []
    confidence_boost = 0.0
   
    # Kategorie-spezifische sichere Patterns
    if category == QuestionCategory.FACTUAL:
        safe_factual_patterns = [
            r'what is the capital of',
            r'when was.*born',
            r'how many.*in the world',
            r'what year did.*happen',
            r'definition of',
            r'meaning of'
        ]
       
        for pattern in safe_factual_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                matched_patterns.append(pattern)
                confidence_boost += 0.2
   
    elif category == QuestionCategory.PROCEDURAL:
        safe_procedural_patterns = [
            r'how to.*recipe',
            r'how to.*calculate',
            r'steps to.*install',
            r'how do I.*save',
            r'tutorial.*basic',
            r'learn.*language'
        ]
       
        for pattern in safe_procedural_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                matched_patterns.append(pattern)
                confidence_boost += 0.2
   
    elif category == QuestionCategory.CONVERSATIONAL:
        safe_conversational_patterns = [
            r'^hello$',
            r'^hi there$',
            r'^good morning$',
            r'^thank you$',
            r'^thanks$',
            r'how are you.*today'
        ]
       
        for pattern in safe_conversational_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                matched_patterns.append(pattern)
                confidence_boost += 0.3
   
    # Zusätzlich: Gelernte Patterns prüfen
    for learned_pattern in self.learned_patterns:
        if learned_pattern.category == category:
            if re.search(learned_pattern.pattern, query, re.IGNORECASE):
                matched_patterns.append(f"learned: {learned_pattern.pattern}")
                confidence_boost += 0.15
   
    # Custom Patterns aus Konfiguration
    for custom_pattern in self.config.custom_patterns:
        if custom_pattern.category == category:
            if re.search(custom_pattern.pattern, query, re.IGNORECASE):
                matched_patterns.append(f"custom: {custom_pattern.pattern}")
                confidence_boost += 0.2
   
    return {
        'matched': len(matched_patterns) > 0,
        'matched_patterns': matched_patterns,
        'confidence_boost': min(1.0, confidence_boost)
    }

def _assess_risk_level(
    self,
    query: str,
    context: Dict[str, Any],
    category_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """⚠️ Detaillierte Risiko-Bewertung"""
   
    risk_level = 0.0
    indicators = []
   
    # Basis-Risiko nach Kategorie
    category_risks = {
        QuestionCategory.FACTUAL: 0.1,
        QuestionCategory.PROCEDURAL: 0.2,
        QuestionCategory.INFORMATIONAL: 0.15,
        QuestionCategory.CREATIVE: 0.3,
        QuestionCategory.CONVERSATIONAL: 0.05,
        QuestionCategory.ETHICAL_CONFLICT: 0.9,
        QuestionCategory.SENSITIVE: 0.8,
        QuestionCategory.HARMFUL: 1.0
    }
   
    category = category_analysis['category']
    risk_level = category_risks.get(category, 0.5)
   
    # Komplexitäts-Indikatoren
    complexity_indicators = [
        (r'(?:should I|what if|whether)', 0.2, "Decision-making question"),
        (r'(?:opinion|think|believe|feel)', 0.3, "Subjective opinion request"),
        (r'(?:recommend|suggest|advise)', 0.2, "Recommendation request"),
        (r'(?:compare|better|worse|best)', 0.15, "Comparative judgment"),
        (r'(?:controversial|debate|argument)', 0.4, "Controversial topic"),
        (r'(?:moral|ethical|right|wrong)', 0.5, "Moral/ethical dimension"),
        (r'(?:personal|private|intimate)', 0.3, "Personal information"),
        (r'(?:future|predict|forecast)', 0.2, "Future prediction")
    ]
   
    for pattern, risk_add, description in complexity_indicators:
        if re.search(pattern, query, re.IGNORECASE):
            risk_level += risk_add
            indicators.append(description)
   
    # Kontext-basierte Risiken
    if context.get('align_score', 1.0) < 0.7:
        risk_level += 0.2
        indicators.append("Low ALIGN score in context")
   
    if context.get('previous_path') == 'deep_path':
        risk_level += 0.1
        indicators.append("Previous deep path usage")
   
    # Längen-basierte Komplexität
    query_length = len(query.split())
    if query_length > 20:
        risk_level += 0.1
        indicators.append("Long, complex query")
    elif query_length > 50:
        risk_level += 0.2
        indicators.append("Very long, complex query")
   
    # Mehrfach-Fragen
    if query.count('?') > 1:
        risk_level += 0.1
        indicators.append("Multiple questions")
   
    return {
        'risk_level': min(1.0, risk_level),
        'indicators': indicators,
        'base_category_risk': category_risks.get(category, 0.5)
    }

def _calculate_confidence(
    self,
    category_analysis: Dict[str, Any],
    pattern_analysis: Dict[str, Any],
    risk_assessment: Dict[str, Any],
    safety_check: Dict[str, Any]
) -> float:
    """📊 Berechnet Gesamtkonfidenz für Fast Path Entscheidung"""
   
    # Basis-Konfidenz aus Kategorisierung
    base_confidence = category_analysis['confidence']
   
    # Pattern-Matching Boost
    pattern_boost = pattern_analysis['confidence_boost']
   
    # Sicherheits-Penalty
    safety_penalty = 0.0
    if not safety_check['safe']:
        safety_penalty = 0.8
    elif safety_check['ethical_flags']:
        safety_penalty = 0.3
   
    # Risiko-Penalty
    risk_level = risk_assessment['risk_level']
    risk_penalty = risk_level * 0.5
   
    # Gesamtkonfidenz berechnen
    confidence = base_confidence + pattern_boost - safety_penalty - risk_penalty
   
    # Normalisierung
    confidence = max(0.0, min(1.0, confidence))
   
    return confidence

def _determine_path(
    self,
    confidence: float,
    risk_level: float,
    category: QuestionCategory,
    patterns_matched: bool
) -> PathDecision:
    """🚦 Finale Path-Entscheidung basierend auf allen Faktoren"""
   
    # Absolute Ausschlusskriterien für Fast Path
    if risk_level > self.config.max_risk_tolerance:
        return PathDecision.DEEP_PATH
   
    if category in [QuestionCategory.ETHICAL_CONFLICT, QuestionCategory.HARMFUL]:
        return PathDecision.DEEP_PATH
   
    # Konfidenz-basierte Entscheidung
    if confidence >= self.config.min_fast_path_confidence:
        return PathDecision.FAST_PATH
    elif confidence >= self.config.uncertainty_threshold:
        # Grenzbereich - zusätzliche Faktoren prüfen
        if patterns_matched and risk_level < 0.3:
            return PathDecision.FAST_PATH
        else:
            return PathDecision.DEEP_PATH
    else:
        return PathDecision.DEEP_PATH

def _generate_reasoning(
    self,
    path: PathDecision,
    confidence: float,
    category_analysis: Dict[str, Any],
    pattern_analysis: Dict[str, Any],
    risk_assessment: Dict[str, Any]
) -> str:
    """💡 Generiert menschenlesbare Begründung für Path-Entscheidung"""
   
    reasoning_parts = []
   
    # Hauptentscheidung
    if path == PathDecision.FAST_PATH:
        reasoning_parts.append(f"Fast Path empfohlen (Konfidenz: {confidence:.2f})")
    else:
        reasoning_parts.append(f"Deep Path empfohlen (Konfidenz: {confidence:.2f})")
   
    # Kategorisierung
    category = category_analysis['category']
    reasoning_parts.append(f"Kategorie: {category.value}")
   
    # Pattern-Matching
    if pattern_analysis['matched']:
        patterns_count = len(pattern_analysis['matched_patterns'])
        reasoning_parts.append(f"Sichere Patterns gefunden: {patterns_count}")
   
    # Risiko-Level
    risk_level = risk_assessment['risk_level']
    if risk_level > 0.5:
        reasoning_parts.append(f"Erhöhtes Risiko: {risk_level:.2f}")
   
    # Spezifische Indikatoren
    if risk_assessment['indicators']:
        top_indicators = risk_assessment['indicators'][:2]
        reasoning_parts.append(f"Indikatoren: {', '.join(top_indicators)}")
   
    return " | ".join(reasoning_parts)

def _update_pattern_learning(
    self,
    query: str,
    category_analysis: Dict[str, Any],
    recommended_path: PathDecision
):
    """🧠 Aktualisiert Pattern-Lernen basierend auf Entscheidungen"""
   
    if not self.config.enable_pattern_learning:
        return
   
    # Lerne nur von sicheren Fast Path Entscheidungen
    if recommended_path == PathDecision.FAST_PATH:
        category = category_analysis['category']
       
        # Extrahiere potentielle Patterns aus erfolgreichem Fast Path
        words = query.lower().split()
       
        # Bi-grams als potentielle neue Patterns
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
           
            # Prüfe ob schon vorhanden
            if not any(bigram in pattern.pattern for pattern in self.learned_patterns):
                # Erstelle neues gelerntes Pattern
                new_pattern = FastPathPattern(
                    pattern=re.escape(bigram),
                    category=category,
                    confidence_threshold=0.7,
                    examples=[query]
                )
               
                self.learned_patterns.append(new_pattern)
               
                # Limitiere Anzahl gelernter Patterns
                if len(self.learned_patterns) > 50:
                    self.learned_patterns = self.learned_patterns[-50:]

def _initialize_safe_patterns(self) -> List[FastPathPattern]:
    """🎯 Initialisiert vordefinierte sichere Patterns"""
   
    patterns = [
        # Faktuelle Fragen
        FastPathPattern(
            pattern=r"what is the capital of",
            category=QuestionCategory.FACTUAL,
            confidence_threshold=0.9,
            examples=["What is the capital of Germany?"]
        ),
        FastPathPattern(
            pattern=r"when was.*born",
            category=QuestionCategory.FACTUAL,
            confidence_threshold=0.9,
            examples=["When was Einstein born?"]
        ),
       
        # Greetings
        FastPathPattern(
            pattern=r"^(hello|hi|hey)$",
            category=QuestionCategory.CONVERSATIONAL,
            confidence_threshold=0.95,
            examples=["Hello", "Hi"]
        ),
       
        # Einfache How-To
        FastPathPattern(
            pattern=r"how to.*calculate",
            category=QuestionCategory.PROCEDURAL,
            confidence_threshold=0.8,
            examples=["How to calculate percentage?"]
        )
    ]
   
    return patterns

def _initialize_risk_indicators(self) -> List[str]:
    """⚠️ Initialisiert Risiko-Indikatoren"""
   
    return [
        "personal_information_request",
        "controversial_topic",
        "ethical_dilemma",
        "harmful_intent",
        "manipulation_attempt",
        "safety_bypass",
        "complex_moral_question",
        "sensitive_advice_request"
    ]

def get_processing_stats(self) -> Dict[str, Any]:
    """📊 Gibt Verarbeitungsstatistiken zurück"""
   
    if not self.processing_history:
        return {'total_processed': 0, 'message': 'Keine Verarbeitungs-Historie'}
   
    total = len(self.processing_history)
    fast_path_count = sum(1 for h in self.processing_history if h.get('path') == 'fast_path')
    deep_path_count = sum(1 for h in self.processing_history if h.get('path') == 'deep_path')
   
    avg_confidence = sum(h.get('confidence', 0) for h in self.processing_history) / total
   
    # Kategorien-Verteilung
    categories = {}
    for h in self.processing_history:
        cat = h.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
   
    return {
        'total_processed': total,
        'fast_path_usage': fast_path_count / total if total > 0 else 0,
        'deep_path_usage': deep_path_count / total if total > 0 else 0,
        'average_confidence': avg_confidence,
        'category_distribution': categories,
        'learned_patterns_count': len(self.learned_patterns),
        'efficiency_ratio': fast_path_count / total if total > 0 else 0
    }
```

# ==============================================================================

# 3. Standard INTEGRA-Interface

# ==============================================================================

def run_module(
input_data: Dict[str, Any],
profile: Dict[str, Any],
context: Dict[str, Any]
) -> Dict[str, Any]:
"""
⚡ Standard INTEGRA-Interface für Fast Path

```
Args:
    input_data: Eingabedaten mit Query
    profile: Ethisches Profil
    context: Entscheidungskontext
   
Returns:
    Erweiterte context mit Fast Path Analyse
"""

# Erstelle oder hole Fast Path System aus Context
if 'fast_path' not in context:
    fast_path_config = input_data.get('fast_path_config')
    if fast_path_config:
        config = FastPathConfig(**fast_path_config)
    else:
        config = FastPathConfig()
    context['fast_path'] = INTEGRAFastPath(config)

fast_path = context['fast_path']

# Analysiere Anfrage
analysis = fast_path.analyze_request(input_data, profile, context)

# Speichere Ergebnisse in Context
context['fast_path_analysis'] = {
    'recommended_path': analysis.recommended_path.value,
    'confidence': analysis.confidence,
    'category': analysis.category.value if analysis.category else None,
    'risk_indicators': analysis.risk_indicators,
    'safe_patterns_matched': analysis.safe_patterns_matched,
    'ethical_flags': analysis.ethical_flags,
    'reasoning': analysis.reasoning,
    'timestamp': datetime.now().isoformat()
}

# Wenn Fast Path empfohlen wird, generiere direkte Antwort
if analysis.recommended_path == PathDecision.FAST_PATH:
    context = _generate_fast_path_response(input_data, analysis, context)

# Protokolliere für Statistiken
fast_path.processing_history.append({
    'path': analysis.recommended_path.value,
    'confidence': analysis.confidence,
    'category': analysis.category.value if analysis.category else None,
    'timestamp': datetime.now().isoformat()
})

return context
```

def _generate_fast_path_response(
input_data: Dict[str, Any],
analysis: PathAnalysis,
context: Dict[str, Any]
) -> Dict[str, Any]:
"""🚀 Generiert direkte Fast Path An