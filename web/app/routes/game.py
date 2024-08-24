from functools import wraps
from flask import Blueprint, request, jsonify

from app.models.Clue import Clue
from app.models.Player import Player
from app.models.Game import Game
from app.models.GamePlayer import GamePlayer
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit, join_room, leave_room
from app import socketio

game_routes = Blueprint('game', __name__)

def player_must_be_in_game(host: bool = False):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            player = Player.query.get(get_jwt_identity())
            game = Game.query.filter(Game.id == kwargs['game_id']).first()
            if not game:
                return jsonify({'message': 'Game not found'}), 404

            if not player.in_game(game):
                return jsonify({'message': 'You are not in this game'}), 403

            if host and not player.is_host(game):
                return jsonify({'message': 'You are not the host of this game'}), 403

            kwargs['game'] = game
            kwargs['player'] = player

            return func(*args, **kwargs)
        return wrapper
    return decorator

def player_must_be_logged_in(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        player = Player.query.get(get_jwt_identity())
        if not player:
            return jsonify({'message': 'Player not found'}), 404
        kwargs['player'] = player
        return func(*args, **kwargs)
    return wrapper

@socketio.on('join_game')
def on_join_game(data):
    game_id = data.get('game_id')
    game_code = data.get('game_code')
    game = Game.query.filter(Game.id == game_id, Game.code == game_code).first()
    if not game:
        emit('error', {'message': 'Game not found'}, room=request.sid)
        return

    room = f"game_{game_code}_{game_id}"
    join_room(room)
    emit('new_player_joined', room=room)
    players = GamePlayer.query.filter_by(game_id=game.id).all()
    emit('player_list', [{'player_id': gp.player_id, 'display_name': gp.display_name, 'host': gp.host} for gp in players], room=room)

@game_routes.route('/game', methods=['POST'])
@player_must_be_logged_in
def create_game(player: 'Player', *args, **kwargs):
    display_name = request.get_json().get('display_name', player.name)
    game = Game.create(player, display_name)
    return jsonify({'game_code': game.code, 'id': game.id}), 201


@game_routes.route('/game/join', methods=['POST'])
@player_must_be_logged_in
def join_game(player: 'Player', *args, **kwargs):
    data = request.get_json()
    code = data.get('game_code')
    if not code:
        return jsonify({'message': 'game_code is required'}), 400
    game = Game.query.filter(Game.code == code, Game.status == Game.STATUS_NEW).first()
    if not game:
        return jsonify({'message': f'Game not found for code {code}'}), 404
    try:
        game.add_player(player, data.get('display_name', player.name))
    except Exception as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'game_code': game.code, 'id': game.id}), 200

@game_routes.route('/game/<int:game_id>')
@player_must_be_in_game()
def get_game(game: 'Game', *args, **kwargs):
    return jsonify({'game_code': game.code, 'id': game.id, 'status': game.status}), 200

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
        return jsonify({'message': f"Failed to start game: {str(e)}"}), 400

    return jsonify({'message': 'Game started'}), 200

@game_routes.route('/game/<int:game_id>/clue/<int:clue_num>')
@player_must_be_in_game()
def get_clue(game: 'Game', player: 'Player', clue_num: int, *args, **kwargs):
    # get all the clues for the game and player
    try:
        clue = game.get_clues_for(player, clue_num)
        return jsonify({
            'id': clue.id,
            'high': clue.scale.high,
            'low': clue.scale.low,
            'value': clue.value,
            'max_value': clue.max_value,
            'clue': clue.clue,
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@game_routes.route('/clue/<int:clue_id>', methods=['PATCH'])
@player_must_be_logged_in
def submit_clue(player: 'Player', clue_id: int, *args, **kwargs):
    clue = Clue.query.filter(Clue.id == clue_id, Clue.player_id == player.id).first()
    if not clue:
        return jsonify({'message': 'Clue not found'}), 404

    data = request.get_json()
    clue_value = data.get('clue')
    if not clue_value:
        return jsonify({'message': f'clue value is required'}), 400

    try:
        clue.clue = clue_value
        clue.save()
    except Exception as e:
        return jsonify({'message': 'Failed to save'}), 400

    game = clue.game
    if game.all_clues_given():
        game.set_status(Game.STATUS_GUESSING)

    return jsonify({'message': 'Clue submitted'}), 200


@game_routes.route('/clue/<int:clue_id>/refresh')
@player_must_be_logged_in
def refresh_clue(player: 'Player', clue_id: int, *args, **kwargs):
    clue = Clue.query.filter(Clue.id == clue_id, Clue.player_id == player.id).first()
    if not clue:
        return jsonify({'message': 'Clue not found'}), 404

    try:
        clue = clue.refresh()
        return jsonify({
            'id': clue.id,
            'high': clue.scale.high,
            'low': clue.scale.low,
            'value': clue.value,
            'max_value': clue.max_value,
            'clue': clue.clue,
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to refresh'}), 400

@game_routes.route('/game/<int:game_id>/guess')
@player_must_be_in_game()
def guess(game: 'Game', player: 'Player', *args, **kwargs):
    clue = Clue.query.filter(Clue.game_id == game.id, Clue.guess_value == None).first()
    if not clue:
        return jsonify({'message': 'No more clues to guess'}), 400
    return jsonify({
        'id': clue.id,
        'high': clue.scale.high,
        'low': clue.scale.low,
        'value': clue.value,
        'max_value': clue.max_value,
        'clue': clue.clue,
        'player_id': clue.player_id,
    }), 200