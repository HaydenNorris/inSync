from app import create_app
import time

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
