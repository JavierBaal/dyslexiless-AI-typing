#!/usr/bin/env python3
"""
Ejemplo básico de uso de DyslexiLess.
Demuestra la configuración básica y el uso del corrector de texto.
"""

from dyslexiless import initialize_application, get_service
from interfaces import ICorrector, INotifier

def main():
    # Inicializar la aplicación
    initialize_application()
    
    # Obtener servicios necesarios
    corrector = get_service(ICorrector)
    notifier = get_service(INotifier)
    
    # Ejemplo de corrección
    word = "qe"
    context = "creo qe esto funciona"
    
    corrected_text, was_corrected = corrector.correct_text(word, context)
    
    if was_corrected:
        notifier.notify(
            f"Corregido: {word} → {corrected_text}",
            "info",
            "✅"
        )
    else:
        print(f"No se necesitó corrección para '{word}'")

if __name__ == "__main__":
    main()
