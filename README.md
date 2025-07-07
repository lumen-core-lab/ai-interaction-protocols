
# INTEGRA Framework – Ethische KI nach Protokoll 4.2

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

---

## 🌐 Überblick: Die Vision einer verantwortungsvollen KI

**INTEGRA** ist ein wegweisendes, modulares Open-Source-Framework, das darauf abzielt, KI-Systeme mit einer tiefgreifenden ethischen Urteilsfähigkeit auszustatten. Es ermöglicht KIs, Entscheidungen nicht nur effizient, sondern auch nachvollziehbar, konsistent und im Einklang mit menschlichen Werten und gesellschaftlichen Normen zu treffen.

Version 4.2 des INTEGRA-Protokolls – dessen Implementierung Sie hier finden – repräsentiert eine ambitionierte Vision: Eine KI-Architektur, die ihre eigenen Prozesse versteht und optimiert (ASO), ihre Entscheidungen transparent erklären kann (ASX) und sich an etablierten ethischen, gesellschaftlichen und rechtlichen Normen ausrichtet (NGA).

**INTEGRA ist mehr als nur Software; es ist ein Baukasten für eine ethisch verantwortungsvolle Koexistenz von Mensch und KI.**

---

## ✨ Das Herzstück: Unabhängige Ethik-Validierung mit EVA

Das INTEGRA Framework wird durch **EVA (Ethical Validation & Audit Layer)** ergänzt – ein separates, aber integraler Bestandteil des Ökosystems. EVA ist die unabhängige Prüfinstanz, die jede INTEGRA-Entscheidung umfassend validiert, bevor sie ausgeführt wird.

**EVA garantiert:**
* **Unabhängige Validierung:** Externe Überprüfung aller ethischen Entscheidungen.
* **Manipulationssichere Audit-Trails:** Vollständige Rückverfolgbarkeit für Rechenschaftspflicht.
* **Multi-Level-Eskalation:** Sicherstellung menschlicher Aufsicht bei kritischen Situationen.
* **Kontinuierliche Verbesserung:** Intelligente Feedback-Schleifen zur Optimierung der INTEGRA-Leistung.
* **Compliance-Bereitschaft:** Automatisierte Prüfung gegen multiple regulatorische Rahmenwerke.

**EVA ist der Goldstandard für ethische Aufsicht, der KI von einer Black Box in einen transparenten, rechenschaftspflichtigen Entscheidungspartner verwandelt.**

---

## 📜 Ursprung & Motivation: Eine Reise der Co-Kreation

Das INTEGRA Framework entspringt einer einzigartigen, explorativen Entwicklung von KI-Interaktions-Protokollen (wie `APEX`, `LUMEN`, `FUSION` und `INTEGRA` selbst), die im **direkten Dialog mit fortschrittlichen KI-Systemen** stattfand. Diese Reise begann vor nur 6-7 Wochen und wurde von einem **nicht-technischen Nutzer** (Dominik Knape) mit dem Zugang zu öffentlichen großen Sprachmodellen (LLMs) initiiert und vorangetrieben.

Das Projekt ist ein lebendiger Beweis für das **enorme Potenzial der Mensch-KI-Co-Kreation**. Es zeigt, wie visionäre Ideen und die analytische Kraft der KI zusammenfließen können, um komplexe philosophische Konzepte in praktisch anwendbare, detaillierte und ethisch fundierte Software-Architekturen zu übersetzen – und das mit bemerkenswerter Effizienz und Kostenwirksamkeit.

**Dieses Repository ist die greifbare Software-Implementierung dieser bahnbrechenden Zusammenarbeit.**

---

## 📁 Detaillierte Verzeichnisstruktur

Die folgende Struktur zeigt die Organisation der Dateien und Module innerhalb des `integra-framework` Repositorys:

