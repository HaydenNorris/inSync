from app import db

game_player = db.Table(
    'game_player',
    db.Column('game_id', db.Integer, db.ForeignKey('game.id')),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'))
)
