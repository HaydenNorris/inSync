from random import Random
from app import db
from app.models import BaseModel
from app.models.Player import Player
from app.models.Scale import Scale
from sqlalchemy.ext.hybrid import hybrid_property


class Clue(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    scale_id = db.Column(db.Integer, db.ForeignKey('scale.id'), nullable=False)
    clue = db.Column(db.String(120), nullable=True)
    _value = db.Column('value', db.Integer, nullable=False)
    _max_value = db.Column('max_value', db.Integer, nullable=False)
    guess_value = db.Column(db.Integer, nullable=True)

    game = db.relationship('Game', back_populates='clues')
    scale = db.relationship('Scale')

    @hybrid_property
    def max_value(self):
        return self._max_value

    @hybrid_property
    def value(self):
        return self._value

    def __init__(self, game_id:int, player_id:int, scale_id:int, max_value:int=10):
        self.game_id = game_id
        self.player_id = player_id
        self.scale_id = scale_id
        # only set on creation
        self._max_value = max_value
        # only set on creation
        self._value = Random().randint(1, max_value)
        self.guess_value = None

    @staticmethod
    def create(game:'Game', player:'Player', scale: 'Scale') -> 'Clue':
        clue = Clue(game.id, player.id, scale.id)
        clue.save()
        return clue

    def set_clue(self, clue:str) -> 'Clue':
        self.clue = clue
        return self.save()

    def set_guess(self, guess:int) -> 'Clue':
        self.guess_value = guess
        return self.save()

