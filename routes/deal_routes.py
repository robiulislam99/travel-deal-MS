from flask import Blueprint, request
from services import deal_service, stats_service
from utils.validators import (
    validate_deal_data,
    validate_deal_id,
    validate_deal_update_data,
    validate_search_params,
    validate_filter_params,
    validate_sort_params,
)
from utils.responses import success_response, error_response
from utils.logger import logger
from utils.stats_tracker import track_api_usage

deals_bp = Blueprint("deals", __name__)


# -------------------- Part 01: Core CRUD --------------------

@deals_bp.route("/deals", methods=["POST"])
@track_api_usage
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
@track_api_usage
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
@track_api_usage
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


# -------------------- Part 03: Update --------------------

@deals_bp.route("/deals/<deal_id>", methods=["PUT"])
@track_api_usage
def update_deal(deal_id):
    """Update an existing travel deal (partial update), validated with the same rules as create."""
    is_valid_id, parsed_id = validate_deal_id(deal_id)
    if not is_valid_id:
        logger.warning(f"Invalid deal id on update: {deal_id}")
        return error_response(message="Invalid deal id. Must be a positive integer.", status_code=400)

    data = request.get_json(silent=True)
    is_valid, errors = validate_deal_update_data(data)
    if not is_valid:
        logger.warning(f"Invalid update request for id={parsed_id}: {errors}")
        return error_response(message="Validation failed", errors=errors, status_code=422)

    try:
        updated_deal = deal_service.update_deal(parsed_id, data)
        if updated_deal is None:
            logger.warning(f"Update failed - deal not found: id={parsed_id}")
            return error_response(message=f"Deal with id {parsed_id} not found", status_code=404)

        logger.info(f"Deal updated successfully: id={parsed_id}")
        return success_response(data=updated_deal, message="Deal updated successfully", status_code=200)
    except Exception as e:
        logger.error(f"Failed to update deal id={deal_id}: {e}")
        return error_response(message="Failed to update deal", errors=str(e), status_code=500)


# -------------------- Part 03: Delete --------------------

@deals_bp.route("/deals/<deal_id>", methods=["DELETE"])
@track_api_usage
def delete_deal(deal_id):
    """Delete a travel deal by id."""
    is_valid_id, parsed_id = validate_deal_id(deal_id)
    if not is_valid_id:
        logger.warning(f"Invalid deal id on delete: {deal_id}")
        return error_response(message="Invalid deal id. Must be a positive integer.", status_code=400)

    try:
        deleted = deal_service.delete_deal(parsed_id)
        if not deleted:
            logger.warning(f"Delete failed - deal not found: id={parsed_id}")
            return error_response(message=f"Deal with id {parsed_id} not found", status_code=404)

        logger.info(f"Deal deleted successfully: id={parsed_id}")
        return success_response(message="Deal deleted successfully", status_code=200)
    except Exception as e:
        logger.error(f"Failed to delete deal id={deal_id}: {e}")
        return error_response(message="Failed to delete deal", errors=str(e), status_code=500)


# -------------------- Part 02: Search --------------------

@deals_bp.route("/deals/search", methods=["GET"])
@track_api_usage
def search_deals_route():
    """Search deals by destination, platform and/or travel_type (partial, case-insensitive)."""
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
        stats_service.log_search(filters.get("destination"))
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
@track_api_usage
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
@track_api_usage
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
@track_api_usage
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


# -------------------- Part 03: Most Viewed Deals --------------------

@deals_bp.route("/deals/popular", methods=["GET"])
@track_api_usage
def popular_deals_route():
    """Return deals ranked by total view count (most popular first)."""
    try:
        deals = deal_service.get_most_viewed_deals(limit=5)
        logger.info(f"Most viewed deals retrieved, count={len(deals)}")

        if not deals:
            return success_response(
                data=[], message="No deals have been viewed yet", status_code=200
            )

        return success_response(data=deals, message="Most viewed deals retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Failed to retrieve most viewed deals: {e}")
        return error_response(message="Failed to retrieve most viewed deals", errors=str(e), status_code=500)