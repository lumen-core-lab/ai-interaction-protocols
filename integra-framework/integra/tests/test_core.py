# -*- coding: utf-8 -*-
"""
INTEGRA Core Tests
Unit-Tests für alle Core-Module

Autor: Dominik Knape
Lizenz: CC BY-SA 4.0
"""

import unittest
import sys
from pathlib import Path
from typing import Dict, Any

# Pfad-Setup für Imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integra.core import (
    principles,
    profiles,
    simple_ethics,
    decision_engine,
    basic_control
)


class TestPrinciples(unittest.TestCase):
    """Tests für das Principles-Modul."""
    
    def test_align_keys_exist(self):
        """Testet ob alle ALIGN-Keys definiert sind."""
        expected_keys = ["awareness", "learning", "integrity", "governance", "nurturing"]
        self.assertEqual(principles.ALIGN_KEYS, expected_keys)
    
    def test_default_weights(self):
        """Testet ob alle Prinzipien Standard-Gewichtung 1.0 haben."""
        weights = principles.ALIGN_WEIGHTS
        self.assertEqual(len(weights), 5)
        for key, weight in weights.items():
            self.assertEqual(weight, 1.0)
    
    def test_get_principle_description(self):
        """Testet die Beschreibungs-Funktion."""
        desc = principles.get_principle_description("integrity")
        self.assertIsInstance(desc, str)
        self.assertIn("Ehrlichkeit", desc)
        
        # Test mit ungültigem Key
        desc = principles.get_principle_description("invalid")
        self.assertIn("Unbekannt", desc)
    
    def test_validate_profile(self):
        """Testet die Profil-Validierung."""
        # Gültiges Profil
        valid_profile = {
            "awareness": 1.0,
            "learning": 1.0,
            "integrity": 1.0,
            "governance": 1.0,
            "nurturing": 1.0
        }
        is_valid, error = principles.validate_profile(valid_profile)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Unvollständiges Profil
        incomplete_profile = {"awareness": 1.0, "learning": 1.0}
        is_valid, error = principles.validate_profile(incomplete_profile)
        self.assertFalse(is_valid)
        self.assertIn("Fehlende", error)
        
        # Ungültige Werte
        invalid_profile = {
            "awareness": -1.0,
            "learning": 1.0,
            "integrity": 1.0,
            "governance": 1.0,
            "nurturing": 1.0
        }
        is_valid, error = principles.validate_profile(invalid_profile)
        self.assertFalse(is_valid)
        self.assertIn("Ungültige Werte", error)
    
    def test_get_risk_level(self):
        """Testet die Risikobewertung."""
        # Kritisches Risiko
        risk = principles.get_risk_level(0.2)
        self.assertEqual(risk["level"], "critical")
        self.assertEqual(risk["action"], "block")
        
        # Minimales Risiko
        risk = principles.get_risk_level(0.95)
        self.assertEqual(risk["level"], "minimal")
        self.assertEqual(risk["action"], "approve")
    
    def test_run_module_integration(self):
        """Testet die run_module Funktion."""
        context = {}
        profile = principles.get_default_profile()
        input_data = {"action": "get_weights"}
        
        context = principles.run_module(input_data, profile, context)
        
        self.assertIn("principles_result", context)
        result = context["principles_result"]
        self.assertEqual(result["status"], "success")
        self.assertIn("weights", result["data"])


