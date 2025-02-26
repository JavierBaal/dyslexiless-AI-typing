# DyslexiLess

Asistente de escritura en tiempo real que ayuda a corregir texto mientras escribes, especialmente diseñado para personas con dislexia.

## Características

- Corrección de texto en tiempo real mientras escribes
- Soporte para múltiples servicios de IA:
  - OpenAI (GPT-4)
  - Anthropic (Claude-3)
  - Mixtral
- Interfaz gráfica simple para configuración
- Funciona en segundo plano en todo el sistema
- Corrección contextual (analiza palabras anteriores y siguientes)
- Notificaciones del sistema para feedback visual

## Requisitos

- Python 3.8 o superior
- macOS (soporte para Windows en desarrollo)
- Conexión a Internet
- API key de alguno de los servicios soportados

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/dyslexiless-AI-typing.git
cd dyslexiless-AI-typing
``dyslexiless-AI-typing/
├── main.py              # Punto de entrada y GUI
├── config_manager.py    # Gestión de configuración
├── keyboardlistener.py  # Monitor de teclado
├── text_corrector.py    # Integración con IA
└── requirements.txt     # Dependencias
```markdown:%2FUsers%2Fvanguardhive%2FDesktop%2FTRABAJOS%2FSALA-CREATIVA%2Fdyslexiless-AI-typing%2FLICENSE
MIT License

Copyright (c) 2024 DyslexiLess

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Project specific
config.json
*.log`