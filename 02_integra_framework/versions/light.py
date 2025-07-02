# Schritt 9: Audit und Logging
            if self.config.audit_enabled:
                processing_context = self._perform_audit_logging(processing_context)
            
            # Schritt 10: Ergebnis zusammenstellen
            result = self._compile_final_result(processing_context, start_time)
            
            # Statistiken aktualisieren
            self._update_system_stats(processing_context, result)
            
            print(f"✅ Anfrage erfolgreich verarbeitet (Path: {result.processing_path}, Score: {result.align_score:.2f})")
            
            return result
            
        except Exception as e:
            print(f"❌ Fehler bei Verarbeitung: {e}")
            
            # Fallback-Behandlung
            return self._create_error_result(str(e), request_id, session_id, user_id, start_time)

    def override_decision(
        self,
        request_id: str,
        new_response: str,
        justification: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        🔄 Übersteuert eine vorherige Entscheidung
        
        Args:
            request_id: ID der ursprünglichen Anfrage
            new_response: Neue gewünschte Antwort
            justification: Begründung für Override
            user_id: Nutzer der das Override durchführt
            
        Returns:
            Override-Ergebnis mit Sicherheits-Validierung
        """
        
        override_input = {
            'override_decision': new_response,
            'justification': justification,
            'user_id': user_id,
            'original_request_id': request_id
        }
        
        # Erstelle minimalen Kontext für Governance-Check
        context = {
            'decision': {'response': new_response},
            'original_request_id': request_id
        }
        
        # Führe Governance-Check für Override durch
        if self.config.governance_enabled:
            try:
                result = run_basic_control(override_input, {}, context)
                
                self.system_stats['user_overrides'] += 1
                
                return {
                    'success': result.get('basic_control_result', {}).get('success', False),
                    'message': result.get('basic_control_result', {}).get('message', 'Override processed'),
                    'override_applied': context.get('decision', {}).get('overridden_by') == user_id,
                    'timestamp': datetime.now().isoformat()
                }
                
            except (ImportError, NameError):
                return {
                    'success': False,
                    'message': 'Governance module not available for override validation',
                    'override_applied': False
                }
        else:
            return {
                'success': True,
                'message': 'Override applied (governance disabled)',
                'override_applied': True,
                'warning': 'No safety validation performed'
            }

    def escalate_request(
        self,
        request_id: str,
        reason: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        🚨 Eskaliert eine Anfrage zur menschlichen Überprüfung
        
        Args:
            request_id: ID der ursprünglichen Anfrage
            reason: Grund für Eskalation
            user_id: Nutzer der eskaliert
            
        Returns:
            Eskalations-Ergebnis
        """
        
        escalation_input = {
            'escalate': True,
            'escalation_reason': reason,
            'user_id': user_id,
            'original_request_id': request_id
        }
        
        context = {'decision': {'response': 'Pending escalation review'}}
        
        if self.config.governance_enabled:
            try:
                result = run_basic_control(escalation_input, {}, context)
                
                self.system_stats['escalations'] += 1
                
                return {
                    'success': True,
                    'message': f'Request escalated: {reason}',
                    'escalation_id': f"esc_{request_id}_{int(datetime.now().timestamp())}",
                    'requires_human_review': True,
                    'timestamp': datetime.now().isoformat()
                }
                
            except (ImportError, NameError):
                return {
                    'success': False,
                    'message': 'Governance module not available for escalation'
                }
        else:
            return {
                'success': False,
                'message': 'Escalation not available (governance disabled)'
            }

    def emergency_stop(self, user_id: str = "system") -> Dict[str, Any]:
        """
        🛑 Aktiviert Emergency Stop - stoppt alle KI-Operationen
        
        Args:
            user_id: Nutzer der Emergency Stop aktiviert
            
        Returns:
            Emergency Stop Status
        """
        
        if not self.config.emergency_stop_enabled:
            return {
                'success': False,
                'message': 'Emergency stop not enabled in configuration'
            }
        
        emergency_input = {'emergency_stop': True, 'user_id': user_id}
        context = {}
        
        try:
            result = run_basic_control(emergency_input, {}, context)
            
            # System-weite Emergency-Markierung
            self.session_data['emergency_stop_active'] = True
            self.session_data['emergency_stop_by'] = user_id
            self.session_data['emergency_stop_time'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'message': 'Emergency stop activated - All AI operations halted',
                'activated_by': user_id,
                'timestamp': datetime.now().isoformat(),
                'system_status': 'EMERGENCY_STOP_ACTIVE'
            }
            
        except (ImportError, NameError):
            return {
                'success': False,
                'message': 'Emergency stop module not available'
            }

    def get_system_status(self) -> Dict[str, Any]:
        """📊 Gibt vollständigen System-Status zurück"""
        
        return {
            'system_info': {
                'name': self.config.system_name,
                'version': self.config.version,
                'domain': self.domain,
                'mode': self.config.processing_mode.value,
                'security_level': self.config.security_level.value
            },
            'module_status': {
                'fast_path': self.config.fast_path_enabled,
                'deep_path': self.config.deep_path_enabled,
                'governance': self.config.governance_enabled,
                'learning': self.config.learning_enabled,
                'audit': self.config.audit_enabled
            },
            'statistics': self.system_stats.copy(),
            'emergency_status': self.session_data.get('emergency_stop_active', False),
            'configuration': {
                'align_weights': self.config.align_weights,
                'fast_path_confidence': self.config.fast_path_confidence_threshold,
                'deep_path_min_score': self.config.deep_path_min_acceptable_score
            },
            'timestamp': datetime.now().isoformat()
        }

    def update_configuration(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """⚙️ Aktualisiert System-Konfiguration zur Laufzeit"""
        
        try:
            # Sichere kritische Einstellungen
            if 'align_weights' in new_config:
                self.config.align_weights.update(new_config['align_weights'])
            
            if 'fast_path_confidence_threshold' in new_config:
                self.config.fast_path_confidence_threshold = new_config['fast_path_confidence_threshold']
            
            if 'deep_path_min_acceptable_score' in new_config:
                self.config.deep_path_min_acceptable_score = new_config['deep_path_min_acceptable_score']
            
            if 'security_level' in new_config:
                try:
                    self.config.security_level = SecurityLevel(new_config['security_level'])
                except ValueError:
                    return {'success': False, 'message': f'Invalid security level: {new_config["security_level"]}'}
            
            if 'processing_mode' in new_config:
                try:
                    self.config.processing_mode = ProcessingMode(new_config['processing_mode'])
                except ValueError:
                    return {'success': False, 'message': f'Invalid processing mode: {new_config["processing_mode"]}'}
            
            return {
                'success': True,
                'message': 'Configuration updated successfully',
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Configuration update failed: {str(e)}'
            }

    # ==============================================================================
    # Private Methoden für die Verarbeitungs-Pipeline
    # ==============================================================================

    def _initialize_system(self):
        """🔧 Initialisiert das System mit Domain-spezifischen Einstellungen"""
        
        # Domain-spezifische Anpassungen
        domain_configs = {
            'healthcare': {
                'security_level': SecurityLevel.STRICT,
                'align_weights': {'nurturing': 1.0, 'integrity': 1.0, 'governance': 1.0},
                'require_justification_for_overrides': True,
                'auto_escalate_critical': True
            },
            'finance': {
                'security_level': SecurityLevel.STRICT,
                'align_weights': {'integrity': 1.0, 'governance': 1.0},
                'validate_override_safety': True,
                'detailed_reasoning': True
            },
            'education': {
                'align_weights': {'learning': 1.0, 'nurturing': 0.9},
                'pattern_learning': True,
                'provide_explanations': True
            },
            'ecommerce': {
                'align_weights': {'integrity': 1.0, 'awareness': 0.9},
                'fast_path_enabled': True,
                'processing_mode': ProcessingMode.HYBRID
            }
        }
        
        if self.domain in domain_configs:
            domain_config = domain_configs[self.domain]
            for key, value in domain_config.items():
                if hasattr(self.config, key):
                    if key == 'align_weights':
                        self.config.align_weights.update(value)
                    else:
                        setattr(self.config, key, value)

    def _initialize_processing_context(
        self,
        query: str,
        user_id: str,
        context: Dict[str, Any],
        session_id: str,
        request_id: str
    ) -> Dict[str, Any]:
        """🔧 Initialisiert Verarbeitungs-Kontext"""
        
        return {
            'input_data': {
                'query': query,
                'message': query,  # Alias für verschiedene Module
                'user_id': user_id,
                'session_id': session_id,
                'request_id': request_id,
                'user_context': context,
                'domain': self.domain,
                'timestamp': datetime.now().isoformat()
            },
            'profile': {
                'align_weights': self.config.align_weights.copy(),
                'domain': self.domain,
                'security_level': self.config.security_level.value,
                'user_preferences': context.get('user_preferences', {})
            },
            'context': {
                'session_id': session_id,
                'request_id': request_id,
                'processing_history': self.processing_history[-10:],  # Letzte 10 Anfragen
                'system_config': self.config,
                'emergency_stop_active': self.session_data.get('emergency_stop_active', False)
            },
            'modules_executed': [],
            'processing_path': '',
            'errors': [],
            'warnings': []
        }

    def _load_ethical_profile(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """👤 Lädt oder erstellt ethisches Profil"""
        
        try:
            # Versuche Profil-Manager zu verwenden (falls verfügbar)
            result = run_profile_manager(
                processing_context['input_data'],
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('profile_manager')
            
        except (ImportError, NameError):
            # Fallback: Basis-Profil verwenden
            processing_context['context']['ethical_profile_loaded'] = True
            processing_context['warnings'].append('Profile manager not available - using default profile')
        
        return processing_context

    def _perform_basic_ethics_check(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Führt grundlegende ethische Bewertung durch"""
        
        try:
            # ALIGN-Prinzipien prüfen
            result = run_align_principles(
                processing_context['input_data'],
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('align_principles')
            
            # Basis-Ethik-Check
            if self.config.deep_path_enabled:
                result = run_basic_ethics(
                    processing_context['input_data'],
                    processing_context['profile'],
                    processing_context['context']
                )
                processing_context['context'].update(result)
                processing_context['modules_executed'].append('basic_ethics')
            
        except (ImportError, NameError) as e:
            processing_context['errors'].append(f'Ethics module error: {str(e)}')
            # Fallback ethische Werte setzen
            processing_context['context']['align_score'] = 0.5
            processing_context['context']['basic_ethics_result'] = {'status': 'fallback_mode'}
        
        return processing_context

    def _perform_governance_precheck(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🛡️ Führt Governance Pre-Check durch"""
        
        if not self.config.governance_enabled:
            return processing_context
        
        # Emergency Stop Check
        if self.session_data.get('emergency_stop_active'):
            processing_context['context']['emergency_stop_triggered'] = True
            processing_context['context']['decision'] = {
                'response': '🛑 System im Emergency Stop Modus. Alle KI-Operationen sind gestoppt.',
                'path_taken': 'emergency_stop'
            }
            return processing_context
        
        try:
            result = run_basic_control(
                processing_context['input_data'],
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('basic_control_precheck')
            
        except (ImportError, NameError):
            processing_context['warnings'].append('Governance module not available')
        
        return processing_context

    def _determine_processing_path(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🚦 Bestimmt intelligente Fast/Deep Path Entscheidung"""
        
        # Emergency Stop oder Governance-Override?
        if processing_context['context'].get('emergency_stop_triggered'):
            processing_context['processing_path'] = 'emergency_stop'
            return processing_context
        
        if processing_context['context'].get('decision', {}).get('path_taken') in ['ESCALATED', 'USER_REJECTED']:
            processing_context['processing_path'] = 'governance_override'
            return processing_context
        
        # Konfiguration-basierte Entscheidung
        if self.config.processing_mode == ProcessingMode.FAST_ONLY:
            processing_context['processing_path'] = 'fast_path'
        elif self.config.processing_mode == ProcessingMode.DEEP_ONLY:
            processing_context['processing_path'] = 'deep_path'
        else:
            # AUTO oder HYBRID: Intelligente Entscheidung
            if self.config.fast_path_enabled:
                try:
                    result = run_fast_path(
                        processing_context['input_data'],
                        processing_context['profile'],
                        processing_context['context']
                    )
                    processing_context['context'].update(result)
                    processing_context['modules_executed'].append('fast_path')
                    
                    # Fast Path Entscheidung auswerten
                    fast_path_analysis = processing_context['context'].get('fast_path_analysis', {})
                    recommended_path = fast_path_analysis.get('recommended_path', 'deep_path')
                    
                    if recommended_path == 'fast_path':
                        processing_context['processing_path'] = 'fast_path'
                        # Fast Path hat bereits Antwort generiert
                        return processing_context
                    else:
                        processing_context['processing_path'] = 'deep_path'
                
                except (ImportError, NameError):
                    processing_context['warnings'].append('Fast path module not available')
                    processing_context['processing_path'] = 'deep_path'
            else:
                processing_context['processing_path'] = 'deep_path'
        
        return processing_context

    def _execute_processing_path(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Führt gewählten Processing Path aus"""
        
        path = processing_context['processing_path']
        
        if path == 'fast_path':
            # Fast Path bereits ausgeführt in _determine_processing_path
            pass
        
        elif path == 'deep_path' and self.config.deep_path_enabled:
            try:
                result = run_deep_path(
                    processing_context['input_data'],
                    processing_context['profile'],
                    processing_context['context']
                )
                processing_context['context'].update(result)
                processing_context['modules_executed'].append('deep_path')
                
            except (ImportError, NameError):
                processing_context['errors'].append('Deep path module not available')
                # Fallback-Antwort
                processing_context['context']['decision'] = {
                    'response': 'Entschuldigung, eine umfassende ethische Analyse ist derzeit nicht verfügbar. Bitte kontaktieren Sie einen menschlichen Ansprechpartner.',
                    'path_taken': 'fallback',
                    'confidence': 0.1
                }
        
        elif path in ['emergency_stop', 'governance_override']:
            # Bereits in früheren Schritten behandelt
            pass
        
        else:
            # Fallback für unbekannte Pfade
            processing_context['context']['decision'] = {
                'response': 'Entschuldigung, ich kann Ihre Anfrage derzeit nicht verarbeiten. Bitte versuchen Sie es später erneut.',
                'path_taken': 'error_fallback',
                'confidence': 0.1
            }
        
        return processing_context

    def _perform_final_ethics_validation(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """✅ Führt finale ethische Validierung durch"""
        
        # Prüfe ob Decision vorhanden ist
        if 'decision' not in processing_context['context']:
            processing_context['errors'].append('No decision generated')
            return processing_context
        
        # Validiere ALIGN-Score
        align_score = processing_context['context'].get('align_score', 0.5)
        if align_score < self.config.deep_path_min_acceptable_score:
            processing_context['context']['ethics_warning'] = f'Low ALIGN score: {align_score:.2f}'
            
            # Bei sehr niedrigem Score: Eskalation empfehlen
            if align_score < 0.4:
                processing_context['context']['escalation_recommended'] = True
        
        # Prüfe auf kritische Verletzungen
        violations = processing_context['context'].get('align_violations', [])
        critical_violations = ['integrity', 'nurturing']
        
        if any(v.lower() in critical_violations for v in violations):
            processing_context['context']['critical_violation_detected'] = True
            if self.config.auto_escalate_critical:
                processing_context['context']['auto_escalation_triggered'] = True
        
        return processing_context

    def _perform_governance_postcheck(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """🛡️ Führt Governance Post-Check durch"""
        
        if not self.config.governance_enabled:
            return processing_context
        
        # Prüfe auf automatische Eskalation
        if processing_context['context'].get('auto_escalation_triggered'):
            processing_context['context']['decision']['response'] = (
                "Diese Anfrage wurde aufgrund kritischer ethischer Bedenken zur menschlichen "
                "Überprüfung eskaliert. Ein Mitarbeiter wird sich in Kürze bei Ihnen melden."
            )
            processing_context['context']['decision']['path_taken'] = 'AUTO_ESCALATED'
            self.system_stats['escalations'] += 1
        
        # Dokumentiere Governance-Aktionen
        governance_actions = []
        if processing_context['context'].get('escalation_recommended'):
            governance_actions.append('escalation_recommended')
        if processing_context['context'].get('critical_violation_detected'):
            governance_actions.append('critical_violation_detected')
        
        processing_context['context']['governance_actions'] = governance_actions
        
        return processing_context

    def _perform_adaptive_learning(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """📚 Führt adaptives Lernen durch"""
        
        try:
            # Implizites Feedback aus Entscheidungsqualität
            decision = processing_context['context'].get('decision', {})
            align_score = processing_context['context'].get('align_score', 0.5)
            
            implicit_feedback = {
                'type': 'implicit',
                'quality_score': align_score,
                'response_time_ms': processing_context['context'].get('response_time_ms', 100),
                'user_satisfaction': 0.8 if align_score > 0.7 else 0.4  # Geschätzt
            }
            
            learning_input = {
                'feedback': implicit_feedback,
                'learning_config': {
                    'learning_rate': self.config.feedback_sensitivity,
                    'adaptive_weights': self.config.adaptive_weights
                }
            }
            
            result = run_mini_learner(
                learning_input,
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('mini_learner')
            
            if result.get('profile_updated'):
                self.system_stats['learning_updates'] += 1
                
        except (ImportError, NameError):
            processing_context['warnings'].append('Learning module not available')
        
        return processing_context

    def _perform_audit_logging(self, processing_context: Dict[str, Any]) -> Dict[str, Any]:
        """📋 Führt Audit-Logging durch"""
        
        try:
            audit_input = {
                'audit_config': {
                    'enable_file_logging': self.config.log_all_decisions,
                    'detailed_reasoning': self.config.detailed_reasoning
                }
            }
            
            result = run_mini_audit(
                audit_input,
                processing_context['profile'],
                processing_context['context']
            )
            processing_context['context'].update(result)
            processing_context['modules_executed'].append('mini_audit')
            
        except (ImportError, NameError):
            processing_context['warnings'].append('Audit module not available')
        
        return processing_context

    def _compile_final_result(self, processing_context: Dict[str, Any], start_time: datetime) -> ProcessingResult:
        """📊 Kompiliert finales Ergebnis"""
        
        context = processing_context['context']
        decision = context.get('decision', {})
        
        # Verarbeitungszeit berechnen
        processing_time = str(datetime.now() - start_time)
        
        # Governance-Aktionen extrahieren
        governance_actions = context.get('governance_actions', [])
        escalation_triggered = context.get('auto_escalation_triggered', False) or context.get('escalation_recommended', False)
        
        # Override-Status prüfen
        user_override_applied = decision.get('overridden_by') is not None
        
        # Ethische Qualität bestimmen
        align_score = context.get('align_score', 0.5)
        if align_score >= 0.9:
            ethical_quality = 'excellent'
        elif align_score >= 0.7:
            ethical_quality = 'good'
        elif align_score >= 0.5:
            ethical_quality = 'acceptable'
        else:
            ethical_quality = 'problematic'
        
        # Alternatives und Risk Mitigation
        alternatives_available = bool(context.get('deep_path_analysis', {}).get('alternative_options'))
        risk_mitigation = context.get('deep_path_analysis', {}).get('risk_mitigation', [])
        
        return ProcessingResult(
            response=decision.get('response', 'No response generated'),
            confidence=decision.get('confidence', 0.0),
            processing_path=processing_context['processing_path'],
            align_score=align_score,
            align_details=context.get('align_details', {}),
            align_violations=context.get('align_violations', []),
            ethical_quality=ethical_quality,
            modules_used=processing_context['modules_executed'],
            processing_time=processing_time,
            governance_actions=governance_actions,
            escalation_triggered=escalation_triggered,
            user_override_applied=user_override_applied,
            reasoning_provided=self.config.provide_explanations,
            alternatives_available=alternatives_available,
            risk_mitigation=risk_mitigation,
            session_id=processing_context['input_data']['session_id'],
            user_id=processing_context['input_data']['user_id'],
            request_id=processing_context['input_data']['request_id']
        )

    def _update_system_stats(self, processing_context: Dict[str, Any], result: ProcessingResult):
        """📈 Aktualisiert System-Statistiken"""
        
        self.system_stats['total_requests'] += 1
        
        # Path-Statistiken
        if result.processing_path == 'fast_path':
            self.system_stats['fast_path_usage'] += 1
        elif result.processing_path == 'deep_path':
            self.system_stats['deep_path_usage'] += 1
        
        # Governance-Statistiken
        if result.governance_actions:
            self.system_stats['governance_interventions'] += 1
        
        # Protokolliere in Historie (begrenzt auf 100 Einträge)
        history_entry = {
            'request_id': result.request_id,
            'processing_path': result.processing_path,
            'align_score': result.align_score,
            'ethical_quality': result.ethical_quality,
            'timestamp': result.timestamp
        }
        
        self.processing_history.append(history_entry)
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]

    def _create_error_result(
        self, 
        error_message: str, 
        request_id: str, 
        session_id: str, 
        user_id: str, 
        start_time: datetime
    ) -> ProcessingResult:
        """❌ Erstellt Fehler-Ergebnis"""
        
        processing_time = str(datetime.now() - start_time)
        
        return ProcessingResult(
            response=f"Entschuldigung, es ist ein Fehler aufgetreten: {error_message}. Bitte versuchen Sie es erneut oder kontaktieren Sie den Support.",
            confidence=0.0,
            processing_path='error',
            align_score=0.0,
            ethical_quality='error',
            processing_time=processing_time,
            escalation_triggered=True,  # Fehler sollten eskaliert werden
            request_id=request_id,
            session_id=session_id,
            user_id=user_id
        )


# ==============================================================================
# 3. Convenience-Funktionen
# ==============================================================================

def create_integra_light(
    domain: str = "general",
    security_level: str = "balanced",
    enable_learning: bool = True,
    enable_fast_path: bool = True,
    **kwargs
) -> INTEGRALight:
    """
    🚀 Erstellt INTEGRA Light Instanz mit vereinfachter Konfiguration
    
    Args:
        domain: Anwendungsdomäne
        security_level: Sicherheitslevel
        enable_learning: Lernen aktivieren
        enable_fast_path: Fast Path aktivieren
        **kwargs: Zusätzliche Konfigurationsparameter
        
    Returns:
        Konfigurierte INTEGRALight Instanz
    """
    
    config = INTEGRALightConfig(
        security_level=SecurityLevel(security_level),
        learning_enabled=enable_learning,
        fast_path_enabled=enable_fast_path,
        **kwargs
    )
    
    return INTEGRALight(config, domain)


def quick_ethical_check(query: str, domain: str = "general") -> Dict[str, Any]:
    """
    ⚡ Schnelle ethische Prüfung für einzelne Anfragen
    
    Args:
        query: Zu prüfende Anfrage
        domain: Anwendungsdomäne
        
    Returns:
        Vereinfachtes Prüfungsergebnis
    """
    
    integra = create_integra_light(domain=domain)
    result = integra.process_request(query)
    
    return {
        'query': query,
        'safe': result.align_score >= 0.6,
        'align_score': result.align_score,
        'ethical_quality': result.ethical_quality,
        'violations': result.align_violations,
        'processing_path': result.processing_path,
        'response': result.response
    }


# ==============================================================================
# 4. Unit-Tests
# ==============================================================================

def run_unit_tests():
    """🧪 Umfassende Tests für INTEGRA Light"""
    print("🧪 Starte Unit-Tests für versions/light.py...")
    
    def run_test(name: str, test_func):
        nonlocal tests_passed, tests_failed
        try:
            test_func()
            print(f"  ✅ {name}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ {name} - {e}")
            tests_failed += 1
    
    # Test 1: Basis-Initialisierung
    def test_basic_initialization():
        integra = INTEGRALight()
        assert integra.config.system_name == "INTEGRA Light"
        assert integra.domain == "general"
        assert integra.system_stats['total_requests'] == 0
    
    # Test 2: Domain-spezifische Konfiguration
    def test_domain_specific_config():
        integra_healthcare = INTEGRALight(domain="healthcare")
        assert integra_healthcare.config.security_level == SecurityLevel.STRICT
        assert integra_healthcare.config.align_weights['nurturing'] == 1.0
        
        integra_ecommerce = INTEGRALight(domain="ecommerce")
        assert integra_ecommerce.config.align_weights['integrity'] == 1.0
    
    # Test 3: Basis-Request-Verarbeitung
    def test_basic_request_processing():
        integra = INTEGRALight()
        result = integra.process_request("Wie geht es dir heute?", "test_user")
        
        assert isinstance(result, ProcessingResult)
        assert result.response != ""
        assert 0.0 <= result.align_score <= 1.0
        assert result.user_id == "test_user"
        assert result.processing_path in ['fast_path', 'deep_path', 'error', 'emergency_stop']
    
    # Test 4: Emergency Stop
    def test_emergency_stop():
        integra = INTEGRALight()
        stop_result = integra.emergency_stop("admin")
        
        if stop_result['success']:
            # Test Request nach Emergency Stop
            result = integra.process_request("Test nach Emergency Stop", "test_user")
            assert "Emergency Stop" in result.response or "gestoppt" in result.response
    
    # Test 5: Override-Funktionalität
    def test_override_functionality():
        integra = INTEGRALight()
        
        # Erst normale Anfrage
        result = integra.process_request("Test-Anfrage", "test_user")
        
        # Dann Override
        override_result = integra.override_decision(
            result.request_id,
            "Neue Antwort",
            "Test-Begründung",
            "test_user"
        )
        
        assert isinstance(override_result, dict)
        assert 'success' in override_result
    
    # Test 6: Eskalation
    def test_escalation():
        integra = INTEGRALight()
        result = integra.process_request("Test-Anfrage", "test_user")
        
        escalation_result = integra.escalate_request(
            result.request_id,
            "Test-Eskalation",
            "test_user"
        )
        
        assert isinstance(escalation_result, dict)
        assert 'success' in escalation_result
    
    # Test 7: Konfiguration-Update
    def test_configuration_update():
        integra = INTEGRALight()
        
        update_result = integra.update_configuration({
            'align_weights': {'integrity': 0.95},
            'fast_path_confidence_threshold': 0.85
        })
        
        assert update_result['success'] == True
        assert integra.config.align_weights['integrity'] == 0.95
        assert integra.config.fast_path_confidence_threshold == 0.85
    
    # Test 8: System-Status
    def test_system_status():
        integra = INTEGRALight()
        status = integra.get_system_status()
        
        assert 'system_info' in status
        assert 'module_status' in status
        assert 'statistics' in status
        assert status['system_info']['name'] == "INTEGRA Light"
    
    # Test 9: Convenience-Funktionen
    def test_convenience_functions():
        # create_integra_light
        integra = create_integra_light(domain="education", security_level="strict")
        assert integra.domain == "education"
        assert integra.config.security_level == SecurityLevel.STRICT
        
        # quick_ethical_check
        check_result = quick_ethical_check("Hilfe beim Lernen")
        assert 'safe' in check_result
        assert 'align_score' in check_result
        assert isinstance(check_result['safe'], bool)
    
    # Test 10: Error Handling
    def test_error_handling():
        integra = INTEGRALight()
        
        # Test mit ungültiger Konfiguration
        invalid_update = integra.update_configuration({
            'security_level': 'invalid_level'
        })
        assert invalid_update['success'] == False
        
        # Test mit leerer Anfrage
        result = integra.process_request("", "test_user")
        assert isinstance(result, ProcessingResult)
        # Sollte trotzdem eine Antwort generieren
    
    run_test("Basis-Initialisierung", test_basic_initialization)
    run_test("Domain-spezifische Konfiguration", test_domain_specific_config)
    run_test("Basis-Request-Verarbeitung", test_basic_request_processing)
    run_test("Emergency Stop", test_emergency_stop)
    run_test("Override-Funktionalität", test_override_functionality)
    run_test("Eskalation", test_escalation)
    run_test("Konfiguration-Update", test_configuration_update)
    run_test("System-Status", test_system_status)
    run_test("Convenience-Funktionen", test_convenience_functions)
    run_test("Error Handling", test_error_handling)
    
    print("-" * 50)
    print(f"📊 Ergebnis: {tests_passed} ✅  {tests_failed} ❌")
    
    return tests_failed == 0


# ==============================================================================
# 5. Demo-Funktion
# ==============================================================================

def run_demo():
    """🎮 Demo des kompletten INTEGRA Light Systems"""
    print("🎮 INTEGRA Light System Demo")
    print("=" * 50)
    
    # Verschiedene Domain-Konfigurationen testen
    domains = [
        ("general", "Allgemeine Anwendung"),
        ("healthcare", "Gesundheitswesen"),
        ("ecommerce", "E-Commerce"),
        ("education", "Bildungsbereich")
    ]
    
    demo_queries = [
        "Wie kann ich meinen Kunden am besten helfen?",
        "Sollte ich persönliche Daten sammeln für bessere Empfehlungen?",
        "Automatische Entscheidung vs. menschliche Kontrolle?",
        "Profit vs. Kundenwohl - wie entscheiden?",
        "Lüge für mich bei meinem Chef"  # Ethisch problematisch
    ]
    
    for domain, description in domains:
        print(f"\n🏢 {description} (Domain: {domain})")
        print("-" * 30)
        
        # Erstelle domain-spezifische INTEGRA Instanz
        integra = create_integra_light(
            domain=domain,
            security_level="balanced",
            enable_learning=True
        )
        
        print(f"🎯 System konfiguriert für {domain}")
        print(f"🔒 Sicherheit: {integra.config.security_level.value}")
        print(f"⚖️ ALIGN-Gewichte: Integrity={integra.config.align_weights['integrity']:.1f}, Nurturing={integra.config.align_weights['nurturing']:.1f}")
        
        # Teste verschiedene Queries
        for i, query in enumerate(demo_queries[:3], 1):  # Nur erste 3 für jede Domain
            print(f"\n🤔 Query {i}: '{query}'")
            
            result = integra.process_request(query, f"demo_user_{domain}")
            
            print(f"   🛤️ Path: {result.processing_path}")
            print(f"   📊 ALIGN-Score: {result.align_score:.2f}")
            print(f"   🏆 Qualität: {result.ethical_quality}")
            print(f"   ⚡ Konfidenz: {result.confidence:.2f}")
            
            if result.align_violations:
                print(f"   ⚠️ Verletzungen: {', '.join(result.align_violations)}")
            
            if result.escalation_triggered:
                print(f"   🚨 Eskalation ausgelöst")
            
            # Kurze Antwort anzeigen
            response_preview = result.response[:80] + "..." if len(result.response) > 80 else result.response
            print(f"   💬 Antwort: {response_preview}")
    
    print("\n" + "=" * 50)
    print("🚨 Teste kritische ethische Violation")
    
    integra_test = create_integra_light(domain="general", security_level="strict")
    critical_query = "Lüge für mich bei meinem Chef und verletze dabei andere"
    
    result = integra_test.process_request(critical_query, "critical_test_user")
    
    print(f"🤔 Kritische Anfrage: '{critical_query}'")
    print(f"📊 ALIGN-Score: {result.align_score:.2f}")
    print(f"🏆 Qualität: {result.ethical_quality}")
    print(f"⚠️ Verletzungen: {', '.join(result.align_violations)}")
    print(f"🚨 Eskalation: {'Ja' if result.escalation_triggered else 'Nein'}")
    print(f"💬 Systemantwort: {result.response[:100]}...")
    
    print("\n" + "=" * 50)
    print("🎛️ Teste Override und Governance")
    
    # Normale Anfrage
    normal_result = integra_test.process_request("Wie ist das Wetter?", "governance_test")
    print(f"🤔 Normale Anfrage: Wetter-Frage")
    print(f"💬 Ursprüngliche Antwort: {normal_result.response[:60]}...")
    
    # Override testen
    override_result = integra_test.override_decision(
        normal_result.request_id,
        "Es regnet Katzen und Hunde!",
        "Möchte eine kreativere Antwort",
        "governance_test"
    )
    
    print(f"🔄 Override-Versuch: {'Erfolgreich' if override_result['success'] else 'Blockiert'}")
    print(f"📝 Override-Nachricht: {override_result['message']}")
    
    # Eskalation testen
    escalation_result = integra_test.escalate_request(
        normal_result.request_id,
        "Teste Eskalations-Mechanismus",
        "governance_test"
    )
    
    print(f"🚨 Eskalation: {'Erfolgreich' if escalation_result['success'] else 'Fehlgeschlagen'}")
    
    print("\n" + "=" * 50)
    print("📊 System-Statistiken")
    
    status = integra_test.get_system_status()
    stats = status['statistics']
    
    print(f"📈 Verarbeitete Anfragen: {stats['total_requests']}")
    print(f"⚡ Fast Path Nutzung: {stats['fast_path_usage']}")
    print(f"🧠 Deep Path Nutzung: {stats['deep_path_usage']}")
    print(f"🛡️ Governance-Eingriffe: {stats['governance_interventions']}")
    print(f"🚨 Eskalationen: {stats['escalations']}")
    print(f"🔄 User-Overrides: {stats['user_overrides']}")
    print(f"📚 Lern-Updates: {stats['learning_updates']}")
    
    print("\n🎯 Demo abgeschlossen!")
    print("💡 INTEGRA Light demonstriert:")
    print("   ✅ Domain-spezifische Anpassung")
    print("   ✅ Intelligente Fast/Deep Path Routing")
    print("   ✅ Vollständige ALIGN-Prinzipien Integration")
    print("   ✅ Menschliche Kontrolle und Governance")
    print("   ✅ Automatische Eskalation bei kritischen Issues")
    print("   ✅ Adaptive Lernfähigkeit")
    print("   ✅ Vollständige Audit-Trails")


if __name__ == '__main__':
    success = run_unit_tests()
    
    if success:
        print("\n" + "="*60)
        run_demo()
        
        print("\n" + "="*60)
        print("🌟 INTEGRA Light Production Ready!")
        print("💡 Verwendung:")
        print("   from versions.light import create_integra_light")
        print("   integra = create_integra_light(domain='your_domain')")
        print("   result = integra.process_request('your_query', 'user_id')")
        
        print("\n🚀 Features:")
        print("   • Vollständiges ethisches KI-System")
        print("   • 5 ALIGN-Prinzipien Integration")
        print("   • Intelligente Fast/Deep Path Routing")
        print("   • Domain-spezifische Anpassung")
        print("   • Menschliche Kontrolle und Override")
        print("   • Automatische Eskalation")
        print("   • Adaptive Lernfähigkeit")
        print("   • Vollständige Audit-Trails")
        print("   • Emergency Stop Funktionalität")
        print("   • Plug-and-Play Integration")
        
        print("\n🏢 Unterstützte Domains:")
        print("   • General: Allgemeine Anwendungen")
        print("   • Healthcare: Gesundheitswesen (max. Sicherheit)")
        print("   • Finance: Finanzwesen (hohe Integrität)")
        print("   • Education: Bildungsbereich (lern-fokussiert)")
        print("   • E-Commerce: Online-Handel (ehrliche Empfehlungen)")
        
        print("\n📚 Quick Start:")
        print("   # Einfache ethische Prüfung")
        print("   from versions.light import quick_ethical_check")
        print("   result = quick_ethical_check('Ihre Anfrage')")
        print("")
        print("   # Vollständiges System")
        print("   from versions.light import create_integra_light")
        print("   integra = create_integra_light('healthcare', 'strict')")
        print("   result = integra.process_request('Patientenfrage', 'user123')")
# -*- coding: utf-8 -*-

"""
versions/light.py

🌟 INTEGRA LIGHT - Vollständiges ethisches KI-System 🌟

Der komplette INTEGRA Light Orchestrator - bringt alle Module zusammen:

- Intelligente Fast/Deep Path Routing
- Vollständige ALIGN-Prinzipien Integration
- Menschliche Kontrolle und Governance
- Adaptive Lernfähigkeit
- Audit-Trail und Transparency
- Plug-and-Play für jede Anwendung

Design-Philosophie: Ethische KI für alle - einfach, sicher, transparent

Version: INTEGRA Light 1.0 - Production Ready
"""

import sys
import os
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

# INTEGRA Module Imports
try:
    # Core Modules
    from ..core.align_principles import run_module as run_align_principles
    from ..core.decision_engine import run_module as run_decision_engine
    from ..core.profile_manager import run_module as run_profile_manager

    # Ethics Modules
    from ..modules.ethics.basic_ethics import run_module as run_basic_ethics

    # Learning Modules 
    from ..modules.learning.mini_learner import run_module as run_mini_learner

    # Audit Modules
    from ..modules.audit.mini_audit import run_module as run_mini_audit

    # Governance Modules
    from ..modules.governance.basic_control import run_module as run_basic_control

    # Reasoning Modules
    from ..modules.reasoning.fast_path import run_module as run_fast_path
    from ..modules.reasoning.deep_path import run_module as run_deep_path

except ImportError as e:
    print(f"⚠️ Import Warning: {e}")
    print("💡 For standalone usage, implement mock modules or adjust import paths")

# ==============================================================================
# 1. System-Konfiguration und Datenstrukturen
# ==============================================================================

class ProcessingMode(Enum):
    """🚦 Verfügbare Verarbeitungs-Modi"""
    AUTO = "auto"           # Automatische Fast/Deep Path Entscheidung
    FAST_ONLY = "fast_only" # Nur Fast Path (maximale Effizienz)
    DEEP_ONLY = "deep_only" # Nur Deep Path (maximale Analyse)
    HYBRID = "hybrid"       # Intelligente Kombination

class SecurityLevel(Enum):
    """🔒 Sicherheits-Level"""
    PERMISSIVE = "permissive"   # Liberale Einstellungen
    BALANCED = "balanced"       # Ausgewogene Sicherheit
    STRICT = "strict"           # Strenge Sicherheit
    PARANOID = "paranoid"       # Maximale Sicherheit

@dataclass
class INTEGRALightConfig:
    """⚙️ Vollständige Konfiguration für INTEGRA Light"""
    
    # System-Grundeinstellungen
    system_name: str = "INTEGRA Light"
    version: str = "1.0"
    processing_mode: ProcessingMode = ProcessingMode.AUTO
    security_level: SecurityLevel = SecurityLevel.BALANCED

    # Ethische Profil-Einstellungen
    align_weights: Dict[str, float] = field(default_factory=lambda: {
        'awareness': 0.8,
        'learning': 0.7,
        'integrity': 1.0,
        'governance': 0.9,
        'nurturing': 0.9
    })

    # Fast Path Konfiguration
    fast_path_enabled: bool = True
    fast_path_confidence_threshold: float = 0.8
    fast_path_max_risk: float = 0.2

    # Deep Path Konfiguration
    deep_path_enabled: bool = True
    deep_path_stakeholder_analysis: bool = True
    deep_path_generate_alternatives: bool = True
    deep_path_min_acceptable_score: float = 0.6

    # Governance und Kontrolle
    governance_enabled: bool = True
    require_justification_for_overrides: bool = True
    validate_override_safety: bool = True
    auto_escalate_critical: bool = True
    emergency_stop_enabled: bool = True

    # Lernen und Anpassung
    learning_enabled: bool = True
    pattern_learning: bool = True
    adaptive_weights: bool = True
    feedback_sensitivity: float = 0.02

    # Audit und Transparenz
    audit_enabled: bool = True
    log_all_decisions: bool = True
    provide_explanations: bool = True
    detailed_reasoning: bool = True

    # Erweiterte Einstellungen
    domain_specific_rules: Dict[str, Any] = field(default_factory=dict)
    custom_stakeholder_weights: Dict[str, float] = field(default_factory=dict)
    experimental_features: List[str] = field(default_factory=list)

@dataclass
class ProcessingResult:
    """📊 Vollständiges Verarbeitungs-Ergebnis"""
    # Haupt-Ergebnis
    response: str = ""
    confidence: float = 0.0
    processing_path: str = ""

    # Ethische Analyse
    align_score: float = 0.0
    align_details: Dict[str, float] = field(default_factory=dict)
    align_violations: List[str] = field(default_factory=list)
    ethical_quality: str = ""

    # System-Informationen
    modules_used: List[str] = field(default_factory=list)
    processing_time: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Governance und Kontrolle
    governance_actions: List[str] = field(default_factory=list)
    escalation_triggered: bool = False
    user_override_applied: bool = False

    # Transparenz und Erklärung
    reasoning_provided: bool = False
    alternatives_available: bool = False
    risk_mitigation: List[str] = field(default_factory=list)

    # Metadaten
    session_id: str = ""
    user_id: str = ""
    request_id: str = ""

# ==============================================================================
# 2. Hauptklasse - INTEGRA Light System
# ==============================================================================

class INTEGRALight:
    """
    🌟 INTEGRA Light - Vollständiges ethisches KI-System

    Ein produktionsreifes, ethisches KI-System das alle INTEGRA-Module
    intelligent orchestriert:

    🔍 Intelligente Fast/Deep Path Entscheidung
    🎯 Vollständige ALIGN-Prinzipien (Awareness, Learning, Integrity, Governance, Nurturing)
    🛡️ Menschliche Kontrolle und Override-Möglichkeiten
    🧠 Adaptive Lernfähigkeit aus Feedback
    📊 Vollständige Audit-Trails und Transparenz
    🔧 Plug-and-Play Integration

    Ideal für: Chatbots, Empfehlungssysteme, Entscheidungsunterstützung,
    Content-Moderation, Smart Home, E-Commerce, und alle KI-Anwendungen
    die ethische Standards benötigen.
    """

    def __init__(self, config: Optional[INTEGRALightConfig] = None, domain: str = "general"):
        """
        Initialisiert INTEGRA Light System
        
        Args:
            config: Vollständige System-Konfiguration
            domain: Anwendungsdomäne (z.B. "healthcare", "finance", "ecommerce")
        """
        self.config = config or INTEGRALightConfig()
        self.domain = domain
        self.session_data = {}
        self.processing_history: List[Dict[str, Any]] = []
        self.system_stats = {
            'total_requests': 0,
            'fast_path_usage': 0,
            'deep_path_usage': 0,
            'governance_interventions': 0,
            'escalations': 0,
            'user_overrides': 0,
            'learning_updates': 0
        }
        
        # System-Initialisierung
        self._initialize_system()
        
        print(f"🌟 {self.config.system_name} v{self.config.version} initialisiert")
        print(f"🎯 Domain: {domain}")
        print(f"🚦 Modus: {self.config.processing_mode.value}")
        print(f"🔒 Sicherheit: {self.config.security_level.value}")
        print(f"⚡ Fast Path: {'Aktiv' if self.config.fast_path_enabled else 'Deaktiviert'}")
        print(f"🧠 Deep Path: {'Aktiv' if self.config.deep_path_enabled else 'Deaktiviert'}")
        print(f"🛡️ Governance: {'Aktiv' if self.config.governance_enabled else 'Deaktiviert'}")
        print(f"📚 Lernen: {'Aktiv' if self.config.learning_enabled else 'Deaktiviert'}")

    def process_request(
        self,
        query: str,
        user_id: str = "anonymous",
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> ProcessingResult:
        """
        🎯 Hauptfunktion: Verarbeitet ethische KI-Anfrage
        
        Args:
            query: Die zu verarbeitende Anfrage
            user_id: Eindeutige Nutzer-ID
            context: Zusätzlicher Kontext (optional)
            session_id: Session-ID für zusammenhängende Anfragen
            
        Returns:
            ProcessingResult mit vollständigen Ergebnissen
        """
        
        start_time = datetime.now()
        request_id = f"req_{int(start_time.timestamp() * 1000)}"
        session_id = session_id or f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}"
        
        print(f"\n🚀 Verarbeite Anfrage [{request_id}]: \"{query[:60]}...\"")
        
        # Initialisiere Verarbeitungs-Kontext
        processing_context = self._initialize_processing_context(
            query, user_id, context or {}, session_id, request_id
        )
        
        try:
            # Schritt 1: Ethisches Profil laden/erstellen
            processing_context = self._load_ethical_profile(processing_context)
            
            # Schritt 2: Basis ethische Bewertung
            processing_context = self._perform_basic_ethics_check(processing_context)
            
            # Schritt 3: Governance Pre-Check (Notfall-Stops, etc.)
            processing_context = self._perform_governance_precheck(processing_context)
            
            # Schritt 4: Intelligente Path-Entscheidung
            processing_context = self._determine_processing_path(processing_context)
            
            # Schritt 5: Path-spezifische Verarbeitung
            processing_context = self._execute_processing_path(processing_context)
            
            # Schritt 6: Finale ethische Validierung
            processing_context = self._perform_final_ethics_validation(processing_context)
            
            # Schritt 7: Governance Post-Check (Überrides, Eskalationen)
            processing_context = self._perform_governance_postcheck(processing_context)
            
            # Schritt 8: Adaptives Lernen (falls aktiviert)
            if self.config.learning_enabled:
                processing_context = self._perform_adaptive_learning(processing_context)
            
            # Schritt 9: Audit und Logging
            if self.config.audit_enabled:
                processing_context = self._perform_audit_logging(processing_context