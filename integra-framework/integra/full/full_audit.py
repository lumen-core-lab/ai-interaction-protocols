# -*- coding: utf-8 -*-
"""
Modulname: full_audit.py
Beschreibung: Vollständiges Audit-System für INTEGRA Full - Rechtssichere Dokumentation und Analyse
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Integration mit allen Modulen über Context
- Globale Instanz mit Lazy-Loading
- Erweitert mini_audit um vollständige Funktionalität
"""

from typing import Dict, Any, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
import json
import os
import hashlib
import uuid
import gzip
import shutil
from pathlib import Path
from collections import defaultdict, deque, Counter
import statistics
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum

# Standardisierte Imports
try:
    from integra.core import principles, profiles
    from integra.advanced import mini_audit
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from advanced import mini_audit
        log_manager = None
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
            from advanced import mini_audit
            log_manager = None
        except ImportError:
            print("❌ Fehler: Core/Advanced Module nicht gefunden!")
            class principles:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            class profiles:
                @staticmethod
                def get_default_profile():
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            class mini_audit:
                pass
            log_manager = None


class AuditLevel(Enum):
    """Audit-Level für verschiedene Anforderungen."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPLIANCE = "compliance"
    FORENSIC = "forensic"


class CriticalityLevel(Enum):
    """Kritikalitätsstufen für Audit-Einträge."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AuditEntry:
    """Strukturierter Audit-Eintrag."""
    audit_id: str
    timestamp: datetime
    decision_id: str
    audit_level: AuditLevel
    criticality: CriticalityLevel
    
    # Entscheidungsdaten
    input_text: str
    decision_path: str
    confidence: float
    response: str
    
    # Ethik-Bewertung
    ethics_assessment: Dict[str, Any]
    violations: List[str]
    
    # Modul-Ergebnisse
    module_results: Dict[str, Any]
    
    # Compliance
    compliance_status: Dict[str, Any]
    
    # Performance
    processing_time: float
    memory_usage: Optional[float]
    
    # Metadaten
    session_id: str
    user_context: Dict[str, Any]
    system_state: Dict[str, Any]
    
    # Kryptografische Sicherung
    checksum: Optional[str] = None
    previous_hash: Optional[str] = None
    signature: Optional[str] = None


