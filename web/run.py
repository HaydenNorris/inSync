from app import create_app
import time
from flask_socketio import SocketIO, emit, send
from flask import request

attempt = 0
app = None
attempt_limit = 3
while attempt < attempt_limit:
    try:
        app = create_app()
        break
    except Exception as e:
        attempt += 1
        if attempt == attempt_limit:
            raise e
        time.sleep(1)
        continue

if app is None:
    raise Exception("App could not be created")

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Dictionary to store client session IDs
client = None
@socketio.on('connect')
def handle_connect():
    client = request.sid # as in the older answer
    print('Client connected with session ID!:', client)

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    send('hi', to=client)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
