from app import create_app, socketio

# Create the app using the factory function
app = create_app()

if __name__ == "__main__":
    import eventlet
    eventlet.monkey_patch()
    socketio.run(app, host="0.0.0.0", port=5000)

# The WSGI server looks for a variable named `application`
application = app
