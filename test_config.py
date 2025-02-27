#!/usr/bin/env python3
"""
Configuración central para pruebas de DyslexiLess.
Define constantes, configuraciones y datos de prueba comunes.
"""

import os
from pathlib import Path
from typing import Dict, List, Any

# Directorios y rutas
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
TEMP_DIR = TEST_DIR / "temp"
REPORTS_DIR = TEST_DIR / "test_reports"
FIXTURES_DIR = TEST_DIR / "fixtures"

# Asegurar que los directorios existen
for dir_path in [TEMP_DIR, REPORTS_DIR, FIXTURES_DIR]:
    dir_path.mkdir(exist_ok=True)

# Configuración de pruebas
TEST_CONFIG = {
    "timeouts": {
        "api_call": 5.0,  # segundos
        "batch_processing": 2.0,
        "keyboard_delay": 0.01,
        "correction_wait": 0.5
    },
    "batch_sizes": {
        "small": 5,
        "medium": 10,
        "large": 20
    },
    "retry_settings": {
        "max_retries": 3,
        "initial_delay": 0.1,
        "backoff_factor": 2.0
    }
}

# Casos de prueba para correcciones
TEST_CORRECTIONS: Dict[str, List[Dict[str, Any]]] = {
    "palabras_simples": [
        {
            "input": "qe",
            "expected": "que",
            "context": "creo qe esto",
            "should_correct": True
        },
        {
            "input": "kiero",
            "expected": "quiero",
            "context": "kiero ir al cine",
            "should_correct": True
        },
        {
            "input": "hola",
            "expected": "hola",
            "context": "hola mundo",
            "should_correct": False
        }
    ],
    "frases_compuestas": [
        {
            "input": "qe kiero aser",
            "expected": ["que", "quiero", "hacer"],
            "context": "digo qe kiero aser algo",
            "should_correct": True
        },
        {
            "input": "voi a aver si puedo",
            "expected": ["voy", "a", "haber", "si", "puedo"],
            "context": "voi a aver si puedo ir",
            "should_correct": True
        }
    ],
    "caracteres_especiales": [
        {
            "input": "asi*",
            "expected": "así",
            "context": "es asi* como se hace",
            "should_correct": True
        },
        {
            "input": "q´tal",
            "expected": "qué tal",
            "context": "q´tal estas",
            "should_correct": True
        }
    ]
}

# Textos de ejemplo para pruebas de carga
LOAD_TEST_TEXTS = [
    "En un lugar de la Mancha, de cuyo nombre no qiero acordarme",
    "La vida es aqella qe sucede mientras estas ocupado asiendo otros planes",
    "El tienpo es mui valioso para perderse en cosas sin inportancia",
    "Ai veses qe es mejor no desir nada y esperar",
    "La felisidad se encuentra en las peqeñas cosas de la vida"
]

# Configuración de correcciones por lotes
BATCH_TEST_CONFIG = {
    "max_batch_size": 20,
    "min_batch_items": 3,
    "max_delay": 0.5,
    "context_window": 3
}

# Configuraciones de APIs simuladas para pruebas
MOCK_API_RESPONSES = {
    "openai": {
        "success_rate": 0.95,
        "avg_latency": 0.2,
        "error_types": ["rate_limit", "timeout", "invalid_request"]
    },
    "anthropic": {
        "success_rate": 0.98,
        "avg_latency": 0.15,
        "error_types": ["rate_limit", "server_error"]
    },
    "mixtral": {
        "success_rate": 0.90,
        "avg_latency": 0.25,
        "error_types": ["connection_error", "validation_error"]
    }
}

# Configuración del circuit breaker para pruebas
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,
    "reset_timeout": 30,
    "failure_window": 60,
    "success_threshold": 2
}

# Configuración del buffer para pruebas
BUFFER_CONFIG = {
    "max_size": 1000,
    "cleanup_interval": 300,  # 5 minutos
    "max_usage_threshold": 0.8,  # 80%
    "min_cleanup_words": 10
}

# Patrones de errores comunes para pruebas
COMMON_ERRORS = {
    "api_errors": [
        "Connection refused",
        "Timeout exceeded",
        "Rate limit reached",
        "Invalid request",
        "Server error"
    ],
    "validation_errors": [
        "Invalid input format",
        "Context too long",
        "Empty input",
        "Unsupported characters"
    ],
    "system_errors": [
        "Out of memory",
        "File not found",
        "Permission denied",
        "Process terminated"
    ]
}

def get_test_file_path(filename: str) -> Path:
    """
    Obtiene la ruta completa para un archivo de prueba.
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Path: Ruta completa del archivo
    """
    return FIXTURES_DIR / filename

def cleanup_test_files():
    """Limpia archivos temporales de prueba."""
    import shutil
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir()

def get_mock_config(api_name: str) -> Dict[str, Any]:
    """
    Obtiene la configuración de mock para una API.
    
    Args:
        api_name: Nombre de la API
        
    Returns:
        Dict[str, Any]: Configuración del mock
    """
    return MOCK_API_RESPONSES.get(api_name, {
        "success_rate": 1.0,
        "avg_latency": 0.1,
        "error_types": []
    })
