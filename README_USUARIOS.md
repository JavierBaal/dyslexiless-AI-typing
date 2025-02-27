# DyslexiLess - Guía para Usuarios

## ¿Qué es DyslexiLess?

DyslexiLess es un asistente de escritura en tiempo real diseñado para ayudar a personas con dislexia. La aplicación corrige automáticamente errores comunes mientras escribes en cualquier programa o aplicación de tu computadora.

## Instalación Rápida

### Opción 1: Ejecutable (Más fácil)

1. Descarga el archivo ejecutable `DyslexiLess.exe` (Windows) o `DyslexiLess.app` (Mac)
2. Haz doble clic en el archivo descargado para iniciar la aplicación
3. ¡Listo! La aplicación se iniciará automáticamente

### Opción 2: Usando el instalador

1. Descarga todos los archivos del proyecto
2. Haz doble clic en `install.py` (o ejecuta `python install.py` si tienes Python instalado)
3. Sigue las instrucciones en pantalla
4. El instalador creará un acceso directo en tu escritorio

## Uso Básico

1. **Iniciar la aplicación**: Haz doble clic en el icono de DyslexiLess en tu escritorio o en el ejecutable
2. **Configurar**: En la pestaña "Configuración", selecciona el servicio de IA que deseas usar
   - Para usar sin internet, selecciona "Modo sin conexión"
   - Para usar con internet, selecciona OpenAI, Anthropic o Mixtral e ingresa tu clave API
3. **Guardar configuración**: Haz clic en "Guardar Configuración"
4. **Iniciar el corrector**: Ve a la pestaña "Estado" y haz clic en "Iniciar Corrector"
5. **¡Comienza a escribir!**: La aplicación corregirá automáticamente tus errores mientras escribes

## Características Principales

- **Corrección en tiempo real**: Corrige errores mientras escribes
- **Funciona en todas las aplicaciones**: Procesadores de texto, navegadores, correo electrónico, etc.
- **Modo sin conexión**: Funciona sin internet usando un diccionario de correcciones comunes
- **Interfaz sencilla**: Fácil de configurar y usar
- **Icono en la bandeja**: La aplicación se minimiza a la bandeja del sistema y funciona en segundo plano

## Obtener Claves API (Opcional)

Si deseas usar los servicios de IA en línea para obtener correcciones más precisas:

- **OpenAI**: Visita [platform.openai.com](https://platform.openai.com) y crea una cuenta
- **Anthropic**: Visita [console.anthropic.com](https://console.anthropic.com) y crea una cuenta
- **Mixtral**: Visita [api.together.xyz](https://api.together.xyz) y crea una cuenta

## Solución de Problemas

### La aplicación no inicia

- Asegúrate de tener los permisos necesarios para ejecutar la aplicación
- En Mac, es posible que debas ir a Preferencias del Sistema > Seguridad y Privacidad y permitir la aplicación

### Las correcciones no funcionan

- Verifica que el corrector esté iniciado (pestaña "Estado")
- Si estás usando un servicio en línea, verifica que tu clave API sea correcta
- Prueba con el modo sin conexión para verificar que la aplicación funciona correctamente

### Otros problemas

- Cierra y vuelve a abrir la aplicación
- Verifica que no haya otra instancia de la aplicación ejecutándose
- Consulta los archivos de registro en la carpeta `logs` para obtener más información

## Contacto y Soporte

Si tienes problemas o sugerencias, por favor contacta a:
- Correo electrónico: soporte@dyslexiless.com
- Sitio web: [www.dyslexiless.com](https://www.dyslexiless.com)