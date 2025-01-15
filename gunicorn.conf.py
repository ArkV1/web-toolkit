import multiprocessing
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server socket settings
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
worker_class = 'gthread'  # Using threaded worker instead of eventlet
workers = 1  # Single worker for WebSocket support
threads = 100  # Number of threads per worker
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 300
keepalive = 2

# Logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'flask_socketio_app'

# SSL (uncomment and configure for HTTPS)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
user = None
group = None
umask = 0
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_reload(server):
    """Called before code is reloaded."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    # Ensure log directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')