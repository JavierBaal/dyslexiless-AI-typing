#!/usr/bin/env python3
"""
Ejemplo avanzado de uso de DyslexiLess.
Muestra características avanzadas como procesamiento por lotes,
telemetría y manejo de errores.
"""

from dyslexiless import initialize_application, get_service
from interfaces import ICorrector, INotifier
from telemetry_system import TelemetrySystem
from batch_processor import BatchProcessor
import time

def correction_callback(correction: str, was_corrected: bool):
    """Callback para procesar resultados de corrección."""
    if was_corrected:
        print(f"Corrección aplicada: {correction}")

def main():
    # Inicializar aplicación
    initialize_application()
    
    # Obtener servicios
    corrector = get_service(ICorrector)
    notifier = get_service(INotifier)
    telemetry = get_service(TelemetrySystem)
    
    # Configurar procesador por lotes
    batch_processor = BatchProcessor(
        corrector=corrector,
        batch_size=5,
        max_delay=0.5
    )
    
    # Registrar métricas personalizadas
    def get_pending_corrections():
        return len(batch_processor.tasks)
    telemetry.register_custom_metric("pending_corrections", get_pending_corrections)
    
    # Ejemplo de procesamiento por lotes
    words = [
        ("qe", "creo qe esto"),
        ("kiero", "kiero ir al parque"),
        ("aver", "vamos a aver que pasa"),
        ("aki", "estoy aki ahora")
    ]
    
    try:
        # Procesar palabras en lote
        for word, context in words:
            batch_processor.add_task(
                word=word,
                context=context,
                callback=correction_callback
            )
            
            # Registrar métrica de latencia
            start_time = time.time()
            corrected_text, was_corrected = corrector.correct_text(word, context)
            latency = (time.time() - start_time) * 1000  # ms
            telemetry.record_metric("correction_latency", latency)
            
        # Esperar a que se procesen todas las correcciones
        time.sleep(1.0)
        
        # Obtener estadísticas
        stats = batch_processor.get_stats()
        print("\nEstadísticas de procesamiento:")
        print(f"Total tareas procesadas: {stats['batches_processed']}")
        print(f"Tareas pendientes: {stats['pending_tasks']}")
        
        # Obtener métricas
        metrics = telemetry.get_metrics_summary()
        print("\nMétricas del sistema:")
        print(f"Latencia promedio: {metrics['correction_latency']['statistics']['avg']:.2f}ms")
        print(f"Uso de CPU: {metrics['cpu_usage']['current']:.1f}%")
        print(f"Uso de memoria: {metrics['memory_usage']['current']:.1f}MB")
        
    except Exception as e:
        notifier.notify(
            f"Error en procesamiento: {e}",
            "error",
            "❌"
        )
    finally:
        # Detener procesador
        batch_processor.stop()

if __name__ == "__main__":
    main()
