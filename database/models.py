from database.db import db


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    platform = db.Column(db.String)
    rating = db.Column(db.Float, nullable=False)
    travel_type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "destination": self.destination,
            "price": self.price,
            "platform": self.platform,
            "rating": self.rating,
            "travel_type": self.travel_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RecentView(db.Model):
    """Tracks every time a single deal is viewed via GET /deals/<id>."""
    __tablename__ = "recent_views"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deal_id = db.Column(db.Integer, db.ForeignKey("deals.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, server_default=db.func.now())