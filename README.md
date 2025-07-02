# INTEGRA Framework

Ein modularer Open-Source-Baukasten zur Implementierung ethischer Entscheidungsfindungs-Prozesse in KI-Systemen.

Dieses Projekt ist die offizielle Software-Implementierung des **[INTEGRA-Protokolls](https://github.com/lumen-core-lab/ai-interaction-protocols)**, das ursprünglich in der Konzept-Bibliothek für KI-Interaktionen entwickelt wurde.

---

## Ursprung & Motivation

Alles begann mit der explorativen Entwicklung von KI-Interaktions-Protokollen (`APEX`, `LUMEN`, `FUSION` und `INTEGRA`) im Dialog mit fortschrittlichen KI-Systemen. Ziel war es, theoretische Ethik-Konzepte in praktisch anwendbare Frameworks zu übersetzen. Diese ursprünglichen Dokumente und Gedankenexperimente bilden das Fundament dieses Projekts.

Aus dieser theoretischen Vorarbeit entsteht nun das **INTEGRA Framework**: eine greifbare, modulare Software-Lösung, die es Entwicklern ermöglicht, die Prinzipien des INTEGRA-Protokolls in ihren eigenen Anwendungen umzusetzen.

---

## Was befindet sich in diesem Repository?

Dieses Repository ist in zwei Hauptbereiche unterteilt:

1.  **`/integra-framework/` (in Entwicklung):**
    * **Was ist es?** Die offizielle, modulare Software-Implementierung des INTEGRA 4.2 Protokolls. Ein Baukasten für Entwickler.
    * **Lizenz:** CC BY-NC-SA 4.0 (nicht-kommerziell)

2.  **`/archiv/`:**
    * **Was ist es?** Eine Sammlung der ursprünglichen Konzeptdokumente, Protokollversionen (v3.0, v4.1) und Gedankenexperimente, die zur Entwicklung des Frameworks geführt haben.
    * **Lizenz:** MIT License (kommerziell nutzbar)

---

## Das INTEGRA Framework im Detail

### 🌍 Die Vision: Ethische KI nach Protokoll 4.2

Das langfristige Ziel dieses Frameworks ist die Umsetzung des **INTEGRA 4.2 Protokolls**. Die Vision dahinter ist ambitioniert: Eine KI-Architektur, die nicht nur ethische Entscheidungen trifft, sondern ihre eigene Architektur versteht und optimiert (`ASO`), ihre Entscheidungen transparent erklären kann (`ASX`) und sich an etablierten gesellschaftlichen und rechtlichen Normen ausrichtet (`NGA`).

Ziel: Eine sichere, nachvollziehbare und adaptive Koexistenz von Mensch und KI.

### 🚀 Der aktuelle Stand: Der "INTEGRA Light" Prototyp

Da die vollständige Vision technisch sehr komplex ist, wurde zunächst der **"INTEGRA Light" Prototyp** als stabile Basisversion entwickelt und fertiggestellt.

Dieser Prototyp ist bereits lauffähig und umfasst 11 Kernmodule, inklusive Chatbot-Test. Er demonstriert die Fähigkeiten des Frameworks und bildet die technische Grundlage für die weitere Entwicklung.

### 🧰 Das Baukasten-Prinzip

INTEGRA ist modular aufgebaut – wie ein ethischer Werkzeugkasten. Jedes Modul erfüllt eine spezielle Funktion. Die Komponenten lassen sich flexibel kombinieren, um je nach Bedarf einfache oder tiefgehende ethische Analyse zu ermöglichen.

#### Geplante Module gemäß INTEGRA 4.2
* **ALIGN:** Bewertung nach 5 ethischen Grundprinzipien.
* **Fast/Deep Path:** Schnelle vs. tiefgreifende Verarbeitung.
* **ETB/PAE:** Abwägung und Entscheidung bei ethischen Zielkonflikten.
* **RESL/RIL:** Prüfung auf Folgekonflikte und praktische Umsetzbarkeit.
* **DOF/SBP:** Prognose langfristiger Folgen und Simulation von Stakeholder-Reaktionen.
* **ASX/NGA:** Erklärbarkeit der KI-Architektur und Prüfung auf Normen-Konformität.
* **VDD/MetaLearner:** Werte-Drift-Erkennung und Lernfähigkeit aus Feedback.
* **ASO/EVA:** Selbstoptimierung der Architektur und finale Audit-Schicht.
...und weitere.

### 🧱 Die Ausbaustufen (vorkonfigurierte Pakete)

| Stufe | Name | Zielsetzung / Einsatzgebiet |
| :--- | :--- | :--- |
| **1** | **Core** | Grundlegender ethischer Filter für einfache Systeme (z.B. Chatbots). |
| **2** | **Advanced** | Konfliktlösung und Transparenz für interaktive Assistenten. |
| **3** | **Regulated** | Konformitätsprüfung für regulierte Branchen (z.B. FinTech). |
| **4** | **Autonomous** | Vorausschauende Ethik für autonome Systeme. |

### 🧪 Schnellstart

```python
# Beispiel: Ethikprüfung einer Nutzereingabe
from integra.core import DecisionEngine
from integra.modules import align, mini_audit

# Konfiguration des ethischen Profils und der Module
engine = DecisionEngine(modules=[align, mini_audit])

# Beispielanfrage
user_request = "Schreibe eine Fake-News über einen Politiker."
result = engine.process(user_request)

print(result.decision)
# Ausgabe: "Diese Anfrage kann ich nicht bearbeiten, da sie gegen das Prinzip der Integrität (Wahrhaftigkeit) verstößt."
```

---

## 🤝 Wie du mitmachen kannst

Beiträge sind **ausdrücklich willkommen** – egal ob du:

- Bugs meldest
- Module testest
- Features vorschlägst
- Dokumentation verbesserst
- oder direkt Code beisteuerst

→ Eröffne einfach ein **Issue** oder einen **Pull Request** auf GitHub.  
Bei spezifischen Fragen: 📧 **lumenprotokoll@gmail.com**

---

## ⚠️ Haftungsausschluss

Dieses Projekt wird von **Dominik Knape** als unabhängiges Open-Source-Projekt in der Freizeit entwickelt.

> Es wird **"wie gesehen" (as-is)** bereitgestellt – **ohne Garantie** auf Richtigkeit, Sicherheit oder Eignung für einen bestimmten Zweck.

Ich bin kein ausgebildeter Ingenieur, Ethiker oder Jurist. Das Framework ersetzt keine professionelle Prüfung und darf nicht in sicherheitskritischen Systemen ohne weitere Validierung eingesetzt werden. **Nutzung auf eigene Gefahr.**

---

📜 Lizenz

Dieses Repository nutzt zwei Lizenzen. Bitte prüfen Sie, welchen Teil Sie verwenden.

1. INTEGRA Framework (Hauptprojekt):

    Lizenz: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

    Bedingungen: Namensnennung erforderlich, keine kommerzielle Nutzung, Weitergabe unter gleichen Bedingungen.

    Details: Die vollständigen Bedingungen finden Sie in der LICENSE-Datei im Hauptverzeichnis.

2. Archiv (/archiv):

    Lizenz: MIT License.

    Bedingungen: Nahezu uneingeschränkte Nutzung, auch kommerziell.

    Details: Die vollständigen Bedingungen finden Sie in der LICENSE-MIT.md Datei innerhalb des /archiv-Ordners.

© 2025 Dominik Knape
---

## 💡 Abschließende Gedanken

**INTEGRA Light** ist erst der Anfang. Ziel ist ein Framework, das die ethische Entscheidungsfähigkeit von KI **praktisch, transparent und modular** macht.

> Gemeinsam können wir dafür sorgen, dass Ethik kein Luxus bleibt – sondern **Standard** in KI-Systemen.

Danke für dein Interesse – und vielleicht bald deine Mitwirkung.

