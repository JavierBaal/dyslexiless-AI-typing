from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import json
import os

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DyslexiLess - Configuración")
        self.setFixedSize(400, 300)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Título
        title = QLabel("Configuración de DyslexiLess")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Selector de servicio
        service_layout = QHBoxLayout()
        service_label = QLabel("Servicio de IA:")
        self.service_selector = QComboBox()
        self.service_selector.addItems(["OpenAI", "Anthropic", "Mixtral"])
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_selector)
        layout.addLayout(service_layout)
        
        # Campo de API Key
        key_layout = QHBoxLayout()
        key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Ingresa tu API key aquí")
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input)
        layout.addLayout(key_layout)
        
        # Botón de guardar
        save_button = QPushButton("Guardar y Comenzar")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)
        
        # Información
        info = QLabel("La aplicación se ejecutará en segundo plano\nPresiona ESC para cerrar")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

    def save_config(self):
        config = {
            "service": self.service_selector.currentText(),
            "api_key": self.api_key_input.text()
        }
        
        config_dir = os.path.expanduser('~/Library/Application Support/DyslexiLess')
        os.makedirs(config_dir, exist_ok=True)
        
        with open(os.path.join(config_dir, 'config.json'), 'w') as f:
            json.dump(config, f)
            
        self.hide()
        # Aquí iniciaremos el servicio de corrección