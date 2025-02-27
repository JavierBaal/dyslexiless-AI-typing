#!/usr/bin/env python3
"""
Servicio de corrección de texto con soporte para múltiples proveedores de IA.
"""

import time
from typing import Tuple, Optional, Dict, Any
from interfaces import ICorrector, ICache
from secure_cache import SecureCache
from circuit_breaker import with_circuit_breaker
from logger_manager import logger
import openai
import anthropic
import requests
from functools import wraps
import random

def retry_on_error(max_retries=3, initial_delay=1, backoff_factor=2, jitter=0.1):
    """
    Decorador para reintentar operaciones que pueden fallar.
    
    Args:
        max_retries: Número máximo de reintentos
        initial_delay: Retraso inicial en segundos
        backoff_factor: Factor de incremento para el retraso
        jitter: Factor de aleatoriedad para evitar tormentas
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Máximo de reintentos alcanzado ({max_retries}). Error: {e}")
                        raise
                    
                    jitter_value = random.uniform(-jitter, jitter)
                    sleep_time = delay * (1 + jitter_value)
                    
                    logger.warning(f"Reintento {retries}/{max_retries} después de {sleep_time:.2f}s. Error: {e}")
                    time.sleep(sleep_time)
                    
                    delay *= backoff_factor
        
        return wrapper
    return decorator

def fallback_correction(word: str, context: str) -> Tuple[str, bool]:
    """
    Corrección local cuando los servicios de IA no están disponibles.
    
    Args:
        word: Palabra a corregir
        context: Contexto de la palabra
        
    Returns:
        Tuple[str, bool]: (texto corregido, si fue corregido)
    """
    # Diccionario de correcciones comunes en español
    common_corrections = {
        "qe": "que",
        "qeu": "que",
        "pq": "porque",
        "xq": "porque",
        "porqe": "porque",
        "kiero": "quiero",
        "aser": "hacer",
        "ablar": "hablar",
        "aver": "haber",
        "ai": "hay",
        "ahi": "ahí",
        "ahy": "ahí",
        "voi": "voy",
        "soi": "soy",
        "mui": "muy",
        "oi": "hoy",
        "ves": "vez",
        "veses": "veces",
        "enpesar": "empezar",
        "entonses": "entonces",
        "inportante": "importante",
        "tanbien": "también",
        "tanvien": "también",
        "desir": "decir",
        "dise": "dice",
        "nesesito": "necesito",
        "nesecito": "necesito"
    }
    
    word_lower = word.lower()
    if word_lower in common_corrections:
        correction = common_corrections[word_lower]
        if word[0].isupper():
            correction = correction.capitalize()
        return correction, True
    
    return word, False

class TextCorrector(ICorrector):
    """
    Implementación del corrector de texto con soporte para múltiples servicios.
    """
    
    def __init__(self, cache: ICache, batch_size: int = 10):
        """
        Inicializa el corrector.
        
        Args:
            cache: Sistema de caché para optimizar correcciones
            batch_size: Tamaño máximo de lote para procesamiento
        """
        self.cache = cache
        self.config = self._load_config()
        self.batch_processor = BatchProcessor(
            self,  # El corrector mismo implementa ICorrector
            batch_size=batch_size,
            max_delay=0.2,  # 200ms máximo de espera
            min_batch_items=3
        )
        self.setup_service()
        logger.info("TextCorrector inicializado")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración del corrector."""
        from config_manager import load_config
        return load_config()
    
    def test_connection(self) -> bool:
        """Prueba la conexión con el servicio configurado."""
        try:
            # Prioridad alta para prueba de conexión
            future_result = asyncio.Future()
            
            def callback(correction: str, was_corrected: bool):
                if not future_result.done():
                    future_result.set_result((correction, was_corrected))
            
            self.batch_processor.add_task(
                "prueba",
                "Esto es una prueba",
                callback,
                priority=5  # Máxima prioridad
            )
            
            # Esperar resultado con timeout
            try:
                asyncio.get_event_loop().run_until_complete(
                    asyncio.wait_for(future_result, timeout=5.0)
                )
                return True
            except asyncio.TimeoutError:
                logger.error("Timeout al probar conexión")
                return False
                
        except Exception as e:
            logger.error(f"Error al probar conexión: {e}")
            return False
    
    def setup_service(self):
        """Configura el servicio de corrección seleccionado."""
        self.service = self.config.get('service', "OpenAI")
        logger.info(f"Servicio configurado: {self.service}")
        
    def correct_text(self, word: str, context: str) -> Tuple[str, bool]:
        """
        Corrige un texto usando el servicio configurado.
        Esta implementación se usa cuando el corrector es llamado directamente,
        no a través del BatchProcessor.
        """
        service_map = {
            "OpenAI": self.openai_correct,
            "Anthropic": self.anthropic_correct,
            "Mixtral": self.mixtral_correct
        }
        
        correction_func = service_map.get(self.service, self.fallback_correct)
        return correction_func(word, context)
    
    @retry_on_error(max_retries=3, initial_delay=1)
    @with_circuit_breaker("openai", fallback=fallback_correction)
    def openai_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """Corrección usando OpenAI."""
        # Intentar obtener del caché primero
        cached = self.cache.get(word, context)
        if cached is not None:
            return cached
        
        try:
            client = openai.OpenAI(api_key=self.config.get('api_key'))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente que corrige texto a español correcto."
                    },
                    {
                        "role": "user",
                        "content": f"{context}"
                    }
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            correction = response.choices[0].message.content.strip()
            was_corrected = correction != word
            
            # Guardar en caché
            self.cache.add(word, context, correction, was_corrected)
            
            return correction, was_corrected
            
        except Exception as e:
            logger.error(f"Error en corrección OpenAI: {e}")
            raise
    
    @retry_on_error(max_retries=3, initial_delay=1)
    @with_circuit_breaker("anthropic", fallback=fallback_correction)
    def anthropic_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """Corrección usando Anthropic Claude."""
        cached = self.cache.get(word, context)
        if cached is not None:
            return cached
        
        try:
            client = anthropic.Anthropic(api_key=self.config.get('api_key'))
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=50,
                temperature=0.1,
                system="Eres un asistente que corrige texto a español correcto.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{context}"
                    }
                ]
            )
            
            correction = message.content[0].text.strip()
            was_corrected = correction != word
            
            self.cache.add(word, context, correction, was_corrected)
            return correction, was_corrected
            
        except Exception as e:
            logger.error(f"Error en corrección Anthropic: {e}")
            raise
    
    @retry_on_error(max_retries=3, initial_delay=1)
    @with_circuit_breaker("mixtral", fallback=fallback_correction)
    def mixtral_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """Corrección usando Mixtral."""
        cached = self.cache.get(word, context)
        if cached is not None:
            return cached
            
        try:
            response = requests.post(
                "https://api.together.xyz/inference",
                headers={
                    "Authorization": f"Bearer {self.config.get('api_key')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "prompt": f"Sistema: Eres un asistente que corrige texto a español correcto.\nUsuario: {context}",
                    "temperature": 0.1,
                    "max_tokens": 50,
                    "stop": ["\n"]
                },
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'output' not in data or 'choices' not in data['output']:
                raise ValueError("Formato de respuesta inválido")
                
            correction = data['output']['choices'][0]['text'].strip()
            was_corrected = correction != word
            
            self.cache.add(word, context, correction, was_corrected)
            return correction, was_corrected
            
        except Exception as e:
            logger.error(f"Error en corrección Mixtral: {e}")
            raise
    
    def fallback_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """Corrección usando el sistema fallback local."""
        # Intentar obtener del caché primero
        cached = self.cache.get(word, context)
        if cached is not None:
            return cached
        
        correction, was_corrected = fallback_correction(word, context)
        
        # Guardar en caché si hubo corrección
        if was_corrected:
            self.cache.add(word, context, correction, True)
        
        return correction, was_corrected
        
    def __del__(self):
        """Limpieza al destruir el objeto."""
        if hasattr(self, 'batch_processor'):
            self.batch_processor.stop()
