#!/usr/bin/env python3
"""
Utilidades y configuración común para pruebas.
Proporciona fixtures, mocks y funciones auxiliares reutilizables.
"""

import unittest
import asyncio
import threading
import time
from typing import Dict, Any, Optional, Callable
from unittest.mock import MagicMock, patch
from contextlib import contextmanager
import functools
import os
import tempfile
from pathlib import Path

from dependency_container import DependencyContainer
from interfaces import (
    ICorrector,
    ICache,
    INotifier,
    ITextBuffer,
    IInputMonitor
)
from service_registry import SystemNotifier
from secure_cache import SecureCache
from batch_processor import BatchProcessor
from keyboardlistener import OptimizedBuffer
from logger_manager import logger

class TestConfiguration:
    """Configuración global para pruebas."""
    
    TEMP_DIR: Optional[str] = None
    
    @classmethod
    def setup(cls):
        """Configura el entorno de pruebas."""
        # Crear directorio temporal para pruebas
        cls.TEMP_DIR = tempfile.mkdtemp(prefix="dyslexiless_test_")
        
        # Configurar variables de entorno para pruebas
        os.environ["DYSLEXILESS_TEST_MODE"] = "1"
        os.environ["DYSLEXILESS_CACHE_DIR"] = cls.TEMP_DIR
    
    @classmethod
    def cleanup(cls):
        """Limpia el entorno después de las pruebas."""
        if cls.TEMP_DIR and os.path.exists(cls.TEMP_DIR):
            import shutil
            shutil.rmtree(cls.TEMP_DIR)
        
        # Limpiar variables de entorno
        os.environ.pop("DYSLEXILESS_TEST_MODE", None)
        os.environ.pop("DYSLEXILESS_CACHE_DIR", None)

def async_test(func: Callable):
    """
    Decorador para pruebas asíncronas.
    Permite usar async/await en pruebas unitarias.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

class BaseMockCorrector(ICorrector):
    """Implementación base para correctores simulados."""
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.calls = []
        self.should_fail = False
        
    def correct_text(self, word: str, context: str) -> tuple[str, bool]:
        """Simula una corrección con retraso configurable."""
        self.calls.append((word, context))
        
        if self.should_fail:
            raise Exception("Simulated API error")
            
        time.sleep(self.delay)
        
        corrections = {
            "qe": "que",
            "kiero": "quiero",
            "aver": "haber",
            "aki": "aquí",
            "voi": "voy",
            "oi": "hoy"
        }
        
        correction = corrections.get(word, word)
        return correction, correction != word
        
    def test_connection(self) -> bool:
        return not self.should_fail

class MockCache(ICache):
    """Caché simulado para pruebas."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0
        
    def get(self, key: str, context: str) -> Optional[tuple[str, bool]]:
        cache_key = f"{key}:{context}"
        result = self.data.get(cache_key)
        if result:
            self.hits += 1
        else:
            self.misses += 1
        return result
        
    def add(self, key: str, context: str, value: str, metadata: bool):
        cache_key = f"{key}:{context}"
        self.data[cache_key] = (value, metadata)
        
    def cleanup(self):
        self.data.clear()

class MockNotifier(INotifier):
    """Sistema de notificaciones simulado."""
    
    def __init__(self):
        self.notifications = []
        
    def notify(self, message: str, level: str = "info", icon: str = ""):
        self.notifications.append({
            "message": message,
            "level": level,
            "icon": icon
        })
        
    def get_settings(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "sound": False,
            "duration": 1
        }

class TestCaseWithServices(unittest.TestCase):
    """
    Caso base para pruebas que requieren servicios.
    Proporciona configuración automática del contenedor de dependencias.
    """
    
    @classmethod
    def setUpClass(cls):
        """Configura el entorno de prueba."""
        TestConfiguration.setup()
    
    @classmethod
    def tearDownClass(cls):
        """Limpia el entorno después de las pruebas."""
        TestConfiguration.cleanup()
    
    def setUp(self):
        """Prepara cada prueba."""
        self.container = DependencyContainer()
        self.container.clear()
        
        # Registrar mocks por defecto
        self.container.register(ICache, MockCache, singleton=True)
        self.container.register(INotifier, MockNotifier, singleton=True)
        self.container.register(ITextBuffer, OptimizedBuffer, singleton=True)
        self.container.register(ICorrector, BaseMockCorrector, singleton=True)
        
        # Guardar referencias a los servicios principales
        self.cache = self.container.resolve(ICache)
        self.notifier = self.container.resolve(INotifier)
        self.corrector = self.container.resolve(ICorrector)
    
    def tearDown(self):
        """Limpia después de cada prueba."""
        self.container.clear()

@contextmanager
def mock_api_call(delay: float = 0.1, should_fail: bool = False):
    """
    Contexto para simular llamadas a API.
    
    Args:
        delay: Retraso simulado en segundos
        should_fail: Si la llamada debe fallar
    """
    def mock_response(*args, **kwargs):
        if should_fail:
            raise Exception("API Error")
        time.sleep(delay)
        return MagicMock()
    
    with patch('requests.post', side_effect=mock_response), \
         patch('openai.OpenAI', return_value=MagicMock()), \
         patch('anthropic.Anthropic', return_value=MagicMock()):
        yield

def simulate_typing(text: str, keyboard_listener: IInputMonitor):
    """
    Simula la escritura de texto a través del KeyboardListener.
    
    Args:
        text: Texto a simular
        keyboard_listener: Instancia del monitor de teclado
    """
    for char in text:
        if char == ' ':
            keyboard_listener.on_press(MagicMock(char=None, name='space'))
        else:
            keyboard_listener.on_press(MagicMock(char=char))
        time.sleep(0.01)  # Simular retraso realista entre teclas

def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 5.0,
    interval: float = 0.1
) -> bool:
    """
    Espera hasta que una condición se cumpla.
    
    Args:
        condition: Función que retorna bool
        timeout: Tiempo máximo de espera en segundos
        interval: Intervalo de verificación en segundos
        
    Returns:
        bool: True si la condición se cumplió, False si se agotó el tiempo
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    return False
