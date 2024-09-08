from app import db
from app.models import BaseModel


class Scale(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    low = db.Column(db.String(80), nullable=False)
    high = db.Column(db.String(80), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)

    @staticmethod
    def get_random_scale(exclude=None) -> 'Scale':
        if exclude is None:
            exclude = []
        return (Scale.query
                .filter(Scale.id.notin_(exclude))
                .order_by(db.func.random()).first())