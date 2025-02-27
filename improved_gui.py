#!/usr/bin/env python3
"""
Interfaz gráfica mejorada para DyslexiLess.
Diseñada para ser intuitiva y fácil de usar para usuarios no técnicos.
"""

import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QCheckBox, 
    QSystemTrayIcon, QMenu, QMessageBox, QTabWidget, QGroupBox,
    QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QFont, QPixmap
import keyboardlistener
import config_manager
from text_corrector import TextCorrector

# Ruta para recursos
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
os.makedirs(RESOURCES_DIR, exist_ok=True)

# Crear un icono simple si no existe
ICON_PATH = os.path.join(RESOURCES_DIR, "icon.png")
if not os.path.exists(ICON_PATH):
    # Usaremos un icono de texto simple si no hay un archivo de icono
    pass

class StatusWidget(QWidget):
    """Widget que muestra el estado actual del corrector."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.correction_count = 0
        self.word_count = 0
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Estado del Corrector")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Estado
        self.status_label = QLabel("Estado: Inactivo")
        self.status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.status_label)
        
        # Servicio
        self.service_label = QLabel("Servicio: Ninguno")
        self.service_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.service_label)
        
        # Estadísticas
        stats_box = QGroupBox("Estadísticas")
        stats_layout = QVBoxLayout()
        
        self.corrections_label = QLabel("Correcciones: 0")
        self.words_label = QLabel("Palabras procesadas: 0")
        self.rate_label = QLabel("Tasa de corrección: 0%")
        
        stats_layout.addWidget(self.corrections_label)
        stats_layout.addWidget(self.words_label)
        stats_layout.addWidget(self.rate_label)
        
        stats_box.setLayout(stats_layout)
        layout.addWidget(stats_box)
        
        # Espacio flexible
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Botón para detener/iniciar
        self.toggle_button = QPushButton("Iniciar Corrector")
        self.toggle_button.setFont(QFont("Arial", 12))
        self.toggle_button.setMinimumHeight(40)
        layout.addWidget(self.toggle_button)
    
    def update_status(self, is_active, service=None):
        """Actualiza el estado mostrado."""
        if is_active:
            self.status_label.setText("Estado: Activo")
            self.toggle_button.setText("Detener Corrector")
            if service:
                self.service_label.setText(f"Servicio: {service}")
        else:
            self.status_label.setText("Estado: Inactivo")
            self.toggle_button.setText("Iniciar Corrector")
            self.service_label.setText("Servicio: Ninguno")
    
    def update_stats(self, corrections, words):
        """Actualiza las estadísticas mostradas."""
        self.correction_count = corrections
        self.word_count = words
        
        self.corrections_label.setText(f"Correcciones: {corrections}")
        self.words_label.setText(f"Palabras procesadas: {words}")
        
        rate = (corrections / words * 100) if words > 0 else 0
        self.rate_label.setText(f"Tasa de corrección: {rate:.1f}%")

class ConfigWidget(QWidget):
    """Widget para configurar el corrector."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Configuración")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Selector de servicio
        service_group = QGroupBox("Servicio de IA")
        service_layout = QVBoxLayout()
        
        self.service_selector = QComboBox()
        self.service_selector.addItems(["OpenAI", "Anthropic", "Mixtral", "Modo sin conexión"])
        self.service_selector.currentIndexChanged.connect(self.on_service_changed)
        
        service_layout.addWidget(QLabel("Selecciona el servicio de IA:"))
        service_layout.addWidget(self.service_selector)
        
        # Descripción del servicio
        self.service_description = QLabel("OpenAI proporciona correcciones de alta calidad usando GPT-4.")
        self.service_description.setWordWrap(True)
        service_layout.addWidget(self.service_description)
        
        service_group.setLayout(service_layout)
        layout.addWidget(service_group)
        
        # Campo de API Key
        self.api_key_group = QGroupBox("Clave API")
        api_key_layout = QVBoxLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Ingresa tu clave API aquí")
        
        api_key_layout.addWidget(QLabel("Clave API:"))
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(QLabel("La clave API es necesaria para usar los servicios de IA."))
        
        self.api_key_group.setLayout(api_key_layout)
        layout.addWidget(self.api_key_group)
        
        # Opciones adicionales
        options_group = QGroupBox("Opciones")
        options_layout = QVBoxLayout()
        
        self.start_with_system = QCheckBox("Iniciar automáticamente con el sistema")
        self.show_notifications = QCheckBox("Mostrar notificaciones de corrección")
        self.show_notifications.setChecked(True)
        
        options_layout.addWidget(self.start_with_system)
        options_layout.addWidget(self.show_notifications)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Espacio flexible
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Botón de guardar
        self.save_button = QPushButton("Guardar Configuración")
        self.save_button.setFont(QFont("Arial", 12))
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_button)
    
    def on_service_changed(self, index):
        """Actualiza la descripción del servicio y muestra/oculta el campo de API key."""
        service = self.service_selector.currentText()
        
        if service == "OpenAI":
            self.service_description.setText("OpenAI proporciona correcciones de alta calidad usando GPT-4.")
            self.api_key_group.setVisible(True)
        elif service == "Anthropic":
            self.service_description.setText("Anthropic Claude ofrece correcciones precisas con comprensión contextual.")
            self.api_key_group.setVisible(True)
        elif service == "Mixtral":
            self.service_description.setText("Mixtral es un modelo de código abierto con buen rendimiento.")
            self.api_key_group.setVisible(True)
        elif service == "Modo sin conexión":
            self.service_description.setText("Modo sin conexión usa un diccionario local para correcciones básicas sin internet.")
            self.api_key_group.setVisible(False)
    
    def load_config(self):
        """Carga la configuración existente."""
        if config_manager.config_exists():
            config = config_manager.load_config()
            
            # Servicio
            service = config.get('service', 'OpenAI')
            index = self.service_selector.findText(service)
            if index >= 0:
                self.service_selector.setCurrentIndex(index)
            
            # API Key
            self.api_key_input.setText(config.get('api_key', ''))
            
            # Opciones
            self.start_with_system.setChecked(config.get('start_with_system', False))
            self.show_notifications.setChecked(config.get('show_notifications', True))
    
    def save_config(self):
        """Guarda la configuración."""
        service = self.service_selector.currentText()
        
        config = {
            'service': "InvalidService" if service == "Modo sin conexión" else service,
            'api_key': self.api_key_input.text() if service != "Modo sin conexión" else "invalid_key",
            'start_with_system': self.start_with_system.isChecked(),
            'show_notifications': self.show_notifications.isChecked()
        }
        
        config_manager.save_config(config)
        QMessageBox.information(self, "Configuración Guardada", 
                               "La configuración se ha guardado correctamente.")

