from uuid import uuid4
from app import db
from app.models.GamePlayer import GamePlayer
from app.models import BaseModel, Player


class Game(BaseModel):
    STATUS_NEW = 'NEW'
    STATUS_CLUE_GIVING = 'CLUE_GIVING'
    STATUS_GUESSING = 'GUESSING'
    STATUS_FINISHED = 'FINISHED'

    id = db.Column(db.Integer, primary_key=True)
    _status = db.Column('status', db.String(80), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    players = db.relationship('Player', secondary='game_player', back_populates='games')

    @property
    def status(self):
        return self._status

    def set_status(self, value):
        if value not in [self.STATUS_NEW, self.STATUS_CLUE_GIVING, self.STATUS_GUESSING, self.STATUS_FINISHED]:
            raise Exception('Invalid status')

        if value == self.status:
            return self

        if value == self.STATUS_NEW and self.status:
            raise Exception('Game already started')

        if value == self.STATUS_CLUE_GIVING:
            if len(self.players) < 2:
                raise Exception('Invalid status change: Game must have at least 2 players')

            if self.status != self.STATUS_NEW:
                raise Exception('Invalid status change: Game must be in status NEW to change to CLUE_GIVING')

        # a game can only be marked as guessing if it has a status of 'CLUE_GIVING'
        if value == self.STATUS_GUESSING and self.status != self.STATUS_CLUE_GIVING:
            raise Exception('Invalid status change: Game must be in status CLUE_GIVING to change to GUESSING')

        self._status = value
        return self.save()


    def __init__(self):
        self._status = self.STATUS_NEW


    @staticmethod
    def create(player: Player, display_name: str = None) -> 'Game':
        game = Game()
        game.code = game.__generate_game_code()
        game.save()
        game.add_player(player, display_name, True)
        return game

    def __generate_game_code(self):
        code = str(uuid4())[:6]
        # Check if code already exists,
        # we only care if it collides with a game that doesn't have status 'FINISHED'
        game = Game.query.filter(Game.code == code, Game.status != self.STATUS_FINISHED).first()
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
            query.filter(Game.status != Game.STATUS_FINISHED)
        if status:
            query.filter(Game.status == status)
        return query.first()
