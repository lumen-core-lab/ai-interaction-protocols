# -*- coding: utf-8 -*-

"""
versions/light.py

🌟 INTEGRA LIGHT - Vollständiges ethisches KI-System 🌟

Der komplette INTEGRA Light Orchestrator - bringt alle Module zusammen:

- Intelligente Fast/Deep Path Routing
- Vollständige ALIGN-Prinzipien Integration
- Menschliche Kontrolle und Governance
- Adaptive Lernfähigkeit
- Audit-Trail und Transparency
- Plug-and-Play für jede Anwendung

Design-Philosophie: Ethische KI für alle - einfach, sicher, transparent

Version: INTEGRA Light 1.0 - Production Ready
"""

import sys
import os
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

# INTEGRA Module Imports
try:
    # Core Modules
    from core.align_principles import run_module as run_align_principles
    from core.decision_engine import run_module as run_decision_engine
    from core.profile_manager import run_module as run_profile_manager

    # Ethics Modules
    from modules.ethics.basic_ethics import run_module as run_basic_ethics

    # Learning Modules 
    from modules.learning.mini_learner import run_module as run_mini_learner

    # Audit Modules
    from modules.audit.mini_audit import run_module as run_mini_audit

    # Governance Modules
    from modules.governance.basic_control import run_module as run_basic_control

    # Reasoning Modules
    from modules.reasoning.fast_path import run_module as run_fast_path
    from modules.reasoning.deep_path import run_module as run_deep_path

except ImportError as e:
    print(f"⚠️ Import Warning: {e}")
    print("💡 For standalone usage, implement mock modules or adjust import paths")
    
    # Mock functions for standalone usage
    def run_align_principles(input_data, profile, context):
        return {'align_score': 0.7, 'align_details': {'integrity': 0.8, 'governance': 0.7}}
    
    def run_decision_engine(input_data, profile, context):
        return {'decision_result': {'response': f"Mock response for: {input_data.get('query', '')}"}}
    
    def run_profile_manager(input_data, profile, context):
        return {'ethical_profile_loaded': True}
    
    def run_basic_ethics(input_data, profile, context):
        return {'basic_ethics_result': {'status': 'acceptable'}}
    
    def run_mini_learner(input_data, profile, context):
        return {'learning_result': {'patterns_updated': True}}
    
    def run_mini_audit(input_data, profile, context):
        return {'audit_result': {'logged': True}}
    
    def run_basic_control(input_data, profile, context):
        return {'basic_control_result': {'success': True, 'message': 'Control check passed'}}
    
    def run_fast_path(input_data, profile, context):
        return {
            'fast_path_analysis': {
                'recommended_path': 'fast_path',
                'confidence': 0.8,
                'response': f"Fast response for: {input_data.get('query', '')}"
            },
            'decision': {
                'response': f"Fast response for: {input_data.get('query', '')}",
                'path_taken': 'fast_path'
            }
        }
    
    def run_deep_path(input_data, profile, context):
        return {
            'deep_path_analysis': {
                'stakeholder_impact': 'positive',
                'alternatives_considered': 3,
                'response': f"Deep response for: {input_data.get('query', '')}"
            },
            'decision': {
                'response': f"Deep response for: {input_data.get('query', '')}",
                'path_taken': 'deep_path'
            }
        }

# ==============================================================================
# 1. System-Konfiguration und Datenstrukturen
# ==============================================================================

class ProcessingMode(Enum):
    """🚦 Verfügbare Verarbeitungs-Modi"""
    AUTO = "auto"           # Automatische Fast/Deep Path Entscheidung
    FAST_ONLY = "fast_only" # Nur Fast Path (maximale Effizienz)
    DEEP_ONLY = "deep_only" # Nur Deep Path (maximale Analyse)
    HYBRID = "hybrid"       # Intelligente Kombination

class SecurityLevel(Enum):
    """🔒 Sicherheits-Level"""
    PERMISSIVE = "permissive"   # Liberale Einstellungen
    BALANCED = "balanced"       # Ausgewogene Sicherheit
    STRICT = "strict"           # Strenge Sicherheit
    PARANOID = "paranoid"       # Maximale Sicherheit

@dataclass
class INTEGRALightConfig:
    """⚙️ Vollständige Konfiguration für INTEGRA Light"""
    
    # System-Grundeinstellungen
    system_name: str = "INTEGRA Light"
    version: str = "1.0"
    processing_mode: ProcessingMode = ProcessingMode.AUTO
    security_level: SecurityLevel = SecurityLevel.BALANCED

    # Ethische Profil-Einstellungen
    align_weights: Dict[str, float] = field(default_factory=lambda: {
        'awareness': 0.8,
        'learning': 0.7,
        'integrity': 1.0,
        'governance': 0.9,
        'nurturing': 0.9
    })

    # Fast Path Konfiguration
    fast_path_enabled: bool = True
    fast_path_confidence_threshold: float = 0.8
    fast_path_max_risk: float = 0.2

    # Deep Path Konfiguration
    deep_path_enabled: bool = True
    deep_path_stakeholder_analysis: bool = True
    deep_path_generate_alternatives: bool = True
    deep_path_min_acceptable_score: float = 0.6

    # Governance und Kontrolle
    governance_enabled: bool = True
    require_justification_for_overrides: bool = True
    validate_override_safety: bool = True
    auto_escalate_critical: bool = True
    emergency_stop_enabled: bool = True

    # Lernen und Anpassung
    learning_enabled: bool = True
    pattern_learning: bool = True
    adaptive_weights: bool = True
    feedback_sensitivity: float = 0.02

    # Audit und Transparenz
    audit_enabled: bool = True
    log_all_decisions: bool = True
    provide_explanations: bool = True
    detailed_reasoning: bool = True

    # Erweiterte Einstellungen
    domain_specific_rules: Dict[str, Any] = field(default_factory=dict)
    custom_stakeholder_weights: Dict[str, float] = field(default_factory=dict)
    experimental_features: List[str] = field(default_factory=list)

