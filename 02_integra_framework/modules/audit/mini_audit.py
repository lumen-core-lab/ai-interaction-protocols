# # -*- coding: utf-8 -*-

"""
modules/audit/mini_audit.py

📋 MINI AUDIT - Comprehensive Decision Tracking für INTEGRA Light 📋

Implementiert vollständige Entscheidungs-Protokollierung:

- Strukturierte Audit-Logs für jede Entscheidung
- Performance-Metriken und Timing-Daten
- Ethische Compliance-Tracking
- Export-fähige Protokolle für Regulierung
- Datenschutz-konforme Speicherung
- Automatische Log-Rotation und -Archivierung

Design-Philosophie: Vollständige Transparenz ohne Performance-Impact

Version: INTEGRA Light 1.0
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
import hashlib
import uuid

# ==============================================================================

# 1. Audit-Datenstrukturen

# ==============================================================================

@dataclass
class AuditEntry:
"""📝 Einzelner Audit-Eintrag für eine INTEGRA-Entscheidung"""

```
# Basis-Identifikation
entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
session_id: str = "default"

# Entscheidungs-Details
decision_type: str = "unknown"          # fast_path, deep_path, blocked, etc.
input_hash: str = ""                    # Hash der Eingabe (Datenschutz)
response_summary: str = ""              # Kurze Antwort-Zusammenfassung

# Ethische Bewertung
align_score: Optional[float] = None
align_violations: List[str] = field(default_factory=list)
ethics_confidence: Optional[float] = None
risk_level: Optional[float] = None

# Profil und Konfiguration
profile_name: str = "unknown"
profile_version: str = "1.0"
sensitivity_level: str = "normal"

# Performance-Metriken
response_time_ms: Optional[float] = None
modules_used: List[str] = field(default_factory=list)
processing_path: str = ""               # Welche Module wurden durchlaufen

# Lern-Informationen
feedback_received: Optional[str] = None  # positive, negative, neutral
learning_triggered: bool = False
profile_modified: bool = False

# Compliance und Governance
compliance_status: str = "compliant"     # compliant, warning, violation
warnings: List[str] = field(default_factory=list)
escalation_required: bool = False

# Kontext-Informationen (anonymisiert)
user_context: Dict[str, Any] = field(default_factory=dict)
domain: str = "general"

def to_dict(self) -> Dict[str, Any]:
    """Konvertiert zu Dictionary für JSON-Export"""
    return asdict(self)

def to_json(self, indent: int = 2) -> str:
    """Serialisiert als JSON-String"""
    return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

def get_privacy_safe_summary(self) -> Dict[str, Any]:
    """Gibt datenschutz-konforme Zusammenfassung zurück"""
    return {
        'entry_id': self.entry_id,
        'timestamp': self.timestamp,
        'decision_type': self.decision_type,
        'align_score': self.align_score,
        'violations_count': len(self.align_violations),
        'response_time_ms': self.response_time_ms,
        'compliance_status': self.compliance_status,
        'domain': self.domain
    }
```

@dataclass
class AuditConfig:
"""⚙️ Konfiguration für das Audit-System"""

```
# Speicher-Einstellungen
enable_file_logging: bool = True
log_directory: str = "integra_audit_logs"
max_log_file_size_mb: int = 10
max_log_files: int = 100

# Datenschutz-Einstellungen
hash_user_input: bool = True             # Input hashen statt speichern
anonymize_user_data: bool = True         # Nutzerdaten anonymisieren
retention_days: int = 90                 # Log-Aufbewahrung in Tagen

# Performance-Einstellungen
async_logging: bool = False              # Async-Logging (für Prod)
batch_size: int = 100                    # Batch-Größe für DB-Writes
enable_performance_tracking: bool = True

# Compliance-Einstellungen
compliance_mode: str = "basic"           # basic, gdpr, hipaa, finance
export_format: str = "json"              # json, csv, xml
audit_level: str = "standard"            # minimal, standard, detailed
```

# ==============================================================================

# 2. Haupt-Audit-Klasse

# ==============================================================================

class INTEGRAMiniAudit:
"""
📋 Comprehensive Audit-System für INTEGRA Light

