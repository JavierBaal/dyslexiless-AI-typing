# DyslexiLess

## Asistente de escritura en tiempo real para personas con dislexia

DyslexiLess es una aplicación que corrige automáticamente errores comunes de escritura mientras escribes, especialmente diseñada para personas con dislexia. Funciona en segundo plano y corrige tu texto en cualquier aplicación.

![DyslexiLess Logo](resources/icon.png)

## Características Principales

- **Corrección en tiempo real** mientras escribes
- **Soporte para múltiples servicios de IA**:
  - OpenAI (GPT-4)
  - Anthropic (Claude-3)
  - Mixtral
  - Modo sin conexión (diccionario local)
- **Interfaz gráfica intuitiva** para usuarios no técnicos
- **Funciona en segundo plano** en todo el sistema
- **Corrección contextual** (analiza palabras anteriores y siguientes)
- **Notificaciones** para feedback visual

## Instalación Rápida

### Para Usuarios No Técnicos

1. **Descarga el ejecutable**:
   - Windows: `dist/DyslexiLess.exe`
   - macOS: `dist/DyslexiLess.app`
   - Linux: `dist/DyslexiLess`

2. **Haz doble clic** en el ejecutable para iniciar la aplicación

3. **Configura** el servicio de IA que deseas usar (o el modo sin conexión)

4. **¡Comienza a escribir!** La aplicación corregirá automáticamente tus errores

Para instrucciones más detalladas, consulta [README_USUARIOS.md](README_USUARIOS.md).

### Para Desarrolladores

1. **Clona este repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/dyslexiless-AI-typing.git
   cd dyslexiless-AI-typing
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación**:
   ```bash
   python improved_gui.py
   ```

4. **Genera el ejecutable** (opcional):
   ```bash
   python build_app.py
   ```

Para más detalles sobre las actualizaciones recientes, consulta [README_UPDATES.md](README_UPDATES.md).

## Requisitos

- Python 3.8 o superior (solo para desarrollo)
- macOS, Windows o Linux
- Conexión a Internet (opcional, para servicios de IA en línea)
- API key de alguno de los servicios soportados (opcional)

## Estructura del Proyecto

```
dyslexiless-AI-typing/
├── improved_gui.py       # Interfaz gráfica principal
├── text_corrector.py     # Motor de corrección de texto
├── keyboardlistener.py   # Monitor de teclado
├── config_manager.py     # Gestión de configuración
├── correction_cache.py   # Sistema de caché
├── logger_manager.py     # Sistema de registro
├── build_app.py          # Script para generar ejecutable
├── install.py            # Script de instalación
├── test_corrector.py     # Script de prueba avanzado
├── test_fallback.py      # Script de prueba simple
├── run_app.py            # Script para ejecutar la aplicación
├── requirements.txt      # Dependencias
└── dist/                 # Ejecutables generados
```

## Licencia

MIT License

Copyright (c) 2024 DyslexiLess

## Contacto

Para soporte o sugerencias, contacta a:
- Correo electrónico: soporte@dyslexiless.com
- Sitio web: [www.dyslexiless.com](https://www.dyslexiless.com)