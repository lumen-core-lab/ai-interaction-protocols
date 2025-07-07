markdown# INTEGRA Installation Guide

## Voraussetzungen
- Python 3.8 oder höher
- Keine externen Dependencies! INTEGRA nutzt nur Python Standard-Bibliotheken

## Installation

### 1. Repository klonen
```bash
git clone https://github.com/DeinUsername/integra-framework.git
cd integra-framework

2. Installation testen
python test_lokal.py
# oder auf Windows:
py test_lokal.py

Sie sollten sehen:

✅ Core Module gefunden
✅ Advanced Module gefunden
✅ Decision Engine funktioniert!
🎉 INTEGRA ist bereit!

Erste Schritte
Einfache Demo

python demo_einfach.py

Interaktive Core Demo

python integra/examples/core_light_demo.py

Batch-Tests

python integra/examples/core_light_demo.py --mode batch

Advanced Module Demo

python integra/examples/light_modular_demo.py

Troubleshooting
Import-Fehler?

Stellen Sie sicher, dass Sie im Hauptverzeichnis sind
Python 3.8+ ist erforderlich

"python" funktioniert nicht?

Auf Windows versuchen Sie py statt python


