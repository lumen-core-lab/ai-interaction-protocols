# -*- coding: utf-8 -*-
"""
Einfacher Log Manager für INTEGRA
"""

from datetime import datetime
from pathlib import Path

class LogManager:
    def __init__(self):
        self.log_file = Path("logs") / "integra.log"
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_event(self, module, message, level="INFO"):
        """Schreibt eine Log-Nachricht."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{module}] {message}\n"
        
        # In Datei schreiben
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass  # Bei Fehler einfach weitermachen
        
        # Bei wichtigen Meldungen auch auf Konsole
        if level in ["ERROR", "WARNING"]:
            print(log_entry.strip())

# Globale Instanz
_log_manager = LogManager()

def log_event(module, message, level="INFO"):
    """Einfache Funktion zum Loggen."""
    _log_manager.log_event(module, message, level)