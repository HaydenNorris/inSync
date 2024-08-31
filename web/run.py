import os

from app import create_app
import time

from app import socketio

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
        time.sleep(3000)
        continue

if app is None:
    raise Exception("App could not be created")

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'development':
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        pass



