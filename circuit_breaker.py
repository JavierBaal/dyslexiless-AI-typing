#!/usr/bin/env python3
"""
Implementación de Circuit Breaker para servicios de IA.
Protege contra fallos en las APIs y proporciona degradación elegante.
"""

import time
from enum import Enum
from typing import Callable, Any, Dict, Optional
from functools import wraps
import threading
from datetime import datetime, timedelta
from logger_manager import logger

class CircuitState(Enum):
    """Estados posibles del circuit breaker."""
    CLOSED = "CLOSED"       # Normal, permitiendo llamadas
    OPEN = "OPEN"          # Bloqueando llamadas
    HALF_OPEN = "HALF_OPEN"  # Permitiendo una llamada de prueba

class CircuitBreaker:
    """
    Implementación del patrón Circuit Breaker.
    
    Attributes:
        failure_threshold: Número de fallos antes de abrir el circuito
        reset_timeout: Segundos antes de intentar half-open
        failure_window: Ventana de tiempo para contar fallos
        success_threshold: Éxitos necesarios en half-open para cerrar
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        failure_window: int = 120,
        success_threshold: int = 2
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_window = failure_window
        self.success_threshold = success_threshold
        
        self._state = CircuitState.CLOSED
        self._failures = []
        self._last_failure_time = None
        self._half_open_successes = 0
        self._lock = threading.RLock()
    
    @property
    def state(self) -> CircuitState:
        """Estado actual del circuit breaker."""
        with self._lock:
            return self._state
    
    def _update_failure_window(self):
        """Actualiza la ventana de fallos, eliminando los antiguos."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.failure_window)
        self._failures = [f for f in self._failures if f > window_start]
    
    def _should_open(self) -> bool:
        """Determina si el circuito debe abrirse."""
        self._update_failure_window()
        return len(self._failures) >= self.failure_threshold
    
    def _should_attempt_reset(self) -> bool:
        """Determina si se debe intentar resetear el circuito."""
        if not self._last_failure_time:
            return True
        
        elapsed = (datetime.now() - self._last_failure_time).total_seconds()
        return elapsed >= self.reset_timeout
    
    def record_failure(self):
        """Registra un fallo en el servicio."""
        with self._lock:
            now = datetime.now()
            self._failures.append(now)
            self._last_failure_time = now
            self._half_open_successes = 0
            
            if self._should_open():
                if self._state != CircuitState.OPEN:
                    logger.warning(
                        f"Circuit Breaker '{self.name}' abierto después de "
                        f"{len(self._failures)} fallos en {self.failure_window}s"
                    )
                self._state = CircuitState.OPEN
    
    def record_success(self):
        """Registra un éxito en el servicio."""
        with self._lock:
            self._failures.clear()
            
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.success_threshold:
                    logger.info(
                        f"Circuit Breaker '{self.name}' cerrado después de "
                        f"{self.success_threshold} éxitos consecutivos"
                    )
                    self._state = CircuitState.CLOSED
                    self._half_open_successes = 0
    
    def allow_request(self) -> bool:
        """Determina si se debe permitir una nueva petición."""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(
                        f"Circuit Breaker '{self.name}' cambiando a half-open "
                        f"después de {self.reset_timeout}s"
                    )
                    self._state = CircuitState.HALF_OPEN
                    return True
                return False
            
            # HALF_OPEN: permitir solo una petición
            return self._half_open_successes < self.success_threshold

class CircuitBreakerRegistry:
    """
    Registro global de circuit breakers.
    
    Permite acceder a los circuit breakers desde cualquier parte de la aplicación.
    """
    
    _instance = None
    _breakers: Dict[str, CircuitBreaker] = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CircuitBreakerRegistry, cls).__new__(cls)
        return cls._instance
    
    def get_breaker(self, name: str) -> CircuitBreaker:
        """Obtiene un circuit breaker por nombre, creándolo si no existe."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name)
            return self._breakers[name]
    
    def reset_all(self):
        """Resetea todos los circuit breakers."""
        with self._lock:
            self._breakers.clear()

def with_circuit_breaker(name: str, fallback: Optional[Callable] = None):
    """
    Decorador para proteger funciones con un circuit breaker.
    
    Args:
        name: Nombre del circuit breaker a usar
        fallback: Función opcional a llamar si el circuit breaker está abierto
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            registry = CircuitBreakerRegistry()
            breaker = registry.get_breaker(name)
            
            if not breaker.allow_request():
                logger.warning(
                    f"Circuit Breaker '{name}' abierto, "
                    f"usando fallback para {func.__name__}"
                )
                if fallback:
                    return fallback(*args, **kwargs)
                raise Exception(
                    f"Servicio '{name}' no disponible y "
                    f"no hay función de fallback"
                )
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                logger.error(f"Error en {func.__name__}: {e}")
                if fallback:
                    return fallback(*args, **kwargs)
                raise
        
        return wrapper
    
    return decorator

# Ejemplo de uso:
"""
from circuit_breaker import with_circuit_breaker

def fallback_correction(text: str) -> str:
    return text  # Devolver texto original como fallback

@with_circuit_breaker("openai", fallback=fallback_correction)
def correct_with_openai(text: str) -> str:
    # Llamada a OpenAI API
    pass

@with_circuit_breaker("anthropic", fallback=fallback_correction)
def correct_with_anthropic(text: str) -> str:
    # Llamada a Anthropic API
    pass
"""
