#!/usr/bin/env python3
"""
Sistema de procesamiento por lotes para optimizar las correcciones de texto.
Implementa una cola de prioridad y procesamiento asíncrono.
"""

import asyncio
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
import time
from datetime import datetime
import heapq
from threading import Lock
from logger_manager import logger
from interfaces import ICorrector

@dataclass(order=True)
class CorrectionTask:
    """Tarea de corrección con prioridad."""
    priority: int
    timestamp: float
    word: str
    context: str
    callback: Callable[[str, bool], None]
    batch_id: int = 0
    
    def __post_init__(self):
        """Inicialización posterior para garantizar unicidad."""
        self._id = id(self)  # ID único para desempate
    
    def __eq__(self, other):
        return self._id == other._id

class BatchProcessor:
    """
    Procesador de lotes para correcciones de texto.
    
    Características:
    - Cola de prioridad para tareas
    - Procesamiento asíncrono
    - Agrupación inteligente de tareas
    - Límites configurables
    """
    
    def __init__(
        self,
        corrector: ICorrector,
        batch_size: int = 10,
        max_delay: float = 0.5,
        min_batch_items: int = 3
    ):
        self.corrector = corrector
        self.batch_size = batch_size
        self.max_delay = max_delay
        self.min_batch_items = min_batch_items
        
        self.tasks: List[CorrectionTask] = []
        self.batch_lock = Lock()
        self.next_batch_id = 0
        
        # Iniciar procesador asíncrono
        self.loop = asyncio.new_event_loop()
        self.running = True
        self.processor_task = asyncio.run_coroutine_threadsafe(
            self._process_batches(),
            self.loop
        )
        
        logger.info("BatchProcessor iniciado")
    
    def add_task(
        self,
        word: str,
        context: str,
        callback: Callable[[str, bool], None],
        priority: int = 1
    ):
        """
        Añade una tarea de corrección a la cola.
        
        Args:
            word: Palabra a corregir
            context: Contexto de la palabra
            callback: Función a llamar con el resultado
            priority: Prioridad (1-5, mayor número = mayor prioridad)
        """
        with self.batch_lock:
            task = CorrectionTask(
                -priority,  # Negativo para que heapq ordene correctamente
                time.time(),
                word,
                context,
                callback
            )
            heapq.heappush(self.tasks, task)
            logger.debug(f"Tarea añadida: {word} (prioridad: {priority})")
    
    async def _process_batches(self):
        """Procesa las tareas en lotes de forma asíncrona."""
        while self.running:
            try:
                batch = self._create_batch()
                if batch:
                    await self._process_batch(batch)
                else:
                    await asyncio.sleep(0.1)  # Evitar CPU spinning
            except Exception as e:
                logger.error(f"Error en procesamiento de lote: {e}")
                await asyncio.sleep(1)  # Pausa más larga en caso de error
    
    def _create_batch(self) -> List[CorrectionTask]:
        """Crea un lote de tareas para procesar."""
        with self.batch_lock:
            if not self.tasks:
                return []
            
            # Asignar ID de lote
            batch_id = self.next_batch_id
            self.next_batch_id += 1
            
            # Extraer tareas hasta llenar el lote
            batch = []
            while self.tasks and len(batch) < self.batch_size:
                task = heapq.heappop(self.tasks)
                task.batch_id = batch_id
                batch.append(task)
                
                # Si tenemos el mínimo de items y ha pasado el tiempo máximo, procesar
                if (len(batch) >= self.min_batch_items and 
                    time.time() - batch[0].timestamp >= self.max_delay):
                    break
            
            return batch
    
    async def _process_batch(self, batch: List[CorrectionTask]):
        """Procesa un lote de tareas."""
        try:
            # Agrupar tareas por contexto similar
            context_groups = self._group_by_context(batch)
            
            # Procesar cada grupo
            for tasks in context_groups.values():
                corrections = await self._correct_group(tasks)
                
                # Notificar resultados
                for task, (correction, was_corrected) in zip(tasks, corrections):
                    try:
                        task.callback(correction, was_corrected)
                    except Exception as e:
                        logger.error(f"Error en callback: {e}")
            
            logger.debug(f"Lote {batch[0].batch_id} procesado: {len(batch)} tareas")
            
        except Exception as e:
            logger.error(f"Error procesando lote {batch[0].batch_id}: {e}")
    
    def _group_by_context(
        self,
        batch: List[CorrectionTask]
    ) -> Dict[str, List[CorrectionTask]]:
        """Agrupa tareas con contexto similar."""
        groups: Dict[str, List[CorrectionTask]] = {}
        
        for task in batch:
            # Usar primeras 3 palabras como clave de contexto
            context_key = " ".join(task.context.split()[:3])
            if context_key not in groups:
                groups[context_key] = []
            groups[context_key].append(task)
        
        return groups
    
    async def _correct_group(
        self,
        tasks: List[CorrectionTask]
    ) -> List[Tuple[str, bool]]:
        """Corrige un grupo de tareas relacionadas."""
        try:
            # Combinar contexto para corrección en lote
            combined_context = " ".join(t.context for t in tasks)
            words = [t.word for t in tasks]
            
            # Realizar corrección
            corrections = []
            for word in words:
                correction, was_corrected = self.corrector.correct_text(
                    word,
                    combined_context
                )
                corrections.append((correction, was_corrected))
            
            return corrections
            
        except Exception as e:
            logger.error(f"Error en corrección de grupo: {e}")
            # Devolver palabras originales en caso de error
            return [(t.word, False) for t in tasks]
    
    def stop(self):
        """Detiene el procesador de lotes."""
        self.running = False
        # Procesar tareas restantes
        with self.batch_lock:
            remaining = len(self.tasks)
            if remaining > 0:
                logger.info(f"Procesando {remaining} tareas pendientes...")
                batch = self._create_batch()
                if batch:
                    asyncio.run_coroutine_threadsafe(
                        self._process_batch(batch),
                        self.loop
                    ).result()
        logger.info("BatchProcessor detenido")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del procesador."""
        with self.batch_lock:
            return {
                'pending_tasks': len(self.tasks),
                'batches_processed': self.next_batch_id,
                'is_running': self.running
            }

# Ejemplo de uso:
"""
processor = BatchProcessor(corrector)

def correction_callback(correction: str, was_corrected: bool):
    print(f"Corrección recibida: {correction} (corregido: {was_corrected})")

# Añadir tareas
processor.add_task("qe", "creo qe esto", correction_callback, priority=2)
processor.add_task("kiero", "kiero ir", correction_callback, priority=1)

# Las correcciones se procesarán en lotes y los resultados se enviarán
# a través del callback cuando estén listos
"""
