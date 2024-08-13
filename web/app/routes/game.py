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
    game = Game.create_game(current_user)
    return jsonify({'game_id': game.id}), 201
