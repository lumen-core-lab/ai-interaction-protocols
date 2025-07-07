# -*- coding: utf-8 -*-
"""
Modulname: nga.py
Beschreibung: Normative Goal Alignment für INTEGRA Full - Validierung gegen externe Normen
Teil von: INTEGRA Full Layer
Autor: Dominik Knape
Version: 2.0
Lizenz: CC BY-SA 4.0

Änderungen in v2.0:
- Standardisierte run_module() Schnittstelle
- Baukasten-kompatible Context-Nutzung
- Integration mit anderen Modulen über Context
- Globale Instanz mit Lazy-Loading
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path

# Import-Kompatibilität
try:
    from integra.core import principles, profiles
    from integra.utils import log_manager
except ImportError:
    try:
        from core import principles, profiles
        from utils import log_manager
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from core import principles, profiles
            log_manager = None
        except ImportError:
            print("❌ Fehler: Core Module nicht gefunden!")
            # Fallback definitions
            class principles:
                ALIGN_KEYS = ["awareness", "learning", "integrity", "governance", "nurturing"]
            class profiles:
                @staticmethod
                def get_default_profile():
                    return {k: 1.0 for k in principles.ALIGN_KEYS}
            log_manager = None


class NormativeFramework(Enum):
    """Unterstützte normative Frameworks."""
    UN_HUMAN_RIGHTS = "un_human_rights"
    GDPR = "gdpr"
    UN_SDG = "un_sdg"
    ISO_26000 = "iso_26000"
    MEDICAL_ETHICS = "medical_ethics"
    CORPORATE_ETHICS = "corporate_ethics"


class ViolationSeverity(Enum):
    """Schweregrad von Normverletzungen."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class NormativeGoalAlignment:
    """
    Normative Goal Alignment (NGA) - Prüft Entscheidungen gegen externe Normen.
    
    Validiert ethische Entscheidungen gegen etablierte normative Frameworks
    wie Menschenrechte, GDPR, SDGs etc.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialisiert das NGA-System.
        
        Args:
            config: Optionale Konfiguration
        """
        self.config = config or {}
        
        # Frameworks aus Config oder Defaults
        enabled_framework_names = self.config.get("enabled_frameworks", [
            NormativeFramework.UN_HUMAN_RIGHTS.value,
            NormativeFramework.GDPR.value
        ])
        
        # Konvertiere String-Namen zu Enums
        self.enabled_frameworks = []
        for framework_name in enabled_framework_names:
            try:
                self.enabled_frameworks.append(NormativeFramework(framework_name))
            except ValueError:
                if log_manager:
                    log_manager.log_event("NGA", f"Unbekanntes Framework: {framework_name}", "WARNING")
        
        # Weitere Config-Optionen
        self.strict_mode = self.config.get("strict_mode", False)
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.escalation_threshold = self.config.get("escalation_threshold", 0.5)
        
        # Lade normative Kataloge
        self.normative_catalogs = self._load_normative_catalogs()
        
        # Statistiken
        self.stats = {
            "total_validations": 0,
            "violations_found": 0,
            "critical_violations": 0,
            "frameworks_checked": 0,
            "compliance_rate": 1.0
        }
        
        # Cache für häufige Prüfungen
        self.validation_cache = {} if self.cache_enabled else None
        
    def _load_normative_catalogs(self) -> Dict[NormativeFramework, Dict[str, Any]]:
        """Lädt die normativen Kataloge."""
        catalogs = {}
        
        # UN Menschenrechte
        catalogs[NormativeFramework.UN_HUMAN_RIGHTS] = {
            "articles": {
                "article_1": {
                    "title": "Würde und Gleichheit",
                    "content": "Alle Menschen sind frei und gleich an Würde und Rechten geboren",
                    "keywords": ["würde", "dignity", "gleichheit", "equality", "rechte", "rights"],
                    "principles": ["integrity", "nurturing"]
                },
                "article_2": {
                    "title": "Diskriminierungsverbot",
                    "content": "Keine Diskriminierung aufgrund von Rasse, Geschlecht, Religion etc.",
                    "keywords": ["diskriminierung", "discrimination", "gleichbehandlung"],
                    "principles": ["integrity", "awareness"]
                },
                "article_12": {
                    "title": "Privatsphäre",
                    "content": "Schutz der Privatsphäre",
                    "keywords": ["privat", "privacy", "persönlich", "personal"],
                    "principles": ["integrity", "governance"]
                },
                "article_19": {
                    "title": "Meinungsfreiheit",
                    "content": "Recht auf freie Meinungsäußerung",
                    "keywords": ["meinung", "opinion", "äußerung", "expression"],
                    "principles": ["integrity", "learning"]
                }
            }
        }
        
        # GDPR
        catalogs[NormativeFramework.GDPR] = {
            "principles": {
                "lawfulness": {
                    "title": "Rechtmäßigkeit",
                    "requirements": ["Rechtsgrundlage", "Transparenz"],
                    "keywords": ["rechtmäßig", "lawful", "legal", "erlaubt"],
                    "principles": ["governance", "integrity"]
                },
                "purpose_limitation": {
                    "title": "Zweckbindung",
                    "requirements": ["Spezifischer Zweck", "Keine Zweckentfremdung"],
                    "keywords": ["zweck", "purpose", "verwendung", "use"],
                    "principles": ["integrity", "governance"]
                },
                "data_minimization": {
                    "title": "Datenminimierung",
                    "requirements": ["Nur notwendige Daten"],
                    "keywords": ["minimal", "notwendig", "necessary", "erforderlich"],
                    "principles": ["governance", "awareness"]
                },
                "consent": {
                    "title": "Einwilligung",
                    "requirements": ["Freiwillig", "Informiert", "Eindeutig"],
                    "keywords": ["einwilligung", "consent", "zustimmung", "erlaubnis"],
                    "principles": ["integrity", "nurturing"]
                }
            }
        }
        
        # UN SDGs
        catalogs[NormativeFramework.UN_SDG] = {
            "goals": {
                "sdg_3": {
                    "title": "Gesundheit und Wohlergehen",
                    "targets": ["Gesundheitsversorgung", "Prävention"],
                    "keywords": ["gesundheit", "health", "wohlbefinden", "wellbeing"],
                    "principles": ["nurturing", "awareness"]
                },
                "sdg_4": {
                    "title": "Hochwertige Bildung",
                    "targets": ["Bildungszugang", "Lebenslanges Lernen"],
                    "keywords": ["bildung", "education", "lernen", "learning"],
                    "principles": ["learning", "nurturing"]
                },
                "sdg_10": {
                    "title": "Weniger Ungleichheiten",
                    "targets": ["Chancengleichheit", "Inklusion"],
                    "keywords": ["gleichheit", "equality", "inklusion", "inclusion"],
                    "principles": ["integrity", "nurturing"]
                }
            }
        }
        
        # ISO 26000
        catalogs[NormativeFramework.ISO_26000] = {
            "core_subjects": {
                "human_rights": {
                    "title": "Menschenrechte",
                    "aspects": ["Due Diligence", "Vulnerable Groups"],
                    "principles": ["integrity", "nurturing", "awareness"]
                },
                "fair_practices": {
                    "title": "Faire Betriebs- und Geschäftspraktiken",
                    "aspects": ["Anti-Korruption", "Fairer Wettbewerb"],
                    "principles": ["integrity", "governance"]
                },
                "consumer_issues": {
                    "title": "Konsumentenanliegen",
                    "aspects": ["Faire Praktiken", "Datenschutz", "Service"],
                    "principles": ["integrity", "nurturing", "governance"]
                }
            }
        }
        
        # Medizinethik
        catalogs[NormativeFramework.MEDICAL_ETHICS] = {
            "principles": {
                "autonomy": {
                    "title": "Autonomie",
                    "content": "Respekt vor Patientenautonomie",
                    "keywords": ["autonomie", "autonomy", "selbstbestimmung"],
                    "principles": ["integrity", "awareness"]
                },
                "beneficence": {
                    "title": "Wohltätigkeit",
                    "content": "Zum Wohl des Patienten handeln",
                    "keywords": ["wohl", "beneficence", "nutzen", "benefit"],
                    "principles": ["nurturing"]
                },
                "non_maleficence": {
                    "title": "Nicht-Schaden",
                    "content": "Primum non nocere",
                    "keywords": ["schaden", "harm", "verletzung", "injury"],
                    "principles": ["nurturing", "awareness"]
                },
                "justice": {
                    "title": "Gerechtigkeit",
                    "content": "Faire Verteilung von Ressourcen",
                    "keywords": ["gerechtigkeit", "justice", "fair", "verteilung"],
                    "principles": ["integrity", "governance"]
                }
            }
        }
        
        # Corporate Ethics
        catalogs[NormativeFramework.CORPORATE_ETHICS] = {
            "standards": {
                "transparency": {
                    "title": "Transparenz",
                    "requirements": ["Offenlegung", "Nachvollziehbarkeit"],
                    "principles": ["integrity", "governance"]
                },
                "accountability": {
                    "title": "Rechenschaftspflicht",
                    "requirements": ["Verantwortung", "Berichterstattung"],
                    "principles": ["governance", "integrity"]
                },
                "sustainability": {
                    "title": "Nachhaltigkeit",
                    "requirements": ["Langfristigkeit", "Ressourcenschonung"],
                    "principles": ["awareness", "nurturing"]
                }
            }
        }
        
        return catalogs
    
    def validate_against_norms(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validiert eine Entscheidung gegen aktivierte normative Frameworks.
        
        Args:
            input_text: Zu prüfender Text
            context: Vollständiger Entscheidungskontext
            
        Returns:
            Dict mit Validierungsergebnissen
        """
        self.stats["total_validations"] += 1
        
        # Cache-Key generieren
        cache_key = None
        if self.cache_enabled:
            cache_key = f"{input_text[:100]}_{hash(str(sorted(context.items())))}"
            if cache_key in self.validation_cache:
                return self.validation_cache[cache_key]
        
        validation_results = {
            "overall_compliance": 1.0,
            "overall_compliance_status": "compliant",
            "frameworks_checked": [],
            "catalogs_checked": [],  # Für Kompatibilität
            "violations": [],
            "warnings": [],
            "recommendations": [],
            "compliance_scores": {},
            "compliance_score": 1.0  # Für Kompatibilität
        }
        
        # Kombiniere relevante Texte
        combined_text = self._combine_texts(input_text, context)
        
        # Nutze Ergebnisse anderer Module aus Context
        ethics_result = context.get("simple_ethics_result", {})
        etb_result = context.get("etb_result", {})
        pae_result = context.get("pae_result", {})
        
        # Prüfe jeden aktivierten Framework
        for framework in self.enabled_frameworks:
            if framework in self.normative_catalogs:
                framework_result = self._validate_framework(
                    framework, 
                    self.normative_catalogs[framework],
                    context,
                    combined_text,
                    ethics_result
                )
                
                validation_results["frameworks_checked"].append(framework.value)
                validation_results["catalogs_checked"].append(framework.value)  # Kompatibilität
                validation_results["compliance_scores"][framework.value] = framework_result["score"]
                
                # Sammle Verletzungen und Warnungen
                validation_results["violations"].extend(framework_result["violations"])
                validation_results["warnings"].extend(framework_result["warnings"])
                validation_results["recommendations"].extend(framework_result["recommendations"])
                
                self.stats["frameworks_checked"] += 1
        
        # Berechne Gesamt-Compliance
        if validation_results["compliance_scores"]:
            validation_results["overall_compliance"] = sum(
                validation_results["compliance_scores"].values()
            ) / len(validation_results["compliance_scores"])
            validation_results["compliance_score"] = validation_results["overall_compliance"]
        
        # Setze Status basierend auf Compliance
        if validation_results["violations"]:
            validation_results["overall_compliance_status"] = "violations"
        elif validation_results["warnings"]:
            validation_results["overall_compliance_status"] = "warnings"
        else:
            validation_results["overall_compliance_status"] = "compliant"
        
        # Aktualisiere Statistiken
        if validation_results["violations"]:
            self.stats["violations_found"] += len(validation_results["violations"])
            critical_count = sum(1 for v in validation_results["violations"] 
                               if v.get("severity") == ViolationSeverity.CRITICAL.value)
            self.stats["critical_violations"] += critical_count
        
        # Aktualisiere Compliance-Rate
        self.stats["compliance_rate"] = (
            (self.stats["total_validations"] - self.stats["violations_found"]) / 
            max(1, self.stats["total_validations"])
        )
        
        # Eskalation bei kritischen Verletzungen oder niedriger Compliance
        validation_results["escalation_required"] = (
            any(v.get("severity") == ViolationSeverity.CRITICAL.value 
                for v in validation_results["violations"]) or
            validation_results["overall_compliance"] < self.escalation_threshold
        )
        
        # Cache Ergebnis
        if self.cache_enabled and cache_key:
            self.validation_cache[cache_key] = validation_results
        
        return validation_results
    
    def _combine_texts(self, input_text: str, context: Dict[str, Any]) -> str:
        """Kombiniert relevante Texte aus dem Kontext."""
        texts = [input_text]
        
        # Response aus Context
        if "response" in context:
            texts.append(context["response"])
        
        # Decision Context
        decision_context = context.get("decision_context", {})
        if decision_context:
            if "user_input" in decision_context:
                texts.append(decision_context["user_input"])
            if "response" in decision_context:
                texts.append(decision_context["response"])
        
        return " ".join(filter(None, texts)).lower()
    
    def _validate_framework(self, framework: NormativeFramework,
                           catalog: Dict[str, Any],
                           context: Dict[str, Any],
                           text: str,
                           ethics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert gegen einen spezifischen normativen Framework."""
        result = {
            "score": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        if framework == NormativeFramework.UN_HUMAN_RIGHTS:
            return self._validate_human_rights(catalog, context, text, ethics_result)
        elif framework == NormativeFramework.GDPR:
            return self._validate_gdpr(catalog, context, text, ethics_result)
        elif framework == NormativeFramework.UN_SDG:
            return self._validate_sdg(catalog, context, text, ethics_result)
        elif framework == NormativeFramework.ISO_26000:
            return self._validate_iso26000(catalog, context, text, ethics_result)
        elif framework == NormativeFramework.MEDICAL_ETHICS:
            return self._validate_medical_ethics(catalog, context, text, ethics_result)
        elif framework == NormativeFramework.CORPORATE_ETHICS:
            return self._validate_corporate_ethics(catalog, context, text, ethics_result)
        
        return result
    
    def _validate_human_rights(self, catalog: Dict[str, Any],
                              context: Dict[str, Any],
                              text: str,
                              ethics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert gegen UN Menschenrechte."""
        result = {
            "score": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Nutze Ethics-Scores wenn verfügbar
        integrity_score = ethics_result.get("scores", {}).get("integrity", 1.0)
        awareness_score = ethics_result.get("scores", {}).get("awareness", 1.0)
        
        # Prüfe jeden Artikel
        for article_id, article in catalog["articles"].items():
            # Keyword-Matching
            violations_found = False
            
            # Spezifische Prüfungen
            if article_id == "article_2":  # Diskriminierung
                discriminatory_terms = ["rasse", "race", "geschlecht", "gender", 
                                      "religion", "herkunft", "origin"]
                if any(term in text and "keine" not in text and "nicht" not in text 
                      for term in discriminatory_terms):
                    violations_found = True
                    result["violations"].append({
                        "framework": NormativeFramework.UN_HUMAN_RIGHTS.value,
                        "catalog": NormativeFramework.UN_HUMAN_RIGHTS.value,  # Kompatibilität
                        "article": article_id,
                        "title": article["title"],
                        "severity": ViolationSeverity.HIGH.value,
                        "description": "Mögliche Diskriminierung erkannt",
                        "affected_principles": article["principles"]
                    })
                # Zusätzlich: Niedrige Awareness deutet auf Diskriminierungsrisiko
                elif awareness_score < 0.4:
                    result["warnings"].append({
                        "framework": NormativeFramework.UN_HUMAN_RIGHTS.value,
                        "catalog": NormativeFramework.UN_HUMAN_RIGHTS.value,
                        "article": article_id,
                        "title": article["title"],
                        "severity": ViolationSeverity.MODERATE.value,
                        "description": "Niedrige Awareness - Diskriminierungsrisiko prüfen",
                        "affected_principles": article["principles"]
                    })
            
            elif article_id == "article_12":  # Privatsphäre
                privacy_terms = ["speichern", "save", "aufzeichnen", "record", 
                               "sammeln", "collect", "daten", "data"]
                consent_terms = ["erlaubnis", "permission", "einwilligung", "consent"]
                
                if any(term in text for term in privacy_terms):
                    if not any(term in text for term in consent_terms):
                        # Nutze Governance-Score aus Ethics
                        governance_score = ethics_result.get("scores", {}).get("governance", 1.0)
                        if governance_score < 0.5:
                            severity = ViolationSeverity.HIGH
                        else:
                            severity = ViolationSeverity.MODERATE
                            
                        result["warnings"].append({
                            "framework": NormativeFramework.UN_HUMAN_RIGHTS.value,
                            "catalog": NormativeFramework.UN_HUMAN_RIGHTS.value,
                            "article": article_id,
                            "title": article["title"],
                            "severity": severity.value,
                            "description": "Datenschutz-Bedenken - Einwilligung prüfen",
                            "affected_principles": article["principles"]
                        })
            
            # Integrity-basierte Prüfung
            elif article_id == "article_1" and integrity_score < 0.3:
                result["violations"].append({
                    "framework": NormativeFramework.UN_HUMAN_RIGHTS.value,
                    "catalog": NormativeFramework.UN_HUMAN_RIGHTS.value,
                    "article": article_id,
                    "title": article["title"],
                    "severity": ViolationSeverity.HIGH.value,
                    "description": "Sehr niedrige Integrität verletzt Menschenwürde",
                    "affected_principles": article["principles"]
                })
        
        # Score anpassen
        violation_penalty = len(result["violations"]) * 0.3
        warning_penalty = len(result["warnings"]) * 0.1
        result["score"] = max(0, 1.0 - violation_penalty - warning_penalty)
        
        # Empfehlungen
        if result["violations"] or result["warnings"]:
            result["recommendations"].append({
                "framework": NormativeFramework.UN_HUMAN_RIGHTS.value,
                "recommendation": "Menschenrechts-Compliance-Review durchführen",
                "priority": "high" if result["violations"] else "medium"
            })
        
        return result
    
    def _validate_gdpr(self, catalog: Dict[str, Any],
                      context: Dict[str, Any],
                      text: str,
                      ethics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert gegen GDPR."""
        result = {
            "score": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Governance-Score ist kritisch für GDPR
        governance_score = ethics_result.get("scores", {}).get("governance", 1.0)
        
        # Datenschutz-Schlüsselwörter
        data_keywords = ["daten", "data", "information", "persönlich", "personal",
                        "name", "adresse", "address", "email", "telefon", "phone"]
        
        # Prüfe ob Datenverarbeitung vorliegt
        if any(keyword in text for keyword in data_keywords):
            # Prüfe Rechtmäßigkeit
            consent_found = any(term in text for term in 
                              ["einwilligung", "consent", "erlaubnis", "permission", 
                               "zustimmung", "agreement"])
            
            if not consent_found and governance_score < 0.7:
                result["violations"].append({
                    "framework": NormativeFramework.GDPR.value,
                    "catalog": NormativeFramework.GDPR.value,
                    "principle": "consent",
                    "title": "Fehlende Einwilligung",
                    "severity": ViolationSeverity.CRITICAL.value,
                    "description": "Datenverarbeitung ohne erkennbare Einwilligung",
                    "affected_principles": ["integrity", "governance"]
                })
            
            # Prüfe Zweckbindung
            purpose_keywords = ["zweck", "purpose", "grund", "reason", "ziel", "goal"]
            if not any(keyword in text for keyword in purpose_keywords):
                result["warnings"].append({
                    "framework": NormativeFramework.GDPR.value,
                    "catalog": NormativeFramework.GDPR.value,
                    "principle": "purpose_limitation",
                    "title": "Unklarer Verarbeitungszweck",
                    "severity": ViolationSeverity.MODERATE.value,
                    "description": "Zweck der Datenverarbeitung nicht eindeutig",
                    "affected_principles": ["integrity", "governance"]
                })
            
            # Datenminimierung
            if text.count("daten") > 3 or text.count("data") > 3:
                result["warnings"].append({
                    "framework": NormativeFramework.GDPR.value,
                    "catalog": NormativeFramework.GDPR.value,
                    "principle": "data_minimization",
                    "title": "Datenminimierung prüfen",
                    "severity": ViolationSeverity.LOW.value,
                    "description": "Umfangreiche Datenverarbeitung - Minimierung prüfen",
                    "affected_principles": ["governance", "awareness"]
                })
        
        # Score anpassen
        violation_penalty = len(result["violations"]) * 0.4
        warning_penalty = len(result["warnings"]) * 0.15
        result["score"] = max(0, 1.0 - violation_penalty - warning_penalty)
        
        # Empfehlungen
        if result["violations"]:
            result["recommendations"].append({
                "framework": NormativeFramework.GDPR.value,
                "recommendation": "Dringende GDPR-Compliance-Prüfung erforderlich",
                "priority": "critical"
            })
        elif result["warnings"] and governance_score < 0.8:
            result["recommendations"].append({
                "framework": NormativeFramework.GDPR.value,
                "recommendation": "Governance-Score erhöhen für bessere GDPR-Compliance",
                "priority": "medium"
            })
        
        return result
    
    def _validate_sdg(self, catalog: Dict[str, Any],
                     context: Dict[str, Any],
                     text: str,
                     ethics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert gegen UN SDGs."""
        result = {
            "score": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Nutze Learning und Nurturing Scores
        learning_score = ethics_result.get("scores", {}).get("learning", 1.0)
        nurturing_score = ethics_result.get("scores", {}).get("nurturing", 1.0)
        
        # SDGs sind eher Ziele als strikte Regeln - hauptsächlich Empfehlungen
        sdg_alignments = []
        
        for goal_id, goal in catalog["goals"].items():
            for keyword in goal["keywords"]:
                if keyword in text:
                    sdg_alignments.append({
                        "goal": goal_id,
                        "title": goal["title"],
                        "relevance": "high"
                    })
                    
                    # Positive Empfehlung
                    result["recommendations"].append({
                        "framework": NormativeFramework.UN_SDG.value,
                        "recommendation": f"Gut ausgerichtet auf {goal['title']}",
                        "priority": "low",
                        "sdg": goal_id
                    })
        
        # Bei fehlender SDG-Ausrichtung und niedrigen Scores
        if not sdg_alignments:
            if learning_score < 0.5:
                result["warnings"].append({
                    "framework": NormativeFramework.UN_SDG.value,
                    "catalog": NormativeFramework.UN_SDG.value,
                    "goal": "sdg_4",
                    "title": "Bildungschancen",
                    "severity": ViolationSeverity.LOW.value,
                    "description": "Niedrige Learning-Score - SDG 4 (Bildung) könnte gefördert werden",
                    "affected_principles": ["learning", "nurturing"]
                })
            
            if nurturing_score < 0.5:
                result["warnings"].append({
                    "framework": NormativeFramework.UN_SDG.value,
                    "catalog": NormativeFramework.UN_SDG.value,
                    "goal": "sdg_3",
                    "title": "Gesundheit und Wohlergehen",
                    "severity": ViolationSeverity.LOW.value,
                    "description": "Niedrige Nurturing-Score - SDG 3 (Wohlergehen) beachten",
                    "affected_principles": ["nurturing", "awareness"]
                })
        
        # Score hauptsächlich positiv
        result["score"] = 1.0 - len(result["warnings"]) * 0.05
        
        return result
    
    def _validate_iso26000(self, catalog: Dict[str, Any],
                          context: Dict[str, Any],
                          text: str,
                          ethics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert gegen ISO 26000."""
        result = {
            "score": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # ISO 26000 ist ein Leitfaden, keine zwingende Norm
        # Fokus auf Empfehlungen
        
        # Vulnerable Groups Check
        vulnerable_keywords = ["kind", "child", "behindert", "disabled", 
                             "alt", "elderly", "minderheit", "minority"]
        
        if any(keyword in text for keyword in vulnerable_keywords):
            # Positiv wenn Schutz erwähnt
            if any(term in text for term in ["schutz", "protect", "unterstütz", "support"]):
                result["recommendations"].append({
                    "framework": NormativeFramework.ISO_26000.value,
                    "recommendation": "Guter Fokus auf vulnerable Gruppen gemäß ISO 26000",
                    "priority": "low"
                })
            else:
                # Nutze Nurturing und Awareness aus Ethics
                nurturing = ethics_result.get("scores", {}).get("nurturing", 1.0)
                awareness = ethics_result.get("scores", {}).get("awareness", 1.0)
                
                if nurturing < 0.6 or awareness < 0.6:
                    result["warnings"].append({
                        "framework": NormativeFramework.ISO_26000.value,
                        "catalog": NormativeFramework.ISO_26000.value,
                        "subject": "human_rights",
                        "title": "Vulnerable Gruppen",
                        "severity": ViolationSeverity.MODERATE.value,
                        "description": "Besondere Sorgfaltspflicht bei vulnerablen Gruppen beachten",
                        "affected_principles": ["nurturing", "awareness"]
                    })
        
        result["score"] = 1.0 - len(result["warnings"]) * 0.1
        
        return result
    
    def _validate_medical_ethics(self, catalog: Dict[str, Any],
                                context: Dict[str, Any],
                                text: str,
                                ethics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert gegen medizinische Ethik."""
        result = {
            "score": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Nur relevant bei medizinischen Themen
        medical_keywords = ["patient", "behandlung", "treatment", "diagnose", 
                          "diagnosis", "medizin", "medical", "gesundheit", "health",
                          "therapie", "therapy", "arzt", "doctor"]
        
        if not any(keyword in text for keyword in medical_keywords):
            # Nicht anwendbar
            return result
        
        # Prüfe die vier Prinzipien
        principles = catalog["principles"]
        
        # Non-maleficence (Nicht-Schaden)
        harm_keywords = ["schaden", "harm", "verletz", "injur", "risiko", "risk"]
        if any(keyword in text for keyword in harm_keywords):
            nurturing_score = ethics_result.get("scores", {}).get("nurturing", 1.0)
            
            if nurturing_score < 0.7:
                result["violations"].append({
                    "framework": NormativeFramework.MEDICAL_ETHICS.value,
                    "catalog": NormativeFramework.MEDICAL_ETHICS.value,
                    "principle": "non_maleficence",
                    "title": principles["non_maleficence"]["title"],
                    "severity": ViolationSeverity.HIGH.value,
                    "description": "Primum non nocere - Niedrige Nurturing-Score bei Risiko",
                    "affected_principles": ["nurturing", "awareness"]
                })
        
        # Autonomie
        autonomy_keywords = ["entscheid", "decide", "wahl", "choice", "selbst", "self"]
        consent_keywords = ["einverständnis", "consent", "aufklärung", "informed"]
        
        if any(keyword in text for keyword in autonomy_keywords):
            if not any(keyword in text for keyword in consent_keywords):
                integrity_score = ethics_result.get("scores", {}).get("integrity", 1.0)
                
                if integrity_score < 0.6:
                    severity = ViolationSeverity.HIGH
                else:
                    severity = ViolationSeverity.MODERATE
                    
                result["warnings"].append({
                    "framework": NormativeFramework.MEDICAL_ETHICS.value,
                    "catalog": NormativeFramework.MEDICAL_ETHICS.value,
                    "principle": "autonomy",
                    "title": principles["autonomy"]["title"],
                    "severity": severity.value,
                    "description": "Patientenautonomie und informierte Einwilligung sicherstellen",
                    "affected_principles": ["integrity", "awareness"]
                })
        
        # Score anpassen
        violation_penalty = len(result["violations"]) * 0.35
        warning_penalty = len(result["warnings"]) * 0.15
        result["score"] = max(0, 1.0 - violation_penalty - warning_penalty)
        
        return result
    
    def _validate_corporate_ethics(self, catalog: Dict[str, Any],
                                  context: Dict[str, Any],
                                  text: str,
                                  ethics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert gegen Unternehmensethik."""
        result = {
            "score": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Corporate Keywords
        corporate_keywords = ["geschäft", "business", "unternehmen", "company",
                            "kunde", "customer", "produkt", "product", "service"]
        
        if not any(keyword in text for keyword in corporate_keywords):
            return result  # Nicht anwendbar
        
        # Nutze Governance und Integrity Scores
        governance_score = ethics_result.get("scores", {}).get("governance", 1.0)
        integrity_score = ethics_result.get("scores", {}).get("integrity", 1.0)
        
        # Transparenz-Check
        if any(term in text for term in ["versteck", "hide", "verschleier", "obscure"]):
            result["violations"].append({
                "framework": NormativeFramework.CORPORATE_ETHICS.value,
                "catalog": NormativeFramework.CORPORATE_ETHICS.value,
                "standard": "transparency",
                "title": "Transparenz",
                "severity": ViolationSeverity.HIGH.value,
                "description": "Mangelnde Transparenz in Geschäftspraktiken",
                "affected_principles": ["integrity", "governance"]
            })
        elif integrity_score < 0.5:
            result["warnings"].append({
                "framework": NormativeFramework.CORPORATE_ETHICS.value,
                "catalog": NormativeFramework.CORPORATE_ETHICS.value,
                "standard": "transparency",
                "title": "Transparenz",
                "severity": ViolationSeverity.MODERATE.value,
                "description": "Niedrige Integrity-Score gefährdet Transparenz",
                "affected_principles": ["integrity", "governance"]
            })
        
        # Accountability
        if governance_score < 0.5:
            result["warnings"].append({
                "framework": NormativeFramework.CORPORATE_ETHICS.value,
                "catalog": NormativeFramework.CORPORATE_ETHICS.value,
                "standard": "accountability",
                "title": "Rechenschaftspflicht",
                "severity": ViolationSeverity.MODERATE.value,
                "description": "Niedrige Governance-Score - Rechenschaftspflicht stärken",
                "affected_principles": ["governance", "integrity"]
            })
        
        # Nachhaltigkeit
        sustainability_positive = ["nachhaltig", "sustainable", "langfristig", "long-term"]
        if any(term in text for term in sustainability_positive):
            result["recommendations"].append({
                "framework": NormativeFramework.CORPORATE_ETHICS.value,
                "recommendation": "Guter Fokus auf Nachhaltigkeit",
                "priority": "low"
            })
        
        # Score
        violation_penalty = len(result["violations"]) * 0.3
        warning_penalty = len(result["warnings"]) * 0.1
        result["score"] = max(0, 1.0 - violation_penalty - warning_penalty)
        
        return result
    
    def get_framework_info(self, framework: NormativeFramework) -> Dict[str, Any]:
        """Gibt Informationen über einen normativen Framework zurück."""
        if framework not in self.normative_catalogs:
            return {"error": "Framework nicht gefunden"}
        
        catalog = self.normative_catalogs[framework]
        
        # Basis-Info
        info = {
            "framework": framework.value,
            "enabled": framework in self.enabled_frameworks,
            "structure": list(catalog.keys())
        }
        
        # Framework-spezifische Details
        if framework == NormativeFramework.UN_HUMAN_RIGHTS:
            info["articles_count"] = len(catalog.get("articles", {}))
            info["articles"] = list(catalog.get("articles", {}).keys())
        elif framework == NormativeFramework.GDPR:
            info["principles_count"] = len(catalog.get("principles", {}))
            info["principles"] = list(catalog.get("principles", {}).keys())
        
        return info
    
    def enable_framework(self, framework: NormativeFramework) -> None:
        """Aktiviert einen normativen Framework."""
        if framework not in self.enabled_frameworks:
            self.enabled_frameworks.append(framework)
    
    def disable_framework(self, framework: NormativeFramework) -> None:
        """Deaktiviert einen normativen Framework."""
        if framework in self.enabled_frameworks:
            self.enabled_frameworks.remove(framework)
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung der Compliance-Statistiken zurück."""
        return {
            "total_validations": self.stats["total_validations"],
            "violations_found": self.stats["violations_found"],
            "critical_violations": self.stats["critical_violations"],
            "compliance_rate": self.stats["compliance_rate"],
            "frameworks_checked": self.stats["frameworks_checked"],
            "enabled_frameworks": [f.value for f in self.enabled_frameworks],
            "average_checks_per_validation": (
                self.stats["frameworks_checked"] / max(1, self.stats["total_validations"])
            )
        }


# ============================================================================
# MODUL-SCHNITTSTELLE
# ============================================================================

# Globale NGA-Instanz
_nga_instance: Optional[NormativeGoalAlignment] = None

def _get_nga_instance(config: Optional[Dict[str, Any]] = None) -> NormativeGoalAlignment:
    """Lazy-Loading der NGA-Instanz."""
    global _nga_instance
    if _nga_instance is None or config is not None:
        _nga_instance = NormativeGoalAlignment(config)
    return _nga_instance


def run_module(input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardisierte Modul-Schnittstelle für INTEGRA.
    
    Args:
        input_text: Text-Eingabe zur Analyse
        context: Entscheidungskontext mit allen Modul-Ergebnissen
        
    Returns:
        Standardisiertes Ergebnis-Dictionary
    """
    if context is None:
        context = {}
    
    try:
        # NGA-Konfiguration aus Context
        nga_config = context.get("config", {}).get("nga", {})
        
        # NGA-Instanz
        nga = _get_nga_instance(nga_config)
        
        # Log Start
        if log_manager:
            log_manager.log_event(
                "NGA",
                f"Starte Norm-Validierung mit {len(nga.enabled_frameworks)} Frameworks",
                "INFO"
            )
        
        # Validierung durchführen
        validation_result = nga.validate_against_norms(input_text, context)
        
        # Speichere im Context
        context["nga_result"] = validation_result
        
        # Log Ergebnis
        if log_manager:
            log_manager.log_event(
                "NGA",
                f"Validierung abgeschlossen - Compliance: {validation_result['overall_compliance']:.2%}, "
                f"Violations: {len(validation_result['violations'])}, "
                f"Warnings: {len(validation_result['warnings'])}",
                "INFO"
            )
            
            if validation_result.get("escalation_required"):
                log_manager.log_event(
                    "NGA",
                    "ESKALATION ERFORDERLICH - Kritische Compliance-Verletzungen",
                    "CRITICAL"
                )
        
        return {
            "success": True,
            "result": validation_result,
            "module": "nga",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
    except Exception as e:
        error_msg = f"NGA error: {str(e)}"
        
        if log_manager:
            log_manager.log_event("NGA", error_msg, "ERROR")
        
        # Fehler-Fallback
        context["nga_result"] = {
            "error": True,
            "error_message": error_msg,
            "overall_compliance": 0.0,
            "overall_compliance_status": "error",
            "violations": [],
            "warnings": [],
            "frameworks_checked": [],
            "catalogs_checked": [],
            "escalation_required": False
        }
        
        return {
            "success": False,
            "error": error_msg,
            "module": "nga",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def demo():
    """Demonstriert die Verwendung des NGA-Moduls."""
    print("=== INTEGRA NGA (Normative Goal Alignment) Demo v2.0 ===")
    print("Standardisierte Baukasten-Integration\n")
    
    # Test-Profil
    test_profile = profiles.get_default_profile()
    
    # Test-Szenarien
    test_scenarios = [
        {
            "name": "Datenschutz-konform",
            "text": "Ich werde Ihre Daten nur mit Ihrer ausdrücklichen Einwilligung und nur für den angegebenen Zweck verwenden.",
            "context": {
                "profile": test_profile.copy(),
                "simple_ethics_result": {
                    "scores": {"integrity": 0.9, "governance": 0.85, "nurturing": 0.8},
                    "overall_score": 0.85,
                    "violations": []
                }
            }
        },
        {
            "name": "GDPR-Verletzung",
            "text": "Ich speichere alle Ihre persönlichen Daten dauerhaft für spätere Analysen.",
            "context": {
                "profile": test_profile.copy(),
                "simple_ethics_result": {
                    "scores": {"integrity": 0.3, "governance": 0.4, "nurturing": 0.5},
                    "overall_score": 0.4,
                    "violations": ["integrity", "governance"]
                },
                "response": "Das wäre nicht GDPR-konform..."
            }
        },
        {
            "name": "Diskriminierung",
            "text": "Personen bestimmter Herkunft werden anders behandelt.",
            "context": {
                "profile": test_profile.copy(),
                "simple_ethics_result": {
                    "scores": {"integrity": 0.2, "awareness": 0.3, "nurturing": 0.2},
                    "overall_score": 0.23,
                    "violations": ["integrity", "awareness", "nurturing"]
                }
            }
        },
        {
            "name": "Medizinethik mit Risiko",
            "text": "Als Behandlung empfehle ich dieses Verfahren, auch wenn es Risiken birgt.",
            "context": {
                "profile": test_profile.copy(),
                "simple_ethics_result": {
                    "scores": {"nurturing": 0.5, "integrity": 0.7, "awareness": 0.6},
                    "overall_score": 0.6,
                    "violations": []
                }
            }
        },
        {
            "name": "Komplexe Entscheidung mit mehreren Modulen",
            "text": "Wir entwickeln eine KI-basierte Lösung für Ihr Unternehmen",
            "context": {
                "profile": test_profile.copy(),
                "decision_context": {
                    "user_input": "Können Sie unsere Kundendaten analysieren?",
                    "response": "Ja, mit entsprechender Einwilligung und Zweckbindung."
                },
                "simple_ethics_result": {
                    "scores": {p: 0.75 for p in principles.ALIGN_KEYS},
                    "overall_score": 0.75
                },
                "etb_result": {
                    "conflicts_detected": False,
                    "trade_offs": {"governance": 0.8, "nurturing": 0.7}
                },
                "pae_result": {
                    "primary_anchor": "governance",
                    "secondary": "integrity"
                },
                "vdd_result": {
                    "drift_detected": False
                }
            }
        }
    ]
    
    # Konfiguration mit mehreren Frameworks
    config = {
        "nga": {
            "enabled_frameworks": [
                NormativeFramework.UN_HUMAN_RIGHTS.value,
                NormativeFramework.GDPR.value,
                NormativeFramework.MEDICAL_ETHICS.value,
                NormativeFramework.CORPORATE_ETHICS.value
            ],
            "strict_mode": True,
            "escalation_threshold": 0.5
        }
    }
    
    print("📋 Aktivierte Frameworks:")
    for fw in config["nga"]["enabled_frameworks"]:
        print(f"  - {fw}")
    print()
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*70}")
        print(f"Test {i+1}: {scenario['name']}")
        print(f"Eingabe: {scenario['text']}")
        
        # Context mit Konfiguration
        test_context = scenario["context"].copy()
        test_context["config"] = config
        
        # Führe NGA durch
        result = run_module(scenario["text"], test_context)
        
        if result["success"]:
            nga_result = result["result"]
            
            print(f"\n📊 Compliance-Ergebnis:")
            print(f"  Gesamt-Compliance: {nga_result['overall_compliance']:.2%}")
            print(f"  Status: {nga_result['overall_compliance_status']}")
            print(f"  Frameworks geprüft: {', '.join(nga_result['frameworks_checked'])}")
            
            if nga_result["violations"]:
                print(f"\n❌ Verletzungen ({len(nga_result['violations'])}):")
                for v in nga_result["violations"]:
                    print(f"  - [{v.get('severity', 'unknown')}] {v.get('framework', '')} - "
                          f"{v.get('title', '')}: {v.get('description', '')}")
            
            if nga_result["warnings"]:
                print(f"\n⚠️ Warnungen ({len(nga_result['warnings'])}):")
                for w in nga_result["warnings"]:
                    print(f"  - [{w.get('severity', 'unknown')}] {w.get('framework', '')} - "
                          f"{w.get('title', '')}: {w.get('description', '')}")
            
            if nga_result["recommendations"]:
                print(f"\n💡 Empfehlungen:")
                for r in nga_result["recommendations"]:
                    print(f"  - [{r.get('priority', 'unknown')}] {r.get('recommendation', '')}")
            
            if nga_result.get("escalation_required"):
                print(f"\n🚨 ESKALATION ERFORDERLICH!")
            
            # Context-Integration zeigen
            print(f"\n🔗 Context-Integration:")
            print(f"  NGA-Ergebnis im Context gespeichert: {'nga_result' in result['context']}")
            if "simple_ethics_result" in test_context:
                print(f"  Ethics-Scores genutzt: ✅")
            if any(key in test_context for key in ["etb_result", "pae_result", "vdd_result"]):
                print(f"  Andere Module integriert: ✅")
        else:
            print(f"\n❌ Fehler: {result['error']}")
    
    # Framework-Info demonstrieren
    print(f"\n\n{'='*70}")
    print("📚 Framework-Informationen:")
    
    nga = _get_nga_instance()
    for framework in [NormativeFramework.UN_HUMAN_RIGHTS, NormativeFramework.GDPR]:
        info = nga.get_framework_info(framework)
        print(f"\n{framework.value}:")
        print(f"  Aktiviert: {info['enabled']}")
        print(f"  Struktur: {', '.join(info['structure'])}")
        if "articles" in info:
            print(f"  Artikel: {len(info['articles'])}")
        if "principles" in info:
            print(f"  Prinzipien: {len(info['principles'])}")
    
    # Compliance-Zusammenfassung
    print(f"\n\n{'='*70}")
    print("📈 Compliance-Zusammenfassung:")
    
    summary = nga.get_compliance_summary()
    print(f"  Gesamt-Validierungen: {summary['total_validations']}")
    print(f"  Compliance-Rate: {summary['compliance_rate']:.2%}")
    print(f"  Verletzungen gefunden: {summary['violations_found']}")
    print(f"  Kritische Verletzungen: {summary['critical_violations']}")
    print(f"  Durchschn. Frameworks pro Prüfung: {summary['average_checks_per_validation']:.1f}")
    
    # Cache-Demo
    print(f"\n\n{'='*70}")
    print("⚡ Cache-Performance Test:")
    
    import time
    
    # Erste Ausführung
    start = time.time()
    result1 = run_module("Test-Text für Cache", {"config": config})
    time1 = time.time() - start
    
    # Zweite Ausführung (sollte gecacht sein)
    start = time.time()
    result2 = run_module("Test-Text für Cache", {"config": config})
    time2 = time.time() - start
    
    print(f"  Erste Ausführung: {time1:.3f}s")
    print(f"  Zweite Ausführung: {time2:.3f}s")
    print(f"  Speedup: {time1/time2:.1f}x" if time2 > 0 else "  Speedup: N/A")
    
    # Framework dynamisch ändern
    print(f"\n\n{'='*70}")
    print("🔧 Dynamische Framework-Verwaltung:")
    
    # Deaktiviere GDPR
    nga.disable_framework(NormativeFramework.GDPR)
    print(f"\n  GDPR deaktiviert")
    
    # Aktiviere ISO 26000
    nga.enable_framework(NormativeFramework.ISO_26000)
    print(f"  ISO 26000 aktiviert")
    
    print(f"\n  Aktive Frameworks: {[f.value for f in nga.enabled_frameworks]}")
    
    print("\n✅ NGA Demo v2.0 abgeschlossen!")
    print("\nDas Modul bietet:")
    print("  • Standardisierte Baukasten-Schnittstelle")
    print("  • Context-basierte Integration mit anderen Modulen")
    print("  • Lazy-Loading mit globaler Instanz")
    print("  • Nutzung von Ethics-Scores für bessere Validierung")
    print("  • Cache für Performance-Optimierung")
    print("  • Dynamische Framework-Verwaltung")


if __name__ == "__main__":
    demo()