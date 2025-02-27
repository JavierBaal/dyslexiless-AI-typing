#!/usr/bin/env python3
"""
Pruebas de integración para verificar la interacción entre componentes.
"""

import unittest
import threading
import time
from typing import List
from dependency_container import DependencyContainer
from service_registry import setup_services, get_service
from interfaces import (
    ICorrector,
    ICache,
    IInputMonitor,
    INotifier,
    ITextBuffer
)
from secure_cache import SecureCache
from text_corrector import TextCorrector
from keyboardlistener import KeyboardListener, OptimizedBuffer
from unittest.mock import MagicMock, patch

class TestServiceIntegration(unittest.TestCase):
    """Pruebas de integración entre servicios."""
    
    @classmethod
    def setUpClass(cls):
        """Configura el entorno de prueba."""
        cls.container = DependencyContainer()
        setup_services()
    
    def setUp(self):
        """Prepara cada prueba."""
        self.container.clear()
        setup_services()
    
    def test_service_registration(self):
        """Prueba que todos los servicios se registran correctamente."""
        # Verificar servicios core
        cache = get_service(ICache)
        notifier = get_service(INotifier)
        buffer = get_service(ITextBuffer)
        corrector = get_service(ICorrector)
        monitor = get_service(IInputMonitor)
        
        self.assertIsInstance(cache, SecureCache)
        self.assertIsInstance(buffer, OptimizedBuffer)
        self.assertIsInstance(corrector, TextCorrector)
        self.assertIsInstance(monitor, KeyboardListener)
    
    def test_dependency_injection(self):
        """Prueba que las dependencias se inyectan correctamente."""
        monitor = get_service(IInputMonitor)
        
        self.assertIsInstance(monitor.corrector, TextCorrector)
        self.assertIsInstance(monitor.buffer, OptimizedBuffer)
    
    def test_correction_flow(self):
        """Prueba el flujo completo de corrección."""
        monitor = get_service(IInputMonitor)
        corrector = get_service(ICorrector)
        
        # Simular entrada de texto
        text = "qe"
        context = "creo qe esto"
        
        # Verificar corrección
        correction, was_corrected = corrector.correct_text(text, context)
        
        self.assertEqual(correction, "que")
        self.assertTrue(was_corrected)
    
    def test_cache_integration(self):
        """Prueba la integración con el caché."""
        cache = get_service(ICache)
        corrector = get_service(ICorrector)
        
        # Primera corrección (debería ir a la API)
        text = "qe"
        context = "test qe prueba"
        correction1, _ = corrector.correct_text(text, context)
        
        # Segunda corrección (debería venir del caché)
        with patch.object(TextCorrector, 'openai_correct') as mock_api:
            correction2, _ = corrector.correct_text(text, context)
            mock_api.assert_not_called()
            
        self.assertEqual(correction1, correction2)
    
    @patch('service_registry.SystemNotifier.notify')
    def test_notification_system(self, mock_notify):
        """Prueba el sistema de notificaciones."""
        notifier = get_service(INotifier)
        
        # Enviar notificación
        message = "Test notification"
        notifier.notify(message, "info", "✅")
        
        # Verificar que se llamó al método notify
        mock_notify.assert_called_once()
        args = mock_notify.call_args[0]
        self.assertEqual(args[0], message)

class TestAsyncCorrection(unittest.TestCase):
    """Pruebas de corrección asíncrona."""
    
    def setUp(self):
        """Prepara el entorno de prueba."""
        setup_services()
        self.monitor = get_service(IInputMonitor)
        self.corrections: List[str] = []
        self.lock = threading.Lock()
    
    def test_concurrent_corrections(self):
        """Prueba correcciones concurrentes."""
        def correction_thread(word: str):
            correction, _ = self.monitor.corrector.correct_text(word, f"test {word} context")
            with self.lock:
                self.corrections.append(correction)
        
        # Crear varios hilos de corrección
        threads = [
            threading.Thread(target=correction_thread, args=(word,))
            for word in ["qe", "kiero", "aver", "mui"]
        ]
        
        # Iniciar hilos
        for t in threads:
            t.start()
        
        # Esperar a que terminen
        for t in threads:
            t.join()
        
        # Verificar resultados
        self.assertEqual(len(self.corrections), 4)
        self.assertIn("que", self.corrections)
        self.assertIn("quiero", self.corrections)

def test_system_integration():
    """
    Prueba completa de integración del sistema.
    Esta prueba simula un uso real de la aplicación.
    """
    print("\n=== Prueba de Integración del Sistema ===")
    
    try:
        # 1. Inicializar servicios
        print("\nInicializando servicios...")
        setup_services()
        
        # 2. Obtener servicios principales
        monitor = get_service(IInputMonitor)
        notifier = get_service(INotifier)
        cache = get_service(ICache)
        
        # 3. Simular escritura y correcciones
        print("\nSimulando uso del sistema...")
        test_words = [
            ("qe", "creo qe esto"),
            ("kiero", "kiero ir al"),
            ("aver", "voy a aver si"),
            ("mui", "es mui tarde")
        ]
        
        for word, context in test_words:
            # Simular corrección
            correction, was_corrected = monitor.corrector.correct_text(word, context)
            print(f"Palabra: {word} → {correction}")
            
            # Verificar caché
            cached = cache.get(word, context)
            print(f"En caché: {cached is not None}")
        
        # 4. Verificar estadísticas
        print("\nVerificando estadísticas...")
        cache_stats = cache.get_stats()
        print(f"Entradas en caché: {cache_stats['total_entries']}")
        print(f"Uso del caché: {cache_stats['usage_percentage']:.1f}%")
        
        print("\n✅ Prueba de integración completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error en prueba de integración: {e}")
        raise

if __name__ == "__main__":
    print("Ejecutando pruebas de integración...")
    
    try:
        # Ejecutar pruebas unitarias
        unittest.main(verbosity=2)
    except SystemExit:
        pass
    
    # Ejecutar prueba de integración completa
    test_system_integration()
