from flask import Blueprint, request, jsonify
from app.models.Player import Player
from app.models.Game import Game
from werkzeug.security import generate_password_hash, check_password_hash

# Create a blueprint instance
main_bp = Blueprint('main', __name__)


# Define routes for this blueprint
@main_bp.route('/')
def home():
    return 'Welcome to the Home Page!'


@main_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    for key in ['name', 'email', 'password']:
        if key not in data:
            return jsonify({'message': f'{key} is required'}), 400

    password = generate_password_hash(data['password'])
    player = Player.query.filter_by(email=data['email']).first()
    if player:
        return jsonify({'message': 'Player already exists'}), 400

    new_player = Player(email=data['email'], name=data['name'], password=password)
    new_player.save()
    return jsonify({'message': 'Player created successfully'}), 201
