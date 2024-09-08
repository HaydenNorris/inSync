from random import Random
from app import db
from app.models import BaseModel
from app.models.Player import Player
from app.models.Scale import Scale
from sqlalchemy.ext.hybrid import hybrid_property


class Clue(BaseModel):
    STATUS_OPEN = 'OPEN'
    STATUS_CLOSED = 'CLOSED'

    MAX_SCORE = 3
    MID_SCORE = 2
    MIN_SCORE = 1

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    scale_id = db.Column(db.Integer, db.ForeignKey('scale.id'), nullable=False)
    prompt = db.Column(db.String(120), nullable=True)
    _value = db.Column('value', db.Integer, nullable=False)
    _max_value = db.Column('max_value', db.Integer, nullable=False)
    guess_value = db.Column(db.Integer, nullable=True)
    _status = db.Column('status', db.String(80), nullable=False, default='NEW')
    _score = db.Column('score', db.Integer, nullable=False, default=0)

    game = db.relationship('Game', back_populates='clues', primaryjoin="Clue.game_id==Game.id")
    scale = db.relationship('Scale')


    @hybrid_property
    def max_value(self):
        return self._max_value

    @hybrid_property
    def score(self):
        return self._score

    @hybrid_property
    def value(self):
        return self._value

    @hybrid_property
    def status(self):
        return self._status

    def __init__(self, game_id:int, player_id:int, scale_id:int, max_value:int=10):
        self.game_id = game_id
        self.player_id = player_id
        self.scale_id = scale_id
        self._max_value = max_value # only set on creation
        self._value = Random().randint(1, max_value) # only set on creation
        self.guess_value = None
        self._status = self.STATUS_OPEN
        self._score = 0

    @staticmethod
    def create(game:'Game', player:'Player', scale: 'Scale') -> 'Clue':
        clue = Clue(game.id, player.id, scale.id)
        clue.save()
        return clue

    def set_prompt(self, prompt:str) -> 'Clue':
        self.prompt = prompt
        return self.save()

    def set_guess(self, guess:int) -> 'Clue':
        self.guess_value = guess
        return self.save()

    def refresh(self) -> 'Clue':
        self._value = Random().randint(1, self._max_value)
        self.prompt = None
        player_clues = Clue.query.filter_by(game_id=self.game_id, player_id=self.player_id).all()
        player_scale_ids = [c.scale_id for c in player_clues]
        scale = Scale.get_random_scale(player_scale_ids)
        self.scale_id = scale.id
        return self.save()

    def close_and_score(self) -> 'Clue':
        self._status = self.STATUS_CLOSED
        self._score = self.__calculate_score()
        return self.save()


    def __calculate_score(self) -> int:
        guess = self.guess_value
        actual = self.value
        diff = abs(guess - actual)
        match diff:
            case 0:
                return self.MAX_SCORE
            case 1:
                return self.MID_SCORE
            case 2:
                return self.MIN_SCORE
            case _:
                return 0