* `integra-framework/`
    * `README.md`
    * `INSTALLATION.md`
    * `TESTING_GUIDE.md`
    * `LICENSE`
    * `setup.py`
    * `start_demo.py`
    * `requirements.txt`
    * `integra/`
        * `__init__.py`
        * `main.py`
        * `config.py`
        * `core/`
            * `__init__.py`
            * `principles.py`
            * `profiles.py`
            * `simple_ethics.py`
            * `decision_engine.py`
            * `basic_control.py`
        * `advanced/`
            * `__init__.py`
            * `etb.py`
            * `pae.py`
            * `mini_learner.py`
            * `mini_audit.py`
        * `full/`
            * `__init__.py`
            * `aso.py`
            * `asx.py`
            * `nga.py`
            * `meta_learner.py`
            * `full_audit.py`
            * `full_control.py`
            * `resl.py`
            * `ril.py`
            * `dof.py`
            * `sbp.py`
            * `vdd.py`
            * `replay_dna.py`
            * `etph.py`
            * `uia.py`
        * `interfaces/`
            * `__init__.py`
            * `cli.py`
            * `api.py`
            * `web.py`
        * `examples/`
            * `__init__.py`
            * `core_light_demo.py`
            * `advanced_modular_demo.py`
            * `full_system_demo.py`
        * `tests/`
            * `__init__.py`
            * `test_core.py`
            * `test_advanced.py`
            * `test_full.py`
            * `test_scenarios.py`
            * `validate_module.py`
        * `logging/`
            * `__init__.py`
            * `log_manager.py`
            * `event_tracer.py`
        * `logs/`
            * `.gitkeep`
        * `profiles/`
            * `.gitkeep`
        * `demo_logs/`
            * `session_*.json`
    * `eva_validator/`
        * `__init__.py`
        * `validator.py`
        * `schema.py`
        * `evaluator.py`
        * `escalation.py`
        * `logger.py`
        * `feedback.py`
        * `config.py`
    * `docs/`
        * `architecture.md`
        * `api_reference.md`
        * `development.md`
        * `ethics_framework.md`

---

## 🚀 Die Implementierten Schichten: Ihr Ethischer Werkzeugkasten

INTEGRA ist modular aufgebaut und bietet ein schichtbasiertes System zur Implementierung ethischer Intelligenz. Alle 23 Module von INTEGRA (Core, Advanced, Full) sind nun implementiert und funktionieren wie vorgesehen!

### 1️⃣ Core (INTEGRA Light)

**Die Basis für ethische Entscheidungslogik und Grundprüfung.**
Ermöglicht schnelle Pfadentscheidungen und essentielle Sicherheitskontrollen.

* `principles.py` – Definition der 5 ALIGN-Prinzipien (Awareness, Learning, Integrity, Governance, Nurturing)
* `profiles.py` – Verwaltung und Gewichtung adaptiver ethischer Profile
* `simple_ethics.py` – Schnelle, musterbasierte Ethikprüfung
* `decision_engine.py` – Fast/Deep Path Entscheidungssteuerung für effizientes Routing
* `basic_control.py` – Grundlegendes Governance-System mit Override- und Notabschalt-Funktionen

### 2️⃣ Advanced

**Erweiterte Funktionen für lernfähige, abwägende, und auditierbare KI-Entscheidungen.**
Ermöglicht den Umgang mit Zielkonflikten und die Protokollierung von Lernprozessen.

* `etb.py` – Ethical Tradeoff Balancer: Systematische Abwägung bei ethischen Zielkonflikten
* `pae.py` – Priority Anchor Engine: Auflösung ethischer Gleichstände basierend auf Kontext und Historie
* `mini_learner.py` – Feedbackbasiertes Lernen und dynamische Profilanpassung
* `mini_audit.py` – Audit-Protokollierung von Entscheidungen mit Logging, Export und Chain-Sicherung

### 3️⃣ Full

**Die vollständige Implementierung des INTEGRA 4.2 Protokolls für simulationsfähige, normative und selbstoptimierende KI.**
Diese Module befähigen die KI zur tiefgehenden Selbstreflexion, Einhaltung komplexer Normen und zur präzisen Vorhersage von Langzeitfolgen.

