from app.models.Game import Game
from app.models.GamePlayer import GamePlayer

from app.resources.Resource import Resource


class GamePlayersResource(Resource):
    def __init__(self, game: Game):
        self.game = game

    def data(self) -> list:
        players = GamePlayer.query.filter_by(game_id=self.game.id).all()
        return [
            {
                'player_id': gp.player_id,
                'display_name': gp.display_name,
                'host': gp.host
            }
            for gp in players
        ]
