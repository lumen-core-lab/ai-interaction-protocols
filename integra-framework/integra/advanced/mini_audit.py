# -*- coding: utf-8 -*-
"""
Modulname: mini_audit.py
Beschreibung: Audit-System für INTEGRA Advanced - Protokollierung ethischer Entscheidungen
Teil von: INTEGRA Light – Advanced Layer
Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
Version: 2.0 - Überarbeitet gemäß INTEGRA 4.2 Standards
"""

from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import os
from pathlib import Path
import uuid
import hashlib
import threading
from collections import defaultdict
import csv

# Import-Kompatibilität
try:
    from integra.core import principles, profiles
    from integra.logging import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from logging import log_manager
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
        except ImportError:
            # Fallback
            class DummyPrinciples:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            principles = DummyPrinciples()
            
            class DummyProfiles:
                def get_default_profile(self):
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            profiles = DummyProfiles()
        
        # Dummy log_manager
        class DummyLogManager:
            def log_event(self, *args, **kwargs): pass
        log_manager = DummyLogManager()


class AuditEventType(Enum):
    """Typen von Audit-Events."""
    DECISION = "decision"
    ETHICS_EVALUATION = "ethics_evaluation"
    PROFILE_CHANGE = "profile_change"
    CONTROL_INTERVENTION = "control_intervention"
    LEARNING_UPDATE = "learning_update"
    ERROR = "error"
    WARNING = "warning"
    SYSTEM = "system"
    USER_FEEDBACK = "user_feedback"
    COMPLIANCE_CHECK = "compliance_check"


class AuditSeverity(Enum):
    """Schweregrad von Audit-Events."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """Strukturierter Audit-Eintrag."""
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    event_type: AuditEventType = AuditEventType.DECISION
    severity: AuditSeverity = AuditSeverity.INFO
    session_id: str = ""
    
    # Kontext
    module: str = ""
    user_input: str = ""
    decision_path: str = ""  # fast/deep/control
    
    # Ethik-Informationen
    ethics_scores: Dict[str, float] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    # Entscheidungsdetails
    chosen_action: str = ""
    alternatives: List[str] = field(default_factory=list)
    reasoning: str = ""
    
    # Module-spezifische Daten
    module_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadaten
    processing_time: float = 0.0
    profile_snapshot: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Compliance
    compliance_flags: List[str] = field(default_factory=list)
    requires_review: bool = False
    
    # Hash für Integrität
    integrity_hash: str = ""
    
    def calculate_hash(self) -> str:
        """Berechnet Hash für Integritätsprüfung."""
        # Wichtige Felder für Hash
        hash_data = {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "user_input": self.user_input,
            "chosen_action": self.chosen_action,
            "ethics_scores": self.ethics_scores
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für JSON-Serialisierung."""
        data = asdict(self)
        # Enums zu Strings
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        return data


