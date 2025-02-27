#!/usr/bin/env python3
"""
Pruebas para el sistema de inyección de dependencias.
"""

import unittest
from typing import Optional
from interfaces import (
    ICorrector,
    ICache,
    IInputMonitor,
    INotifier
)
from dependency_container import DependencyContainer

# Clases de prueba
class TestCorrector(ICorrector):
    def __init__(self, cache: ICache, notifier: Optional[INotifier] = None):
        self.cache = cache
        self.notifier = notifier
        
    def correct_text(self, word: str, context: str):
        return word, False
        
    def test_connection(self) -> bool:
        return True

class TestCache(ICache):
    def get(self, key: str, context: str):
        return None
        
    def add(self, key: str, context: str, value: str, metadata: bool):
        pass
        
    def cleanup(self):
        pass

class TestNotifier(INotifier):
    def notify(self, message: str, level: str = "info", icon: str = ""):
        pass
        
    def get_settings(self):
        return {}

class TestMonitor(IInputMonitor):
    def __init__(self, corrector: ICorrector):
        self.corrector = corrector
        
    def start(self):
        pass
        
    def stop(self):
        pass
        
    def pause(self):
        pass
        
    def resume(self):
        pass

class TestDependencyContainer(unittest.TestCase):
    """Pruebas unitarias para DependencyContainer."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.container = DependencyContainer()
        self.container.clear()
        
        # Registrar servicios básicos
        self.container.register(ICache, TestCache, singleton=True)
        self.container.register(INotifier, TestNotifier, singleton=True)
        self.container.register(ICorrector, TestCorrector, singleton=True)
        self.container.register(IInputMonitor, TestMonitor)
    
    def test_singleton_resolution(self):
        """Prueba la resolución de singletons."""
        cache1 = self.container.resolve(ICache)
        cache2 = self.container.resolve(ICache)
        
        self.assertIs(cache1, cache2, "Las instancias singleton deben ser idénticas")
    
    def test_transient_resolution(self):
        """Prueba la resolución de instancias transient."""
        monitor1 = self.container.resolve(IInputMonitor)
        monitor2 = self.container.resolve(IInputMonitor)
        
        self.assertIsNot(monitor1, monitor2, "Las instancias transient deben ser diferentes")
    
    def test_dependency_injection(self):
        """Prueba la inyección automática de dependencias."""
        corrector = self.container.resolve(ICorrector)
        
        self.assertIsInstance(corrector.cache, TestCache)
        self.assertIsInstance(corrector.notifier, TestNotifier)
    
    def test_named_implementations(self):
        """Prueba el registro y resolución de implementaciones nombradas."""
        class AlternativeCache(ICache):
            def get(self, key: str, context: str):
                return None
            def add(self, key: str, context: str, value: str, metadata: bool):
                pass
            def cleanup(self):
                pass
        
        self.container.register(ICache, AlternativeCache, name="alternative")
        
        default_cache = self.container.resolve(ICache)
        alt_cache = self.container.resolve(ICache, name="alternative")
        
        self.assertIsInstance(default_cache, TestCache)
        self.assertIsInstance(alt_cache, AlternativeCache)
    
    def test_missing_dependency(self):
        """Prueba el manejo de dependencias faltantes."""
        class BrokenService:
            def __init__(self, missing_dependency):
                pass
        
        with self.assertRaises(ValueError):
            self.container.register("broken", BrokenService)
            self.container.resolve("broken")
    
    def test_circular_dependency(self):
        """Prueba la detección de dependencias circulares."""
        class ServiceA:
            def __init__(self, b: 'ServiceB'):
                pass
        
        class ServiceB:
            def __init__(self, a: ServiceA):
                pass
        
        self.container.register("ServiceA", ServiceA)
        self.container.register("ServiceB", ServiceB)
        
        with self.assertRaises(ValueError):
            self.container.resolve("ServiceA")
    
    def test_optional_dependency(self):
        """Prueba el manejo de dependencias opcionales."""
        class OptionalService:
            def __init__(self, cache: ICache, optional: Optional[INotifier] = None):
                self.cache = cache
                self.optional = optional
        
        self.container.register("optional", OptionalService)
        instance = self.container.resolve("optional")
        
        self.assertIsInstance(instance.cache, TestCache)
        self.assertIsInstance(instance.optional, TestNotifier)

def test_dependency_resolution():
    """
    Prueba completa de resolución de dependencias.
    Esta prueba simula un escenario real de uso.
    """
    print("\n=== Prueba de Resolución de Dependencias ===")
    
    container = DependencyContainer()
    container.clear()
    
    # 1. Registrar servicios
    print("\nRegistrando servicios...")
    container.register(ICache, TestCache)
    container.register(INotifier, TestNotifier)
    container.register(ICorrector, TestCorrector)
    container.register(IInputMonitor, TestMonitor)
    
    # 2. Resolver servicios con dependencias
    print("\nResolviendo servicios...")
    try:
        monitor = container.resolve(IInputMonitor)
        print(f"Monitor creado: {monitor.__class__.__name__}")
        print(f"Corrector inyectado: {monitor.corrector.__class__.__name__}")
        print(f"Cache inyectado en corrector: {monitor.corrector.cache.__class__.__name__}")
        
        # Verificar que los singletons son reutilizados
        cache1 = container.resolve(ICache)
        cache2 = container.resolve(ICache)
        print(f"\nSingletons idénticos: {cache1 is cache2}")
        
    except Exception as e:
        print(f"❌ Error en resolución: {e}")
        raise
    
    print("\n✅ Prueba completada exitosamente")

if __name__ == "__main__":
    print("Ejecutando pruebas de inyección de dependencias...")
    
    # Ejecutar pruebas unitarias
    unittest.main(verbosity=2)
    
    # Ejecutar prueba completa
    test_dependency_resolution()
