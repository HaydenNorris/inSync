from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies, get_jwt
from app.models.Player import Player
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import timedelta
from datetime import timezone

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

    new_player = Player(email=data['email'], name=data['name'], password=password).save()

    access_token = create_access_token(identity=new_player.id)
    response = jsonify({'message': 'Player created successfully'}), 201
    set_access_cookies(response, access_token)
    return response


@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    for key in ['email', 'password']:
        if key not in data:
            return jsonify({'message': f'{key} is required'}), 400

    player = Player.query.filter_by(email=data['email']).first()
    if not player:
        return jsonify({'message': 'Email not found'}), 404

    if not check_password_hash(player.password, data['password']):
        return jsonify({'message': 'Invalid password'}), 400

    access_token = create_access_token(identity=player.id)
    response = jsonify({'message': 'Logged in successfully'})
    set_access_cookies(response, access_token)
    return response, 200


@main_bp.after_request
def refresh_expiring_jwt(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=10))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


@main_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200


@main_bp.route('/test', methods=['GET'])
@jwt_required()
def test():
    return jsonify({'message': 'You are authorized to access this route'}), 200
