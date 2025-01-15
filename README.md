# Video Transcription Service

A Flask application that provides real-time video/audio transcription using OpenAI's Whisper model.

## Features

- Drag-and-drop file upload
- Real-time transcription progress via WebSocket
- Support for multiple audio/video formats
- Timestamped transcription segments
- Clean and modern UI

## Project Structure

```
.
├── app/
│   ├── __init__.py          # Application factory
│   ├── api/                 # API routes
│   ├── core/                # Core configuration
│   ├── services/            # Business logic
│   ├── static/              # Static files
│   └── templates/           # HTML templates
├── config/                  # Configuration files
├── tests/                   # Test files
├── uploads/                 # Upload directory
├── logs/                    # Log files
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── wsgi.py                # WSGI entry point
```

## Prerequisites

- Python 3.12+
- FFmpeg (required for audio processing)
- pip (Python package manager)

## Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Create required directories:
```bash
mkdir -p uploads logs
```

6. Run the development server:
```bash
python wsgi.py
```

The application will be available at http://localhost:5001

## Docker Setup

1. Build and start the container:
```bash
docker compose up --build
```

2. Or run in detached mode:
```bash
docker compose up -d
```

3. View logs:
```bash
docker compose logs -f
```

4. Stop the container:
```bash
docker compose down
```

The application will be available at http://localhost:5001

## Docker Commands Reference

- Rebuild the container:
```bash
docker compose build --no-cache
```

- Restart the service:
```bash
docker compose restart web
```

- View container status:
```bash
docker compose ps
```

- Execute commands inside the container:
```bash
docker compose exec web bash
```

## Configuration

The application can be configured through environment variables in `.env`:

- `FLASK_DEBUG`: Enable debug mode (default: False)
- `SECRET_KEY`: Flask secret key
- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to listen on (default: 5001)
- `WHISPER_MODEL`: Whisper model size (tiny/base/small/medium/large)

## Supported File Formats

- Video: mp4, avi, mov, mkv
- Audio: mp3, wav, m4a

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # If you have one
```

2. Run tests:
```bash
pytest
```

3. Run with debug mode:
```bash
FLASK_DEBUG=True python wsgi.py
```

## Production Deployment Notes

1. Always change the default SECRET_KEY
2. Configure proper CORS settings
3. Use HTTPS in production
4. Set up proper logging
5. Consider using a process manager (e.g., Supervisor)
6. Use a reverse proxy (Nginx/Apache) in front of Gunicorn

## Troubleshooting

1. Port already in use:
   - Change the port in .env file
   - Or stop the process using the port: `lsof -i :5001`

2. FFmpeg not found:
   - Install FFmpeg:
     - macOS: `brew install ffmpeg`
     - Ubuntu: `sudo apt-get install ffmpeg`
     - Windows: Download from FFmpeg website

3. Memory issues:
   - Reduce Whisper model size in config
   - Adjust Docker memory limits in docker-compose.yml

## License

MIT