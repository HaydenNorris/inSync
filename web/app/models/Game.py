from uuid import uuid4
from app import db
from app.models.GamePlayer import game_player
from app.models.Player import Player


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    players = db.relationship('Player', secondary=game_player, back_populates='games')

    def __init__(self, players):
        self.status = 'NEW'
        self.players = players

    @staticmethod
    def create_game(player: Player):
        game = Game(players=[player])
        game.code = game.__generate_game_code()
        db.session.add(game)
        db.session.commit()
        return game

    def __generate_game_code(self):
        code = str(uuid4())[:6]
        # Check if code already exists,
        # we only care if it collides with a game that doesn't have status 'FINISHED'
        game = Game.query.filter(Game.code == code, Game.status != 'FINISHED').first()
        if game:
            return self.__generate_game_code()
        return code

    def add_player(self, player: Player):
        if player in self.players:
            raise Exception('Player already in game')
        self.players.append(player)
        db.session.commit()
        return self

    @staticmethod
    def get_game(game_code: str, status: str = None, active_only: bool = False):
        query = Game.query.filter(Game.code == game_code)
        if active_only:
            query.filter(Game.status != 'FINISHED')
        if status:
            query.filter(Game.status == status)
        return query.first()
