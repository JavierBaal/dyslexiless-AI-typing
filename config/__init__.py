"""
Módulo de configuración para DyslexiLess.
Gestiona las configuraciones de los diferentes componentes del sistema.
"""

import os
from pathlib import Path
import json
import shutil
from typing import Dict, Any
from logger_manager import logger

# Asegurar que el directorio de configuración existe
CONFIG_DIR = Path(__file__).parent
CONFIG_DIR.mkdir(exist_ok=True)

# Rutas predeterminadas
NOTIFICATIONS_CONFIG = CONFIG_DIR / "notifications.json"
KEYBOARD_CONFIG = CONFIG_DIR / "keyboard.json"
SERVICES_CONFIG = CONFIG_DIR / "services.json"

# Configuraciones por defecto
DEFAULT_NOTIFICATIONS = {
    "enabled": True,
    "sound_enabled": True,
    "duration": 3,
    "max_queue": 10,
    "min_interval": 0.5,
    "position": "top-right",
    "log_notifications": True
}

DEFAULT_KEYBOARD = {
    "auto_correct": True,
    "correction_delay": 0.5,
    "min_word_length": 2,
    "context_size": 3
}

DEFAULT_SERVICES = {
    "default_service": "OpenAI",
    "batch_size": 10,
    "max_retries": 3,
    "timeout": 5.0
}

def create_default_config(path: Path, default_config: Dict[str, Any]):
    """
    Crea un archivo de configuración con valores por defecto.
    
    Args:
        path: Ruta del archivo
        default_config: Configuración por defecto
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
            logger.info(f"Creado archivo de configuración: {path}")
    except Exception as e:
        logger.error(f"Error creando archivo de configuración {path}: {e}")

def load_config(path: Path) -> Dict[str, Any]:
    """
    Carga una configuración desde archivo.
    
    Args:
        path: Ruta del archivo
        
    Returns:
        Dict[str, Any]: Configuración cargada
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando configuración {path}: {e}")
        return {}

def save_config(path: Path, config: Dict[str, Any]):
    """
    Guarda una configuración en archivo.
    
    Args:
        path: Ruta del archivo
        config: Configuración a guardar
    """
    try:
        # Crear backup antes de guardar
        if path.exists():
            backup_path = path.with_suffix('.json.bak')
            shutil.copy2(path, backup_path)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            logger.info(f"Guardada configuración en {path}")
            
    except Exception as e:
        logger.error(f"Error guardando configuración {path}: {e}")

def ensure_config_files():
    """Asegura que todos los archivos de configuración existan."""
    config_files = {
        NOTIFICATIONS_CONFIG: DEFAULT_NOTIFICATIONS,
        KEYBOARD_CONFIG: DEFAULT_KEYBOARD,
        SERVICES_CONFIG: DEFAULT_SERVICES
    }
    
    for path, default_config in config_files.items():
        if not path.exists():
            create_default_config(path, default_config)

def get_config_path(name: str) -> Path:
    """
    Obtiene la ruta de un archivo de configuración.
    
    Args:
        name: Nombre del archivo (sin extensión)
        
    Returns:
        Path: Ruta completa del archivo
    """
    return CONFIG_DIR / f"{name}.json"

# Crear archivos de configuración al importar el módulo
ensure_config_files()
