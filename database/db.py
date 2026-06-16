from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize SQLAlchemy with the Flask app and create tables."""
    db.init_app(app)

    with app.app_context():
        from database.models import Deal, RecentView, SearchLog, ApiRequestLog  # noqa: F401
        db.create_all()