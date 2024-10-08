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
        print(f"Error creating app: {e}, attempt {attempt}/{attempt_limit}")
        time.sleep(3)
        continue

if app is None:
    raise Exception("App could not be created")

port = int(os.environ.get('PORT', 5000))

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'development':
        print("Running in development mode")
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
if os.environ.get('FLASK_ENV') == 'production':
    print("Running in production mode!")
    try:
        socketio.run(app, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Error running app: {e}")