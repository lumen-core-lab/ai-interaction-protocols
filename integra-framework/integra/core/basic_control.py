# -*- coding: utf-8 -*-
"""
Modulname: basic_control.py
Beschreibung: Basic Control Module für INTEGRA Light - Governance und Sicherheitskontrolle
Teil von: INTEGRA Light – Core
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Vollständig implementiert und Baukasten-kompatibel
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import uuid
import json
from pathlib import Path

# Standardisierte Imports
try:
    from integra.core import principles
    from integra.core import profiles
except ImportError:
    import principles
    import profiles


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class InterventionType(Enum):
    """Typen von Kontroll-Interventionen."""
    PASS = "pass"
    OVERRIDE = "override"
    SAFETY = "safety"
    ESCALATION = "escalation"
    TRANSPARENCY = "transparency"
    ERROR = "error"


class RiskLevel(Enum):
    """Risikostufen für Sicherheitsbewertung."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(Enum):
    """Benutzerrollen für Governance."""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SYSTEM = "system"
    
    @property
    def priority(self) -> int:
        """Gibt Priorität der Rolle zurück."""
        priorities = {
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3,
            UserRole.SYSTEM: 4
        }
        return priorities.get(self, 0)


@dataclass
class ControlAnalysis:
    """Container für Kontroll-Analyse-Ergebnisse."""
    safety_risk: float = 0.0
    safety_matches: List[str] = field(default_factory=list)
    override_detected: bool = False
    override_type: Optional[str] = None
    transparency_request: bool = False
    transparency_type: Optional[str] = None
    escalation_triggers: List[str] = field(default_factory=list)
    context_factors: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    
    def get_risk_level(self) -> RiskLevel:
        """Bestimmt Risikostufe basierend auf Safety Risk Score."""
        if self.safety_risk >= 0.8:
            return RiskLevel.CRITICAL
        elif self.safety_risk >= 0.6:
            return RiskLevel.HIGH
        elif self.safety_risk >= 0.4:
            return RiskLevel.MEDIUM
        elif self.safety_risk >= 0.2:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL


@dataclass
class InterventionRecord:
    """Aufzeichnung einer Kontroll-Intervention."""
    control_id: str
    intervention_type: InterventionType
    timestamp: datetime
    user_input_snippet: str
    analysis_summary: Dict[str, Any]
    action_taken: str
    user_role: UserRole = UserRole.USER
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "control_id": self.control_id,
            "intervention_type": self.intervention_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_input_snippet": self.user_input_snippet,
            "analysis_summary": self.analysis_summary,
            "action_taken": self.action_taken,
            "user_role": self.user_role.value
        }


# ============================================================================
# PATTERN DEFINITIONS
# ============================================================================

class ControlPatterns:
    """Zentrale Verwaltung von Kontroll-Patterns."""
    
    # Safety Keywords nach Kategorie
    SAFETY_KEYWORDS = {
        "physical_harm": [
            "harm", "hurt", "damage", "injure", "wound", "pain", "kill",
            "schaden", "verletzen", "schädigen", "wehtun", "töten"
        ],
        "violence": [
            "violence", "violent", "attack", "assault", "fight", "beat",
            "gewalt", "angriff", "kämpfen", "schlagen", "prügeln"
        ],
        "illegal": [
            "illegal", "criminal", "crime", "steal", "theft", "fraud",
            "illegal", "straftat", "kriminell", "stehlen", "betrug"
        ],
        "dangerous": [
            "dangerous", "toxic", "poison", "explosive", "weapon",
            "gefährlich", "giftig", "explosiv", "waffe"
        ],
        "self_harm": [
            "suicide", "self-harm", "kill myself", "hurt myself",
            "selbstmord", "selbstverletzung", "umbringen"
        ]
    }
    
    # Override Keywords
    OVERRIDE_KEYWORDS = {
        "stop": ["stop", "halt", "cancel", "abort", "stopp", "anhalten", "abbrechen"],
        "emergency": ["emergency", "urgent", "critical", "notfall", "dringend", "kritisch"],
        "manual": ["override", "manual", "intervention", "überschreiben", "manuell", "eingriff"],
        "exit": ["quit", "exit", "end", "terminate", "beenden", "verlassen", "terminieren"]
    }
    
    # Transparenz Patterns (Regex)
    TRANSPARENCY_PATTERNS = {
        "reasoning": [
            r"warum\s+(hast|haben|wurde|hat).*(entschied|entscheid|gesagt|geantwortet)",
            r"why\s+(did|have|was).*(decide|say|answer)"
        ],
        "process": [
            r"wie\s+(funktioniert|arbeitet).*(system|integra|du)",
            r"how\s+(do|does).*(work|function|decide)"
        ],
        "principles": [
            r"was\s+(sind|ist).*(prinzipien|grundlagen|principles)",
            r"what\s+(are|is).*(principles|foundations|based on)"
        ],
        "explanation": [
            r"(erkläre|erklären|explain).*(entscheidung|antwort|decision|answer)",
            r"(zeige|zeig).*(begründung|erklärung|grund)"
        ]
    }
    
    # Eskalations-Trigger
    ESCALATION_KEYWORDS = [
        "threat", "blackmail", "extortion", "kidnap", "ransom",
        "bedrohung", "erpressung", "entführung", "lösegeld",
        "terrorism", "bomb", "massacre", "genocide",
        "terrorismus", "bombe", "massaker", "völkermord"
    ]


