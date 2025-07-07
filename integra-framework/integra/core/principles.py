# -*- coding: utf-8 -*-
"""
Modulname: principles.py
Beschreibung: ALIGN-Prinzipien für INTEGRA Light - erweitert mit Baukasten-Kompatibilität
Teil von: INTEGRA Light – Core
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Verbessert für Baukasten-System
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class ALIGNPrinciple(Enum):
    """Enum für die 5 ALIGN-Prinzipien zur typsicheren Verwendung."""
    AWARENESS = "awareness"
    LEARNING = "learning"
    INTEGRITY = "integrity"
    GOVERNANCE = "governance"
    NURTURING = "nurturing"


@dataclass
class PrincipleInfo:
    """Datenklasse für erweiterte Prinzipien-Informationen."""
    key: str
    weight: float
    short_description: str
    detailed_description: str
    examples: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für JSON-Serialisierung."""
        return {
            "key": self.key,
            "weight": self.weight,
            "short_description": self.short_description,
            "detailed_description": self.detailed_description,
            "examples": self.examples,
            "violations": self.violations
        }


@dataclass
class RiskLevel:
    """Datenklasse für Risikostufen-Definitionen."""
    level: str
    threshold: float
    description: str
    action: str
    
    def applies_to_score(self, score: float) -> bool:
        """Prüft, ob diese Risikostufe für einen gegebenen Score gilt."""
        return score <= self.threshold


