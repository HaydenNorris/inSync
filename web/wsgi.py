from app import create_app, socketio

# Create the app using the factory function
app = create_app()

# The WSGI server looks for a variable named `application`
application = app