class HelpWidget(QWidget):
    """Widget que muestra ayuda e información sobre la aplicación."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Ayuda y Soporte")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Contenido de ayuda
        help_text = """
<h3>¿Qué es DyslexiLess?</h3>
<p>DyslexiLess es un asistente de escritura en tiempo real diseñado para ayudar a personas con dislexia. Corrige automáticamente errores comunes mientras escribes en cualquier aplicación.</p>

<h3>¿Cómo funciona?</h3>
<p>La aplicación monitorea tu escritura y corrige automáticamente errores comunes de dislexia. Funciona en segundo plano y no interfiere con tu flujo de trabajo normal.</p>

<h3>Configuración</h3>
<p><b>1. Selecciona un servicio de IA</b> - Elige entre OpenAI, Anthropic, Mixtral o el modo sin conexión.</p>
<p><b>2. Ingresa tu clave API</b> - Si elegiste un servicio en línea, necesitarás una clave API.</p>
<p><b>3. Guarda la configuración</b> - Haz clic en "Guardar Configuración".</p>
<p><b>4. Inicia el corrector</b> - Ve a la pestaña "Estado" y haz clic en "Iniciar Corrector".</p>

<h3>Obtener claves API</h3>
<p><b>OpenAI:</b> Visita <a href="https://platform.openai.com">platform.openai.com</a></p>
<p><b>Anthropic:</b> Visita <a href="https://console.anthropic.com">console.anthropic.com</a></p>
<p><b>Mixtral:</b> Visita <a href="https://api.together.xyz">api.together.xyz</a></p>

