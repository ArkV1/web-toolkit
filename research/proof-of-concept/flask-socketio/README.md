# Flask-SocketIO Production Application

A production-ready Flask application with SocketIO support for real-time bidirectional communication.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Development

Run the development server:
```bash
python app.py
```

## Production Deployment

For production deployment, we use Gunicorn with Eventlet worker. The configuration is in `gunicorn.conf.py`.

1. Create required directories:
```bash
mkdir -p logs
```

2. Start the server:
```bash
gunicorn -c gunicorn.conf.py app:app
```

### Gunicorn Configuration

The `gunicorn.conf.py` file includes:
- Single worker with Eventlet for WebSocket support
- 1000 threads per worker
- Proper logging configuration
- Process management
- Server hooks
- Environment variable integration

### Important Production Notes:

1. Always change the SECRET_KEY in production
2. Configure proper CORS settings in production
3. Use HTTPS in production (uncomment and configure SSL settings in gunicorn.conf.py)
4. Set up proper logging (logs directory will be created automatically)
5. Consider using a process manager like Supervisor
6. Use a reverse proxy (Nginx/Apache) in front of Gunicorn

#### Example Supervisor Configuration

Create `/etc/supervisor/conf.d/flask_socketio.conf`:
```ini
[program:flask_socketio]
directory=/path/to/your/app
command=/path/to/venv/bin/gunicorn -c gunicorn.conf.py app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/flask_socketio.err.log
stdout_logfile=/var/log/supervisor/flask_socketio.out.log
```

## Features

- Real-time bidirectional communication
- Production-ready configuration
- Easy to deploy
- Scalable architecture
- Clean and modern UI
- Comprehensive logging
- Process management
- Environment-based configuration

## License

MIT