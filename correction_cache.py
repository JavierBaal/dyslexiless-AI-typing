import json
import os
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

class CorrectionCache:
    def __init__(self, cache_file: str = "correction_cache.json", max_size: int = 1000, ttl_days: int = 30):
        self.cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), cache_file)
        self.max_size = max_size
        self.ttl = timedelta(days=ttl_days)
        self.cache: Dict[str, Dict] = {}
        self.load_cache()

    def load_cache(self):
        """Carga el caché desde el archivo si existe."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # Filtrar entradas expiradas durante la carga
                    current_time = datetime.now()
                    self.cache = {
                        word: data for word, data in cached_data.items()
                        if datetime.fromisoformat(data['timestamp']) + self.ttl > current_time
                    }
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.cache = {}

    def save_cache(self):
        """Guarda el caché en el archivo."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def get(self, word: str, context: str) -> Optional[Tuple[str, bool]]:
        """
        Obtiene una corrección del caché si existe y no ha expirado.
        
        Args:
            word: Palabra a corregir
            context: Contexto de la palabra
            
        Returns:
            Tuple[str, bool] si existe en caché, None si no existe
        """
        if word in self.cache:
            entry = self.cache[word]
            cached_time = datetime.fromisoformat(entry['timestamp'])
            
            # Verificar si la entrada ha expirado
            if cached_time + self.ttl > datetime.now():
                # Si el contexto coincide o es similar, usar la corrección en caché
                if self._context_similarity(context, entry['context']) >= 0.7:
                    return entry['correction'], entry['was_corrected']
        return None

    def add(self, word: str, context: str, correction: str, was_corrected: bool):
        """
        Añade una corrección al caché.
        
        Args:
            word: Palabra original
            context: Contexto de la palabra
            correction: Palabra corregida
            was_corrected: Si la palabra fue corregida
        """
        # Si el caché está lleno, eliminar la entrada más antigua
        if len(self.cache) >= self.max_size:
            oldest_word = min(self.cache.keys(), 
                            key=lambda k: datetime.fromisoformat(self.cache[k]['timestamp']))
            del self.cache[oldest_word]

        self.cache[word] = {
            'correction': correction,
            'was_corrected': was_corrected,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        self.save_cache()

    def _context_similarity(self, context1: str, context2: str) -> float:
        """
        Calcula la similitud entre dos contextos.
        Implementación simple basada en palabras comunes.
        
        Returns:
            float: Score de similitud entre 0 y 1
        """
        if not context1 or not context2:
            return 0.0
            
        words1 = set(context1.lower().split())
        words2 = set(context2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    def clear_expired(self):
        """Limpia las entradas expiradas del caché."""
        current_time = datetime.now()
        expired_words = [
            word for word, data in self.cache.items()
            if datetime.fromisoformat(data['timestamp']) + self.ttl <= current_time
        ]
        
        for word in expired_words:
            del self.cache[word]
            
        if expired_words:
            self.save_cache()
