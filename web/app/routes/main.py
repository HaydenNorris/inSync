from flask import Blueprint

# Create a blueprint instance
main_bp = Blueprint('main', __name__)

# Define routes for this blueprint
@main_bp.route('/')
def home():
    return 'Welcome to the Home Page!'