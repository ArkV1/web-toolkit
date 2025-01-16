import os
import uuid
import traceback
from flask import request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
from app.api import bp
from app.core.config import Config
from app import socketio
from app.services.queue_manager import queue_manager, VALID_MODELS
from app.services.persistent_storage import persistent_storage

@bp.route('/')
def index():
    queue_data = persistent_storage.get_queue()
    results_data = persistent_storage.get_results()
    return render_template('index.html', queue_data=queue_data, results_data=results_data)

@bp.route('/clear-queue', methods=['POST'])
def clear_queue():
    try:
        session_id = request.form.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
            
        queue_manager.clear_queue(session_id)
        return jsonify({'message': 'Queue cleared successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Clear queue error: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        current_app.logger.info(f"Upload request received. Files: {request.files}")
        current_app.logger.info(f"Form data: {request.form}")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        session_id = request.form.get('session_id')
        model_name = request.form.get('model', 'base')
        queue_id = request.form.get('queue_id')
        
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
            
        if not queue_id:
            return jsonify({'error': 'No queue ID provided'}), 400
            
        if model_name not in VALID_MODELS:
            return jsonify({'error': f'Invalid model name. Must be one of: {", ".join(VALID_MODELS)}'}), 400
            
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
        
        # Add to processing queue with selected model
        queue_manager.add_task(filepath, session_id, model_name, queue_id)
        
        return jsonify({
            'message': 'File uploaded successfully, added to processing queue',
            'status': 'success',
            'queue_id': queue_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'queue_id': queue_id if 'queue_id' in locals() else None
        }), 500

@socketio.on('connect')
def handle_connect():
    current_app.logger.info(f"Client connected: {request.sid}")
    socketio.emit('response', {'data': 'Connected'})

@socketio.on('register_client')
def handle_client_registration(data):
    client_id = data.get('clientId')
    if client_id:
        current_app.logger.info(f"Registering client ID {client_id} for socket {request.sid}")
        # Join the client's room using their persistent ID
        socketio.server.enter_room(request.sid, client_id) 