import queue
import threading
import logging
from typing import Dict, Any
from flask import current_app
from app import socketio
from app.services.transcription import TranscriptionService, VALID_MODELS
from app.services.persistent_storage import persistent_storage
import traceback

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.processing_thread = None
        self.is_running = False
        self.transcription_service = TranscriptionService()
        self._app_context = None
        self.current_task = None
        self.processing_lock = threading.Lock()
        self._restore_queue()

    def _restore_queue(self):
        """Restore queue from persistent storage"""
        stored_queue = persistent_storage.get_queue()
        for task in stored_queue:
            self.task_queue.put(task)
        logger.info(f"Restored {len(stored_queue)} tasks from persistent storage")

    def start(self):
        """Start the queue processing thread"""
        if not self.is_running:
            if not current_app:
                raise RuntimeError("Queue manager must be started within an application context")
            
            self.is_running = True
            self._app_context = current_app._get_current_object().app_context()
            
            self.processing_thread = threading.Thread(target=self._process_queue)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            logger.info("Queue manager started")

    def stop(self):
        """Stop the queue processing thread"""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join()
            logger.info("Queue manager stopped")

    def clear_queue(self, session_id: str = None):
        """Clear all tasks from the queue and stop current processing"""
        with self.processing_lock:
            # Stop current processing
            if self.current_task and (not session_id or self.current_task['session_id'] == session_id):
                logger.info("Stopping current task processing")
                socketio.emit('task_cancelled', {
                    'queue_id': self.current_task['queue_id']
                }, to=self.current_task['session_id'])
            
            # Clear the queue
            stored_tasks = []
            while not self.task_queue.empty():
                try:
                    task = self.task_queue.get_nowait()
                    if not session_id or task['session_id'] == session_id:
                        socketio.emit('task_cancelled', {
                            'queue_id': task['queue_id']
                        }, to=task['session_id'])
                        logger.info(f"Removed task from queue: {task['queue_id']}")
                    else:
                        stored_tasks.append(task)
                except queue.Empty:
                    break
            
            # Update persistent storage
            persistent_storage._save_queue(stored_tasks)
            logger.info("Queue cleared")

    def add_task(self, file_path: str, session_id: str, model_name: str = 'base', queue_id: str = None):
        """Add a new transcription task to the queue"""
        if model_name not in VALID_MODELS:
            raise ValueError(f"Invalid model name. Must be one of: {', '.join(VALID_MODELS)}")
            
        task = {
            'file_path': file_path,
            'session_id': session_id,
            'model_name': model_name,
            'queue_id': queue_id
        }
        self.task_queue.put(task)
        
        # Save to persistent storage
        persistent_storage.add_to_queue(task)
        
        queue_size = self.task_queue.qsize()
        logger.info(f"Added task to queue. Current queue size: {queue_size}")
        
        socketio.emit('queue_update', {
            'position': queue_size,
            'status': 'queued',
            'queue_id': queue_id
        }, to=session_id)

    def _process_queue(self):
        """Process tasks from the queue"""
        with self._app_context:
            logger.info("Queue processing thread started with app context")
            while self.is_running:
                try:
                    logger.info("Waiting for next task...")
                    task = self.task_queue.get(timeout=1)
                    logger.info(f"Got task from queue: {task['queue_id']}")
                    
                    with self.processing_lock:
                        self.current_task = task
                        logger.info(f"Processing task: {task['queue_id']}")
                    
                    # Remove from persistent storage
                    persistent_storage.remove_from_queue(task['queue_id'])
                    
                    socketio.emit('queue_update', {
                        'status': 'processing',
                        'queue_id': task['queue_id']
                    }, to=task['session_id'])
                    
                    try:
                        logger.info(f"Starting transcription for task: {task['queue_id']}")
                        result = self.transcription_service.transcribe(
                            task['file_path'], 
                            task['session_id'],
                            task['model_name']
                        )
                        logger.info(f"Transcription completed for task: {task['queue_id']}")
                        
                        # Save result to persistent storage
                        persistent_storage.save_result(task['queue_id'], result)
                        
                        logger.info(f"Emitting completion for task: {task['queue_id']}")
                        socketio.emit('transcription_complete', {
                            'text': result,
                            'queue_id': task['queue_id']
                        }, to=task['session_id'])
                    except Exception as e:
                        logger.error(f"Error processing task: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        socketio.emit('error', {
                            'message': f"Error processing file: {str(e)}",
                            'queue_id': task['queue_id']
                        }, to=task['session_id'])
                    finally:
                        with self.processing_lock:
                            self.current_task = None
                    
                    self.task_queue.task_done()
                    
                    remaining = self.task_queue.qsize()
                    logger.info(f"Task completed. Remaining tasks: {remaining}")
                    
                    if remaining > 0:
                        try:
                            with self.task_queue.mutex:
                                remaining_tasks = list(self.task_queue.queue)
                            for pos, remaining_task in enumerate(remaining_tasks, 1):
                                socketio.emit('queue_update', {
                                    'position': pos,
                                    'status': 'queued',
                                    'queue_id': remaining_task['queue_id']
                                }, to=remaining_task['session_id'])
                        except Exception as e:
                            logger.error(f"Error updating queue positions: {str(e)}")

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in queue processing: {str(e)}")
                    if 'task' in locals():
                        socketio.emit('error', {
                            'message': f"Queue processing error: {str(e)}",
                            'queue_id': task['queue_id']
                        }, room=task['session_id'])

# Create a global instance
queue_manager = QueueManager() 