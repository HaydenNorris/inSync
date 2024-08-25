from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from app.models.Clue import Clue
from app.models.Player import Player
from app.models.Game import Game

def player_must_be_linked_to_clue():
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            clue = Clue.query.filter(Clue.id == kwargs['clue_id']).first()
            if not clue:
                return jsonify({'message': 'Clue not found'}), 404

            player = Player.query.get(get_jwt_identity())
            game = clue.game

            if not player.in_game(game):
                return jsonify({'message': 'You are not in this game'}), 403

            kwargs['clue'] = clue
            kwargs['player'] = player
            kwargs['game'] = game
            return func(*args, **kwargs)
        return wrapper
    return decorator

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