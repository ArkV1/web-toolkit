import os
import uuid
import traceback
from flask import request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
import threading
from app.api import bp
from app.services.transcription import TranscriptionService
from app.core.config import Config
from app import socketio, create_app
from threading import Thread

@bp.route('/')
def index():
    return render_template('index.html')

def run_with_context(ctx, filepath, session_id):
    """Run transcription with app context"""
    with ctx:
        transcribe_and_cleanup(filepath, session_id)

@bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        current_app.logger.info(f"Upload request received. Files: {request.files}")
        current_app.logger.info(f"Form data: {request.form}")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        session_id = request.form.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
            
        current_app.logger.info(f"File received: {file.filename}")
        
        if not Config.allowed_file(file.filename):
            current_app.logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
            
        # Ensure upload directory exists
        upload_dir = current_app.config['UPLOAD_FOLDER']
        current_app.logger.info(f"Upload directory confirmed: {upload_dir}")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename.replace(' ', '_')}"
        filepath = os.path.join(upload_dir, unique_filename)
        
        current_app.logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        current_app.logger.info("File saved successfully")
        
        # Start transcription in background
        ctx = current_app.app_context()
        thread = Thread(target=run_with_context, args=(ctx, filepath, session_id))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'File uploaded successfully, transcription started',
            'status': 'success'
        })
        
    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def transcribe_and_cleanup(file_path, session_id):
    """Handle transcription and cleanup in a background thread"""
    try:
        current_app.logger.info(f"Starting transcription for file: {file_path}")
        transcription_service = TranscriptionService()
        result = transcription_service.transcribe(file_path, session_id)
        
        # Emit the result via Socket.IO
        socketio.emit('transcription_complete', {'text': result}, room=session_id)
        current_app.logger.info("Transcription completed successfully")
        
        try:
            # Clean up the uploaded file
            os.remove(file_path)
            current_app.logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            current_app.logger.error(f"Cleanup error: {str(e)}")
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
    except Exception as e:
        current_app.logger.error(f"Transcription error: {str(e)}")
        socketio.emit('transcription_error', {'error': str(e)}, room=session_id)

@socketio.on('connect')
def handle_connect():
    current_app.logger.info(f"Client connected: {request.sid}")
    socketio.emit('response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    current_app.logger.info(f"Client disconnected: {request.sid}") 