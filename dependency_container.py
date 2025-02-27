#!/usr/bin/env python3
"""
Contenedor de dependencias para DyslexiLess.
Implementa un sistema simple de inyección de dependencias.
"""

from typing import Dict, Any, Type, Optional
from interfaces import (
    ICorrector,
    ICache,
    IInputMonitor,
    INotifier,
    IConfigManager,
    IMetricsCollector,
    ITextBuffer,
    IServiceRegistry
)
import inspect
import threading
from logger_manager import logger

class DependencyContainer:
    """
    Contenedor de dependencias simple con soporte para:
    - Registro de servicios
    - Singleton y transient lifetimes
    - Resolución automática de dependencias
    - Lazy loading
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DependencyContainer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._services: Dict[Type, Dict[str, Any]] = {}
            self._instances: Dict[Type, Any] = {}
            self._initialized = True
    
    def register(
        self,
        interface: Type,
        implementation: Type,
        singleton: bool = True,
        name: str = None
    ):
        """
        Registra una implementación para una interfaz.
        
        Args:
            interface: Interfaz o tipo base
            implementation: Clase de implementación
            singleton: Si debe mantener una única instancia
            name: Nombre opcional para múltiples implementaciones
        """
        if interface not in self._services:
            self._services[interface] = {}
        
        key = name or implementation.__name__
        self._services[interface][key] = {
            'implementation': implementation,
            'singleton': singleton
        }
        
        logger.debug(
            f"Registrado servicio: {interface.__name__} → "
            f"{implementation.__name__} ({'singleton' if singleton else 'transient'})"
        )
    
    def resolve(
        self,
        interface: Type,
        name: str = None,
        **kwargs
    ) -> Any:
        """
        Resuelve una implementación registrada.
        
        Args:
            interface: Interfaz a resolver
            name: Nombre de la implementación específica
            **kwargs: Argumentos adicionales para la construcción
            
        Returns:
            Any: Instancia de la implementación
            
        Raises:
            KeyError: Si la interfaz o implementación no está registrada
            ValueError: Si hay un error en la resolución de dependencias
        """
        if interface not in self._services:
            raise KeyError(f"No hay implementaciones registradas para {interface.__name__}")
        
        services = self._services[interface]
        if name and name not in services:
            raise KeyError(f"Implementación '{name}' no encontrada para {interface.__name__}")
        
        service_info = services[name or next(iter(services))]
        implementation = service_info['implementation']
        
        # Si es singleton y ya existe instancia, retornarla
        if service_info['singleton']:
            instance_key = (interface, name)
            if instance_key in self._instances:
                return self._instances[instance_key]
        
        # Resolver dependencias del constructor
        try:
            instance = self._create_instance(implementation, **kwargs)
            
            # Guardar instancia si es singleton
            if service_info['singleton']:
                self._instances[(interface, name)] = instance
            
            return instance
            
        except Exception as e:
            logger.error(f"Error al resolver {implementation.__name__}: {e}")
            raise ValueError(f"Error de resolución de dependencias: {e}")
    
    def _create_instance(self, implementation: Type, **kwargs) -> Any:
        """
        Crea una instancia resolviendo sus dependencias.
        
        Args:
            implementation: Clase a instanciar
            **kwargs: Argumentos adicionales
            
        Returns:
            Any: Nueva instancia
        """
        # Obtener parámetros del constructor
        signature = inspect.signature(implementation.__init__)
        parameters = signature.parameters
        
        # Filtrar kwargs inválidos
        valid_kwargs = {
            k: v for k, v in kwargs.items() 
            if k in parameters
        }
        
        # Resolver dependencias faltantes
        for name, param in parameters.items():
            if name == 'self' or name in valid_kwargs:
                continue
            
            # Si el parámetro tiene anotación de tipo, intentar resolverlo
            if param.annotation != inspect.Parameter.empty:
                try:
                    valid_kwargs[name] = self.resolve(param.annotation)
                except Exception as e:
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(
                            f"No se pudo resolver la dependencia {name}: {e}"
                        )
        
        return implementation(**valid_kwargs)
    
    def clear(self):
        """Limpia todas las instancias singleton."""
        self._instances.clear()
        logger.info("Contenedor de dependencias limpiado")

# Ejemplo de uso:
"""
# Registrar servicios
container = DependencyContainer()
container.register(ICorrector, OpenAICorrector, singleton=True)
container.register(ICache, SecureCache, singleton=True)
container.register(IInputMonitor, KeyboardMonitor)

# Resolver servicios
corrector = container.resolve(ICorrector)
cache = container.resolve(ICache)
input_monitor = container.resolve(IInputMonitor)
"""
