# Quick Start

Video transcription service with drag-and-drop interface.

## Local Development

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run
python wsgi.py
```

## Docker

```bash
# Run with Docker
docker compose up --build

# Or in background
docker compose up -d
```

Visit http://localhost:5001

That's it! Drop a video/audio file and get your transcription. 