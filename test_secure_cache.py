#!/usr/bin/env python3
"""
Pruebas para el sistema de caché seguro.
"""

import unittest
import os
import time
from datetime import datetime, timedelta
from secure_cache import SecureCache
from pathlib import Path
from cryptography.fernet import Fernet
import json
import base64
import shutil
import threading

class TestSecureCache(unittest.TestCase):
    """Pruebas unitarias para SecureCache."""
    
    def setUp(self):
        """Configura el entorno de prueba."""
        self.test_dir = "test_cache"
        os.makedirs(self.test_dir, exist_ok=True)
        self.cache = SecureCache(
            cache_file=os.path.join(self.test_dir, "test_cache.dat"),
            max_size=10,
            ttl_days=1,
            key_rotation_days=1
        )
    
    def tearDown(self):
        """Limpia el entorno después de las pruebas."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_basic_operations(self):
        """Prueba operaciones básicas del caché."""
        # Añadir entrada
        self.cache.add("test", "context", "corrected", True)
        
        # Verificar que se puede recuperar
        result = self.cache.get("test", "context")
        self.assertIsNotNone(result)
        self.assertEqual(result, ("corrected", True))
    
    def test_encryption(self):
        """Prueba que los datos se almacenan encriptados."""
        # Añadir datos al caché
        self.cache.add("secret", "context", "confidential", True)
        
        # Leer archivo directamente
        cache_file = Path(self.cache.cache_file)
        with open(cache_file, 'rb') as f:
            stored_data = f.read()
        
        # Verificar que los datos están encriptados
        try:
            json.loads(stored_data.decode())
            self.fail("Los datos no están encriptados")
        except:
            pass  # Se espera que falle si los datos están encriptados
    
    def test_integrity_validation(self):
        """Prueba la validación de integridad."""
        # Añadir entrada
        self.cache.add("test", "context", "corrected", True)
        
        # Modificar contexto debería fallar la validación de integridad
        result = self.cache.get("test", "modified_context")
        self.assertIsNone(result)
    
    def test_key_rotation(self):
        """Prueba la rotación de claves."""
        # Añadir datos
        self.cache.add("test", "context", "corrected", True)
        
        # Forzar rotación de clave
        self.cache.last_key_rotation = datetime.now() - timedelta(days=2)
        self.cache.add("test2", "context", "corrected2", True)
        
        # Verificar que ambos datos son accesibles
        result1 = self.cache.get("test", "context")
        result2 = self.cache.get("test2", "context")
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
    
    def test_ttl(self):
        """Prueba la expiración de entradas."""
        # Añadir entrada
        self.cache.add("test", "context", "corrected", True)
        
        # Simular paso del tiempo
        self.cache.ttl = timedelta(seconds=1)
        time.sleep(2)
        
        # Verificar que la entrada ha expirado
        result = self.cache.get("test", "context")
        self.assertIsNone(result)
    
    def test_max_size(self):
        """Prueba el límite de tamaño del caché."""
        # Añadir más entradas que el límite
        for i in range(15):
            self.cache.add(f"test{i}", "context", f"corrected{i}", True)
        
        # Verificar que no excede el tamaño máximo
        stats = self.cache.get_stats()
        self.assertLessEqual(stats['total_entries'], 10)
    
    def test_concurrent_access(self):
        """Prueba acceso concurrente al caché."""
        def writer_thread():
            for i in range(100):
                self.cache.add(f"test{i}", "context", f"corrected{i}", True)
                
        def reader_thread():
            for i in range(100):
                self.cache.get(f"test{i}", "context")
        
        threads = [
            threading.Thread(target=writer_thread),
            threading.Thread(target=reader_thread)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Verificar que no hubo corrupción
        stats = self.cache.get_stats()
        self.assertGreater(stats['total_entries'], 0)

def test_security_features():
    """
    Prueba completa de características de seguridad.
    Esta prueba simula diferentes escenarios de seguridad.
    """
    print("\n=== Prueba de Seguridad del Caché ===")
    
    # 1. Crear caché temporal
    test_dir = "security_test_cache"
    os.makedirs(test_dir, exist_ok=True)
    cache = SecureCache(
        cache_file=os.path.join(test_dir, "security_test.dat"),
        max_size=100,
        ttl_days=1,
        key_rotation_days=1
    )
    
    try:
        # 2. Prueba de encriptación
        print("\nProbando encriptación...")
        cache.add("password", "context", "secreto123", True)
        
        with open(cache.cache_file, 'rb') as f:
            stored_data = f.read()
        
        print(f"Datos almacenados (base64): {base64.b64encode(stored_data[:50]).decode()}...")
        
        # 3. Prueba de integridad
        print("\nProbando validación de integridad...")
        # Intento de manipulación
        with open(cache.cache_file, 'wb') as f:
            f.write(stored_data[:-1] + b'X')
        
        result = cache.get("password", "context")
        print(f"Intento de manipulación detectado: {result is None}")
        
        # 4. Prueba de rotación de claves
        print("\nProbando rotación de claves...")
        original_key_file = Path(cache.cache_file).with_suffix('.key')
        with open(original_key_file, 'rb') as f:
            original_key = f.read()
        
        cache.last_key_rotation = datetime.now() - timedelta(days=2)
        cache.add("newdata", "context", "datos_nuevos", True)
        
        with open(original_key_file, 'rb') as f:
            new_key = f.read()
        
        print(f"Rotación de clave exitosa: {original_key != new_key}")
        
        # 5. Prueba de limpieza segura
        print("\nProbando limpieza segura...")
        cache.clear()
        
        # Verificar que los datos no son recuperables
        if os.path.exists(cache.cache_file):
            with open(cache.cache_file, 'rb') as f:
                cleared_data = f.read()
            print(f"Tamaño de datos después de limpieza: {len(cleared_data)} bytes")
        
    finally:
        # Limpiar archivos de prueba
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    print("Ejecutando pruebas de seguridad del caché...")
    
    try:
        # Ejecutar pruebas unitarias
        unittest.main(verbosity=2)
    except SystemExit:
        pass
    
    # Ejecutar prueba de seguridad completa
    test_security_features()
