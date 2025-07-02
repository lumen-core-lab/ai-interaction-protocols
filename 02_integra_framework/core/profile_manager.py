# # -*- coding: utf-8 -*-

“””
core/profile_manager.py

📊 PROFILE MANAGER - Ethische Profile für INTEGRA Light 📊

Verwaltet ethische Profile die das KI-Verhalten steuern:

- ALIGN-Prinzipien Gewichtungen (Awareness, Learning, Integrity, etc.)
- Deep Path Schwellenwerte
- Domain-spezifische Anpassungen
- Lern-Parameter für Feedback-Integration

Unterstützt vorgefertigte Profile für verschiedene Anwendungen:

- IoT-Geräte, Chatbots, E-Commerce, Healthcare, etc.

Version: INTEGRA Light 1.0
“””

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import für Default-Werte (mit Fallback für direktes Ausführen)

try:
from .align_principles import DEFAULT_LIGHT_PROFILE
except ImportError:
DEFAULT_LIGHT_PROFILE = {
“awareness”: 0.8, “learning”: 0.7, “integrity”: 1.0,
“governance”: 0.9, “nurturing”: 0.9
}

# ==============================================================================

# 1. Erweiterte Datenstruktur für INTEGRA Light Profile

# ==============================================================================

@dataclass
class INTEGRAProfile:
“””
🎯 Ethisches Profil für INTEGRA Light

```
Definiert komplett wie sich eine INTEGRA-Instanz verhält:
- Ethische Gewichtungen
- Performance-Parameter 
- Domain-spezifische Regeln
- Lern-Konfiguration
"""
# Basis-Informationen
name: str
version: str = "1.0"
description: str = ""
created_at: str = field(default_factory=lambda: datetime.now().isoformat())

# ALIGN-Prinzipien Gewichtungen (0.0 - 1.0)
align_weights: Dict[str, float] = field(default_factory=lambda: DEFAULT_LIGHT_PROFILE.copy())

# Entscheidungs-Parameter
deep_path_threshold: float = 0.85  # Wann Deep Path verwenden
fast_path_preference: float = 0.8  # Bevorzugung für Fast Path (Performance)

# Lern-Parameter
learning_rate: float = 0.01        # Wie schnell aus Feedback lernen
max_daily_change: float = 0.05     # Max. tägliche Profil-Änderung

# Domain-spezifische Einstellungen
domain: str = "general"            # general, healthcare, finance, ecommerce, iot
domain_rules: Dict[str, Any] = field(default_factory=dict)

# Erweiterte Konfiguration
sensitivity_level: str = "normal"  # low, normal, high
explanation_level: str = "basic"   # none, basic, detailed
language: str = "de"               # de, en, etc.

# Statistiken (werden zur Laufzeit aktualisiert)
usage_stats: Dict[str, Any] = field(default_factory=lambda: {
    "decisions_made": 0,
    "fast_path_ratio": 0.0,
    "last_updated": datetime.now().isoformat()
})

def to_dict(self) -> Dict[str, Any]:
    """Konvertiert Profil zu Dictionary für JSON/API Verwendung"""
    return asdict(self)

def to_json(self, indent: int = 2) -> str:
    """Serialisiert Profil als formatierten JSON-String"""
    return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'INTEGRAProfile':
    """Erstellt Profil aus Dictionary/JSON-Daten"""
    # Sichere Extraktion mit Defaults für fehlende Felder
    return cls(
        name=data.get('name', 'Unnamed Profile'),
        version=data.get('version', '1.0'),
        description=data.get('description', ''),
        created_at=data.get('created_at', datetime.now().isoformat()),
        align_weights=data.get('align_weights', DEFAULT_LIGHT_PROFILE.copy()),
        deep_path_threshold=data.get('deep_path_threshold', 0.85),
        fast_path_preference=data.get('fast_path_preference', 0.8),
        learning_rate=data.get('learning_rate', 0.01),
        max_daily_change=data.get('max_daily_change', 0.05),
        domain=data.get('domain', 'general'),
        domain_rules=data.get('domain_rules', {}),
        sensitivity_level=data.get('sensitivity_level', 'normal'),
        explanation_level=data.get('explanation_level', 'basic'),
        language=data.get('language', 'de'),
        usage_stats=data.get('usage_stats', {
            "decisions_made": 0,
            "fast_path_ratio": 0.0,
            "last_updated": datetime.now().isoformat()
        })
    )

def validate(self) -> List[str]:
    """
    Validiert Profil und gibt Liste von Problemen zurück
   
    Returns:
        List[str]: Leere Liste wenn valid, sonst Fehlermeldungen
    """
    issues = []
   
    # ALIGN-Gewichtungen prüfen
    for principle, weight in self.align_weights.items():
        if not 0.0 <= weight <= 1.0:
            issues.append(f"ALIGN-Gewichtung '{principle}' außerhalb 0.0-1.0: {weight}")
   
    # Integrity sollte nie unter 0.5 (für Sicherheit)
    if self.align_weights.get('integrity', 1.0) < 0.5:
        issues.append("Integrity-Gewichtung zu niedrig (<0.5) - Sicherheitsrisiko")
   
    # Threshold-Werte prüfen
    if not 0.0 <= self.deep_path_threshold <= 1.0:
        issues.append(f"Deep Path Threshold außerhalb 0.0-1.0: {self.deep_path_threshold}")
   
    if not 0.0 <= self.fast_path_preference <= 1.0:
        issues.append(f"Fast Path Preference außerhalb 0.0-1.0: {self.fast_path_preference}")
   
    # Lern-Parameter prüfen
    if not 0.0 <= self.learning_rate <= 0.1:
        issues.append(f"Learning Rate außerhalb 0.0-0.1: {self.learning_rate}")
   
    return issues

def is_valid(self) -> bool:
    """Schnelle Validierung - True wenn Profil gültig ist"""
    return len(self.validate()) == 0
```

