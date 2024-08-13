from flask import Blueprint, request, jsonify
from app.models.Player import Player
from app.models.Game import Game
from flask_jwt_extended import jwt_required, get_jwt_identity

game_routes = Blueprint('game', __name__)


@game_routes.route('/game', methods=['POST'])
@jwt_required()
def create_game():
    current_user_id = get_jwt_identity()
    current_user = Player.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    display_name = request.get_json().get('display_name', current_user.name)
    game = Game.create_game(current_user, display_name)
    return jsonify({'game_code': game.code}), 201


@game_routes.route('/game/join', methods=['POST'])
@jwt_required()
def join_game():
    user = Player.query.get(get_jwt_identity())
    if not user:
        return jsonify({'message': 'User not found'}), 404
    data = request.get_json()
    if 'game_code' not in data:
        return jsonify({'message': 'game_code is required'}), 400
    game = Game.get_game(data['game_code'], 'NEW')
    if not game:
        return jsonify({'message': 'Game not found'}), 404
    display_name = data.get('display_name', user.name)
    try:
        game.add_player(user, display_name)
    except Exception as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'message': 'Success'}), 200
