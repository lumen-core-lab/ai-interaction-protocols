# INTEGRA Framework

Ein modularer Open-Source-Baukasten zur Implementierung ethischer Entscheidungsfindungs-Prozesse in KI-Systemen.

Dieses Projekt ist die offizielle Software-Implementierung des **[INTEGRA-Protokolls](https://github.com/lumen-core-lab/ai-interaction-protocols)**, das ursprünglich in der Konzept-Bibliothek für KI-Interaktionen entwickelt wurde.

---

## 🌍 Die Vision: Ethische KI nach Protokoll 4.2

Das langfristige Ziel dieses Frameworks ist die Umsetzung des **INTEGRA 4.2 Protokolls**. Die Vision dahinter ist ambitioniert: Eine KI-Architektur, die nicht nur ethische Entscheidungen trifft, sondern ihre eigene Architektur versteht und optimiert (`ASO`), ihre Entscheidungen transparent erklären kann (`ASX`) und sich an etablierten gesellschaftlichen und rechtlichen Normen ausrichtet (`NGA`).

> Ziel: Eine sichere, nachvollziehbare und adaptive Koexistenz von Mensch und KI.

---

## 🚀 Der aktuelle Stand: Der "INTEGRA Light" Prototyp

Da die vollständige Vision technisch sehr komplex ist, wurde zunächst der **"INTEGRA Light" Prototyp** als stabile Basisversion entwickelt.

Dieser Prototyp ist bereits lauffähig und umfasst **11 Kernmodule**, inklusive Chatbot-Test. Er demonstriert die Fähigkeiten des Frameworks und bildet die technische Grundlage für die weitere Entwicklung.

---

## 🧰 Das Baukasten-Prinzip

INTEGRA ist modular aufgebaut – wie ein ethischer Werkzeugkasten. Jedes Modul erfüllt eine spezielle Funktion. Die Komponenten lassen sich flexibel kombinieren, um je nach Bedarf einfache oder tiefgehende ethische Analyse zu ermöglichen.

### Geplante Module gemäß INTEGRA 4.2

- **ALIGN** – Bewertung nach 5 ethischen Grundprinzipien (Awareness, Learning, Integrity, Governance, Nurturing)
- **Fast Path / Deep Path** – Schnelle vs. tiefgreifende Verarbeitung
- **ETB** – Dynamische Abwägung zwischen konkurrierenden ethischen Prinzipien
- **PAE** – Entscheidung bei Gleichgewicht
- **RESL** – Prüfung auf neue Folgekonflikte
- **RIL** – Prüfung auf praktische Umsetzbarkeit
- **DOF** – Prognose langfristiger Folgen
- **SBP** – Simulation von Stakeholder-Reaktionen
- **UIA** – Erkennung manipulativer Intentionen
- **ETPH** – Handhabung ethischer Zeitdruck-Situationen
- **ASX** – Nachvollziehbare Erklärung von ASO-Optimierungen
- **NGA** – Normenprüfung (z. B. DSGVO, UN-Menschenrechte)
- **VDD** – Werte-Drift-Erkennung über Zeit
- **MetaLearner** – Lernfähigkeit aus Feedback & Verlauf
- **ASO** – Selbstoptimierung der eigenen Entscheidungsarchitektur
- **EVA** – Letztinstanzliche Audit- und Validierungsschicht

---

## 🧱 Die Ausbaustufen (vorkonfigurierte Pakete)

| Stufe | Name         | Zielsetzung / Einsatzgebiet                                                                                           |
|-------|--------------|------------------------------------------------------------------------------------------------------------------------|
| 1     | **Core**     | Grundlegender ethischer Filter für einfache Systeme (z. B. Chatbots, IoT)                                              |
| 2     | **Advanced** | Konfliktlösung, 5-Schritt-Analyse, erste Lerneffekte – z. B. für interaktive Assistenten                               |
| 3     | **Regulated**| Konformitätsprüfung, Audit-Trail – z. B. für FinTech, Versicherungen, Gesundheitswesen                                 |
| 4     | **Autonomous**| Vollständige vorausschauende Ethik mit Selbstoptimierung – z. B. autonome Systeme, Langzeit-KI-Strategien              |

---

## 🧪 Schnellstart

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

## 📁 Projektstruktur (INTEGRA Light v1.0)

```
integra/
├── core/
│   ├── align_principles.py
│   ├── decision_engine.py
│   └── profile_manager.py
├── modules/
│   ├── ethics/basic_ethics.py
│   ├── learning/mini_learner.py
│   ├── audit/mini_audit.py
│   ├── governance/basic_control.py
│   └── reasoning/ (fast_path.py, deep_path.py)
├── versions/light.py
├── examples/basic_chatbot.py
└── tests/
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

## 📜 Lizenz

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

- ✅ Du darfst den Code verwenden, kopieren und ändern
- ❗ Nur **nicht-kommerziell**
- ✅ Urhebernennung (Dominik Knape) erforderlich
- ✅ Modifikationen müssen unter derselben Lizenz veröffentlicht werden

📄 Siehe [LICENSE](./LICENSE) für vollständige Bedingungen.

---

## 💡 Abschließende Gedanken

**INTEGRA Light** ist erst der Anfang. Ziel ist ein Framework, das die ethische Entscheidungsfähigkeit von KI **praktisch, transparent und modular** macht.

> Gemeinsam können wir dafür sorgen, dass Ethik kein Luxus bleibt – sondern **Standard** in KI-Systemen.

Danke für dein Interesse – und vielleicht bald deine Mitwirkung.

**© 2025 Dominik Knape**
