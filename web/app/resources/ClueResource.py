from app.models.Clue import Clue
from app.models.GamePlayer import GamePlayer
from app.resources.Resource import Resource


class ClueResource(Resource):
    def __init__(self, clue: Clue):
        self.clue = clue

    def data(self) -> dict:
        game_player = GamePlayer.query.filter(
            GamePlayer.game_id == self.clue.game_id,
            GamePlayer.player_id == self.clue.player_id
        ).first()
        return {
            'id': self.clue.id,
            'high': self.clue.scale.high,
            'low': self.clue.scale.low,
            'value': self.clue.value,
            'max_value': self.clue.max_value,
            'clue': self.clue.clue,
            'player_id': self.clue.player_id,
            'player_name': game_player.display_name,
            'total_clues': len(self.clue.game.clues),
            'guess_value': self.clue.guess_value,
        }