```
Features:
- Vollständige Entscheidungs-Protokollierung
- Datenschutz-konforme Speicherung
- Performance-Tracking
- Compliance-Monitoring
- Export-Funktionen für Audits
"""

def __init__(self, config: Optional[AuditConfig] = None):
    self.config = config or AuditConfig()
    self.session_id = str(uuid.uuid4())[:12]
    self.audit_entries: List[AuditEntry] = []
   
    # Log-Verzeichnis erstellen falls nötig
    if self.config.enable_file_logging:
        os.makedirs(self.config.log_directory, exist_ok=True)
   
    print(f"📋 INTEGRA Mini-Audit initialisiert")
    print(f"🆔 Session: {self.session_id}")
    print(f"📁 Logging: {'Aktiviert' if self.config.enable_file_logging else 'Deaktiviert'}")

def create_audit_entry(
    self,
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> AuditEntry:
    """
    📝 Erstellt detailliertes Audit-Log aus Entscheidungs-Kontext
   
    Args:
        input_data: Original-Eingabedaten
        profile: Verwendetes ethisches Profil
        context: Vollständiger Entscheidungskontext
       
    Returns:
        AuditEntry: Strukturiertes Audit-Log
    """
   
    # Basis-Informationen extrahieren
    entry = AuditEntry(session_id=self.session_id)
   
    # Input-Hash für Datenschutz (falls aktiviert)
    if self.config.hash_user_input:
        input_text = str(input_data.get('text', ''))
        entry.input_hash = hashlib.sha256(input_text.encode()).hexdigest()[:16]
   
    # Entscheidungs-Details
    decision = context.get('decision', {})
    entry.decision_type = decision.get('path_taken', 'unknown')
    entry.response_summary = self._create_safe_summary(decision.get('response', ''))
   
    # Ethische Bewertung
    entry.align_score = context.get('align_score')
    entry.align_violations = context.get('align_violations', [])
    entry.ethics_confidence = context.get('ethics_confidence')
    entry.risk_level = context.get('risk_level')
   
    # Profil-Informationen
    entry.profile_name = profile.get('name', 'unknown')
    entry.profile_version = profile.get('version', '1.0')
    entry.sensitivity_level = profile.get('sensitivity_level', 'normal')
    entry.domain = profile.get('domain', 'general')
   
    # Performance-Metriken
    entry.response_time_ms = context.get('response_time_ms')
    entry.modules_used = self._extract_modules_used(context)
    entry.processing_path = self._create_processing_path(context)
   
    # Lern-Informationen
    learning_result = context.get('learning_result', {})
    entry.feedback_received = learning_result.get('feedback_type')
    entry.learning_triggered = learning_result.get('action') == 'weight_adjustment'
    entry.profile_modified = context.get('profile_updated', False)
   
    # Compliance-Status ermitteln
    entry.compliance_status, entry.warnings = self._assess_compliance(context)
    entry.escalation_required = self._requires_escalation(context)
   
    # Anonymisierte Kontext-Daten
    if not self.config.anonymize_user_data:
        entry.user_context = self._extract_safe_context(context)
   
    return entry

def log_decision(
    self,
    input_data: Dict[str, Any],
    profile: Dict[str, Any],
    context: Dict[str, Any]
) -> str:
    """
    📋 Protokolliert eine Entscheidung vollständig
   
    Returns:
        str: Entry-ID für Referenz
    """
    entry = self.create_audit_entry(input_data, profile, context)
    self.audit_entries.append(entry)
   
    # File-Logging falls aktiviert
    if self.config.enable_file_logging:
        self._write_to_file(entry)
   
    # Console-Output für Debug
    self._print_audit_summary(entry)
   
    return entry.entry_id

def _create_safe_summary(self, response: str, max_length: int = 100) -> str:
    """Erstellt datenschutz-konforme Antwort-Zusammenfassung"""
    if not response:
        return ""
   
    # Kürze und anonymisiere
    summary = response[:max_length]
    if len(response) > max_length:
        summary += "..."
   
    # Entferne potentiell persönliche Daten
    # (Einfache Heuristiken für Demo - in Prod würde man NLP verwenden)
    sensitive_patterns = ['email', '@', 'telefon', 'adresse', 'name:', 'ich bin']
    for pattern in sensitive_patterns:
        if pattern in summary.lower():
            summary = "[REDACTED - POTENTIALLY SENSITIVE]"
            break
   
    return summary

def _extract_modules_used(self, context: Dict[str, Any]) -> List[str]:
    """Extrahiert Liste der verwendeten Module"""
    modules = []
   
    # Standard INTEGRA Module checken
    if 'align_score' in context:
        modules.append('align_principles')
    if 'ethics_assessment' in context:
        modules.append('basic_ethics')
    if 'decision' in context:
        modules.append('decision_engine')
    if 'learning_result' in context:
        modules.append('mini_learner')
   
    # Module aus Decision-Details
    decision_modules = context.get('decision', {}).get('modules_used', [])
    modules.extend(decision_modules)
   
    return list(set(modules))  # Duplikate entfernen

def _create_processing_path(self, context: Dict[str, Any]) -> str:
    """Erstellt String-Darstellung des Verarbeitungspfads"""
    path_components = []
   
    # Basis-Pfad
    decision_type = context.get('decision', {}).get('path_taken', 'unknown')
    path_components.append(decision_type)
   
    # Ethik-Module
    if context.get('align_violations'):
        path_components.append('ethics_violation_detected')
   
    # Lern-Module
    if context.get('learning_result'):
        path_components.append('learning_applied')
   
    return ' → '.join(path_components)

def _assess_compliance(self, context: Dict[str, Any]) -> tuple[str, List[str]]:
    """Bewertet Compliance-Status der Entscheidung"""
    warnings = []
    status = "compliant"
   
    # Ethische Compliance prüfen
    align_violations = context.get('align_violations', [])
    if align_violations:
        warnings.append(f"ALIGN-Verletzungen: {', '.join(align_violations)}")
        if 'integrity' in [v.lower() for v in align_violations]:
            status = "violation"  # Integrity-Verletzungen sind kritisch
        else:
            status = "warning"
   
    # Risiko-Level prüfen
    risk_level = context.get('risk_level', 0.0)
    if risk_level > 0.8:
        warnings.append(f"Hohes Risiko-Level: {risk_level:.2f}")
        status = "violation" if status != "violation" else status
    elif risk_level > 0.6:
        warnings.append(f"Erhöhtes Risiko-Level: {risk_level:.2f}")
        status = "warning" if status == "compliant" else status
   
    # Response-Time Compliance (für Performance-SLAs)
    response_time = context.get('response_time_ms', 0)
    if response_time > 1000:  # > 1 Sekunde
        warnings.append(f"Langsame Antwortzeit: {response_time:.1f}ms")
   
    return status, warnings

def _requires_escalation(self, context: Dict[str, Any]) -> bool:
    """Bestimmt ob Eskalation erforderlich ist"""
    # Kritische Violations
    align_violations = context.get('align_violations', [])
    critical_violations = ['integrity', 'nurturing']
    if any(v.lower() in critical_violations for v in align_violations):
        return True
   
    # Sehr hohes Risiko
    risk_level = context.get('risk_level', 0.0)
    if risk_level > 0.9:
        return True
   
    # Wiederholte Probleme (würde man aus Historie prüfen)
    # TODO: Implementierung für Wiederholungs-Erkennung
   
    return False

def _extract_safe_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Extrahiert sichere Kontext-Informationen ohne PII"""
    safe_context = {}
   
    # Performance-Daten
    if 'response_time_ms' in context:
        safe_context['performance'] = {
            'response_time_ms': context['response_time_ms']
        }
   
    # Entscheidungs-Metadaten
    decision = context.get('decision', {})
    if decision:
        safe_context['decision_meta'] = {
            'confidence': decision.get('confidence'),
            'reasoning_length': len(str(decision.get('reasoning', ''))),
            'has_explanation': bool(decision.get('explanation'))
        }
   
    return safe_context

def _write_to_file(self, entry: AuditEntry):
    """Schreibt Audit-Entry in Log-Datei"""
    try:
        # Dateiname mit Datum für einfache Rotation
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"integra_audit_{date_str}.jsonl"
        filepath = os.path.join(self.config.log_directory, filename)
       
        # Als JSON-Lines schreiben (eine Zeile pro Entry)
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(entry.to_json(indent=None) + '\n')
           
    except Exception as e:
        print(f"⚠️ Fehler beim Schreiben der Audit-Datei: {e}")

def _print_audit_summary(self, entry: AuditEntry):
    """Gibt Audit-Zusammenfassung auf Konsole aus"""
    print("📋 AUDIT LOG ENTRY")
    print(f"   ID: {entry.entry_id}")
    print(f"   Entscheidung: {entry.decision_type}")
    print(f"   ALIGN-Score: {entry.align_score:.2f}" if entry.align_score else "   ALIGN-Score: N/A")
    if entry.align_violations:
        print(f"   ⚠️ Verletzungen: {', '.join(entry.align_violations)}")
    print(f"   Compliance: {entry.compliance_status}")
    if entry.warnings:
        print(f"   Warnungen: {len(entry.warnings)}")
    print(f"   Zeit: {entry.response_time_ms:.1f}ms" if entry.response_time_ms else "")
    print("   " + "-" * 30)

def get_audit_statistics(self) -> Dict[str, Any]:
    """📊 Gibt umfassende Audit-Statistiken zurück"""
    if not self.audit_entries:
        return {'total_entries': 0, 'message': 'Keine Audit-Einträge vorhanden'}
   
    total_entries = len(self.audit_entries)
   
    # Entscheidungs-Typen
    decision_types = {}
    compliance_status = {}
    violations_count = {}
   
    # Performance-Statistiken
    response_times = [e.response_time_ms for e in self.audit_entries if e.response_time_ms]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
   
    for entry in self.audit_entries:
        # Decision Types
        dt = entry.decision_type
        decision_types[dt] = decision_types.get(dt, 0) + 1
       
        # Compliance Status
        cs = entry.compliance_status
        compliance_status[cs] = compliance_status.get(cs, 0) + 1
       
        # Violations
        for violation in entry.align_violations:
            violations_count[violation] = violations_count.get(violation, 0) + 1
   
    # Compliance-Rate berechnen
    compliant_count = compliance_status.get('compliant', 0)
    compliance_rate = (compliant_count / total_entries) * 100
   
    return {
        'total_entries': total_entries,
        'session_id': self.session_id,
        'compliance_rate': round(compliance_rate, 1),
        'decision_types': decision_types,
        'compliance_status': compliance_status,
        'violations_summary': violations_count,
        'performance': {
            'avg_response_time_ms': round(avg_response_time, 2),
            'total_decisions_logged': total_entries
        },
        'escalations_required': sum(1 for e in self.audit_entries if e.escalation_required),
        'learning_events': sum(1 for e in self.audit_entries if e.learning_triggered)
    }

def export_audit_logs(
    self,
    format: str = 'json',
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    privacy_safe: bool = True
) -> str:
    """
    📤 Exportiert Audit-Logs in verschiedenen Formaten
   
    Args:
        format: 'json', 'csv', oder 'summary'
        start_date: Startdatum für Filter
        end_date: Enddatum für Filter
        privacy_safe: Nur datenschutz-konforme Daten exportieren
       
    Returns:
        str: Exportierte Daten als String
    """
    # Filter Entries nach Datum
    filtered_entries = self.audit_entries
    if start_date or end_date:
        filtered_entries = []
        for entry in self.audit_entries:
            entry_date = datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00'))
            if start_date and entry_date < start_date:
                continue
            if end_date and entry_date > end_date:
                continue
            filtered_entries.append(entry)
   
    if format == 'json':
        if privacy_safe:
            safe_entries = [entry.get_privacy_safe_summary() for entry in filtered_entries]
            return json.dumps(safe_entries, indent=2, ensure_ascii=False)
        else:
            return json.dumps([entry.to_dict() for entry in filtered_entries], indent=2, ensure_ascii=False)
   
    elif format == 'csv':
        # Einfache CSV-Darstellung
        lines = ['timestamp,decision_type,align_score,violations_count,compliance_status,response_time_ms']
        for entry in filtered_entries:
            line = f"{entry.timestamp},{entry.decision_type},{entry.align_score or 'N/A'},{len(entry.align_violations)},{entry.compliance_status},{entry.response_time_ms or 'N/A'}"
            lines.append(line)
        return '\n'.join(lines)
   
    elif format == 'summary':
        stats = self.get_audit_statistics()
        return json.dumps(stats, indent=2, ensure_ascii=False)
   
    else:
        raise ValueError(f"Unbekanntes Export-Format: {format}")
```