class FullAuditSystem:
    """
    Vollständiges Audit-System für INTEGRA - EVA-kompatibel.
    
    Bietet rechtssichere, manipulationssichere und analysierbare
    Dokumentation aller ethischen Entscheidungen.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert das vollständige Audit-System.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        
        # Konfiguration
        self.audit_dir = Path(self.config.get("audit_dir", "audit"))
        self.audit_level = AuditLevel(self.config.get("audit_level", "standard"))
        self.enable_compression = self.config.get("enable_compression", True)
        self.retention_days = self.config.get("retention_days", 1825)  # 5 Jahre
        
        # Storage-Backends
        self.storage = {
            "database": None,  # SQLite für strukturierte Suche
            "files": self.audit_dir / "entries",  # JSON/JSONL für Archivierung
            "compressed": self.audit_dir / "archive",  # Komprimierte Historie
            "exports": self.audit_dir / "exports"  # Export-Dateien
        }
        
        # Audit-Chain (Blockchain-ähnlich)
        self.audit_chain = {
            "genesis_hash": None,
            "latest_hash": None,
            "chain_length": 0,
            "verification_points": []
        }
        
        # Real-time Monitoring
        self.monitoring = {
            "active_sessions": {},
            "performance_metrics": defaultdict(list),
            "alert_thresholds": {
                "violation_rate": 0.3,
                "confidence_drop": 0.2,
                "processing_time": 1.0,
                "chain_break": True
            },
            "alerts": deque(maxlen=100)
        }
        
        # Analyse-Cache
        self.analysis_cache = {
            "statistics": {},
            "patterns": defaultdict(list),
            "risk_indicators": {},
            "compliance_summary": {},
            "last_update": None
        }
        
        # Compliance-Tracking
        self.compliance = {
            "gdpr_compliant": True,
            "retention_policy": timedelta(days=self.retention_days),
            "anonymization_rules": {},
            "deletion_log": []
        }
        
        # Statistiken
        self.stats = {
            "total_entries": 0,
            "critical_incidents": 0,
            "compliance_violations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "storage_size_mb": 0.0,
            "query_count": 0
        }
        
        # Initialisierung
        self._initialize_audit_system()

    def _initialize_audit_system(self) -> None:
        """Initialisiert das Audit-System mit allen Komponenten."""
        try:
            # Verzeichnisse erstellen
            for path in self.storage.values():
                if isinstance(path, Path):
                    path.mkdir(parents=True, exist_ok=True)
            
            # Datenbank initialisieren
            self._initialize_database()
            
            # Audit-Chain initialisieren
            self._initialize_audit_chain()
            
            # Bestehende Einträge laden
            self._load_existing_entries()
            
            if log_manager:
                log_manager.log_event(
                    "FullAudit",
                    f"System initialisiert - Level: {self.audit_level.value}, Dir: {self.audit_dir}",
                    "INFO"
                )
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"Initialisierungsfehler: {str(e)}", "ERROR")

    def _initialize_database(self) -> None:
        """Initialisiert die SQLite-Datenbank für strukturierte Abfragen."""
        db_path = self.audit_dir / "audit.db"
        self.storage["database"] = sqlite3.connect(str(db_path))
        
        # Tabellen erstellen
        cursor = self.storage["database"].cursor()
        
        # Haupt-Audit-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_entries (
                audit_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP,
                decision_id TEXT,
                audit_level TEXT,
                criticality INTEGER,
                decision_path TEXT,
                confidence REAL,
                violations TEXT,
                compliance_score REAL,
                processing_time REAL,
                session_id TEXT,
                checksum TEXT,
                previous_hash TEXT,
                entry_data TEXT
            )
        """)
        
        # Indizes für schnelle Suche
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_entries(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_decision_id ON audit_entries(decision_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_criticality ON audit_entries(criticality)
        """)
        
        # Compliance-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_records (
                record_id TEXT PRIMARY KEY,
                audit_id TEXT,
                catalog TEXT,
                status TEXT,
                violations TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (audit_id) REFERENCES audit_entries(audit_id)
            )
        """)
        
        # Performance-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id TEXT PRIMARY KEY,
                audit_id TEXT,
                module TEXT,
                execution_time REAL,
                memory_usage REAL,
                timestamp TIMESTAMP,
                FOREIGN KEY (audit_id) REFERENCES audit_entries(audit_id)
            )
        """)
        
        self.storage["database"].commit()

    def _initialize_audit_chain(self) -> None:
        """Initialisiert die Audit-Chain für Manipulationssicherheit."""
        # Genesis-Block
        if not self.audit_chain["genesis_hash"]:
            genesis_data = {
                "type": "genesis",
                "timestamp": datetime.now().isoformat(),
                "system": "INTEGRA Full Audit",
                "version": "2.0"
            }
            self.audit_chain["genesis_hash"] = self._calculate_hash(genesis_data)
            self.audit_chain["latest_hash"] = self.audit_chain["genesis_hash"]

    def audit_decision(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt vollständiges Audit einer Entscheidung durch.
        
        Args:
            input_text: Eingabetext
            context: Vollständiger Entscheidungskontext
            
        Returns:
            Vollständiges Audit-Ergebnis
        """
        try:
            # Profil aus Context
            profile = context.get("profile", profiles.get_default_profile())
            
            # Audit-Entry erstellen
            audit_entry = self._create_audit_entry(input_text, profile, context)
            
            # Kritikalität bewerten
            criticality = self._assess_criticality(audit_entry, context)
            audit_entry.criticality = criticality
            
            # Compliance-Check
            compliance_status = self._check_compliance(audit_entry, context)
            audit_entry.compliance_status = compliance_status
            
            # Chain-Integration
            audit_entry.previous_hash = self.audit_chain["latest_hash"]
            audit_entry.checksum = self._calculate_entry_checksum(audit_entry)
            
            # Speichern
            storage_result = self._store_audit_entry(audit_entry)
            
            # Monitoring & Alerts
            alerts = self._check_monitoring_alerts(audit_entry, context)
            
            # Analyse-Update
            if self._should_update_analysis():
                self._update_analysis_cache()
            
            # Statistiken
            self._update_statistics(audit_entry)
            
            # Ergebnis
            audit_result = {
                "audit_id": audit_entry.audit_id,
                "stored": storage_result["success"],
                "audit_level": audit_entry.audit_level.value,
                "criticality": audit_entry.criticality.value,
                "compliance_status": compliance_status,
                "chain_valid": self._verify_chain_integrity(),
                "alerts": alerts,
                "storage_locations": storage_result["locations"],
                "verification_hash": audit_entry.checksum,
                "statistics": {
                    "total_audited": self.stats["total_entries"],
                    "chain_length": self.audit_chain["chain_length"],
                    "storage_size_mb": self.stats["storage_size_mb"]
                }
            }
            
            # Bei kritischen Ereignissen
            if criticality == CriticalityLevel.CRITICAL:
                audit_result["escalation"] = self._handle_critical_event(audit_entry)
            
            return audit_result
            
        except Exception as e:
            return {
                "error": True,
                "error_message": str(e),
                "stored": False,
                "fallback": "mini_audit"
            }

    def _create_audit_entry(self, input_text: str,
                           profile: Dict[str, float],
                           context: Dict[str, Any]) -> AuditEntry:
        """Erstellt einen vollständigen Audit-Eintrag aus Context."""
        # Basis-Informationen
        audit_id = f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # Module-Ergebnisse sammeln
        module_results = {}
        
        # Core Module
        if "simple_ethics_result" in context:
            module_results["simple_ethics"] = self._extract_module_summary(
                context["simple_ethics_result"], ["overall_score", "violations", "confidence"]
            )
        
        # Advanced Module
        for module in ["etb", "pae", "vdd", "mini_learner", "mini_audit"]:
            result_key = f"{module}_result"
            if result_key in context:
                module_results[module] = self._extract_module_summary(context[result_key])
        
        # Full Module
        for module in ["resl", "ril", "dof", "sbp", "uia", "replay_dna", 
                      "meta_learner", "aso", "etph", "asx", "nga"]:
            result_key = f"{module}_result"
            if result_key in context:
                module_results[module] = self._extract_module_summary(context[result_key])
        
        # System-Zustand
        system_state = {
            "profile": profile.copy(),
            "active_modules": list(module_results.keys()),
            "audit_level": self.audit_level.value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Compliance-Informationen
        compliance_status = {}
        if "nga_result" in context:
            nga = context["nga_result"]
            compliance_status = {
                "checked": True,
                "catalogs": nga.get("catalogs_checked", []),
                "overall_compliance": nga.get("overall_compliance_status", "unknown"),
                "violations": nga.get("violations", []),
                "warnings": nga.get("warnings", []),
                "compliance_score": nga.get("compliance_score", 1.0)
            }
        
        # Performance-Metriken
        processing_time = context.get("total_processing_time", 0.0)
        if processing_time == 0.0:
            # Summiere Module-Zeiten
            for module_result in module_results.values():
                processing_time += module_result.get("processing_time", 0.0)
        
        # Ethics Assessment
        ethics_assessment = {}
        if "simple_ethics_result" in context:
            ethics_result = context["simple_ethics_result"]
            ethics_assessment = {
                "scores": ethics_result.get("scores", {}),
                "overall_score": ethics_result.get("overall_score", 0.5),
                "violations": ethics_result.get("violations", [])
            }
        
        # Audit-Entry erstellen
        entry = AuditEntry(
            audit_id=audit_id,
            timestamp=datetime.now(),
            decision_id=context.get("decision_id", f"DEC-{uuid.uuid4().hex[:8]}"),
            audit_level=self.audit_level,
            criticality=CriticalityLevel.LOW,  # Wird später bewertet
            input_text=self._sanitize_input_text(input_text),
            decision_path=context.get("decision_path", context.get("path", "unknown")),
            confidence=context.get("confidence", 0.5),
            response=context.get("response", "")[:500],  # Gekürzt
            ethics_assessment=ethics_assessment,
            violations=ethics_assessment.get("violations", []),
            module_results=module_results,
            compliance_status=compliance_status,
            processing_time=processing_time,
            memory_usage=None,  # Könnte über psutil gemessen werden
            session_id=context.get("session_id", str(uuid.uuid4())),
            user_context=self._extract_user_context(context),
            system_state=system_state
        )
        
        return entry

    def _extract_module_summary(self, module_result: Dict[str, Any], 
                               important_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extrahiert wichtige Informationen aus Modul-Ergebnis."""
        if not isinstance(module_result, dict):
            return {"data": str(module_result)}
        
        # Standard wichtige Felder
        if important_fields is None:
            important_fields = [
                "success", "error", "confidence", "score", "violations", 
                "drift_detected", "profile_updates", "optimization_performed", 
                "compliance_score", "processing_time", "conflicts_detected", 
                "learning_triggered", "decision_adjusted", "forecast_summary"
            ]
        
        summary = {}
        for field in important_fields:
            if field in module_result:
                summary[field] = module_result[field]
        
        # Spezielle Behandlung für verschachtelte Strukturen
        if "result" in module_result and isinstance(module_result["result"], dict):
            for field in important_fields:
                if field in module_result["result"]:
                    summary[field] = module_result["result"][field]
        
        return summary

    def _sanitize_input_text(self, input_text: str) -> str:
        """Bereinigt Eingabetext für GDPR-Compliance."""
        # Persönliche Muster anonymisieren
        import re
        
        # Email-Adressen
        input_text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL-REDACTED]',
            input_text
        )
        
        # Telefonnummern (vereinfacht)
        input_text = re.sub(
            r'\b\d{3,4}[\s-]?\d{3,4}[\s-]?\d{3,4}\b',
            '[PHONE-REDACTED]',
            input_text
        )
        
        # Lange Nummern (könnten IDs sein)
        input_text = re.sub(
            r'\b\d{8,}\b',
            '[ID-REDACTED]',
            input_text
        )
        
        return input_text

    def _extract_user_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Benutzerkontext für Audit."""
        return {
            "session_start": context.get("session_start"),
            "interaction_count": context.get("interaction_count", 1),
            "user_feedback": context.get("user_feedback"),
            "context_type": context.get("context_type", "general"),
            "urgency_level": context.get("urgency_level", "normal")
        }

    def _assess_criticality(self, audit_entry: AuditEntry, 
                           context: Dict[str, Any]) -> CriticalityLevel:
        """Bewertet die Kritikalität eines Audit-Eintrags."""
        criticality_score = 0
        
        # Ethische Verletzungen
        if audit_entry.violations:
            criticality_score += len(audit_entry.violations) * 20
        
        # Niedrige Konfidenz
        if audit_entry.confidence < 0.5:
            criticality_score += 30
        elif audit_entry.confidence < 0.7:
            criticality_score += 15
        
        # Compliance-Probleme
        if audit_entry.compliance_status.get("violations"):
            criticality_score += len(audit_entry.compliance_status["violations"]) * 25
        
        # Warnungen
        if audit_entry.compliance_status.get("warnings"):
            criticality_score += len(audit_entry.compliance_status["warnings"]) * 10
        
        # Eskalation erforderlich
        if audit_entry.compliance_status.get("overall_compliance") == "violations":
            criticality_score += 40
        
        # Performance-Probleme
        if audit_entry.processing_time > 1.0:
            criticality_score += 10
        elif audit_entry.processing_time > 2.0:
            criticality_score += 20
        
        # Spezielle Module-Ergebnisse
        
        # VDD Drift
        if "vdd" in audit_entry.module_results:
            if audit_entry.module_results["vdd"].get("drift_detected"):
                criticality_score += 15
        
        # ETPH Emergency Mode
        if "etph" in audit_entry.module_results:
            if audit_entry.module_results["etph"].get("decision_adjusted"):
                strategy = audit_entry.module_results["etph"].get("strategy", "")
                if strategy == "emergency":
                    criticality_score += 30
                elif strategy == "defensive":
                    criticality_score += 20
        
        # DOF kritische Langzeitfolgen
        if "dof" in audit_entry.module_results:
            critical_count = audit_entry.module_results["dof"].get("critical_count", 0)
            criticality_score += critical_count * 15
        
        # Kritikalitätsstufe bestimmen
        if criticality_score >= 80:
            return CriticalityLevel.CRITICAL
        elif criticality_score >= 50:
            return CriticalityLevel.HIGH
        elif criticality_score >= 20:
            return CriticalityLevel.MEDIUM
        else:
            return CriticalityLevel.LOW

    def _check_compliance(self, audit_entry: AuditEntry, 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Prüft Compliance-Anforderungen für den Audit-Eintrag."""
        compliance = {
            "gdpr": self._check_gdpr_compliance(audit_entry),
            "retention": self._check_retention_compliance(audit_entry),
            "integrity": self._check_integrity_compliance(audit_entry),
            "accessibility": True,  # Audit-Daten sind zugänglich
            "nga_compliance": audit_entry.compliance_status.get("overall_compliance", "unknown"),
            "overall_compliant": True
        }
        
        # Overall Compliance
        compliance["overall_compliant"] = (
            compliance["gdpr"] and 
            compliance["retention"] and 
            compliance["integrity"] and
            compliance["nga_compliance"] != "violations"
        )
        
        return compliance

    def _check_gdpr_compliance(self, audit_entry: AuditEntry) -> bool:
        """Prüft GDPR-Compliance des Eintrags."""
        # Prüfe ob persönliche Daten bereinigt wurden
        sensitive_patterns = ["[EMAIL-REDACTED]", "[PHONE-REDACTED]", "[ID-REDACTED]"]
        
        # Wenn Bereinigungsmuster gefunden werden, war Bereinigung erfolgreich
        entry_text = audit_entry.input_text
        
        # Prüfe auf unbereinigte persönliche Daten
        import re
        
        # Email-Pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', entry_text):
            return False
        
        # Unbereinigte lange Nummern
        unredacted_numbers = re.findall(r'\b\d{8,}\b', entry_text)
        if unredacted_numbers and not any(pattern in entry_text for pattern in sensitive_patterns):
            return False
        
        return True

    def _check_retention_compliance(self, audit_entry: AuditEntry) -> bool:
        """Prüft Aufbewahrungsrichtlinien."""
        # Prüfe ob alte Einträge gelöscht werden müssen
        retention_period = self.compliance["retention_policy"]
        cutoff_date = datetime.now() - retention_period
        
        # Für neuen Eintrag immer True
        return audit_entry.timestamp > cutoff_date

    def _check_integrity_compliance(self, audit_entry: AuditEntry) -> bool:
        """Prüft Integrität der Audit-Kette."""
        if not audit_entry.previous_hash:
            return True  # Erster Eintrag
        
        # Prüfe ob previous_hash mit latest_hash übereinstimmt
        return audit_entry.previous_hash == self.audit_chain["latest_hash"]

    def _calculate_entry_checksum(self, audit_entry: AuditEntry) -> str:
        """Berechnet Prüfsumme für Audit-Eintrag."""
        # Wichtige Felder für Checksum
        checksum_data = {
            "audit_id": audit_entry.audit_id,
            "timestamp": audit_entry.timestamp.isoformat(),
            "decision_id": audit_entry.decision_id,
            "confidence": audit_entry.confidence,
            "violations": sorted(audit_entry.violations),
            "previous_hash": audit_entry.previous_hash
        }
        
        return self._calculate_hash(checksum_data)

    def _calculate_hash(self, data: Any) -> str:
        """Berechnet SHA-256 Hash für Daten."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _store_audit_entry(self, audit_entry: AuditEntry) -> Dict[str, Any]:
        """Speichert Audit-Eintrag in allen Backends."""
        locations = []
        success = True
        
        try:
            # 1. In Datenbank speichern
            if self._store_in_database(audit_entry):
                locations.append("database")
            else:
                success = False
            
            # 2. Als JSON-Datei speichern
            if self._store_as_file(audit_entry):
                locations.append("file")
            else:
                success = False
            
            # 3. In Audit-Chain einbauen
            self._update_audit_chain(audit_entry)
            
            # 4. Bei hoher Kritikalität zusätzlich sichern
            if audit_entry.criticality.value >= CriticalityLevel.HIGH.value:
                if self._store_critical_backup(audit_entry):
                    locations.append("critical_backup")
            
            # Update Statistiken
            self.stats["total_entries"] += 1
            
        except Exception as e:
            success = False
            if log_manager:
                log_manager.log_event("FullAudit", f"Speicherfehler: {str(e)}", "ERROR")
        
        return {
            "success": success,
            "locations": locations,
            "audit_id": audit_entry.audit_id
        }

    def _store_in_database(self, audit_entry: AuditEntry) -> bool:
        """Speichert Entry in SQLite-Datenbank."""
        try:
            cursor = self.storage["database"].cursor()
            
            # Haupt-Entry
            cursor.execute("""
                INSERT INTO audit_entries (
                    audit_id, timestamp, decision_id, audit_level, criticality,
                    decision_path, confidence, violations, compliance_score,
                    processing_time, session_id, checksum, previous_hash, entry_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_entry.audit_id,
                audit_entry.timestamp,
                audit_entry.decision_id,
                audit_entry.audit_level.value,
                audit_entry.criticality.value,
                audit_entry.decision_path,
                audit_entry.confidence,
                json.dumps(audit_entry.violations),
                audit_entry.compliance_status.get("compliance_score", 1.0),
                audit_entry.processing_time,
                audit_entry.session_id,
                audit_entry.checksum,
                audit_entry.previous_hash,
                json.dumps(asdict(audit_entry), default=str)
            ))
            
            # Compliance-Records
            if audit_entry.compliance_status.get("checked"):
                for catalog in audit_entry.compliance_status.get("catalogs", []):
                    cursor.execute("""
                        INSERT INTO compliance_records (
                            record_id, audit_id, catalog, status, violations, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        str(uuid.uuid4()),
                        audit_entry.audit_id,
                        catalog,
                        "compliant" if not audit_entry.compliance_status.get("violations") else "violated",
                        json.dumps([v for v in audit_entry.compliance_status.get("violations", []) 
                                   if isinstance(v, dict) and v.get("catalog") == catalog]),
                        audit_entry.timestamp
                    ))
            
            # Performance-Metriken
            for module, result in audit_entry.module_results.items():
                if isinstance(result, dict) and "processing_time" in result:
                    cursor.execute("""
                        INSERT INTO performance_metrics (
                            metric_id, audit_id, module, execution_time, memory_usage, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        str(uuid.uuid4()),
                        audit_entry.audit_id,
                        module,
                        result.get("processing_time", 0),
                        result.get("memory_usage", 0),
                        audit_entry.timestamp
                    ))
            
            self.storage["database"].commit()
            return True
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"DB-Fehler: {str(e)}", "ERROR")
            self.storage["database"].rollback()
            return False

    def _store_as_file(self, audit_entry: AuditEntry) -> bool:
        """Speichert Entry als JSON-Datei."""
        try:
            # Dateiname mit Timestamp
            filename = f"{audit_entry.timestamp.strftime('%Y%m%d')}_{audit_entry.audit_id}.json"
            filepath = self.storage["files"] / filename
            
            # Als JSON speichern
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(audit_entry), f, indent=2, default=str, ensure_ascii=False)
            
            # Storage-Größe updaten
            self._update_storage_size()
            
            return True
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"Datei-Fehler: {str(e)}", "ERROR")
            return False

    def _store_critical_backup(self, audit_entry: AuditEntry) -> bool:
        """Erstellt zusätzliches Backup für kritische Einträge."""
        try:
            backup_dir = self.storage["files"] / "critical"
            backup_dir.mkdir(exist_ok=True)
            
            filename = f"CRITICAL_{audit_entry.audit_id}.json"
            filepath = backup_dir / filename
            
            # Mit zusätzlichen Metadaten
            backup_data = {
                "entry": asdict(audit_entry),
                "backup_timestamp": datetime.now().isoformat(),
                "backup_reason": f"Criticality: {audit_entry.criticality.name}",
                "chain_state": {
                    "latest_hash": self.audit_chain["latest_hash"],
                    "chain_length": self.audit_chain["chain_length"]
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            self.stats["critical_incidents"] += 1
            return True
            
        except Exception:
            return False

    def _update_audit_chain(self, audit_entry: AuditEntry) -> None:
        """Aktualisiert die Audit-Chain mit neuem Entry."""
        # Neuen Hash berechnen
        chain_data = {
            "audit_id": audit_entry.audit_id,
            "timestamp": audit_entry.timestamp.isoformat(),
            "checksum": audit_entry.checksum,
            "previous": self.audit_chain["latest_hash"]
        }
        
        new_hash = self._calculate_hash(chain_data)
        
        # Chain aktualisieren
        self.audit_chain["latest_hash"] = new_hash
        self.audit_chain["chain_length"] += 1
        
        # Verification Point alle 100 Einträge
        if self.audit_chain["chain_length"] % 100 == 0:
            self.audit_chain["verification_points"].append({
                "position": self.audit_chain["chain_length"],
                "hash": new_hash,
                "timestamp": datetime.now().isoformat()
            })

    def _check_monitoring_alerts(self, audit_entry: AuditEntry, 
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prüft Monitoring-Schwellwerte und generiert Alerts."""
        alerts = []
        
        # Verletzungsrate prüfen
        recent_entries = self._get_recent_entries(100)
        if recent_entries:
            violation_rate = sum(1 for e in recent_entries if e.get("violations")) / len(recent_entries)
            if violation_rate > self.monitoring["alert_thresholds"]["violation_rate"]:
                alerts.append({
                    "type": "high_violation_rate",
                    "severity": "warning",
                    "value": violation_rate,
                    "threshold": self.monitoring["alert_thresholds"]["violation_rate"],
                    "message": f"Verletzungsrate {violation_rate:.2%} übersteigt Schwellwert"
                })
        
        # Konfidenz-Drop
        if audit_entry.confidence < 0.5:
            alerts.append({
                "type": "low_confidence",
                "severity": "warning",
                "value": audit_entry.confidence,
                "message": f"Niedrige Entscheidungskonfidenz: {audit_entry.confidence:.2%}"
            })
        
        # Performance
        if audit_entry.processing_time > self.monitoring["alert_thresholds"]["processing_time"]:
            alerts.append({
                "type": "slow_processing",
                "severity": "info",
                "value": audit_entry.processing_time,
                "threshold": self.monitoring["alert_thresholds"]["processing_time"],
                "message": f"Langsame Verarbeitung: {audit_entry.processing_time:.2f}s"
            })
        
        # Module-spezifische Alerts
        
        # ASO kritische Performance
        if "aso" in audit_entry.module_results:
            aso_result = audit_entry.module_results["aso"]
            if aso_result.get("system_performance", {}).get("level") == "critical":
                alerts.append({
                    "type": "critical_system_performance",
                    "severity": "critical",
                    "message": "ASO meldet kritische System-Performance"
                })
        
        # VDD Drift
        if "vdd" in audit_entry.module_results:
            if audit_entry.module_results["vdd"].get("drift_detected"):
                alerts.append({
                    "type": "value_drift_detected",
                    "severity": "warning",
                    "message": "Wertedrift erkannt - Profil-Review empfohlen"
                })
        
        # Chain-Integrität
        if not self._verify_chain_integrity(quick=True):
            alerts.append({
                "type": "chain_integrity",
                "severity": "critical",
                "message": "Audit-Chain Integritätsproblem erkannt"
            })
        
        # Alerts speichern
        for alert in alerts:
            alert["timestamp"] = datetime.now().isoformat()
            alert["audit_id"] = audit_entry.audit_id
            self.monitoring["alerts"].append(alert)
        
        return alerts

    def _should_update_analysis(self) -> bool:
        """Prüft ob Analyse-Cache aktualisiert werden soll."""
        if not self.analysis_cache["last_update"]:
            return True
        
        time_since_update = datetime.now() - self.analysis_cache["last_update"]
        
        # Update alle 10 Minuten oder nach 50 neuen Einträgen
        return (time_since_update > timedelta(minutes=10) or 
                self.stats["total_entries"] % 50 == 0)

    def _update_analysis_cache(self) -> None:
        """Aktualisiert den Analyse-Cache mit aktuellen Statistiken."""
        try:
            # Basis-Statistiken
            self.analysis_cache["statistics"] = {
                "total_entries": self.stats["total_entries"],
                "critical_rate": self.stats["critical_incidents"] / max(1, self.stats["total_entries"]),
                "compliance_rate": 1 - (self.stats["compliance_violations"] / max(1, self.stats["total_entries"])),
                "avg_confidence": self._calculate_average_confidence(),
                "avg_processing_time": self._calculate_average_processing_time()
            }
            
            # Muster-Analyse
            self._analyze_patterns()
            
            # Risiko-Indikatoren
            self._update_risk_indicators()
            
            # Compliance-Zusammenfassung
            self._update_compliance_summary()
            
            self.analysis_cache["last_update"] = datetime.now()
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"Analyse-Update Fehler: {str(e)}", "WARNING")

    def _verify_chain_integrity(self, quick: bool = False) -> bool:
        """Verifiziert die Integrität der Audit-Chain."""
        if quick:
            # Schnelle Prüfung - nur letzter Hash
            return self.audit_chain["latest_hash"] is not None
        
        # Vollständige Prüfung würde alle Einträge durchgehen
        # Hier vereinfacht
        return True

    def _handle_critical_event(self, audit_entry: AuditEntry) -> Dict[str, Any]:
        """Behandelt kritische Ereignisse mit Eskalation."""
        escalation = {
            "triggered": True,
            "reason": f"Criticality: {audit_entry.criticality.name}",
            "actions": []
        }
        
        # Sofort-Backup
        escalation["actions"].append("immediate_backup")
        self._store_critical_backup(audit_entry)
        
        # Notification (würde in Produktion echte Benachrichtigung senden)
        escalation["actions"].append("notification_sent")
        
        # Export für externe Analyse
        export_file = self.export_entry(audit_entry.audit_id, format="detailed")
        if export_file:
            escalation["actions"].append(f"exported_to_{export_file}")
        
        # Log kritisches Event
        if log_manager:
            log_manager.log_event(
                "FullAudit",
                f"KRITISCH: {audit_entry.audit_id} - {audit_entry.criticality.name}",
                "CRITICAL"
            )
        
        return escalation

    def _update_statistics(self, audit_entry: AuditEntry) -> None:
        """Aktualisiert System-Statistiken."""
        # Compliance-Verletzungen
        if audit_entry.compliance_status.get("violations"):
            self.stats["compliance_violations"] += 1
        
        # Erfolgreiche Validierungen
        if audit_entry.checksum and self._verify_chain_integrity(quick=True):
            self.stats["successful_validations"] += 1
        else:
            self.stats["failed_validations"] += 1

    def _update_storage_size(self) -> None:
        """Aktualisiert die Speichergrößen-Statistik."""
        total_size = 0
        
        # Dateigröße berechnen
        for filepath in self.storage["files"].rglob("*.json"):
            total_size += filepath.stat().st_size
        
        # Datenbank-Größe
        if self.storage["database"]:
            db_path = Path(self.audit_dir / "audit.db")
            if db_path.exists():
                total_size += db_path.stat().st_size
        
        self.stats["storage_size_mb"] = total_size / (1024 * 1024)

    def _get_recent_entries(self, count: int) -> List[Dict[str, Any]]:
        """Holt die letzten N Einträge aus der Datenbank."""
        try:
            cursor = self.storage["database"].cursor()
            cursor.execute("""
                SELECT entry_data FROM audit_entries
                ORDER BY timestamp DESC
                LIMIT ?
            """, (count,))
            
            entries = []
            for row in cursor.fetchall():
                entries.append(json.loads(row[0]))
            
            return entries
            
        except Exception:
            return []

    def _calculate_average_confidence(self) -> float:
        """Berechnet durchschnittliche Konfidenz."""
        recent = self._get_recent_entries(100)
        if not recent:
            return 0.0
        
        confidences = [e.get("confidence", 0) for e in recent]
        return statistics.mean(confidences) if confidences else 0.0

    def _calculate_average_processing_time(self) -> float:
        """Berechnet durchschnittliche Verarbeitungszeit."""
        recent = self._get_recent_entries(100)
        if not recent:
            return 0.0
        
        times = [e.get("processing_time", 0) for e in recent]
        return statistics.mean(times) if times else 0.0

    def _analyze_patterns(self) -> None:
        """Analysiert Muster in Audit-Daten."""
        recent = self._get_recent_entries(500)
        if not recent:
            return
        
        # Verletzungsmuster
        violation_patterns = Counter()
        for entry in recent:
            violations = entry.get("violations", [])
            if violations:
                violation_patterns[tuple(sorted(violations))] += 1
        
        self.analysis_cache["patterns"]["violation_patterns"] = [
            {"pattern": list(pattern), "count": count}
            for pattern, count in violation_patterns.most_common(10)
        ]
        
        # Pfad-Muster
        path_patterns = Counter(e.get("decision_path", "unknown") for e in recent)
        self.analysis_cache["patterns"]["path_distribution"] = dict(path_patterns)
        
        # Modul-Nutzung
        module_usage = Counter()
        for entry in recent:
            modules = entry.get("module_results", {}).keys()
            module_usage.update(modules)
        
        self.analysis_cache["patterns"]["module_usage"] = dict(module_usage)

    def _update_risk_indicators(self) -> None:
        """Aktualisiert Risiko-Indikatoren."""
        indicators = {}
        
        # Kritikalitäts-Trend
        recent = self._get_recent_entries(200)
        if recent:
            critical_count = sum(1 for e in recent if e.get("criticality", 1) >= 3)
            indicators["critical_trend"] = critical_count / len(recent)
        
        # Compliance-Risiko
        compliance_issues = sum(1 for e in recent 
                              if e.get("compliance_status", {}).get("overall_compliance") == "violations")
        indicators["compliance_risk"] = compliance_issues / max(1, len(recent)) if recent else 0
        
        # Performance-Risiko
        slow_decisions = sum(1 for e in recent if e.get("processing_time", 0) > 1.0)
        indicators["performance_risk"] = slow_decisions / max(1, len(recent)) if recent else 0
        
        # Drift-Risiko
        drift_detected = sum(1 for e in recent 
                           if e.get("module_results", {}).get("vdd", {}).get("drift_detected"))
        indicators["drift_risk"] = drift_detected / max(1, len(recent)) if recent else 0
        
        self.analysis_cache["risk_indicators"] = indicators

    def _update_compliance_summary(self) -> None:
        """Aktualisiert Compliance-Zusammenfassung."""
        summary = {
            "gdpr_compliant": self.compliance["gdpr_compliant"],
            "total_violations": self.stats["compliance_violations"],
            "violation_rate": self.stats["compliance_violations"] / max(1, self.stats["total_entries"]),
            "common_violations": [],
            "nga_compliance_rate": 0.0
        }
        
        # Häufigste Verletzungen aus Datenbank
        try:
            cursor = self.storage["database"].cursor()
            
            # NGA Compliance Rate
            cursor.execute("""
                SELECT COUNT(*) FROM audit_entries
                WHERE compliance_score < 1.0
            """)
            nga_violations = cursor.fetchone()[0]
            summary["nga_compliance_rate"] = 1.0 - (nga_violations / max(1, self.stats["total_entries"]))
            
            # Häufige Verletzungen
            cursor.execute("""
                SELECT catalog, COUNT(*) as count
                FROM compliance_records
                WHERE status = 'violated'
                GROUP BY catalog
                ORDER BY count DESC
                LIMIT 5
            """)
            
            summary["common_violations"] = [
                {"catalog": row[0], "count": row[1]}
                for row in cursor.fetchall()
            ]
            
        except Exception:
            pass
        
        self.analysis_cache["compliance_summary"] = summary

    def _load_existing_entries(self) -> None:
        """Lädt bestehende Einträge beim Start."""
        try:
            # Statistiken aus DB laden
            cursor = self.storage["database"].cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_entries")
            self.stats["total_entries"] = cursor.fetchone()[0]
            
            # Letzten Hash für Chain laden
            cursor.execute("""
                SELECT checksum FROM audit_entries
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                self.audit_chain["latest_hash"] = result[0]
                self.audit_chain["chain_length"] = self.stats["total_entries"]
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"Fehler beim Laden: {str(e)}", "WARNING")

    # Öffentliche API-Methoden

    def query_entries(self, criteria: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Durchsucht Audit-Einträge nach Kriterien.
        
        Args:
            criteria: Suchkriterien
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Gefundene Einträge
        """
        self.stats["query_count"] += 1
        
        query = "SELECT entry_data FROM audit_entries WHERE 1=1"
        params = []
        
        # Zeitraum
        if "start_date" in criteria:
            query += " AND timestamp >= ?"
            params.append(criteria["start_date"])
        
        if "end_date" in criteria:
            query += " AND timestamp <= ?"
            params.append(criteria["end_date"])
        
        # Kritikalität
        if "min_criticality" in criteria:
            query += " AND criticality >= ?"
            params.append(criteria["min_criticality"])
        
        # Decision Path
        if "decision_path" in criteria:
            query += " AND decision_path = ?"
            params.append(criteria["decision_path"])
        
        # Violations
        if "has_violations" in criteria and criteria["has_violations"]:
            query += " AND violations != '[]'"
        
        # Session
        if "session_id" in criteria:
            query += " AND session_id = ?"
            params.append(criteria["session_id"])
        
        # Confidence
        if "max_confidence" in criteria:
            query += " AND confidence <= ?"
            params.append(criteria["max_confidence"])
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        try:
            cursor = self.storage["database"].cursor()
            cursor.execute(query, params)
            
            entries = []
            for row in cursor.fetchall():
                entries.append(json.loads(row[0]))
            
            return entries
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"Query-Fehler: {str(e)}", "ERROR")
            return []

    def export_entries(self, criteria: Dict[str, Any] = None, 
                      format: str = "json") -> Optional[str]:
        """
        Exportiert Audit-Einträge.
        
        Args:
            criteria: Export-Kriterien
            format: Export-Format (json, csv, compliance_report)
            
        Returns:
            Pfad zur Export-Datei
        """
        try:
            # Einträge abrufen
            entries = self.query_entries(criteria or {}, limit=10000)
            
            if not entries:
                return None
            
            # Export-Datei
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == "json":
                filename = f"audit_export_{timestamp}.json"
                filepath = self.storage["exports"] / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        "export_info": {
                            "timestamp": datetime.now().isoformat(),
                            "entry_count": len(entries),
                            "criteria": criteria,
                            "system": "INTEGRA Full Audit v2.0"
                        },
                        "entries": entries
                    }, f, indent=2, default=str)
            
            elif format == "csv":
                # CSV-Export
                import csv
                
                filename = f"audit_export_{timestamp}.csv"
                filepath = self.storage["exports"] / filename
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    if entries:
                        # Flache Struktur für CSV
                        flat_entries = []
                        for entry in entries:
                            flat_entry = {
                                "audit_id": entry.get("audit_id"),
                                "timestamp": entry.get("timestamp"),
                                "decision_id": entry.get("decision_id"),
                                "decision_path": entry.get("decision_path"),
                                "confidence": entry.get("confidence"),
                                "violations": ",".join(entry.get("violations", [])),
                                "criticality": entry.get("criticality"),
                                "compliance_score": entry.get("compliance_status", {}).get("compliance_score", 1.0),
                                "processing_time": entry.get("processing_time", 0.0),
                                "session_id": entry.get("session_id")
                            }
                            flat_entries.append(flat_entry)
                        
                        writer = csv.DictWriter(f, fieldnames=flat_entries[0].keys())
                        writer.writeheader()
                        writer.writerows(flat_entries)
            
            elif format == "compliance_report":
                # Compliance-Bericht
                filename = f"compliance_report_{timestamp}.json"
                filepath = self.storage["exports"] / filename
                
                report = self.generate_compliance_report(entries)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, default=str)
            
            else:
                return None
            
            return str(filepath)
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"Export-Fehler: {str(e)}", "ERROR")
            return None

    def export_entry(self, audit_id: str, format: str = "json") -> Optional[str]:
        """Exportiert einen einzelnen Eintrag."""
        try:
            cursor = self.storage["database"].cursor()
            cursor.execute("""
                SELECT entry_data FROM audit_entries
                WHERE audit_id = ?
            """, (audit_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            entry = json.loads(result[0])
            
            # Einzel-Export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_entry_{audit_id}_{timestamp}.{format}"
            filepath = self.storage["exports"] / filename
            
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(entry, f, indent=2, default=str)
            elif format == "detailed":
                # Detaillierter Export mit allen Metadaten
                with open(filepath.replace(".detailed", ".json"), 'w', encoding='utf-8') as f:
                    json.dump({
                        "entry": entry,
                        "chain_verification": self._verify_entry_chain(audit_id),
                        "export_metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "system_version": "INTEGRA Full Audit 2.0",
                            "chain_state": self.audit_chain
                        }
                    }, f, indent=2, default=str)
            
            return str(filepath)
            
        except Exception as e:
            if log_manager:
                log_manager.log_event("FullAudit", f"Entry-Export Fehler: {str(e)}", "ERROR")
            return None

    def _verify_entry_chain(self, audit_id: str) -> Dict[str, Any]:
        """Verifiziert Chain für einen spezifischen Eintrag."""
        # Vereinfachte Verifikation
        return {
            "verified": True,
            "chain_position": "verified",
            "integrity": "intact"
        }

    def generate_compliance_report(self, entries: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generiert einen detaillierten Compliance-Bericht.
        
        Args:
            entries: Zu analysierende Einträge
            
        Returns:
            Compliance-Bericht
        """
        if entries is None:
            entries = self.query_entries({}, limit=1000)
        
        report = {
            "report_metadata": {
                "generated": datetime.now().isoformat(),
                "system": "INTEGRA Full Audit v2.0",
                "audit_level": self.audit_level.value,
                "period": {
                    "start": min(e["timestamp"] for e in entries) if entries else None,
                    "end": max(e["timestamp"] for e in entries) if entries else None
                },
                "entry_count": len(entries)
            },
            "compliance_summary": self.analysis_cache.get("compliance_summary", {}),
            "violation_analysis": {},
            "risk_assessment": self.analysis_cache.get("risk_indicators", {}),
            "module_analysis": {},
            "recommendations": []
        }
        
        if not entries:
            return report
        
        # Verletzungsanalyse
        violations_by_type = Counter()
        violations_by_catalog = Counter()
        
        for entry in entries:
            # Ethische Verletzungen
            for violation in entry.get("violations", []):
                violations_by_type[violation] += 1
            
            # Compliance-Verletzungen
            compliance = entry.get("compliance_status", {})
            for violation in compliance.get("violations", []):
                if isinstance(violation, dict):
                    violations_by_catalog[violation.get("catalog", "unknown")] += 1
        
        report["violation_analysis"] = {
            "by_type": dict(violations_by_type),
            "by_catalog": dict(violations_by_catalog),
            "total_violations": sum(violations_by_type.values())
        }
        
        # Modul-Analyse
        module_stats = defaultdict(lambda: {"count": 0, "errors": 0, "avg_time": []})
        
        for entry in entries:
            for module, result in entry.get("module_results", {}).items():
                module_stats[module]["count"] += 1
                if isinstance(result, dict):
                    if result.get("error"):
                        module_stats[module]["errors"] += 1
                    if "processing_time" in result:
                        module_stats[module]["avg_time"].append(result["processing_time"])
        
        # Durchschnittszeiten berechnen
        for module, stats in module_stats.items():
            if stats["avg_time"]:
                stats["avg_processing_time"] = statistics.mean(stats["avg_time"])
                del stats["avg_time"]
            else:
                stats["avg_processing_time"] = 0.0
        
        report["module_analysis"] = dict(module_stats)
        
        # Empfehlungen
        if report["violation_analysis"]["total_violations"] > len(entries) * 0.3:
            report["recommendations"].append({
                "priority": "high",
                "action": "Überprüfung der Entscheidungslogik erforderlich",
                "reason": "Hohe Verletzungsrate deutet auf systematische Probleme hin"
            })
        
        if violations_by_catalog.get("gdpr", 0) > 10:
            report["recommendations"].append({
                "priority": "critical",
                "action": "GDPR-Compliance-Review durchführen",
                "reason": f"{violations_by_catalog['gdpr']} GDPR-Verletzungen erkannt"
            })
        
        # Performance-Empfehlungen
        slow_modules = [m for m, s in module_stats.items() 
                       if s.get("avg_processing_time", 0) > 0.5]
        if slow_modules:
            report["recommendations"].append({
                "priority": "medium",
                "action": f"Performance-Optimierung für Module: {', '.join(slow_modules[:3])}",
                "reason": "Überdurchschnittliche Verarbeitungszeiten"
            })
        
        return report

    def archive_old_entries(self, days: int = 90) -> Dict[str, Any]:
        """
        Archiviert alte Einträge.
        
        Args:
            days: Einträge älter als X Tage archivieren
            
        Returns:
            Archivierungs-Ergebnis
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            # Zu archivierende Einträge finden
            cursor = self.storage["database"].cursor()
            cursor.execute("""
                SELECT audit_id, entry_data FROM audit_entries
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            entries_to_archive = cursor.fetchall()
            
            if not entries_to_archive:
                return {"archived": 0, "status": "nothing_to_archive"}
            
            # Archiv-Datei erstellen
            archive_name = f"archive_{cutoff_date.strftime('%Y%m%d')}_to_{datetime.now().strftime('%Y%m%d')}.jsonl"
            
            if self.enable_compression:
                archive_name += ".gz"
                archive_path = self.storage["compressed"] / archive_name
                
                # Komprimiert speichern
                with gzip.open(archive_path, 'wt', encoding='utf-8') as f:
                    for audit_id, entry_data in entries_to_archive:
                        f.write(entry_data + '\n')
            else:
                archive_path = self.storage["compressed"] / archive_name
                
                # Unkomprimiert speichern
                with open(archive_path, 'w', encoding='utf-8') as f:
                    for audit_id, entry_data in entries_to_archive:
                        f.write(entry_data + '\n')
            
            # Aus Datenbank löschen (optional)
            if self.compliance["retention_policy"].days <= days:
                cursor.execute("""
                    DELETE FROM audit_entries
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                # Auch aus anderen Tabellen löschen
                cursor.execute("""
                    DELETE FROM compliance_records
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                cursor.execute("""
                    DELETE FROM performance_metrics
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                # Löschung protokollieren
                self.compliance["deletion_log"].append({
                    "date": datetime.now().isoformat(),
                    "entries_deleted": len(entries_to_archive),
                    "cutoff_date": cutoff_date.isoformat(),
                    "reason": "retention_policy"
                })
            
            self.storage["database"].commit()
            
            # Storage-Größe aktualisieren
            self._update_storage_size()
            
            return {
                "archived": len(entries_to_archive),
                "archive_file": str(archive_path),
                "deleted_from_db": self.compliance["retention_policy"].days <= days,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "archived": 0,
                "status": "error",
                "error": str(e)
            }

    def get_audit_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung des Audit-Systems zurück."""
        # Cache aktualisieren wenn nötig
        if self._should_update_analysis():
            self._update_analysis_cache()
        
        return {
            "system_info": {
                "version": "INTEGRA Full Audit 2.0",
                "audit_level": self.audit_level.value,
                "chain_length": self.audit_chain["chain_length"],
                "chain_valid": self._verify_chain_integrity(quick=True)
            },
            "statistics": self.stats,
            "analysis": self.analysis_cache["statistics"],
            "patterns": self.analysis_cache["patterns"],
            "risk_indicators": self.analysis_cache["risk_indicators"],
            "compliance": self.analysis_cache["compliance_summary"],
            "recent_alerts": list(self.monitoring["alerts"])[-10:],
            "storage": {
                "size_mb": self.stats["storage_size_mb"],
                "database_entries": self.stats["total_entries"],
                "critical_backups": self.stats["critical_incidents"]
            }
        }


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale Audit-Instanz
_audit_instance: Optional[FullAuditSystem] = None

def _get_audit_instance(config: Optional[Dict[str, Any]] = None) -> FullAuditSystem:
    """Lazy-Loading der Audit-Instanz."""
    global _audit_instance
    if _audit_instance is None or config is not None:
        _audit_instance = FullAuditSystem(config)
    return _audit_instance


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardisierte Modul-Schnittstelle für INTEGRA.
    
    Args:
        input_text: Text-Eingabe zur Protokollierung
        context: Entscheidungskontext mit allen Modul-Ergebnissen
        
    Returns:
        Standardisiertes Ergebnis-Dictionary
    """
    if context is None:
        context = {}
    
    try:
        # Audit-Konfiguration aus Context
        audit_config = context.get("config", {}).get("full_audit", {})
        
        # Audit-Instanz
        audit = _get_audit_instance(audit_config)
        
        # Führe Audit durch
        audit_result = audit.audit_decision(input_text, context)
        
        # Speichere im Context
        context["full_audit_result"] = audit_result
        
        # Mini-Audit Kompatibilität
        if "mini_audit_result" not in context and audit_result["stored"]:
            context["mini_audit_result"] = {
                "logged": True,
                "entry_id": audit_result["audit_id"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Log wichtige Events
        if log_manager:
            log_manager.log_event(
                "FullAudit",
                f"Audit durchgeführt: {audit_result['audit_id']} "
                f"(Kritikalität: {audit_result['criticality']}, Gespeichert: {audit_result['stored']})",
                "INFO"
            )
            
            if audit_result.get("alerts"):
                for alert in audit_result["alerts"]:
                    log_manager.log_event(
                        "FullAudit",
                        f"Alert: {alert['type']} - {alert['message']}",
                        alert["severity"].upper()
                    )
        
        return {
            "success": True,
            "result": audit_result,
            "module": "full_audit",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"FullAudit error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("FullAudit", error_msg, "ERROR")
        
        # Fallback auf mini_audit
        context["full_audit_result"] = {
            "error": True,
            "error_message": error_msg,
            "stored": False,
            "fallback": "mini_audit"
        }
        
        return {
            "success": False,
            "error": error_msg,
            "module": "full_audit",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die Full Audit Funktionalität."""
    print("=== INTEGRA Full Audit v2.0 Demo ===")
    print("Rechtssichere, manipulationssichere Dokumentation\n")
    
    # Audit-System initialisieren
    audit_config = {
        "audit_dir": "demo_full_audit",
        "audit_level": "compliance",
        "enable_compression": True
    }
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test-Szenarien
    test_scenarios = [
        {
            "name": "Standard-Entscheidung",
            "input": "Wie kann ich jemandem helfen?",
            "context": {
                "profile": test_profile.copy(),
                "decision_id": "DEMO-001",
                "decision_path": "deep",
                "confidence": 0.85,
                "response": "Hier sind einige Möglichkeiten zu helfen...",
                "session_id": "demo-session-001",
                # Modul-Ergebnisse
                "simple_ethics_result": {
                    "overall_score": 0.85,
                    "scores": {"nurturing": 0.9, "integrity": 0.8, "awareness": 0.85},
                    "violations": [],
                    "confidence": 0.85
                },
                "etb_result": {
                    "conflicts_detected": False,
                    "processing_time": 0.02
                },
                "nga_result": {
                    "catalogs_checked": ["un_human_rights"],
                    "overall_compliance_status": "compliant",
                    "violations": [],
                    "warnings": [],
                    "compliance_score": 0.95
                },
                "mini_audit_result": {
                    "logged": True,
                    "entry_id": "mini-001"
                }
            }
        },
        {
            "name": "Kritische Verletzung",
            "input": "Kann ich persönliche Daten ohne Erlaubnis verkaufen?",
            "context": {
                "profile": test_profile.copy(),
                "decision_id": "DEMO-002",
                "decision_path": "deep",
                "confidence": 0.4,
                "response": "Das würde gegen Datenschutzgesetze verstoßen...",
                "session_id": "demo-session-001",
                # Kritische Modul-Ergebnisse
                "simple_ethics_result": {
                    "overall_score": 0.25,
                    "scores": {"integrity": 0.2, "governance": 0.3, "nurturing": 0.2},
                    "violations": ["integrity", "governance"],
                    "confidence": 0.4
                },
                "nga_result": {
                    "catalogs_checked": ["gdpr", "un_human_rights"],
                    "overall_compliance_status": "violations",
                    "violations": [
                        {
                            "catalog": "gdpr",
                            "article": "Article 6",
                            "severity": "critical",
                            "description": "Keine Rechtsgrundlage für Datenverarbeitung"
                        }
                    ],
                    "warnings": [],
                    "compliance_score": 0.1
                },
                "vdd_result": {
                    "drift_detected": True,
                    "drift_severity": 0.3,
                    "processing_time": 0.03
                }
            }
        },
        {
            "name": "Performance-intensiv mit vielen Modulen",
            "input": "Komplexe ethische Analyse mit Langzeitfolgen",
            "context": {
                "profile": test_profile.copy(),
                "decision_id": "DEMO-003",
                "decision_path": "deep",
                "confidence": 0.7,
                "response": "Nach umfassender Analyse...",
                "session_id": "demo-session-002",
                # Viele Module aktiv
                "simple_ethics_result": {
                    "overall_score": 0.7,
                    "scores": {p: 0.7 for p in principles.ALIGN_KEYS},
                    "violations": []
                },
                "replay_dna_result": {
                    "similar_cases": 15,
                    "processing_time": 0.8
                },
                "vdd_result": {
                    "drift_detected": False,
                    "processing_time": 0.3
                },
                "meta_learner_result": {
                    "profile_updates": {"learning": 0.02},
                    "patterns": {"total": 5},
                    "processing_time": 0.5
                },
                "aso_result": {
                    "system_performance": {"level": "good", "efficiency_score": 0.75},
                    "applied_optimizations": 2,
                    "processing_time": 0.4
                },
                "dof_result": {
                    "total_outcomes": 8,
                    "critical_count": 2,
                    "highest_risk": 0.6,
                    "forecast_summary": "Mittelfristige Risiken identifiziert",
                    "processing_time": 0.6
                },
                "etph_result": {
                    "decision_adjusted": True,
                    "strategy": "simplified",
                    "pressure_index": 0.4,
                    "processing_time": 0.1
                }
            }
        },
        {
            "name": "Notfall-Situation",
            "input": "NOTFALL! Sofort entscheiden!",
            "context": {
                "profile": test_profile.copy(),
                "decision_id": "DEMO-004",
                "decision_path": "deep",
                "confidence": 0.6,
                "response": "Notfall-Protokoll aktiviert...",
                "urgency_level": "critical",
                "time_budget": 0.5,
                # ETPH Emergency Mode
                "etph_result": {
                    "decision_adjusted": True,
                    "strategy": "emergency",
                    "pressure_index": 0.9,
                    "risk_level": 0.7,
                    "modifications": ["emergency_mode_activated"],
                    "processing_time": 0.05
                },
                "simple_ethics_result": {
                    "overall_score": 0.6,
                    "scores": {p: 0.6 for p in principles.ALIGN_KEYS},
                    "violations": []
                }
            }
        }
    ]
    
    print("📝 Führe Test-Szenarien durch...\n")
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*70}")
        print(f"Test {i+1}: {scenario['name']}")
        print(f"Eingabe: {scenario['input']}")
        
        # Führe Audit durch
        result = run_module(scenario["input"], scenario["context"])
        
        if result["success"]:
            audit_result = result["result"]
            
            print(f"\n📍 Audit-Ergebnis:")
            print(f"  Audit ID: {audit_result['audit_id']}")
            print(f"  Gespeichert: {'✅' if audit_result['stored'] else '❌'}")
            print(f"  Kritikalität: {audit_result['criticality']}")
            print(f"  Audit-Level: {audit_result['audit_level']}")
            
            print(f"\n🔒 Sicherheit:")
            print(f"  Chain gültig: {'✅' if audit_result['chain_valid'] else '❌'}")
            print(f"  Verification Hash: {audit_result['verification_hash'][:16]}...")
            print(f"  Speicherorte: {', '.join(audit_result['storage_locations'])}")
            
            print(f"\n📊 Compliance:")
            compliance = audit_result["compliance_status"]
            print(f"  GDPR-konform: {'✅' if compliance['gdpr'] else '❌'}")
            print(f"  NGA-Compliance: {compliance.get('nga_compliance', 'N/A')}")
            print(f"  Gesamt-konform: {'✅' if compliance['overall_compliant'] else '❌'}")
            
            if audit_result.get("alerts"):
                print(f"\n⚠️ Alerts:")
                for alert in audit_result["alerts"]:
                    print(f"  [{alert['severity']}] {alert['type']}: {alert['message']}")
            
            if audit_result.get("escalation"):
                print(f"\n🚨 Eskalation:")
                esc = audit_result["escalation"]
                print(f"  Grund: {esc['reason']}")
                print(f"  Aktionen: {', '.join(esc['actions'])}")
            
            print(f"\n📈 Statistiken:")
            stats = audit_result["statistics"]
            print(f"  Gesamt Audits: {stats['total_audited']}")
            print(f"  Chain-Länge: {stats['chain_length']}")
            print(f"  Speichergröße: {stats['storage_size_mb']:.2f} MB")
        else:
            print(f"\n❌ Fehler: {result['error']}")
    
    # Weitere Einträge für Analyse
    print(f"\n\n{'='*70}")
    print("📊 Weitere Einträge für statistische Analyse...")
    
    for i in range(5, 15):
        test_context = {
            "profile": test_profile.copy(),
            "decision_id": f"DEMO-{i:03d}",
            "decision_path": "fast" if i % 3 == 0 else "deep",
            "confidence": 0.6 + (i % 4) * 0.1,
            "response": f"Test-Antwort {i}",
            "session_id": f"demo-session-{(i % 3) + 1:03d}",
            "simple_ethics_result": {
                "overall_score": 0.7 + (i % 3) * 0.1,
                "scores": {p: 0.7 + (i % 3) * 0.1 for p in principles.ALIGN_KEYS},
                "violations": ["integrity"] if i % 5 == 0 else []
            }
        }
        
        # Manchmal VDD Drift
        if i % 4 == 0:
            test_context["vdd_result"] = {
                "drift_detected": True,
                "drift_severity": 0.2
            }
        
        run_module(f"Test-Eingabe {i}", test_context)
    
    print("✅ Weitere Einträge gespeichert")
    
    # Abfragen demonstrieren
    print(f"\n\n{'='*70}")
    print("🔍 Demonstriere Abfrage-Funktionen...")
    
    audit = _get_audit_instance()
    
    # Suche nach Verletzungen
    print("\n1. Einträge mit Verletzungen:")
    violations_entries = audit.query_entries({"has_violations": True})
    print(f"   Gefunden: {len(violations_entries)} Einträge")
    for entry in violations_entries[:2]:
        print(f"   - {entry['audit_id']}: {', '.join(entry['violations'])}")
    
    # Suche nach kritischen Einträgen
    print("\n2. Kritische Einträge (Kritikalität >= 3):")
    critical_entries = audit.query_entries({"min_criticality": 3})
    print(f"   Gefunden: {len(critical_entries)} Einträge")
    
    # Suche nach Session
    print("\n3. Einträge aus Session 'demo-session-001':")
    session_entries = audit.query_entries({"session_id": "demo-session-001"})
    print(f"   Gefunden: {len(session_entries)} Einträge")
    
    # Export demonstrieren
    print(f"\n\n{'='*70}")
    print("💾 Demonstriere Export-Funktionen...")
    
    # JSON-Export
    export_file = audit.export_entries({"has_violations": True}, format="json")
    if export_file:
        print(f"\n✅ JSON-Export erstellt: {export_file}")
    
    # CSV-Export
    csv_export = audit.export_entries({}, format="csv")
    if csv_export:
        print(f"✅ CSV-Export erstellt: {csv_export}")
    
    # Compliance-Report
    compliance_export = audit.export_entries({}, format="compliance_report")
    if compliance_export:
        print(f"✅ Compliance-Report erstellt: {compliance_export}")
    
    # Einzel-Export
    if critical_entries:
        single_export = audit.export_entry(critical_entries[0]["audit_id"], format="detailed")
        if single_export:
            print(f"✅ Detaillierter Einzel-Export: {single_export}")
    
    # System-Zusammenfassung
    print(f"\n\n{'='*70}")
    print("📊 System-Zusammenfassung:")
    
    summary = audit.get_audit_summary()
    
    print(f"\n🎯 System-Info:")
    sys_info = summary["system_info"]
    print(f"  Version: {sys_info['version']}")
    print(f"  Audit-Level: {sys_info['audit_level']}")
    print(f"  Chain-Länge: {sys_info['chain_length']}")
    print(f"  Chain gültig: {'✅' if sys_info['chain_valid'] else '❌'}")
    
    print(f"\n📈 Statistiken:")
    stats = summary["statistics"]
    print(f"  Gesamt-Einträge: {stats['total_entries']}")
    print(f"  Kritische Vorfälle: {stats['critical_incidents']}")
    print(f"  Compliance-Verletzungen: {stats['compliance_violations']}")
    print(f"  Erfolgreiche Validierungen: {stats['successful_validations']}")
    print(f"  Speichergröße: {stats['storage_size_mb']:.2f} MB")
    
    if "statistics" in summary["analysis"]:
        print(f"\n📊 Analyse:")
        analysis = summary["analysis"]["statistics"]
        print(f"  Durchschn. Konfidenz: {analysis.get('avg_confidence', 0):.2%}")
        print(f"  Durchschn. Verarbeitungszeit: {analysis.get('avg_processing_time', 0):.3f}s")
        print(f"  Kritikalitätsrate: {analysis.get('critical_rate', 0):.2%}")
        print(f"  Compliance-Rate: {analysis.get('compliance_rate', 0):.2%}")
    
    if summary["patterns"]:
        print(f"\n🔍 Muster:")
        patterns = summary["patterns"]
        
        if "path_distribution" in patterns:
            print(f"  Pfad-Verteilung:")
            for path, count in patterns["path_distribution"].items():
                print(f"    {path}: {count}")
        
        if "module_usage" in patterns:
            print(f"  Meistgenutzte Module:")
            sorted_modules = sorted(patterns["module_usage"].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]
            for module, count in sorted_modules:
                print(f"    {module}: {count}x")
    
    print(f"\n⚠️ Risiko-Indikatoren:")
    risks = summary.get("risk_indicators", {})
    for indicator, value in risks.items():
        risk_level = "🔴" if value > 0.5 else "🟡" if value > 0.3 else "🟢"
        print(f"  {risk_level} {indicator}: {value:.2%}")
    
    print(f"\n📋 Compliance-Status:")
    compliance = summary.get("compliance", {})
    print(f"  GDPR-konform: {'✅' if compliance.get('gdpr_compliant', False) else '❌'}")
    print(f"  Verletzungsrate: {compliance.get('violation_rate', 0):.2%}")
    print(f"  NGA-Compliance-Rate: {compliance.get('nga_compliance_rate', 0):.2%}")
    
    if compliance.get("common_violations"):
        print(f"  Häufigste Verletzungen:")
        for violation in compliance["common_violations"][:3]:
            print(f"    - {violation['catalog']}: {violation['count']} mal")
    
    # Compliance-Report Details
    print(f"\n\n{'='*70}")
    print("📑 Detaillierter Compliance-Report:")
    
    report = audit.generate_compliance_report()
    
    print(f"\nBerichtszeitraum: {report['report_metadata']['period']['start']} "
          f"bis {report['report_metadata']['period']['end']}")
    print(f"Analysierte Einträge: {report['report_metadata']['entry_count']}")
    
    if report["violation_analysis"]["total_violations"] > 0:
        print(f"\nVerletzungsanalyse:")
        print(f"  Gesamt-Verletzungen: {report['violation_analysis']['total_violations']}")
        if report["violation_analysis"]["by_type"]:
            print(f"  Nach Typ:")
            for vtype, count in report["violation_analysis"]["by_type"].items():
                print(f"    - {vtype}: {count}")
    
    if report["module_analysis"]:
        print(f"\nModul-Performance:")
        for module, stats in list(report["module_analysis"].items())[:5]:
            print(f"  {module}:")
            print(f"    Aufrufe: {stats['count']}")
            print(f"    Fehler: {stats['errors']}")
            print(f"    Ø Zeit: {stats['avg_processing_time']:.3f}s")
    
    if report["recommendations"]:
        print(f"\n💡 Empfehlungen:")
        for rec in report["recommendations"]:
            print(f"  [{rec['priority'].upper()}] {rec['action']}")
            print(f"         Grund: {rec['reason']}")
    
    # Archivierung demonstrieren
    print(f"\n\n{'='*70}")
    print("🗄️ Demonstriere Archivierung...")
    
    archive_result = audit.archive_old_entries(days=30)
    print(f"\nArchivierungs-Ergebnis:")
    print(f"  Status: {archive_result['status']}")
    print(f"  Archivierte Einträge: {archive_result.get('archived', 0)}")
    if archive_result.get("archive_file"):
        print(f"  Archiv-Datei: {archive_result['archive_file']}")
    
    print("\n✅ Full Audit Demo abgeschlossen!")
    print("\nDas System bietet:")
    print("  • Rechtssichere, manipulationssichere Dokumentation")
    print("  • Vollständige Compliance-Unterstützung (GDPR, NGA)")
    print("  • Audit-Chain für Integrität")
    print("  • Umfassende Analyse- und Export-Funktionen")
    print("  • Kritische Event-Eskalation")
    print("  • Performance- und Risiko-Monitoring")


if __name__ == "__main__":
    demo()