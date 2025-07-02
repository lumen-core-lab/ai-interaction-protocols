# # -*- coding: utf-8 -*-

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
def **init**(self, *args, **kwargs):
self.config = type(‘Config’, (), {‘system_name’: ‘Mock INTEGRA’, ‘version’: ‘1.0’})()
print("🤖 Mock INTEGRA Light Chatbot initialisiert")

```
    def process_request(self, query, **kwargs):
        return type('Result', (), {
            'response': f"Mock-Antwort für: {query}",
            'align_score': 0.85,
            'ethical_quality': 'good',
            'processing_path': 'mock_path',
            'confidence': 0.8,
            'escalation_triggered': False,
            'timestamp': datetime.now().isoformat()
        })()
   
    def get_system_status(self):
        return {'statistics': {'total_requests': 0}}

INTEGRALight = MockINTEGRALight
create_integra_light = lambda **kwargs: MockINTEGRALight()
```

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

```
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
```

# ==============================================================================

# 2. Hauptklasse - INTEGRA Chatbot

# ==============================================================================

class INTEGRAChatbot:
"""
🤖 INTEGRA-basierter ethischer Chatbot

```
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
   
    if modifiers.get('provide_explanations') and 'warum' in base_response.lower() or 'wie' in base_response.lower():
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
        session.ethical_flags.appen
```