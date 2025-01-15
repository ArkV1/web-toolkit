import logging
from flask import current_app
import whisper
from app import socketio
import traceback

logger = logging.getLogger(__name__)

VALID_MODELS = {
    'tiny', 'tiny.en',
    'base', 'base.en',
    'small', 'small.en',
    'medium', 'medium.en',
    'large-v1', 'large-v2', 'large-v3', 'large',
    'turbo'
}

class TranscriptionService:
    def __init__(self):
        self.models = {}  # Cache for loaded models

    def load_model(self, model_name: str):
        """Load the Whisper model if not already loaded"""
        if model_name not in VALID_MODELS:
            raise ValueError(f"Invalid model name. Must be one of: {', '.join(sorted(VALID_MODELS))}")
            
        if model_name not in self.models:
            current_app.logger.info(f"Loading Whisper model: {model_name}")
            self.models[model_name] = whisper.load_model(model_name)
            current_app.logger.info(f"Whisper model {model_name} loaded successfully")
        return self.models[model_name]

    def transcribe(self, file_path: str, session_id: str, model_name: str = 'base'):
        """Transcribe audio file with progress updates"""
        try:
            model = self.load_model(model_name)
            
            # First detect the language
            current_app.logger.info("Detecting language...")
            audio = whisper.load_audio(file_path)
            
            # Get audio duration for progress calculation
            duration = len(audio) / whisper.audio.SAMPLE_RATE
            current_app.logger.info(f"Audio duration: {duration:.2f} seconds")
            
            # Emit initial progress
            self._emit_progress(0.1, session_id)
            
            # Perform transcription
            current_app.logger.info(f"Starting transcription with {model_name} model...")
            result = model.transcribe(
                audio,
                verbose=True,
                language='en',
                task='transcribe'
            )
            
            # Emit completion
            self._emit_progress(1.0, session_id)
            current_app.logger.info("Transcription completed successfully")
            return result['text']
            
        except Exception as e:
            # Log the error with traceback
            current_app.logger.error(f"Transcription error: {str(e)}")
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            # Re-raise the exception for the caller to handle
            raise

    def _emit_progress(self, progress: float, session_id: str):
        """Emit transcription progress via Socket.IO"""
        try:
            socketio.emit(
                'transcription_progress',
                {'progress': progress * 100},
                room=session_id
            )
        except Exception as e:
            current_app.logger.error(f"Error emitting progress: {str(e)}") 