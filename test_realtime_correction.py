#!/usr/bin/env python3
"""
Pruebas para el sistema de corrección en tiempo real.
Verifica la integración entre el procesamiento por lotes y la corrección interactiva.
"""

import unittest
import asyncio
import threading
import time
from typing import List, Dict
from unittest.mock import MagicMock, patch
from test_utils import TestCaseWithServices, async_test, simulate_typing, wait_for_condition
from test_config import TEST_CORRECTIONS, LOAD_TEST_TEXTS, BATCH_TEST_CONFIG
from interfaces import ICorrector, INotifier, ITextBuffer
from keyboardlistener import KeyboardListener
from batch_processor import BatchProcessor
from text_corrector import TextCorrector

class MockKeyboard:
    """Mock para simular el teclado."""
    def __init__(self):
        self.pressed_keys = []
        self.position = 0
    
    def press(self, key):
        self.pressed_keys.append(("press", key))
    
    def release(self, key):
        self.pressed_keys.append(("release", key))
    
    def type(self, text):
        for char in text:
            self.pressed_keys.append(("type", char))

class TestRealtimeCorrection(TestCaseWithServices):
    """Pruebas para corrección en tiempo real."""
    
    def setUp(self):
        """Prepara el entorno de prueba."""
        super().setUp()
        
        # Mock para el teclado
        self.keyboard_mock = MockKeyboard()
        with patch('keyboardlistener.Controller', return_value=self.keyboard_mock):
            self.listener = KeyboardListener(
                corrector=self.corrector,
                buffer=self.container.resolve(ITextBuffer),
                notifier=self.container.resolve(INotifier)
            )
    
    def test_basic_correction_flow(self):
        """Prueba el flujo básico de corrección."""
        test_word = "qe"
        expected = "que"
        
        # Simular escritura
        simulate_typing(f"{test_word} ", self.listener)
        
        # Esperar corrección
        def check_correction():
            notifications = self.notifier.notifications
            return any(
                expected in n["message"]
                for n in notifications
            )
        
        self.assertTrue(
            wait_for_condition(check_correction),
            "No se realizó la corrección esperada"
        )
    
    def test_batch_correction(self):
        """Prueba corrección por lotes."""
        # Preparar palabras de prueba
        test_words = ["qe", "kiero", "aser"]
        corrections = []
        
        def correction_callback(correction: str, was_corrected: bool):
            corrections.append((correction, was_corrected))
        
        # Simular escritura rápida
        for word in test_words:
            simulate_typing(f"{word} ", self.listener)
        
        # Esperar a que se procesen todas las correcciones
        time.sleep(BATCH_TEST_CONFIG["max_delay"] * 2)
        
        # Verificar correcciones
        self.assertEqual(len(corrections), len(test_words))
        self.assertIn(("que", True), corrections)
        self.assertIn(("quiero", True), corrections)
        self.assertIn(("hacer", True), corrections)
    
    @async_test
    async def test_concurrent_corrections(self):
        """Prueba correcciones concurrentes."""
        # Preparar datos de prueba
        test_data = TEST_CORRECTIONS["palabras_simples"][:5]
        corrections_received = []
        
        def correction_callback(correction: str, was_corrected: bool):
            corrections_received.append((correction, was_corrected))
        
        # Simular escritura concurrente
        tasks = []
        for case in test_data:
            word = case["input"]
            task = asyncio.create_task(
                self._simulate_typing_async(f"{word} ")
            )
            tasks.append(task)
        
        # Esperar a que se completen todas las tareas
        await asyncio.gather(*tasks)
        
        # Esperar procesamiento de correcciones
        await asyncio.sleep(BATCH_TEST_CONFIG["max_delay"] * 2)
        
        # Verificar resultados
        self.assertEqual(
            len(corrections_received),
            len(test_data),
            "No se recibieron todas las correcciones"
        )
    
    def test_correction_priority(self):
        """Prueba priorización de correcciones."""
        # Palabras con diferentes prioridades
        test_cases = [
            ("qe", "contexto corto", 1),  # Baja prioridad
            ("kiero", "un contexto más largo para mayor prioridad", 3),  # Alta prioridad
            ("aser", "contexto medio", 2)  # Prioridad media
        ]
        
        corrections_order = []
        
        def correction_callback(word: str):
            corrections_order.append(word)
        
        # Simular escritura
        for word, context, _ in test_cases:
            simulate_typing(f"{word} ", self.listener)
        
        # Esperar procesamiento
        time.sleep(BATCH_TEST_CONFIG["max_delay"] * 2)
        
        # Verificar orden de correcciones
        self.assertEqual(
            corrections_order[0],
            "quiero",
            "La corrección de alta prioridad debería procesarse primero"
        )
    
    def test_backspace_handling(self):
        """Prueba manejo de borrado de texto."""
        # Escribir palabra con error
        simulate_typing("qe", self.listener)
        
        # Simular backspace
        self.listener.on_press(MagicMock(name='backspace'))
        
        # Verificar que se canceló la corrección pendiente
        self.assertIsNone(
            self.listener.current_word,
            "La palabra actual debería ser None después de backspace"
        )
    
    def test_load_handling(self):
        """Prueba manejo de carga alta."""
        # Cargar texto de prueba
        test_text = LOAD_TEST_TEXTS[0]
        words = test_text.split()
        
        start_time = time.time()
        
        # Simular escritura rápida
        for word in words:
            simulate_typing(f"{word} ", self.listener)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar que el procesamiento no excede el límite
        self.assertLess(
            processing_time,
            len(words) * 0.1,  # 100ms por palabra máximo
            "El procesamiento es demasiado lento"
        )
    
    async def _simulate_typing_async(self, text: str):
        """Simula escritura de forma asíncrona."""
        for char in text:
            if char == ' ':
                self.listener.on_press(MagicMock(char=None, name='space'))
            else:
                self.listener.on_press(MagicMock(char=char))
            await asyncio.sleep(0.01)

def test_realtime_performance():
    """
    Prueba de rendimiento del sistema en tiempo real.
    Esta prueba simula un uso intensivo del sistema.
    """
    print("\n=== Prueba de Rendimiento en Tiempo Real ===")
    
    # Configurar sistema
    listener = KeyboardListener(
        corrector=TextCorrector(batch_size=20),
        buffer=OptimizedBuffer(max_size=1000),
        notifier=MockNotifier()
    )
    
    # Métricas
    total_words = 0
    total_corrections = 0
    start_time = time.time()
    
    try:
        # Simular sesión de escritura intensa
        for text in LOAD_TEST_TEXTS:
            words = text.split()
            total_words += len(words)
            
            # Simular escritura
            simulate_typing(text + "\n", listener)
            
            # Esperar procesamiento
            time.sleep(BATCH_TEST_CONFIG["max_delay"])
            
            # Actualizar métricas
            total_corrections = listener.corrections_count
        
        # Calcular estadísticas
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\nTiempo total: {total_time:.2f}s")
        print(f"Palabras procesadas: {total_words}")
        print(f"Correcciones realizadas: {total_corrections}")
        print(f"Tasa de corrección: {(total_corrections/total_words)*100:.1f}%")
        print(f"Palabras por segundo: {total_words/total_time:.1f}")
        
    except Exception as e:
        print(f"Error en prueba de rendimiento: {e}")
        raise

if __name__ == "__main__":
    unittest.main()
