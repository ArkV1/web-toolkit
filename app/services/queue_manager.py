import queue
import threading
import logging
from typing import Dict, Any
from flask import current_app
from app import socketio
from app.services.transcription import TranscriptionService, VALID_MODELS

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.processing_thread = None
        self.is_running = False
        self.transcription_service = TranscriptionService()
        self._app_context = None

    def start(self):
        """Start the queue processing thread"""
        if not self.is_running:
            if not current_app:
                raise RuntimeError("Queue manager must be started within an application context")
            
            self.is_running = True
            # Store the app context for the background thread
            self._app_context = current_app.app_context()
            
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
        queue_size = self.task_queue.qsize()
        logger.info(f"Added task to queue. Current queue size: {queue_size}")
        
        # Notify client about queue position
        socketio.emit('queue_update', {
            'position': queue_size,
            'status': 'queued',
            'queue_id': queue_id
        }, room=session_id)

    def _process_queue(self):
        """Process tasks from the queue"""
        # Enter the app context for the entire processing thread
        with self._app_context:
            while self.is_running:
                try:
                    # Get task with timeout to allow for clean shutdown
                    task = self.task_queue.get(timeout=1)
                    
                    # Notify client that processing is starting
                    socketio.emit('queue_update', {
                        'status': 'processing',
                        'queue_id': task['queue_id']
                    }, room=task['session_id'])
                    
                    # Process the task
                    try:
                        result = self.transcription_service.transcribe(
                            task['file_path'], 
                            task['session_id'],
                            task['model_name']
                        )
                        # Emit the result via Socket.IO
                        socketio.emit('transcription_complete', {
                            'text': result,
                            'queue_id': task['queue_id']
                        }, room=task['session_id'])
                    except Exception as e:
                        logger.error(f"Error processing task: {str(e)}")
                        socketio.emit('error', {
                            'message': f"Error processing file: {str(e)}",
                            'queue_id': task['queue_id']
                        }, room=task['session_id'])
                    
                    # Mark task as done
                    self.task_queue.task_done()
                    
                    # Update queue positions for remaining tasks
                    remaining = self.task_queue.qsize()
                    logger.info(f"Task completed. Remaining tasks: {remaining}")
                    
                    # Notify remaining tasks about their new position
                    if remaining > 0:
                        try:
                            # Get all remaining tasks without removing them
                            with self.task_queue.mutex:
                                remaining_tasks = list(self.task_queue.queue)
                            for pos, remaining_task in enumerate(remaining_tasks, 1):
                                socketio.emit('queue_update', {
                                    'position': pos,
                                    'status': 'queued',
                                    'queue_id': remaining_task['queue_id']
                                }, room=remaining_task['session_id'])
                        except Exception as e:
                            logger.error(f"Error updating queue positions: {str(e)}")

                except queue.Empty:
                    # No tasks available, continue waiting
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