# ============================================================================
# CONTROL ANALYZER
# ============================================================================

class ControlAnalyzer:
    """Analysiert Eingaben auf Kontroll-relevante Muster."""
    
    def __init__(self):
        """Initialisiert den Analyzer mit kompilierten Patterns."""
        self.patterns = ControlPatterns()
        self._compile_patterns()
        
    def _compile_patterns(self) -> None:
        """Kompiliert Regex-Patterns für Performance."""
        # Safety Patterns
        self.safety_patterns = {}
        for category, keywords in self.patterns.SAFETY_KEYWORDS.items():
            self.safety_patterns[category] = [
                re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE) 
                for word in keywords
            ]
            
        # Override Patterns
        self.override_patterns = {}
        for category, keywords in self.patterns.OVERRIDE_KEYWORDS.items():
            self.override_patterns[category] = [
                re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                for word in keywords
            ]
            
        # Transparency Patterns
        self.transparency_patterns = {}
        for category, patterns in self.patterns.TRANSPARENCY_PATTERNS.items():
            self.transparency_patterns[category] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]
            
        # Escalation Patterns
        self.escalation_patterns = [
            re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            for word in self.patterns.ESCALATION_KEYWORDS
        ]
        
    def analyze(self, user_input: str) -> ControlAnalysis:
        """
        Führt vollständige Kontroll-Analyse durch.
        
        Args:
            user_input: Zu analysierende Eingabe
            
        Returns:
            ControlAnalysis mit allen Analysedaten
        """
        if not user_input:
            return ControlAnalysis()
            
        # Safety Risk bewerten
        safety_matches = []
        safety_score = 0.0
        
        for category, patterns in self.safety_patterns.items():
            for pattern in patterns:
                if pattern.search(user_input):
                    safety_matches.append(category)
                    # Verschiedene Kategorien unterschiedlich gewichten
                    if category == "self_harm":
                        safety_score += 0.4
                    elif category in ["violence", "illegal"]:
                        safety_score += 0.3
                    else:
                        safety_score += 0.2
                    break
                    
        # Override Detection
        override_detected = False
        override_type = None
        
        for category, patterns in self.override_patterns.items():
            for pattern in patterns:
                if pattern.search(user_input):
                    override_detected = True
                    override_type = category
                    break
            if override_detected:
                break
                
        # Transparency Detection
        transparency_request = False
        transparency_type = None
        
        for category, patterns in self.transparency_patterns.items():
            for pattern in patterns:
                if pattern.search(user_input):
                    transparency_request = True
                    transparency_type = category
                    break
            if transparency_request:
                break
                
        # Escalation Detection
        escalation_triggers = []
        for pattern in self.escalation_patterns:
            match = pattern.search(user_input)
            if match:
                escalation_triggers.append(match.group())
                
        # Context Factors
        context_factors = self._analyze_context(user_input)
        
        # Confidence berechnen
        confidence = self._calculate_confidence(
            safety_score, override_detected, transparency_request, 
            len(escalation_triggers), context_factors
        )
        
        return ControlAnalysis(
            safety_risk=min(1.0, safety_score),
            safety_matches=list(set(safety_matches)),
            override_detected=override_detected,
            override_type=override_type,
            transparency_request=transparency_request,
            transparency_type=transparency_type,
            escalation_triggers=escalation_triggers,
            context_factors=context_factors,
            confidence=confidence
        )
        
    def _analyze_context(self, text: str) -> Dict[str, Any]:
        """Analysiert Kontext-Faktoren."""
        return {
            "length": len(text),
            "has_question": "?" in text,
            "has_exclamation": "!" in text,
            "caps_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            "urgency_indicators": any(
                word in text.lower() 
                for word in ["urgent", "immediate", "now", "quickly", "dringend", "sofort", "jetzt"]
            ),
            "polite_indicators": any(
                word in text.lower()
                for word in ["please", "bitte", "thank", "danke", "sorry", "entschuldigung"]
            )
        }
        
    def _calculate_confidence(self, safety_score: float, override: bool,
                            transparency: bool, escalation_count: int,
                            context: Dict[str, Any]) -> float:
        """Berechnet Analyse-Konfidenz."""
        confidence = 0.8
        
        # Klare Signale erhöhen Konfidenz
        if safety_score > 0.5 or escalation_count > 0:
            confidence += 0.15
        if override:
            confidence += 0.1
        if transparency:
            confidence += 0.05
            
        # Kontext-Faktoren
        if context.get("caps_ratio", 0) > 0.5:  # Viel Großschreibung
            confidence -= 0.05
        if context.get("polite_indicators"):
            confidence += 0.05
            
        return max(0.3, min(0.99, confidence))


