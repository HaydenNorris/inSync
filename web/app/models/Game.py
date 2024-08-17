from uuid import uuid4
from app import db
from app.models.GamePlayer import GamePlayer
from app.models import BaseModel, Player
from app.models.Scale import Scale
from sqlalchemy.ext.hybrid import hybrid_property


class Game(BaseModel):
    STATUS_NEW = 'NEW'
    STATUS_CLUE_GIVING = 'CLUE_GIVING'
    STATUS_GUESSING = 'GUESSING'
    STATUS_FINISHED = 'FINISHED'

    id = db.Column(db.Integer, primary_key=True)
    _status = db.Column('status', db.String(80), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    players = db.relationship('Player', secondary='game_player', back_populates='games')
    clues = db.relationship('Clue', back_populates='game')

    @hybrid_property
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
        if not player.in_game(self):
            GamePlayer(game_id=self.id, player_id=player.id, display_name=display_name, host=host).save()
        return self

    def get_clues_for(self, player: Player, clue_num: int) -> 'Clue':
        from app.models.Clue import Clue
        # if self.status != self.STATUS_CLUE_GIVING: TODO: Uncomment this line after the tests
        #     raise Exception('Game is not in the clue giving status')
        if clue_num < 1 or clue_num > 3:
            raise Exception('Clue number must be between 1 and 3')
        play_clues = Clue.query.filter_by(game_id=self.id, player_id=player.id).order_by(Clue.id).all()
        player_scale_ids = [c.scale_id for c in play_clues]

        # if the user has less than the requested number of clues, add more
        while len(play_clues) < clue_num:
            new_clue = self.__add_clue(player, player_scale_ids)
            play_clues.append(new_clue)
            player_scale_ids.append(new_clue.scale_id)

        return play_clues[clue_num - 1]


    def __add_clue(self, player: Player, exclude_scale_ids:list) -> 'Clue':
        from app.models.Clue import Clue
        scale = Scale.get_random_scale(exclude=exclude_scale_ids)
        clue = Clue.create(self, player, scale)
        return clue


