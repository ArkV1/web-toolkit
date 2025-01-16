import json
import os
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class PersistentStorage:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = Path(storage_dir)
        self.queue_file = self.storage_dir / "queue.json"
        self.results_file = self.storage_dir / "results.json"
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage directory and files exist"""
        self.storage_dir.mkdir(exist_ok=True)
        if not self.queue_file.exists():
            self._save_queue([])
        if not self.results_file.exists():
            self._save_results({})
    
    def _save_queue(self, queue_data: List[Dict[str, Any]]):
        """Save queue data to file"""
        with open(self.queue_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
    
    def _save_results(self, results_data: Dict[str, Any]):
        """Save results data to file"""
        with open(self.results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
    
    def get_queue(self) -> List[Dict[str, Any]]:
        """Get current queue data"""
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading queue file: {e}")
            return []
    
    def get_results(self) -> Dict[str, Any]:
        """Get stored results"""
        try:
            with open(self.results_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading results file: {e}")
            return {}
    
    def add_to_queue(self, task: Dict[str, Any]):
        """Add a task to the queue"""
        queue_data = self.get_queue()
        queue_data.append(task)
        self._save_queue(queue_data)
    
    def remove_from_queue(self, queue_id: str) -> Dict[str, Any]:
        """Remove and return a task from the queue"""
        queue_data = self.get_queue()
        for i, task in enumerate(queue_data):
            if task['queue_id'] == queue_id:
                removed_task = queue_data.pop(i)
                self._save_queue(queue_data)
                return removed_task
        return None
    
    def save_result(self, queue_id: str, result: str):
        """Save a transcription result"""
        results = self.get_results()
        results[queue_id] = result
        self._save_results(results)
    
    def clear_queue(self):
        """Clear the entire queue"""
        self._save_queue([])

# Create a global instance
persistent_storage = PersistentStorage() 