# ==============================================================================

# 3. Standard INTEGRA-Interface

# ==============================================================================

def run_module(
input_data: Dict[str, Any],
profile: Dict[str, Any],
context: Dict[str, Any]
) -> Dict[str, Any]:
"""
📋 Standard INTEGRA-Interface für Mini-Audit

```
Args:
    input_data: Eingabedaten
    profile: Ethisches Profil
    context: Entscheidungskontext
   
Returns:
    Erweiterte context mit Audit-Informationen
"""

# Erstelle oder hole Audit-System aus Context
if 'mini_audit' not in context:
    audit_config = input_data.get('audit_config')
    if audit_config:
        config = AuditConfig(**audit_config)
    else:
        config = AuditConfig()
    context['mini_audit'] = INTEGRAMiniAudit(config)

auditor = context['mini_audit']

# Erstelle Audit-Entry
entry_id = auditor.log_decision(input_data, profile, context)

# Füge Audit-Informationen zum Context hinzu
context['audit_entry_id'] = entry_id
context['audit_logged'] = True

# Für Kompatibilität: Vereinfachtes Audit-Result
context['mini_audit_result'] = {
    'entry_id': entry_id,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'profile_used': profile.get('name', 'unknown'),
    'decision_logged': True
}

return context
```

# ==============================================================================

# 4. Convenience-Funktionen

# ==============================================================================

def create_simple_audit_log(
decision_type: str,
align_score: float,
violations: List[str] = None,
response_time_ms: float = None
) -> AuditEntry:
"""
📝 Erstellt einfaches Audit-Log für Quick-Tests

```
Args:
    decision_type: Art der Entscheidung
    align_score: ALIGN-Score
    violations: Liste von Verletzungen
    response_time_ms: Antwortzeit
   
