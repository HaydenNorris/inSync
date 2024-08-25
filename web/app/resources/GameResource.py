from app.models.Game import Game
from app.resources.Resource import Resource


class GameResource(Resource):
    def __init__(self, game: Game):
        self.game = game

    def data(self) -> dict:
        return {
            'game_code': self.game.code,
            'id': self.game.id,
            'status': self.game.status
        }
