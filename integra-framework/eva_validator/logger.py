# -*- coding: utf-8 -*-
"""
Modulname: logger.py
Beschreibung: Audit-Logging und Protokollierung für EVA Validator
Teil von: EVA Validator v1.0 - Universal Ethical Validation System
Autor: Dominik Knape
Lizenz: CC BY-NC-SA 4.0
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import json
import csv
import threading
import hashlib
from collections import defaultdict
import gzip
import shutil

# EVA imports
try:
    from . import schema
except ImportError:
    import schema

from schema import AuditLogEntry


class LogRotator:
    """Verwaltet Log-Rotation und Archivierung."""
    
    def __init__(self, log_dir: Path, max_size_mb: float = 100.0,
                 max_files: int = 50, compress: bool = True):
        self.log_dir = log_dir
        self.max_size = max_size_mb * 1024 * 1024  # in Bytes
        self.max_files = max_files
        self.compress = compress
        
    def should_rotate(self, current_file: Path) -> bool:
        """Prüft ob Rotation nötig ist."""
        if not current_file.exists():
            return False
        return current_file.stat().st_size >= self.max_size
    
    def rotate(self, current_file: Path) -> Path:
        """Führt Rotation durch und gibt neue Datei zurück."""
        if not current_file.exists():
            return current_file
        
        # Neue Dateinummer
        base_name = current_file.stem.split('_')[0]
        existing_files = list(self.log_dir.glob(f"{base_name}_*.jsonl*"))
        
        # Höchste Nummer finden
        max_num = 0
        for f in existing_files:
            try:
                num = int(f.stem.split('_')[-1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                continue
        
        # Aktuelle Datei umbenennen
        new_name = f"{base_name}_{max_num + 1:04d}.jsonl"
        rotated_file = self.log_dir / new_name
        current_file.rename(rotated_file)
        
        # Komprimieren wenn gewünscht
        if self.compress:
            self._compress_file(rotated_file)
        
        # Alte Dateien löschen
        self._cleanup_old_files(base_name)
        
        # Neue Datei zurückgeben
        return current_file
    
    def _compress_file(self, file_path: Path):
        """Komprimiert eine Log-Datei."""
        compressed_path = file_path.with_suffix('.jsonl.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Original löschen
        file_path.unlink()
    
    def _cleanup_old_files(self, base_name: str):
        """Löscht alte Dateien wenn Limit überschritten."""
        files = sorted(self.log_dir.glob(f"{base_name}_*.jsonl*"))
        
        if len(files) > self.max_files:
            for f in files[:len(files) - self.max_files]:
                f.unlink()


class LogIndex:
    """Verwaltet Index für schnelle Log-Suche."""
    
    def __init__(self, index_file: Path):
        self.index_file = index_file
        self.index = self._load_index()
        self.dirty = False
        
    def _load_index(self) -> Dict[str, Any]:
        """Lädt bestehenden Index."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "by_decision_id": defaultdict(list),
            "by_date": defaultdict(list),
            "by_severity": defaultdict(list),
            "by_status": defaultdict(list),
            "by_source": defaultdict(list),
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_entries": 0
            }
        }
    
    def add_entry(self, entry: AuditLogEntry, file_ref: str):
        """Fügt Eintrag zum Index hinzu."""
        # Nach Decision ID
        self.index["by_decision_id"][entry.decision_id].append(file_ref)
        
        # Nach Datum
        date = entry.timestamp.split('T')[0]
        self.index["by_date"][date].append(file_ref)
        
        # Nach Severity
        self.index["by_severity"][entry.severity.value].append(file_ref)
        
        # Nach Status
        self.index["by_status"][entry.validation_status.value].append(file_ref)
        
        # Nach Source System
        self.index["by_source"][entry.source_system].append(file_ref)
        
        # Metadaten
        self.index["metadata"]["last_updated"] = datetime.now().isoformat()
        self.index["metadata"]["total_entries"] += 1
        
        self.dirty = True
    
    def save(self):
        """Speichert Index wenn nötig."""
        if not self.dirty:
            return
        
        try:
            # Konvertiere defaultdict zu normalen dicts für JSON
            save_data = {
                "by_decision_id": dict(self.index["by_decision_id"]),
                "by_date": dict(self.index["by_date"]),
                "by_severity": dict(self.index["by_severity"]),
                "by_status": dict(self.index["by_status"]),
                "by_source": dict(self.index["by_source"]),
                "metadata": self.index["metadata"]
            }
            
            with open(self.index_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            self.dirty = False
            
        except Exception as e:
            print(f"Fehler beim Speichern des Index: {e}")
    
    def search(self, criteria: Dict[str, Any]) -> List[str]:
        """Sucht nach Kriterien und gibt Datei-Referenzen zurück."""
        results = set()
        
        if "decision_id" in criteria:
            refs = self.index["by_decision_id"].get(criteria["decision_id"], [])
            if results:
                results &= set(refs)
            else:
                results = set(refs)
        
        if "date" in criteria:
            refs = self.index["by_date"].get(criteria["date"], [])
            if results:
                results &= set(refs)
            else:
                results = set(refs)
        
        if "severity" in criteria:
            refs = self.index["by_severity"].get(criteria["severity"], [])
            if results:
                results &= set(refs)
            else:
                results = set(refs)
        
        return list(results)


class EVALogger:
    """
    Hauptklasse für EVA Audit-Logging.
    Thread-safe, mit Rotation und Indexierung.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Konfiguration
        self.enabled = self.config.get("enabled", True)
        self.log_dir = Path(self.config.get("log_dir", "eva_logs"))
        self.log_dir.mkdir(exist_ok=True)
        
        # Log-Dateien
        self.audit_file = self.log_dir / "eva_audit.jsonl"
        self.event_file = self.log_dir / "eva_events.jsonl"
        
        # Rotation
        self.rotator = LogRotator(
            self.log_dir,
            max_size_mb=self.config.get("max_file_size_mb", 100.0),
            max_files=self.config.get("max_files", 50),
            compress=self.config.get("compress_logs", True)
        )
        
        # Index
        self.index = LogIndex(self.log_dir / "eva_index.json")
        
        # Thread-Safety
        self.write_lock = threading.Lock()
        
        # Buffer für Performance
        self.buffer = []
        self.buffer_size = self.config.get("buffer_size", 10)
        self.last_flush = datetime.now()
        
        # Statistiken
        self.stats = {
            "total_audits": 0,
            "total_events": 0,
            "by_severity": defaultdict(int),
            "by_status": defaultdict(int)
        }
    
    def log_audit(self, entry: AuditLogEntry) -> bool:
        """
        Loggt einen Audit-Eintrag.
        
        Args:
            entry: Strukturierter Audit-Eintrag
            
        Returns:
            True bei Erfolg
        """
        if not self.enabled:
            return True
        
        try:
            with self.write_lock:
                # Checksumme berechnen
                entry.checksum = self._calculate_checksum(entry)
                
                # In Buffer
                self.buffer.append(("audit", entry))
                
                # Index aktualisieren
                file_ref = f"{self.audit_file.name}:{entry.log_id}"
                self.index.add_entry(entry, file_ref)
                
                # Statistiken
                self.stats["total_audits"] += 1
                self.stats["by_severity"][entry.severity.value] += 1
                self.stats["by_status"][entry.validation_status.value] += 1
                
                # Flush wenn nötig
                if len(self.buffer) >= self.buffer_size:
                    self._flush()
                
                return True
                
        except Exception as e:
            print(f"Fehler beim Audit-Logging: {e}")
            return False
    
    def log_event(self, event_type: str, severity: str, 
                  details: Dict[str, Any]) -> bool:
        """
        Loggt ein allgemeines Event.
        
        Args:
            event_type: Typ des Events
            severity: Schweregrad (info, warning, error)
            details: Event-Details
            
        Returns:
            True bei Erfolg
        """
        if not self.enabled:
            return True
        
        try:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "severity": severity,
                "details": details
            }
            
            with self.write_lock:
                self.buffer.append(("event", event))
                self.stats["total_events"] += 1
                
                if len(self.buffer) >= self.buffer_size:
                    self._flush()
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Event-Logging: {e}")
            return False
    
    def _flush(self):
        """Schreibt Buffer auf Disk."""
        if not self.buffer:
            return
        
        # Nach Typ gruppieren
        audits = []
        events = []
        
        for log_type, data in self.buffer:
            if log_type == "audit":
                audits.append(data)
            else:
                events.append(data)
        
        # Audit-Einträge schreiben
        if audits:
            # Rotation prüfen
            if self.rotator.should_rotate(self.audit_file):
                self.audit_file = self.rotator.rotate(self.audit_file)
            
            with open(self.audit_file, 'a') as f:
                for entry in audits:
                    f.write(entry.to_json_line() + '\n')
        
        # Events schreiben
        if events:
            # Rotation prüfen
            if self.rotator.should_rotate(self.event_file):
                self.event_file = self.rotator.rotate(self.event_file)
            
            with open(self.event_file, 'a') as f:
                for event in events:
                    f.write(json.dumps(event, ensure_ascii=False) + '\n')
        
        # Buffer leeren
        self.buffer.clear()
        self.last_flush = datetime.now()
        
        # Index speichern
        self.index.save()
    
    def _calculate_checksum(self, entry: AuditLogEntry) -> str:
        """Berechnet Checksumme für Integrität."""
        # Wichtige Felder für Checksum
        checksum_data = {
            "log_id": entry.log_id,
            "decision_id": entry.decision_id,
            "timestamp": entry.timestamp,
            "validation_status": entry.validation_status.value,
            "score": entry.score,
            "recommendation": entry.recommendation
        }
        
        checksum_string = json.dumps(checksum_data, sort_keys=True)
        return hashlib.sha256(checksum_string.encode()).hexdigest()[:16]
    
    def search_audits(self, criteria: Dict[str, Any], 
                     limit: int = 100) -> List[AuditLogEntry]:
        """
        Durchsucht Audit-Logs.
        
        Args:
            criteria: Suchkriterien
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von Audit-Einträgen
        """
        # Flush vor Suche
        with self.write_lock:
            self._flush()
        
        # Index nutzen für Datei-Referenzen
        file_refs = self.index.search(criteria)
        
        results = []
        files_to_search = set()
        
        # Dateien aus Referenzen extrahieren
        for ref in file_refs:
            file_name = ref.split(':')[0]
            files_to_search.add(self.log_dir / file_name)
        
        # Falls keine Index-Treffer, alle Audit-Dateien
        if not files_to_search:
            files_to_search = set(self.log_dir.glob("eva_audit*.jsonl*"))
        
        # Dateien durchsuchen
        for file_path in files_to_search:
            if len(results) >= limit:
                break
            
            try:
                if file_path.suffix == '.gz':
                    opener = gzip.open
                else:
                    opener = open
                
                with opener(file_path, 'rt') as f:
                    for line in f:
                        if len(results) >= limit:
                            break
                        
                        try:
                            data = json.loads(line.strip())
                            
                            # Kriterien prüfen
                            if self._matches_criteria(data, criteria):
                                # Zurück zu AuditLogEntry konvertieren
                                # (vereinfacht hier)
                                results.append(data)
                                
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                print(f"Fehler beim Durchsuchen von {file_path}: {e}")
        
        return results
    
    def _matches_criteria(self, entry_data: Dict[str, Any], 
                         criteria: Dict[str, Any]) -> bool:
        """Prüft ob Eintrag den Kriterien entspricht."""
        if "decision_id" in criteria:
            if entry_data.get("decision_id") != criteria["decision_id"]:
                return False
        
        if "severity" in criteria:
            if entry_data.get("severity") != criteria["severity"]:
                return False
        
        if "status" in criteria:
            if entry_data.get("validation_status") != criteria["status"]:
                return False
        
        if "date_from" in criteria:
            entry_date = datetime.fromisoformat(entry_data["timestamp"])
            if entry_date < criteria["date_from"]:
                return False
        
        if "date_to" in criteria:
            entry_date = datetime.fromisoformat(entry_data["timestamp"])
            if entry_date > criteria["date_to"]:
                return False
        
        return True
    
    def export_logs(self, output_file: str, format: str = "json",
                   criteria: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exportiert Logs in verschiedene Formate.
        
        Args:
            output_file: Ausgabedatei
            format: Export-Format (json, csv, markdown)
            criteria: Filter-Kriterien
            
        Returns:
            True bei Erfolg
        """
        try:
            # Logs suchen
            if criteria:
                entries = self.search_audits(criteria, limit=10000)
            else:
                entries = self.search_audits({}, limit=10000)
            
            if format == "json":
                with open(output_file, 'w') as f:
                    json.dump({
                        "export_date": datetime.now().isoformat(),
                        "criteria": criteria,
                        "count": len(entries),
                        "entries": entries
                    }, f, indent=2)
            
            elif format == "csv":
                with open(output_file, 'w', newline='') as f:
                    if not entries:
                        return True
                    
                    # Header aus erstem Eintrag
                    fieldnames = entries[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(entries)
            
            elif format == "markdown":
                with open(output_file, 'w') as f:
                    f.write("# EVA Validator Audit Log Export\n\n")
                    f.write(f"Export Date: {datetime.now().isoformat()}\n\n")
                    f.write(f"Total Entries: {len(entries)}\n\n")
                    
                    # Zusammenfassung
                    f.write("## Summary\n\n")
                    severity_counts = defaultdict(int)
                    status_counts = defaultdict(int)
                    
                    for entry in entries:
                        severity_counts[entry.get("severity", "unknown")] += 1
                        status_counts[entry.get("validation_status", "unknown")] += 1
                    
                    f.write("### By Severity\n")
                    for sev, count in severity_counts.items():
                        f.write(f"- {sev}: {count}\n")
                    
                    f.write("\n### By Status\n")
                    for status, count in status_counts.items():
                        f.write(f"- {status}: {count}\n")
                    
                    # Top 10 Einträge
                    f.write("\n## Recent Entries (Top 10)\n\n")
                    for entry in entries[:10]:
                        f.write(f"### {entry.get('log_id', 'N/A')}\n")
                        f.write(f"- **Decision ID**: {entry.get('decision_id', 'N/A')}\n")
                        f.write(f"- **Timestamp**: {entry.get('timestamp', 'N/A')}\n")
                        f.write(f"- **Status**: {entry.get('validation_status', 'N/A')}\n")
                        f.write(f"- **Score**: {entry.get('score', 'N/A')}\n")
                        f.write(f"- **Recommendation**: {entry.get('recommendation', 'N/A')}\n\n")
            
            return True
            
        except Exception as e:
            print(f"Export-Fehler: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Logger-Statistiken zurück."""
        with self.write_lock:
            # Aktuelle Buffer-Größe einbeziehen
            buffered_audits = sum(1 for t, _ in self.buffer if t == "audit")
            buffered_events = sum(1 for t, _ in self.buffer if t == "event")
            
            return {
                "enabled": self.enabled,
                "total_audits": self.stats["total_audits"] + buffered_audits,
                "total_events": self.stats["total_events"] + buffered_events,
                "by_severity": dict(self.stats["by_severity"]),
                "by_status": dict(self.stats["by_status"]),
                "buffer_size": len(self.buffer),
                "last_flush": self.last_flush.isoformat(),
                "log_files": len(list(self.log_dir.glob("eva_*.jsonl*"))),
                "index_entries": self.index.index["metadata"]["total_entries"]
            }
    
    def close(self):
        """Schließt Logger und flusht alle Daten."""
        with self.write_lock:
            self._flush()
            self.index.save()


def demo():
    """Demonstriert die Logger-Funktionalität."""
    print("=== EVA Logger Demo ===\n")
    
    # Logger erstellen
    logger = EVALogger({
        "enabled": True,
        "log_dir": "demo_logs",
        "buffer_size": 3,
        "max_file_size_mb": 0.1  # Klein für Demo
    })
    
    # Test 1: Audit-Einträge
    print("1. Audit-Einträge loggen")
    print("-" * 50)
    
    from schema import ValidationStatus, SeverityLevel, ScenarioType, UserRiskLevel
    
    for i in range(5):
        entry = AuditLogEntry(
            log_id=f"DEMO-{i:03d}",
            timestamp=datetime.now().isoformat(),
            decision_id=f"decision-{i:03d}",
            validation_status=ValidationStatus.APPROVED if i % 2 == 0 else ValidationStatus.REJECTED,
            severity=SeverityLevel.INFO if i < 3 else SeverityLevel.WARNING,
            escalated=i == 4,
            input_summary=f"Test-Eingabe {i}",
            output_summary=f"Test-Ausgabe {i}",
            score=0.9 - (i * 0.1),
            confidence=0.8,
            source_system="DemoBot",
            user_risk=UserRiskLevel.LOW,
            scenario_type=ScenarioType.GENERAL,
            recommendation=f"Empfehlung {i}",
            reasons=[f"Grund {i}.1", f"Grund {i}.2"],
            improvements=[f"Verbesserung {i}"],
            processing_time=0.1 + (i * 0.01),
            validator_version="1.0"
        )
        
        success = logger.log_audit(entry)
        print(f"  Audit {i}: {'✓' if success else '✗'}")
    
    # Test 2: Events
    print("\n2. Events loggen")
    print("-" * 50)
    
    events = [
        ("session_start", "info", {"session_id": "demo-123"}),
        ("validation_error", "error", {"error": "Test-Fehler"}),
        ("escalation_triggered", "warning", {"trigger": "low_score"}),
    ]
    
    for event_type, severity, details in events:
        success = logger.log_event(event_type, severity, details)
        print(f"  Event '{event_type}': {'✓' if success else '✗'}")
    
    # Test 3: Suche
    print("\n3. Audit-Logs durchsuchen")
    print("-" * 50)
    
    # Nach Decision ID
    results = logger.search_audits({"decision_id": "decision-001"})
    print(f"  Suche nach decision-001: {len(results)} Treffer")
    
    # Nach Severity
    results = logger.search_audits({"severity": "warning"})
    print(f"  Suche nach warnings: {len(results)} Treffer")
    
    # Test 4: Export
    print("\n4. Logs exportieren")
    print("-" * 50)
    
    # JSON Export
    success = logger.export_logs("demo_export.json", format="json")
    print(f"  JSON Export: {'✓' if success else '✗'}")
    
    # CSV Export
    success = logger.export_logs("demo_export.csv", format="csv")
    print(f"  CSV Export: {'✓' if success else '✗'}")
    
    # Markdown Export
    success = logger.export_logs("demo_export.md", format="markdown")
    print(f"  Markdown Export: {'✓' if success else '✗'}")
    
    # Test 5: Statistiken
    print("\n5. Logger-Statistiken")
    print("-" * 50)
    stats = logger.get_statistics()
    print(f"  Total Audits: {stats['total_audits']}")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  By Severity: {stats['by_severity']}")
    print(f"  By Status: {stats['by_status']}")
    print(f"  Buffer Size: {stats['buffer_size']}")
    print(f"  Log Files: {stats['log_files']}")
    
    # Aufräumen
    logger.close()
    
    # Demo-Dateien löschen
    import shutil
    try:
        shutil.rmtree("demo_logs")
        for f in ["demo_export.json", "demo_export.csv", "demo_export.md"]:
            Path(f).unlink(missing_ok=True)
    except:
        pass
    
    print("\n✅ Logger Demo abgeschlossen!")


if __name__ == "__main__":
    demo()