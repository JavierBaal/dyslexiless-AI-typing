from pynput import keyboard
from pynput.keyboard import Key, Controller
import queue
import threading
import time
from text_corrector import TextCorrector
import os
from logger_manager import logger

class KeyboardListener:
    def __init__(self):
        self.word_queue = queue.Queue()
        self.current_sentence = []
        self.words_buffer = []
        self.corrector = TextCorrector()
        self.keyboard = Controller()
        self.is_backspacing = False
        self.corrections_count = 0
        self.total_words = 0
        logger.info("Iniciando KeyboardListener")
        self.notify("DyslexiLess iniciado y monitoreando", "✨")
        
    def notify(self, message, icon=""):
        notification_text = f"{icon} {message}" if icon else message
        os.system(f"""
            osascript -e 'display notification "{notification_text}" with title "DyslexiLess"'
        """)
        logger.info(message)

    def on_press(self, key):
        try:
            # Manejar backspace
            if key == Key.backspace:
                self.is_backspacing = True
                if self.current_sentence:
                    self.current_sentence.pop()
                return

            if hasattr(key, 'char'):
                self.current_sentence.append(key.char)
                logger.debug(f"Buffer actual: {''.join(self.current_sentence)}")
            elif key == Key.space and not self.is_backspacing:
                if self.current_sentence:
                    word = ''.join(self.current_sentence)
                    self.words_buffer.append(word)
                    self.current_sentence = []
                    self.total_words += 1
                    logger.debug(f"Palabra añadida: {word}")
                    
                    if len(self.words_buffer) >= 3:
                        self.process_correction()
            
            self.is_backspacing = False
                
        except AttributeError as e:
            logger.error(f"Error en procesamiento de tecla: {e}")

    def apply_correction(self, original_text, corrected_text):
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

    def process_correction(self):
        if len(self.words_buffer) < 3:
            return
            
        text_to_correct = ' '.join(self.words_buffer)
        word_to_correct = self.words_buffer[0]
        
        corrected_text, was_corrected = self.corrector.correct_text(word_to_correct, text_to_correct)
        
        if was_corrected:
            self.corrections_count += 1
            success_rate = (self.corrections_count / self.total_words) * 100 if self.total_words > 0 else 0
            self.notify(
                f"Corrigiendo: {word_to_correct} → {corrected_text}\n"
                f"Tasa de corrección: {success_rate:.1f}%",
                "✅"
            )
            self.apply_correction(word_to_correct, corrected_text)
            
        self.words_buffer.pop(0)

def start_listener():
    try:
        listener = KeyboardListener()
        keyboard_listener = keyboard.Listener(on_press=listener.on_press)
        keyboard_listener.start()
        logger.info("Listener iniciado exitosamente")
        return listener
    except Exception as e:
        logger.error(f"Error al iniciar el listener: {e}")
        raise