Returns:
    AuditEntry: Einfaches Audit-Log
"""
entry = AuditEntry(
    decision_type=decision_type,
    align_score=align_score,
    align_violations=violations or [],
    response_time_ms=response_time_ms
)
return entry
```

# ==============================================================================

# 5. Unit-Tests

# ==============================================================================

def run_unit_tests():
"""🧪 Umfassende Tests für Mini-Audit"""
import tempfile
import shutil

```
print("🧪 Starte Unit-Tests für modules/audit/mini_audit.py...")

tests_passed = 0
tests_failed = 0

def run_test(name: str, test_func):
    nonlocal tests_passed, tests_failed
    try:
        test_func()
        print(f"  ✅ {name}")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ {name} - {e}")
        tests_failed += 1

# Test 1: Standard Interface
def test_standard_interface():
    profile = {'name': 'Test Profile', 'version': '1.0'}
    context = {
        'decision': {'path_taken': 'fast_path', 'response': 'Test response'},
        'align_score': 0.9,
        'align_violations': []
    }
   
    result = run_module({}, profile, context)
    assert 'audit_entry_id' in result
    assert 'mini_audit_result' in result
    assert result['audit_logged'] == True

# Test 2: AuditEntry Erstellung
def test_audit_entry_creation():
    auditor = INTEGRAMiniAudit()
   
    input_data = {'text': 'Test input'}
    profile = {'name': 'Test', 'sensitivity_level': 'normal'}
    context = {
        'decision': {'path_taken': 'deep_path'},
        'align_score': 0.75,
        'align_violations': ['awareness'],
        'response_time_ms': 150.5
    }
   
    entry = auditor.create_audit_entry(input_data, profile, context)
   
    assert entry.decision_type == 'deep_path'
    assert entry.align_score == 0.75
    assert 'awareness' in entry.align_violations
    assert entry.response_time_ms == 150.5

# Test 3: Compliance Assessment
def test_compliance_assessment():
    auditor = INTEGRAMiniAudit()
   
    # Test mit Violations
    context_with_violations = {
        'align_violations': ['integrity'],
        'risk_level': 0.9
    }
   
    status, warnings = auditor._assess_compliance(context_with_violations)
    assert status == 'violation'  # Integrity = kritisch
    assert len(warnings) >= 1

# Test 4: Privacy-Safe Summary
def test_privacy_safe_summary():
    auditor = INTEGRAMiniAudit()
   
    # Test mit sensitiven Daten
    sensitive_text = "Hallo, mein Name ist Max Mustermann und meine Email ist max@example.com"
    summary = auditor._create_safe_summary(sensitive_text)
   
    assert summary == "[REDACTED - POTENTIALLY SENSITIVE]"

# Test 5: File Logging
def test_file_logging():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = AuditConfig(log_directory=temp_dir, enable_file_logging=True)
        auditor = INTEGRAMiniAudit(config)
       
        # Log eine Entscheidung
        input_data = {'text': 'test'}
        profile = {'name': 'test'}
        context = {'decision': {'path_taken': 'fast_path'}}
       
        entry_id = auditor.log_decision(input_data, profile, context)
       
        # Prüfe ob Datei erstellt wurde
        files = os.listdir(temp_dir)
        assert len(files) > 0
        assert any('.jsonl' in f for f in files)

# Test 6: Statistiken
def test_audit_statistics():
    auditor = INTEGRAMiniAudit()
   
    # Füge Test-Entries hinzu
    for i in range(5):
        entry = create_simple_audit_log(
            'fast_path' if i % 2 == 0 else 'deep_path',
            0.8 + (i * 0.05),
            ['integrity'] if i == 2 else [],
            100 + (i * 10)
        )
        auditor.audit_entries.append(entry)
   
    stats = auditor.get_audit_statistics()
   
    assert stats['total_entries'] == 5
    assert 'decision_types' in stats
    assert 'compliance_rate' in stats

# Test 7: Export-Funktionen
def test_export_functions():
    auditor = INTEGRAMiniAudit()
   
    # Füge Test-Entry hinzu
    entry = create_simple_audit_log('fast_path', 0.9)
    auditor.audit_entries.append(entry)
   
    # Test JSON Export
    json_export = auditor.export_audit_logs('json', privacy_safe=True)
    assert 'entry_id' in json_export
   
    # Test CSV Export
    csv_export = auditor.export_audit_logs('csv')
    assert 'timestamp,decision_type' in csv_export

run_test("Standard INTEGRA Interface", test_standard_interface)
run_test("AuditEntry Erstellung", test_audit_entry_creation)
run_test("Compliance Assessment", test_compliance_assessment)
run_test("Privacy-Safe Summary", test_privacy_safe_summary)
run_test("File Logging", test_file_logging)
run_test("Audit Statistiken", test_audit_statistics)
run_test("Export Funktionen", test_export_functions)

print("-" * 50)
print(f"📊 Ergebnis: {tests_passed} ✅  {tests_failed} ❌")

return tests_failed == 0
```

# ==============================================================================

# 6. Demo-Funktion

# ==============================================================================

def run_demo():
"""🎮 Demo des Mini-Audit Systems"""
print("🎮 INTEGRA Mini-Audit Demo")
print("=" * 40)

```
# Setup mit temporärem Log-Directory
import tempfile
with tempfile.TemporaryDirectory() as temp_dir:
    config = AuditConfig(log_directory=temp
```