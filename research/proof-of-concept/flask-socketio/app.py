from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')

# Initialize SocketIO with websocket transport
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print('received message: ' + str(data))
    emit('response', {'data': f'Server received: {data}'}, broadcast=True)

if __name__ == '__main__':
    # In development
    socketio.run(app, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', 
                host=os.getenv('HOST', '0.0.0.0'),
                port=int(os.getenv('PORT', 5000)),
                allow_unsafe_werkzeug=True)