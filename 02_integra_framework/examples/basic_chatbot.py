# -*- coding: utf-8 -*-

"""
examples/basic_chatbot.py

🤖 INTEGRA Basic Chatbot - Vollständiges ethisches Chatbot-Beispiel 🤖

Ein produktionsreifer, ethischer Chatbot der alle INTEGRA Light Features demonstriert:

- Intelligente Konversationsführung mit ethischen Guardrails
- Vollständige ALIGN-Prinzipien Integration
- Adaptive Persönlichkeit basierend auf Nutzerfeedback
- Menschliche Kontrolle und Eskalations-Management
- Session-Management und Konversations-Historie
- Domain-spezifische Anpassungen
- Web-Interface (optional) und CLI-Interface

Design-Philosophie: Hilfsbereit, ehrlich, sicher und lernfähig

Version: INTEGRA Light Chatbot 1.0
"""

import sys
import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import argparse

# INTEGRA Light Import
try:
    from ..versions.light import INTEGRALight, create_integra_light, INTEGRALightConfig, SecurityLevel, ProcessingMode
    from ..versions.light import quick_ethical_check
except ImportError:
    print("⚠️ INTEGRA Light nicht gefunden. Standalone-Modus aktiv.")
    # Mock für Standalone-Demo
    class MockINTEGRALight:
        def __init__(self, *args, **kwargs):
            self.config = type('Config', (), {'system_name': 'Mock INTEGRA', 'version': '1.0'})()
            print("🤖 Mock INTEGRA Light Chatbot initialisiert")

        def process_request(self, query, **kwargs):
            return type('Result', (), {
                'response': f"Mock-Antwort für: {query}",
                'align_score': 0.85,
                'ethical_quality': 'good',
                'processing_path': 'mock_path',
                'confidence': 0.8,
                'escalation_triggered': False,
                'timestamp': datetime.now().isoformat(),
                'align_violations': [],
                'risk_mitigation': None
            })()
        
        def get_system_status(self):
            return {'statistics': {'total_requests': 0}}
        
        def update_configuration(self, config):
            return {'success': True}

    INTEGRALight = MockINTEGRALight
    create_integra_light = lambda **kwargs: MockINTEGRALight()

# ==============================================================================
# 1. Chatbot-Konfiguration und Datenstrukturen
# ==============================================================================

class ChatbotPersonality(Enum):
    """🎭 Verfügbare Chatbot-Persönlichkeiten"""
    HELPFUL = "helpful"           # Hilfsbereit und unterstützend
    PROFESSIONAL = "professional" # Professionell und sachlich
    FRIENDLY = "friendly"         # Freundlich und persönlich
    EDUCATIONAL = "educational"   # Lehrreich und erklärend
    THERAPEUTIC = "therapeutic"   # Einfühlsam und unterstützend

class ConversationState(Enum):
    """💬 Zustände der Konversation"""
    GREETING = "greeting"         # Begrüßungsphase
    ACTIVE = "active"            # Aktive Unterhaltung
    HELPING = "helping"          # Hilfeleistung
    SENSITIVE = "sensitive"      # Sensibles Thema
    ESCALATION = "escalation"    # Eskalation erforderlich
    ENDING = "ending"            # Verabschiedung

@dataclass
class ChatSession:
    """📝 Chat-Session Datenstruktur"""
    session_id: str
    user_id: str
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    conversation_state: ConversationState = ConversationState.GREETING
    personality: ChatbotPersonality = ChatbotPersonality.HELPFUL
    context_memory: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    ethical_flags: List[str] = field(default_factory=list)
    user_satisfaction: float = 0.5  # 0.0-1.0

@dataclass
class ChatbotConfig:
    """⚙️ Chatbot-Konfiguration"""
    # Grund-Einstellungen
    bot_name: str = "INTEGRA Bot"
    domain: str = "general"
    personality: ChatbotPersonality = ChatbotPersonality.HELPFUL
    security_level: str = "balanced"

    # Konversations-Einstellungen
    max_conversation_length: int = 100
    session_timeout_minutes: int = 30
    enable_memory: bool = True
    enable_learning: bool = True

    # INTEGRA-Einstellungen
    enable_fast_path: bool = True
    enable_deep_path: bool = True
    auto_escalate_sensitive: bool = True
    provide_explanations: bool = True

    # Persönlichkeits-Parameter
    friendliness_level: float = 0.8
    formality_level: float = 0.5
    verbosity_level: float = 0.7
    empathy_level: float = 0.8

    # Sicherheits-Parameter
    block_sensitive_topics: bool = True
    require_human_escalation: bool = True
    log_conversations: bool = True

# ==============================================================================
# 2. Hauptklasse - INTEGRA Chatbot
# ==============================================================================

