from flask import Flask
from config import Config
from utils.logger import logger  # noqa: F401 - configures logging on import
from routes.deal_routes import deals_bp
from database.db import init_db
from utils.responses import error_response


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)


    # Initialize SQLAlchemy + create tables
    init_db(app)

    # Register the deals blueprint (routes layer)
    app.register_blueprint(deals_bp)

    # Global error handlers for consistent JSON error responses
    @app.errorhandler(404)
    def not_found(e):
        return error_response(message="Resource not found", status_code=404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response(message="Method not allowed", status_code=405)

    @app.errorhandler(500)
    def internal_error(e):
        return error_response(message="Internal server error", status_code=500)

    @app.route("/", methods=["GET"])
    def health_check():
        return {"status": "ok", "message": "Travel Deal Management System API"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)