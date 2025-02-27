#!/usr/bin/env python3
"""
Generador de documentación para DyslexiLess.
Crea documentación completa del proyecto en múltiples formatos.
"""

import os
import sys
from pathlib import Path
import inspect
import ast
import json
import re
from typing import Dict, List, Any, Optional
import pkgutil
import importlib
import datetime
import shutil
import markdown2
from jinja2 import Environment, FileSystemLoader

# Configuración de directorios
DOCS_DIR = Path(__file__).parent
PROJECT_ROOT = DOCS_DIR.parent
OUTPUT_DIR = DOCS_DIR / "build"
TEMPLATE_DIR = DOCS_DIR / "templates"

# Asegurar que los directorios existen
for dir_path in [OUTPUT_DIR, TEMPLATE_DIR]:
    dir_path.mkdir(exist_ok=True)

class DocGenerator:
    """Generador de documentación."""
    
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self.modules = {}
        self.classes = {}
        self.functions = {}
        self.examples = {}
    
    def analyze_module(self, module_path: Path) -> Dict[str, Any]:
        """
        Analiza un módulo Python y extrae su documentación.
        
        Args:
            module_path: Ruta al módulo
            
        Returns:
            Dict con información del módulo
        """
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        module = ast.parse(content)
        module_doc = ast.get_docstring(module) or ""
        
        # Extraer información
        classes = []
        functions = []
        
        for node in ast.walk(module):
            if isinstance(node, ast.ClassDef):
                classes.append(self._analyze_class(node))
            elif isinstance(node, ast.FunctionDef):
                functions.append(self._analyze_function(node))
        
        return {
            "name": module_path.stem,
            "path": str(module_path.relative_to(PROJECT_ROOT)),
            "docstring": module_doc,
            "classes": classes,
            "functions": functions
        }
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analiza una clase y extrae su documentación."""
        methods = []
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                methods.append(self._analyze_function(child))
        
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "methods": methods,
            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
            "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
        }
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analiza una función y extrae su documentación."""
        args = []
        for arg in node.args.args:
            annotation = ""
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    annotation = arg.annotation.id
                elif isinstance(arg.annotation, ast.Subscript):
                    annotation = self._get_annotation_str(arg.annotation)
            
            args.append({
                "name": arg.arg,
                "annotation": annotation
            })
        
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "args": args,
            "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
            "returns": self._get_return_annotation(node)
        }
    
    def _get_annotation_str(self, node: ast.Subscript) -> str:
        """Convierte una anotación de tipo en string."""
        if isinstance(node.value, ast.Name):
            if isinstance(node.slice, ast.Name):
                return f"{node.value.id}[{node.slice.id}]"
            return node.value.id
        return ""
    
    def _get_return_annotation(self, node: ast.FunctionDef) -> str:
        """Extrae la anotación de retorno de una función."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Subscript):
                return self._get_annotation_str(node.returns)
        return ""
    
    def collect_examples(self):
        """Recolecta ejemplos de uso del código."""
        examples_dir = DOCS_DIR / "examples"
        if not examples_dir.exists():
            return
        
        for file in examples_dir.glob("*.py"):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.examples[file.stem] = {
                "code": content,
                "description": self._extract_description(content)
            }
    
    def _extract_description(self, content: str) -> str:
        """Extrae la descripción de un archivo de ejemplo."""
        try:
            module = ast.parse(content)
            return ast.get_docstring(module) or ""
        except:
            return ""
    
    def generate_markdown(self):
        """Genera documentación en formato Markdown."""
        template = self.env.get_template("api.md.j2")
        
        # Generar contenido
        content = template.render(
            modules=self.modules,
            classes=self.classes,
            functions=self.functions,
            examples=self.examples,
            generation_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Guardar documentación
        output_file = OUTPUT_DIR / "api.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_html(self):
        """Genera documentación en formato HTML."""
        # Convertir markdown a HTML
        md_file = OUTPUT_DIR / "api.md"
        if not md_file.exists():
            self.generate_markdown()
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown2.markdown(
            md_content,
            extras=['fenced-code-blocks', 'tables']
        )
        
        # Aplicar template HTML
        template = self.env.get_template("api.html.j2")
        content = template.render(
            content=html_content,
            generation_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Guardar documentación
        output_file = OUTPUT_DIR / "api.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def analyze_project(self):
        """Analiza todos los módulos del proyecto."""
        for module_path in PROJECT_ROOT.rglob("*.py"):
            if module_path.name.startswith("test_"):
                continue
            if "build" in str(module_path):
                continue
            
            try:
                module_info = self.analyze_module(module_path)
                self.modules[module_path.stem] = module_info
                
                # Recolectar clases y funciones globalmente
                for cls in module_info["classes"]:
                    self.classes[f"{module_path.stem}.{cls['name']}"] = cls
                for func in module_info["functions"]:
                    self.functions[f"{module_path.stem}.{func['name']}"] = func
                    
            except Exception as e:
                print(f"Error analizando {module_path}: {e}")
    
    def copy_static_files(self):
        """Copia archivos estáticos necesarios."""
        static_dir = TEMPLATE_DIR / "static"
        if static_dir.exists():
            dest_dir = OUTPUT_DIR / "static"
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(static_dir, dest_dir)
    
    def generate_docs(self):
        """Genera toda la documentación."""
        print("Generando documentación...")
        
        # Limpiar directorio de salida
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir()
        
        # Analizar proyecto
        print("Analizando módulos...")
        self.analyze_project()
        
        # Recolectar ejemplos
        print("Recolectando ejemplos...")
        self.collect_examples()
        
        # Generar documentación
        print("Generando Markdown...")
        self.generate_markdown()
        
        print("Generando HTML...")
        self.generate_html()
        
        print("Copiando archivos estáticos...")
        self.copy_static_files()
        
        print(f"\nDocumentación generada en {OUTPUT_DIR}")

def main():
    """Función principal."""
    generator = DocGenerator()
    generator.generate_docs()

if __name__ == "__main__":
    main()