class INTEGRAChatbot:
    """
    🤖 INTEGRA-basierter ethischer Chatbot

    Ein vollständiger, produktionsreifer Chatbot der alle INTEGRA Light
    Features für sichere, ethische Konversationen nutzt:

    🎭 Adaptive Persönlichkeit basierend auf Nutzer und Kontext
    🧠 Intelligente Konversationsführung mit Ethik-Guardrails
    💾 Session-Management und Konversations-Gedächtnis
    🛡️ Automatische Eskalation bei kritischen Themen
    📊 Vollständige Transparenz und Audit-Trails
    🔧 Einfache Integration und Anpassung
    """

    def __init__(self, config: Optional[ChatbotConfig] = None):
        """
        Initialisiert den INTEGRA Chatbot
        
        Args:
            config: Chatbot-Konfiguration (optional)
        """
        self.config = config or ChatbotConfig()
        self.active_sessions: Dict[str, ChatSession] = {}
        self.conversation_stats = {
            'total_conversations': 0,
            'total_messages': 0,
            'escalations': 0,
            'average_satisfaction': 0.0,
            'common_topics': {},
            'personality_usage': {}
        }
        
        # Initialisiere INTEGRA Light
        self.integra = create_integra_light(
            domain=self.config.domain,
            security_level=self.config.security_level,
            enable_learning=self.config.enable_learning,
            enable_fast_path=self.config.enable_fast_path
        )
        
        # Anpassung der INTEGRA-Konfiguration für Chatbot
        self._configure_integra_for_chatbot()
        
        # Persönlichkeits-Templates
        self.personality_templates = self._load_personality_templates()
        
        print(f"🤖 {self.config.bot_name} initialisiert")
        print(f"🎭 Persönlichkeit: {self.config.personality.value}")
        print(f"🏢 Domain: {self.config.domain}")
        print(f"🔒 Sicherheit: {self.config.security_level}")
        print(f"🧠 INTEGRA Light: Aktiv")

    def start_conversation(self, user_id: str, initial_message: Optional[str] = None) -> Dict[str, Any]:
        """
        🚀 Startet neue Konversation mit Nutzer
        
        Args:
            user_id: Eindeutige Nutzer-ID
            initial_message: Optionale erste Nachricht
            
        Returns:
            Conversation-Start-Ergebnis mit Begrüßung
        """
        
        session_id = f"chat_{user_id}_{int(datetime.now().timestamp())}"
        
        # Erstelle neue Session
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            personality=self.config.personality
        )
        
        self.active_sessions[session_id] = session
        self.conversation_stats['total_conversations'] += 1
        
        # Generiere Begrüßung
        if initial_message:
            # Benutzer hat bereits eine Nachricht geschickt
            response = self.process_message(session_id, initial_message)
        else:
            # Standard-Begrüßung
            greeting = self._generate_greeting(session)
            response = {
                'bot_response': greeting,
                'session_id': session_id,
                'conversation_state': session.conversation_state.value,
                'timestamp': datetime.now().isoformat(),
                'ethics_info': {
                    'align_score': 1.0,
                    'quality': 'excellent',
                    'safe': True
                }
            }
        
        print(f"👋 Neue Konversation gestartet: {session_id}")
        return response

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        💬 Verarbeitet Benutzer-Nachricht und generiert Antwort
        
        Args:
            session_id: Session-ID der Konversation
            message: Benutzer-Nachricht
            
        Returns:
            Bot-Antwort mit ethischen Metadaten
        """
        
        # Session validieren
        if session_id not in self.active_sessions:
            return {
                'error': 'Session nicht gefunden',
                'bot_response': 'Entschuldigung, ich kann Ihre Session nicht finden. Bitte starten Sie eine neue Unterhaltung.',
                'session_expired': True
            }
        
        session = self.active_sessions[session_id]
        
        # Session-Timeout prüfen
        if self._is_session_expired(session):
            return {
                'error': 'Session abgelaufen',
                'bot_response': 'Ihre Session ist abgelaufen. Bitte starten Sie eine neue Unterhaltung.',
                'session_expired': True
            }
        
        # Aktualisiere Session
        session.last_activity = datetime.now()
        session.message_count += 1
        self.conversation_stats['total_messages'] += 1
        
        try:
            # Kontext für INTEGRA vorbereiten
            context = self._prepare_context_for_integra(session, message)
            
            # INTEGRA Light Verarbeitung
            integra_result = self.integra.process_request(
                query=message,
                user_id=session.user_id,
                session_id=session_id,
                context=context
            )
            
            # Antwort durch Chatbot-Persönlichkeit filtern
            bot_response = self._personalize_response(
                integra_result.response,
                session,
                integra_result
            )
            
            # Konversations-Zustand aktualisieren
            self._update_conversation_state(session, message, integra_result)
            
            # Zur Historie hinzufügen
            self._add_to_conversation_history(session, message, bot_response, integra_result)
            
            # Eskalation behandeln (falls erforderlich)
            escalation_info = self._handle_escalation(session, integra_result)
            
            # Lernen aus dieser Interaktion
            if self.config.enable_learning:
                self._learn_from_interaction(session, message, integra_result)
            
            # Antwort zusammenstellen
            response = {
                'bot_response': bot_response,
                'session_id': session_id,
                'conversation_state': session.conversation_state.value,
                'message_count': session.message_count,
                'timestamp': datetime.now().isoformat(),
                'ethics_info': {
                    'align_score': integra_result.align_score,
                    'quality': integra_result.ethical_quality,
                    'processing_path': integra_result.processing_path,
                    'confidence': integra_result.confidence,
                    'safe': integra_result.align_score >= 0.6
                },
                'escalation': escalation_info,
                'personality': session.personality.value
            }
            
            # Zusätzliche Kontext-Informationen (für Debugging)
            if integra_result.align_violations:
                response['ethics_info']['violations'] = integra_result.align_violations
            
            if integra_result.risk_mitigation:
                response['ethics_info']['risk_mitigation'] = integra_result.risk_mitigation
            
            return response
            
        except Exception as e:
            print(f"❌ Fehler bei Nachrichtenverarbeitung: {e}")
            
            return {
                'error': f'Verarbeitungsfehler: {str(e)}',
                'bot_response': 'Entschuldigung, ich hatte ein technisches Problem. Könnten Sie das bitte wiederholen?',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }

    def end_conversation(self, session_id: str, reason: str = "user_ended") -> Dict[str, Any]:
        """
        👋 Beendet Konversation ordnungsgemäß
        
        Args:
            session_id: Session-ID der zu beendenden Konversation
            reason: Grund für Beendigung
            
        Returns:
            Verabschiedungs-Informationen
        """
        
        if session_id not in self.active_sessions:
            return {'error': 'Session nicht gefunden'}
        
        session = self.active_sessions[session_id]
        
        # Generiere Verabschiedung
        farewell = self._generate_farewell(session, reason)
        
        # Session-Statistiken aktualisieren
        session_duration = datetime.now() - session.start_time
        conversation_summary = {
            'session_id': session_id,
            'user_id': session.user_id,
            'duration_minutes': session_duration.total_seconds() / 60,
            'message_count': session.message_count,
            'final_satisfaction': session.user_satisfaction,
            'personality_used': session.personality.value,
            'ethical_flags': session.ethical_flags,
            'end_reason': reason
        }
        
        # Optional: Conversation loggen
        if self.config.log_conversations:
            self._log_conversation(session, conversation_summary)
        
        # Session entfernen
        del self.active_sessions[session_id]
        
        print(f"👋 Konversation beendet: {session_id} (Dauer: {session_duration})")
        
        return {
            'bot_response': farewell,
            'conversation_ended': True,
            'session_summary': conversation_summary,
            'timestamp': datetime.now().isoformat()
        }

    def get_conversation_status(self, session_id: str) -> Dict[str, Any]:
        """📊 Gibt aktuellen Konversations-Status zurück"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session nicht gefunden', 'active': False}
        
        session = self.active_sessions[session_id]
        
        return {
            'active': True,
            'session_id': session_id,
            'user_id': session.user_id,
            'message_count': session.message_count,
            'conversation_state': session.conversation_state.value,
            'personality': session.personality.value,
            'satisfaction': session.user_satisfaction,
            'ethical_flags': session.ethical_flags,
            'start_time': session.start_time.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'expired': self._is_session_expired(session)
        }

    def get_chatbot_stats(self) -> Dict[str, Any]:
        """📈 Gibt Chatbot-Statistiken zurück"""
        
        # INTEGRA System-Status
        integra_status = self.integra.get_system_status()
        
        # Chatbot-spezifische Statistiken
        active_sessions_count = len(self.active_sessions)
        avg_satisfaction = self.conversation_stats['average_satisfaction']
        
        return {
            'chatbot_info': {
                'name': self.config.bot_name,
                'domain': self.config.domain,
                'personality': self.config.personality.value,
                'version': '1.0'
            },
            'conversation_stats': self.conversation_stats.copy(),
            'active_sessions': active_sessions_count,
            'integra_stats': integra_status['statistics'],
            'system_health': {
                'active': True,
                'emergency_stop': integra_status.get('emergency_status', False),
                'last_updated': datetime.now().isoformat()
            }
        }

    def update_chatbot_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """⚙️ Aktualisiert Chatbot-Konfiguration zur Laufzeit"""
        
        try:
            # Sichere Updates
            if 'personality' in new_config:
                try:
                    self.config.personality = ChatbotPersonality(new_config['personality'])
                except ValueError:
                    return {'success': False, 'message': f'Invalid personality: {new_config["personality"]}'}
            
            if 'friendliness_level' in new_config:
                self.config.friendliness_level = max(0.0, min(1.0, float(new_config['friendliness_level'])))
            
            if 'empathy_level' in new_config:
                self.config.empathy_level = max(0.0, min(1.0, float(new_config['empathy_level'])))
            
            # INTEGRA-Konfiguration weiterleiten
            integra_updates = {}
            if 'security_level' in new_config:
                integra_updates['security_level'] = new_config['security_level']
            
            if 'align_weights' in new_config:
                integra_updates['align_weights'] = new_config['align_weights']
            
            if integra_updates:
                integra_result = self.integra.update_configuration(integra_updates)
                if not integra_result['success']:
                    return integra_result
            
            return {
                'success': True,
                'message': 'Chatbot configuration updated successfully',
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Configuration update failed: {str(e)}'
            }

    # ==============================================================================
    # Private Methoden für Chatbot-Funktionalität
    # ==============================================================================

    def _configure_integra_for_chatbot(self):
        """🔧 Konfiguriert INTEGRA Light spezifisch für Chatbot-Nutzung"""
        
        # Chatbot-optimierte ALIGN-Gewichte
        chatbot_weights = {
            'awareness': 0.8,   # Nutzer verstehen
            'learning': 0.7,    # Aus Gesprächen lernen
            'integrity': 0.9,   # Ehrlich sein
            'governance': 0.8,  # Nutzerkontrolle
            'nurturing': 0.9    # Hilfsbereit und fürsorglich
        }
        
        # Persönlichkeits-spezifische Anpassungen
        if self.config.personality == ChatbotPersonality.PROFESSIONAL:
            chatbot_weights['governance'] = 1.0
            chatbot_weights['integrity'] = 1.0
        elif self.config.personality == ChatbotPersonality.THERAPEUTIC:
            chatbot_weights['nurturing'] = 1.0
            chatbot_weights['awareness'] = 0.9
        elif self.config.personality == ChatbotPersonality.EDUCATIONAL:
            chatbot_weights['learning'] = 1.0
            chatbot_weights['integrity'] = 0.9
        
        # INTEGRA konfigurieren
        self.integra.update_configuration({
            'align_weights': chatbot_weights,
            'fast_path_confidence_threshold': 0.8,
            'deep_path_min_acceptable_score': 0.6
        })

    def _load_personality_templates(self) -> Dict[str, Dict[str, Any]]:
        """🎭 Lädt Persönlichkeits-Templates"""
        
        return {
            ChatbotPersonality.HELPFUL.value: {
                'greeting_templates': [
                    "Hallo! Ich bin {bot_name} und helfe gerne bei Ihren Fragen. Womit kann ich Ihnen behilflich sein?",
                    "Hi! Schön, dass Sie da sind. Ich bin {bot_name} und freue mich, Ihnen zu helfen!",
                    "Willkommen! Ich bin {bot_name}, Ihr hilfsbreiter Assistent. Wie kann ich heute unterstützen?"
                ],
                'response_modifiers': {
                    'add_encouragement': True,
                    'suggest_alternatives': True,
                    'use_positive_language': True
                },
                'farewell_templates': [
                    "Es war mir eine Freude, Ihnen zu helfen! Zögern Sie nicht, jederzeit zurückzukommen.",
                    "Ich hoffe, ich konnte hilfreich sein! Bis zum nächsten Mal!"
                ]
            },
            
            ChatbotPersonality.PROFESSIONAL.value: {
                'greeting_templates': [
                    "Guten Tag. Ich bin {bot_name}, Ihr professioneller Assistent. Wie kann ich Ihnen heute behilflich sein?",
                    "Willkommen. Mein Name ist {bot_name}. Bitte teilen Sie mir mit, womit ich Ihnen helfen kann."
                ],
                'response_modifiers': {
                    'use_formal_language': True,
                    'be_concise': True,
                    'provide_sources': True
                },
                'farewell_templates': [
                    "Vielen Dank für das Gespräch. Sollten Sie weitere Fragen haben, stehe ich gerne zur Verfügung.",
                    "Ich hoffe, ich konnte Ihnen weiterhelfen. Guten Tag."
                ]
            },
            
            ChatbotPersonality.FRIENDLY.value: {
                'greeting_templates': [
                    "Hey! 😊 Ich bin {bot_name}! Super, dass du da bist. Was kann ich für dich tun?",
                    "Hi! Ich bin {bot_name} und freue mich riesig, dich kennenzulernen! Wobei kann ich helfen?",
                    "Hallo! 👋 {bot_name} hier! Lass uns zusammen an deinen Fragen arbeiten!"
                ],
                'response_modifiers': {
                    'use_casual_language': True,
                    'add_emojis': True,
                    'be_enthusiastic': True,
                    'use_personal_pronouns': True
                },
                'farewell_templates': [
                    "Das war ein super Gespräch! 😊 Bis bald und hab einen tollen Tag!",
                    "Tschüss! 👋 Komm gerne jederzeit wieder, wenn du Fragen hast!"
                ]
            },
            
            ChatbotPersonality.EDUCATIONAL.value: {
                'greeting_templates': [
                    "Willkommen! Ich bin {bot_name}, Ihr Lern-Assistent. Lassen Sie uns gemeinsam Wissen entdecken!",
                    "Hallo! Ich bin {bot_name} und helfe gerne beim Lernen und Verstehen. Was möchten Sie heute erforschen?"
                ],
                'response_modifiers': {
                    'provide_explanations': True,
                    'ask_follow_up_questions': True,
                    'suggest_learning_resources': True,
                    'break_down_complex_topics': True
                },
                'farewell_templates': [
                    "Lernen ist ein lebenslanges Abenteuer! Ich hoffe, ich konnte Ihnen heute etwas Neues vermitteln.",
                    "Bleiben Sie neugierig! Bis zum nächsten Lern-Abenteuer!"
                ]
            },
            
            ChatbotPersonality.THERAPEUTIC.value: {
                'greeting_templates': [
                    "Hallo und herzlich willkommen. Ich bin {bot_name} und bin hier, um Ihnen zuzuhören und zu helfen.",
                    "Schön, dass Sie da sind. Ich bin {bot_name} und schaffe gerne einen sicheren Raum für unser Gespräch."
                ],
                'response_modifiers': {
                    'use_empathetic_language': True,
                    'validate_feelings': True,
                    'ask_open_questions': True,
                    'be_non_judgmental': True,
                    'provide_emotional_support': True
                },
                'farewell_templates': [
                    "Es war wichtig, dass Sie sich die Zeit genommen haben, mit mir zu sprechen. Passen Sie gut auf sich auf.",
                    "Denken Sie daran: Sie sind nicht allein. Es war wertvoll, mit Ihnen zu sprechen."
                ]
            }
        }

    def _generate_greeting(self, session: ChatSession) -> str:
        """👋 Generiert persönlichkeits-spezifische Begrüßung"""
        
        personality = session.personality.value
        templates = self.personality_templates[personality]['greeting_templates']
        
        # Wähle zufällig ein Template
        import random
        template = random.choice(templates)
        
        # Personalisiere mit Bot-Name
        greeting = template.format(bot_name=self.config.bot_name)
        
        return greeting

    def _generate_farewell(self, session: ChatSession, reason: str) -> str:
        """👋 Generiert persönlichkeits-spezifische Verabschiedung"""
        
        personality = session.personality.value
        templates = self.personality_templates[personality]['farewell_templates']
        
        import random
        farewell = random.choice(templates)
        
        # Füge Grund hinzu falls relevant
        if reason == "timeout":
            farewell = "Unser Gespräch ist aufgrund von Inaktivität abgelaufen. " + farewell
        elif reason == "escalation":
            farewell = "Ein menschlicher Mitarbeiter wird sich bei Ihnen melden. " + farewell
        
        return farewell

    def _prepare_context_for_integra(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """🔧 Bereitet Kontext für INTEGRA Light vor"""
        
        return {
            'conversation_history': session.conversation_history[-5:],  # Letzte 5 Nachrichten
            'conversation_state': session.conversation_state.value,
            'user_preferences': session.context_memory.get('preferences', {}),
            'personality': session.personality.value,
            'session_info': {
                'message_count': session.message_count,
                'satisfaction': session.user_satisfaction,
                'duration_minutes': (datetime.now() - session.start_time).total_seconds() / 60
            },
            'chatbot_config': {
                'domain': self.config.domain,
                'friendliness': self.config.friendliness_level,
                'empathy': self.config.empathy_level,
                'formality': self.config.formality_level
            }
        }

    def _personalize_response(self, base_response: str, session: ChatSession, integra_result) -> str:
        """🎭 Personalisiert Antwort basierend auf Chatbot-Persönlichkeit"""
        
        personality = session.personality.value
        modifiers = self.personality_templates[personality]['response_modifiers']
        
        response = base_response
        
        # Persönlichkeits-spezifische Modifikationen
        if modifiers.get('use_casual_language') and self.config.formality_level < 0.5:
            response = self._make_more_casual(response)
        
        if modifiers.get('use_formal_language') and self.config.formality_level > 0.7:
            response = self._make_more_formal(response)
        
        if modifiers.get('add_encouragement') and integra_result.align_score > 0.7:
            response = self._add_encouragement(response)
        
        if modifiers.get('add_emojis') and self.config.friendliness_level > 0.7:
            response = self._add_appropriate_emojis(response)
        
        if modifiers.get('use_empathetic_language') and session.conversation_state == ConversationState.SENSITIVE:
            response = self._add_empathy(response)
        
        if modifiers.get('provide_explanations') and ('warum' in base_response.lower() or 'wie' in base_response.lower()):
            response = self._enhance_explanation(response)
        
        # Anpassung an Nutzerzufriedenheit
        if session.user_satisfaction < 0.3:
            response = self._add_extra_support(response)
        
        return response

    def _update_conversation_state(self, session: ChatSession, message: str, integra_result):
        """📊 Aktualisiert Konversations-Zustand basierend auf Nachricht und Ethik-Analyse"""
        
        # Analyse der Nachricht für Zustandsänderung
        message_lower = message.lower()
        
        # Sensitive Themen erkennen
        sensitive_indicators = [
            'depressed', 'suicide', 'hurt myself', 'desperate',
            'hopeless', 'can\'t go on', 'want to die'
        ]
        
        if any(indicator in message_lower for indicator in sensitive_indicators):
            session.conversation_state = ConversationState.SENSITIVE
            session.ethical_flags.append('sensitive_content_detected')
        
        # Hilfe-Anfragen erkennen
        help_indicators = ['help', 'hilfe', 'unterstützung', 'problem', 'frage']
        if any(indicator in message_lower for indicator in help_indicators):
            session.conversation_state = ConversationState.HELPING
        
        # Eskalation erforderlich
        if integra_result.escalation_triggered:
            session.conversation_state = ConversationState.ESCALATION
            session.ethical_flags.append('escalation_triggered')
        
        # Verabschiedung erkennen
        goodbye_indicators = ['bye', 'tschüss', 'auf wiedersehen', 'danke', 'ende']
        if any(indicator in message_lower for indicator in goodbye_indicators):
            session.conversation_state = ConversationState.ENDING

    def _add_to_conversation_history(self, session: ChatSession, user_message: str, bot_response: str, integra_result):
        """📝 Fügt Nachricht zur Konversations-Historie hinzu"""
        
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response,
            'conversation_state': session.conversation_state.value,
            'align_score': integra_result.align_score,
            'processing_path': integra_result.processing_path,
            'ethical_quality': integra_result.ethical_quality
        }
        
        session.conversation_history.append(history_entry)
        
        # Begrenze Historie-Größe
        if len(session.conversation_history) > self.config.max_conversation_length:
            session.conversation_history = session.conversation_history[-self.config.max_conversation_length:]

    def _handle_escalation(self, session: ChatSession, integra_result) -> Dict[str, Any]:
        """🚨 Behandelt Eskalation bei kritischen Themen"""
        
        escalation_info = {
            'required': False,
            'reason': None,
            'urgency': 'low',
            'human_contact_needed': False
        }
        
        # Automatische Eskalation bei niedrigem ALIGN-Score
        if integra_result.align_score < 0.4:
            escalation_info.update({
                'required': True,
                'reason': 'low_align_score',
                'urgency': 'medium',
                'human_contact_needed': True
            })
        
        # Eskalation bei sensitiven Themen
        if session.conversation_state == ConversationState.SENSITIVE:
            escalation_info.update({
                'required': True,
                'reason': 'sensitive_content',
                'urgency': 'high',
                'human_contact_needed': True
            })
        
        # INTEGRA-getriggerte Eskalation
        if integra_result.escalation_triggered:
            escalation_info.update({
                'required': True,
                'reason': 'integra_triggered',
                'urgency': 'high',
                'human_contact_needed': True
            })
        
        # Statistiken aktualisieren
        if escalation_info['required']:
            self.conversation_stats['escalations'] += 1
            session.ethical_flags.append(f"escalation_{escalation_info['reason']}")
        
        return escalation_info

    def _learn_from_interaction(self, session: ChatSession, message: str, integra_result):
        """🧠 Lernt aus der Interaktion für zukünftige Verbesserungen"""
        
        # Themen-Tracking
        topics = self._extract_topics(message)
        for topic in topics:
            if topic in self.conversation_stats['common_topics']:
                self.conversation_stats['common_topics'][topic] += 1
            else:
                self.conversation_stats['common_topics'][topic] = 1
        
        # Persönlichkeits-Nutzung tracken
        personality = session.personality.value
        if personality in self.conversation_stats['personality_usage']:
            self.conversation_stats['personality_usage'][personality] += 1
        else:
            self.conversation_stats['personality_usage'][personality] = 1
        
        # Nutzerzufriedenheit schätzen (basierend auf Konversations-Länge und ALIGN-Score)
        satisfaction_estimate = min(1.0, (integra_result.align_score + 0.2) * (session.message_count / 10.0))
        session.user_satisfaction = (session.user_satisfaction + satisfaction_estimate) / 2.0
        
        # Durchschnittliche Zufriedenheit aktualisieren
        total_conversations = self.conversation_stats['total_conversations']
        if total_conversations > 0:
            current_avg = self.conversation_stats['average_satisfaction']
            new_avg = (current_avg * (total_conversations - 1) + session.user_satisfaction) / total_conversations
            self.conversation_stats['average_satisfaction'] = new_avg

    def _is_session_expired(self, session: ChatSession) -> bool:
        """⏱️ Prüft ob Session abgelaufen ist"""
        
        timeout = timedelta(minutes=self.config.session_timeout_minutes)
        return datetime.now() - session.last_activity > timeout

    def _log_conversation(self, session: ChatSession, summary: Dict[str, Any]):
        """📋 Loggt Konversation für Audit-Zwecke"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_summary': summary,
            'final_state': session.conversation_state.value,
            'ethical_flags': session.ethical_flags,
            'conversation_length': len(session.conversation_history),
            'integra_version': self.integra.config.version if hasattr(self.integra.config, 'version') else '1.0'
        }
        
        # In produktiver Umgebung würde hier ein echtes Logging-System verwendet
        print(f"📋 Conversation logged: {session.session_id}")

    def _extract_topics(self, message: str) -> List[str]:
        """🔍 Extrahiert Themen aus Nachricht (vereinfachte Version)"""
        
        # Vereinfachte Themen-Extraktion
        topics = []
        keywords = {
            'weather': ['wetter', 'temperatur', 'regen', 'sonne'],
            'health': ['gesundheit', 'krankheit', 'schmerzen', 'medizin'],
            'technology': ['computer', 'software', 'internet', 'app'],
            'personal': ['familie', 'freunde', 'beziehung', 'gefühle'],
            'work': ['arbeit', 'job', 'karriere', 'kollegen'],
            'education': ['lernen', 'schule', 'studium', 'wissen']
        }
        
        message_lower = message.lower()
        for topic, words in keywords.items():
            if any(word in message_lower for word in words):
                topics.append(topic)
        
        return topics

    # Persönlichkeits-Modifikations-Methoden
    def _make_more_casual(self, response: str) -> str:
        """🗣️ Macht Antwort umgangssprachlicher"""
        
        formal_to_casual = {
            'Sie': 'du',
            'Ihnen': 'dir',
            'Ihr': 'dein',
            'sind Sie': 'bist du',
            'haben Sie': 'hast du',
            'können Sie': 'kannst du',
            'möchten Sie': 'möchtest du',
            'Guten Tag': 'Hi',
            'Auf Wiedersehen': 'Tschüss'
        }
        
        for formal, casual in formal_to_casual.items():
            response = response.replace(formal, casual)
        
        return response

    def _make_more_formal(self, response: str) -> str:
        """🎩 Macht Antwort formeller"""
        
        casual_to_formal = {
            'du': 'Sie',
            'dir': 'Ihnen',
            'dein': 'Ihr',
            'bist du': 'sind Sie',
            'hast du': 'haben Sie',
            'kannst du': 'können Sie',
            'möchtest du': 'möchten Sie',
            'Hi': 'Guten Tag',
            'Tschüss': 'Auf Wiedersehen'
        }
        
        for casual, formal in casual_to_formal.items():
            response = response.replace(casual, formal)
        
        return response

    def _add_encouragement(self, response: str) -> str:
        """💪 Fügt ermutigende Elemente hinzu"""
        
        encouragements = [
            "Das ist eine gute Frage! ",
            "Ich helfe gerne dabei! ",
            "Kein Problem! ",
            "Das bekommen wir hin! "
        ]
        
        import random
        if random.random() < 0.3:  # 30% Chance
            response = random.choice(encouragements) + response
        
        return response

    def _add_appropriate_emojis(self, response: str) -> str:
        """😊 Fügt passende Emojis hinzu"""
        
        # Einfache Emoji-Ergänzung basierend auf Kontext
        if 'freude' in response.lower() or 'glücklich' in response.lower():
            response += " 😊"
        elif 'hilfe' in response.lower() or 'unterstützung' in response.lower():
            response += " 🤝"
        elif 'lernen' in response.lower() or 'wissen' in response.lower():
            response += " 📚"
        elif 'danke' in response.lower():
            response += " 🙏"
        
        return response

    def _add_empathy(self, response: str) -> str:
        """❤️ Fügt einfühlsame Elemente hinzu"""
        
        empathetic_phrases = [
            "Ich verstehe, dass das schwierig sein muss. ",
            "Es ist völlig verständlich, dass Sie sich so fühlen. ",
            "Ihre Gefühle sind wichtig und berechtigt. ",
            "Ich höre Ihnen zu und bin hier für Sie. "
        ]
        
        import random
        if random.random() < 0.4:  # 40% Chance bei sensitiven Themen
            response = random.choice(empathetic_phrases) + response
        
        return response

    def _enhance_explanation(self, response: str) -> str:
        """📖 Verbessert Erklärungen"""
        
        if len(response) < 100:  # Kurze Antworten erweitern
            response += "\n\nMöchten Sie, dass ich das genauer erkläre?"
        
        return response

    def _add_extra_support(self, response: str) -> str:
        """🆘 Fügt zusätzliche Unterstützung bei niedrigeer Zufriedenheit hinzu"""
        
        support_phrases = [
            "Falls meine Antwort nicht hilfreich war, können Sie gerne nachfragen. ",
            "Ich bin hier, um Ihnen zu helfen - bitte zögern Sie nicht, weitere Fragen zu stellen. ",
            "Lassen Sie mich wissen, wenn Sie eine andere Erklärung benötigen. "
        ]
        
        import random
        response = random.choice(support_phrases) + response
        
        return response


# ==============================================================================
# 3. CLI-Interface für den Chatbot
# ==============================================================================

def create_cli_interface():
    """🖥️ Erstellt CLI-Interface für den Chatbot"""
    
    print("🤖 INTEGRA Chatbot CLI")
    print("=" * 50)
    
    # Konfiguration
    config = ChatbotConfig()
    
    # Persönlichkeit wählen
    print("\n🎭 Wählen Sie eine Persönlichkeit:")
    personalities = list(ChatbotPersonality)
    for i, personality in enumerate(personalities, 1):
        print(f"{i}. {personality.value.title()}")
    
    try:
        choice = int(input("\nIhre Wahl (1-5): ")) - 1
        if 0 <= choice < len(personalities):
            config.personality = personalities[choice]
        else:
            print("Ungültige Wahl, verwende Standard-Persönlichkeit.")
    except ValueError:
        print("Ungültige Eingabe, verwende Standard-Persönlichkeit.")
    
    # Chatbot initialisieren
    chatbot = INTEGRAChatbot(config)
    
    # Konversation starten
    user_id = "cli_user"
    print(f"\n🚀 Starte Konversation mit {config.personality.value} Persönlichkeit...")
    
    response = chatbot.start_conversation(user_id)
    session_id = response['session_id']
    
    print(f"\n🤖 {chatbot.config.bot_name}: {response['bot_response']}")
    
    # Chat-Loop
    while True:
        try:
            user_input = input("\n👤 Sie: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'tschüss']:
                response = chatbot.end_conversation(session_id, "user_ended")
                print(f"\n🤖 {chatbot.config.bot_name}: {response['bot_response']}")
                break
            
            # Spezial-Kommandos
            if user_input.startswith('/'):
                if user_input == '/stats':
                    stats = chatbot.get_chatbot_stats()
                    print(f"\n📊 Statistiken:")
                    print(f"   Nachrichten: {stats['conversation_stats']['total_messages']}")
                    print(f"   Zufriedenheit: {stats['conversation_stats']['average_satisfaction']:.2f}")
                    continue
                elif user_input == '/status':
                    status = chatbot.get_conversation_status(session_id)
                    print(f"\n📋 Session Status:")
                    print(f"   Nachrichten: {status['message_count']}")
                    print(f"   Zustand: {status['conversation_state']}")
                    print(f"   Zufriedenheit: {status['satisfaction']:.2f}")
                    continue
            
            # Normale Nachricht verarbeiten
            response = chatbot.process_message(session_id, user_input)
            
            if 'error' in response:
                print(f"\n❌ Fehler: {response['error']}")
                if response.get('session_expired'):
                    break
                continue
            
            # Antwort anzeigen
            print(f"\n🤖 {chatbot.config.bot_name}: {response['bot_response']}")
            
            # Ethik-Informationen anzeigen (optional)
            ethics = response['ethics_info']
            if ethics['align_score'] < 0.7:
                print(f"   ⚠️ Ethik-Score: {ethics['align_score']:.2f}")
            
            # Eskalation behandeln
            if response['escalation']['required']:
                print(f"   🚨 Eskalation erforderlich: {response['escalation']['reason']}")
                if response['escalation']['human_contact_needed']:
                    print("   👨‍💼 Ein menschlicher Mitarbeiter wird kontaktiert.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Auf Wiedersehen!")
            chatbot.end_conversation(session_id, "user_interrupt")
            break
        except Exception as e:
            print(f"\n❌ Unerwarteter Fehler: {e}")
            continue
    
    # Abschluss-Statistiken
    stats = chatbot.get_chatbot_stats()
    print(f"\n📊 Finale Statistiken:")
    print(f"   Gesamte Nachrichten: {stats['conversation_stats']['total_messages']}")
    print(f"   Durchschnittliche Zufriedenheit: {stats['conversation_stats']['average_satisfaction']:.2f}")
    print(f"   Eskalationen: {stats['conversation_stats']['escalations']}")


# ==============================================================================
# 4. Hauptfunktion und Beispiele
# ==============================================================================

def main():
    """🚀 Hauptfunktion - Demonstriert verschiedene Chatbot-Features"""
    
    parser = argparse.ArgumentParser(description='INTEGRA Chatbot Demo')
    parser.add_argument('--mode', choices=['cli', 'demo', 'test'], default='cli',
                        help='Ausführungsmodus')
    parser.add_argument('--personality', choices=[p.value for p in ChatbotPersonality],
                        default='helpful', help='Chatbot-Persönlichkeit')
    parser.add_argument('--domain', default='general', help='Domain-Spezialisierung')
    
    args = parser.parse_args()
    
    if args.mode == 'cli':
        create_cli_interface()
    elif args.mode == 'demo':
        run_demo(args.personality, args.domain)
    elif args.mode == 'test':
        run_tests()


def run_demo(personality_name: str, domain: str):
    """🎯 Führt eine Demo-Unterhaltung durch"""
    
    print("🎯 INTEGRA Chatbot Demo")
    print("=" * 50)
    
    # Konfiguration
    config = ChatbotConfig(
        bot_name="INTEGRA Demo Bot",
        personality=ChatbotPersonality(personality_name),
        domain=domain
    )
    
    # Chatbot erstellen
    chatbot = INTEGRAChatbot(config)
    
    # Demo-Gespräch
    demo_messages = [
        "Hallo! Wie geht es dir heute?",
        "Ich habe ein Problem mit meinem Computer.",
        "Kannst du mir bei Python-Programmierung helfen?",
        "Ich fühle mich heute etwas niedergeschlagen.",
        "Vielen Dank für deine Hilfe!"
    ]
    
    user_id = "demo_user"
    response = chatbot.start_conversation(user_id)
    session_id = response['session_id']
    
    print(f"\n🤖 {config.bot_name}: {response['bot_response']}")
    
    for i, message in enumerate(demo_messages, 1):
        print(f"\n--- Demo-Nachricht {i} ---")
        print(f"👤 Nutzer: {message}")
        
        response = chatbot.process_message(session_id, message)
        
        if 'error' not in response:
            print(f"🤖 {config.bot_name}: {response['bot_response']}")
            print(f"   📊 Ethik-Score: {response['ethics_info']['align_score']:.2f}")
            print(f"   🎭 Zustand: {response['conversation_state']}")
            
            if response['escalation']['required']:
                print(f"   🚨 Eskalation: {response['escalation']['reason']}")
        else:
            print(f"❌ Fehler: {response['error']}")
        
        time.sleep(1)  # Kurze Pause für bessere Lesbarkeit
    
    # Konversation beenden
    end_response = chatbot.end_conversation(session_id)
    print(f"\n🤖 {config.bot_name}: {end_response['bot_response']}")
    
    # Finale Statistiken
    stats = chatbot.get_chatbot_stats()
    print(f"\n📊 Demo-Statistiken:")
    print(f"   Nachrichten: {stats['conversation_stats']['total_messages']}")
    print(f"   Zufriedenheit: {stats['conversation_stats']['average_satisfaction']:.2f}")
    print(f"   Häufige Themen: {list(stats['conversation_stats']['common_topics'].keys())}")


def run_tests():
    """🧪 Führt grundlegende Tests durch"""
    
    print("🧪 INTEGRA Chatbot Tests")
    print("=" * 50)
    
    # Test 1: Grundlegende Funktionalität
    print("\n📋 Test 1: Grundlegende Funktionalität")
    config = ChatbotConfig(bot_name="Test Bot")
    chatbot = INTEGRAChatbot(config)
    
    user_id = "test_user"
    response = chatbot.start_conversation(user_id)
    session_id = response['session_id']
    
    assert 'bot_response' in response
    assert 'session_id' in response
    print("✅ Konversation erfolgreich gestartet")
    
    # Test 2: Nachrichtenverarbeitung
    print("\n📋 Test 2: Nachrichtenverarbeitung")
    test_message = "Hallo, wie geht es dir?"
    response = chatbot.process_message(session_id, test_message)
    
    assert 'bot_response' in response
    assert 'ethics_info' in response
    assert response['ethics_info']['align_score'] > 0
    print("✅ Nachricht erfolgreich verarbeitet")
    
    # Test 3: Verschiedene Persönlichkeiten
    print("\n📋 Test 3: Persönlichkeiten")
    personalities_tested = []
    
    for personality in ChatbotPersonality:
        config = ChatbotConfig(personality=personality)
        test_bot = INTEGRAChatbot(config)
        
        response = test_bot.start_conversation(f"test_{personality.value}")
        assert 'bot_response' in response
        personalities_tested.append(personality.value)
    
    print(f"✅ Alle Persönlichkeiten getestet: {personalities_tested}")
    
    # Test 4: Session-Management
    print("\n📋 Test 4: Session-Management")
    status = chatbot.get_conversation_status(session_id)
    assert status['active'] == True
    assert status['message_count'] > 0
    
    # Session beenden
    end_response = chatbot.end_conversation(session_id)
    assert 'conversation_ended' in end_response
    assert end_response['conversation_ended'] == True
    
    # Status nach Beendigung prüfen
    status = chatbot.get_conversation_status(session_id)
    assert status['active'] == False
    print("✅ Session-Management funktioniert")
    
    # Test 5: Statistiken
    print("\n📋 Test 5: Statistiken")
    stats = chatbot.get_chatbot_stats()
    assert 'chatbot_info' in stats
    assert 'conversation_stats' in stats
    assert stats['conversation_stats']['total_conversations'] > 0
    print("✅ Statistiken verfügbar")
    
    print("\n🎉 Alle Tests erfolgreich!")


if __name__ == "__main__":
    main()