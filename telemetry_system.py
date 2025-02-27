#!/usr/bin/env python3
"""
Sistema de telemetría y monitoreo para DyslexiLess.
Recolecta, procesa y reporta métricas del sistema.
"""

import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import json
import os
from pathlib import Path
import psutil
from collections import deque
import statistics
from logger_manager import logger

@dataclass
class MetricValue:
    """Representa un valor de métrica con timestamp."""
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class MetricConfig:
    """Configuración para una métrica."""
    name: str
    description: str
    unit: str = ""
    alert_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    retention_days: int = 7
    sampling_interval: float = 60.0  # segundos
    aggregation: str = "avg"  # avg, sum, min, max

class MetricCollector:
    """
    Recolector de métricas individuales.
    Mantiene historial y realiza agregaciones.
    """
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.values: deque[MetricValue] = deque(maxlen=10000)  # ~1 semana a 1 min intervalo
        self.last_collection = datetime.now()
        self._lock = threading.Lock()
    
    def add_value(self, value: float, tags: Dict[str, str] = None):
        """Añade un nuevo valor a la métrica."""
        with self._lock:
            metric = MetricValue(
                value=value,
                timestamp=datetime.now(),
                tags=tags or {}
            )
            self.values.append(metric)
            self._check_alerts(metric)
    
    def get_statistics(
        self,
        interval: timedelta = timedelta(hours=1)
    ) -> Dict[str, float]:
        """Calcula estadísticas para el período especificado."""
        with self._lock:
            now = datetime.now()
            recent_values = [
                v.value for v in self.values
                if now - v.timestamp <= interval
            ]
            
            if not recent_values:
                return {}
            
            return {
                "min": min(recent_values),
                "max": max(recent_values),
                "avg": statistics.mean(recent_values),
                "median": statistics.median(recent_values),
                "stddev": statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            }
    
    def _check_alerts(self, metric: MetricValue):
        """Verifica si se deben generar alertas."""
        if (self.config.alert_threshold and 
            metric.value >= self.config.alert_threshold):
            logger.error(
                f"ALERTA: {self.config.name} excedió umbral crítico "
                f"({metric.value} {self.config.unit})"
            )
        elif (self.config.warning_threshold and 
              metric.value >= self.config.warning_threshold):
            logger.warning(
                f"ADVERTENCIA: {self.config.name} excedió umbral de advertencia "
                f"({metric.value} {self.config.unit})"
            )

class TelemetrySystem:
    """
    Sistema central de telemetría.
    Gestiona la recolección y almacenamiento de métricas.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.collectors: Dict[str, MetricCollector] = {}
        self.custom_metrics: Dict[str, Callable[[], float]] = {}
        self._running = False
        self._collection_thread = None
        self.load_config(config_file)
    
    def load_config(self, config_file: Optional[str] = None):
        """Carga configuración desde archivo."""
        config_path = config_file or os.path.join(
            os.path.dirname(__file__),
            "config",
            "telemetry.json"
        )
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Configurar métricas predefinidas
            for metric_config in config.get("metrics", []):
                self.add_collector(MetricConfig(**metric_config))
                
        except Exception as e:
            logger.error(f"Error cargando configuración de telemetría: {e}")
            # Usar configuración por defecto
            self._setup_default_metrics()
    
    def _setup_default_metrics(self):
        """Configura métricas por defecto del sistema."""
        default_metrics = [
            MetricConfig(
                name="cpu_usage",
                description="Uso de CPU",
                unit="%",
                warning_threshold=70,
                alert_threshold=90
            ),
            MetricConfig(
                name="memory_usage",
                description="Uso de memoria",
                unit="MB",
                warning_threshold=1000,
                alert_threshold=2000
            ),
            MetricConfig(
                name="correction_latency",
                description="Latencia de corrección",
                unit="ms",
                warning_threshold=500,
                alert_threshold=1000
            ),
            MetricConfig(
                name="corrections_per_minute",
                description="Correcciones por minuto",
                unit="corrections/min"
            ),
            MetricConfig(
                name="api_success_rate",
                description="Tasa de éxito de API",
                unit="%",
                warning_threshold=95,
                alert_threshold=90
            )
        ]
        
        for config in default_metrics:
            self.add_collector(config)
    
    def add_collector(self, config: MetricConfig):
        """Añade un nuevo recolector de métricas."""
        self.collectors[config.name] = MetricCollector(config)
    
    def register_custom_metric(
        self,
        name: str,
        collector: Callable[[], float]
    ):
        """Registra una métrica personalizada."""
        self.custom_metrics[name] = collector
    
    def record_metric(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Registra un valor para una métrica."""
        if name in self.collectors:
            self.collectors[name].add_value(value, tags)
        else:
            logger.warning(f"Métrica no registrada: {name}")
    
    def start_collection(self):
        """Inicia la recolección automática de métricas."""
        self._running = True
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self._collection_thread.start()
    
    def stop_collection(self):
        """Detiene la recolección automática."""
        self._running = False
        if self._collection_thread:
            self._collection_thread.join(timeout=5.0)
    
    def _collection_loop(self):
        """Loop principal de recolección de métricas."""
        while self._running:
            try:
                self._collect_system_metrics()
                self._collect_custom_metrics()
                time.sleep(60)  # Recolectar cada minuto
            except Exception as e:
                logger.error(f"Error en recolección de métricas: {e}")
    
    def _collect_system_metrics(self):
        """Recolecta métricas del sistema."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self.record_metric("cpu_usage", cpu_percent)
        
        # Memoria
        memory = psutil.Process().memory_info()
        self.record_metric("memory_usage", memory.rss / 1024 / 1024)
    
    def _collect_custom_metrics(self):
        """Recolecta métricas personalizadas."""
        for name, collector in self.custom_metrics.items():
            try:
                value = collector()
                self.record_metric(name, value)
            except Exception as e:
                logger.error(f"Error recolectando métrica {name}: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de todas las métricas.
        
        Returns:
            Dict con estadísticas de todas las métricas
        """
        summary = {}
        
        for name, collector in self.collectors.items():
            summary[name] = {
                "config": collector.config.__dict__,
                "current": collector.values[-1].value if collector.values else None,
                "statistics": collector.get_statistics()
            }
        
        return summary
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Exporta métricas en el formato especificado.
        
        Args:
            format: Formato de exportación (json/csv)
            
        Returns:
            str: Métricas formateadas
        """
        summary = self.get_metrics_summary()
        
        if format == "json":
            return json.dumps(summary, indent=2, default=str)
        elif format == "csv":
            # TODO: Implementar exportación CSV
            raise NotImplementedError("Exportación CSV no implementada")
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def __del__(self):
        """Limpieza al destruir el objeto."""
        self.stop_collection()
