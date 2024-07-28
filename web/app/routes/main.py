from flask import Blueprint
from app.models.Player import Player
from app.models.Game import Game

# Create a blueprint instance
main_bp = Blueprint('main', __name__)


# Define routes for this blueprint
@main_bp.route('/')
def home():
    return 'Welcome to the Home Page!'


@main_bp.route('/game/<player_id>', methods=['POST'])
def newGame(player_id):
    player = Player.query.filter_by(uuid=player_id).first()
    game = Game.create_game(player)
    return game.uuid


# @main_bp.route('/player/<player_id>', methods=['GET'])
# def newGame(player_id):
#     player = Player.query.filter_by(uuid=player_id).first()
#     player_game = player.games[0].uuid
#     return f'Found player: {player_game}'
