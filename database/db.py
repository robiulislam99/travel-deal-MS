import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "travel_deals.db")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"


def init_db(app):
    """Configure SQLAlchemy with the Flask app and create tables."""
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        from services.deal_service import Deal, RecentView  # noqa: F401
        db.create_all()