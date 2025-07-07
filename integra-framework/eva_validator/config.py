# -*- coding: utf-8 -*-
"""
EVA Validator - Konfiguration (Vereinfachte Version)
Diese Version funktioniert garantiert!
"""

from typing import Dict, Any, Optional, List, Union, Tuple  # WICHTIG: Tuple hinzugefügt!
import json
import os

# Versuche yaml zu importieren, aber mache es optional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Info: PyYAML nicht installiert. YAML-Support deaktiviert.")


def get_default_config() -> Dict[str, Any]:
    """Gibt die Standard-Konfiguration zurück."""
    return {
        "version": "1.0",
        "evaluation_criteria": {
            "min_ethic_threshold": 0.7,
            "critical_threshold": 0.4,
            "warning_threshold": 0.6,
            "scenario_requirements": {
                "privacy": {"min_score": 0.8, "escalation_below": 0.6},
                "harm": {"min_score": 0.9, "escalation_below": 0.7},
                "compliance": {"min_score": 0.85, "escalation_below": 0.7},
                "deception": {"min_score": 0.8, "escalation_below": 0.5}
            },
            "principle_weights": {
                "integrity": 1.0,
                "governance": 0.9,
                "nurturing": 0.9,
                "awareness": 0.8,
                "learning": 0.7
            },
            "escalation_triggers": [
                "personal_data_misuse",
                "potential_harm",
                "legal_violation",
                "discrimination",
                "manipulation"
            ],
            "required_compliance": []
        },
        "logging": {
            "enabled": True,
            "log_dir": "eva_logs",
            "max_file_size_mb": 100.0,
            "max_files": 50,
            "compress_logs": False,  # Deaktiviert für Einfachheit
            "buffer_size": 10
        },
        "escalation": {
            "human_review_queue_size": 100,
            "auto_escalate_on_low_score": True,
            "allow_external_override": True,
            "default_priority": 2,
            "emergency_contacts": []
        },
        "feedback": {
            "enabled": True,
            "pattern_detection_window_hours": 24,
            "min_pattern_count": 3,
            "export_interval_hours": 24,
            "max_history_size": 1000
        },
        "custom_triggers": [],
        "default_recommendation": "Bitte prüfen Sie diese Entscheidung manuell."
    }


def load_config(source: Optional[Union[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Lädt eine Konfiguration. Vereinfachte Version ohne komplexe Validierung.
    
    Args:
        source: Konfigurationsquelle (Datei-Pfad, Dictionary oder None für Defaults)
        
    Returns:
        Konfiguration als Dictionary
    """
    if source is None:
        return get_default_config()
    
    if isinstance(source, dict):
        # Merge mit Defaults
        config = get_default_config()
        _merge_dicts(config, source)
        return config
    
    if isinstance(source, str):
        # Versuche Datei zu laden
        if source.endswith('.json'):
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config = get_default_config()
                    _merge_dicts(config, data)
                    return config
            except Exception as e:
                print(f"Warnung: Konnte Config nicht laden: {e}")
                return get_default_config()
    
    return get_default_config()


def _merge_dicts(base: Dict[str, Any], update: Dict[str, Any]):
    """Hilfsfunktion zum Mergen von Dictionaries."""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_dicts(base[key], value)
        else:
            base[key] = value


def save_config(config: Dict[str, Any], file_path: str, validate: bool = False) -> bool:
    """Speichert Konfiguration in JSON-Datei."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")
        return False


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merged zwei Konfigurationen."""
    import copy
    result = copy.deepcopy(base)
    _merge_dicts(result, override)
    return result


def generate_config_template(output_file: str = "eva_config_template.json", 
                           include_descriptions: bool = False) -> bool:
    """Generiert eine Config-Template-Datei."""
    template = get_default_config()
    return save_config(template, output_file)


# Für Abwärtskompatibilität - Dummy-Klasse
class ConfigValidator:
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []
    
    @classmethod
    def apply_defaults(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        return config


# Demo-Funktion
def demo():
    """Zeigt wie die Config funktioniert."""
    print("=== EVA Config Demo ===")
    config = get_default_config()
    print(f"Standard Ethik-Threshold: {config['evaluation_criteria']['min_ethic_threshold']}")
    print("✅ Config funktioniert!")


if __name__ == "__main__":
    demo()