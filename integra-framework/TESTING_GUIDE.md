#### 📝 **TESTING_GUIDE.md**
```markdown
# INTEGRA Testing Guide

## Verfügbare Tests

### 1. Schnelltest
```bash
python test_lokal.py

2. Core Module Tests

python integra/tests/test_core.py

3. Demo-Programme
Einfache Demo
Testet Basis-Funktionalität mit verschiedenen Anfragen:

python demo_einfach.py

Core Light Demo (Interaktiv)

python integra/examples/core_light_demo.py

Wählen Sie ein Profil (default, strict, supportive, conservative)
Stellen Sie eigene Fragen
Beenden mit 'quit'

Batch-Test
Führt 8 vordefinierte Szenarien aus:

python integra/examples/core_light_demo.py --mode batch

Advanced Module Demo
Testet ETB, PAE, Mini Learner und Mini Audit:

python integra/examples/light_modular_demo.py

Erwartete Ergebnisse
Core Tests

8/8 Tests sollten bestehen
Fast Path für einfache Fragen
Deep Path für ethische Fragen
Transparenz-Anfragen funktionieren
Override nur mit Admin-Rechten

ETB (Ethical Tradeoff Balancer)

Bewertet mehrere Optionen
Zeigt Prinzipien-Beiträge
Konfidenz-Scores

PAE (Priority Anchor Engine)

Löst Gleichstände auf
Verschiedene Auflösungsmethoden
Kontext-basierte Entscheidungen