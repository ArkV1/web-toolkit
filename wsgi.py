import logging
import sys
from flask import jsonify
from app import create_app, socketio

app = create_app()

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return jsonify(error=str(error)), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'Unhandled Exception: {e}', exc_info=True)
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001) 