import os


class Config:
    """Application configuration."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'travel_deals.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False