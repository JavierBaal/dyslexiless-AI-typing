#!/usr/bin/env python3
"""
Sistema centralizado de notificaciones para DyslexiLess.
Proporciona una interfaz unificada para notificaciones en todas las plataformas.
"""

import os
import sys
import platform
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
from pathlib import Path
from interfaces import INotifier
from logger_manager import logger

@dataclass
class NotificationConfig:
    """Configuración del sistema de notificaciones."""
    enabled: bool = True
    sound_enabled: bool = True
    duration: int = 3  # segundos
    max_queue: int = 5
    min_interval: float = 0.5  # segundos entre notificaciones
    position: str = "top-right"
    log_notifications: bool = True
    notification_history: int = 100  # número de notificaciones a mantener en historial

@dataclass
class NotificationEvent:
    """Representa una notificación individual."""
    message: str
    level: str
    icon: str
    timestamp: str
    id: str
    metadata: Dict[str, Any]

class NotificationSystem(INotifier):
    """
    Sistema centralizado de notificaciones multiplataforma.
    
    Características:
    - Soporte para múltiples plataformas (Windows, macOS, Linux)
    - Cola de notificaciones con prioridad
    - Historial de notificaciones
    - Configuración personalizable
    - Soporte para temas y estilos
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa el sistema de notificaciones.
        
        Args:
            config_file: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_file)
        self._init_platform_specific()
        self.notification_queue: List[NotificationEvent] = []
        self.notification_history: List[NotificationEvent] = []
        self._queue_lock = threading.Lock()
        self._last_notification = datetime.now()
        self._running = True
        
        # Iniciar procesador de cola
        self._queue_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self._queue_thread.start()
        
        logger.info("Sistema de notificaciones inicializado")
    
    def _load_config(self, config_file: Optional[str]) -> NotificationConfig:
        """Carga la configuración del sistema."""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                return NotificationConfig(**config_data)
            except Exception as e:
                logger.error(f"Error al cargar configuración: {e}")
        
        return NotificationConfig()
    
    def _init_platform_specific(self):
        """Inicializa componentes específicos de la plataforma."""
        self.platform = platform.system().lower()
        
        if self.platform == "darwin":  # macOS
            try:
                import Foundation
                import AppKit
                self._notify = self._notify_macos
            except ImportError:
                self._notify = self._notify_fallback
                
        elif self.platform == "windows":
            try:
                from win10toast import ToastNotifier
                self.toaster = ToastNotifier()
                self._notify = self._notify_windows
            except ImportError:
                self._notify = self._notify_fallback
                
        else:  # Linux y otros
            try:
                import dbus
                self._notify = self._notify_linux
            except ImportError:
                self._notify = self._notify_fallback
    
    def notify(
        self,
        message: str,
        level: str = "info",
        icon: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Envía una notificación.
        
        Args:
            message: Mensaje a mostrar
            level: Nivel de la notificación (info/warning/error)
            icon: Ícono opcional
            metadata: Metadatos adicionales
        """
        if not self.config.enabled:
            return
            
        event = NotificationEvent(
            message=message,
            level=level,
            icon=icon,
            timestamp=datetime.now().isoformat(),
            id=f"notif_{len(self.notification_history)}",
            metadata=metadata or {}
        )
        
        with self._queue_lock:
            # Mantener tamaño máximo de cola
            if len(self.notification_queue) < self.config.max_queue:
                self.notification_queue.append(event)
                
            # Actualizar historial
            self.notification_history.append(event)
            if len(self.notification_history) > self.config.notification_history:
                self.notification_history.pop(0)
        
        # Logging si está habilitado
        if self.config.log_notifications:
            log_func = getattr(logger, level, logger.info)
            log_func(f"[{level.upper()}] {message}")
    
    def _process_queue(self):
        """Procesa la cola de notificaciones."""
        while self._running:
            try:
                # Verificar intervalo mínimo
                now = datetime.now()
                if (now - self._last_notification).total_seconds() < self.config.min_interval:
                    continue
                
                # Obtener siguiente notificación
                with self._queue_lock:
                    if not self.notification_queue:
                        continue
                    event = self.notification_queue.pop(0)
                
                # Mostrar notificación
                self._notify(event)
                self._last_notification = datetime.now()
                
            except Exception as e:
                logger.error(f"Error procesando notificación: {e}")
            finally:
                time.sleep(0.1)  # Evitar CPU spinning
    
    def _notify_macos(self, event: NotificationEvent):
        """Notificación nativa en macOS."""
        os.system(f"""
            osascript -e 'display notification "{event.message}" with title "DyslexiLess"'
        """)
    
    def _notify_windows(self, event: NotificationEvent):
        """Notificación nativa en Windows."""
        self.toaster.show_toast(
            "DyslexiLess",
            event.message,
            duration=self.config.duration,
            threaded=True
        )
    
    def _notify_linux(self, event: NotificationEvent):
        """Notificación nativa en Linux."""
        try:
            bus = dbus.SessionBus()
            notify = bus.get_object(
                'org.freedesktop.Notifications',
                '/org/freedesktop/Notifications'
            )
            interface = dbus.Interface(
                notify,
                'org.freedesktop.Notifications'
            )
            interface.Notify(
                "DyslexiLess",
                0,
                "",  # icon
                "DyslexiLess",
                event.message,
                [],
                {},
                self.config.duration * 1000
            )
        except Exception as e:
            logger.error(f"Error en notificación Linux: {e}")
            self._notify_fallback(event)
    
    def _notify_fallback(self, event: NotificationEvent):
        """Notificación fallback usando print."""
        print(f"\n[DyslexiLess] {event.icon} {event.message}")
    
    def get_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración actual."""
        return asdict(self.config)
    
    def update_settings(self, settings: Dict[str, Any]):
        """Actualiza la configuración."""
        self.config = NotificationConfig(**settings)
    
    def get_history(
        self,
        limit: Optional[int] = None,
        level: Optional[str] = None
    ) -> List[NotificationEvent]:
        """
        Obtiene el historial de notificaciones.
        
        Args:
            limit: Número máximo de notificaciones a retornar
            level: Filtrar por nivel
            
        Returns:
            List[NotificationEvent]: Lista de notificaciones
        """
        history = self.notification_history
        
        if level:
            history = [e for e in history if e.level == level]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def clear_history(self):
        """Limpia el historial de notificaciones."""
        self.notification_history.clear()
    
    def __del__(self):
        """Limpieza al destruir el objeto."""
        self._running = False
        if hasattr(self, '_queue_thread'):
            self._queue_thread.join(timeout=1.0)
