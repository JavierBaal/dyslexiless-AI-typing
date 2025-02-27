# DyslexiLess Technical Architecture

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DyslexiLess                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Main Application                          │
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
│                       External Services                              │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │   OpenAI API  │        │ Anthropic API │      │  Mixtral API  │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      Alternative Implementations                     │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │correction_handler.py│  │live_corrector.py│    │ karabiner.json │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐     ┌───────────────┐     ┌───────────────┐
│              │     │               │     │               │
│  User Input  │────►│Keyboard Listener│───►│  Text Buffer  │
│              │     │               │     │               │
└──────────────┘     └───────────────┘     └───────┬───────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌───────────────┐     ┌───────────────┐
│              │     │               │     │               │
│  Correction  │◄────│Text Corrector │◄────│ Word Analysis │
│              │     │               │     │               │
└──────┬───────┘     └───────────────┘     └───────────────┘
       │                     ▲
       │                     │
       ▼                     │
┌──────────────┐     ┌───────────────┐
│              │     │               │
│ User Display │     │Correction Cache│
│              │     │               │
└──────────────┘     └───────────────┘
```

## Proposed Improved Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DyslexiLess                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Core Components                           │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │  Application  │◄──────►│ Configuration │◄────►│  Config UI    │  │
│  │    Core       │        │   Manager     │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│          │                                                          │
│          ▼                                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     Input Processing                          │  │
│  │                                                               │  │
│  │  ┌───────────────┐        ┌───────────────┐                   │  │
│  │  │               │        │               │                   │  │
│  │  │ Input Monitor │◄──────►│ Text Analyzer │                   │  │
│  │  │               │        │               │                   │  │
│  │  └───────────────┘        └───────────────┘                   │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                  │                                   │
│                                  ▼                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     Correction Engine                         │  │
│  │                                                               │  │
│  │  ┌───────────────┐        ┌───────────────┐                   │  │
│  │  │               │        │               │                   │  │
│  │  │ Correction    │◄──────►│ Correction    │                   │  │
│  │  │ Strategies    │        │ Cache         │                   │  │
│  │  └───────────────┘        └───────────────┘                   │  │
│  │          │                                                    │  │
│  │          ▼                                                    │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │                  Strategy Implementations             │    │  │
│  │  │                                                       │    │  │
│  │  │  ┌───────────┐    ┌───────────┐    ┌───────────┐     │    │  │
│  │  │  │           │    │           │    │           │     │    │  │
│  │  │  │  OpenAI   │    │ Anthropic │    │  Mixtral  │     │    │  │
│  │  │  │ Strategy  │    │ Strategy  │    │ Strategy  │     │    │  │
│  │  │  │           │    │           │    │           │     │    │  │
│  │  │  └───────────┘    └───────────┘    └───────────┘     │    │  │
│  │  │                                                       │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                  │                                   │
│                                  ▼                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     Output Processing                         │  │
│  │                                                               │  │
│  │  ┌───────────────┐        ┌───────────────┐                   │  │
│  │  │               │        │               │                   │  │
│  │  │ Text Replacer │        │ Notification  │                   │  │
│  │  │               │        │ Manager       │                   │  │
│  │  └───────────────┘        └───────────────┘                   │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Cross-Cutting Concerns                         │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │    Logging    │        │ Error Handling│      │  Telemetry    │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Improvements in Proposed Architecture

1. **Modular Design**
   - Clear separation of concerns
   - Well-defined interfaces between components
   - Easier to maintain and extend

2. **Strategy Pattern for Correction Services**
   - Unified interface for all correction strategies
   - Easy to add new correction services
   - Simple fallback mechanism

3. **Cross-Cutting Concerns**
   - Centralized logging, error handling, and telemetry
   - Consistent approach across all components

4. **Platform Abstraction**
   - Input/output processing abstracted for cross-platform support
   - Platform-specific implementations hidden behind interfaces

## Component Descriptions

### Core Components

- **Application Core**: Central coordinator that manages the application lifecycle
- **Configuration Manager**: Handles loading, saving, and validating configuration
- **Config UI**: User interface for configuration settings

### Input Processing

- **Input Monitor**: Platform-specific keyboard monitoring
- **Text Analyzer**: Analyzes text to identify words and context

### Correction Engine

- **Correction Strategies**: Interface for different correction approaches
- **Correction Cache**: Caches previous corrections for performance
- **Strategy Implementations**: Specific implementations for each AI service

### Output Processing

- **Text Replacer**: Handles replacing text in the active application
- **Notification Manager**: Manages system notifications

### Cross-Cutting Concerns

- **Logging**: Centralized logging system
- **Error Handling**: Consistent error handling and recovery
- **Telemetry**: Usage statistics and performance monitoring

## Technology Stack

- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **AI Services**: OpenAI, Anthropic, Mixtral
- **Input Monitoring**: pynput
- **Testing**: pytest
- **Packaging**: pyinstaller (for distribution)

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           User's Computer                           │
│                                                                     │
│  ┌───────────────┐                              ┌───────────────┐   │
│  │               │                              │               │   │
│  │  DyslexiLess  │◄─────────────────────────────│ Configuration │   │
│  │  Application  │                              │     Files     │   │
│  │               │                              │               │   │
│  └───────┬───────┘                              └───────────────┘   │
│          │                                                          │
│          │                                                          │
│          ▼                                                          │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │  Keyboard     │        │  System       │      │  Log Files    │  │
│  │  Input        │        │  Notifications│      │               │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Cloud Services                            │
│                                                                     │
│  ┌───────────────┐        ┌───────────────┐      ┌───────────────┐  │
│  │               │        │               │      │               │  │
│  │   OpenAI API  │        │ Anthropic API │      │  Mixtral API  │  │
│  │               │        │               │      │               │  │
│  └───────────────┘        └───────────────┘      └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

This technical architecture provides a blueprint for both the current state of the DyslexiLess application and the proposed improvements. The modular design with clear separation of concerns will make the application more maintainable, extensible, and robust.