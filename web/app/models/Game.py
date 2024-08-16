from uuid import uuid4
from app import db
from app.models.GamePlayer import GamePlayer
from app.models.Player import Player
from app.models import BaseModel


class Game(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    players = db.relationship('Player', secondary='game_player', back_populates='games')

    def __init__(self):
        self.status = 'NEW'

    @staticmethod
    def create_game(player: Player, display_name: str = None) -> 'Game':
        game = Game()
        game.code = game.__generate_game_code()
        db.session.add(game)
        db.session.commit()
        game.add_player(player, display_name, True)
        return game

    def __generate_game_code(self):
        code = str(uuid4())[:6]
        # Check if code already exists,
        # we only care if it collides with a game that doesn't have status 'FINISHED'
        game = Game.query.filter(Game.code == code, Game.status != 'FINISHED').first()
        if game:
            return self.__generate_game_code()
        return code

    def add_player(self, player: Player, display_name: str = None, host: bool = False):
        if not display_name:
            display_name = player.name
        if player in self.players:
            raise Exception('Player already in game')
        GamePlayer(game_id=self.id, player_id=player.id, display_name=display_name, host=host).save()
        return self

    @staticmethod
    def get_game(game_code: str, status: str = None, active_only: bool = False):
        query = Game.query.filter(Game.code == game_code)
        if active_only:
            query.filter(Game.status != 'FINISHED')
        if status:
            query.filter(Game.status == status)
        return query.first()
