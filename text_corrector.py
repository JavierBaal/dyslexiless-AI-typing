import requests
import json
import time
from config_manager import load_config
import anthropic
import openai
from typing import Tuple, Optional, Callable, Any
from logger_manager import logger
from correction_cache import CorrectionCache
from functools import wraps
import random

def retry_on_error(max_retries=3, initial_delay=1, backoff_factor=2, jitter=0.1):
    """
    Decorador para reintentar funciones que pueden fallar debido a errores transitorios.
    
    Args:
        max_retries: Número máximo de reintentos
        initial_delay: Retraso inicial en segundos
        backoff_factor: Factor de incremento para el retraso entre reintentos
        jitter: Factor de aleatoriedad para evitar tormentas de reintentos
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
                    
                    # Calcular retraso con jitter para evitar tormentas de reintentos
                    jitter_value = random.uniform(-jitter, jitter)
                    sleep_time = delay * (1 + jitter_value)
                    
                    logger.warning(f"Reintento {retries}/{max_retries} después de {sleep_time:.2f}s. Error: {e}")
                    time.sleep(sleep_time)
                    
                    # Incrementar el retraso para el próximo reintento
                    delay *= backoff_factor
        
        return wrapper
    
    return decorator

class TextCorrector:
    def __init__(self):
        self.config = load_config()
        self.cache = CorrectionCache()
        self.setup_service()
        self.test_api_connection()
        logger.info("TextCorrector inicializado")
        
    def test_api_connection(self):
        """Prueba la conexión con el servicio de IA configurado para verificar que funciona correctamente."""
        try:
            service = self.config.get('service', "OpenAI")
            logger.info(f"Probando conexión con el servicio: {service}")
            
            # Texto simple para probar la corrección
            test_word = "prueba"
            test_context = "Esto es una prueba de conexión"
            
            # Intentar una corrección simple
            correction, was_corrected = self.correct_text(test_word, test_context)
            
            logger.info(f"Prueba de conexión exitosa con {service}")
            return True
        except Exception as e:
            logger.error(f"Error al probar la conexión con el servicio: {e}")
            logger.error(f"Detalles del error: {str(e)}")
            return False
        
    def setup_service(self):
        service = self.config.get('service', "OpenAI")  # Valor predeterminado si no hay servicio configurado
        
        # Definir un servicio de respaldo en caso de error
        fallback_service = None
        
        try:
            if service == "OpenAI":
                # Ya no necesitamos asignar la clave API globalmente
                # ya que creamos un cliente en el método openai_correct
                self.correct_text = self.openai_correct
                logger.info("Servicio OpenAI configurado correctamente")
            elif service == "Anthropic":
                # Inicialización actualizada para la versión más reciente de la API de Anthropic
                self.claude = anthropic.Anthropic(api_key=self.config.get('api_key'))
                self.correct_text = self.anthropic_correct
                logger.info("Servicio Anthropic configurado correctamente")
            elif service == "Mixtral":
                self.correct_text = self.mixtral_correct
                logger.info("Servicio Mixtral configurado correctamente")
            else:
                logger.warning(f"Servicio desconocido: {service}, usando OpenAI como respaldo")
                self.correct_text = self.openai_correct
                
        except Exception as e:
            logger.error(f"Error al configurar el servicio {service}: {e}")
            logger.info("Utilizando OpenAI como servicio de respaldo")
            
            # Intentar usar OpenAI como respaldo
            try:
                self.correct_text = self.openai_correct
            except Exception as fallback_error:
                logger.error(f"Error al configurar servicio de respaldo OpenAI: {fallback_error}")
                
                # Si OpenAI falla, intentar con Mixtral como segunda opción de respaldo
                try:
                    logger.info("Intentando usar Mixtral como servicio de respaldo secundario")
                    self.correct_text = self.mixtral_correct
                except Exception as second_fallback_error:
                    logger.error(f"Error al configurar servicio de respaldo Mixtral: {second_fallback_error}")
                    logger.critical("No se pudo configurar ningún servicio de corrección en línea")
                    logger.info("Utilizando corrector fallback sin conexión")
                    self.correct_text = self.fallback_correct
            
    @retry_on_error(max_retries=3, initial_delay=1)
    def openai_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """Método de corrección usando la API de OpenAI."""
        # Intentar obtener del caché primero
        cached_result = self.cache.get(word, context)
        if cached_result is not None:
            logger.info(f"Corrección encontrada en caché para: {word}")
            return cached_result

        try:
            logger.info(f"Solicitando corrección a OpenAI para: {word}")
            # Estructura actualizada para la API más reciente de OpenAI
            client = openai.OpenAI(api_key=self.config.get('api_key'))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente que corrige cualquier texto a español correcto. No expliques las correcciones, solo devuelve el texto corregido."
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
            # Registrar más detalles del error para diagnóstico
            logger.error(f"Detalles del error: {str(e)}")
            return word, False
        
    @retry_on_error(max_retries=3, initial_delay=1)
    def anthropic_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """Método de corrección usando la API de Anthropic Claude."""
        # Intentar obtener del caché primero
        cached_result = self.cache.get(word, context)
        if cached_result is not None:
            logger.info(f"Corrección encontrada en caché para: {word}")
            return cached_result

        try:
            logger.info(f"Solicitando corrección a Anthropic para: {word}")
            # Estructura actualizada para la API más reciente de Anthropic
            message = self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=50,
                temperature=0.1,
                system="Eres un asistente que corrige cualquier texto a español correcto. No expliques las correcciones, solo devuelve el texto corregido.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{context}"
                    }
                ]
            )
            # Acceso actualizado a la respuesta
            correction = message.content[0].text.strip()
            was_corrected = correction != word
            
            # Guardar en caché
            self.cache.add(word, context, correction, was_corrected)
            
            return correction, was_corrected
        except Exception as e:
            logger.error(f"Error en corrección Anthropic: {e}")
            # Registrar más detalles del error para diagnóstico
            logger.error(f"Detalles del error: {str(e)}")
            return word, False
        
    @retry_on_error(max_retries=3, initial_delay=1)
    def mixtral_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """Método de corrección usando la API de Mixtral."""
        # Intentar obtener del caché primero
        cached_result = self.cache.get(word, context)
        if cached_result is not None:
            logger.info(f"Corrección encontrada en caché para: {word}")
            return cached_result

        try:
            logger.info(f"Solicitando corrección a Mixtral para: {word}")
            response = requests.post(
                "https://api.together.xyz/inference",
                headers={
                    "Authorization": f"Bearer {self.config.get('api_key')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "prompt": f"Sistema: Eres un asistente que corrige cualquier texto a español correcto. No expliques las correcciones, solo devuelve el texto corregido.\nUsuario: {context}",
                    "temperature": 0.1,
                    "max_tokens": 50,
                    "stop": ["\n"]
                },
                timeout=10  # Añadir timeout para evitar bloqueos indefinidos
            )
            
            # Verificar el código de estado de la respuesta
            response.raise_for_status()
            
            # Procesar la respuesta JSON con manejo de errores
            response_data = response.json()
            if 'output' not in response_data or 'choices' not in response_data['output'] or not response_data['output']['choices']:
                raise ValueError("Formato de respuesta inesperado de la API de Mixtral")
                
            correction = response_data['output']['choices'][0]['text'].strip()
            was_corrected = correction != word
            
            # Guardar en caché
            self.cache.add(word, context, correction, was_corrected)
            
            return correction, was_corrected
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con la API de Mixtral: {e}")
            logger.error(f"Detalles del error: {str(e)}")
            return word, False
            
    def fallback_correct(self, word: str, context: str) -> Tuple[str, bool]:
        """
        Método de corrección de respaldo que funciona sin conexión.
        Utiliza reglas básicas y un diccionario de correcciones comunes.
        """
        # Intentar obtener del caché primero
        cached_result = self.cache.get(word, context)
        if cached_result is not None:
            logger.info(f"Corrección encontrada en caché para: {word}")
            return cached_result
            
        # Diccionario de correcciones comunes en español
        common_corrections = {
            # Errores comunes de dislexia
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
            "nesecito": "necesito",
            "colejio": "colegio",
            "vijilante": "vigilante",
            "ajente": "agente",
            "urjente": "urgente",
            "jente": "gente",
            "vijente": "vigente",
            "intelijente": "inteligente",
            "orijinal": "original",
            "relijion": "religión",
            "imajinar": "imaginar",
            "imájen": "imagen",
            "reflecsion": "reflexión",
            "reflecsionar": "reflexionar",
            "reflecsivo": "reflexivo",
            "conección": "conexión",
            "coneccion": "conexión",
            "conecxion": "conexión",
            "exito": "éxito",
            "examen": "examen",
            "espresion": "expresión",
            "espreso": "expreso",
            "esplicar": "explicar",
            "esplicacion": "explicación",
            "estrangero": "extranjero",
            "estension": "extensión",
            "estender": "extender",
            "esterno": "externo",
            "estracto": "extracto",
            "estraño": "extraño",
            "estranjero": "extranjero",
            "estricto": "estricto",
            "escusa": "excusa",
            "esperiencia": "experiencia",
            "esperimento": "experimento",
            "esperto": "experto",
            "esposicion": "exposición",
            "esponer": "exponer",
            "espuesto": "expuesto",
            "espresion": "expresión",
            "espresar": "expresar",
            "espreso": "expreso",
            "espropiar": "expropiar",
            "espulsar": "expulsar",
            "estender": "extender",
            "estenso": "extenso",
            "estension": "extensión",
            "esterior": "exterior",
            "esterno": "externo",
            "estinguir": "extinguir",
            "estinto": "extinto",
            "estraer": "extraer",
            "estraño": "extraño",
            "estrangero": "extranjero",
            "estraviar": "extraviar",
            "estremo": "extremo"
        }
        
        # Convertir a minúsculas para la búsqueda
        word_lower = word.lower()
        
        # Verificar si la palabra está en el diccionario de correcciones
        if word_lower in common_corrections:
            correction = common_corrections[word_lower]
            
            # Preservar mayúsculas si la palabra original comienza con mayúscula
            if word and word[0].isupper():
                correction = correction.capitalize()
                
            # Guardar en caché
            self.cache.add(word, context, correction, True)
            
            logger.info(f"Corrección fallback: {word} → {correction}")
            return correction, True
            
        # Si no hay corrección disponible, devolver la palabra original
        return word, False
