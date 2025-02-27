#!/usr/bin/env python3
"""
Pruebas para verificar la optimización de memoria.
"""

import unittest
import time
import psutil
import os
from keyboardlistener import KeyboardListener, OptimizedBuffer
from typing import List
import threading
from pynput.keyboard import Key

class TestOptimizedBuffer(unittest.TestCase):
    """Pruebas unitarias para OptimizedBuffer."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.buffer = OptimizedBuffer(max_size=100)
    
    def test_buffer_limits(self):
        """Prueba que el buffer respeta sus límites."""
        # Añadir más caracteres que el límite
        for i in range(150):
            self.buffer.add_char(str(i))
        
        # Verificar que no excede el tamaño máximo
        self.assertEqual(len(self.buffer.chars), 100)
        self.assertEqual(self.buffer.stats.total_chars, 100)
        
        # Verificar uso del buffer
        self.assertEqual(self.buffer.stats.buffer_usage, 1.0)
    
    def test_word_buffer(self):
        """Prueba el buffer de palabras."""
        words = ["hola", "mundo", "python", "test"]
        for word in words:
            self.buffer.add_word(word)
        
        context = self.buffer.get_context()
        self.assertEqual(context, "hola mundo python test")
    
    def test_cleanup(self):
        """Prueba la limpieza automática del buffer."""
        # Llenar el buffer
        for i in range(80):
            self.buffer.add_char(str(i))
        
        # Simular tiempo pasado
        self.buffer.stats.last_cleanup = self.buffer.stats.last_cleanup.replace(
            year=2020
        )
        
        # Ejecutar limpieza
        self.buffer.cleanup()
        
        # Verificar que se realizó la limpieza
        self.assertTrue(self.buffer.stats.buffer_usage < 0.8)

class TestMemoryUsage(unittest.TestCase):
    """Pruebas de uso de memoria."""
    
    @staticmethod
    def get_memory_usage() -> float:
        """Obtiene el uso de memoria actual en MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_sustained_typing(self):
        """Prueba el uso de memoria durante escritura sostenida."""
        listener = KeyboardListener()
        initial_memory = self.get_memory_usage()
        
        # Simular escritura intensiva
        text = "Este es un texto largo para probar el uso de memoria " * 100
        words = text.split()
        
        for word in words:
            # Simular escribir cada palabra
            for char in word:
                listener.on_press(type('obj', (), {'char': char})())
            # Simular espacio entre palabras
            listener.on_press(Key.space)
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # La memoria no debe aumentar más de 10MB
        self.assertLess(memory_increase, 10.0)
        print(f"Aumento de memoria: {memory_increase:.2f}MB")

class TestLongTermMemory(unittest.TestCase):
    """Pruebas de memoria a largo plazo."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.listener = KeyboardListener()
        self.running = True
        self.memory_samples: List[float] = []
    
    def memory_monitor(self):
        """Monitorea el uso de memoria en segundo plano."""
        while self.running:
            memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            self.memory_samples.append(memory)
            time.sleep(1)
    
    def test_memory_stability(self):
        """Prueba la estabilidad de memoria durante uso prolongado."""
        # Iniciar monitor de memoria
        monitor_thread = threading.Thread(target=self.memory_monitor)
        monitor_thread.start()
        
        try:
            # Simular uso prolongado
            for _ in range(1000):
                # Simular escritura de palabras
                for word in ["prueba", "de", "memoria", "prolongada"]:
                    for char in word:
                        self.listener.on_press(type('obj', (), {'char': char})())
                    self.listener.on_press(Key.space)
                time.sleep(0.01)
            
            # Analizar muestras de memoria
            max_increase = max(self.memory_samples) - self.memory_samples[0]
            print(f"Máximo aumento de memoria: {max_increase:.2f}MB")
            
            # La memoria no debe aumentar más de 20MB durante uso prolongado
            self.assertLess(max_increase, 20.0)
            
            # La desviación estándar debe ser baja (memoria estable)
            import numpy as np
            std_dev = np.std(self.memory_samples)
            print(f"Desviación estándar de memoria: {std_dev:.2f}MB")
            self.assertLess(std_dev, 5.0)
            
        finally:
            self.running = False
            monitor_thread.join()

def test_memory_optimization():
    """
    Prueba completa de optimización de memoria.
    Esta prueba simula un uso intensivo de la aplicación.
    """
    print("\n=== Prueba de Optimización de Memoria ===")
    
    # 1. Crear listener
    listener = KeyboardListener()
    initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    print(f"\nMemoria inicial: {initial_memory:.2f}MB")
    
    # 2. Simular escritura intensiva
    print("\nSimulando escritura intensiva...")
    for _ in range(10):
        text = "Este es un texto muy largo para probar la optimización " * 50
        for word in text.split():
            for char in word:
                listener.on_press(type('obj', (), {'char': char})())
            listener.on_press(Key.space)
    
    # 3. Verificar memoria después de escritura
    memory_after_typing = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    print(f"Memoria después de escritura: {memory_after_typing:.2f}MB")
    print(f"Aumento de memoria: {memory_after_typing - initial_memory:.2f}MB")
    
    # 4. Forzar limpieza
    print("\nForzando limpieza de buffer...")
    listener.buffer.cleanup()
    
    # 5. Verificar memoria final
    final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    print(f"Memoria final: {final_memory:.2f}MB")
    print(f"Diferencia total: {final_memory - initial_memory:.2f}MB")
    
    # 6. Verificar estadísticas del buffer
    print("\nEstadísticas del buffer:")
    print(f"Uso del buffer: {listener.buffer.stats.buffer_usage * 100:.1f}%")
    print(f"Total de caracteres: {listener.buffer.stats.total_chars}")

if __name__ == "__main__":
    print("Ejecutando pruebas de optimización de memoria...")
    
    try:
        # Ejecutar pruebas unitarias
        unittest.main(verbosity=2)
    except SystemExit:
        pass
    
    # Ejecutar prueba de memoria completa
    test_memory_optimization()
