from flask import Blueprint, request
from services import deal_service
from utils.validators import validate_deal_data, validate_deal_id
from utils.responses import success_response, error_response

deals_bp = Blueprint("deals", __name__)


@deals_bp.route("/deals", methods=["POST"])
def add_deal():
    """Add a new travel deal after validation."""
    data = request.get_json(silent=True)

    is_valid, errors = validate_deal_data(data)
    if not is_valid:
        return error_response(message="Validation failed", errors=errors, status_code=422)

    try:
        new_deal = deal_service.create_deal(data)
        return success_response(data=new_deal, message="Deal created successfully", status_code=201)
    except Exception as e:
        return error_response(message="Failed to create deal", errors=str(e), status_code=500)


@deals_bp.route("/deals", methods=["GET"])
def list_deals():
    """Get all travel deals."""
    try:
        deals = deal_service.get_all_deals()
        return success_response(data=deals, message="Deals retrieved successfully", status_code=200)
    except Exception as e:
        return error_response(message="Failed to retrieve deals", errors=str(e), status_code=500)


@deals_bp.route("/deals/<deal_id>", methods=["GET"])
def get_deal(deal_id):
    """Get a single travel deal by id."""
    is_valid, parsed_id = validate_deal_id(deal_id)
    if not is_valid:
        return error_response(message="Invalid deal id. Must be a positive integer.", status_code=400)

    try:
        deal = deal_service.get_deal_by_id(parsed_id)
        if deal is None:
            return error_response(message=f"Deal with id {parsed_id} not found", status_code=404)
        return success_response(data=deal, message="Deal retrieved successfully", status_code=200)
    except Exception as e:
        return error_response(message="Failed to retrieve deal", errors=str(e), status_code=500)