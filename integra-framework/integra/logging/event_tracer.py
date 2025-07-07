# -*- coding: utf-8 -*-
"""
Event Tracer für INTEGRA
Erweiterte Event-Verfolgung
"""

from datetime import datetime
import json

class EventTracer:
    def __init__(self):
        self.events = []
    
    def trace_event(self, event_type, module, data):
        """Verfolgt ein Event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "module": module,
            "data": data
        }
        self.events.append(event)
        return event
    
    def get_trace(self):
        """Gibt alle Events zurück."""
        return self.events

# Globale Instanz
_tracer = EventTracer()

def trace_event(event_type, module, data):
    """Einfache Funktion zum Event-Tracing."""
    return _tracer.trace_event(event_type, module, data)