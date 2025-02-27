# Arquitectura Técnica de DyslexiLess

## Arquitectura Actual

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DyslexiLess                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Aplicación Principal                      │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │    main.py    │◄──────►│config_window.py│     │config_manager.py│ │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│          │                                               ▲          │
│          │                                               │          │
│          ▼                                               │          │
│  ┌───────────────┐                                       │          │
│  │               │                                       │          │
│  │keyboardlistener.py│                                   │          │
│  │               │                                       │          │
│  └───────────────┘                                       │          │
│          │                                               │          │
│          ▼                                               │          │
│  ┌───────────────┐        ┌───────────────┐             │          │
│  │               │        │               │             │          │
│  │text_corrector.py│◄────►│correction_cache.py│         │          │
│  │               │        │               │             │          │
│  └───────────────┘        └───────────────┘             │          │
│          │                                               │          │
│          ▼                                               │          │
│  ┌───────────────┐                                       │          │
│  │               │                                       │          │
│  │logger_manager.py│                                     │          │
│  │               │                                       │          │
│  └───────────────┘                                       │          │
│                                                          │          │
└─────────────────────────────────────────────────────────┬┘          │
                                                          │           │
┌─────────────────────────────────────────────────────────▼───────────┘
│                       Servicios Externos                             │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │   API OpenAI  │        │ API Anthropic │      │  API Mixtral  │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      Implementaciones Alternativas                   │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │correction_handler.py│  │live_corrector.py│    │ karabiner.json │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

```
┌──────────────┐     ┌───────────────┐     ┌───────────────┐
│              │     │               │     │               │
│  Entrada de  │────►│Monitor de     │───►│  Búfer de     │
│   Usuario    │     │  Teclado      │     │   Texto       │
│              │     │               │     │               │
└──────────────┘     └───────────────┘     └───────┬───────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌───────────────┐     ┌───────────────┐
│              │     │               │     │               │
│  Corrección  │◄────│Corrector de   │◄────│ Análisis de   │
│              │     │    Texto      │     │   Palabras    │
│              │     │               │     │               │
└──────┬───────┘     └───────────────┘     └───────────────┘
       │                     ▲
       │                     │
       ▼                     │
┌──────────────┐     ┌───────────────┐
│              │     │               │
│ Visualización│     │Caché de       │
│   Usuario    │     │ Correcciones  │
│              │     │               │
└──────────────┘     └───────────────┘
```

## Arquitectura Mejorada Propuesta

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DyslexiLess                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Componentes Principales                      │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │  Núcleo de    │◄──────►│ Gestor de     │◄────►│  Interfaz de  │  │
│  │  Aplicación   │        │ Configuración │      │ Configuración │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│          │                                                          │
│          ▼                                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   Procesamiento de Entrada                    │  │
│  │                                                               │  │
│  │  ┌───────────────┐        ┌───────────────┐                   │  │
│  │  │               │        │               │                   │  │
│  │  │ Monitor de    │◄──────►│ Analizador de │                   │  │
│  │  │   Entrada     │        │    Texto      │                   │  │
│  │  │               │        │               │                   │  │
│  │  └───────────────┘        └───────────────┘                   │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                  │                                   │
│                                  ▼                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     Motor de Corrección                       │  │
│  │                                                               │  │
│  │  ┌───────────────┐        ┌───────────────┐                   │  │
│  │  │               │        │               │                   │  │
│  │  │ Estrategias   │◄──────►│   Caché de    │                   │  │
│  │  │ de Corrección │        │ Correcciones  │                   │  │
│  │  └───────────────┘        └───────────────┘                   │  │
│  │          │                                                    │  │
│  │          ▼                                                    │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │             Implementaciones de Estrategias           │    │  │
│  │  │                                                       │    │  │
│  │  │  ┌───────────┐    ┌───────────┐    ┌───────────┐     │    │  │
│  │  │  │           │    │           │    │           │     │    │  │
│  │  │  │  OpenAI   │    │ Anthropic │    │  Mixtral  │     │    │  │
│  │  │  │ Estrategia│    │ Estrategia│    │ Estrategia│     │    │  │
│  │  │  │           │    │           │    │           │     │    │  │
│  │  │  └───────────┘    └───────────┘    └───────────┘     │    │  │
│  │  │                                                       │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                  │                                   │
│                                  ▼                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   Procesamiento de Salida                     │  │
│  │                                                               │  │
│  │  ┌───────────────┐        ┌───────────────┐                   │  │
│  │  │               │        │               │                   │  │
│  │  │ Reemplazador  │        │ Gestor de     │                   │  │
│  │  │   de Texto    │        | Notificaciones│                   │  │
│  │  │               │        │               │                   │  │
│  │  └───────────────┘        └───────────────┘                   │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Preocupaciones Transversales                     │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │    Registro   │        │ Manejo de     │      │  Telemetría   │  │
│  │               │        │   Errores     │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Mejoras Clave en la Arquitectura Propuesta

