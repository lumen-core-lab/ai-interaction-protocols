# -*- coding: utf-8 -*-
"""
Modulname: profiles.py
Beschreibung: Ethische Profile für INTEGRA Light - Verwaltung von ALIGN-Gewichtungen
Teil von: INTEGRA Light – Core
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Mit Baukasten-Integration
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import copy

# Standardisierte Imports (Fallback nur für lokale Tests)
try:
    from integra.core import principles
except ImportError:
    import principles  # Für lokale Tests

# CONFIG wird lazy geladen für bessere Testbarkeit
_CONFIG = None

def get_config():
    """Lazy-loading für CONFIG."""
    global _CONFIG
    if _CONFIG is None:
        try:
            from integra.config import CONFIG
            _CONFIG = CONFIG
        except ImportError:
            _CONFIG = {"paths": {"profiles": "profiles"}}
    return _CONFIG


@dataclass
class ProfileModification:
    """Datenklasse für Profil-Änderungen."""
    timestamp: str
    principle: Optional[str] = None
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    reason: str = "manual"
    action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class EthicalProfile:
    """
    Repräsentiert ein ethisches Profil mit ALIGN-Gewichtungen und Metadaten.
    Erweitert mit Baukasten-Kompatibilität.
    """
    
    def __init__(self, name: str, weights: Dict[str, float], 
                 description: str = "", metadata: Optional[Dict[str, Any]] = None):
        """
        Initialisiert ein ethisches Profil.
        
        Args:
            name: Name des Profils
            weights: ALIGN-Gewichtungen
            description: Beschreibung des Profils
            metadata: Zusätzliche Metadaten
        """
        self.name = name
        self.weights = self._normalize_weights(weights)
        self.description = description
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.usage_count = 0
        self.modification_history: List[ProfileModification] = []
        self.metadata = metadata or {}
        
        # Validierung bei Erstellung
        is_valid, error = self._validate_weights()
        if not is_valid:
            raise ValueError(f"Ungültiges Profil '{name}': {error}")
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Stellt sicher, dass alle ALIGN-Prinzipien vorhanden sind."""
        normalized = {}
        for principle in principles.ALIGN_KEYS:
            normalized[principle] = float(weights.get(principle, 1.0))
        return normalized
    
    def _validate_weights(self) -> Tuple[bool, str]:
        """Validiert die Gewichtungen des Profils."""
        # Nutze die verbesserte validate_profile Funktion aus principles
        if hasattr(principles, '_manager'):
            return principles._manager.validate_profile(self.weights)
        else:
            # Fallback für alte Version
            return principles.validate_profile(self.weights)
    
    def get_weight(self, principle: str) -> float:
        """
        Gibt die Gewichtung für ein Prinzip zurück.
        
        Args:
            principle: Name des Prinzips
            
        Returns:
            Gewichtung oder 1.0 als Fallback
        """
        return self.weights.get(principle, 1.0)
    
    def set_weight(self, principle: str, weight: float, reason: str = "manual") -> bool:
        """
        Setzt die Gewichtung für ein Prinzip.
        
        Args:
            principle: Name des Prinzips
            weight: Neue Gewichtung
            reason: Grund für die Änderung
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        if principle not in principles.ALIGN_KEYS:
            return False
        
        if not isinstance(weight, (int, float)) or weight < 0:
            return False
        
        old_weight = self.weights.get(principle, 1.0)
        self.weights[principle] = float(weight)
        self.modified_at = datetime.now()
        
        # Historie aufzeichnen
        modification = ProfileModification(
            timestamp=self.modified_at.isoformat(),
            principle=principle,
            old_value=old_weight,
            new_value=float(weight),
            reason=reason
        )
        self.modification_history.append(modification)
        
        # Historie begrenzen
        if len(self.modification_history) > 100:
            self.modification_history = self.modification_history[-100:]
        
        return True
    
    def adjust_weight(self, principle: str, delta: float, reason: str = "adjustment") -> bool:
        """
        Passt die Gewichtung für ein Prinzip relativ an.
        
        Args:
            principle: Name des Prinzips
            delta: Änderung der Gewichtung
            reason: Grund für die Anpassung
            
        Returns:
            True wenn erfolgreich
        """
        current = self.get_weight(principle)
        new_weight = max(0.0, current + delta)
        
        # Optional: Maximale Gewichtung begrenzen
        max_weight = self.metadata.get("max_weight", 2.0)
        new_weight = min(new_weight, max_weight)
        
        return self.set_weight(principle, new_weight, reason)
    
    def batch_adjust_weights(self, adjustments: Dict[str, float], reason: str = "batch_adjustment") -> Dict[str, bool]:
        """
        Führt mehrere Gewichtungsanpassungen gleichzeitig durch.
        
        Args:
            adjustments: Dictionary mit Prinzip -> Delta
            reason: Grund für die Anpassungen
            
        Returns:
            Dictionary mit Prinzip -> Erfolg
        """
        results = {}
        for principle, delta in adjustments.items():
            results[principle] = self.adjust_weight(principle, delta, reason)
        return results
    
    def normalize_weights(self, target_sum: float = 5.0) -> None:
        """
        Normalisiert alle Gewichtungen auf eine Zielsumme.
        
        Args:
            target_sum: Zielsumme für alle Gewichtungen (Standard: 5.0)
        """
        total = sum(self.weights.values())
        if total > 0:
            factor = target_sum / total
            old_weights = self.weights.copy()
            
            for principle in self.weights:
                self.weights[principle] = round(self.weights[principle] * factor, 3)
            
            modification = ProfileModification(
                timestamp=datetime.now().isoformat(),
                action="normalization",
                reason=f"normalize_weights(target_sum={target_sum})"
            )
            self.modification_history.append(modification)
            
            self.modified_at = datetime.now()
    
    def get_risk_assessment(self) -> Dict[str, Any]:
        """
        Bewertet das Risikoprofil basierend auf den Gewichtungen.
        
        Returns:
            Risikobewertung mit Warnungen und Empfehlungen
        """
        assessment = {
            "warnings": [],
            "recommendations": [],
            "risk_level": "low",
            "balance_score": 0.0,
            "flags": []
        }
        
        # Prüfe auf extreme Werte
        for principle, weight in self.weights.items():
            if weight < 0.5:
                assessment["warnings"].append(f"{principle} ist sehr niedrig gewichtet ({weight})")
                assessment["flags"].append(f"low_{principle}")
            elif weight > 1.5:
                assessment["warnings"].append(f"{principle} ist sehr hoch gewichtet ({weight})")
                assessment["flags"].append(f"high_{principle}")
        
        # Prüfe Balance
        weights_list = list(self.weights.values())
        avg = sum(weights_list) / len(weights_list)
        variance = sum((w - avg) ** 2 for w in weights_list) / len(weights_list)
        assessment["balance_score"] = round(1.0 - min(1.0, variance), 3)
        
        # Risikostufe bestimmen
        if variance > 0.5:
            assessment["risk_level"] = "high"
            assessment["recommendations"].append("Profil ist unausgewogen - Normalisierung empfohlen")
        elif variance > 0.3:
            assessment["risk_level"] = "medium"
            assessment["recommendations"].append("Profil zeigt moderate Unausgewogenheit")
        
        # Spezifische Empfehlungen
        if self.weights.get("integrity", 1.0) < 0.7:
            assessment["recommendations"].append("Integrity sollte nicht zu niedrig sein")
        
        if self.weights.get("governance", 1.0) < 0.6:
            assessment["recommendations"].append("Governance wichtig für Kontrollierbarkeit")
        
        return assessment
    
    def calculate_distance(self, other: 'EthicalProfile') -> float:
        """
        Berechnet die Distanz zu einem anderen Profil (Euklidische Distanz).
        
        Args:
            other: Anderes Profil zum Vergleich
            
        Returns:
            Distanz als float (0.0 = identisch)
        """
        distance_squared = 0.0
        for principle in principles.ALIGN_KEYS:
            diff = self.get_weight(principle) - other.get_weight(principle)
            distance_squared += diff ** 2
        return round(distance_squared ** 0.5, 3)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Profil zu einem Dictionary."""
        return {
            "name": self.name,
            "weights": self.weights.copy(),
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "usage_count": self.usage_count,
            "modification_history": [
                mod.to_dict() if isinstance(mod, ProfileModification) else mod
                for mod in self.modification_history[-10:]
            ],
            "risk_assessment": self.get_risk_assessment(),
            "metadata": self.metadata.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EthicalProfile':
        """Erstellt ein Profil aus einem Dictionary."""
        try:
            profile = cls(
                name=data["name"],
                weights=data["weights"],
                description=data.get("description", ""),
                metadata=data.get("metadata", {})
            )
            
            # Metadaten wiederherstellen
            if "created_at" in data:
                profile.created_at = datetime.fromisoformat(data["created_at"])
            if "modified_at" in data:
                profile.modified_at = datetime.fromisoformat(data["modified_at"])
            if "usage_count" in data:
                profile.usage_count = data["usage_count"]
            if "modification_history" in data:
                profile.modification_history = [
                    ProfileModification(**mod) if isinstance(mod, dict) else mod
                    for mod in data["modification_history"]
                ]
            
            return profile
            
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Ungültige Profil-Daten: {e}")
    
    def mark_used(self) -> None:
        """Markiert das Profil als verwendet (für Statistiken)."""
        self.usage_count += 1
    
    def clone(self, new_name: str, suffix: str = "_copy") -> 'EthicalProfile':
        """
        Erstellt eine Kopie des Profils mit neuem Namen.
        
        Args:
            new_name: Name für das neue Profil
            suffix: Suffix für automatische Benennung
            
        Returns:
            Kopie des Profils
        """
        if not new_name:
            new_name = f"{self.name}{suffix}"
            
        cloned = EthicalProfile(
            name=new_name,
            weights=self.weights.copy(),
            description=f"Kopie von {self.name}: {self.description}",
            metadata=self.metadata.copy()
        )
        
        # Historie übernehmen mit Vermerk
        cloned.modification_history = [
            ProfileModification(
                timestamp=datetime.now().isoformat(),
                action="cloned",
                reason=f"Geklont von '{self.name}'"
            )
        ]
        
        return cloned
    
    def __str__(self) -> str:
        return f"EthicalProfile('{self.name}', usage={self.usage_count})"
    
    def __repr__(self) -> str:
        return f"EthicalProfile(name='{self.name}', weights={self.weights})"


class ProfileManager:
    """Zentrale Verwaltungsklasse für Profile mit Baukasten-Integration."""
    
    def __init__(self, profiles_dir: Optional[str] = None):
        """
        Initialisiert den ProfileManager.
        
        Args:
            profiles_dir: Verzeichnis für Profile-Dateien
        """
        config = get_config()
        self.profiles_dir = Path(profiles_dir or config.get("paths", {}).get("profiles", "profiles"))
        self._cache: Dict[str, EthicalProfile] = {}
        self._test_mode = False  # Für Unit-Tests
        self._load_predefined_profiles()
    
    def _load_predefined_profiles(self) -> None:
        """Lädt die vordefinierten Profile aus principles."""
        for profile_name, profile_data in principles.STANDARD_PROFILES.items():
            self._cache[profile_name] = EthicalProfile(
                name=profile_data["name"],
                weights=profile_data["weights"],
                description=profile_data["description"],
                metadata={"type": "predefined", "source": "principles.py"}
            )
    
    def get_profile(self, name: str) -> Optional[EthicalProfile]:
        """
        Gibt ein Profil anhand des Namens zurück.
        
        Args:
            name: Name des Profils
            
        Returns:
            EthicalProfile oder None
        """
        # Cache prüfen
        if name in self._cache:
            return self._cache[name]
        
        # Von Disk laden
        profile = self._load_from_disk(name)
        if profile:
            self._cache[name] = profile
            
        return profile
    
    def _load_from_disk(self, name: str) -> Optional[EthicalProfile]:
        """Lädt ein Profil von der Festplatte."""
        if self._test_mode:  # Skip disk access in test mode
            return None
            
        try:
            filepath = self.profiles_dir / f"{name}.json"
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                profile = EthicalProfile.from_dict(data)
                profile.metadata["source"] = "disk"
                return profile
        except (json.JSONDecodeError, ValueError, OSError) as e:
            # Logging für besseres Debugging
            if get_config().get("debug", False):
                print(f"Error loading profile {name}: {e}")
        return None
    
    def save_profile(self, profile: EthicalProfile) -> Dict[str, Any]:
        """
        Speichert ein Profil.
        
        Args:
            profile: Zu speicherndes Profil
            
        Returns:
            Ergebnis-Dictionary
        """
        if self._test_mode:  # Skip disk write in test mode
            self._cache[profile.name] = profile
            return {
                "success": True,
                "filepath": f"test://profiles/{profile.name}.json",
                "profile_name": profile.name,
                "test_mode": True
            }
            
        try:
            self.profiles_dir.mkdir(exist_ok=True, parents=True)
            filepath = self.profiles_dir / f"{profile.name}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Cache aktualisieren
            self._cache[profile.name] = profile
            
            return {
                "success": True,
                "filepath": str(filepath),
                "profile_name": profile.name
            }
            
        except (OSError, TypeError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": None  # Könnte erweitert werden mit traceback.format_exc()
            }
    
    def list_profiles(self) -> List[str]:
        """Gibt eine Liste aller verfügbaren Profile zurück."""
        profiles = set(self._cache.keys())
        
        # Gespeicherte Profile hinzufügen
        if self.profiles_dir.exists():
            for filepath in self.profiles_dir.glob("*.json"):
                profiles.add(filepath.stem)
        
        return sorted(list(profiles))
    
    def delete_profile(self, name: str) -> Dict[str, Any]:
        """
        Löscht ein Profil (nur custom Profile).
        
        Args:
            name: Name des Profils
            
        Returns:
            Ergebnis-Dictionary
        """
        # Vordefinierte Profile können nicht gelöscht werden
        if name in principles.STANDARD_PROFILES:
            return {
                "success": False,
                "error": "Vordefinierte Profile können nicht gelöscht werden"
            }
        
        try:
            filepath = self.profiles_dir / f"{name}.json"
            if filepath.exists():
                filepath.unlink()
            
            # Aus Cache entfernen
            self._cache.pop(name, None)
            
            return {"success": True, "deleted": name}
            
        except OSError as e:
            return {"success": False, "error": str(e)}


# Globale Instanz
_profile_manager = ProfileManager()


def run_module(input_data: Dict[str, Any], 
               profile: Dict[str, float], 
               context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hauptfunktion für die Baukasten-Integration.
    Verwaltet Profile und führt profilbezogene Operationen aus.
    
    Args:
        input_data: Dictionary mit Eingabedaten
            - action: gewünschte Aktion
            - profile_name: Name des Profils (optional)
            - weights: Gewichtungen für neues Profil (optional)
            - adjustments: Anpassungen für Profil (optional)
            - test_mode: Boolean für Test-Modus (optional)
        profile: Aktuelles Profil (als Dictionary)
        context: Laufender Kontext
        
    Returns:
        Erweiterter Kontext mit Ergebnis in context["profiles_result"]
    """
    try:
        action = input_data.get("action", "get_current")
        test_mode = input_data.get("test_mode", False)
        
        # Test-Modus für Unit-Tests
        if test_mode:
            _profile_manager._test_mode = True
        
        result = {}
        
        # Aktuelles Profil als EthicalProfile-Objekt
        current_profile = EthicalProfile(
            name="current",
            weights=profile,
            description="Aktuelles Laufzeit-Profil"
        )
        
        # Immer die aktuellen Gewichtungen mitgeben (API-Konsistenz)
        base_result = {
            "current_weights": current_profile.weights,
            "current_profile_name": current_profile.name
        }
        
        if action == "get_current":
            # Aktuelles Profil zurückgeben
            result = {
                **base_result,
                "profile": current_profile.to_dict(),
                "risk_assessment": current_profile.get_risk_assessment(),
                "weights": current_profile.weights  # Explizit für API-Konsistenz
            }
            
        elif action == "load":
            # Profil laden
            profile_name = input_data.get("profile_name", "default")
            loaded_profile = _profile_manager.get_profile(profile_name)
            
            if loaded_profile:
                loaded_profile.mark_used()
                result = {
                    **base_result,
                    "success": True,
                    "profile": loaded_profile.to_dict(),
                    "weights": loaded_profile.weights,
                    "loaded_from": loaded_profile.metadata.get("source", "unknown")
                }
            else:
                result = {
                    **base_result,
                    "success": False,
                    "error": f"Profil '{profile_name}' nicht gefunden",
                    "error_type": "ProfileNotFound",
                    "available": _profile_manager.list_profiles()
                }
                
        elif action == "save":
            # Aktuelles Profil speichern
            profile_name = input_data.get("profile_name", f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            description = input_data.get("description", "Gespeichertes Profil")
            
            save_profile = EthicalProfile(
                name=profile_name,
                weights=profile,
                description=description
            )
            
            result = {
                **base_result,
                **_profile_manager.save_profile(save_profile)
            }
            
        elif action == "adjust":
            # Profil anpassen
            adjustments = input_data.get("adjustments", {})
            reason = input_data.get("reason", "module_adjustment")
            
            # Kopie erstellen für Anpassungen
            adjusted_profile = current_profile.clone("adjusted")
            results = adjusted_profile.batch_adjust_weights(adjustments, reason)
            
            result = {
                **base_result,
                "success": all(results.values()),
                "adjusted_weights": adjusted_profile.weights,
                "weights": adjusted_profile.weights,  # Für API-Konsistenz
                "adjustment_results": results,
                "risk_assessment": adjusted_profile.get_risk_assessment()
            }
            
        elif action == "normalize":
            # Profil normalisieren
            target_sum = input_data.get("target_sum", 5.0)
            
            normalized_profile = current_profile.clone("normalized")
            normalized_profile.normalize_weights(target_sum)
            
            result = {
                "success": True,
                "normalized_weights": normalized_profile.weights,
                "risk_assessment": normalized_profile.get_risk_assessment()
            }
            
        elif action == "compare":
            # Profile vergleichen
            other_name = input_data.get("other_profile", "default")
            other_profile = _profile_manager.get_profile(other_name)
            
            if other_profile:
                distance = current_profile.calculate_distance(other_profile)
                result = {
                    **base_result,
                    "success": True,
                    "distance": distance,
                    "similarity": max(0.0, 1.0 - (distance / 2.0)),  # Normalisiert
                    "current_risk": current_profile.get_risk_assessment(),
                    "other_risk": other_profile.get_risk_assessment(),
                    "weights": current_profile.weights,  # Aktuelle Gewichtungen
                    "other_weights": other_profile.weights  # Vergleichsgewichtungen
                }
            else:
                result = {
                    **base_result,
                    "success": False,
                    "error": f"Vergleichsprofil '{other_name}' nicht gefunden",
                    "error_type": "ProfileNotFound"
                }
                
        elif action == "list":
            # Verfügbare Profile auflisten
            profiles = _profile_manager.list_profiles()
            profile_details = {}
            
            for name in profiles:
                prof = _profile_manager.get_profile(name)
                if prof:
                    profile_details[name] = {
                        "description": prof.description,
                        "risk_level": prof.get_risk_assessment()["risk_level"],
                        "usage_count": prof.usage_count
                    }
            
            result = {
                "profiles": profiles,
                "count": len(profiles),
                "details": profile_details
            }
            
        elif action == "assess_risk":
            # Risikobewertung für aktuelles Profil
            assessment = current_profile.get_risk_assessment()
            result = {
                "risk_assessment": assessment,
                "profile_name": current_profile.name
            }
            
        else:
            result = {
                **base_result,
                "error": f"Unbekannte Aktion: {action}",
                "error_type": "UnknownAction",
                "available_actions": [
                    "get_current", "load", "save", "adjust", 
                    "normalize", "compare", "list", "assess_risk"
                ]
            }
        
        # Test-Modus zurücksetzen
        if test_mode:
            _profile_manager._test_mode = False
        
        # Ergebnis in Kontext speichern
        context["profiles_result"] = {
            "status": "success" if "error" not in result else "error",
            "action": action,
            "data": result,
            "module": "profiles",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        import traceback
        # Erweiterte Fehlerbehandlung
        context["profiles_result"] = {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "module": "profiles",
            "timestamp": datetime.now().isoformat()
        }
        
        # Debug-Info wenn aktiviert
        if get_config().get("debug", False):
            context["profiles_result"]["traceback"] = traceback.format_exc()
    
    return context


# Rückwärtskompatible Funktionen
def get_default_profile() -> Dict[str, float]:
    """Gibt das Standardprofil zurück."""
    return principles.STANDARD_PROFILES["default"]["weights"].copy()


def create_profile(name: str, weights: Optional[Dict[str, float]] = None, 
                  description: str = "") -> EthicalProfile:
    """Erstellt ein neues Profil."""
    if weights is None:
        weights = get_default_profile()
    return EthicalProfile(name, weights, description)


def get_profile_by_name(name: str) -> Optional[EthicalProfile]:
    """Gibt ein Profil anhand des Namens zurück."""
    return _profile_manager.get_profile(name)


def save_profile(profile: EthicalProfile) -> Dict[str, Any]:
    """Speichert ein Profil."""
    return _profile_manager.save_profile(profile)


def list_available_profiles() -> List[str]:
    """Listet alle verfügbaren Profile auf."""
    return _profile_manager.list_profiles()


def demo():
    """Demonstriert die Baukasten-Integration des profiles-Moduls."""
    print("=== INTEGRA Profiles Demo (Baukasten-Version 2.0) ===")
    print()
    
    # Test 1: Aktuelles Profil abrufen (mit Test-Modus)
    print("1. Test: Aktuelles Profil (Test-Modus)")
    context = {}
    profile = get_default_profile()
    input_data = {"action": "get_current", "test_mode": True}
    
    context = run_module(input_data, profile, context)
    risk = context["profiles_result"]["data"]["risk_assessment"]
    print(f"   Risiko-Level: {risk['risk_level']}")
    print(f"   Balance-Score: {risk['balance_score']}")
    print(f"   Weights vorhanden: {'weights' in context['profiles_result']['data']}")
    print()
    
    # Test 2: Profil laden
    print("2. Test: Conservative-Profil laden")
    input_data = {"action": "load", "profile_name": "conservative"}
    context = run_module(input_data, profile, {})
    
    if context["profiles_result"]["data"]["success"]:
        loaded = context["profiles_result"]["data"]["profile"]
        print(f"   Geladen: {loaded['name']}")
        print(f"   Governance: {loaded['weights']['governance']}")
    print()
    
    # Test 3: Profil anpassen
    print("3. Test: Profil anpassen")
    adjustments = {
        "integrity": 0.2,
        "nurturing": -0.1,
        "learning": 0.3
    }
    input_data = {
        "action": "adjust",
        "adjustments": adjustments,
        "reason": "demo_test"
    }
    context = run_module(input_data, profile, {})
    
    adjusted = context["profiles_result"]["data"]["adjusted_weights"]
    print(f"   Integrity: {profile['integrity']} → {adjusted['integrity']}")
    print(f"   Neue Risikobewertung: {context['profiles_result']['data']['risk_assessment']['risk_level']}")
    print()
    
    # Test 4: Profil normalisieren
    print("4. Test: Profil normalisieren")
    unbalanced_profile = {
        "awareness": 2.0,
        "learning": 0.5,
        "integrity": 3.0,
        "governance": 0.8,
        "nurturing": 1.2
    }
    input_data = {"action": "normalize", "target_sum": 5.0}
    context = run_module(input_data, unbalanced_profile, {})
    
    normalized = context["profiles_result"]["data"]["normalized_weights"]
    total = sum(normalized.values())
    print(f"   Summe vorher: {sum(unbalanced_profile.values()):.1f}")
    print(f"   Summe nachher: {total:.1f}")
    print()
    
    # Test 5: Profile vergleichen
    print("5. Test: Profile vergleichen")
    input_data = {
        "action": "compare",
        "other_profile": "supportive"
    }
    context = run_module(input_data, profile, {})
    
    if context["profiles_result"]["data"]["success"]:
        comparison = context["profiles_result"]["data"]
        print(f"   Distanz: {comparison['distance']:.3f}")
        print(f"   Ähnlichkeit: {comparison['similarity']:.1%}")
    print()
    
    # Test 6: Verfügbare Profile
    print("6. Test: Alle Profile auflisten")
    input_data = {"action": "list"}
    context = run_module(input_data, profile, {})
    
    profiles_list = context["profiles_result"]["data"]["profiles"]
    print(f"   Verfügbare Profile: {len(profiles_list)}")
    for name in profiles_list[:3]:
        details = context["profiles_result"]["data"]["details"].get(name, {})
        print(f"   - {name}: {details.get('risk_level', 'unknown')}")
    print()
    
    print("=== Demo abgeschlossen ===")


if __name__ == "__main__":
    demo()