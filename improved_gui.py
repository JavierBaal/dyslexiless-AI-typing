#!/usr/bin/env python3
"""
Interfaz gráfica mejorada para DyslexiLess.
Esta versión incluye una interfaz más amigable y asistente de configuración.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QSystemTrayIcon,
    QMenu, QMessageBox, QWizard, QWizardPage, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap
import keyboardlistener
import config_manager
from logger_manager import logger

class ConfigWizard(QWizard):
    """Asistente de configuración inicial."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asistente de Configuración DyslexiLess")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
        # Cargar icono si existe
        icon_path = os.path.join("resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Añadir páginas
        self.addPage(WelcomePage())
        self.addPage(ServiceSelectionPage())
        self.addPage(APIConfigPage())
        self.addPage(SettingsPage())
        self.addPage(CompletionPage())
        
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

class WelcomePage(QWizardPage):
    """Página de bienvenida del asistente."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Bienvenido a DyslexiLess")
        self.setSubTitle("Este asistente te ayudará a configurar DyslexiLess para su primer uso.")
        
        layout = QVBoxLayout()
        
        # Agregar logo si existe
        icon_path = os.path.join("resources", "icon.png")
        if os.path.exists(icon_path):
            logo = QLabel()
            pixmap = QPixmap(icon_path)
            logo.setPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio))
            layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Texto de bienvenida
        welcome_text = QLabel(
            "DyslexiLess es tu asistente personal de escritura que te ayuda "
            "a corregir errores comunes de dislexia en tiempo real.\n\n"
            "Este asistente te guiará a través de los siguientes pasos:\n"
            "• Selección del servicio de IA\n"
            "• Configuración de la API\n"
            "• Personalización de ajustes\n\n"
            "Haz clic en 'Siguiente' para comenzar."
        )
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)
        
        self.setLayout(layout)

class ServiceSelectionPage(QWizardPage):
    """Página para seleccionar el servicio de IA."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Selección de Servicio")
        self.setSubTitle("Elige el servicio de IA que deseas utilizar.")
        
        layout = QVBoxLayout()
        
        # Selector de servicio
        self.service_combo = QComboBox()
        self.service_combo.addItems(["OpenAI (Recomendado)", "Anthropic", "Mixtral (Local)"])
        layout.addWidget(QLabel("Servicio de IA:"))
        layout.addWidget(self.service_combo)
        
        # Explicación de cada servicio
        self.service_info = QLabel()
        self.service_info.setWordWrap(True)
        layout.addWidget(self.service_info)
        
        self.service_combo.currentIndexChanged.connect(self.update_service_info)
        self.update_service_info()
        
        self.setLayout(layout)
        
        # Registrar campo
        self.registerField("service", self.service_combo)
    
    def update_service_info(self):
        info = {
            0: "OpenAI ofrece el mejor balance entre precisión y velocidad. Recomendado para la mayoría de usuarios.",
            1: "Anthropic Claude es muy preciso pero puede ser más lento. Bueno para textos complejos.",
            2: "Mixtral es una opción local que no requiere conexión a internet, pero puede ser menos precisa."
        }
        self.service_info.setText(info[self.service_combo.currentIndex()])

class APIConfigPage(QWizardPage):
    """Página para configurar la API key."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Configuración de API")
        self.setSubTitle("Introduce tu clave de API para el servicio seleccionado.")
        
        layout = QVBoxLayout()
        
        # Campo de API key
        self.api_key = QLineEdit()
        self.api_key.setPlaceholderText("Introduce tu API key aquí")
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(self.api_key)
        
        # Botón para mostrar/ocultar API key
        self.show_key = QCheckBox("Mostrar API key")
        self.show_key.stateChanged.connect(self.toggle_key_visibility)
        layout.addWidget(self.show_key)
        
        # Instrucciones
        instructions = QLabel(
            "Para obtener tu API key:\n\n"
            "1. Ve al sitio web del servicio seleccionado\n"
            "2. Crea una cuenta o inicia sesión\n"
            "3. Navega a la sección de API keys\n"
            "4. Genera una nueva key y cópiala aquí"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        self.setLayout(layout)
        
        # Registrar campo
        self.registerField("api_key*", self.api_key)
    
    def toggle_key_visibility(self, state):
        self.api_key.setEchoMode(
            QLineEdit.EchoMode.Normal if state 
            else QLineEdit.EchoMode.Password
        )

class SettingsPage(QWizardPage):
    """Página para configurar ajustes adicionales."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Ajustes Adicionales")
        self.setSubTitle("Personaliza el comportamiento de DyslexiLess.")
        
        layout = QVBoxLayout()
        
        # Iniciar con el sistema
        self.autostart = QCheckBox("Iniciar DyslexiLess automáticamente con el sistema")
        self.autostart.setChecked(True)
        layout.addWidget(self.autostart)
        
        # Mostrar notificaciones
        self.notifications = QCheckBox("Mostrar notificaciones de corrección")
        self.notifications.setChecked(True)
        layout.addWidget(self.notifications)
        
        # Modo silencioso
        self.quiet_mode = QCheckBox("Modo silencioso (sin sonidos)")
        layout.addWidget(self.quiet_mode)
        
        # Corrección agresiva
        self.aggressive = QCheckBox("Corrección agresiva (corregir más errores)")
        layout.addWidget(self.aggressive)
        
        self.setLayout(layout)
        
        # Registrar campos
        self.registerField("autostart", self.autostart)
        self.registerField("notifications", self.notifications)
        self.registerField("quiet_mode", self.quiet_mode)
        self.registerField("aggressive", self.aggressive)

