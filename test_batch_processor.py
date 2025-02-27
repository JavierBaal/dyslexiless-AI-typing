#!/usr/bin/env python3
"""
Pruebas para el sistema de procesamiento por lotes.
"""

import unittest
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple
from batch_processor import BatchProcessor, CorrectionTask
from interfaces import ICorrector
from unittest.mock import MagicMock

class MockCorrector(ICorrector):
    """Corrector simulado para pruebas."""
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.calls = []
    
    def correct_text(self, word: str, context: str) -> Tuple[str, bool]:
        """Simula una corrección con retraso configurable."""
        self.calls.append((word, context))
        time.sleep(self.delay)
        
        corrections = {
            "qe": "que",
            "kiero": "quiero",
            "aver": "haber",
            "aki": "aquí"
        }
        
        correction = corrections.get(word, word)
        return correction, correction != word

    def test_connection(self) -> bool:
        return True

class TestBatchProcessor(unittest.TestCase):
    """Pruebas unitarias para BatchProcessor."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.corrector = MockCorrector()
        self.processor = BatchProcessor(
            self.corrector,
            batch_size=5,
            max_delay=0.2,
            min_batch_items=2
        )
        self.results = []
    
    def tearDown(self):
        """Limpia el entorno después de las pruebas."""
        self.processor.stop()
    
    def callback(self, correction: str, was_corrected: bool):
        """Callback para recolectar resultados."""
        self.results.append((correction, was_corrected))
    
    def test_basic_processing(self):
        """Prueba el procesamiento básico de tareas."""
        # Añadir tareas
        words = ["qe", "kiero", "aver"]
        for word in words:
            self.processor.add_task(
                word,
                f"test {word} context",
                self.callback
            )
        
        # Esperar procesamiento
        time.sleep(0.5)
        
        # Verificar resultados
        self.assertEqual(len(self.results), 3)
        self.assertEqual(self.results[0][0], "que")
        self.assertEqual(self.results[1][0], "quiero")
        self.assertEqual(self.results[2][0], "haber")
    
    def test_priority_ordering(self):
        """Prueba que las tareas se procesan según su prioridad."""
        # Añadir tareas con diferentes prioridades
        tasks = [
            ("qe", 1),
            ("kiero", 3),
            ("aver", 2)
        ]
        
        for word, priority in tasks:
            self.processor.add_task(
                word,
                f"test {word}",
                self.callback,
                priority=priority
            )
        
        # Esperar procesamiento
        time.sleep(0.5)
        
        # Verificar orden
        expected = ["quiero", "haber", "que"]
        processed = [r[0] for r in self.results]
        self.assertEqual(processed, expected)
    
    def test_batch_size_limit(self):
        """Prueba que se respeta el límite de tamaño de lote."""
        # Añadir más tareas que el tamaño del lote
        words = ["qe"] * 10
        for word in words:
            self.processor.add_task(word, "test context", self.callback)
        
        # Esperar primer lote
        time.sleep(0.3)
        
        # Verificar que se procesó el primer lote
        self.assertEqual(len(self.results), 5)
        
        # Esperar segundo lote
        time.sleep(0.3)
        
        # Verificar que se procesaron todas las tareas
        self.assertEqual(len(self.results), 10)
    
    def test_concurrent_access(self):
        """Prueba acceso concurrente al procesador."""
        def add_tasks():
            for _ in range(20):
                self.processor.add_task(
                    "qe",
                    "test context",
                    self.callback
                )
                time.sleep(0.01)
        
        # Crear múltiples hilos que añaden tareas
        threads = [
            threading.Thread(target=add_tasks)
            for _ in range(3)
        ]
        
        # Iniciar hilos
        for t in threads:
            t.start()
        
        # Esperar a que terminen
        for t in threads:
            t.join()
        
        # Esperar procesamiento
        time.sleep(1)
        
        # Verificar que todas las tareas se procesaron
        self.assertEqual(len(self.results), 60)

def test_batch_performance():
    """
    Prueba de rendimiento del procesador por lotes.
    Compara el tiempo de procesamiento en lote vs individual.
    """
    print("\n=== Prueba de Rendimiento del Procesador por Lotes ===")
    
    # Configurar prueba
    num_tasks = 100
    words = ["qe", "kiero", "aver", "aki"] * 25
    results = []
    
    def callback(correction: str, was_corrected: bool):
        results.append((correction, was_corrected))
    
    # 1. Procesamiento individual
    print("\nProcesando tareas individualmente...")
    corrector = MockCorrector(delay=0.01)
    start_time = time.time()
    
    for word in words:
        corrector.correct_text(word, f"test {word}")
    
    individual_time = time.time() - start_time
    print(f"Tiempo de procesamiento individual: {individual_time:.2f}s")
    
    # 2. Procesamiento por lotes
    print("\nProcesando tareas en lotes...")
    results.clear()
    processor = BatchProcessor(
        MockCorrector(delay=0.01),
        batch_size=10,
        max_delay=0.1
    )
    
    start_time = time.time()
    
    for word in words:
        processor.add_task(word, f"test {word}", callback)
    
    # Esperar a que se procesen todas las tareas
    while len(results) < num_tasks:
        time.sleep(0.1)
    
    batch_time = time.time() - start_time
    print(f"Tiempo de procesamiento por lotes: {batch_time:.2f}s")
    
    # Calcular mejora
    improvement = (individual_time - batch_time) / individual_time * 100
    print(f"\nMejora de rendimiento: {improvement:.1f}%")
    
    # Limpiar
    processor.stop()
    
    return individual_time, batch_time, improvement

if __name__ == "__main__":
    print("Ejecutando pruebas del procesador por lotes...")
    
    try:
        # Ejecutar pruebas unitarias
        unittest.main(verbosity=2)
    except SystemExit:
        pass
    
    # Ejecutar prueba de rendimiento
    test_batch_performance()
