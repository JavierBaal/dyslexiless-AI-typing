import pyperclip
import requests
import time
from pynput.keyboard import Controller, Key
from fastapi import FastAPI
import uvicorn
import os

keyboard = Controller()
app = FastAPI()

def notify(message):
    os.system(f"""
        osascript -e 'display notification "{message}" with title "Dyslexia Helper"'
    """)

def get_selected_text():
    # Guardar el contenido actual del portapapeles
    original_clipboard = pyperclip.paste()
    
    # Copiar texto seleccionado
    keyboard.press(Key.cmd)
    keyboard.press('c')
    keyboard.release('c')
    keyboard.release(Key.cmd)
    time.sleep(0.2)  # Aumentamos el tiempo de espera
    
    selected_text = pyperclip.paste()
    
    # Restaurar el portapapeles original
    time.sleep(0.1)
    pyperclip.copy(original_clipboard)
    
    return selected_text

def paste_corrected_text(corrected_text):
    if not corrected_text:
        return
        
    # Guardar el contenido actual del portapapeles
    original_clipboard = pyperclip.paste()
    
    # Copiar el texto corregido al portapapeles
    pyperclip.copy(corrected_text)
    time.sleep(0.1)
    
    # Pegar el texto corregido
    keyboard.press(Key.cmd)
    keyboard.press('v')
    keyboard.release('v')
    keyboard.release(Key.cmd)
    
    # Restaurar el portapapeles original
    time.sleep(0.2)
    pyperclip.copy(original_clipboard)

@app.post("/correct")
async def correct_text():
    try:
        text = get_selected_text()
        if not text:
            notify("No text selected!")
            return {"status": "error", "message": "No text selected"}

        # Aquí implementamos una corrección simple
        # (después podemos conectar con una API más sofisticada)
        corrected_text = text.strip()
        
        # Ejemplo de correcciones básicas
        common_fixes = {
            "q": "que",
            "xq": "porque",
            "pq": "porque",
            "tb": "también",
            "tmb": "también"
        }
        
        words = corrected_text.split()
        corrected_words = [common_fixes.get(word.lower(), word) for word in words]
        corrected_text = " ".join(corrected_words)
        
        # Notificar al usuario
        notify(f"Original: {text}\nCorregido: {corrected_text}")
        
        # Pegar el texto corregido
        paste_corrected_text(corrected_text)
        
        return {"status": "success", "original": text, "corrected": corrected_text}
        
    except Exception as e:
        notify(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    notify("Server started!")
    uvicorn.run(app, host="127.0.0.1", port=8000)