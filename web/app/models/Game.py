from app import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    uuid = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    players = db.relationship('Player', secondary='player_game', backref='games')
