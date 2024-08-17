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

            if not user.in_game(game):
                return jsonify({'message': 'You are not in this game'}), 403

            if host and not user.is_host(game):
                return jsonify({'message': 'You are not the host of this game'}), 403

            kwargs['game'] = game
            kwargs['user'] = user

            return func(*args, **kwargs)
        return wrapper
    return decorator

def player_must_be_logged_in(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = Player.query.get(get_jwt_identity())
        if not user:
            return jsonify({'message': 'User not found'}), 404
        kwargs['user'] = user
        return func(*args, **kwargs)
    return wrapper

@game_routes.route('/game', methods=['POST'])
@player_must_be_logged_in
def create_game(user: 'Player', *args, **kwargs):
    display_name = request.get_json().get('display_name', user.name)
    game = Game.create(user, display_name)
    return jsonify({'game_code': game.code, 'id': game.id}), 201


@game_routes.route('/game/join', methods=['POST'])
@player_must_be_logged_in
def join_game(user: 'Player', *args, **kwargs):
    data = request.get_json()
    code = data.get('game_code')
    if code not in data:
        return jsonify({'message': 'game_code is required'}), 400
    game = Game.query.filter(Game.code == data.get('game_code'), Game.status == Game.STATUS_NEW).first()
    if not game:
        return jsonify({'message': f'Game not found for code {code}'}), 404
    try:
        game.add_player(user, data.get('display_name', user.name))
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

