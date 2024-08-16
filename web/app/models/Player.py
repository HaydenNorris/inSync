from app import db
from app.models import BaseModel

class Player(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    games = db.relationship('Game', secondary='game_player', back_populates='players')

    def __repr__(self):
        return f"Player('{self.name}')"