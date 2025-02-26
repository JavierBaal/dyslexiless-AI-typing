from pynput import keyboard
from pynput.keyboard import Key, Controller
import queue
import threading
import time
from text_corrector import TextCorrector
import os

class KeyboardListener:
    def __init__(self):
        self.word_queue = queue.Queue()
        self.current_sentence = []
        self.words_buffer = []
        self.corrector = TextCorrector()
        self.keyboard = Controller()
        self.is_backspacing = False
        self.notify("DyslexiLess iniciado y monitoreando")
        
    def notify(self, message):
        os.system(f"""
            osascript -e 'display notification "{message}" with title "DyslexiLess"'
        """)
        print(f"DyslexiLess: {message}")

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
                print(f"Buffer actual: {''.join(self.current_sentence)}")
            elif key == Key.space and not self.is_backspacing:
                if self.current_sentence:
                    word = ''.join(self.current_sentence)
                    self.words_buffer.append(word)
                    self.current_sentence = []
                    self.notify(f"Palabra añadida: {word}")
                    
                    if len(self.words_buffer) >= 3:
                        self.process_correction()
            
            self.is_backspacing = False
                
        except AttributeError as e:
            print(f"Error: {e}")

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
            self.notify(f"Corrigiendo: {word_to_correct} → {corrected_text}")
            self.apply_correction(word_to_correct, corrected_text)
            
        self.words_buffer.pop(0)

def start_listener():
    listener = KeyboardListener()
    keyboard_listener = keyboard.Listener(on_press=listener.on_press)
    keyboard_listener.start()
    print("Listener iniciado")
    return listener