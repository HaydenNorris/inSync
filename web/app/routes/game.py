from functools import wraps
from flask import Blueprint, request, jsonify
from app.models.Player import Player
from app.models.Game import Game
from app.models.GamePlayer import GamePlayer
from flask_jwt_extended import jwt_required, get_jwt_identity

game_routes = Blueprint('game', __name__)

def player_must_be_in_game(host: bool = False):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = Player.query.get(get_jwt_identity())
            game = Game.query.filter(Game.id == kwargs['game_id']).first()
            if not game:
                return jsonify({'message': 'Game not found'}), 404

            if not user.belongs_to_game(game):
                return jsonify({'message': 'You are not in this game'}), 403

            if host and not user.is_host(game):
                return jsonify({'message': 'You are not the host of this game'}), 403

            kwargs['game'] = game
            kwargs['user'] = user

            return func(*args, **kwargs)
        return wrapper
    return decorator

@game_routes.route('/game', methods=['POST'])
@jwt_required()
def create_game():
    current_user_id = get_jwt_identity()
    current_user = Player.query.get(current_user_id)
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    display_name = request.get_json().get('display_name', current_user.name)
    game = Game.create(current_user, display_name)
    return jsonify({'game_code': game.code, 'id': game.id}), 201


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

    return jsonify({'game_code': game.code, 'id': game.id}), 200


@game_routes.route('/game/<int:game_id>/players', methods=['GET'])
@player_must_be_in_game()
def game_players(game: 'Game', *args, **kwargs):
    players = GamePlayer.query.filter_by(game_id=game.id).all()
    return jsonify([{ 'player_id': gp.player_id, 'display_name': gp.display_name, 'host': gp.host } for gp in players]), 200


@game_routes.route('/game/<int:game_id>/start', methods=['PUT'])
@player_must_be_in_game(host=True)
def start_game(game: 'Game', *args, **kwargs):
    try:
        game.set_status(Game.STATUS_CLUE_GIVING)
    except Exception as e:
        return jsonify({'message': "Failed to start game"}), 400

    return jsonify({'message': 'Game started'}), 200