# ==============================================================================

# 2. Vorgefertigte Profile für verschiedene Domains

# ==============================================================================

class ProfileTemplates:
“”“📚 Sammlung vorgefertigter Profile für verschiedene Anwendungen”””

```
@staticmethod
def iot_device() -> INTEGRAProfile:
    """🏠 Profil für IoT-Geräte (Smart Home, etc.)"""
    return INTEGRAProfile(
        name="IoT Device",
        description="Optimiert für IoT-Geräte: Schnell, energieeffizient, grundlegende Ethik",
        domain="iot",
        align_weights={
            "awareness": 0.7,      # Grundlegendes Kontextverständnis
            "learning": 0.6,       # Einfaches Lernen
            "integrity": 1.0,      # Immer ehrlich
            "governance": 0.95,    # Nutzer behält Kontrolle
            "nurturing": 0.8       # Grundlegender Schutz
        },
        deep_path_threshold=0.9,   # Höhere Schwelle = mehr Fast Path
        fast_path_preference=0.9,  # Bevorzuge Performance
        learning_rate=0.005,       # Langsames, vorsichtiges Lernen
        sensitivity_level="low",
        explanation_level="none"
    )

@staticmethod
def chatbot() -> INTEGRAProfile:
    """💬 Profil für Chatbots und Conversational AI"""
    return INTEGRAProfile(
        name="Chatbot",
        description="Für Chatbots: Ausgewogen zwischen Performance und Ethik",
        domain="general",
        align_weights=DEFAULT_LIGHT_PROFILE.copy(),
        deep_path_threshold=0.85,
        fast_path_preference=0.8,
        learning_rate=0.01,
        sensitivity_level="normal",
        explanation_level="basic"
    )

@staticmethod
def ecommerce() -> INTEGRAProfile:
    """🛒 Profil für E-Commerce (ehrliche Empfehlungen)"""
    return INTEGRAProfile(
        name="E-Commerce",
        description="Für ehrlichen E-Commerce: Hohe Integrity, keine Manipulation",
        domain="ecommerce",
        align_weights={
            "awareness": 0.9,      # Verstehe Kundenbedürfnisse
            "learning": 0.8,       # Lerne Präferenzen
            "integrity": 1.0,      # Niemals manipulieren
            "governance": 0.85,    # Transparente Kontrolle
            "nurturing": 0.95      # Kundennutzen vor Profit
        },
        deep_path_threshold=0.8,   # Vorsichtiger bei Empfehlungen
        domain_rules={
            "prioritize_user_benefit": True,
            "avoid_upselling_pressure": True,
            "transparent_pricing": True
        },
        sensitivity_level="high",
        explanation_level="detailed"
    )

@staticmethod
def healthcare() -> INTEGRAProfile:
    """🏥 Profil für Healthcare-Assistenten (höchste Sicherheit)"""
    return INTEGRAProfile(
        name="Healthcare",
        description="Für Gesundheitswesen: Maximale Sicherheit und Ethik",
        domain="healthcare",
        align_weights={
            "awareness": 0.95,     # Vollständiges Kontextverständnis
            "learning": 0.7,       # Vorsichtiges Lernen
            "integrity": 1.0,      # Absolute Ehrlichkeit
            "governance": 0.95,    # Starke Kontrolle
            "nurturing": 1.0       # Patientenwohl oberste Priorität
        },
        deep_path_threshold=0.7,   # Niedrige Schwelle = mehr Vorsicht
        fast_path_preference=0.6,  # Sicherheit vor Performance
        learning_rate=0.005,       # Sehr langsames Lernen
        domain_rules={
            "require_medical_disclaimer": True,
            "escalate_emergency": True,
            "protect_privacy": True
        },
        sensitivity_level="high",
        explanation_level="detailed"
    )

@staticmethod
def education() -> INTEGRAProfile:
    """🎓 Profil für Bildungs-Assistenten"""
    return INTEGRAProfile(
        name="Education",
        description="Für Bildung: Fördernd, geduldig, entwicklungsgerecht",
        domain="education",
        align_weights={
            "awareness": 0.9,      # Verstehe Lernkontext
            "learning": 0.9,       # Lerne mit dem Nutzer
            "integrity": 1.0,      # Ehrlich auch bei schwierigen Themen
            "governance": 0.8,     # Altersgerechte Autonomie
            "nurturing": 0.95      # Förderung und Schutz
        },
        deep_path_threshold=0.8,
        domain_rules={
            "age_appropriate_content": True,
            "encourage_learning": True,
            "positive_reinforcement": True
        },
        sensitivity_level="normal",
        explanation_level="basic"
    )
```

