#!/usr/bin/env python3
"""
Registro central de servicios para DyslexiLess.
Configura y registra todos los servicios en el contenedor de dependencias.
"""

from dependency_container import DependencyContainer
from interfaces import (
    ICorrector,
    ICache,
    IInputMonitor,
    INotifier,
    ITextBuffer
)
from text_corrector import TextCorrector
from secure_cache import SecureCache
from keyboardlistener import KeyboardListener, OptimizedBuffer
from logger_manager import logger

from notification_system import NotificationSystem
from telemetry_system import TelemetrySystem

class Metrics:
    """Interfaz para métricas globales del sistema."""
    def __init__(self):
        self.telemetry = None
        self.start_time = datetime.now()
    
    def initialize(self, telemetry: TelemetrySystem):
        """Inicializa el sistema de métricas."""
        self.telemetry = telemetry
        self.register_global_metrics()
    
    def register_global_metrics(self):
        """Registra métricas globales del sistema."""
        if not self.telemetry:
            return
        
        # Uptime
        def get_uptime():
            return (datetime.now() - self.start_time).total_seconds()
        self.telemetry.register_custom_metric("system_uptime", get_uptime)
        
        # Número de correcciones activas
        def get_active_corrections():
            return len(self.telemetry.collectors.get("corrections_per_minute", []))
        self.telemetry.register_custom_metric("active_corrections", get_active_corrections)

def setup_services():
    """
    Configura y registra todos los servicios en el contenedor.
    Esta función debe llamarse al inicio de la aplicación.
    
    Returns:
        bool: True si la inicialización fue exitosa
    """
    try:
        container = DependencyContainer()
        
        # Registrar servicios core
        container.register(ICache, SecureCache, singleton=True)
        
        # Configurar e instanciar sistema de notificaciones
        notifications_config = os.path.join(
            os.path.dirname(__file__),
            "config",
            "notifications.json"
        )
        
        container.register(
            INotifier,
            lambda: NotificationSystem(notifications_config),
            singleton=True
        )
        container.register(ITextBuffer, OptimizedBuffer, singleton=True)
        
        # Registrar servicios de corrección con configuración de lotes
        container.register(
            ICorrector,
            lambda: TextCorrector(
                cache=container.resolve(ICache),
                batch_size=10  # Configurable según necesidades
            ),
            singleton=True
        )
        
        # Registrar monitor de teclado
        container.register(IInputMonitor, KeyboardListener)
        
        logger.info("Servicios registrados exitosamente")
        
        # Configurar sistema de telemetría
        telemetry_config = os.path.join(config_dir, "telemetry.json")
        telemetry = TelemetrySystem(telemetry_config)
        container.register_instance(TelemetrySystem, telemetry)
        
        # Inicializar métricas globales
        metrics = Metrics()
        metrics.initialize(telemetry)
        container.register_instance(Metrics, metrics)
        
        # Iniciar recolección de métricas
        telemetry.start_collection()
        
        # Obtener servicios principales para verificación
        corrector = container.resolve(ICorrector)
        notifier = container.resolve(INotifier)
        
        # Verificar que el batch processor está configurado
        if hasattr(corrector, 'batch_processor'):
            logger.info("Sistema de procesamiento por lotes inicializado")
            stats = corrector.batch_processor.get_stats()
            logger.debug(f"Estado inicial del procesador: {stats}")
        else:
            logger.warning("Sistema de procesamiento por lotes no disponible")
        
        return True
        
    except Exception as e:
        logger.error(f"Error al registrar servicios: {e}")
        return False

def get_service(interface, name=None):
    """
    Obtiene una instancia de un servicio registrado.
    
    Args:
        interface: Interfaz del servicio
        name: Nombre opcional para implementaciones específicas
        
    Returns:
        Instancia del servicio solicitado
    """
    try:
        container = DependencyContainer()
        return container.resolve(interface, name=name)
    except Exception as e:
        logger.error(f"Error al obtener servicio {interface.__name__}: {e}")
        raise

# Función de inicialización principal
def initialize_application():
    """
    Inicializa la aplicación configurando todos los servicios necesarios.
    
    Returns:
        bool: True si la inicialización fue exitosa
    """
    try:
        logger.info("Iniciando DyslexiLess...")
        
        # Configurar servicios
        if not setup_services():
            raise RuntimeError("Error al configurar servicios")
        
        # Obtener servicios principales
        notifier = get_service(INotifier)
        corrector = get_service(ICorrector)
        
        # Probar conexión con servicios de IA
        if not corrector.test_connection():
            notifier.notify(
                "No se pudo conectar con el servicio de IA. "
                "Usando corrector local.",
                "warning",
                "⚠️"
            )
        
        # Iniciar monitor de teclado
        monitor = get_service(IInputMonitor)
        monitor.start()
        
        notifier.notify(
            "DyslexiLess iniciado correctamente",
            "info",
            "✨"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error al inicializar la aplicación: {e}")
        return False