<h3>Modo sin conexión</h3>
<p>Si no tienes una clave API o prefieres no usar servicios en línea, puedes usar el modo sin conexión. Este modo utiliza un diccionario local para corregir errores comunes de dislexia.</p>
"""
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.TextFormat.RichText)
        help_label.setOpenExternalLinks(True)
        
        layout.addWidget(help_label)
        
        # Espacio flexible
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Información de versión
        version_label = QLabel("DyslexiLess v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación DyslexiLess."""
    
    def __init__(self):
        super().__init__()
        self.correction_service = None
        self.setup_ui()
        self.setup_tray()
        
    def setup_ui(self):
        self.setWindowTitle("DyslexiLess - Asistente de Escritura")
        self.setMinimumSize(600, 500)
        
        # Widget central con pestañas
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Título principal
        header = QLabel("DyslexiLess")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Subtítulo
        subtitle = QLabel("Asistente de escritura en tiempo real para personas con dislexia")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de estado
        self.status_widget = StatusWidget()
        self.status_widget.toggle_button.clicked.connect(self.toggle_service)
        self.tabs.addTab(self.status_widget, "Estado")
        
        # Pestaña de configuración
        self.config_widget = ConfigWidget()
        self.tabs.addTab(self.config_widget, "Configuración")
        
        # Pestaña de ayuda
        self.help_widget = HelpWidget()
        self.tabs.addTab(self.help_widget, "Ayuda")
        
        main_layout.addWidget(self.tabs)
        
        # Barra de estado
        self.statusBar().showMessage("Listo")
    
    def setup_tray(self):
        """Configura el icono en la bandeja del sistema."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Usar un icono si existe, o crear uno por defecto
        if os.path.exists(ICON_PATH):
            self.tray_icon.setIcon(QIcon(ICON_PATH))
        else:
            # Usar un icono por defecto del sistema
            self.tray_icon.setIcon(self.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon))
        
        # Menú contextual para el icono de la bandeja
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Mostrar")
        show_action.triggered.connect(self.show)
        
        toggle_action = tray_menu.addAction("Iniciar/Detener Corrector")
        toggle_action.triggered.connect(self.toggle_service)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Salir")
        quit_action.triggered.connect(self.close_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Maneja la activación del icono de la bandeja."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def toggle_service(self):
        """Inicia o detiene el servicio de corrección."""
        if self.correction_service is None:
            # Iniciar el servicio
            try:
                self.correction_service = keyboardlistener.start_listener()
                self.status_widget.update_status(True, config_manager.load_config().get('service'))
                self.statusBar().showMessage("Servicio de corrección iniciado")
                
                # Configurar un temporizador para actualizar las estadísticas
                self.stats_timer = QTimer(self)
                self.stats_timer.timeout.connect(self.update_stats)
                self.stats_timer.start(5000)  # Actualizar cada 5 segundos
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo iniciar el servicio: {e}")
        else:
            # Detener el servicio
            try:
                # Aquí deberíamos tener un método para detener el listener
                # Por ahora, simplemente establecemos la variable a None
                self.correction_service = None
                if hasattr(self, 'stats_timer'):
                    self.stats_timer.stop()
                self.status_widget.update_status(False)
                self.statusBar().showMessage("Servicio de corrección detenido")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo detener el servicio: {e}")
    
    def update_stats(self):
        """Actualiza las estadísticas mostradas."""
        if self.correction_service:
            # Aquí deberíamos obtener las estadísticas reales del servicio
            # Por ahora, usamos valores de ejemplo
            corrections = getattr(self.correction_service, 'corrections_count', 0)
            words = getattr(self.correction_service, 'total_words', 0)
            self.status_widget.update_stats(corrections, words)
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "DyslexiLess sigue ejecutándose",
            "La aplicación sigue ejecutándose en segundo plano. Haz clic en el icono para mostrarla de nuevo.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def close_application(self):
        """Cierra completamente la aplicación."""
        if self.correction_service:
            # Detener el servicio antes de cerrar
            try:
                # Aquí deberíamos tener un método para detener el listener
                self.correction_service = None
            except:
                pass
        
        self.tray_icon.hide()
        QApplication.quit()

def main():
    """Función principal que inicia la aplicación."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Evitar que la aplicación se cierre al cerrar la ventana
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()