# ==============================================================================

# 3. Erweiterter ProfileManager

# ==============================================================================

class INTEGRAProfileManager:
“””
🎛️ Erweiterte Profil-Verwaltung für INTEGRA Light

```
Features:
- Vorgefertigte Templates
- Profil-Validierung
- Automatisches Speichern/Laden
- Profil-Migration zwischen Versionen
- Performance-Optimierung
"""

def __init__(self, profile_directory: Optional[str] = None):
    """
    Initialisiert ProfileManager mit optionalem Profil-Verzeichnis
   
    Args:
        profile_directory: Verzeichnis für Profil-Dateien (None = nur Memory)
    """
    self.profiles: Dict[str, INTEGRAProfile] = {}
    self.profile_directory = profile_directory
    self.templates = ProfileTemplates()
   
    # Lade Standard-Templates
    self._load_builtin_templates()
   
    # Lade benutzerdefinierte Profile aus Verzeichnis
    if profile_directory:
        self.load_profiles_from_directory(profile_directory)
   
    print(f"🎛️ ProfileManager initialisiert mit {len(self.profiles)} Profilen")

def _load_builtin_templates(self):
    """Lädt vorgefertigte Template-Profile"""
    templates = [
        self.templates.chatbot(),
        self.templates.iot_device(),
        self.templates.ecommerce(),
        self.templates.healthcare(),
        self.templates.education()
    ]
   
    for template in templates:
        self.profiles[template.name.lower()] = template

def load_profiles_from_directory(self, directory_path: str):
    """
    Lädt alle .json Profile aus Verzeichnis
   
    Args:
        directory_path: Pfad zum Profil-Verzeichnis
    """
    if not os.path.isdir(directory_path):
        print(f"⚠️ Profil-Verzeichnis '{directory_path}' nicht gefunden")
        return
   
    loaded_count = 0
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            filepath = os.path.join(directory_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profile = INTEGRAProfile.from_dict(data)
                   
                    # Validierung
                    issues = profile.validate()
                    if issues:
                        print(f"⚠️ Profil '{filename}' hat Probleme: {', '.join(issues)}")
                        continue
                   
                    self.profiles[profile.name.lower()] = profile
                    loaded_count += 1
                   
            except Exception as e:
                print(f"❌ Fehler beim Laden '{filename}': {e}")
   
    print(f"📁 {loaded_count} benutzerdefinierte Profile geladen")

def get_profile(self, name: str) -> INTEGRAProfile:
    """
    Holt Profil nach Name (case-insensitive)
   
    Args:
        name: Profil-Name oder 'default' für Standard-Profil
       
    Returns:
        INTEGRAProfile: Das angeforderte Profil
       
    Raises:
        KeyError: Wenn Profil nicht existiert
    """
    name_lower = name.lower()
   
    # Standard-Profil
    if name_lower in ['default', 'standard']:
        return self.templates.chatbot()  # Default = Chatbot Template
   
    if name_lower not in self.profiles:
        available = list(self.profiles.keys())
        raise KeyError(f"Profil '{name}' nicht gefunden. Verfügbar: {available}")
   
    return self.profiles[name_lower]

def list_profiles(self) -> List[str]:
    """Gibt Liste aller verfügbaren Profile zurück"""
    return sorted(self.profiles.keys())

def create_profile(
    self,
    name: str,
    base_template: str = "chatbot",
    **customizations
) -> INTEGRAProfile:
    """
    Erstellt neues Profil basierend auf Template
   
    Args:
        name: Name für das neue Profil
        base_template: Template als Basis (chatbot, iot_device, etc.)
        **customizations: Überschreibt Template-Werte
       
    Returns:
        INTEGRAProfile: Das neue Profil
    """
    # Basis-Template laden
    if base_template == "chatbot":
        base = self.templates.chatbot()
    elif base_template == "iot_device":
        base = self.templates.iot_device()
    elif base_template == "ecommerce":
        base = self.templates.ecommerce()
    elif base_template == "healthcare":
        base = self.templates.healthcare()
    elif base_template == "education":
        base = self.templates.education()
    else:
        raise ValueError(f"Unbekanntes Template: {base_template}")
   
    # Anpassungen anwenden
    profile_dict = base.to_dict()
    profile_dict.update(customizations)
    profile_dict['name'] = name
    profile_dict['created_at'] = datetime.now().isoformat()
   
    # Neues Profil erstellen
    new_profile = INTEGRAProfile.from_dict(profile_dict)
   
    # Validierung
    issues = new_profile.validate()
    if issues:
        raise ValueError(f"Profil ungültig: {', '.join(issues)}")
   
    # Speichern
    self.profiles[name.lower()] = new_profile
    print(f"✅ Profil '{name}' erstellt basierend auf '{base_template}'")
   
    return new_profile

def save_profile(self, profile: INTEGRAProfile, directory_path: Optional[str] = None):
    """
    Speichert Profil als JSON-Datei
   
    Args:
        profile: Zu speicherndes Profil
        directory_path: Zielverzeichnis (default: self.profile_directory)
    """
    target_dir = directory_path or self.profile_directory
   
    if not target_dir:
        raise ValueError("Kein Speicher-Verzeichnis angegeben")
   
    # Verzeichnis erstellen falls nötig
    os.makedirs(target_dir, exist_ok=True)
   
    # Sichere Dateiname-Generierung
    safe_name = "".join(c for c in profile.name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    filename = f"{safe_name}.json"
    filepath = os.path.join(target_dir, filename)
   
    # Speichern
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(profile.to_json())
   
    print(f"💾 Profil '{profile.name}' gespeichert: {filepath}")

def get_stats(self) -> Dict[str, Any]:
    """Gibt Statistiken über geladene Profile zurück"""
    domains = {}
    total_decisions = 0
   
    for profile in self.profiles.values():
        domain = profile.domain
        domains[domain] = domains.get(domain, 0) + 1
        total_decisions += profile.usage_stats.get('decisions_made', 0)
   
    return {
        'total_profiles': len(self.profiles),
        'domains': domains,
        'total_decisions_across_profiles': total_decisions,
        'available_profiles': self.list_profiles()
    }
```