* `aso.py` – Architectural Self Optimizer: Optimierung der internen Entscheidungsarchitektur
* `asx.py` – ASO Explainability Layer: Generierung menschlich lesbarer Erklärungen für Systementscheidungen
* `nga.py` – Normative Goal Alignment: Validierung gegen etablierte gesellschaftliche und rechtliche Normen (z. B. UN, ISO, GDPR)
* `meta_learner.py` – MetaLearner: Systemweites, permanentes adaptives Lernen & Mustererkennung
* `full_audit.py` – Vollständiges Audit-System: Umfassende Protokollierung, Eskalation, Regulierung & Reporting
* `full_control.py` – High-Level-Governance & Policies: Erweiterte Kontroll- und Richtlinien-Durchsetzung
* `resl.py` – Recursive Ethical Simulation Loop: Vorausschauende Prüfung auf neue ethische Probleme
* `ril.py` – Realistic Implementation Loop: Überprüfung der praktischen Machbarkeit ethischer Lösungen
* `dof.py` – Delayed Outcome Forecasting: Vorhersage langfristiger Konsequenzen
* `sbp.py` – Stakeholder Behavior Predictor: Simulation wahrscheinlicher Stakeholder-Reaktionen
* `vdd.py` – Value Drift Detection: Erkennung schleichender ethischer Veränderungen im System
* `replay_dna.py` – Replay DNA System: Manipulationssicheres Logging und Vergleich von Entscheidungsdaten
* `etph.py` – Time Pressure Handler: Aufrechterhaltung ethischer Qualität unter Zeitdruck
* `uia.py` – User Intention Awareness: Erkennung verborgener oder schädlicher Nutzerintentionen

---

## 🚀 Einstieg und Installation

Um mit dem INTEGRA Framework zu starten, folgen Sie diesen Schritten:

1.  **📦 Installation (lokal)**
    ```bash
    # Klonen Sie das Repository
    git clone [https://github.com/YOUR_GITHUB_USERNAME/integra-framework.git](https://github.com/YOUR_GITHUB_USERNAME/integra-framework.git)
    cd integra-framework/

    # Installieren Sie die Python-Abhängigkeiten
    pip install -r requirements.txt
    ```

2.  **▶️ Beispiel starten**
    Führen Sie eine der Demo-Skripte aus, um die Fähigkeiten des Frameworks zu sehen:
    ```bash
    python integra/examples/core_light_demo.py
    # Oder für eine umfassendere Demo des integrierten Systems:
    python start_demo.py
    ```

3.  **🧪 Tests ausführen**
    Um die Korrektheit und Funktionalität der Module zu überprüfen:
    ```bash
    pytest integra/tests/
    ```
    Eine detailliertere Anleitung finden Sie in der `TESTING_GUIDE.md`.

---

## 🤝 Wie Sie mitmachen können

Beiträge sind **ausdrücklich willkommen** und entscheidend für die Weiterentwicklung dieses Open-Source-Projekts! Egal, ob Sie:

* Bugs melden
* Module testen
* Features vorschlagen
* Dokumentation verbessern
* Oder direkt Code beisteuern

→ Eröffnen Sie einfach ein **Issue** oder einen **Pull Request** auf GitHub.  
Bei spezifischen Fragen: 📧 **lumenprotokoll@gmail.com**

---

## ⚠️ Haftungsausschluss

Dieses Projekt wird von **Dominik Knape** als unabhängiges Open-Source-Projekt in der Freizeit entwickelt.

> Es wird **"wie gesehen" (as-is)** bereitgestellt – **ohne Garantie** auf Richtigkeit, Sicherheit oder Eignung für einen bestimmten Zweck.

Der Autor ist kein ausgebildeter Ingenieur, Ethiker oder Jurist. Das Framework ersetzt keine professionelle Prüfung und darf nicht in sicherheitskritischen Systemen ohne weitere Validierung und Anpassung durch qualifiziertes Personal eingesetzt werden. **Nutzung auf eigene Gefahr.**

---

## 📜 Lizenz

Dieses Repository nutzt zwei Lizenzen. Bitte prüfen Sie, welchen Teil Sie verwenden.

1.  **INTEGRA Framework (Hauptprojekt):**
    * **Lizenz:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).
    * **Bedingungen:** Namensnennung erforderlich, keine kommerzielle Nutzung, Weitergabe unter gleichen Bedingungen.
    * **Details:** Die vollständigen Bedingungen finden Sie in der `LICENSE`-Datei im Hauptverzeichnis.

2.  **Archiv (`/archiv`):**
    * **Lizenz:** MIT License.
    * **Bedingungen:** Nahezu uneingeschränkte Nutzung, auch kommerziell.
    * **Details:** Die vollständigen Bedingungen finden Sie in der `LICENSE-MIT.md`-Datei innerhalb des `/archiv`-Ordners.

---
<<<<<<< HEAD
© 2025 Dominik Knape
=======
© 2025 Dominik Knape
>>>>>>> 44df3e2986f339302ebc2a03ac2a11817233d2d3
