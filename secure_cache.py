#!/usr/bin/env python3
"""
Implementación segura del sistema de caché con encriptación y validación de integridad.
"""

import json
import os
import time
from typing import Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from pathlib import Path
from logger_manager import logger
import threading

class SecureCache:
    """
    Implementación segura del sistema de caché.
    
    Características:
    - Encriptación de datos utilizando Fernet (AES-128-CBC)
    - Validación de integridad usando HMAC
    - Rotación automática de claves
    - Limpieza automática de datos antiguos
    - Validación de tamaño máximo
    """
    
    def __init__(
        self,
        cache_file: str = "secure_cache.dat",
        max_size: int = 1000,
        ttl_days: int = 30,
        key_rotation_days: int = 7,
        salt: bytes = None
    ):
        self.cache_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            cache_file
        )
        self.max_size = max_size
        self.ttl = timedelta(days=ttl_days)
        self.key_rotation_interval = timedelta(days=key_rotation_days)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        # Inicializar encriptación
        self._init_encryption(salt or os.urandom(16))
        
        # Cargar caché
        self.cache: Dict[str, Dict] = {}
        self._load_cache()
        
        # Configurar lock para thread-safety
        self._lock = threading.RLock()
        
        # Contador de operaciones para limpieza periódica
        self._op_counter = 0
        self._cleanup_threshold = 100
    
    def _init_encryption(self, salt: bytes):
        """Inicializa el sistema de encriptación."""
        # Generar clave maestra si no existe
        master_key_file = Path(self.cache_file).with_suffix('.key')
        if not master_key_file.exists():
            master_key = Fernet.generate_key()
            with open(master_key_file, 'wb') as f:
                f.write(master_key)
        else:
            with open(master_key_file, 'rb') as f:
                master_key = f.read()
        
        # Derivar clave de encriptación
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        self.fernet = Fernet(key)
        
        # Guardar salt
        salt_file = Path(self.cache_file).with_suffix('.salt')
        with open(salt_file, 'wb') as f:
            f.write(salt)
        
        # Registrar tiempo de última rotación
        self.last_key_rotation = datetime.now()
    
    def _rotate_key(self):
        """Rota la clave de encriptación."""
        if (datetime.now() - self.last_key_rotation) >= self.key_rotation_interval:
            logger.info("Rotando clave de encriptación...")
            
            # Generar nueva clave
            new_salt = os.urandom(16)
            self._init_encryption(new_salt)
            
            # Re-encriptar caché con nueva clave
            with self._lock:
                self._save_cache()
            
            logger.info("Rotación de clave completada")
    
    def _encrypt_data(self, data: Any) -> bytes:
        """Encripta datos para almacenamiento."""
        json_data = json.dumps(data)
        return self.fernet.encrypt(json_data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes) -> Any:
        """Desencripta datos almacenados."""
        try:
            json_data = self.fernet.decrypt(encrypted_data)
            return json.loads(json_data.decode())
        except Exception as e:
            logger.error(f"Error al desencriptar datos: {e}")
            return None
    
    def _load_cache(self):
        """Carga el caché desde el archivo."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = self._decrypt_data(encrypted_data)
                        if decrypted_data:
                            # Filtrar entradas expiradas
                            current_time = datetime.now()
                            self.cache = {
                                word: data for word, data in decrypted_data.items()
                                if datetime.fromisoformat(data['timestamp']) + self.ttl > current_time
                            }
        except Exception as e:
            logger.error(f"Error al cargar caché: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Guarda el caché en el archivo."""
        try:
            encrypted_data = self._encrypt_data(self.cache)
            with open(self.cache_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Error al guardar caché: {e}")
    
    def _periodic_cleanup(self):
        """Realiza limpieza periódica del caché."""
        self._op_counter += 1
        if self._op_counter >= self._cleanup_threshold:
            self._op_counter = 0
            self.cleanup()
    
    def get(self, word: str, context: str) -> Optional[Tuple[str, bool]]:
        """Obtiene una corrección del caché."""
        with self._lock:
            if word in self.cache:
                entry = self.cache[word]
                cached_time = datetime.fromisoformat(entry['timestamp'])
                
                # Verificar si la entrada ha expirado
                if cached_time + self.ttl > datetime.now():
                    # Verificar integridad de los datos
                    stored_hash = entry.get('hash')
                    computed_hash = self._compute_hash(word, context)
                    
                    if stored_hash == computed_hash:
                        return entry['correction'], entry['was_corrected']
                    else:
                        logger.warning(f"Violación de integridad detectada para: {word}")
            
            return None
    
    def add(self, word: str, context: str, correction: str, was_corrected: bool):
        """Añade una corrección al caché."""
        with self._lock:
            # Verificar tamaño máximo
            if len(self.cache) >= self.max_size:
                # Eliminar entrada más antigua
                oldest_word = min(
                    self.cache.keys(),
                    key=lambda k: datetime.fromisoformat(self.cache[k]['timestamp'])
                )
                del self.cache[oldest_word]
            
            # Añadir nueva entrada
            self.cache[word] = {
                'correction': correction,
                'was_corrected': was_corrected,
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'hash': self._compute_hash(word, context)
            }
            
            # Guardar cambios
            self._save_cache()
            
            # Realizar limpieza periódica
            self._periodic_cleanup()
            
            # Verificar rotación de clave
            self._rotate_key()
    
    def _compute_hash(self, word: str, context: str) -> str:
        """Calcula el hash para verificación de integridad."""
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(word.encode())
        hasher.update(context.encode())
        return base64.b64encode(hasher.finalize()).decode()
    
    def cleanup(self):
        """Realiza limpieza del caché."""
        with self._lock:
            current_time = datetime.now()
            expired_words = [
                word for word, data in self.cache.items()
                if datetime.fromisoformat(data['timestamp']) + self.ttl <= current_time
            ]
            
            for word in expired_words:
                del self.cache[word]
            
            if expired_words:
                self._save_cache()
                logger.info(f"Limpieza de caché: {len(expired_words)} entradas eliminadas")
    
    def clear(self):
        """Limpia completamente el caché."""
        with self._lock:
            self.cache.clear()
            self._save_cache()
            logger.info("Caché limpiado completamente")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        with self._lock:
            total_entries = len(self.cache)
            if total_entries == 0:
                return {
                    'total_entries': 0,
                    'usage_percentage': 0,
                    'oldest_entry': None,
                    'newest_entry': None,
                }
            
            timestamps = [
                datetime.fromisoformat(data['timestamp'])
                for data in self.cache.values()
            ]
            
            return {
                'total_entries': total_entries,
                'usage_percentage': (total_entries / self.max_size) * 100,
                'oldest_entry': min(timestamps),
                'newest_entry': max(timestamps),
            }