# ============================================================================
# GOVERNANCE SYSTEM
# ============================================================================

class GovernanceSystem:
    """Verwaltet Berechtigungen und Rollensystem."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisiert das Governance System."""
        self.config = config or {}
        
        # Rollen-Berechtigungen
        self.permissions = {
            UserRole.USER: {
                "can_override": False,
                "can_emergency_stop": False,
                "can_view_logs": False,
                "can_change_config": False
            },
            UserRole.MODERATOR: {
                "can_override": True,
                "can_emergency_stop": False,
                "can_view_logs": True,
                "can_change_config": False
            },
            UserRole.ADMIN: {
                "can_override": True,
                "can_emergency_stop": True,
                "can_view_logs": True,
                "can_change_config": True
            },
            UserRole.SYSTEM: {
                "can_override": True,
                "can_emergency_stop": True,
                "can_view_logs": True,
                "can_change_config": True
            }
        }
        
    def validate_override_request(self, user_role: UserRole, 
                                override_type: str,
                                context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validiert eine Override-Anfrage.
        
        Args:
            user_role: Rolle des Benutzers
            override_type: Art des Overrides
            context: Zusätzlicher Kontext
            
        Returns:
            Tuple aus (ist_erlaubt, Begründung)
        """
        # Berechtigungen prüfen
        permissions = self.permissions.get(user_role, {})
        
        if override_type == "emergency" and not permissions.get("can_emergency_stop", False):
            return False, f"Rolle {user_role.value} hat keine Berechtigung für Emergency Stop"
            
        if not permissions.get("can_override", False):
            return False, f"Rolle {user_role.value} hat keine Override-Berechtigung"
            
        # Zusätzliche Validierung basierend auf Kontext
        if override_type == "emergency":
            # Emergency immer erlauben wenn Berechtigung vorhanden
            return True, "Emergency Override autorisiert"
            
        # Standard Override
        return True, f"Override autorisiert für {user_role.value}"
        
    def check_permission(self, user_role: UserRole, permission: str) -> bool:
        """Prüft eine spezifische Berechtigung."""
        return self.permissions.get(user_role, {}).get(permission, False)


# ============================================================================
# BASIC CONTROL SYSTEM
# ============================================================================

class BasicControl:
    """
    Hauptklasse für Governance und Sicherheitskontrolle.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert das Control System.
        
        Args:
            config: Konfiguration für Kontrollparameter
        """
        self.config = self._get_default_config()
        if config:
            self.config.update(config)
            
        self.analyzer = ControlAnalyzer()
        self.governance = GovernanceSystem(self.config)
        
        # System State
        self.safe_mode = False
        self.intervention_history: List[InterventionRecord] = []
        self.blocked_count = 0
        self.transparency_count = 0
        
        # Audit Integration (wenn verfügbar)
        self._audit_available = False
        self._check_audit_availability()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Standard-Konfiguration."""
        return {
            "safety_threshold": 0.3,
            "escalation_threshold": 0.1,
            "transparency_enabled": True,
            "logging_enabled": True,
            "max_history": 100,
            "safe_mode_on_escalation": True,
            "audit_integration": True
        }
        
    def _check_audit_availability(self) -> None:
        """Prüft ob Audit-Modul verfügbar ist."""
        if not self.config.get("audit_integration", True):
            return
            
        try:
            from integra.advanced import mini_audit
            self._audit_available = True
        except ImportError:
            self._audit_available = False
            
    def process_control(self, user_input: str,
                       user_role: UserRole,
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hauptmethode für Kontrollprüfung.
        
        Args:
            user_input: Benutzereingabe
            user_role: Rolle des Benutzers
            context: Aktueller Kontext
            
        Returns:
            Kontroll-Entscheidung
        """
        # Safe Mode Check
        if self.safe_mode:
            return self._create_safe_mode_response()
            
        # Control ID generieren
        control_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        
        # Analyse durchführen
        analysis = self.analyzer.analyze(user_input)
        
        # Prioritätsbasierte Prüfung
        
        # 1. Eskalation (höchste Priorität)
        if analysis.escalation_triggers:
            return self._handle_escalation(
                user_input, analysis, user_role, control_id, timestamp
            )
            
        # 2. Override
        if analysis.override_detected:
            return self._handle_override(
                user_input, analysis, user_role, control_id, timestamp
            )
            
        # 3. Safety Risk
        risk_level = analysis.get_risk_level()
        if risk_level.value in ["high", "critical"]:
            return self._handle_safety_risk(
                user_input, analysis, user_role, control_id, timestamp
            )
            
        # 4. Transparency
        if analysis.transparency_request and self.config["transparency_enabled"]:
            return self._handle_transparency(
                user_input, analysis, user_role, control_id, timestamp
            )
            
        # 5. Pass (keine Intervention)
        return self._create_response(
            InterventionType.PASS,
            "Keine Kontrollaktion erforderlich",
            {
                "control_id": control_id,
                "analysis_summary": {
                    "risk_level": risk_level.value,
                    "confidence": analysis.confidence
                }
            }
        )
        
    def _handle_escalation(self, user_input: str, analysis: ControlAnalysis,
                          user_role: UserRole, control_id: str, 
                          timestamp: datetime) -> Dict[str, Any]:
        """Behandelt Eskalationsfälle."""
        # In Safe Mode wechseln wenn konfiguriert
        if self.config.get("safe_mode_on_escalation", True):
            self.safe_mode = True
            
        # Intervention aufzeichnen
        self._record_intervention(
            InterventionType.ESCALATION,
            user_input, analysis, user_role, 
            control_id, timestamp,
            "System in Safe Mode - Menschliche Intervention erforderlich"
        )
        
        # Audit wenn verfügbar
        self._audit_action("escalation", {
            "control_id": control_id,
            "triggers": analysis.escalation_triggers,
            "user_role": user_role.value
        })
        
        return self._create_response(
            InterventionType.ESCALATION,
            "KRITISCH: Schwerwiegender Sicherheitsvorfall. System gesperrt.",
            {
                "control_id": control_id,
                "escalation_triggers": analysis.escalation_triggers,
                "safe_mode_activated": self.safe_mode,
                "required_action": "human_intervention",
                "severity": "critical"
            }
        )
        
    def _handle_override(self, user_input: str, analysis: ControlAnalysis,
                        user_role: UserRole, control_id: str,
                        timestamp: datetime) -> Dict[str, Any]:
        """Behandelt Override-Anfragen."""
        # Berechtigung prüfen
        allowed, reason = self.governance.validate_override_request(
            user_role, analysis.override_type or "general", {"input": user_input}
        )
        
        if not allowed:
            # Override verweigert
            self._record_intervention(
                InterventionType.OVERRIDE,
                user_input, analysis, user_role,
                control_id, timestamp,
                f"Override verweigert: {reason}"
            )
            
            return self._create_response(
                InterventionType.OVERRIDE,
                f"Override-Anfrage abgelehnt: {reason}",
                {
                    "control_id": control_id,
                    "override_type": analysis.override_type,
                    "authorized": False,
                    "reason": reason
                }
            )
            
        # Override erlaubt
        action_taken = "Override autorisiert und ausgeführt"
        
        # Bei Emergency Stop
        if analysis.override_type == "emergency":
            self.trigger_emergency_stop(user_role, "User-initiated emergency stop")
            action_taken = "Emergency Stop ausgeführt - System angehalten"
            
        self._record_intervention(
            InterventionType.OVERRIDE,
            user_input, analysis, user_role,
            control_id, timestamp,
            action_taken
        )
        
        return self._create_response(
            InterventionType.OVERRIDE,
            action_taken,
            {
                "control_id": control_id,
                "override_type": analysis.override_type,
                "authorized": True,
                "user_role": user_role.value,
                "safe_mode": self.safe_mode
            }
        )
        
    def _handle_safety_risk(self, user_input: str, analysis: ControlAnalysis,
                           user_role: UserRole, control_id: str,
                           timestamp: datetime) -> Dict[str, Any]:
        """Behandelt Sicherheitsrisiken."""
        risk_level = analysis.get_risk_level()
        
        # Aktion basierend auf Risikostufe
        if risk_level == RiskLevel.CRITICAL:
            action = "Anfrage blockiert - Kritisches Risiko"
            recommendation = "Keine Ausführung möglich"
        elif risk_level == RiskLevel.HIGH:
            action = "Anfrage erfordert Überprüfung"
            recommendation = "Vorsichtige Behandlung mit Einschränkungen"
        else:
            action = "Erhöhte Aufmerksamkeit erforderlich"
            recommendation = "Mit Sicherheitshinweisen fortfahren"
            
        self._record_intervention(
            InterventionType.SAFETY,
            user_input, analysis, user_role,
            control_id, timestamp,
            action
        )
        
        self.blocked_count += 1
        
        return self._create_response(
            InterventionType.SAFETY,
            action,
            {
                "control_id": control_id,
                "risk_level": risk_level.value,
                "risk_score": analysis.safety_risk,
                "safety_categories": analysis.safety_matches,
                "recommendation": recommendation
            }
        )
        
    def _handle_transparency(self, user_input: str, analysis: ControlAnalysis,
                           user_role: UserRole, control_id: str,
                           timestamp: datetime) -> Dict[str, Any]:
        """Behandelt Transparenz-Anfragen."""
        # Erklärung basierend auf Typ generieren
        explanations = {
            "reasoning": (
                "Meine Entscheidungen basieren auf den INTEGRA ALIGN-Prinzipien:\n"
                "- Awareness: Bewusstsein für Kontext und Auswirkungen\n"
                "- Learning: Kontinuierliche Verbesserung\n"
                "- Integrity: Ehrlichkeit und Konsistenz\n"
                "- Governance: Kontrollierbarkeit und Regelkonformität\n"
                "- Nurturing: Fürsorge und Unterstützung"
            ),
            "process": (
                "Das System analysiert jede Anfrage in mehreren Schritten:\n"
                "1. Sicherheitsprüfung auf potenzielle Risiken\n"
                "2. Ethische Bewertung nach ALIGN-Prinzipien\n"
                "3. Kontextanalyse und Anpassung\n"
                "4. Auswahl des angemessenen Antwortpfads"
            ),
            "principles": (
                "INTEGRA ist ein ethisches KI-Framework mit folgenden Zielen:\n"
                "- Verantwortungsvolle Entscheidungsfindung\n"
                "- Transparenz und Nachvollziehbarkeit\n"
                "- Schutz vor schädlichen Ausgaben\n"
                "- Förderung positiver Interaktionen"
            ),
            "explanation": (
                "Gerne erkläre ich meine Funktionsweise:\n"
                "Ich nutze ein mehrstufiges Kontrollsystem, das Sicherheit,\n"
                "Ethik und Transparenz in jeder Entscheidung berücksichtigt."
            )
        }
        
        explanation = explanations.get(
            analysis.transparency_type or "explanation",
            explanations["explanation"]
        )
        
        self._record_intervention(
            InterventionType.TRANSPARENCY,
            user_input, analysis, user_role,
            control_id, timestamp,
            "Transparenz-Information bereitgestellt"
        )
        
        self.transparency_count += 1
        
        return self._create_response(
            InterventionType.TRANSPARENCY,
            explanation,
            {
                "control_id": control_id,
                "transparency_type": analysis.transparency_type,
                "additional_resources": {
                    "documentation": "https://integra-docs.example.com",
                    "principles": list(principles.ALIGN_KEYS),
                    "version": "INTEGRA Light 2.0"
                }
            }
        )
        
    def trigger_emergency_stop(self, initiated_by: UserRole, reason: str) -> None:
        """
        Führt einen Emergency Stop aus.
        
        Args:
            initiated_by: Wer den Stop ausgelöst hat
            reason: Grund für den Stop
        """
        self.safe_mode = True
        
        # Audit
        self._audit_action("emergency_stop", {
            "initiated_by": initiated_by.value,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        # Hier könnten weitere Shutdown-Prozesse stehen
        # z.B. Benachrichtigungen, Prozess-Stops, etc.
        
    def _create_safe_mode_response(self) -> Dict[str, Any]:
        """Erstellt Response wenn System im Safe Mode ist."""
        return self._create_response(
            InterventionType.ERROR,
            "System ist im Safe Mode. Nur autorisierte Aktionen möglich.",
            {
                "safe_mode": True,
                "allowed_actions": ["status", "unlock_with_admin"],
                "contact": "admin@integra-system.com"
            }
        )
        
    def _create_response(self, intervention_type: InterventionType,
                        message: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt standardisierte Response."""
        return {
            "action": intervention_type.value,
            "message": message,
            "path": "control" if intervention_type != InterventionType.PASS else "continue",
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
            "controller": "basic_control_v2.0"
        }
        
    def _record_intervention(self, intervention_type: InterventionType,
                           user_input: str, analysis: ControlAnalysis,
                           user_role: UserRole, control_id: str,
                           timestamp: datetime, action_taken: str) -> None:
        """Zeichnet Intervention auf."""
        if not self.config.get("logging_enabled", True):
            return
            
        record = InterventionRecord(
            control_id=control_id,
            intervention_type=intervention_type,
            timestamp=timestamp,
            user_input_snippet=user_input[:100] + "..." if len(user_input) > 100 else user_input,
            analysis_summary={
                "risk_level": analysis.get_risk_level().value,
                "safety_risk": analysis.safety_risk,
                "confidence": analysis.confidence
            },
            action_taken=action_taken,
            user_role=user_role
        )
        
        self.intervention_history.append(record)
        
        # History begrenzen
        if len(self.intervention_history) > self.config.get("max_history", 100):
            self.intervention_history.pop(0)
            
    def _audit_action(self, action: str, details: Dict[str, Any]) -> None:
        """Sendet Aktion an Audit-System wenn verfügbar."""
        if not self._audit_available:
            return
            
        try:
            from integra.advanced import mini_audit
            audit_input = {
                "action": "log_control_action",
                "control_action": action,
                "details": details
            }
            # Dummy context/profile für Audit
            mini_audit.run_module(audit_input, {}, {})
        except Exception:
            pass  # Audit-Fehler dürfen Control nicht stören
            
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken zurück."""
        intervention_counts = {}
        for record in self.intervention_history:
            key = record.intervention_type.value
            intervention_counts[key] = intervention_counts.get(key, 0) + 1
            
        return {
            "total_interventions": len(self.intervention_history),
            "intervention_breakdown": intervention_counts,
            "blocked_count": self.blocked_count,
            "transparency_count": self.transparency_count,
            "safe_mode": self.safe_mode,
            "audit_available": self._audit_available,
            "config": self.config.copy()
        }


# ============================================================================
# MODULE INTERFACE (BAUKASTEN)
# ============================================================================

# Globale Instanz
_control = None

def get_control() -> BasicControl:
    """Lazy-Loading der Control-Instanz."""
    global _control
    if _control is None:
        _control = BasicControl()
    return _control


def run_module(input_data: Dict[str, Any], 
               profile: Dict[str, float], 
               context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hauptfunktion für die Baukasten-Integration.
    
    Args:
        input_data: Dictionary mit Eingabedaten
            - text: Zu prüfende Eingabe (required)
            - user_role: Rolle des Benutzers (optional, default: "user")
            - config: Control-Konfiguration (optional)
        profile: Aktuelles ethisches Profil (wird hier nicht direkt genutzt)
        context: Laufender Kontext (wird erweitert)
        
    Returns:
        Erweiterter Kontext mit Ergebnis in context["basic_control_result"]
    """
    try:
        # Input extrahieren
        text = input_data.get("text", "")
        if not text:
            raise ValueError("Kein Text in input_data gefunden")
            
        # User Role extrahieren
        role_str = input_data.get("user_role", "user")
        try:
            user_role = UserRole(role_str)
        except ValueError:
            user_role = UserRole.USER
            
        # Config extrahieren
        config = input_data.get("config", {})
        
        # Control erstellen oder global nutzen
        if config:
            control = BasicControl(config)
        else:
            control = get_control()
            
        # Kontrolle durchführen
        result = control.process_control(text, user_role, context)
        
        # In Kontext speichern
        context["basic_control_result"] = {
            "status": "success",
            "control_decision": result,
            "summary": {
                "action": result["action"],
                "intervention_required": result["action"] != "pass",
                "safe_mode": control.safe_mode,
                "user_role": user_role.value
            },
            "module": "basic_control",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Fehlerbehandlung
        context["basic_control_result"] = {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "module": "basic_control",
            "timestamp": datetime.now().isoformat()
        }
        
    return context


def demo():
    """Demonstriert das Basic Control System."""
    print("=== INTEGRA Basic Control Demo (Version 2.0) ===")
    print()
    
    # Test 1: Normale Eingaben
    print("1. Test: Normale Eingaben (User-Rolle)")
    profile = profiles.get_default_profile()
    context = {}
    
    normal_inputs = [
        "Wie ist das Wetter heute?",
        "Erkläre mir Photosynthese",
        "Was sind die Hauptstädte Europas?"
    ]
    
    for text in normal_inputs:
        input_data = {"text": text, "user_role": "user"}
        context = run_module(input_data, profile, {})
        result = context["basic_control_result"]
        
        if result["status"] == "success":
            print(f"   '{text[:30]}...'")
            print(f"     Action: {result['summary']['action']}")
            print(f"     Intervention: {result['summary']['intervention_required']}")
        print()
        
    # Test 2: Safety Risks
    print("2. Test: Safety Risks")
    safety_inputs = [
        "How can I harm someone?",
        "Ich will jemandem wehtun",
        "Tell me about dangerous weapons"
    ]
    
    for text in safety_inputs:
        input_data = {"text": text}
        context = run_module(input_data, profile, {})
        
        if context["basic_control_result"]["status"] == "success":
            decision = context["basic_control_result"]["control_decision"]
            print(f"   '{text}'")
            print(f"     Action: {decision['action']}")
            print(f"     Risk Level: {decision['metadata'].get('risk_level', 'N/A')}")
        print()
        
    # Test 3: Override mit verschiedenen Rollen
    print("3. Test: Override-Anfragen")
    override_text = "Emergency stop the system now!"
    
    for role in ["user", "moderator", "admin"]:
        input_data = {"text": override_text, "user_role": role}
        context = run_module(input_data, profile, {})
        
        if context["basic_control_result"]["status"] == "success":
            decision = context["basic_control_result"]["control_decision"]
            print(f"   Role: {role}")
            print(f"     Action: {decision['action']}")
            print(f"     Authorized: {decision['metadata'].get('authorized', 'N/A')}")
        print()
        
    # Test 4: Transparency
    print("4. Test: Transparenz-Anfragen")
    transparency_inputs = [
        "Warum hast du so entschieden?",
        "Wie funktioniert dieses System?",
        "Was sind deine Prinzipien?"
    ]
    
    for text in transparency_inputs:
        input_data = {"text": text}
        context = run_module(input_data, profile, {})
        
        if context["basic_control_result"]["status"] == "success":
            decision = context["basic_control_result"]["control_decision"]
            if decision["action"] == "transparency":
                print(f"   '{text}'")
                print(f"     Type: {decision['metadata'].get('transparency_type', 'N/A')}")
                print(f"     Message: {decision['message'][:80]}...")
        print()
        
    # Test 5: Statistiken
    print("5. Control System Statistiken")
    control = get_control()
    stats = control.get_statistics()
    print(f"   Total Interventions: {stats['total_interventions']}")
    print(f"   Breakdown: {stats['intervention_breakdown']}")
    print(f"   Safe Mode: {stats['safe_mode']}")
    print(f"   Audit Available: {stats['audit_available']}")
    
    print("\n=== Demo abgeschlossen ===")


if __name__ == "__main__":
    demo()