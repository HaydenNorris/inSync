from flask import Blueprint, request, jsonify
from app.models.Player import Player
from app.models.Game import Game
from app.models.GamePlayer import GamePlayer
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
@jwt_required()
def game_players(game_id: int):
    user = Player.query.get(get_jwt_identity())
    game = Game.query.filter(Game.id == game_id, Game.status != 'FINISHED').first()
    if not game:
        return jsonify({'message': 'No active game found'}), 404

    player_belongs = False

    players = GamePlayer.query.filter_by(game_id=game.id).all()

    body = []
    for gp in players:
        body.append({'player_id': gp.player_id, 'display_name': gp.display_name, 'host': gp.host})
        if gp.player_id == user.id:
            player_belongs = True

    if not player_belongs:
        return jsonify({'message': 'You are not in this game'}), 403

    return jsonify(body), 200
