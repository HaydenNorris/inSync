import sys
import os

# Set the path to the directory containing 'app'
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import create_app

# Create the app using the factory function
app = create_app()

# The WSGI server looks for a variable named `application`
application = app
