from app import db
from app.models import BaseModel


class GamePlayer(BaseModel):
    __tablename__ = 'game_player'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    host = db.Column(db.Boolean, default=False)

    def __init__(self, game_id, player_id, display_name, host=False):
        self.game_id = game_id
        self.player_id = player_id
        self.display_name = display_name
        self.host = host
