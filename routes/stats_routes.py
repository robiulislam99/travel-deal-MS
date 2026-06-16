from flask import Blueprint
from services import stats_service
from utils.responses import success_response, error_response
from utils.logger import logger
from utils.stats_tracker import track_api_usage

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/stats", methods=["GET"])
@track_api_usage
def get_stats():
    """Return overall API usage statistics."""
    try:
        stats = stats_service.get_api_usage_stats()
        logger.info(f"Stats retrieved: total={stats['total_requests']}")
        return success_response(data=stats, message="Statistics retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {e}")
        return error_response(message="Failed to retrieve statistics", errors=str(e), status_code=500)