class AuditStorage:
    """Verwaltet Speicherung und Rotation von Audit-Logs."""
    
    def __init__(self, log_dir: str = "logs", max_file_size_mb: float = 10.0,
                 max_files: int = 100, rotation_callback: Optional[Callable] = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.max_file_size = max_file_size_mb * 1024 * 1024  # in Bytes
        self.max_files = max_files
        self.rotation_callback = rotation_callback
        
        self.current_file = None
        self.file_counter = 0
        self.write_lock = threading.Lock()
        
        # Index für schnelle Suche
        self.index_file = self.log_dir / "audit_index.json"
        self.index = self._load_index()
        
        self._initialize_current_file()
    
    def _initialize_current_file(self):
        """Initialisiert die aktuelle Log-Datei."""
        # Finde höchste existierende Nummer
        existing_files = list(self.log_dir.glob("audit_*.jsonl"))
        if existing_files:
            numbers = []
            for f in existing_files:
                try:
                    num = int(f.stem.split('_')[1])
                    numbers.append(num)
                except (IndexError, ValueError):
                    continue
            
            if numbers:
                self.file_counter = max(numbers)
        
        # Prüfe ob aktuelle Datei noch Platz hat
        current_file_path = self.log_dir / f"audit_{self.file_counter:04d}.jsonl"
        if current_file_path.exists() and current_file_path.stat().st_size >= self.max_file_size:
            self._rotate_file()
        else:
            self.current_file = current_file_path
    
    def _rotate_file(self):
        """Rotiert zur nächsten Log-Datei."""
        with self.write_lock:
            # Callback vor Rotation
            if self.rotation_callback:
                self.rotation_callback(self.current_file)
            
            # Neue Datei
            self.file_counter += 1
            self.current_file = self.log_dir / f"audit_{self.file_counter:04d}.jsonl"
            
            # Alte Dateien löschen wenn zu viele
            self._cleanup_old_files()
            
            # Index aktualisieren
            self._update_index()
    
    def _cleanup_old_files(self):
        """Löscht alte Dateien wenn Limit überschritten."""
        files = sorted(self.log_dir.glob("audit_*.jsonl"))
        if len(files) > self.max_files:
            for f in files[:len(files) - self.max_files]:
                try:
                    f.unlink()
                    log_manager.log_event("MiniAudit", f"Alte Datei gelöscht: {f}", "INFO")
                except Exception as e:
                    log_manager.log_event("MiniAudit", f"Fehler beim Löschen: {e}", "ERROR")
    
    def write_entry(self, entry: AuditEntry) -> bool:
        """Schreibt einen Audit-Eintrag."""
        try:
            with self.write_lock:
                # Rotation prüfen
                if self.current_file.exists() and self.current_file.stat().st_size >= self.max_file_size:
                    self._rotate_file()
                
                # Entry schreiben
                with open(self.current_file, 'a', encoding='utf-8') as f:
                    json.dump(entry.to_dict(), f, ensure_ascii=False)
                    f.write('\n')
                
                # Index aktualisieren
                self._add_to_index(entry)
                
                return True
                
        except Exception as e:
            log_manager.log_event("MiniAudit", f"Fehler beim Schreiben: {e}", "ERROR")
            return False
    
    def _load_index(self) -> Dict[str, Any]:
        """Lädt den Suchindex."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "sessions": defaultdict(list),
            "dates": defaultdict(list),
            "types": defaultdict(list),
            "severity": defaultdict(list),
            "modules": defaultdict(list)
        }
    
    def _add_to_index(self, entry: AuditEntry):
        """Fügt Entry zum Index hinzu."""
        file_ref = f"{self.current_file.name}:{entry.audit_id}"
        
        # Nach Session
        if entry.session_id:
            self.index["sessions"][entry.session_id].append(file_ref)
        
        # Nach Datum
        date = entry.timestamp.split('T')[0]
        self.index["dates"][date].append(file_ref)
        
        # Nach Typ
        self.index["types"][entry.event_type.value].append(file_ref)
        
        # Nach Severity
        self.index["severity"][entry.severity.value].append(file_ref)
        
        # Nach Modul
        if entry.module:
            self.index["modules"][entry.module].append(file_ref)
    
    def _update_index(self):
        """Speichert den Index."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            log_manager.log_event("MiniAudit", f"Fehler beim Index-Update: {e}", "ERROR")


class AuditAnalyzer:
    """Analysiert und durchsucht Audit-Logs."""
    
    def __init__(self, storage: AuditStorage):
        self.storage = storage
    
    def search(self, criteria: Dict[str, Any], limit: int = 100) -> List[AuditEntry]:
        """
        Durchsucht Audit-Logs nach Kriterien.
        
        Criteria können sein:
        - session_id: str
        - date_from/date_to: datetime
        - event_type: AuditEventType
        - severity: AuditSeverity
        - module: str
        - has_violations: bool
        - min_confidence: float
        - tags: List[str]
        """
        results = []
        files_to_search = self._determine_files_to_search(criteria)
        
        for file_path in files_to_search:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if len(results) >= limit:
                            return results
                        
                        try:
                            entry_dict = json.loads(line.strip())
                            if self._matches_criteria(entry_dict, criteria):
                                # Rekonstruiere AuditEntry
                                entry = self._dict_to_entry(entry_dict)
                                results.append(entry)
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                log_manager.log_event("MiniAudit", f"Fehler beim Durchsuchen: {e}", "ERROR")
        
        return results
    
    def _determine_files_to_search(self, criteria: Dict[str, Any]) -> List[Path]:
        """Bestimmt welche Dateien durchsucht werden müssen."""
        # Nutze Index für Optimierung
        if "session_id" in criteria:
            refs = self.storage.index["sessions"].get(criteria["session_id"], [])
            files = set(self.storage.log_dir / ref.split(':')[0] for ref in refs)
            return list(files)
        
        # Sonst alle Dateien
        return sorted(self.storage.log_dir.glob("audit_*.jsonl"))
    
    def _matches_criteria(self, entry_dict: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Prüft ob Entry den Kriterien entspricht."""
        # Session ID
        if "session_id" in criteria:
            if entry_dict.get("session_id") != criteria["session_id"]:
                return False
        
        # Event Type
        if "event_type" in criteria:
            if entry_dict.get("event_type") != criteria["event_type"].value:
                return False
        
        # Severity
        if "severity" in criteria:
            if entry_dict.get("severity") != criteria["severity"].value:
                return False
        
        # Module
        if "module" in criteria:
            if entry_dict.get("module") != criteria["module"]:
                return False
        
        # Violations
        if criteria.get("has_violations"):
            if not entry_dict.get("violations"):
                return False
        
        # Confidence
        if "min_confidence" in criteria:
            if entry_dict.get("confidence", 0) < criteria["min_confidence"]:
                return False
        
        # Date range
        if "date_from" in criteria or "date_to" in criteria:
            try:
                entry_date = datetime.fromisoformat(entry_dict["timestamp"])
                if "date_from" in criteria and entry_date < criteria["date_from"]:
                    return False
                if "date_to" in criteria and entry_date > criteria["date_to"]:
                    return False
            except (KeyError, ValueError):
                return False
        
        # Tags
        if "tags" in criteria:
            entry_tags = set(entry_dict.get("tags", []))
            required_tags = set(criteria["tags"])
            if not required_tags.issubset(entry_tags):
                return False
        
        return True
    
    def _dict_to_entry(self, entry_dict: Dict[str, Any]) -> AuditEntry:
        """Konvertiert Dictionary zurück zu AuditEntry."""
        # Enums wiederherstellen
        if "event_type" in entry_dict:
            entry_dict["event_type"] = AuditEventType(entry_dict["event_type"])
        if "severity" in entry_dict:
            entry_dict["severity"] = AuditSeverity(entry_dict["severity"])
        
        return AuditEntry(**entry_dict)
    
    def get_statistics(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Erstellt Statistiken über Audit-Einträge."""
        stats = {
            "total_entries": 0,
            "by_type": defaultdict(int),
            "by_severity": defaultdict(int),
            "by_module": defaultdict(int),
            "violations_count": 0,
            "average_confidence": 0.0,
            "control_interventions": 0,
            "time_range": str(time_range) if time_range else "all"
        }
        
        # Zeitfilter
        if time_range:
            cutoff = datetime.now() - time_range
            criteria = {"date_from": cutoff}
        else:
            criteria = {}
        
        # Alle relevanten Einträge durchgehen
        entries = self.search(criteria, limit=10000)
        
        confidence_sum = 0.0
        confidence_count = 0
        
        for entry in entries:
            stats["total_entries"] += 1
            stats["by_type"][entry.event_type.value] += 1
            stats["by_severity"][entry.severity.value] += 1
            
            if entry.module:
                stats["by_module"][entry.module] += 1
            
            if entry.violations:
                stats["violations_count"] += len(entry.violations)
            
            if entry.confidence > 0:
                confidence_sum += entry.confidence
                confidence_count += 1
            
            if entry.event_type == AuditEventType.CONTROL_INTERVENTION:
                stats["control_interventions"] += 1
        
        if confidence_count > 0:
            stats["average_confidence"] = confidence_sum / confidence_count
        
        return dict(stats)


class AuditExporter:
    """Exportiert Audit-Daten in verschiedene Formate."""
    
    def __init__(self, analyzer: AuditAnalyzer):
        self.analyzer = analyzer
    
    def export_json(self, criteria: Dict[str, Any], output_path: str) -> bool:
        """Exportiert gefilterte Einträge als JSON."""
        try:
            entries = self.analyzer.search(criteria, limit=10000)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "criteria": criteria,
                "entry_count": len(entries),
                "entries": [entry.to_dict() for entry in entries]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            log_manager.log_event("MiniAudit", f"Export-Fehler: {e}", "ERROR")
            return False
    
    def export_csv(self, criteria: Dict[str, Any], output_path: str) -> bool:
        """Exportiert gefilterte Einträge als CSV."""
        try:
            entries = self.analyzer.search(criteria, limit=10000)
            
            if not entries:
                return False
            
            # CSV-Header bestimmen
            fieldnames = [
                "audit_id", "timestamp", "event_type", "severity",
                "session_id", "module", "user_input", "chosen_action",
                "confidence", "violations", "reasoning", "tags"
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in entries:
                    row = {
                        "audit_id": entry.audit_id,
                        "timestamp": entry.timestamp,
                        "event_type": entry.event_type.value,
                        "severity": entry.severity.value,
                        "session_id": entry.session_id,
                        "module": entry.module,
                        "user_input": entry.user_input[:100],  # Gekürzt
                        "chosen_action": entry.chosen_action,
                        "confidence": entry.confidence,
                        "violations": ", ".join(entry.violations),
                        "reasoning": entry.reasoning[:200],  # Gekürzt
                        "tags": ", ".join(entry.tags)
                    }
                    writer.writerow(row)
            
            return True
            
        except Exception as e:
            log_manager.log_event("MiniAudit", f"CSV-Export-Fehler: {e}", "ERROR")
            return False
    
    def generate_compliance_report(self, time_range: timedelta, 
                                 output_path: str) -> bool:
        """Generiert einen Compliance-Bericht."""
        try:
            stats = self.analyzer.get_statistics(time_range)
            
            # Kritische Events
            critical_events = self.analyzer.search({
                "severity": AuditSeverity.CRITICAL,
                "date_from": datetime.now() - time_range
            })
            
            # Violations
            violation_events = self.analyzer.search({
                "has_violations": True,
                "date_from": datetime.now() - time_range
            })
            
            report = {
                "report_type": "compliance",
                "generated": datetime.now().isoformat(),
                "time_range": str(time_range),
                "summary": stats,
                "critical_events": len(critical_events),
                "total_violations": stats["violations_count"],
                "requires_review": len([e for e in violation_events if e.requires_review]),
                "critical_details": [
                    {
                        "id": e.audit_id,
                        "time": e.timestamp,
                        "module": e.module,
                        "reasoning": e.reasoning
                    }
                    for e in critical_events[:10]  # Top 10
                ]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            log_manager.log_event("MiniAudit", f"Report-Fehler: {e}", "ERROR")
            return False


class MiniAudit:
    """
    Haupt-Audit-System für INTEGRA.
    Orchestriert Storage, Analyse und Export.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Session-Management
        self.session_id = config.get('session_id', str(uuid.uuid4())[:8])
        self.session_start = datetime.now()
        
        # Komponenten initialisieren
        self.storage = AuditStorage(
            log_dir=config.get('log_dir', 'logs'),
            max_file_size_mb=config.get('max_file_size_mb', 10.0),
            max_files=config.get('max_files', 100),
            rotation_callback=self._on_rotation
        )
        
        self.analyzer = AuditAnalyzer(self.storage)
        self.exporter = AuditExporter(self.analyzer)
        
        # Session-Statistiken
        self.session_stats = {
            "entries_logged": 0,
            "decisions": 0,
            "violations": 0,
            "interventions": 0,
            "errors": 0
        }
        
        # Buffer für Batch-Writes (optional)
        self.buffer = []
        self.buffer_size = config.get('buffer_size', 0)  # 0 = no buffering
        
        # Log Session-Start
        self._log_session_event("SESSION_START")
    
    def log_decision(self, decision_context: Dict[str, Any], 
                    profile: Dict[str, float], 
                    context: Dict[str, Any]) -> AuditEntry:
        """
        Hauptfunktion zum Loggen einer Entscheidung.
        
        Args:
            decision_context: Entscheidungsdetails
            profile: Aktuelles ethisches Profil
            context: Vollständiger Kontext
            
        Returns:
            Der erstellte AuditEntry
        """
        # Entry erstellen
        entry = self._create_decision_entry(decision_context, profile, context)
        
        # Hash berechnen
        entry.integrity_hash = entry.calculate_hash()
        
        # Speichern
        self._write_entry(entry)
        
        # Statistiken
        self.session_stats["entries_logged"] += 1
        self.session_stats["decisions"] += 1
        if entry.violations:
            self.session_stats["violations"] += len(entry.violations)
        
        return entry
    
    def log_event(self, event_type: AuditEventType, 
                 severity: AuditSeverity,
                 message: str,
                 module: str = "",
                 data: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """
        Loggt ein allgemeines Event.
        
        Args:
            event_type: Typ des Events
            severity: Schweregrad
            message: Beschreibung
            module: Auslösendes Modul
            data: Zusätzliche Daten
            
        Returns:
            Der erstellte AuditEntry
        """
        entry = AuditEntry(
            event_type=event_type,
            severity=severity,
            session_id=self.session_id,
            module=module,
            reasoning=message,
            module_data=data or {}
        )
        
        entry.integrity_hash = entry.calculate_hash()
        self._write_entry(entry)
        
        # Statistiken
        if event_type == AuditEventType.ERROR:
            self.session_stats["errors"] += 1
        elif event_type == AuditEventType.CONTROL_INTERVENTION:
            self.session_stats["interventions"] += 1
        
        return entry
    
    def _create_decision_entry(self, decision_context: Dict[str, Any],
                              profile: Dict[str, float],
                              context: Dict[str, Any]) -> AuditEntry:
        """Erstellt strukturierten Audit-Entry aus Entscheidungskontext."""
        entry = AuditEntry(
            event_type=AuditEventType.DECISION,
            session_id=self.session_id
        )
        
        # Basis-Informationen
        entry.user_input = context.get("user_input", "")[:500]  # Begrenzen
        entry.decision_path = context.get("path", "unknown")
        entry.module = context.get("module", "decision_engine")
        
        # Ethik-Scores
        if "ethics" in context:
            ethics = context["ethics"]
            entry.ethics_scores = ethics.get("scores", {})
            entry.violations = ethics.get("violations", [])
            entry.confidence = context.get("confidence", 0.0)
        
        # ETB-Ergebnis
        if "etb_result" in context:
            etb = context["etb_result"]
            entry.module_data["etb"] = {
                "chosen_option": etb.get("chosen_option"),
                "score": etb.get("score"),
                "matrix": etb.get("matrix", [])[:3]  # Top 3 Optionen
            }
            entry.chosen_action = etb.get("chosen_option", "")
        
        # PAE-Ergebnis
        if "pae_result" in context:
            pae = context["pae_result"]
            entry.module_data["pae"] = {
                "chosen_principle": pae.get("chosen_principle"),
                "method": pae.get("method"),
                "tie_count": len(pae.get("tie_groups", []))
            }
        
        # Profil-Snapshot
        entry.profile_snapshot = profile.copy()
        
        # Reasoning
        if "response" in context:
            entry.reasoning = context["response"][:500]
        
        # Processing Time
        if "processing_time" in context:
            entry.processing_time = context["processing_time"]
        
        # Severity bestimmen
        if entry.violations:
            if "integrity" in entry.violations or "governance" in entry.violations:
                entry.severity = AuditSeverity.HIGH
            else:
                entry.severity = AuditSeverity.MEDIUM
        elif entry.confidence < 0.5:
            entry.severity = AuditSeverity.LOW
        else:
            entry.severity = AuditSeverity.INFO
        
        # Compliance-Checks
        self._check_compliance(entry, context)
        
        # Tags
        if entry.violations:
            entry.tags.append("has_violations")
        if entry.decision_path == "deep":
            entry.tags.append("deep_path")
        if entry.confidence < 0.6:
            entry.tags.append("low_confidence")
        
        return entry
    
    def _check_compliance(self, entry: AuditEntry, context: Dict[str, Any]):
        """Prüft Compliance-Anforderungen."""
        # Beispiel-Checks
        if "personal_data" in str(entry.user_input).lower():
            entry.compliance_flags.append("gdpr_relevant")
            entry.requires_review = True
        
        if entry.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
            entry.requires_review = True
        
        if "medical" in context.get("domain", ""):
            entry.compliance_flags.append("hipaa_relevant")
        
        if "financial" in context.get("domain", ""):
            entry.compliance_flags.append("sox_relevant")
    
    def _write_entry(self, entry: AuditEntry):
        """Schreibt Entry (mit optionalem Buffering)."""
        if self.buffer_size > 0:
            self.buffer.append(entry)
            if len(self.buffer) >= self.buffer_size:
                self.flush()
        else:
            self.storage.write_entry(entry)
    
    def flush(self):
        """Schreibt Buffer-Inhalt."""
        for entry in self.buffer:
            self.storage.write_entry(entry)
        self.buffer.clear()
    
    def _log_session_event(self, event_name: str):
        """Loggt Session-bezogene Events."""
        self.log_event(
            AuditEventType.SYSTEM,
            AuditSeverity.INFO,
            f"Session {event_name}",
            module="mini_audit",
            data={"session_stats": self.session_stats.copy()}
        )
    
    def _on_rotation(self, old_file: Path):
        """Callback bei Datei-Rotation."""
        self.log_event(
            AuditEventType.SYSTEM,
            AuditSeverity.INFO,
            f"Log-Datei rotiert: {old_file.name}",
            module="mini_audit"
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Gibt Session-Zusammenfassung zurück."""
        duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "duration_seconds": duration,
            "stats": self.session_stats.copy(),
            "current_file": str(self.storage.current_file),
            "files_count": len(list(self.storage.log_dir.glob("audit_*.jsonl")))
        }
    
    def close(self):
        """Schließt Audit-System sauber."""
        # Buffer leeren
        if self.buffer:
            self.flush()
        
        # Session-Ende loggen
        self._log_session_event("SESSION_END")
        
        # Index speichern
        self.storage._update_index()


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Hauptschnittstelle gemäß INTEGRA-Standard.
    
    Args:
        input_text: Aktion (log, search, export, stats)
        context: Kontext mit action, criteria, data etc.
        
    Returns:
        Standardisiertes Ergebnis
    """
    context = context or {}
    
    try:
        # Konfiguration
        config = context.get("audit_config", {})
        
        # Audit-System initialisieren oder abrufen
        if "audit_instance" in context:
            audit = context["audit_instance"]
        else:
            audit = MiniAudit(config)
        
        # Action bestimmen
        action = context.get("action", "log")
        
        if action == "log":
            # Entscheidung loggen
            decision_context = context.get("decision", {})
            profile = context.get("profile", {})
            
            if not decision_context:
                # Fallback: Generisches Event
                entry = audit.log_event(
                    AuditEventType.SYSTEM,
                    AuditSeverity.INFO,
                    input_text or "Event logged",
                    module=context.get("module", "unknown")
                )
            else:
                entry = audit.log_decision(decision_context, profile, context)
            
            return {
                "success": True,
                "action": "logged",
                "audit_id": entry.audit_id,
                "timestamp": entry.timestamp,
                "severity": entry.severity.value,
                "session_id": audit.session_id,
                "module": "mini_audit",
                "version": "2.0"
            }
        
        elif action == "search":
            # Logs durchsuchen
            criteria = context.get("criteria", {})
            limit = context.get("limit", 100)
            
            # Criteria konvertieren
            if "event_type" in criteria and isinstance(criteria["event_type"], str):
                criteria["event_type"] = AuditEventType(criteria["event_type"])
            if "severity" in criteria and isinstance(criteria["severity"], str):
                criteria["severity"] = AuditSeverity(criteria["severity"])
            
            entries = audit.analyzer.search(criteria, limit)
            
            return {
                "success": True,
                "action": "search",
                "count": len(entries),
                "entries": [entry.to_dict() for entry in entries],
                "criteria": criteria,
                "module": "mini_audit",
                "version": "2.0"
            }
        
        elif action == "export":
            # Daten exportieren
            export_format = context.get("format", "json")
            output_path = context.get("output_path", f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}")
            criteria = context.get("criteria", {})
            
            if export_format == "csv":
                success = audit.exporter.export_csv(criteria, output_path)
            elif export_format == "compliance":
                time_range = timedelta(days=context.get("days", 30))
                success = audit.exporter.generate_compliance_report(time_range, output_path)
            else:
                success = audit.exporter.export_json(criteria, output_path)
            
            return {
                "success": success,
                "action": "export",
                "format": export_format,
                "output_path": output_path,
                "module": "mini_audit",
                "version": "2.0"
            }
        
        elif action == "stats":
            # Statistiken abrufen
            days = context.get("days", 0)
            time_range = timedelta(days=days) if days > 0 else None
            
            stats = audit.analyzer.get_statistics(time_range)
            summary = audit.get_session_summary()
            
            return {
                "success": True,
                "action": "stats",
                "statistics": stats,
                "session": summary,
                "module": "mini_audit",
                "version": "2.0"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unbekannte Action: {action}",
                "module": "mini_audit",
                "version": "2.0"
            }
        
    except Exception as e:
        log_manager.log_event("MiniAudit", f"Fehler in run_module: {e}", "ERROR")
        return {
            "success": False,
            "error": str(e),
            "module": "mini_audit",
            "version": "2.0",
            "timestamp": datetime.now().isoformat()
        }


def demo():
    """Demonstriert die erweiterte Mini-Audit Funktionalität."""
    print("=== INTEGRA Mini-Audit 2.0 Demo ===\n")
    
    # Audit-System initialisieren
    audit = MiniAudit({
        "session_id": "DEMO-001",
        "max_file_size_mb": 0.1  # Klein für Demo
    })
    
    # Demo 1: Verschiedene Entscheidungen loggen
    print("Demo 1: Entscheidungen protokollieren")
    print("-" * 50)
    
    # Normale Entscheidung
    context1 = {
        "user_input": "Soll ich helfen?",
        "path": "fast",
        "ethics": {
            "scores": {"integrity": 0.9, "nurturing": 0.8},
            "violations": [],
        },
        "confidence": 0.85,
        "response": "Ja, Hilfe ist angebracht.",
        "processing_time": 0.123
    }
    
    entry1 = audit.log_decision({}, profiles.get_default_profile(), context1)
    print(f"✅ Entscheidung geloggt: {entry1.audit_id}")
    print(f"   Severity: {entry1.severity.value}")
    
    # Entscheidung mit Verletzung
    context2 = {
        "user_input": "Soll ich private Daten teilen?",
        "path": "deep",
        "ethics": {
            "scores": {"integrity": 0.3, "governance": 0.2},
            "violations": ["integrity", "governance"],
        },
        "confidence": 0.4,
        "etb_result": {
            "chosen_option": "Daten nicht teilen",
            "score": 0.9
        }
    }
    
    entry2 = audit.log_decision({}, profiles.get_default_profile(), context2)
    print(f"⚠️  Verletzung geloggt: {entry2.audit_id}")
    print(f"   Violations: {entry2.violations}")
    print(f"   Requires Review: {entry2.requires_review}")
    
    # Control Intervention
    audit.log_event(
        AuditEventType.CONTROL_INTERVENTION,
        AuditSeverity.HIGH,
        "Nutzer-Override: Entscheidung blockiert",
        module="basic_control"
    )
    print("🛑 Control-Eingriff geloggt")
    
    # Learning Update
    audit.log_event(
        AuditEventType.LEARNING_UPDATE,
        AuditSeverity.INFO,
        "Profil angepasst basierend auf Feedback",
        module="mini_learner",
        data={"adjustments": {"nurturing": "+0.05"}}
    )
    print("📚 Lern-Update geloggt")
    print()
    
    # Demo 2: Suche
    print("Demo 2: Audit-Logs durchsuchen")
    print("-" * 50)
    
    # Nach Violations suchen
    violations_found = audit.analyzer.search({
        "has_violations": True
    })
    print(f"Einträge mit Verletzungen: {len(violations_found)}")
    
    # Nach Severity suchen
    high_severity = audit.analyzer.search({
        "severity": AuditSeverity.HIGH
    })
    print(f"High-Severity Events: {len(high_severity)}")
    
    # Nach Session suchen
    session_entries = audit.analyzer.search({
        "session_id": "DEMO-001"
    })
    print(f"Einträge dieser Session: {len(session_entries)}")
    print()
    
    # Demo 3: Statistiken
    print("Demo 3: Statistiken abrufen")
    print("-" * 50)
    
    stats = audit.analyzer.get_statistics()
    print("Gesamt-Statistiken:")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  By Type: {dict(stats['by_type'])}")
    print(f"  By Severity: {dict(stats['by_severity'])}")
    print(f"  Violations Count: {stats['violations_count']}")
    print(f"  Average Confidence: {stats['average_confidence']:.2f}")
    
    summary = audit.get_session_summary()
    print(f"\nSession-Zusammenfassung:")
    print(f"  Session ID: {summary['session_id']}")
    print(f"  Duration: {summary['duration_seconds']:.1f}s")
    print(f"  Decisions: {summary['stats']['decisions']}")
    print(f"  Violations: {summary['stats']['violations']}")
    print()
    
    # Demo 4: Export
    print("Demo 4: Daten exportieren")
    print("-" * 50)
    
    # JSON Export
    json_path = "audit_export_demo.json"
    success = audit.exporter.export_json({"session_id": "DEMO-001"}, json_path)
    print(f"JSON Export: {'✅' if success else '❌'} -> {json_path}")
    
    # CSV Export
    csv_path = "audit_export_demo.csv"
    success = audit.exporter.export_csv({}, csv_path)
    print(f"CSV Export: {'✅' if success else '❌'} -> {csv_path}")
    
    # Compliance Report
    report_path = "compliance_report_demo.json"
    success = audit.exporter.generate_compliance_report(timedelta(days=1), report_path)
    print(f"Compliance Report: {'✅' if success else '❌'} -> {report_path}")
    print()
    
    # Demo 5: run_module Interface
    print("Demo 5: Standardisierte run_module Schnittstelle")
    print("-" * 50)
    
    # Log via run_module
    result = run_module("Test-Event", {
        "action": "log",
        "decision": {"path": "fast"},
        "profile": profiles.get_default_profile()
    })
    print(f"Log Result: {result['success']} - ID: {result.get('audit_id', 'N/A')}")
    
    # Search via run_module
    result = run_module("", {
        "action": "search",
        "criteria": {"event_type": "decision"},
        "limit": 5
    })
    print(f"Search Result: Found {result.get('count', 0)} entries")
    
    # Stats via run_module
    result = run_module("", {
        "action": "stats",
        "days": 1
    })
    if result['success']:
        print(f"Stats: {result['statistics']['total_entries']} total entries")
    
    # Aufräumen
    audit.close()
    print("\n✅ Mini-Audit Demo abgeschlossen!")
    
    # Clean up demo files
    for f in [json_path, csv_path, report_path]:
        try:
            Path(f).unlink()
        except:
            pass


if __name__ == "__main__":
    demo()