class CompletionPage(QWizardPage):
    """Página final del asistente."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Configuración Completada")
        self.setSubTitle("DyslexiLess está listo para usar.")
        
        layout = QVBoxLayout()
        
        # Mensaje de finalización
        completion_text = QLabel(
            "¡Felicidades! Has completado la configuración de DyslexiLess.\n\n"
            "• La aplicación se iniciará automáticamente\n"
            "• Encontrarás el icono en la barra de sistema\n"
            "• Puedes comenzar a escribir en cualquier aplicación\n\n"
            "Haz clic en 'Finalizar' para comenzar a usar DyslexiLess."
        )
        completion_text.setWordWrap(True)
        layout.addWidget(completion_text)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DyslexiLess")
        self.setFixedSize(400, 300)
        
        # Cargar icono
        icon_path = os.path.join("resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status
        self.status_label = QLabel("Estado: Activo")
        layout.addWidget(self.status_label)
        
        # Estadísticas
        self.stats_label = QLabel("Correcciones: 0")
        layout.addWidget(self.stats_label)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.toggle_button = QPushButton("Pausar")
        self.toggle_button.clicked.connect(self.toggle_service)
        button_layout.addWidget(self.toggle_button)
        
        settings_button = QPushButton("Ajustes")
        settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(settings_button)
        
        layout.addLayout(button_layout)
        
        # Ícono en la barra de sistema
        self.setup_tray()
        
        # Iniciar servicio
        self.start_service()
    
    def setup_tray(self):
        """Configura el ícono en la barra de sistema."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Usar el mismo ícono de la ventana
        icon_path = os.path.join("resources", "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        
        # Menú contextual
        tray_menu = QMenu()
        
        toggle_action = tray_menu.addAction("Pausar")
        toggle_action.triggered.connect(self.toggle_service)
        self.toggle_action = toggle_action
        
        settings_action = tray_menu.addAction("Ajustes")
        settings_action.triggered.connect(self.show_settings)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Salir")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Mostrar la ventana al hacer doble clic
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Maneja los clics en el ícono de la barra de sistema."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def start_service(self):
        """Inicia el servicio de corrección."""
        try:
            self.correction_service = keyboardlistener.start_listener()
            self.status_label.setText("Estado: Activo")
            self.toggle_button.setText("Pausar")
            self.toggle_action.setText("Pausar")
            self.tray_icon.setToolTip("DyslexiLess: Activo")
        except Exception as e:
            logger.error(f"Error al iniciar el servicio: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo iniciar el servicio:\n{str(e)}"
            )
    
    def toggle_service(self):
        """Alterna entre pausar/reanudar el servicio."""
        if self.toggle_button.text() == "Pausar":
            self.status_label.setText("Estado: Pausado")
            self.toggle_button.setText("Reanudar")
            self.toggle_action.setText("Reanudar")
            self.tray_icon.setToolTip("DyslexiLess: Pausado")
        else:
            self.status_label.setText("Estado: Activo")
            self.toggle_button.setText("Pausar")
            self.toggle_action.setText("Pausar")
            self.tray_icon.setToolTip("DyslexiLess: Activo")
    
    def show_settings(self):
        """Muestra la ventana de configuración."""
        wizard = ConfigWizard(self)
        if wizard.exec():
            # Guardar configuración
            config = {
                "service": wizard.field("service"),
                "api_key": wizard.field("api_key"),
                "autostart": wizard.field("autostart"),
                "notifications": wizard.field("notifications"),
                "quiet_mode": wizard.field("quiet_mode"),
                "aggressive": wizard.field("aggressive")
            }
            config_manager.save_config(config)
            
            # Reiniciar servicio
            self.start_service()
    
    def quit_application(self):
        """Cierra la aplicación."""
        reply = QMessageBox.question(
            self,
            "Confirmar Salida",
            "¿Estás seguro de que quieres cerrar DyslexiLess?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de ventana."""
        event.ignore()
        self.hide()

def main():
    """Función principal."""
    app = QApplication(sys.argv)
    
    # Estilo moderno
    app.setStyle("Fusion")
    
    # Comprobar primera ejecución
    if not config_manager.config_exists():
        wizard = ConfigWizard()
        if wizard.exec():
            # Guardar configuración inicial
            config = {
                "service": wizard.field("service"),
                "api_key": wizard.field("api_key"),
                "autostart": wizard.field("autostart"),
                "notifications": wizard.field("notifications"),
                "quiet_mode": wizard.field("quiet_mode"),
                "aggressive": wizard.field("aggressive")
            }
            config_manager.save_config(config)
        else:
            sys.exit(1)
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
