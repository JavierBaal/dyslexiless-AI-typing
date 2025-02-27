#!/usr/bin/env python3
"""
Interfaces abstractas para los componentes principales de DyslexiLess.
Define los contratos que deben implementar los diferentes módulos.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional, Any
from datetime import datetime

class ICorrector(ABC):
    """Interfaz para servicios de corrección."""
    
    @abstractmethod
    def correct_text(self, word: str, context: str) -> Tuple[str, bool]:
        """
        Corrige un texto dado su contexto.
        
        Args:
            word: Palabra a corregir
            context: Contexto de la palabra
            
        Returns:
            Tuple[str, bool]: (texto corregido, si fue corregido)
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Prueba la conexión con el servicio.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        pass

class ICache(ABC):
    """Interfaz para sistemas de caché."""
    
    @abstractmethod
    def get(self, key: str, context: str) -> Optional[Tuple[str, bool]]:
        """
        Obtiene una entrada del caché.
        
        Args:
            key: Clave a buscar
            context: Contexto de la clave
            
        Returns:
            Optional[Tuple[str, bool]]: Valor almacenado o None si no existe
        """
        pass
    
    @abstractmethod
    def add(self, key: str, context: str, value: str, metadata: bool):
        """
        Añade una entrada al caché.
        
        Args:
            key: Clave a almacenar
            context: Contexto de la clave
            value: Valor a almacenar
            metadata: Metadatos adicionales
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """Realiza limpieza de entradas expiradas."""
        pass

class IInputMonitor(ABC):
    """Interfaz para monitores de entrada."""
    
    @abstractmethod
    def start(self):
        """Inicia el monitoreo de entrada."""
        pass
    
    @abstractmethod
    def stop(self):
        """Detiene el monitoreo de entrada."""
        pass
    
    @abstractmethod
    def pause(self):
        """Pausa temporalmente el monitoreo."""
        pass
    
    @abstractmethod
    def resume(self):
        """Reanuda el monitoreo."""
        pass

class INotifier(ABC):
    """Interfaz para sistema de notificaciones."""
    
    @abstractmethod
    def notify(self, message: str, level: str = "info", icon: str = ""):
        """
        Muestra una notificación.
        
        Args:
            message: Mensaje a mostrar
            level: Nivel de la notificación (info/warning/error)
            icon: Ícono opcional
        """
        pass
    
    @abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        """
        Obtiene configuración de notificaciones.
        
        Returns:
            Dict[str, Any]: Configuración actual
        """
        pass

class IConfigManager(ABC):
    """Interfaz para gestión de configuración."""
    
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """
        Carga la configuración.
        
        Returns:
            Dict[str, Any]: Configuración cargada
        """
        pass
    
    @abstractmethod
    def save(self, config: Dict[str, Any]):
        """
        Guarda la configuración.
        
        Args:
            config: Configuración a guardar
        """
        pass
    
    @abstractmethod
    def get_defaults(self) -> Dict[str, Any]:
        """
        Obtiene configuración por defecto.
        
        Returns:
            Dict[str, Any]: Configuración por defecto
        """
        pass

class IMetricsCollector(ABC):
    """Interfaz para recolección de métricas."""
    
    @abstractmethod
    def record_correction(self, was_successful: bool, latency: float):
        """
        Registra una corrección.
        
        Args:
            was_successful: Si la corrección fue exitosa
            latency: Tiempo de respuesta en segundos
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas.
        
        Returns:
            Dict[str, Any]: Estadísticas recolectadas
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reinicia las métricas."""
        pass

class ITextBuffer(ABC):
    """Interfaz para buffer de texto."""
    
    @abstractmethod
    def add_char(self, char: str):
        """
        Añade un carácter al buffer.
        
        Args:
            char: Carácter a añadir
        """
        pass
    
    @abstractmethod
    def get_word(self) -> str:
        """
        Obtiene la palabra actual.
        
        Returns:
            str: Palabra actual en el buffer
        """
        pass
    
    @abstractmethod
    def get_context(self) -> str:
        """
        Obtiene el contexto actual.
        
        Returns:
            str: Contexto actual
        """
        pass
    
    @abstractmethod
    def clear(self):
        """Limpia el buffer."""
        pass

class IServiceRegistry(ABC):
    """Interfaz para registro de servicios."""
    
    @abstractmethod
    def register(self, name: str, service: Any):
        """
        Registra un servicio.
        
        Args:
            name: Nombre del servicio
            service: Instancia del servicio
        """
        pass
    
    @abstractmethod
    def get_service(self, name: str) -> Any:
        """
        Obtiene un servicio registrado.
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Any: Instancia del servicio
        """
        pass
    
    @abstractmethod
    def list_services(self) -> Dict[str, Any]:
        """
        Lista todos los servicios registrados.
        
        Returns:
            Dict[str, Any]: Servicios registrados
        """
        pass