1. **Diseño Modular**
   - Separación clara de responsabilidades
   - Interfaces bien definidas entre componentes
   - Más fácil de mantener y extender

2. **Patrón de Estrategia para Servicios de Corrección**
   - Interfaz unificada para todas las estrategias de corrección
   - Fácil adición de nuevos servicios de corrección
   - Mecanismo simple de respaldo

3. **Preocupaciones Transversales**
   - Registro, manejo de errores y telemetría centralizados
   - Enfoque consistente en todos los componentes

4. **Abstracción de Plataforma**
   - Procesamiento de entrada/salida abstraído para soporte multiplataforma
   - Implementaciones específicas de plataforma ocultas detrás de interfaces

## Descripción de Componentes

### Componentes Principales

- **Núcleo de Aplicación**: Coordinador central que gestiona el ciclo de vida de la aplicación
- **Gestor de Configuración**: Maneja carga, guardado y validación de configuración
- **Interfaz de Configuración**: Interfaz de usuario para configuraciones

### Procesamiento de Entrada

- **Monitor de Entrada**: Monitoreo de teclado específico de plataforma
- **Analizador de Texto**: Analiza texto para identificar palabras y contexto

### Motor de Corrección

- **Estrategias de Corrección**: Interfaz para diferentes enfoques de corrección
- **Caché de Correcciones**: Almacena correcciones previas para rendimiento
- **Implementaciones de Estrategias**: Implementaciones específicas para cada servicio de IA

### Procesamiento de Salida

- **Reemplazador de Texto**: Maneja reemplazo de texto en la aplicación activa
- **Gestor de Notificaciones**: Gestiona notificaciones del sistema

### Preocupaciones Transversales

- **Registro**: Sistema de registro centralizado
- **Manejo de Errores**: Manejo y recuperación de errores consistentes
- **Telemetría**: Estadísticas de uso y monitoreo de rendimiento

## Pila Tecnológica

- **Lenguaje**: Python 3.8+
- **Framework de GUI**: PyQt6
- **Servicios de IA**: OpenAI, Anthropic, Mixtral
- **Monitoreo de Entrada**: pynput
- **Pruebas**: pytest
- **Empaquetado**: pyinstaller (para distribución)

## Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Computadora del Usuario                   │
│                                                                     │
│  ┌───────────────┐                              ┌───────────────┐   │
│  │               │                              │               │   │
│  │  Aplicación   │◄─────────────────────────────│ Archivos de   │   │
│  │  DyslexiLess  │                              │ Configuración │   │
│  │               │                              │               │   │
│  └───────┬───────┘                              └───────────────┘   │
│          │                                                          │
│          │                                                          │
│          ▼                                                          │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │  Entrada de   │        │  Notificaciones│      │  Archivos de  │  │
│  │   Teclado     │        │    Sistema    │      │     Logs      │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Servicios en la Nube                          │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │   API OpenAI  │        │ API Anthropic │      │  API Mixtral  │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Conclusión

Esta arquitectura técnica proporciona un modelo tanto para el estado actual de la aplicación DyslexiLess como para las mejoras propuestas. El diseño modular con una clara separación de responsabilidades hará que la aplicación sea más mantenible, extensible y robusta.

Los diagramas y descripciones presentados ofrecen una visión detallada de la estructura interna, los flujos de datos y las interacciones entre componentes, proporcionando una base sólida para futuras mejoras y desarrollo del proyecto.