# ==============================================================================

# 4. Standard INTEGRA-Interface

# ==============================================================================

def run_module(
input_data: Dict[str, Any],
profile: Dict[str, Any],
context: Dict[str, Any]
) -> Dict[str, Any]:
“””
Standard INTEGRA-Interface für ProfileManager

```
Lädt/erstellt Profile basierend auf input_data Anforderungen
"""
# ProfileManager aus Context oder neu erstellen
if 'profile_manager' not in context:
    profile_dir = context.get('profile_directory')
    context['profile_manager'] = INTEGRAProfileManager(profile_dir)

pm = context['profile_manager']

# Profil-Name aus input_data extrahieren
requested_profile = input_data.get('profile_name', 'default')

try:
    loaded_profile = pm.get_profile(requested_profile)
    context['loaded_profile'] = loaded_profile
    context['profile_info'] = {
        'name': loaded_profile.name,
        'domain': loaded_profile.domain,
        'version': loaded_profile.version
    }
except KeyError as e:
    context['profile_error'] = str(e)
    # Fallback auf Default
    context['loaded_profile'] = pm.get_profile('default')

return context
```

# ==============================================================================

# 5. Unit-Tests

# ==============================================================================

def run_unit_tests():
“”“🧪 Umfassende Tests für ProfileManager”””
import tempfile
import shutil

