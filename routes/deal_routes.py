from flask import Blueprint, request
from services import deal_service
from utils.validators import (
    validate_deal_data,
    validate_deal_id,
    validate_search_params,
    validate_filter_params,
    validate_sort_params,
)
from utils.responses import success_response, error_response
from utils.logger import logger

deals_bp = Blueprint("deals", __name__)


@deals_bp.route("/deals", methods=["POST"])
def add_deal():
    """Add a new travel deal after validation."""
    data = request.get_json(silent=True)

    is_valid, errors = validate_deal_data(data)
    if not is_valid:
        logger.warning(f"Invalid create deal request: {errors}")
        return error_response(message="Validation failed", errors=errors, status_code=422)

    try:
        new_deal = deal_service.create_deal(data)
        logger.info(f"Deal created successfully: id={new_deal['id']}")
        return success_response(data=new_deal, message="Deal created successfully", status_code=201)
    except Exception as e:
        logger.error(f"Failed to create deal: {e}")
        return error_response(message="Failed to create deal", errors=str(e), status_code=500)


@deals_bp.route("/deals", methods=["GET"])
def list_deals():
    """Get all travel deals."""
    try:
        deals = deal_service.get_all_deals()
        logger.info(f"Retrieved all deals, count={len(deals)}")
        return success_response(data=deals, message="Deals retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Failed to retrieve deals: {e}")
        return error_response(message="Failed to retrieve deals", errors=str(e), status_code=500)


@deals_bp.route("/deals/<deal_id>", methods=["GET"])
def get_deal(deal_id):
    """Get a single travel deal by id, and record it as a recently viewed deal."""
    is_valid, parsed_id = validate_deal_id(deal_id)
    if not is_valid:
        logger.warning(f"Invalid deal id requested: {deal_id}")
        return error_response(message="Invalid deal id. Must be a positive integer.", status_code=400)

    try:
        deal = deal_service.get_deal_by_id(parsed_id)
        if deal is None:
            logger.warning(f"Deal not found: id={parsed_id}")
            return error_response(message=f"Deal with id {parsed_id} not found", status_code=404)

        deal_service.record_deal_view(parsed_id)
        logger.info(f"Deal viewed: id={parsed_id}")
        return success_response(data=deal, message="Deal retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Failed to retrieve deal id={deal_id}: {e}")
        return error_response(message="Failed to retrieve deal", errors=str(e), status_code=500)

    
# -------------------- Part 02: Search --------------------

@deals_bp.route("/deals/search", methods=["GET"])
def search_deals_route():
    """
    Search deals by destination, platform and/or travel_type.
    Supports partial, case-insensitive matching.
    """
    args = request.args

    is_valid, errors = validate_search_params(args)
    if not is_valid:
        logger.warning(f"Invalid search request: params={dict(args)}, errors={errors}")
        return error_response(message="Validation failed", errors=errors, status_code=400)

    filters = {
        "destination": args.get("destination"),
        "platform": args.get("platform"),
        "travel_type": args.get("travel_type"),
    }

    try:
        deals = deal_service.search_deals(filters)
        logger.info(f"Search performed: params={dict(args)}, results={len(deals)}")

        if not deals:
            return success_response(
                data=[], message="No deals found matching the search criteria", status_code=200
            )

        return success_response(data=deals, message="Deals retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Search request failed: {e}")
        return error_response(message="Failed to search deals", errors=str(e), status_code=500)


# -------------------- Part 02: Filter by Budget --------------------

@deals_bp.route("/deals/filter", methods=["GET"])
def filter_deals_route():
    """Filter deals by price range using min_price and/or max_price."""
    args = request.args

    is_valid, errors, min_price, max_price = validate_filter_params(args)
    if not is_valid:
        logger.warning(f"Invalid filter request: params={dict(args)}, errors={errors}")
        return error_response(message="Validation failed", errors=errors, status_code=400)

    try:
        deals = deal_service.filter_deals_by_price(min_price, max_price)
        logger.info(
            f"Filter performed: min_price={min_price}, max_price={max_price}, results={len(deals)}"
        )

        if not deals:
            return success_response(
                data=[], message="No deals found within the given price range", status_code=200
            )

        return success_response(data=deals, message="Deals retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Filter request failed: {e}")
        return error_response(message="Failed to filter deals", errors=str(e), status_code=500)


# -------------------- Part 02: Sort --------------------

@deals_bp.route("/deals/sort", methods=["GET"])
def sort_deals_route():
    """Sort deals by a given field (sort_by) and order (asc/desc)."""
    args = request.args

    is_valid, errors, sort_by, order = validate_sort_params(args)
    if not is_valid:
        logger.warning(f"Invalid sort request: params={dict(args)}, errors={errors}")
        return error_response(message="Validation failed", errors=errors, status_code=400)

    try:
        deals = deal_service.sort_deals(sort_by, order)
        logger.info(f"Sort performed: sort_by={sort_by}, order={order}, results={len(deals)}")
        return success_response(data=deals, message="Deals retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Sort request failed: {e}")
        return error_response(message="Failed to sort deals", errors=str(e), status_code=500)


# -------------------- Part 02: Recently Viewed --------------------

@deals_bp.route("/deals/recent", methods=["GET"])
def recent_deals_route():
    """Return the most recently viewed deals."""
    try:
        deals = deal_service.get_recently_viewed_deals(limit=5)
        logger.info(f"Recently viewed deals retrieved, count={len(deals)}")

        if not deals:
            return success_response(
                data=[], message="No deals have been viewed yet", status_code=200
            )

        return success_response(data=deals, message="Recently viewed deals retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Failed to retrieve recently viewed deals: {e}")
        return error_response(message="Failed to retrieve recently viewed deals", errors=str(e), status_code=500)