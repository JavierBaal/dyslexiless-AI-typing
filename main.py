import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QComboBox, QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt
import keyboardlistener
import config_manager

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DyslexiLess Configuration")
        self.setFixedSize(400, 300)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # API Service selector
        self.service_selector = QComboBox()
        self.service_selector.addItems(["OpenAI", "Anthropic", "Ollama (Local)"])
        layout.addWidget(QLabel("Select AI Service:"))
        layout.addWidget(self.service_selector)
        
        # API Key input
        self.api_key = QLineEdit()
        self.api_key.setPlaceholderText("Enter API Key")
        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(self.api_key)
        
        # Save button
        save_button = QPushButton("Save & Start")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

    def save_config(self):
        config = {
            "service": self.service_selector.currentText(),
            "api_key": self.api_key.text()
        }
        config_manager.save_config(config)
        self.hide()
        self.start_background_service()

    def start_background_service(self):
        self.correction_service = keyboardlistener.start_listener()

def main():
    app = QApplication(sys.argv)
    
    if not config_manager.config_exists():
        window = ConfigWindow()
        window.show()
    else:
        keyboardlistener.start_listener()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()