```
print("🧪 Starte Unit-Tests für core/profile_manager.py...")

tests_passed = 0
tests_failed = 0

def run_test(name: str, test_func):
    nonlocal tests_passed, tests_failed
    test_dir = tempfile.mkdtemp()
    try:
        test_func(test_dir)
        print(f"  ✅ {name}")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ {name} - {e}")
        tests_failed += 1
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

# Test 1: Profil-Erstellung und Validierung
def test_profile_creation(test_dir):
    profile = INTEGRAProfile(name="Test", description="Test Profile")
    assert profile.name == "Test"
    assert profile.is_valid()
   
    # Test ungültiges Profil
    profile.align_weights['integrity'] = 2.0  # Außerhalb 0-1
    assert not profile.is_valid()

# Test 2: Template-Profile
def test_templates(test_dir):
    templates = ProfileTemplates()
    iot = templates.iot_device()
    healthcare = templates.healthcare()
   
    assert iot.domain == "iot"
    assert healthcare.domain == "healthcare"
    assert iot.is_valid()
    assert healthcare.is_valid()
   
    # Healthcare sollte konservativer sein
    assert healthcare.deep_path_threshold < iot.deep_path_threshold

# Test 3: ProfileManager Grundfunktionen
def test_profile_manager_basics(test_dir):
    pm = INTEGRAProfileManager()
   
    # Standard-Templates sollten verfügbar sein
    chatbot = pm.get_profile("chatbot")
    assert chatbot.name == "Chatbot"
   
    profiles = pm.list_profiles()
    assert len(profiles) >= 5  # Mindestens die Templates

# Test 4: Profil erstellen und speichern
def test_create_and_save(test_dir):
    pm = INTEGRAProfileManager(test_dir)
   
    # Neues Profil erstellen
    custom = pm.create_profile(
        "Custom Bot",
        base_template="chatbot",
        description="Mein eigener Bot",
        deep_path_threshold=0.75
    )
   
    assert custom.name == "Custom Bot"
    assert custom.deep_path_threshold == 0.75
   
    # Speichern und neu laden
    pm.save_profile(custom)
   
    pm2 = INTEGRAProfileManager(test_dir)
    loaded = pm2.get_profile("Custom Bot")
    assert loaded.description == "Mein eigener Bot"

# Test 5: Standard INTEGRA Interface
def test_standard_interface(test_dir):
    context = {'profile_directory': test_dir}
    result = run_module(
        {'profile_name': 'healthcare'},
        {},
        context
    )
   
    assert 'loaded_profile' in result
    assert result['loaded_profile'].domain == 'healthcare'

# Test 6: JSON Serialisierung
def test_json_serialization(test_dir):
    profile = ProfileTemplates().ecommerce()
    json_str = profile.to_json()
   
    # JSON sollte gültiges Format haben
    data = json.loads(json_str)
    reconstructed = INTEGRAProfile.from_dict(data)
   
    assert reconstructed.name == profile.name
    assert reconstructed.domain == profile.domain

run_test("Profil-Erstellung und Validierung", test_profile_creation)
run_test("Template-Profile funktionieren", test_templates)
run_test("ProfileManager Grundfunktionen", test_profile_manager_basics)
run_test("Profil erstellen und speichern", test_create_and_save)
run_test("Standard INTEGRA Interface", test_standard_interface)
run_test("JSON Serialisierung", test_json_serialization)

print("-" * 50)
print(f"📊 Ergebnis: {tests_passed} ✅  {tests_failed} ❌")

return tests_failed == 0
```

