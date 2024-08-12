from uuid import uuid4
from app import db
from app.models.GamePlayer import game_player
from app.models.Player import Player


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    players = db.relationship('Player', secondary=game_player, back_populates='games')

    def __init__(self, players):
        self.status = 'NEW'
        self.players = players

    @staticmethod
    def create_game(player: Player):
        game = Game(players=[player])
        db.session.add(game)
        db.session.commit()
        return game
