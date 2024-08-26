from flask import Blueprint, request, jsonify

from app.models.Clue import Clue
from app.models.Player import Player
from app.models.Game import Game
from app import socketio
from app.resources.ClueResource import ClueResource
from app.resources.GameResource import GameResource
from app.routes import player_must_be_logged_in, player_must_be_linked_to_clue

clue_routes = Blueprint('clue', __name__)

@clue_routes.route('/clue/<int:clue_id>/guess', methods=['POST'])
@player_must_be_linked_to_clue()
def submit_guess(clue: 'Clue', *args, **kwargs):
    data = request.get_json()
    guess_value = data.get('guess_value', None)
    if not guess_value is None:
        try:
            clue.guess_value = guess_value
            clue.save()
        except Exception as e:
            return jsonify({'message': 'Failed to save'}), 400

        socketio.emit('clue_updated', ClueResource(clue).data(), room=clue.game.socket_room)
        return jsonify({'message': 'Clue submitted'}), 200

    return jsonify({'message': 'Missing guess_value'}), 400

@clue_routes.route('/clue/<int:clue_id>/prompt', methods=['POST'])
@player_must_be_linked_to_clue()
def submit_prompt(player: 'Player', clue: 'Clue', *args, **kwargs):
    data = request.get_json()
    prompt = data.get('prompt')
    if prompt:
        try:
            if clue.player_id != player.id:
                return jsonify({'message': 'You are not the owner of this clue'}), 403
            clue.prompt = prompt
            clue.save()
        except Exception as e:
            return jsonify({'message': 'Failed to save'}), 400

        game = clue.game
        if game.all_clues_given():
            game.set_status(Game.STATUS_GUESSING)
            socketio.emit('game_updated', GameResource(game).data(), room=game.socket_room)
        return jsonify({'message': 'Clue submitted'}), 200
    return jsonify({'message': 'Missing clue'}), 400

@clue_routes.route('/clue/<int:clue_id>/close', methods=['POST'])
@player_must_be_linked_to_clue()
def close_clue(player: 'Player', clue: 'Clue', game: 'Game', *args, **kwargs):
    if clue.player_id == player.id:
        return jsonify({'message': 'You cannot close your own clue'}), 403
    try:
        clue.close()
        socketio.emit('clue_updated', ClueResource(clue).data(), room=game.socket_room)
        return jsonify({'message': 'Clue closed'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to close'}), 400

@clue_routes.route('/clue/<int:clue_id>/refresh')
@player_must_be_logged_in
def refresh_clue(player: 'Player', clue_id: int, *args, **kwargs):
    clue = Clue.query.filter(Clue.id == clue_id, Clue.player_id == player.id).first()
    if not clue:
        return jsonify({'message': 'Clue not found'}), 404

    try:
        clue = clue.refresh()
        return ClueResource(clue).json(), 200
    except Exception as e:
        return jsonify({'message': 'Failed to refresh'}), 400

@clue_routes.route('/clue/<int:clue_id>')
@player_must_be_linked_to_clue()
def get_clue(player: 'Player', clue: 'Clue', *args, **kwargs):
    return ClueResource(clue).json(), 200