from pynput import keyboard
from pynput.keyboard import Key, Controller
import time
import threading
import os
from transformers import pipeline
import torch

keyboard_controller = Controller()
text_buffer = []
word_buffer = []
correction_delay = 0.5

# Inicializar el modelo de corrección
corrector = pipeline(
    "text2text-generation",
    model="facebook/bart-large",
    device=0 if torch.cuda.is_available() else -1
)

def ai_correct_text(text):
    try:
        # Generar la corrección usando el modelo
        correction = corrector(
            text,
            max_length=100,
            do_sample=False
        )[0]['generated_text']
        
        return correction, correction != text
    except Exception as e:
        print(f"Error en corrección: {e}")
        return text, False

def correct_text():
    global text_buffer, word_buffer
    while True:
        if text_buffer:
            text = ''.join(text_buffer)
            
            if len(text.strip()) > 0:
                corrected_text, needs_correction = ai_correct_text(text)
                if needs_correction:
                    # Borrar el texto original
                    for _ in range(len(text)):
                        keyboard_controller.press(Key.backspace)
                        keyboard_controller.release(Key.backspace)
                        time.sleep(0.01)
                    
                    # Escribir la corrección
                    keyboard_controller.type(corrected_text)
                    text_buffer = list(corrected_text)
            
        time.sleep(correction_delay)

def on_press(key):
    global text_buffer, word_buffer
    try:
        if hasattr(key, 'char'):
            text_buffer.append(key.char)
            word_buffer.append(key.char)
        elif key == Key.space:
            text_buffer.append(' ')
            word_buffer = []  # Reset word buffer
        elif key == Key.backspace:
            if text_buffer:
                text_buffer.pop()
            if word_buffer:
                word_buffer.pop()
        elif key == Key.enter:
            # Modo aprendizaje: Alt + Enter para guardar la última corrección
            if keyboard.Key.alt in keyboard.Controller().pressed_keys:
                if word_buffer:
                    word = ''.join(word_buffer).lower()
                    print(f"¿Cuál es la corrección para '{word}'?")
                    correction = input()
                    if correction:
                        save_patterns(word, correction)
                        print(f"Aprendido: {word} -> {correction}")
    except AttributeError:
        pass

def on_release(key):
    if key == Key.esc:
        return False

# Cargar patrones aprendidos
learned_patterns = load_patterns()

# Iniciar el hilo de corrección
correction_thread = threading.Thread(target=correct_text, daemon=True)
correction_thread.start()

print("Corrector iniciado. Presiona Alt + Enter para enseñar nuevas correcciones.")
print("Presiona ESC para salir.")

# Iniciar el listener del teclado
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()