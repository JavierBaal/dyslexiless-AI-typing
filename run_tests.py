#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas y generar informes de cobertura.
"""

import unittest
import coverage
import sys
import os
from pathlib import Path
import argparse
import time
from datetime import datetime
import json

def setup_test_environment():
    """Configura el entorno para las pruebas."""
    # Asegurar que estamos en modo test
    os.environ["DYSLEXILESS_TEST_MODE"] = "1"
    
    # Añadir directorio raíz al path
    root_dir = Path(__file__).parent
    sys.path.insert(0, str(root_dir))
    
    # Crear directorio para reportes si no existe
    reports_dir = root_dir / "test_reports"
    reports_dir.mkdir(exist_ok=True)
    
    return reports_dir

def discover_tests() -> unittest.TestSuite:
    """
    Descubre todas las pruebas en el proyecto.
    
    Returns:
        TestSuite con todas las pruebas encontradas
    """
    loader = unittest.TestLoader()
    start_dir = '.'
    pattern = 'test_*.py'
    return loader.discover(start_dir, pattern=pattern)

def run_tests(
    suite: unittest.TestSuite,
    reports_dir: Path,
    verbose: bool = False
) -> unittest.TestResult:
    """
    Ejecuta las pruebas y genera reportes.
    
    Args:
        suite: Suite de pruebas a ejecutar
        reports_dir: Directorio para reportes
        verbose: Si se debe mostrar salida detallada
        
    Returns:
        Resultado de las pruebas
    """
    # Configurar runner
    if verbose:
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout
        )
    else:
        # Redirigir salida a archivo
        log_file = reports_dir / f"test_log_{datetime.now():%Y%m%d_%H%M%S}.txt"
        with open(log_file, 'w') as f:
            runner = unittest.TextTestRunner(
                verbosity=2,
                stream=f
            )
            result = runner.run(suite)
    
    return result

def generate_coverage_report(
    cov: coverage.Coverage,
    reports_dir: Path,
    show_missing: bool = True
) -> dict:
    """
    Genera reportes de cobertura en múltiples formatos.
    
    Args:
        cov: Instancia de coverage
        reports_dir: Directorio para reportes
        show_missing: Si se deben mostrar líneas sin cobertura
        
    Returns:
        dict: Estadísticas de cobertura
    """
    # Generar reporte HTML
    html_dir = reports_dir / "coverage_html"
    cov.html_report(directory=str(html_dir))
    
    # Generar reporte XML para herramientas de CI
    xml_file = reports_dir / "coverage.xml"
    cov.xml_report(outfile=str(xml_file))
    
    # Generar reporte de texto
    text_file = reports_dir / "coverage.txt"
    with open(text_file, 'w') as f:
        cov.report(file=f, show_missing=show_missing)
    
    # Obtener estadísticas
    stats = {
        "total_statements": cov.get_total_statements(),
        "covered_statements": len(cov.get_data().measured_files()),
        "branches_covered": len(cov.get_data().has_arcs()),
        "coverage_percent": cov.report(file=None)
    }
    
    # Guardar estadísticas en JSON
    stats_file = reports_dir / "coverage_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Ejecuta pruebas y genera reportes")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mostrar salida detallada"
    )
    parser.add_argument(
        "--show-missing",
        action="store_true",
        help="Mostrar líneas sin cobertura"
    )
    args = parser.parse_args()
    
    # Configurar entorno
    reports_dir = setup_test_environment()
    start_time = time.time()
    
    # Iniciar medición de cobertura
    cov = coverage.Coverage(
        branch=True,
        source=["."],
        omit=[
            "*/test_*",
            "*/venv/*",
            "setup.py",
            "run_tests.py"
        ]
    )
    cov.start()
    
    try:
        # Descubrir y ejecutar pruebas
        suite = discover_tests()
        result = run_tests(suite, reports_dir, args.verbose)
        
        # Detener medición y generar reportes
        cov.stop()
        cov.save()
        stats = generate_coverage_report(cov, reports_dir, args.show_missing)
        
        # Mostrar resumen
        elapsed_time = time.time() - start_time
        print("\n=== Resumen de Pruebas ===")
        print(f"Tiempo total: {elapsed_time:.2f}s")
        print(f"Pruebas ejecutadas: {result.testsRun}")
        print(f"Errores: {len(result.errors)}")
        print(f"Fallos: {len(result.failures)}")
        print(f"\nCobertura total: {stats['coverage_percent']:.1f}%")
        print(f"Sentencias totales: {stats['total_statements']}")
        print(f"Sentencias cubiertas: {stats['covered_statements']}")
        print(f"Ramas cubiertas: {stats['branches_covered']}")
        print(f"\nReportes generados en: {reports_dir}")
        
        # Salir con código apropiado
        if result.wasSuccessful():
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error al ejecutar pruebas: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
