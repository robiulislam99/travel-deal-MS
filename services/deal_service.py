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


def create_deal(data):
    """Insert a new travel deal into the database and return it."""
    deal = Deal(
        destination=data.get("destination").strip(),
        price=data.get("price"),
        platform=data.get("platform"),
        rating=data.get("rating"),
        travel_type=data.get("travel_type"),
    )
    db.session.add(deal)
    db.session.commit()
    return deal.to_dict()


def get_all_deals():
    """Return all travel deals."""
    deals = Deal.query.order_by(Deal.id.asc()).all()
    return [deal.to_dict() for deal in deals]


def get_deal_by_id(deal_id):
    """Return a single deal by id, or None if not found."""
    deal = Deal.query.get(deal_id)
    return deal.to_dict() if deal else None