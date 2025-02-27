#!/usr/bin/env python3
"""
Pruebas para el sistema de telemetría.
"""

import unittest
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json
from typing import Dict, Any
from unittest.mock import MagicMock, patch
from test_utils import TestCaseWithServices
from telemetry_system import (
    TelemetrySystem,
    MetricCollector,
    MetricConfig,
    MetricValue
)

class TestTelemetrySystem(TestCaseWithServices):
    """Pruebas para el sistema de telemetría."""
    
    def setUp(self):
        """Prepara el entorno de prueba."""
        super().setUp()
        
        # Crear directorio temporal para pruebas
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "test_telemetry.json"
        
        # Configuración de prueba
        self.test_config = {
            "enabled": True,
            "collection_interval": 1,
            "metrics": [
                {
                    "name": "test_metric",
                    "description": "Metric for testing",
                    "unit": "units",
                    "warning_threshold": 80,
                    "alert_threshold": 90
                }
            ]
        }
        
        # Guardar configuración
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
        
        # Inicializar sistema
        self.telemetry = TelemetrySystem(str(self.config_file))
    
    def tearDown(self):
        """Limpia el entorno después de las pruebas."""
        super().tearDown()
        import shutil
        shutil.rmtree(self.test_dir)
        
        # Detener recolección
        if hasattr(self, 'telemetry'):
            self.telemetry.stop_collection()
    
    def test_metric_collection(self):
        """Prueba recolección básica de métricas."""
        metric_name = "test_metric"
        test_value = 42.0
        
        # Registrar valor
        self.telemetry.record_metric(metric_name, test_value)
        
        # Verificar recolección
        summary = self.telemetry.get_metrics_summary()
        self.assertIn(metric_name, summary)
        self.assertEqual(
            summary[metric_name]["current"],
            test_value
        )
    
    def test_alert_thresholds(self):
        """Prueba umbrales de alerta."""
        metric_name = "test_metric"
        warning_value = 85.0  # Por encima del umbral de advertencia
        alert_value = 95.0    # Por encima del umbral crítico
        
        # Capturar logs
        with self.assertLogs() as logs:
            self.telemetry.record_metric(metric_name, warning_value)
            self.telemetry.record_metric(metric_name, alert_value)
        
        # Verificar alertas
        log_output = "\n".join(logs.output)
        self.assertIn("ADVERTENCIA", log_output)
        self.assertIn("ALERTA", log_output)
    
    def test_statistics_calculation(self):
        """Prueba cálculo de estadísticas."""
        metric_name = "test_metric"
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        # Registrar valores
        for value in values:
            self.telemetry.record_metric(metric_name, value)
        
        # Obtener estadísticas
        summary = self.telemetry.get_metrics_summary()
        stats = summary[metric_name]["statistics"]
        
        # Verificar estadísticas
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 50.0)
        self.assertEqual(stats["avg"], 30.0)
    
    def test_custom_metrics(self):
        """Prueba métricas personalizadas."""
        metric_name = "custom_metric"
        mock_collector = MagicMock(return_value=42.0)
        
        # Registrar métrica personalizada
        self.telemetry.register_custom_metric(metric_name, mock_collector)
        
        # Iniciar recolección
        self.telemetry.start_collection()
        
        # Esperar recolección
        time.sleep(2)
        
        # Verificar que se llamó al recolector
        mock_collector.assert_called()
        
        # Verificar valor recolectado
        summary = self.telemetry.get_metrics_summary()
        self.assertIn(metric_name, summary)
    
    def test_metric_retention(self):
        """Prueba retención de métricas."""
        metric_name = "retention_test"
        retention_days = 7
        
        config = MetricConfig(
            name=metric_name,
            description="Test retention",
            retention_days=retention_days
        )
        
        collector = MetricCollector(config)
        
        # Simular métricas antiguas
        old_date = datetime.now() - timedelta(days=retention_days + 1)
        collector.values.append(MetricValue(
            value=42.0,
            timestamp=old_date,
            tags={}
        ))
        
        # Obtener estadísticas recientes
        stats = collector.get_statistics(
            interval=timedelta(days=retention_days)
        )
        
        # Verificar que se excluyeron valores antiguos
        self.assertEqual(len(stats), 0)
    
    def test_export_metrics(self):
        """Prueba exportación de métricas."""
        # Registrar algunas métricas
        self.telemetry.record_metric("test_metric", 42.0)
        
        # Exportar como JSON
        json_export = self.telemetry.export_metrics(format="json")
        data = json.loads(json_export)
        
        # Verificar formato
        self.assertIn("test_metric", data)
        self.assertEqual(data["test_metric"]["current"], 42.0)
        
        # Verificar que formato no soportado lanza error
        with self.assertRaises(ValueError):
            self.telemetry.export_metrics(format="invalid")
    
    @patch('psutil.cpu_percent')
    @patch('psutil.Process')
    def test_system_metrics(self, mock_process, mock_cpu):
        """Prueba recolección de métricas del sistema."""
        # Configurar mocks
        mock_cpu.return_value = 50.0
        mock_memory = MagicMock()
        mock_memory.rss = 1024 * 1024 * 100  # 100 MB
        mock_process.return_value.memory_info.return_value = mock_memory
        
        # Recolectar métricas
        self.telemetry._collect_system_metrics()
        
        # Verificar métricas
        summary = self.telemetry.get_metrics_summary()
        self.assertIn("cpu_usage", summary)
        self.assertIn("memory_usage", summary)
        
        self.assertEqual(summary["cpu_usage"]["current"], 50.0)
        self.assertEqual(summary["memory_usage"]["current"], 100.0)

def test_telemetry_performance():
    """
    Prueba de rendimiento del sistema de telemetría.
    Esta prueba simula un uso intensivo del sistema.
    """
    print("\n=== Prueba de Rendimiento de Telemetría ===")
    
    # Configurar sistema
    with tempfile.TemporaryDirectory() as temp_dir:
        telemetry = TelemetrySystem()
        metrics_recorded = 0
        start_time = time.time()
        
        try:
            # Simular recolección intensiva
            for i in range(1000):
                # Registrar múltiples métricas
                telemetry.record_metric("test_1", i * 1.5)
                telemetry.record_metric("test_2", i * 2.0)
                telemetry.record_metric("test_3", i * 0.5)
                metrics_recorded += 3
                
                if i % 100 == 0:
                    # Forzar cálculo de estadísticas periódicamente
                    telemetry.get_metrics_summary()
            
            # Calcular estadísticas
            end_time = time.time()
            total_time = end_time - start_time
            ops_per_second = metrics_recorded / total_time
            
            print(f"\nTiempo total: {total_time:.2f}s")
            print(f"Métricas registradas: {metrics_recorded}")
            print(f"Operaciones por segundo: {ops_per_second:.1f}")
            
            # Verificar uso de memoria
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024
            print(f"Uso de memoria: {memory_usage:.1f} MB")
            
        except Exception as e:
            print(f"Error en prueba de rendimiento: {e}")
            raise

if __name__ == "__main__":
    unittest.main()
