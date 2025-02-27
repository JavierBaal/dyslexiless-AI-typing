#!/usr/bin/env python3
"""
Pruebas para el sistema de notificaciones.
"""

import unittest
import threading
import time
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import List, Dict
from test_utils import TestCaseWithServices
from notification_system import (
    NotificationSystem,
    NotificationConfig,
    NotificationEvent
)

class TestNotificationSystem(TestCaseWithServices):
    """Pruebas para el sistema de notificaciones."""
    
    def setUp(self):
        """Prepara el entorno de prueba."""
        super().setUp()
        
        # Crear directorio temporal para pruebas
        self.test_dir = Path("test_notifications")
        self.test_dir.mkdir(exist_ok=True)
        
        # Crear archivo de configuración de prueba
        self.config_file = self.test_dir / "test_config.json"
        self.test_config = {
            "enabled": True,
            "sound_enabled": False,
            "duration": 1,
            "max_queue": 3,
            "min_interval": 0.1,
            "position": "top-right",
            "log_notifications": True,
            "notification_history": 50
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
        
        # Inicializar sistema de notificaciones
        self.notifier = NotificationSystem(str(self.config_file))
    
    def tearDown(self):
        """Limpia el entorno después de las pruebas."""
        super().tearDown()
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_config_loading(self):
        """Prueba la carga de configuración."""
        settings = self.notifier.get_settings()
        
        self.assertEqual(settings["duration"], 1)
        self.assertEqual(settings["max_queue"], 3)
        self.assertFalse(settings["sound_enabled"])
    
    def test_basic_notification(self):
        """Prueba notificación básica."""
        test_message = "Test notification"
        self.notifier.notify(test_message)
        
        # Esperar procesamiento
        time.sleep(0.2)
        
        # Verificar historial
        history = self.notifier.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].message, test_message)
        self.assertEqual(history[0].level, "info")
    
    def test_notification_levels(self):
        """Prueba diferentes niveles de notificación."""
        levels = ["info", "warning", "error"]
        
        for level in levels:
            message = f"Test {level}"
            self.notifier.notify(message, level=level)
        
        # Esperar procesamiento
        time.sleep(0.5)
        
        # Verificar por nivel
        for level in levels:
            filtered = self.notifier.get_history(level=level)
            self.assertEqual(len(filtered), 1)
            self.assertEqual(filtered[0].level, level)
    
    def test_queue_limit(self):
        """Prueba límite de cola de notificaciones."""
        max_queue = self.test_config["max_queue"]
        
        # Enviar más notificaciones que el límite
        for i in range(max_queue + 2):
            self.notifier.notify(f"Test {i}")
        
        self.assertLessEqual(
            len(self.notifier.notification_queue),
            max_queue,
            "La cola excede el límite configurado"
        )
    
    def test_notification_history(self):
        """Prueba historial de notificaciones."""
        history_limit = self.test_config["notification_history"]
        
        # Generar notificaciones
        for i in range(history_limit + 10):
            self.notifier.notify(f"Test {i}")
            time.sleep(0.01)
        
        history = self.notifier.get_history()
        self.assertLessEqual(
            len(history),
            history_limit,
            "El historial excede el límite configurado"
        )
    
    @patch('notification_system.NotificationSystem._notify_windows')
    @patch('notification_system.NotificationSystem._notify_macos')
    @patch('notification_system.NotificationSystem._notify_linux')
    def test_platform_specific_notifications(
        self,
        mock_linux,
        mock_macos,
        mock_windows
    ):
        """Prueba notificaciones específicas de plataforma."""
        message = "Platform test"
        
        # Probar Windows
        with patch('platform.system', return_value='Windows'):
            notifier = NotificationSystem()
            notifier.notify(message)
            time.sleep(0.2)
            mock_windows.assert_called()
        
        # Probar macOS
        with patch('platform.system', return_value='Darwin'):
            notifier = NotificationSystem()
            notifier.notify(message)
            time.sleep(0.2)
            mock_macos.assert_called()
        
        # Probar Linux
        with patch('platform.system', return_value='Linux'):
            notifier = NotificationSystem()
            notifier.notify(message)
            time.sleep(0.2)
            mock_linux.assert_called()
    
    def test_concurrent_notifications(self):
        """Prueba notificaciones concurrentes."""
        num_threads = 5
        notifications_per_thread = 20
        received_notifications = []
        
        def send_notifications():
            for i in range(notifications_per_thread):
                self.notifier.notify(f"Thread notification {i}")
                time.sleep(0.01)
        
        # Crear y ejecutar hilos
        threads = [
            threading.Thread(target=send_notifications)
            for _ in range(num_threads)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Esperar procesamiento
        time.sleep(1)
        
        # Verificar que no se perdieron notificaciones
        history = self.notifier.get_history()
        total_expected = min(
            num_threads * notifications_per_thread,
            self.test_config["notification_history"]
        )
        
        self.assertEqual(
            len(history),
            total_expected,
            "Se perdieron notificaciones en el procesamiento concurrente"
        )
    
    def test_notification_metadata(self):
        """Prueba metadatos en notificaciones."""
        metadata = {
            "source": "test",
            "priority": "high",
            "tags": ["test", "metadata"]
        }
        
        self.notifier.notify(
            "Test with metadata",
            metadata=metadata
        )
        
        # Verificar metadatos
        history = self.notifier.get_history(limit=1)
        self.assertEqual(
            history[0].metadata,
            metadata,
            "Los metadatos no se preservaron correctamente"
        )
    
    def test_disabled_notifications(self):
        """Prueba cuando las notificaciones están deshabilitadas."""
        # Deshabilitar notificaciones
        self.notifier.update_settings({"enabled": False})
        
        # Intentar enviar notificación
        self.notifier.notify("Should not appear")
        
        # Verificar que no se registró
        history = self.notifier.get_history()
        self.assertEqual(len(history), 0)

def test_notification_performance():
    """
    Prueba de rendimiento del sistema de notificaciones.
    Esta prueba simula un uso intensivo del sistema.
    """
    print("\n=== Prueba de Rendimiento de Notificaciones ===")
    
    notifier = NotificationSystem()
    num_notifications = 1000
    start_time = time.time()
    
    try:
        # Enviar notificaciones rápidamente
        for i in range(num_notifications):
            notifier.notify(
                f"Performance test {i}",
                metadata={"test_id": i}
            )
        
        # Esperar procesamiento
        time.sleep(2)
        
        # Calcular estadísticas
        end_time = time.time()
        total_time = end_time - start_time
        notifications_per_second = num_notifications / total_time
        
        print(f"\nTiempo total: {total_time:.2f}s")
        print(f"Notificaciones procesadas: {num_notifications}")
        print(f"Notificaciones por segundo: {notifications_per_second:.1f}")
        
        # Verificar uso de memoria
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Uso de memoria: {memory_usage:.1f} MB")
        
    except Exception as e:
        print(f"Error en prueba de rendimiento: {e}")
        raise

if __name__ == "__main__":
    unittest.main()
