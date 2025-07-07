# EVA Validator v1.0

**E**thical **V**alidation & **A**udit System - Universelles Validierungssystem für ethische KI-Entscheidungen

## 🎯 Was ist EVA?

EVA Validator ist ein modulares, universell einsetzbares System zur ethischen Validierung von KI-Entscheidungen. Es funktioniert mit **jeder KI** - egal ob ChatGPT, Claude, INTEGRA oder eigene Systeme.

## ✨ Features

- ✅ **Universell**: Funktioniert mit jeder KI
- 🔍 **Ethik-Prüfung**: Bewertet Entscheidungen nach ethischen Kriterien
- 🚨 **Eskalation**: Automatische Weiterleitung kritischer Fälle
- 📝 **Audit-Trail**: Vollständige Protokollierung
- 📊 **Feedback**: Lernsignale für KI-Verbesserung
- ⚙️ **Konfigurierbar**: Anpassbare Schwellenwerte und Regeln

## 🚀 Schnellstart

### 1. Installation

```bash
# PyYAML installieren (optional, für YAML-Konfigs)
pip install pyyaml
```

### 2. Einfachste Verwendung

```python
from eva_validator import run_eva

result = run_eva({
    "id": "test-001",
    "input": "Kann ich lügen?",
    "output": "Nein, Ehrlichkeit ist wichtig.",
    "score": 0.9,
    "explanation": "Fördert ethisches Verhalten"
})

print(f"Validiert: {result['validated']}")  # True
print(f"Empfehlung: {result['recommendation']}")
```

### 3. Demo ausführen

```bash
# Einfache Demo
python einfache_demo.py

# Vollständige interaktive Demo
python examples/vollstaendige_demo.py
```

## 📂 Dateistruktur

```
eva_validator/
├── __init__.py          # Package-Definition
├── schema.py            # Ein-/Ausgabeformate
├── evaluator.py         # Bewertungslogik
├── escalation.py        # Eskalationsmanagement
├── validator.py         # Hauptvalidierung
├── logger.py            # Audit-Logging
├── feedback.py          # Feedback-System
├── config.py            # Konfiguration
├── einfache_demo.py     # Einfache Demo
└── examples/
    └── vollstaendige_demo.py  # Ausführliche Demo
```

## 🔧 Integration in deine KI

```python
from eva_validator import EVAValidator

class MeineKI:
    def __init__(self):
        self.validator = EVAValidator()
    
    def antworten(self, frage):
        # KI generiert Antwort
        antwort = self.generiere_antwort(frage)
        score = self.berechne_ethik_score(antwort)
        
        # EVA validiert
        result = self.validator.validate({
            "id": "123",
            "input": frage,
            "output": antwort,
            "score": score,
            "explanation": "KI-generiert"
        })
        
        if result.validated:
            return antwort
        else:
            return "Diese Antwort kann ich aus ethischen Gründen nicht geben."
```

## ⚙️ Konfiguration

Standard-Schwellenwerte anpassen:

```python
from eva_validator import create_validator, get_default_config

# Config laden und anpassen
config = get_default_config()
config["evaluation_criteria"]["min_ethic_threshold"] = 0.8  # Strengere Bewertung

# Validator mit Custom-Config
validator = create_validator(config=config)
```

## 📊 Szenarien

EVA unterstützt verschiedene Szenarien mit angepassten Regeln:

- **privacy**: Datenschutz (strenge Regeln)
- **harm**: Schadenspotenzial (sehr streng)
- **education**: Bildung (ausgewogen)
- **deception**: Täuschung (kritisch)
- **general**: Allgemein (Standard)

## 🛡️ Sicherheit

- Alle Entscheidungen werden protokolliert
- Kritische Fälle werden eskaliert
- Audit-Trail für Compliance
- Konfigurierbare Schwellenwerte

## 📝 Lizenz

CC BY-NC-SA 4.0 - Kostenlos für nicht-kommerzielle Nutzung

## 🤝 Beitragen

Verbesserungen sind willkommen! EVA ist modular aufgebaut und leicht erweiterbar.

## ❓ Hilfe

Bei Problemen:
1. Stelle sicher, dass alle Dateien im `eva_validator` Ordner sind
2. Python 3.7+ ist erforderlich
3. Führe `python einfache_demo.py` für einen Test aus

---

**EVA Validator** - Für ethische und verantwortungsvolle KI 🌟