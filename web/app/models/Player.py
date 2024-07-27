from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    uuid = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    games = db.relationship('Game', secondary='player_game', backref='players')
    def __repr__(self):
        return f"Player('{self.name}', '{self.uuid}', '{self.status}')"