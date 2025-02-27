#!/usr/bin/env python3
"""
Monitor de teclado optimizado con inyección de dependencias.
"""

from pynput import keyboard
from pynput.keyboard import Key, Controller
import threading
import time
from typing import List, Deque
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from interfaces import ICorrector, INotifier, ITextBuffer, IInputMonitor
from dependency_container import DependencyContainer
from logger_manager import logger

@dataclass
class BufferStats:
    """Estadísticas del buffer para monitoreo de memoria."""
    total_chars: int = 0
    max_chars: int = 1000  # Límite de caracteres
    buffer_usage: float = 0.0
    last_cleanup: datetime = datetime.now()

class OptimizedBuffer(ITextBuffer):
    """Buffer optimizado para manejo eficiente de texto."""
    
    def __init__(self, max_size: int = 1000):
        self.chars: Deque[str] = deque(maxlen=max_size)
        self.words: Deque[str] = deque(maxlen=50)
        self.stats = BufferStats(max_chars=max_size)
        
    def add_char(self, char: str):
        """Añade un carácter al buffer."""
        self.chars.append(char)
        self.stats.total_chars = len(self.chars)
        self.stats.buffer_usage = self.stats.total_chars / self.stats.max_chars
        
    def add_word(self, word: str):
        """Añade una palabra al buffer."""
        self.words.append(word)
        
    def pop_char(self) -> str:
        """Elimina y retorna el último carácter."""
        if self.chars:
            self.stats.total_chars -= 1
            return self.chars.pop()
        return ""
        
    def clear(self):
        """Limpia el buffer."""
        self.chars.clear()
        self.stats.total_chars = 0
        
    def get_word(self) -> str:
        """Obtiene la palabra actual del buffer."""
        return "".join(self.chars)
        
    def get_context(self) -> str:
        """Obtiene el contexto actual."""
        return " ".join(list(self.words)[-3:])  # Últimas 3 palabras
        
    def cleanup(self):
        """Realiza limpieza periódica del buffer."""
        now = datetime.now()
        if now - self.stats.last_cleanup > timedelta(minutes=5):
            self.stats.last_cleanup = now
            if self.stats.buffer_usage > 0.8:  # 80% utilización
                # Mantener solo las últimas 10 palabras
                old_words = list(self.words)[:-10]
                self.words.clear()
                self.words.extend(old_words)
                logger.info(f"Buffer cleanup: {len(old_words)} palabras eliminadas")

class KeyboardListener(IInputMonitor):
    def __init__(self, corrector: ICorrector, buffer: ITextBuffer, notifier: INotifier):
        self.buffer = buffer
        self.corrector = corrector
        self.notifier = notifier
        self.keyboard = Controller()
        self.is_backspacing = False
        self.corrections_count = 0
        self.total_words = 0
        self.is_paused = False
        self.current_word = None  # Palabra actual siendo procesada
        logger.info("Iniciando KeyboardListener")
        self.notifier.notify("DyslexiLess iniciado y monitoreando", "info", "✨")
        
    def start(self):
        """Inicia el monitor de teclado."""
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()
        logger.info("Monitor de teclado iniciado")
        
    def stop(self):
        """Detiene el monitor de teclado."""
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        logger.info("Monitor de teclado detenido")
        
    def pause(self):
        """Pausa el monitoreo."""
        self.is_paused = True
        logger.info("Monitor de teclado pausado")
        
    def resume(self):
        """Reanuda el monitoreo."""
        self.is_paused = False
        logger.info("Monitor de teclado reanudado")

    def on_press(self, key):
        if self.is_paused:
            return
            
        try:
            # Manejar backspace
            if key == Key.backspace:
                self.is_backspacing = True
                self.buffer.pop_char()
                self.current_word = None  # Cancelar corrección pendiente
                return

            if hasattr(key, 'char'):
                self.buffer.add_char(key.char)
                logger.debug(f"Buffer actual: {self.buffer.get_word()}")
            elif key == Key.space and not self.is_backspacing:
                word = self.buffer.get_word()
                if word:
                    self.buffer.add_word(word)
                    self.buffer.clear()
                    self.total_words += 1
                    logger.debug(f"Palabra añadida: {word}")
                    
                    # Procesar corrección si tenemos contexto
                    context = self.buffer.get_context()
                    if context:
                        self.process_correction(word, context)
            
            self.is_backspacing = False
                
        except AttributeError as e:
            logger.error(f"Error en procesamiento de tecla: {e}")
        except Exception as e:
            logger.error(f"Error inesperado: {e}")

    def apply_correction(self, original_text: str, corrected_text: str):
        """Aplica una corrección reemplazando el texto original."""
        if self.is_backspacing:
            return
            
        cursor_position = len(original_text) + 1  # +1 por el espacio
        
        # Mover cursor atrás
        for _ in range(cursor_position):
            self.keyboard.press(Key.left)
            self.keyboard.release(Key.left)
            time.sleep(0.01)
        
        # Borrar texto original
        for _ in range(len(original_text)):
            self.keyboard.press(Key.delete)
            self.keyboard.release(Key.delete)
            time.sleep(0.01)
        
        # Escribir corrección
        self.keyboard.type(corrected_text)
        
        # Volver a la posición original
        self.keyboard.press(Key.right)
        self.keyboard.release(Key.right)

    def correction_callback(self, correction: str, was_corrected: bool):
        """Callback para procesar el resultado de una corrección."""
        if was_corrected and not self.is_backspacing and self.current_word:
            self.corrections_count += 1
            success_rate = (self.corrections_count / self.total_words) * 100 if self.total_words > 0 else 0
            
            # Notificar corrección
            self.notifier.notify(
                f"Corrigiendo: {self.current_word} → {correction}\n"
                f"Tasa de corrección: {success_rate:.1f}%",
                "info",
                "✅"
            )
            
            # Aplicar corrección
            self.apply_correction(self.current_word, correction)
            self.current_word = None

    def process_correction(self, word: str, context: str):
        """
        Procesa la corrección de una palabra con su contexto.
        Ahora usa el sistema de procesamiento por lotes.
        """
        if not word or not context:
            return
        
        # Guardar palabra actual para el callback
        self.current_word = word
        
        # Añadir tarea de corrección al procesador por lotes
        # La prioridad se basa en la longitud del contexto
        priority = min(len(context.split()), 5)  # Máximo 5
        self.corrector.batch_processor.add_task(
            word,
            context,
            self.correction_callback,
            priority=priority
        )
            
        # Realizar limpieza periódica del buffer
        self.buffer.cleanup()

def create_listener() -> IInputMonitor:
    """
    Fábrica para crear una instancia del monitor de teclado.
    Utiliza el contenedor de dependencias para resolver las dependencias.
    """
    try:
        container = DependencyContainer()
        container.register(ITextBuffer, OptimizedBuffer, singleton=True)
        container.register(IInputMonitor, KeyboardListener)
        
        listener = container.resolve(IInputMonitor)
        listener.start()
        logger.info("Monitor de teclado creado exitosamente")
        return listener
    except Exception as e:
        logger.error(f"Error al crear el monitor de teclado: {e}")
        raise
