#!/usr/bin/env python3
"""
Ejemplo de uso de las características de seguridad y monitoreo de DyslexiLess.
Muestra el uso del Circuit Breaker, caché seguro y sistema de telemetría.
"""

from dyslexiless import initialize_application, get_service
from interfaces import ICorrector, INotifier, ICache
from secure_cache import SecureCache
from telemetry_system import TelemetrySystem
from circuit_breaker import CircuitBreaker
import time
import threading
from typing import Optional

class MonitoredCorrector:
    """Ejemplo de corrector con monitoreo integrado."""
    
    def __init__(self):
        # Obtener servicios
        self.corrector = get_service(ICorrector)
        self.cache = get_service(ICache)
        self.notifier = get_service(INotifier)
        self.telemetry = get_service(TelemetrySystem)
        
        # Configurar Circuit Breaker
        self.breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=30,
            name="api_breaker"
        )
        
        # Iniciar monitoreo
        self.start_monitoring()
    
    def start_monitoring(self):
        """Inicia el monitoreo del sistema."""
        # Registrar métricas personalizadas
        self.telemetry.register_custom_metric(
            "cache_hits",
            lambda: self.cache.hits
        )
        self.telemetry.register_custom_metric(
            "cache_misses",
            lambda: self.cache.misses
        )
        self.telemetry.register_custom_metric(
            "circuit_breaker_state",
            lambda: int(self.breaker.is_closed())
        )
        
        # Iniciar thread de monitoreo
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Loop principal de monitoreo."""
        while self.monitoring:
            try:
                # Verificar estado del Circuit Breaker
                if not self.breaker.is_closed():
                    self.notifier.notify(
                        "Circuit Breaker abierto - Usando correcciones locales",
                        "warning",
                        "⚠️"
                    )
                
                # Verificar tasa de aciertos del caché
                hits = self.cache.hits
                total = hits + self.cache.misses
                if total > 0:
                    hit_rate = (hits / total) * 100
                    self.telemetry.record_metric("cache_hit_rate", hit_rate)
                
                # Esperar próximo ciclo
                time.sleep(60)
                
            except Exception as e:
                self.notifier.notify(
                    f"Error en monitoreo: {e}",
                    "error",
                    "❌"
                )
    
    @CircuitBreaker.decorate(
        failure_threshold=5,
        reset_timeout=30
    )
    def correct_text(self, word: str, context: str) -> Optional[str]:
        """Corrige texto con monitoreo y protección."""
        try:
            # Verificar caché primero
            cached = self.cache.get(word, context)
            if cached is not None:
                return cached
            
            # Medir tiempo de respuesta
            start_time = time.time()
            result = self.corrector.correct_text(word, context)
            latency = (time.time() - start_time) * 1000
            
            # Registrar métricas
            self.telemetry.record_metric("correction_latency", latency)
            
            # Guardar en caché si hubo corrección
            if result[1]:  # was_corrected
                self.cache.add(word, context, result[0], True)
            
            return result
            
        except Exception as e:
            self.notifier.notify(
                f"Error en corrección: {e}",
                "error",
                "❌"
            )
            # El Circuit Breaker manejará el error
            raise
    
    def stop_monitoring(self):
        """Detiene el monitoreo."""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5.0)

def main():
    # Inicializar aplicación
    initialize_application()
    
    # Crear corrector monitorizado
    corrector = MonitoredCorrector()
    
    try:
        # Ejemplo de uso
        words = [
            ("qe", "creo qe esto"),
            ("kiero", "kiero ir al parque"),
            ("aver", "vamos a aver que pasa")
        ]
        
        for word, context in words:
            try:
                result = corrector.correct_text(word, context)
                if result and result[1]:
                    print(f"Corregido: {word} → {result[0]}")
            except Exception as e:
                print(f"Error corrigiendo {word}: {e}")
        
        # Mostrar estadísticas
        telemetry = get_service(TelemetrySystem)
        metrics = telemetry.get_metrics_summary()
        
        print("\nEstadísticas del sistema:")
        print(f"Tasa de aciertos caché: {metrics['cache_hit_rate']['current']:.1f}%")
        print(f"Latencia promedio: {metrics['correction_latency']['statistics']['avg']:.2f}ms")
        print(f"Estado Circuit Breaker: {'Cerrado' if metrics['circuit_breaker_state']['current'] else 'Abierto'}")
        
    finally:
        corrector.stop_monitoring()

if __name__ == "__main__":
    main()