@dataclass
class ProcessingResult:
    """📊 Vollständiges Verarbeitungs-Ergebnis"""
    # Haupt-Ergebnis
    response: str = ""
    confidence: float = 0.0
    processing_path: str = ""

    # Ethische Analyse
    align_score: float = 0.0
    align_details: Dict[str, float] = field(default_factory=dict)
    align_violations: List[str] = field(default_factory=list)
    ethical_quality: str = ""

    # System-Informationen
    modules_used: List[str] = field(default_factory=list)
    processing_time: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Governance und Kontrolle
    governance_actions: List[str] = field(default_factory=list)
    escalation_triggered: bool = False
    user_override_applied: bool = False

    # Transparenz und Erklärung
    reasoning_provided: bool = False
    alternatives_available: bool = False
    risk_mitigation: List[str] = field(default_factory=list)

    # Metadaten
    session_id: str = ""
    user_id: str = ""
    request_id: str = ""

# ==============================================================================
# 2. Hauptklasse - INTEGRA Light System
# ==============================================================================

class INTEGRALight:
    """
    🌟 INTEGRA Light - Vollständiges ethisches KI-System

    Ein produktionsreifes, ethisches KI-System das alle INTEGRA-Module
    intelligent orchestriert:

    🔍 Intelligente Fast/Deep Path Entscheidung
    🎯 Vollständige ALIGN-Prinzipien (Awareness, Learning, Integrity, Governance, Nurturing)
    🛡️ Menschliche Kontrolle und Override-Möglichkeiten
    🧠 Adaptive Lernfähigkeit aus Feedback
    📊 Vollständige Audit-Trails und Transparenz
    🔧 Plug-and-Play Integration

    Ideal für: Chatbots, Empfehlungssysteme, Entscheidungsunterstützung,
    Content-Moderation, Smart Home, E-Commerce, und alle KI-Anwendungen
    die ethische Standards benötigen.
    """

    def __init__(self, config: Optional[INTEGRALightConfig] = None, domain: str = "general"):
        """
        Initialisiert INTEGRA Light System
       
        Args:
            config: Vollständige System-Konfiguration
            domain: Anwendungsdomäne (z.B. "healthcare", "finance", "ecommerce")
        """
        self.config = config or INTEGRALightConfig()
        self.domain = domain
        self.session_data = {}
        self.processing_history: List[Dict[str, Any]] = []
        self.system_stats = {
            'total_requests': 0,
            'fast_path_usage': 0,
            'deep_path_usage': 0,
            'governance_interventions': 0,
            'escalations': 0,
            'user_overrides': 0,
            'learning_updates': 0
        }
       
        # System-Initialisierung
        self._initialize_system()
       
        print(f"🌟 {self.config.system_name} v{self.config.version} initialisiert")
        print(f"🎯 Domain: {domain}")
        print(f"🚦 Modus: {self.config.processing_mode.value}")
        print(f"🔒 Sicherheit: {self.config.security_level.value}")
        print(f"⚡ Fast Path: {'Aktiv' if self.config.fast_path_enabled else 'Deaktiviert'}")
        print(f"🧠 Deep Path: {'Aktiv' if self.config.deep_path_enabled else 'Deaktiviert'}")
        print(f"🛡️ Governance: {'Aktiv' if self.config.governance_enabled else 'Deaktiviert'}")
        print(f"📚 Lernen: {'Aktiv' if self.config.learning_enabled else 'Deaktiviert'}")

    def process_request(
        self,
        query: str,
        user_id: str = "anonymous",
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> ProcessingResult:
        """
        🎯 Hauptfunktion: Verarbeitet ethische KI-Anfrage
       
        Args:
            query: Die zu verarbeitende Anfrage
            user_id: Eindeutige Nutzer-ID
            context: Zusätzlicher Kontext (optional)
            session_id: Session-ID für zusammenhängende Anfragen
           
        Returns:
            ProcessingResult mit vollständigen Ergebnissen
        """
       
        start_time = datetime.now()
        request_id = f"req_{int(start_time.timestamp() * 1000)}"
        session_id = session_id or f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}"
       
        print(f"\n🚀 Verarbeite Anfrage [{request_id}]: \"{query[:60]}...\"")
       
        # Initialisiere Verarbeitungs-Kontext
        processing_context = self._initialize_processing_context(
            query, user_id, context or {}, session_id, request_id
        )
       
        try:
            # Schritt 1: Ethisches Profil laden/erstellen
            processing_context = self._load_ethical_profile(processing_context)
           
            # Schritt 2: Basis ethische Bewertung
            processing_context = self._perform_basic_ethics_check(processing_context)
           
            # Schritt 3: Governance Pre-Check (Notfall-Stops, etc.)
            processing_context = self._perform_governance_precheck(processing_context)
           
            # Schritt 4: Intelligente Path-Entscheidung
            processing_context = self._determine_processing_path(processing_context)
           
            # Schritt 5: Path-spezifische Verarbeitung
            processing_context = self._execute_processing_path(processing_context)
           
            # Schritt 6: Finale ethische Validierung
            processing_context = self._perform_final_ethics_validation(processing_context)
           
            # Schritt 7: Governance Post-Check (Überrides, Eskalationen)
            processing_context = self._perform_governance_postcheck(processing_context)
           
            # Schritt 8: Adaptives Lernen (falls aktiviert)
            if self.config.learning_enabled:
                processing_context = self._perform_adaptive_learning(processing_context)
           
            # Schritt 9: Audit und Logging
            if self.config.audit_enabled:
                processing_context = self._perform_audit_logging(processing_context)
           
            # Schritt 10: Ergebnis zusammenstellen
            result = self._compile_final_result(processing_context, start_time)
           
            # Statistiken aktualisieren
            self._update_system_stats(processing_context, result)
           
            print(f"✅ Anfrage erfolgreich verarbeitet (Path: {result.processing_path}, Score: {result.align_score:.2f})")
           
            return result
           
        except Exception as e:
            print(f"❌ Fehler bei Verarbeitung: {e}")
           
            # Fallback-Behandlung
            return self._create_error_result(str(e), request_id, session_id, user_id, start_time)

    def override_decision(
        self,
        request_id: str,
        new_response: str,
        justification: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        🔄 Übersteuert eine vorherige Entscheidung
       
        Args:
            request_id: ID der ursprünglichen Anfrage
            new_response: Neue gewünschte Antwort
            justification: Begründung für Override
            user_id: Nutzer der das Override durchführt
           
        Returns:
            Override-Ergebnis mit Sicherheits-Validierung
        """
       
        override_input = {
            'override_decision': new_response,
            'justification': justification,
            'user_id': user_id,
            'original_request_id': request_id
        }
       
        # Erstelle minimalen Kontext für Governance-Check
        context = {
            'decision': {'response': new_response},
            'original_request_id': request_id
        }
       
        # Führe Governance-Check für Override durch
        if self.config.governance_enabled:
            try:
                result = run_basic_control(override_input, {}, context)
               
                self.system_stats['user_overrides'] += 1
               
                return {
                    'success': result.get('basic_control_result', {}).get('success', False),
                    'message': result.get('basic_control_result', {}).get('message', 'Override processed'),
                    'override_applied': context.get('decision', {}).get('overridden_by') == user_id,
                    'timestamp': datetime.now().isoformat()
                }
               
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Governance module error: {str(e)}',
                    'override_applied': False
                }
        else:
            return {
                'success': True,
                'message': 'Override applied (governance disabled)',
                'override_applied': True,
                'warning': 'No safety validation performed'
            }

    def escalate_request(
        self,
        request_id: str,
        reason: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        🚨 Eskaliert eine Anfrage zur menschlichen Überprüfung
       
        Args:
            request_id: ID der ursprünglichen Anfrage
            reason: Grund für Eskalation
            user_id: Nutzer der eskaliert
           
        Returns:
            Eskalations-Ergebnis
        """
       
        escalation_input = {
            'escalate': True,
            'escalation_reason': reason,
            'user_id': user_id,
            'original_request_id': request_id
        }
       
        context = {'decision': {'response': 'Pending escalation review'}}
       
        if self.config.governance_enabled:
            try:
                result = run_basic_control(escalation_input, {}, context)
               
                self.system_stats['escalations'] += 1
               
                return {
                    'success': True,
                    'message': f'Request escalated: {reason}',
                    'escalation_id': f"esc_{request_id}_{int(datetime.now().timestamp())}",
                    'requires_human_review': True,
                    'timestamp': datetime.now().isoformat()
                }
               
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Governance module error: {str(e)}'
                }
        else:
            return {
                'success': False,
                'message': 'Escalation not available (governance disabled)'
            }

    def emergency_stop(self, user_id: str = "system") -> Dict[str, Any]:
        """
        🛑 Aktiviert Emergency Stop - stoppt alle KI-Operationen
       
        Args:
            user_id: Nutzer der Emergency Stop aktiviert
           
        Returns:
            Emergency Stop Status
        """
       
        if not self.config.emergency_stop_enabled:
            return {
                'success': False,
                'message': 'Emergency stop not enabled in configuration'
            }
       
        emergency_input = {'emergency_stop': True, 'user_id': user_id}
        context = {}
       
        try:
            result = run_basic_control(emergency_input, {}, context)
           
            # System-weite Emergency-Markierung
            self.session_data['emergency_stop_active'] = True
            self.session_data['emergency_stop_by'] = user_id
            self.session_data['emergency_stop_time'] = datetime.now().isoformat()
           
            return {
                'success': True,
                'message': 'Emergency stop activated - All AI operations halted',
                'activated_by': user_id,
                'timestamp': datetime.now().isoformat(),
                'system_status': 'EMERGENCY_STOP_ACTIVE'
            }
           
        except Exception as e:
            return {
                'success': False,
                'message': f'Emergency stop module error: {str(e)}'
            }

    def get_system_status(self) -> Dict[str, Any]:
        """📊 Gibt vollständigen System-Status zurück"""
       
        return {
            'system_info': {
                'name': self.config.system_name,
                'version': self.config.version,
                'domain': self.domain,
                'mode': self.config.processing_mode.value,
                'security_level': self.config.security_level.value
            },
            'module_status': {
                'fast_path': self.config.fast_path_enabled,
                'deep_path': self.config.deep_path_enabled,
                'governance': self.config.governance_enabled,
                'learning': self.config.learning_enabled,
                'audit': self.config.audit_enabled
            },
            'statistics': self.system_stats.copy(),
            'emergency_status': self.session_data.get('emergency_stop_active', False),
            'configuration': {
                'align_weights': self.config.align_weights,
                'fast_path_confidence': self.config.fast_path_confidence_threshold,
                'deep_path_min_score': self.config.deep_path_min_acceptable_score
            },
            'timestamp': datetime.now().isoformat()
        }

    def update_configuration(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """⚙️ Aktualisiert System-Konfiguration zur Laufzeit"""
       
        try:
            # Sichere kritische Einstellungen
            if 'align_weights' in new_config:
                self.config.align_weights.update(new_config['align_weights'])
           
            if 'fast_path_confidence_threshold' in new_config:
                self.config.fast_path_confidence_threshold = new_config['fast_path_confidence_threshold']
           
            if 'deep_path_min_acceptable_score' in new_config:
                self.config.deep_path_min_acceptable_score = new_config['deep_path_min_acceptable_score']
           
            if 'security_level' in new_config:
                try:
                    self.config.security_level = SecurityLevel(new_config['security_level'])
                except ValueError:
                    return {'success': False, 'message': f'Invalid security level: {new_config["security_level"]}'}
           
            if 'processing_mode' in new_config:
                try:
                    self.config.processing_mode = ProcessingMode(new_config['processing_mode'])
                except ValueError:
                    return {'success': False, 'message': f'Invalid processing mode: {new_config["processing_mode"]}'}
           
            return {
                'success': True,
                'message': 'Configuration updated successfully',
                'updated_at': datetime.now().isoformat()
            }
           
        except Exception as e:
            return {
                'success': False,
                'message': f'Configuration update failed: {str(e)}'
            }

    # ==============================================================================
    # Private Methoden für die Verarbeitungs-Pipeline
    # ==============================================================================

    def _initialize_system(self):
        """🔧 Initialisiert das System mit Domain-spezifischen Einstellungen"""
       
        # Domain-spezifische Anpassungen
        domain_configs = {
            'healthcare': {
                'security_level': SecurityLevel.STRICT,
                'align_weights': {'nurturing': 1.0, 'integrity': 1.0, 'governance': 1.0},
                'require_justification_for_overrides': True,
                'auto_escalate_critical': True
            },
            'finance': {
                'security_level': SecurityLevel.STRICT,
                'align_weights': {'integrity': 1.0, 'governance': 1.0},
                'validate_override_safety': True,
                'detailed_reasoning': True
            },
            'education': {
                'align_weights': {'learning': 1.0, 'nurturing': 0.9},
                'pattern_learning': True,
                'provide_explanations': True
            },
            'ecommerce': {
                'align_weights': {'integrity': 1.0, 'awareness': 0.9},
                'fast_path_enabled': True,
                'processing_mode': ProcessingMode.HYBRID
            }
        }
       
        if self.domain in domain_configs:
            domain_config = domain_configs[self.domain]
            for key, value in domain_config.items():
                if hasattr(self.config, key):
                    if key == 'align_weights':
                        self.config.align_weights.update(value)
                    else:
                        setattr(self.config, key, value)

    def _initialize_processing_context(
        self,
        query: str,
        user_id: str,
        context: Dict[str, Any],
        session_id: str,
        request_id: str
    ) -> Dict[str, Any]:
        """🔧 Initialisiert Verarbeitungs-Kontext"""
       
        return {
            'input_data': {
                'query': query,
                'message': query,  # Alias für verschiedene Module
                'user_id': user_id,
                'session_id': session_id,
                'request_id': request_id,
                'user_context': context,
                'domain': self.domain,
                'timestamp': datetime.now().isoformat()
            },
            'profile': {
                'align_weights': self.config.align_weights.copy(),
                'domain': self.domain,
                'security_level': self.config.security_level.value,
                'user_preferences': context.get('user_preferences', {})
            },
            'context': {
                'session_id': session_id,
                'request_id': request_id,
                'processing_history': self.processing_history[-10:],  # Letzte 10 Anfragen
                'system_config': self.config,
                'emergency_stop_active': self.session_data.get('emergency_stop_active', False)
            },
            'modules_executed': [],
            'processing_path': '',
            'errors': [],
            'warnings': []
        }

    def _load_ethical_profile(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """👤 Lädt oder erstellt ethisches Profil"""
       
        try:
            # Versuche Profil-Manager zu verwenden (falls verfügbar)
            result = run_profile_manager(
                processing_context['input_data'],
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('profile_manager')
           
        except Exception as e:
            # Fallback: Basis-Profil verwenden
            processing_context['context']['ethical_profile_loaded'] = True
            processing_context['warnings'].append(f'Profile manager error: {str(e)} - using default profile')
       
        return processing_context

    def _perform_basic_ethics_check(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Führt grundlegende ethische Bewertung durch"""
       
        try:
            # ALIGN-Prinzipien prüfen
            result = run_align_principles(
                processing_context['input_data'],
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('align_principles')
           
            # Basis-Ethik-Check
            if self.config.deep_path_enabled:
                result = run_basic_ethics(
                    processing_context['input_data'],
                    processing_context['profile'],
                    processing_context['context']
                )
                processing_context['context'].update(result)
                processing_context['modules_executed'].append('basic_ethics')
           
        except Exception as e:
            processing_context['errors'].append(f'Ethics module error: {str(e)}')
            # Fallback ethische Werte setzen
            processing_context['context']['align_score'] = 0.5
            processing_context['context']['basic_ethics_result'] = {'status': 'fallback_mode'}
       
        return processing_context

    def _perform_governance_precheck(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🛡️ Führt Governance Pre-Check durch"""
       
        if not self.config.governance_enabled:
            return processing_context
       
        # Emergency Stop Check
        if self.session_data.get('emergency_stop_active'):
            processing_context['context']['emergency_stop_triggered'] = True
            processing_context['context']['decision'] = {
                'response': '🛑 System im Emergency Stop Modus. Alle KI-Operationen sind gestoppt.',
                'path_taken': 'emergency_stop'
            }
            return processing_context
       
        try:
            result = run_basic_control(
                processing_context['input_data'],
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('basic_control_precheck')
           
        except Exception as e:
            processing_context['warnings'].append(f'Governance module error: {str(e)}')
       
        return processing_context

    def _determine_processing_path(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🚦 Bestimmt intelligente Fast/Deep Path Entscheidung"""
       
        # Emergency Stop oder Governance-Override?
        if processing_context['context'].get('emergency_stop_triggered'):
            processing_context['processing_path'] = 'emergency_stop'
            return processing_context
       
        if processing_context['context'].get('decision', {}).get('path_taken') in ['ESCALATED', 'USER_REJECTED']:
            processing_context['processing_path'] = 'governance_override'
            return processing_context
       
        # Konfiguration-basierte Entscheidung
        if self.config.processing_mode == ProcessingMode.FAST_ONLY:
            processing_context['processing_path'] = 'fast_path'
        elif self.config.processing_mode == ProcessingMode.DEEP_ONLY:
            processing_context['processing_path'] = 'deep_path'
        else:
            # AUTO oder HYBRID: Intelligente Entscheidung
            if self.config.fast_path_enabled:
                try:
                    result = run_fast_path(
                        processing_context['input_data'],
                        processing_context['profile'],
                        processing_context['context']
                    )
                    processing_context['context'].update(result)
                    processing_context['modules_executed'].append('fast_path')
                   
                    # Fast Path Entscheidung auswerten
                    fast_path_analysis = processing_context['context'].get('fast_path_analysis', {})
                    recommended_path = fast_path_analysis.get('recommended_path', 'deep_path')
                   
                    if recommended_path == 'fast_path':
                        processing_context['processing_path'] = 'fast_path'
                        # Fast Path hat bereits Antwort generiert
                        return processing_context
                    else:
                        processing_context['processing_path'] = 'deep_path'
               
                except Exception as e:
                    processing_context['warnings'].append(f'Fast path module error: {str(e)}')
                    processing_context['processing_path'] = 'deep_path'
            else:
                processing_context['processing_path'] = 'deep_path'
       
        return processing_context

    def _execute_processing_path(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Führt gewählten Processing Path aus"""
       
        path = processing_context['processing_path']
       
        if path == 'fast_path':
            # Fast Path bereits ausgeführt in _determine_processing_path
            pass
       
        elif path == 'deep_path' and self.config.deep_path_enabled:
            try:
                result = run_deep_path(
                    processing_context['input_data'],
                    processing_context['profile'],
                    processing_context['context']
                )
                processing_context['context'].update(result)
                processing_context['modules_executed'].append('deep_path')
               
            except Exception as e:
                processing_context['errors'].append(f'Deep path module error: {str(e)}')
                # Fallback-Antwort
                processing_context['context']['decision'] = {
                    'response': 'Entschuldigung, eine umfassende ethische Analyse ist derzeit nicht verfügbar. Bitte kontaktieren Sie einen menschlichen Ansprechpartner.',
                    'path_taken': 'fallback'
                }
       
        elif path in ['emergency_stop', 'governance_override']:
            # Bereits in vorherigen Schritten behandelt
            pass
       
        else:
            # Fallback für unbekannte Pfade
            processing_context['errors'].append(f'Unknown processing path: {path}')
            processing_context['context']['decision'] = {
                'response': 'Entschuldigung, es gab ein Problem bei der Verarbeitung Ihrer Anfrage.',
                'path_taken': 'error_fallback'
            }
       
        return processing_context

    def _perform_final_ethics_validation(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """✅ Führt finale ethische Validierung durch"""
       
        try:
            # Finale ALIGN-Bewertung der generierten Antwort
            decision = processing_context['context'].get('decision', {})
            if 'response' in decision:
                # Bewerte die finale Antwort nochmals ethisch
                validation_input = processing_context['input_data'].copy()
                validation_input['generated_response'] = decision['response']
                
                result = run_align_principles(
                    validation_input,
                    processing_context['profile'],
                    processing_context['context']
                )
                
                # Speichere finale Ethik-Scores
                processing_context['context']['final_align_score'] = result.get('align_score', 0.5)
                processing_context['context']['final_align_details'] = result.get('align_details', {})
                processing_context['modules_executed'].append('final_ethics_validation')
           
        except Exception as e:
            processing_context['warnings'].append(f'Final ethics validation error: {str(e)}')
            processing_context['context']['final_align_score'] = processing_context['context'].get('align_score', 0.5)
       
        return processing_context

    def _perform_governance_postcheck(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🛡️ Führt Governance Post-Check durch"""
       
        if not self.config.governance_enabled:
            return processing_context
       
        try:
            # Post-Check für finale Antwort
            postcheck_input = processing_context['input_data'].copy()
            decision = processing_context['context'].get('decision', {})
            postcheck_input['final_response'] = decision.get('response', '')
            
            result = run_basic_control(
                postcheck_input,
                processing_context['profile'],
                processing_context['context']
            )
            
            # Aktualisiere Kontext mit Post-Check Ergebnissen
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('governance_postcheck')
            
            # Prüfe auf Governance-Interventionen
            governance_result = result.get('basic_control_result', {})
            if governance_result.get('intervention_required'):
                processing_context['context']['governance_intervention'] = True
                self.system_stats['governance_interventions'] += 1
           
        except Exception as e:
            processing_context['warnings'].append(f'Governance postcheck error: {str(e)}')
       
        return processing_context

    def _perform_adaptive_learning(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🧠 Führt adaptives Lernen durch"""
       
        try:
            learning_input = processing_context['input_data'].copy()
            learning_input['processing_result'] = processing_context['context'].get('decision', {})
            learning_input['align_scores'] = processing_context['context'].get('align_details', {})
            learning_input['user_feedback'] = processing_context['input_data'].get('user_context', {}).get('feedback')
            
            result = run_mini_learner(
                learning_input,
                processing_context['profile'],
                processing_context['context']
            )
            
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('adaptive_learning')
            
            # Aktualisiere Statistiken
            if result.get('learning_result', {}).get('patterns_updated'):
                self.system_stats['learning_updates'] += 1
           
        except Exception as e:
            processing_context['warnings'].append(f'Adaptive learning error: {str(e)}')
       
        return processing_context

    def _perform_audit_logging(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """📋 Führt Audit und Logging durch"""
       
        try:
            audit_input = processing_context['input_data'].copy()
            audit_input['full_processing_context'] = processing_context
            audit_input['modules_used'] = processing_context['modules_executed']
            audit_input['final_decision'] = processing_context['context'].get('decision', {})
            
            result = run_mini_audit(
                audit_input,
                processing_context['profile'],
                processing_context['context']
            )
            
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('audit_logging')
           
        except Exception as e:
            processing_context['warnings'].append(f'Audit logging error: {str(e)}')
       
        return processing_context

    def _compile_final_result(self, processing_context: Dict[str, Any], start_time: datetime) -> ProcessingResult:
        """📊 Kompiliert finales Verarbeitungs-Ergebnis"""
       
        # Verarbeitungszeit berechnen
        processing_time = datetime.now() - start_time
        
        # Hauptentscheidung extrahieren
        decision = processing_context['context'].get('decision', {})
        
        # ALIGN-Scores extrahieren
        align_score = processing_context['context'].get('final_align_score') or processing_context['context'].get('align_score', 0.5)
        align_details = processing_context['context'].get('final_align_details') or processing_context['context'].get('align_details', {})
        
        # Ethische Qualität bestimmen
        ethical_quality = self._determine_ethical_quality(align_score)
        
        # Governance-Aktionen sammeln
        governance_actions = []
        if processing_context['context'].get('governance_intervention'):
            governance_actions.append('intervention_applied')
        if processing_context['context'].get('escalation_triggered'):
            governance_actions.append('escalation_triggered')
        
        # Verarbeitungs-Ergebnis erstellen
        result = ProcessingResult(
            response=decision.get('response', 'Keine Antwort generiert'),
            confidence=decision.get('confidence', 0.5),
            processing_path=processing_context['processing_path'],
            align_score=align_score,
            align_details=align_details,
            align_violations=processing_context['context'].get('align_violations', []),
            ethical_quality=ethical_quality,
            modules_used=processing_context['modules_executed'],
            processing_time=f"{processing_time.total_seconds():.3f}s",
            governance_actions=governance_actions,
            escalation_triggered=processing_context['context'].get('escalation_triggered', False),
            user_override_applied=processing_context['context'].get('user_override_applied', False),
            reasoning_provided=self.config.provide_explanations,
            alternatives_available=processing_context['context'].get('alternatives_generated', False),
            risk_mitigation=processing_context['context'].get('risk_mitigation_actions', []),
            session_id=processing_context['input_data']['session_id'],
            user_id=processing_context['input_data']['user_id'],
            request_id=processing_context['input_data']['request_id']
        )
        
        # Zu Verarbeitungs-Historie hinzufügen
        self.processing_history.append({
            'request_id': result.request_id,
            'timestamp': result.timestamp,
            'processing_path': result.processing_path,
            'align_score': result.align_score,
            'modules_used': result.modules_used,
            'errors': processing_context['errors'],
            'warnings': processing_context['warnings']
        })
        
        # Historie-Größe begrenzen
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]
        
        return result

    def _create_error_result(self, error_message: str, request_id: str, session_id: str, user_id: str, start_time: datetime) -> ProcessingResult:
        """❌ Erstellt Fehler-Ergebnis bei Verarbeitungsproblemen"""
        
        processing_time = datetime.now() - start_time
        
        return ProcessingResult(
            response=f"Entschuldigung, es gab einen technischen Fehler: {error_message}. Bitte versuchen Sie es später erneut oder kontaktieren Sie den Support.",
            confidence=0.0,
            processing_path='error',
            align_score=0.0,
            ethical_quality='error',
            processing_time=f"{processing_time.total_seconds():.3f}s",
            session_id=session_id,
            user_id=user_id,
            request_id=request_id
        )

    def _update_system_stats(self, processing_context: Dict[str, Any], result: ProcessingResult):
        """📈 Aktualisiert System-Statistiken"""
        
        self.system_stats['total_requests'] += 1
        
        if result.processing_path == 'fast_path':
            self.system_stats['fast_path_usage'] += 1
        elif result.processing_path == 'deep_path':
            self.system_stats['deep_path_usage'] += 1
        
        if result.escalation_triggered:
            self.system_stats['escalations'] += 1
        
        if processing_context['context'].get('governance_intervention'):
            self.system_stats['governance_interventions'] += 1

    def _determine_ethical_quality(self, align_score: float) -> str:
        """🎯 Bestimmt ethische Qualitäts-Bewertung basierend auf ALIGN-Score"""
        
        if align_score >= 0.9:
            return 'excellent'
        elif align_score >= 0.8:
            return 'good'
        elif align_score >= 0.6:
            return 'acceptable'
        elif align_score >= 0.4:
            return 'concerning'
        else:
            return 'unacceptable'


# ==============================================================================
# 3. Hilfsfunktionen und Factory-Methoden
# ==============================================================================

def create_integra_light(
    domain: str = "general",
    security_level: str = "balanced",
    processing_mode: str = "auto",
    enable_learning: bool = True,
    enable_fast_path: bool = True,
    **kwargs
) -> INTEGRALight:
    """
    🏗️ Factory-Funktion zum einfachen Erstellen von INTEGRA Light Instanzen
    
    Args:
        domain: Anwendungsdomäne
        security_level: Sicherheitslevel (permissive, balanced, strict, paranoid)
        processing_mode: Verarbeitungsmodus (auto, fast_only, deep_only, hybrid)
        enable_learning: Aktiviere adaptives Lernen
        enable_fast_path: Aktiviere Fast Path
        **kwargs: Zusätzliche Konfigurationsparameter
    
    Returns:
        Konfigurierte INTEGRALight Instanz
    """
    
    # Konvertiere String-Parameter zu Enums
    try:
        security_enum = SecurityLevel(security_level)
    except ValueError:
        print(f"⚠️ Ungültiges Sicherheitslevel '{security_level}', verwende 'balanced'")
        security_enum = SecurityLevel.BALANCED
    
    try:
        mode_enum = ProcessingMode(processing_mode)
    except ValueError:
        print(f"⚠️ Ungültiger Verarbeitungsmodus '{processing_mode}', verwende 'auto'")
        mode_enum = ProcessingMode.AUTO
    
    # Erstelle Konfiguration
    config = INTEGRALightConfig(
        security_level=security_enum,
        processing_mode=mode_enum,
        learning_enabled=enable_learning,
        fast_path_enabled=enable_fast_path
    )
    
    # Wende zusätzliche Parameter an
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"⚠️ Unbekannter Konfigurationsparameter: {key}")
    
    # Erstelle und returniere INTEGRA Light Instanz
    return INTEGRALight(config=config, domain=domain)


def quick_ethical_check(query: str, domain: str = "general") -> Dict[str, Any]:
    """
    ⚡ Schnelle ethische Bewertung ohne vollständige INTEGRA-Pipeline
    
    Args:
        query: Zu bewertende Anfrage
        domain: Anwendungsdomäne
    
    Returns:
        Schnelle ethische Bewertung
    """
    
    # Erstelle minimal-konfigurierte INTEGRA Light Instanz
    config = INTEGRALightConfig(
        processing_mode=ProcessingMode.FAST_ONLY,
        governance_enabled=False,
        learning_enabled=False,
        audit_enabled=False
    )
    
    integra = INTEGRALight(config=config, domain=domain)
    
    # Führe schnelle Bewertung durch
    result = integra.process_request(query, user_id="quick_check")
    
    return {
        'query': query,
        'align_score': result.align_score,
        'ethical_quality': result.ethical_quality,
        'safe': result.align_score >= 0.6,
        'processing_time': result.processing_time,
        'recommendation': 'safe' if result.align_score >= 0.6 else 'review_required'
    }


def create_domain_specific_integra(domain: str) -> INTEGRALight:
    """
    🎯 Erstellt domain-spezifisch optimierte INTEGRA Light Instanz
    
    Args:
        domain: Anwendungsdomäne (healthcare, finance, education, ecommerce, etc.)
    
    Returns:
        Domain-optimierte INTEGRA Light Instanz
    """
    
    domain_configs = {
        'healthcare': {
            'security_level': 'strict',
            'processing_mode': 'deep_only',
            'align_weights': {'nurturing': 1.0, 'integrity': 1.0, 'governance': 1.0},
            'auto_escalate_critical': True,
            'require_justification_for_overrides': True
        },
        'finance': {
            'security_level': 'strict',
            'processing_mode': 'hybrid',
            'align_weights': {'integrity': 1.0, 'governance': 1.0},
            'detailed_reasoning': True,
            'validate_override_safety': True
        },
        'education': {
            'security_level': 'balanced',
            'processing_mode': 'auto',
            'align_weights': {'learning': 1.0, 'nurturing': 0.9},
            'provide_explanations': True,
            'pattern_learning': True
        },
        'ecommerce': {
            'security_level': 'balanced',
            'processing_mode': 'hybrid',
            'align_weights': {'integrity': 1.0, 'awareness': 0.9},
            'fast_path_enabled': True
        },
        'social_media': {
            'security_level': 'strict',
            'processing_mode': 'auto',
            'align_weights': {'nurturing': 0.9, 'governance': 1.0},
            'auto_escalate_critical': True
        }
    }
    
    if domain in domain_configs:
        return create_integra_light(domain=domain, **domain_configs[domain])
    else:
        print(f"⚠️ Unbekannte Domain '{domain}', verwende Standard-Konfiguration")
        return create_integra_light(domain=domain)


# ==============================================================================
# 4. Beispiel-Anwendungen
# ==============================================================================

def example_basic_usage():
    """💡 Zeigt grundlegende Verwendung von INTEGRA Light"""
    
    print("💡 INTEGRA Light - Grundlegende Verwendung")
    print("=" * 50)
    
    # Einfache Erstellung
    integra = create_integra_light()
    
    # Anfrage verarbeiten
    result = integra.process_request(
        query="Wie kann ich meinen Kunden besser helfen?",
        user_id="demo_user"
    )
    
    print(f"🤖 Antwort: {result.response}")
    print(f"📊 Ethik-Score: {result.align_score:.2f}")
    print(f"🛤️ Verarbeitungsweg: {result.processing_path}")
    print(f"⏱️ Verarbeitungszeit: {result.processing_time}")


def example_domain_specific():
    """🏥 Zeigt domain-spezifische Konfiguration"""
    
    print("\n🏥 INTEGRA Light - Healthcare Domain")
    print("=" * 50)
    
    # Healthcare-optimierte Instanz
    healthcare_integra = create_domain_specific_integra('healthcare')
    
    # Medizinische Anfrage
    result = healthcare_integra.process_request(
        query="Ein Patient fragt nach Medikamentenempfehlungen für Depressionen",
        user_id="doctor_123"
    )
    
    print(f"🏥 Healthcare-Antwort: {result.response}")
    print(f"🛡️ Sicherheitslevel: {healthcare_integra.config.security_level.value}")
    print(f"🚨 Eskalation erforderlich: {result.escalation_triggered}")


def example_quick_check():
    """⚡ Zeigt schnelle ethische Bewertung"""
    
    print("\n⚡ INTEGRA Light - Schnelle Ethik-Prüfung")
    print("=" * 50)
    
    queries = [
        "Wie backe ich einen Kuchen?",
        "Wie kann ich jemanden verletzen?",
        "Hilf mir bei meinen Hausaufgaben"
    ]
    
    for query in queries:
        result = quick_ethical_check(query)
        print(f"❓ '{query}'")
        print(f"   📊 Score: {result['align_score']:.2f} | {result['ethical_quality']} | {result['recommendation']}")


if __name__ == "__main__":
    # Beispiele ausführen
    example_basic_usage()
    example_domain_specific()
    example_quick_check()