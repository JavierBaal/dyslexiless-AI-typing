#!/usr/bin/env python3
"""
Pruebas para el sistema de Circuit Breaker.
"""

import unittest
import time
from datetime import datetime, timedelta
from circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerRegistry,
    with_circuit_breaker
)
from text_corrector import TextCorrector
from unittest.mock import patch, MagicMock

class TestCircuitBreaker(unittest.TestCase):
    """Pruebas unitarias para CircuitBreaker."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.breaker = CircuitBreaker(
            name="test",
            failure_threshold=2,
            reset_timeout=1,
            failure_window=5,
            success_threshold=1
        )
    
    def test_initial_state(self):
        """Prueba el estado inicial del circuit breaker."""
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertTrue(self.breaker.allow_request())
    
    def test_open_on_failures(self):
        """Prueba que el circuito se abre después de varios fallos."""
        self.breaker.record_failure()
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        
        self.breaker.record_failure()
        self.assertEqual(self.breaker.state, CircuitState.OPEN)
        self.assertFalse(self.breaker.allow_request())
    
    def test_reset_after_timeout(self):
        """Prueba que el circuito intenta reset después del timeout."""
        self.breaker.record_failure()
        self.breaker.record_failure()
        self.assertEqual(self.breaker.state, CircuitState.OPEN)
        
        time.sleep(1.1)  # Esperar más que reset_timeout
        
        self.assertTrue(self.breaker.allow_request())
        self.assertEqual(self.breaker.state, CircuitState.HALF_OPEN)
    
    def test_close_after_success(self):
        """Prueba que el circuito se cierra después de éxitos en half-open."""
        self.breaker.record_failure()
        self.breaker.record_failure()
        time.sleep(1.1)
        
        self.breaker.record_success()
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
    
    def test_failure_window(self):
        """Prueba que los fallos antiguos se descartan."""
        self.breaker.record_failure()
        time.sleep(5.1)  # Más que failure_window
        self.breaker.record_failure()
        
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

class TestCircuitBreakerRegistry(unittest.TestCase):
    """Pruebas unitarias para CircuitBreakerRegistry."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.registry = CircuitBreakerRegistry()
        self.registry.reset_all()
    
    def test_singleton(self):
        """Prueba que el registro es un singleton."""
        registry2 = CircuitBreakerRegistry()
        self.assertIs(self.registry, registry2)
    
    def test_get_breaker(self):
        """Prueba la obtención y creación de breakers."""
        breaker1 = self.registry.get_breaker("test1")
        breaker2 = self.registry.get_breaker("test1")
        
        self.assertIs(breaker1, breaker2)
        self.assertEqual(breaker1.name, "test1")
    
    def test_reset_all(self):
        """Prueba el reset de todos los breakers."""
        self.registry.get_breaker("test1")
        self.registry.get_breaker("test2")
        
        self.registry.reset_all()
        
        breaker = self.registry.get_breaker("test1")
        self.assertEqual(breaker.state, CircuitState.CLOSED)

class TestIntegrationWithTextCorrector(unittest.TestCase):
    """Pruebas de integración con TextCorrector."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.corrector = TextCorrector()
        CircuitBreakerRegistry().reset_all()
    
    @patch('openai.OpenAI')
    def test_openai_circuit_breaker(self, mock_openai):
        """Prueba el circuit breaker con OpenAI."""
        # Simular fallos de API
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Provocar fallos
        for _ in range(5):
            result, corrected = self.corrector.openai_correct("test", "context")
            self.assertEqual(result, "test")
            self.assertFalse(corrected)
        
        # Verificar que el circuito está abierto
        breaker = CircuitBreakerRegistry().get_breaker("openai")
        self.assertEqual(breaker.state, CircuitState.OPEN)
        
        # Verificar que se usa el fallback
        result, corrected = self.corrector.openai_correct("qe", "context")
        self.assertEqual(result, "que")
        self.assertTrue(corrected)
    
    @patch('anthropic.Anthropic')
    def test_anthropic_circuit_breaker(self, mock_anthropic):
        """Prueba el circuit breaker con Anthropic."""
        # Simular fallos de API
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")
        
        # Provocar fallos
        for _ in range(5):
            result, corrected = self.corrector.anthropic_correct("test", "context")
            self.assertEqual(result, "test")
            self.assertFalse(corrected)
        
        # Verificar que el circuito está abierto
        breaker = CircuitBreakerRegistry().get_breaker("anthropic")
        self.assertEqual(breaker.state, CircuitState.OPEN)
        
        # Verificar que se usa el fallback
        result, corrected = self.corrector.anthropic_correct("kiero", "context")
        self.assertEqual(result, "quiero")
        self.assertTrue(corrected)

def test_corrector_resilience():
    """
    Prueba completa de resiliencia del corrector.
    Esta prueba simula diferentes escenarios de fallo y recuperación.
    """
    corrector = TextCorrector()
    
    # 1. Probar corrección normal
    print("\nProbando corrección normal...")
    result, corrected = corrector.correct_text("qe", "Creo qe esto funciona")
    print(f"Resultado: {result}, Corregido: {corrected}")
    
    # 2. Simular fallos de API
    print("\nSimulando fallos de API...")
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Provocar varios fallos
        for i in range(5):
            print(f"Intento {i+1}...")
            result, corrected = corrector.correct_text("test", "context")
            print(f"Resultado: {result}, Corregido: {corrected}")
    
    # 3. Verificar fallback
    print("\nVerificando funcionamiento del fallback...")
    result, corrected = corrector.correct_text("kiero", "Kiero ir al cine")
    print(f"Resultado: {result}, Corregido: {corrected}")
    
    # 4. Esperar reset del circuit breaker
    print("\nEsperando reset del circuit breaker...")
    time.sleep(60)
    
    # 5. Verificar recuperación
    print("\nVerificando recuperación del servicio...")
    result, corrected = corrector.correct_text("qe", "Creo qe esto funciona")
    print(f"Resultado: {result}, Corregido: {corrected}")

if __name__ == "__main__":
    print("Ejecutando pruebas de Circuit Breaker...")
    
    # Ejecutar pruebas unitarias
    unittest.main(verbosity=2)
    
    # Ejecutar prueba de resiliencia
    print("\n=== Prueba de Resiliencia ===")
    test_corrector_resilience()
