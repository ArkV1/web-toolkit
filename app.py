from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
import whisper
import tempfile
import uuid
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
import threading

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize SocketIO with websocket transport
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize Whisper model
model = whisper.load_model("base")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'm4a'}

def transcribe_file(file_path, session_id):
    try:
        emit('status', {'message': 'Starting transcription...'}, room=session_id)
        
        # Load and transcribe the file
        result = model.transcribe(file_path, verbose=False)
        
        # Send the transcription result
        emit('transcription_complete', {
            'text': result['text'],
            'segments': result['segments']
        }, room=session_id)
        
    except Exception as e:
        emit('error', {'message': str(e)}, room=session_id)
    finally:
        # Clean up the temporary file
        try:
            os.remove(file_path)
        except:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Create a unique filename
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Start transcription in a background thread
        session_id = request.form.get('session_id')
        thread = threading.Thread(target=transcribe_file, args=(filepath, session_id))
        thread.start()
        
        return jsonify({'message': 'File uploaded successfully, transcription started'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, 
                debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
                host=os.getenv('HOST', '0.0.0.0'),
                port=int(os.getenv('PORT', 5001)),
                allow_unsafe_werkzeug=True)