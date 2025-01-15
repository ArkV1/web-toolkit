# Development Guide

## Quick Start

1. Set up development environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run in development mode:
```bash
FLASK_DEBUG=True python wsgi.py
```

## Code Organization

- `app/__init__.py`: Application factory and extensions
- `app/api/`: API routes and endpoints
- `app/core/`: Core configuration and utilities
- `app/services/`: Business logic and services
- `app/templates/`: HTML templates
- `app/static/`: Static files (CSS, JS, images)

## Development Workflow

1. Create a new feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Run tests (when we add them)
4. Submit a pull request

## Adding New Features

1. **New API Endpoints**
   - Add routes in `app/api/routes.py`
   - Use blueprints for feature grouping

2. **New Services**
   - Create new service in `app/services/`
   - Follow singleton pattern if needed

3. **Configuration Changes**
   - Update `app/core/config.py`
   - Add to `.env.example`

## Testing

(To be implemented)
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Run with `pytest`

## Common Development Tasks

1. **Adding a New Dependency**
   ```bash
   pip install new-package
   pip freeze > requirements.txt
   ```

2. **Database Migrations** (if we add a database)
   ```bash
   flask db migrate -m "migration message"
   flask db upgrade
   ```

3. **Running with Different Whisper Models**
   - Edit `WHISPER_MODEL` in `.env`:
     - tiny: Fastest, least accurate
     - base: Good balance
     - small: Better accuracy
     - medium: High accuracy
     - large: Best accuracy, slowest

## Debugging

1. **Flask Debug Mode**
   - Set `FLASK_DEBUG=True` in `.env`
   - Access debugger at error page

2. **Logging**
   - Check `logs/` directory
   - Development logs are verbose

3. **WebSocket Debugging**
   - Browser console for client-side
   - Server logs for backend

## Code Style

- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions small and focused

## Performance Considerations

1. **File Uploads**
   - Clean up temporary files
   - Use background tasks for processing

2. **WebSocket Connections**
   - Handle disconnections gracefully
   - Limit concurrent connections

3. **Memory Usage**
   - Monitor Whisper model memory usage
   - Clean up resources properly

## Security Best Practices

1. **File Uploads**
   - Validate file types
   - Sanitize filenames
   - Set maximum file size

2. **API Security**
   - Input validation
   - Rate limiting (to be implemented)
   - CORS configuration

3. **Environment Variables**
   - Never commit `.env`
   - Use strong secret keys 