# DyslexiLess

![Estado de Desarrollo](https://img.shields.io/badge/estado-estable-green)
![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Cobertura de Pruebas](https://img.shields.io/badge/cobertura-85%25-brightgreen)
![Licencia](https://img.shields.io/badge/licencia-MIT-blue)

Sistema de corrección en tiempo real para personas con dislexia.

## Características Principales

- 🚀 Corrección en tiempo real mientras escribes
- 💾 Caché encriptado para respuestas rápidas
- 🔄 Procesamiento por lotes para optimizar uso de API
- 📊 Sistema de telemetría y monitoreo integrado
- 🔒 Circuit Breaker para manejo robusto de APIs
- 📱 Soporte multiplataforma (Windows, macOS, Linux)

## Requisitos

- Python 3.8 o superior
- Sistema operativo compatible:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+, Fedora 34+)
- 4GB RAM mínimo
- Conexión a Internet

## Instalación

### Usando el Instalador

1. Descarga el instalador para tu sistema operativo desde la sección de releases
2. Ejecuta el instalador y sigue las instrucciones
3. La aplicación se iniciará automáticamente al finalizar

### Instalación Manual

```bash
# Clonar el repositorio
git clone https://github.com/dyslexiless/dyslexiless.git
cd dyslexiless

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar la aplicación
python setup.py configure

# Iniciar la aplicación
python run_app.py
```

## Uso Rápido

```python
from dyslexiless import initialize_application, get_service
from interfaces import ICorrector

# Inicializar la aplicación
initialize_application()

# Obtener el corrector
corrector = get_service(ICorrector)

# Corregir texto
text = "qe"
context = "creo qe esto funciona"
corrected_text, was_corrected = corrector.correct_text(text, context)

print(f"Original: {text}")
print(f"Corregido: {corrected_text}")
```

## Configuración

La aplicación puede configurarse mediante archivos JSON en el directorio `config/`:

- `notifications.json`: Configuración de notificaciones
- `telemetry.json`: Configuración de telemetría
- `services.json`: Configuración de servicios de IA

## Documentación

La documentación completa está disponible en el directorio `docs/`:

- [Guía de Inicio](docs/getting_started.md)
- [API Reference](docs/api.md)
- [Guía de Desarrollo](docs/development.md)
- [Ejemplos](docs/examples/)

Para generar la documentación:

```bash
cd docs
python generate_docs.py
```

## Características de Seguridad

- Caché encriptado para datos sensibles
- Circuit Breaker para APIs externas
- Validación de integridad de datos
- Rotación automática de claves
- Monitoreo de seguridad en tiempo real

## Monitoreo y Telemetría

La aplicación incluye un sistema completo de monitoreo:

- Métricas de rendimiento en tiempo real
- Dashboard de telemetría
- Sistema de alertas configurable
- Exportación de métricas en varios formatos

## Desarrollo

### Configurar Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Ejecutar pruebas
python -m pytest
```

### Estándares de Código

- Seguimos PEP 8
- Type hints obligatorios
- Docstrings en formato Google
- Tests unitarios requeridos para nuevas funcionalidades

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo MIT License - ver [LICENSE](LICENSE) para más detalles.

## Soporte

- [Reportar un Bug](https://github.com/dyslexiless/dyslexiless/issues)
- [Solicitar una Funcionalidad](https://github.com/dyslexiless/dyslexiless/issues)
- [Documentación de Soporte](docs/support.md)

## Autores

- **Equipo DyslexiLess** - *Trabajo inicial*

## Agradecimientos

- A la comunidad de Python por sus herramientas y librerías
- A todos los contribuidores del proyecto
- A los usuarios por su retroalimentación y sugerencias

## Estado del Proyecto

- ✅ Versión 1.0.0 liberada
- 🚀 En mejora continua
- 📈 Actualizaciones regulares
