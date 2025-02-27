import logging
import os
from datetime import datetime

class LoggerManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        # Crear directorio de logs si no existe
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurar el logger
        self.logger = logging.getLogger('DyslexiLess')
        self.logger.setLevel(logging.INFO)
        
        # Formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        log_file = os.path.join(log_dir, f'dyslexiless_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message, exc_info=True):
        self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)

# Singleton instance
logger = LoggerManager()