class PrinciplesManager:
    """Zentrale Verwaltungsklasse für ALIGN-Prinzipien mit Baukasten-Integration."""
    
    def __init__(self):
        """Initialisiert den PrinciplesManager mit Standard-Werten."""
        self._principles: Dict[str, PrincipleInfo] = self._initialize_principles()
        self._risk_levels: List[RiskLevel] = self._initialize_risk_levels()
        self._thresholds: Dict[str, float] = self._initialize_thresholds()
        self._standard_profiles: Dict[str, Dict[str, Any]] = self._initialize_profiles()
    
    def _initialize_principles(self) -> Dict[str, PrincipleInfo]:
        """Initialisiert die ALIGN-Prinzipien mit vollständigen Informationen."""
        return {
            ALIGNPrinciple.AWARENESS.value: PrincipleInfo(
                key="awareness",
                weight=1.0,
                short_description="Bewusstsein für Risiken, Wirkung und ethischen Kontext",
                detailed_description=(
                    "Das Prinzip des Bewusstseins umfasst die Fähigkeit, potenzielle Risiken zu erkennen, "
                    "die Auswirkungen von Entscheidungen zu verstehen und den ethischen Kontext zu berücksichtigen."
                ),
                examples=["Risikoanalyse", "Folgenabschätzung", "Kontextsensitivität"],
                violations=["Ignoranz", "Fahrlässigkeit", "Kurzsichtigkeit"]
            ),
            ALIGNPrinciple.LEARNING.value: PrincipleInfo(
                key="learning",
                weight=1.0,
                short_description="Fähigkeit, aus Erfahrungen zu lernen und sich zu verbessern",
                detailed_description=(
                    "Das Lernprinzip fördert kontinuierliche Verbesserung, Anpassungsfähigkeit und "
                    "die Bereitschaft, aus Fehlern zu lernen."
                ),
                examples=["Fehleranalyse", "Anpassung", "Wissenstransfer"],
                violations=["Lernverweigerung", "Stagnation", "Wiederholungsfehler"]
            ),
            ALIGNPrinciple.INTEGRITY.value: PrincipleInfo(
                key="integrity",
                weight=1.0,
                short_description="Ehrlichkeit, Transparenz und Konsistenz im Handeln",
                detailed_description=(
                    "Integrität bedeutet Wahrhaftigkeit, Offenheit und Verlässlichkeit in allen Handlungen "
                    "und Entscheidungen."
                ),
                examples=["Ehrlichkeit", "Transparenz", "Konsistenz"],
                violations=["Täuschung", "Verschleierung", "Widersprüchlichkeit"]
            ),
            ALIGNPrinciple.GOVERNANCE.value: PrincipleInfo(
                key="governance",
                weight=1.0,
                short_description="Kontrollierbarkeit und Regelkonformität",
                detailed_description=(
                    "Governance stellt sicher, dass Systeme kontrollierbar bleiben, Regeln eingehalten werden "
                    "und Verantwortlichkeiten klar definiert sind."
                ),
                examples=["Compliance", "Auditierbarkeit", "Verantwortung"],
                violations=["Regelverstoß", "Unkontrollierbarkeit", "Anarchie"]
            ),
            ALIGNPrinciple.NURTURING.value: PrincipleInfo(
                key="nurturing",
                weight=1.0,
                short_description="Förderung, Fürsorge und Schutz anderer Beteiligter",
                detailed_description=(
                    "Das Fürsorgeprinzip priorisiert das Wohlergehen aller Beteiligten und fördert "
                    "unterstützende, schützende Handlungen."
                ),
                examples=["Unterstützung", "Schutz", "Empathie"],
                violations=["Schädigung", "Vernachlässigung", "Ausbeutung"]
            )
        }
    
    def _initialize_risk_levels(self) -> List[RiskLevel]:
        """Initialisiert die Risikostufen-Definitionen."""
        return [
            RiskLevel("critical", 0.3, "Kritisches Risiko - sofortige Intervention erforderlich", "block"),
            RiskLevel("high", 0.5, "Hohes Risiko - Vorsicht und Überprüfung erforderlich", "review"),
            RiskLevel("medium", 0.7, "Mittleres Risiko - erhöhte Aufmerksamkeit empfohlen", "monitor"),
            RiskLevel("low", 0.9, "Geringes Risiko - normale Verarbeitung möglich", "proceed"),
            RiskLevel("minimal", 1.0, "Minimales Risiko - keine Bedenken", "approve")
        ]
    
    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialisiert die ethischen Schwellwerte."""
        return {
            "critical": 0.3,
            "warning": 0.6,
            "acceptable": 0.8,
            "excellent": 0.95
        }
    
    def _initialize_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialisiert die Standard-Profile."""
        return {
            "default": {
                "name": "Standard",
                "description": "Ausgewogenes Profil für allgemeine Anwendungen",
                "weights": {p.value: 1.0 for p in ALIGNPrinciple}
            },
            "conservative": {
                "name": "Konservativ",
                "description": "Erhöhte Sicherheit und Regelkonformität",
                "weights": {
                    ALIGNPrinciple.AWARENESS.value: 1.2,
                    ALIGNPrinciple.LEARNING.value: 0.8,
                    ALIGNPrinciple.INTEGRITY.value: 1.3,
                    ALIGNPrinciple.GOVERNANCE.value: 1.2,
                    ALIGNPrinciple.NURTURING.value: 1.1,
                }
            },
            "supportive": {
                "name": "Unterstützend",
                "description": "Fokus auf Hilfe und Lernen",
                "weights": {
                    ALIGNPrinciple.AWARENESS.value: 0.9,
                    ALIGNPrinciple.LEARNING.value: 1.2,
                    ALIGNPrinciple.INTEGRITY.value: 1.0,
                    ALIGNPrinciple.GOVERNANCE.value: 0.8,
                    ALIGNPrinciple.NURTURING.value: 1.3,
                }
            },
            "strict": {
                "name": "Strikt",
                "description": "Maximale Regelkonformität und Integrität",
                "weights": {
                    ALIGNPrinciple.AWARENESS.value: 1.1,
                    ALIGNPrinciple.LEARNING.value: 0.7,
                    ALIGNPrinciple.INTEGRITY.value: 1.5,
                    ALIGNPrinciple.GOVERNANCE.value: 1.4,
                    ALIGNPrinciple.NURTURING.value: 0.8,
                }
            }
        }
    
    def get_weights(self, profile: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Gibt die aktuellen ALIGN-Gewichtungen zurück.
        
        Args:
            profile: Optionales Profil mit angepassten Gewichtungen
            
        Returns:
            Dictionary mit Prinzip -> Gewichtung
        """
        if profile:
            return profile
        return {key: info.weight for key, info in self._principles.items()}
    
    def get_principle_info(self, principle: Union[str, ALIGNPrinciple], 
                          detailed: bool = False) -> Dict[str, Any]:
        """
        Gibt Informationen zu einem spezifischen Prinzip zurück.
        
        Args:
            principle: Prinzip-Schlüssel oder Enum
            detailed: Ob erweiterte Informationen zurückgegeben werden sollen
            
        Returns:
            Dictionary mit Prinzip-Informationen
        """
        key = principle.value if isinstance(principle, ALIGNPrinciple) else principle
        
        if key not in self._principles:
            return {"error": f"Unbekanntes Prinzip: {key}"}
        
        info = self._principles[key]
        result = {
            "key": info.key,
            "weight": info.weight,
            "description": info.detailed_description if detailed else info.short_description
        }
        
        if detailed:
            result.update({
                "examples": info.examples,
                "violations": info.violations
            })
        
        return result
    
    def validate_profile(self, profile: Dict[str, float]) -> Tuple[bool, str]:
        """
        Validiert ein ethisches Profil auf Vollständigkeit und gültige Werte.
        
        Args:
            profile: Zu validierendes Profil
            
        Returns:
            Tuple aus (ist_gültig, Fehlermeldung)
        """
        if not isinstance(profile, dict):
            return False, "Profil muss ein Dictionary sein"
        
        missing_keys = []
        invalid_values = []
        
        for principle in ALIGNPrinciple:
            key = principle.value
            if key not in profile:
                missing_keys.append(key)
            else:
                value = profile[key]
                if not isinstance(value, (int, float)) or value < 0:
                    invalid_values.append(f"{key}: {value}")
        
        if missing_keys:
            return False, f"Fehlende Prinzipien: {', '.join(missing_keys)}"
        
        if invalid_values:
            return False, f"Ungültige Werte (müssen >= 0 sein): {', '.join(invalid_values)}"
        
        return True, ""
    
    def get_risk_level(self, score: float) -> Dict[str, Any]:
        """
        Bestimmt die Risikostufe basierend auf einem Score.
        
        Args:
            score: Ethischer Score (0.0-1.0)
            
        Returns:
            Dictionary mit Risikoinformationen
        """
        for risk_level in self._risk_levels:
            if risk_level.applies_to_score(score):
                return {
                    "level": risk_level.level,
                    "description": risk_level.description,
                    "action": risk_level.action,
                    "threshold": risk_level.threshold
                }
        
        # Fallback (sollte nie erreicht werden)
        return self._risk_levels[-1].__dict__
    
    def get_threshold_level(self, score: float) -> str:
        """
        Gibt die Bewertungsstufe für einen Score zurück.
        
        Args:
            score: Zu bewertender Score
            
        Returns:
            Bewertungsstufe als String
        """
        if score < self._thresholds["critical"]:
            return "critical"
        elif score < self._thresholds["warning"]:
            return "warning"
        elif score < self._thresholds["acceptable"]:
            return "acceptable"
        elif score >= self._thresholds["excellent"]:
            return "excellent"
        else:
            return "acceptable"
    
    def export_principles(self) -> Dict[str, Any]:
        """
        Exportiert alle Prinzipien in einem serialisierbaren Format.
        
        Returns:
            Dictionary mit allen Prinzipien-Daten
        """
        return {
            "principles": {key: info.to_dict() for key, info in self._principles.items()},
            "risk_levels": [vars(rl) for rl in self._risk_levels],
            "thresholds": self._thresholds,
            "profiles": self._standard_profiles
        }


# Globale Instanz für einfachen Zugriff
_manager = PrinciplesManager()


def run_module(input_data: Dict[str, Any], 
               profile: Dict[str, float], 
               context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hauptfunktion für die Baukasten-Integration.
    Verarbeitet Anfragen zu ALIGN-Prinzipien und fügt Ergebnisse zum Kontext hinzu.
    
    Args:
        input_data: Dictionary mit Eingabedaten
            - action: "get_weights" | "validate_profile" | "get_info" | "assess_risk"
            - principle: (optional) spezifisches Prinzip für get_info
            - score: (optional) Score für assess_risk
            - profile_to_validate: (optional) zu validierendes Profil
        profile: Aktuelles ethisches Profil
        context: Laufender Kontext (wird erweitert)
        
    Returns:
        Erweiterter Kontext mit Ergebnis in context["principles_result"]
    """
    try:
        action = input_data.get("action", "get_weights")
        result = {}
        
        if action == "get_weights":
            # Standard-Aktion: Gewichtungen zurückgeben
            result = {
                "weights": _manager.get_weights(profile),
                "profile_valid": _manager.validate_profile(profile)[0]
            }
            
        elif action == "validate_profile":
            # Profil validieren
            profile_to_check = input_data.get("profile_to_validate", profile)
            is_valid, error_msg = _manager.validate_profile(profile_to_check)
            result = {
                "valid": is_valid,
                "error": error_msg if not is_valid else None
            }
            
        elif action == "get_info":
            # Informationen zu einem Prinzip abrufen
            principle = input_data.get("principle")
            detailed = input_data.get("detailed", False)
            
            if principle:
                result = _manager.get_principle_info(principle, detailed)
            else:
                # Alle Prinzipien zurückgeben
                result = {
                    "principles": {
                        p.value: _manager.get_principle_info(p, detailed) 
                        for p in ALIGNPrinciple
                    }
                }
                
        elif action == "assess_risk":
            # Risikobewertung durchführen
            score = input_data.get("score", 0.5)
            result = {
                "risk": _manager.get_risk_level(score),
                "threshold": _manager.get_threshold_level(score)
            }
            
        elif action == "export":
            # Alle Daten exportieren
            result = _manager.export_principles()
            
        else:
            result = {
                "error": f"Unbekannte Aktion: {action}",
                "available_actions": ["get_weights", "validate_profile", "get_info", "assess_risk", "export"]
            }
        
        # Ergebnis in Kontext speichern
        context["principles_result"] = {
            "status": "success" if "error" not in result else "error",
            "action": action,
            "data": result,
            "module": "principles"
        }
        
    except Exception as e:
        # Fehlerbehandlung
        context["principles_result"] = {
            "status": "error",
            "error": str(e),
            "module": "principles"
        }
    
    return context


# Rückwärtskompatibilität: Alte Funktionen als Wrapper
def get_principle_description(principle_key: str, detailed: bool = False) -> str:
    """Rückwärtskompatible Wrapper-Funktion."""
    info = _manager.get_principle_info(principle_key, detailed)
    return info.get("description", info.get("error", ""))


def get_all_principles() -> Dict[str, Dict[str, Any]]:
    """Rückwärtskompatible Wrapper-Funktion."""
    return _manager.export_principles()["principles"]


def validate_profile(profile: Dict[str, float]) -> Tuple[bool, str]:
    """Rückwärtskompatible Wrapper-Funktion."""
    return _manager.validate_profile(profile)


def get_risk_level(score: float) -> Dict[str, str]:
    """Rückwärtskompatible Wrapper-Funktion."""
    return _manager.get_risk_level(score)


def get_threshold_level(score: float) -> str:
    """Rückwärtskompatible Wrapper-Funktion."""
    return _manager.get_threshold_level(score)


# Rückwärtskompatible Konstanten
ALIGN_WEIGHTS = _manager.get_weights()
ALIGN_KEYS = [p.value for p in ALIGNPrinciple]
ALIGN_DESCRIPTIONS = {
    key: info.short_description 
    for key, info in _manager._principles.items()
}
ETHICAL_THRESHOLDS = _manager._thresholds
STANDARD_PROFILES = _manager._standard_profiles


def demo():
    """Demonstriert die Verwendung des principles-Moduls im Baukasten-System."""
    print("=== INTEGRA ALIGN-Prinzipien Demo (Baukasten-Version 2.0) ===")
    print()
    
    # Test 1: Standard-Gewichtungen abrufen
    print("1. Test: Gewichtungen abrufen")
    context = {}
    input_data = {"action": "get_weights"}
    profile = STANDARD_PROFILES["default"]["weights"]
    
    context = run_module(input_data, profile, context)
    print(f"   Ergebnis: {context['principles_result']['data']['weights']}")
    print()
    
    # Test 2: Profil validieren
    print("2. Test: Profil validieren")
    test_profile = {"awareness": 1.0, "learning": 0.8}  # Unvollständig
    input_data = {"action": "validate_profile", "profile_to_validate": test_profile}
    context = run_module(input_data, profile, {})
    print(f"   Gültig: {context['principles_result']['data']['valid']}")
    print(f"   Fehler: {context['principles_result']['data']['error']}")
    print()
    
    # Test 3: Prinzip-Info abrufen
    print("3. Test: Detaillierte Info zu 'integrity'")
    input_data = {"action": "get_info", "principle": "integrity", "detailed": True}
    context = run_module(input_data, profile, {})
    info = context['principles_result']['data']
    print(f"   Beschreibung: {info['description'][:80]}...")
    print(f"   Beispiele: {', '.join(info['examples'])}")
    print()
    
    # Test 4: Risikobewertung
    print("4. Test: Risikobewertung für verschiedene Scores")
    for score in [0.2, 0.5, 0.8, 0.95]:
        input_data = {"action": "assess_risk", "score": score}
        context = run_module(input_data, profile, {})
        risk = context['principles_result']['data']['risk']
        print(f"   Score {score}: {risk['level']} - {risk['action']}")
    print()
    
    # Test 5: Export aller Daten
    print("5. Test: Export aller Prinzipien-Daten")
    input_data = {"action": "export"}
    context = run_module(input_data, profile, {})
    export_data = context['principles_result']['data']
    print(f"   Exportierte Prinzipien: {len(export_data['principles'])}")
    print(f"   Risikostufen: {len(export_data['risk_levels'])}")
    print(f"   Profile: {list(export_data['profiles'].keys())}")
    print()
    
    print("=== Demo abgeschlossen ===")


if __name__ == "__main__":
    demo()