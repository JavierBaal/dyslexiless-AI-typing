#!/usr/bin/env python3
"""
Generador de datos de prueba para DyslexiLess.
Crea conjuntos de datos aleatorios para pruebas de carga y rendimiento.
"""

import random
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse
from datetime import datetime, timedelta

# Lista de errores comunes en español
COMMON_MISSPELLINGS = {
    "que": ["qe", "ke", "q", "k"],
    "porque": ["xq", "pq", "porqe", "porke"],
    "hacer": ["aser", "acer", "haser"],
    "había": ["abia", "avia", "habia"],
    "hay": ["ai", "ay", "hai"],
    "hoy": ["oi", "oy"],
    "ahí": ["ai", "ay", "ahi"],
    "voy": ["boy", "voi"],
    "bien": ["vien", "bn"],
    "también": ["tambien", "tamien", "tb"],
    "aquí": ["aki", "akí", "aqui"],
    "tiempo": ["tienpo", "tiempo", "tiemp"],
    "siempre": ["ciempre", "simpre", "sienpre"],
    "estaba": ["estava", "estaba", "estav"],
    "entonces": ["entonses", "entonce", "tons"],
    "bastante": ["vastante", "bastante", "vastant"],
    "verdad": ["berdad", "verda", "berdá"],
    "decir": ["desir", "decirr", "desirr"],
    "después": ["despues", "despue", "despué"],
    "necesito": ["nesesito", "nesecito", "necesit"]
}

# Conjuntos de contextos temáticos
CONTEXT_TEMPLATES = {
    "casual": [
        "Hola, {}, ¿cómo estás?",
        "Me gustaría {} ir al cine",
        "No sé si {} hoy",
        "Creo que {} es mejor así",
        "¿Sabes {} dónde está?"
    ],
    "formal": [
        "Estimado señor, {} le informo",
        "En relación a {}, le comento",
        "Considerando que {}, podemos",
        "Es importante {} mencionar",
        "Por lo tanto, {} concluimos"
    ],
    "técnico": [
        "El sistema {} está funcionando",
        "Se requiere {} implementar",
        "El proceso {} ha finalizado",
        "Configuración {} completada",
        "Error al {} ejecutar"
    ]
}

def generate_misspelled_text(text: str, error_rate: float = 0.3) -> str:
    """
    Genera una versión con errores de un texto.
    
    Args:
        text: Texto original
        error_rate: Probabilidad de introducir errores
        
    Returns:
        str: Texto con errores
    """
    words = text.split()
    result = []
    
    for word in words:
        word_lower = word.lower()
        if word_lower in COMMON_MISSPELLINGS and random.random() < error_rate:
            misspelled = random.choice(COMMON_MISSPELLINGS[word_lower])
            # Mantener mayúsculas si el original las tenía
            if word[0].isupper():
                misspelled = misspelled.capitalize()
            result.append(misspelled)
        else:
            result.append(word)
    
    return " ".join(result)

def generate_test_cases(
    num_cases: int,
    context_type: str = "mixed"
) -> List[Dict[str, Any]]:
    """
    Genera casos de prueba.
    
    Args:
        num_cases: Número de casos a generar
        context_type: Tipo de contexto (casual/formal/técnico/mixed)
        
    Returns:
        List[Dict[str, Any]]: Lista de casos de prueba
    """
    test_cases = []
    templates = []
    
    if context_type == "mixed":
        for templates_list in CONTEXT_TEMPLATES.values():
            templates.extend(templates_list)
    else:
        templates = CONTEXT_TEMPLATES.get(context_type, [])
    
    for _ in range(num_cases):
        # Seleccionar palabra a introducir error
        word = random.choice(list(COMMON_MISSPELLINGS.keys()))
        misspelled = random.choice(COMMON_MISSPELLINGS[word])
        
        # Generar contexto
        template = random.choice(templates)
        context = template.format(misspelled)
        
        # Añadir caso
        test_cases.append({
            "input": misspelled,
            "expected": word,
            "context": context,
            "should_correct": True,
            "metadata": {
                "context_type": context_type,
                "error_type": "common_misspelling",
                "timestamp": datetime.now().isoformat()
            }
        })
    
    return test_cases

def generate_load_test_data(
    num_sentences: int,
    words_per_sentence: int = 10,
    error_rate: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Genera datos para pruebas de carga.
    
    Args:
        num_sentences: Número de oraciones a generar
        words_per_sentence: Palabras por oración
        error_rate: Tasa de error a introducir
        
    Returns:
        List[Dict[str, Any]]: Datos de prueba de carga
    """
    load_test_data = []
    
    for _ in range(num_sentences):
        # Construir oración base
        words = []
        for _ in range(words_per_sentence):
            word = random.choice(list(COMMON_MISSPELLINGS.keys()))
            words.append(word)
        
        original_text = " ".join(words)
        misspelled_text = generate_misspelled_text(original_text, error_rate)
        
        load_test_data.append({
            "original": original_text,
            "input": misspelled_text,
            "metadata": {
                "words": words_per_sentence,
                "error_rate": error_rate,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    return load_test_data

def save_test_data(data: List[Dict[str, Any]], filename: str):
    """
    Guarda datos de prueba en un archivo.
    
    Args:
        data: Datos a guardar
        filename: Nombre del archivo
    """
    output_dir = Path("test_data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Genera datos de prueba para DyslexiLess")
    
    parser.add_argument(
        "--test-cases",
        type=int,
        default=100,
        help="Número de casos de prueba a generar"
    )
    
    parser.add_argument(
        "--load-sentences",
        type=int,
        default=1000,
        help="Número de oraciones para pruebas de carga"
    )
    
    parser.add_argument(
        "--context-type",
        choices=["casual", "formal", "técnico", "mixed"],
        default="mixed",
        help="Tipo de contexto para los casos de prueba"
    )
    
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.3,
        help="Tasa de error para pruebas de carga"
    )
    
    args = parser.parse_args()
    
    # Generar casos de prueba
    print(f"Generando {args.test_cases} casos de prueba...")
    test_cases = generate_test_cases(args.test_cases, args.context_type)
    save_test_data(test_cases, "test_cases.json")
    
    # Generar datos para pruebas de carga
    print(f"Generando {args.load_sentences} oraciones para pruebas de carga...")
    load_data = generate_load_test_data(
        args.load_sentences,
        error_rate=args.error_rate
    )
    save_test_data(load_data, "load_test_data.json")
    
    print("Datos de prueba generados exitosamente")

if __name__ == "__main__":
    main()