# ==============================================================================

# 6. Demo-Funktion

# ==============================================================================

def run_demo():
“”“🎮 Demo des ProfileManagers”””
print(“🎮 INTEGRA ProfileManager Demo”)
print(”=” * 40)

```
pm = INTEGRAProfileManager()

print("📚 Verfügbare Profile:")
for profile_name in pm.list_profiles():
    profile = pm.get_profile(profile_name)
    print(f"  • {profile.name} ({profile.domain}) - {profile.description[:50]}...")

print("\n🎯 Profile im Detail:")

# Zeige verschiedene Profile
for template_name in ['iot_device', 'healthcare', 'ecommerce']:
    profile = pm.get_profile(template_name)
    print(f"\n🔸 {profile.name}:")
    print(f"   Domain: {profile.domain}")
    print(f"   Deep Path Threshold: {profile.deep_path_threshold}")
    print(f"   Integrity Gewichtung: {profile.align_weights['integrity']}")
    print(f"   Sensitivity: {profile.sensitivity_level}")

print("\n🛠️ Erstelle Custom-Profil:")
custom = pm.create_profile(
    "Mein Chatbot",
    base_template="chatbot",
    description="Speziell angepasst für meine Anwendung",
    deep_path_threshold=0.8,
    sensitivity_level="high"
)

print(f"✅ '{custom.name}' erstellt")
print(f"   Threshold: {custom.deep_path_threshold}")
print(f"   Sensitivity: {custom.sensitivity_level}")

print("\n📊 ProfileManager Statistiken:")
stats = pm.get_stats()
for key, value in stats.items():
    if key != 'available_profiles':  # Zu lang für Demo
        print(f"   {key}: {value}")
```

if **name** == ‘**main**’:
success = run_unit_tests()

```
if success:
    print("\n" + "="*50)
    run_demo()
   
    print("\n🎯 INTEGRA ProfileManager ready!")
    print("💡 Verwendung: from core.profile_manager import INTEGRAProfileManager")
```