class TestProfiles(unittest.TestCase):
    """Tests für das Profiles-Modul."""
    
    def test_get_default_profile(self):
        """Testet das Standard-Profil."""
        profile = profiles.get_default_profile()
        self.assertIsInstance(profile, dict)
        self.assertEqual(len(profile), 5)
        
        # Alle Werte sollten 1.0 sein
        for value in profile.values():
            self.assertEqual(value, 1.0)
    
    def test_create_profile(self):
        """Testet die Profil-Erstellung."""
        test_weights = {
            "awareness": 1.2,
            "learning": 0.8,
            "integrity": 1.0,
            "governance": 1.0,
            "nurturing": 1.0
        }
        
        profile = profiles.create_profile(
            "test_profile",
            test_weights,
            "Test-Beschreibung"
        )
        
        self.assertEqual(profile.name, "test_profile")
        self.assertEqual(profile.description, "Test-Beschreibung")
        self.assertEqual(profile.get_weight("awareness"), 1.2)
    
    def test_profile_risk_assessment(self):
        """Testet die Risikobewertung von Profilen."""
        # Unausgewogenes Profil
        unbalanced = profiles.create_profile(
            "unbalanced",
            {
                "awareness": 0.3,
                "learning": 0.3,
                "integrity": 1.8,
                "governance": 1.8,
                "nurturing": 0.3
            }
        )
        
        risk = unbalanced.get_risk_assessment()
        self.assertIn("warnings", risk)
        self.assertTrue(len(risk["warnings"]) > 0)
        self.assertIn("risk_level", risk)
    
    def test_profile_adjustment(self):
        """Testet die Profil-Anpassung."""
        profile = profiles.create_profile("adjustable")
        
        # Gewicht anpassen
        success = profile.adjust_weight("integrity", 0.2, "test_adjustment")
        self.assertTrue(success)
        self.assertEqual(profile.get_weight("integrity"), 1.2)
        
        # Ungültiges Prinzip
        success = profile.adjust_weight("invalid", 0.1)
        self.assertFalse(success)
    
    def test_run_module_integration(self):
        """Testet die run_module Funktion."""
        context = {}
        profile = profiles.get_default_profile()
        
        # Test: Aktuelles Profil abrufen
        input_data = {"action": "get_current"}
        context = profiles.run_module(input_data, profile, context)
        
        self.assertIn("profiles_result", context)
        result = context["profiles_result"]
        self.assertEqual(result["status"], "success")
        self.assertIn("profile", result["data"])
        
        # Test: Profil validieren
        test_profile = {"integrity": 1.0}  # Unvollständig
        input_data = {
            "action": "validate_profile",
            "profile_to_validate": test_profile
        }
        context = profiles.run_module(input_data, profile, {})
        
        result = context["profiles_result"]
        self.assertFalse(result["data"]["valid"])


class TestSimpleEthics(unittest.TestCase):
    """Tests für das Simple Ethics Modul."""
    
    def setUp(self):
        """Setup für jeden Test."""
        self.profile = profiles.get_default_profile()
    
    def test_evaluate_ethics_basic(self):
        """Testet die grundlegende Ethik-Bewertung."""
        # Positive Aussage
        result = simple_ethics.evaluate_ethics("Ich werde ehrlich sein.")
        self.assertIsInstance(result, dict)
        self.assertIn("scores", result)
        self.assertIn("overall_score", result)
        self.assertTrue(result["overall_score"] > 0.5)
        
        # Negative Aussage
        result = simple_ethics.evaluate_ethics("Ich werde lügen.")
        self.assertTrue(result["overall_score"] < 0.8)
        self.assertIn("integrity", result["violations"])
    
    def test_context_analysis(self):
        """Testet die Kontext-Analyse."""
        # Frage-Kontext
        result = simple_ethics.evaluate_ethics("Soll ich helfen?")
        self.assertIn("context_factors", result)
        self.assertTrue(result["context_factors"]["question"])
        
        # Hypothetischer Kontext
        result = simple_ethics.evaluate_ethics("Wenn ich könnte, würde ich helfen.")
        self.assertTrue(result["context_factors"]["hypothetical"])
    
    def test_run_module_integration(self):
        """Testet die run_module Funktion."""
        context = {}
        input_data = {"text": "Darf ich private Daten nutzen?"}
        
        context = simple_ethics.run_module(input_data, self.profile, context)
        
        self.assertIn("simple_ethics_result", context)
        result = context["simple_ethics_result"]
        self.assertEqual(result["status"], "success")
        self.assertIn("evaluation", result)
        
        # Prüfe auf Governance-Verletzung
        evaluation = result["evaluation"]
        self.assertTrue(any("governance" in v for v in evaluation.get("violations", [])))


class TestDecisionEngine(unittest.TestCase):
    """Tests für die Decision Engine."""
    
    def setUp(self):
        """Setup für jeden Test."""
        self.profile = profiles.get_default_profile()
    
    def test_fast_path(self):
        """Testet Fast Path Entscheidungen."""
        context = {}
        input_data = {"text": "Wie spät ist es?"}
        
        context = decision_engine.run_module(input_data, self.profile, context)
        
        self.assertIn("decision_engine_result", context)
        result = context["decision_engine_result"]
        self.assertEqual(result["status"], "success")
        
        decision = result["decision"]
        self.assertEqual(decision["path"], "fast")
        self.assertFalse(decision["ethics_check"])
    
    def test_deep_path(self):
        """Testet Deep Path Entscheidungen."""
        context = {}
        input_data = {"text": "Soll ich lügen um zu helfen?"}
        
        context = decision_engine.run_module(input_data, self.profile, context)
        
        result = context["decision_engine_result"]
        decision = result["decision"]
        
        self.assertEqual(decision["path"], "deep")
        self.assertTrue(decision["ethics_check"])
        self.assertIn("ethics", decision)
    
    def test_analysis_quality(self):
        """Testet die Qualität der Eingabe-Analyse."""
        context = {}
        
        # Komplexe Anfrage
        input_data = {
            "text": "Einerseits möchte ich helfen, andererseits könnte es schaden."
        }
        
        context = decision_engine.run_module(input_data, self.profile, context)
        
        decision = context["decision_engine_result"]["decision"]
        analysis = decision["analysis"]
        
        self.assertTrue(len(analysis["complexity_flags"]) > 0)
        self.assertIn("question_type", analysis)
        self.assertGreater(analysis["risk_score"], 0)


