from app import db
from app.models import BaseModel
from app.models.Game import Game
from app.models.GamePlayer import GamePlayer


class Player(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    games = db.relationship('Game', secondary='game_player', viewonly=True)
    game_players = db.relationship('GamePlayer', viewonly=True)

    def __repr__(self):
        return f"Player('{self.name}')"

    def in_game(self, game):
        return game in self.games

    def is_host(self, game: 'Game'):
       return self.game_players.filter(GamePlayer.game_id == game.id, GamePlayer.host == True).first() is not None
