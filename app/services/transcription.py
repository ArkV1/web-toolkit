import logging
from flask import current_app
import whisper
from app import socketio
import traceback

class TranscriptionService:
    def __init__(self):
        self.model = None

    def load_model(self):
        """Load the Whisper model if not already loaded"""
        if self.model is None:
            current_app.logger.info(f"Loading Whisper model: {current_app.config['WHISPER_MODEL']}")
            self.model = whisper.load_model(current_app.config['WHISPER_MODEL'])
            current_app.logger.info("Whisper model loaded successfully")
        return self.model

    def transcribe(self, file_path, session_id):
        """Transcribe audio file with progress updates"""
        try:
            model = self.load_model()
            
            # First detect the language
            current_app.logger.info("Detecting language...")
            audio = whisper.load_audio(file_path)
            
            # Get audio duration for progress calculation
            duration = len(audio) / whisper.audio.SAMPLE_RATE
            current_app.logger.info(f"Audio duration: {duration:.2f} seconds")
            
            # Emit initial progress
            self._emit_progress(0.1, session_id)
            
            # Perform transcription
            current_app.logger.info("Starting transcription...")
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

    def _emit_progress(self, progress, session_id):
        """Emit transcription progress via Socket.IO"""
        try:
            socketio.emit(
                'transcription_progress',
                {'progress': progress * 100},
                room=session_id
            )
        except Exception as e:
            current_app.logger.error(f"Error emitting progress: {str(e)}") 