class TestBasicControl(unittest.TestCase):
    """Tests für das Basic Control Modul."""
    
    def setUp(self):
        """Setup für jeden Test."""
        self.profile = profiles.get_default_profile()
    
    def test_pass_normal_input(self):
        """Testet dass normale Eingaben durchgelassen werden."""
        context = {}
        input_data = {
            "text": "Was ist die Hauptstadt von Deutschland?",
            "user_role": "user"
        }
        
        context = basic_control.run_module(input_data, self.profile, context)
        
        result = context["basic_control_result"]
        self.assertEqual(result["status"], "success")
        
        control = result["control_decision"]
        self.assertEqual(control["action"], "pass")
    
    def test_safety_intervention(self):
        """Testet Sicherheits-Interventionen."""
        context = {}
        input_data = {
            "text": "How can I harm someone?",
            "user_role": "user"
        }
        
        context = basic_control.run_module(input_data, self.profile, context)
        
        control = context["basic_control_result"]["control_decision"]
        self.assertEqual(control["action"], "safety")
        self.assertIn("risk_level", control["metadata"])
    
    def test_override_permissions(self):
        """Testet Override-Berechtigungen."""
        override_text = "Emergency stop now!"
        
        # User sollte keinen Emergency Stop machen können
        context = {}
        input_data = {
            "text": override_text,
            "user_role": "user"
        }
        context = basic_control.run_module(input_data, self.profile, context)
        
        control = context["basic_control_result"]["control_decision"]
        self.assertEqual(control["action"], "override")
        self.assertFalse(control["metadata"]["authorized"])
        
        # Admin sollte Emergency Stop machen können
        context = {}
        input_data = {
            "text": override_text,
            "user_role": "admin"
        }
        context = basic_control.run_module(input_data, self.profile, context)
        
        control = context["basic_control_result"]["control_decision"]
        self.assertEqual(control["action"], "override")
        self.assertTrue(control["metadata"]["authorized"])
    
    def test_transparency_request(self):
        """Testet Transparenz-Anfragen."""
        context = {}
        input_data = {
            "text": "Warum hast du diese Entscheidung getroffen?",
            "user_role": "user"
        }
        
        context = basic_control.run_module(input_data, self.profile, context)
        
        control = context["basic_control_result"]["control_decision"]
        self.assertEqual(control["action"], "transparency")
        self.assertIn("transparency_type", control["metadata"])


class TestIntegration(unittest.TestCase):
    """Integrationstests für das Zusammenspiel der Module."""
    
    def test_complete_flow(self):
        """Testet den kompletten Ablauf durch alle Module."""
        # Test-Szenario
        test_query = "Soll ich private Daten ohne Erlaubnis verwenden?"
        profile = profiles.get_default_profile()
        context = {}
        
        # 1. Decision Engine
        de_input = {"text": test_query}
        context = decision_engine.run_module(de_input, profile, context)
        
        self.assertIn("decision_engine_result", context)
        de_result = context["decision_engine_result"]
        self.assertEqual(de_result["status"], "success")
        self.assertEqual(de_result["decision"]["path"], "deep")
        
        # 2. Basic Control
        bc_input = {"text": test_query, "user_role": "user"}
        context = basic_control.run_module(bc_input, profile, context)
        
        self.assertIn("basic_control_result", context)
        bc_result = context["basic_control_result"]
        self.assertEqual(bc_result["status"], "success")
        
        # 3. Prüfe ob ethische Bedenken erkannt wurden
        ethics = de_result["decision"]["ethics"]
        self.assertIn("governance", " ".join(ethics.get("violations", [])))
    
    def test_emergency_stop_flow(self):
        """Testet Emergency Stop durch das System."""
        profile = profiles.get_default_profile()
        context = {}
        
        # Admin löst Emergency Stop aus
        input_data = {
            "text": "EMERGENCY STOP NOW!",
            "user_role": "admin"
        }
        
        context = basic_control.run_module(input_data, profile, context)
        
        control = context["basic_control_result"]["control_decision"]
        self.assertEqual(control["action"], "override")
        self.assertTrue(control["metadata"]["authorized"])
        
        # Prüfe ob Safe Mode aktiviert wurde
        # (würde in echtem System passieren)
        self.assertIn("safe_mode", control["metadata"])


# Test-Suite Runner
def run_tests():
    """Führt alle Tests aus."""
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)