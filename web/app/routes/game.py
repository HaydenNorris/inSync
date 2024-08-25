from flask import Blueprint, request, jsonify
from app.models.Clue import Clue
from app.models.Player import Player
from app.models.Game import Game
from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.resources.ClueResource import ClueResource
from app.resources.GamePlayersResource import GamePlayersResource
from app.resources.GameResource import GameResource
from app.routes import player_must_be_logged_in, player_must_be_in_game

game_routes = Blueprint('game', __name__)

@socketio.on('join_game')
def on_join_game(data):
    game_id = data.get('game_id')
    game_code = data.get('game_code')
    game = Game.query.filter(Game.id == game_id, Game.code == game_code).first()
    if not game:
        emit('error', {'message': 'Game not found'}, room=request.sid)
        return

    join_room(game.socket_room)
    emit('player_list', GamePlayersResource(game).data(), room=game.socket_room)

@game_routes.route('/game', methods=['POST'])
@player_must_be_logged_in
def create_game(player: 'Player', *args, **kwargs):
    display_name = request.get_json().get('display_name', player.name)
    game = Game.create(player, display_name)
    return GameResource(game).json(), 201


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

    return GameResource(game).json(), 200

@game_routes.route('/game/<int:game_id>')
@player_must_be_in_game()
def get_game(game: 'Game', *args, **kwargs):
    return GameResource(game).json(), 200

@game_routes.route('/game/<int:game_id>/players', methods=['GET'])
@player_must_be_in_game()
def game_players(game: 'Game', *args, **kwargs):
    return GamePlayersResource(game).json(), 200


@game_routes.route('/game/<int:game_id>/start', methods=['POST'])
@player_must_be_in_game(host=True)
def start_game(game: 'Game', *args, **kwargs):
    try:
        game.set_status(Game.STATUS_CLUE_GIVING)
    except Exception as e:
        return jsonify({'message': f"Failed to start game: {str(e)}"}), 400

    socketio.emit('game_updated', GameResource(game).data(), room=game.socket_room)

    return jsonify({'message': 'Game started'}), 200

@game_routes.route('/game/<int:game_id>/clue/<int:clue_num>')
@player_must_be_in_game()
def get_clue(game: 'Game', player: 'Player', clue_num: int, *args, **kwargs):
    # get all the clues for the game and player
    try:
        clue = game.get_clues_for(player, clue_num)
        return ClueResource(clue).json(), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@game_routes.route('/game/<int:game_id>/guess')
@player_must_be_in_game()
def guess(game: 'Game', player: 'Player', *args, **kwargs):
    clue = Clue.query.filter(Clue.game_id == game.id, Clue.guess_value == None).first()
    if not clue:
        return jsonify({'message': 'No more clues to guess'}), 400
    return ClueResource(clue).json(), 200