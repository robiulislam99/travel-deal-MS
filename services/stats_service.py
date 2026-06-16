from database.db import db
from database.models import ApiRequestLog, SearchLog, RecentView, Deal


# -------------------- API Request Tracking --------------------

def log_api_request(endpoint, method, status_code):
    """Persist a single API request record. Used by the track_api_usage decorator."""
    log = ApiRequestLog(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        is_success=200 <= status_code < 400,
    )
    db.session.add(log)
    db.session.commit()


# -------------------- Search Tracking --------------------

def log_search(destination):
    """Persist a search term for 'most searched destination' statistics."""
    if not destination:
        return
    log = SearchLog(destination=destination.strip().lower())
    db.session.add(log)
    db.session.commit()


# -------------------- Statistics Aggregation --------------------

def get_most_searched_destination():
    """Return the destination searched most often, or None if no searches logged."""
    result = (
        db.session.query(
            SearchLog.destination,
            db.func.count(SearchLog.id).label("search_count"),
        )
        .filter(SearchLog.destination.isnot(None))
        .group_by(SearchLog.destination)
        .order_by(db.desc("search_count"))
        .first()
    )
    if result is None:
        return None
    return {"destination": result[0], "search_count": result[1]}


def get_most_viewed_deal():
    """Return the single most-viewed deal, or None if no views logged."""
    result = (
        db.session.query(Deal, db.func.count(RecentView.id).label("view_count"))
        .join(RecentView, Deal.id == RecentView.deal_id)
        .group_by(Deal.id)
        .order_by(db.desc("view_count"))
        .first()
    )
    if result is None:
        return None
    deal, view_count = result
    deal_dict = deal.to_dict()
    deal_dict["view_count"] = view_count
    return deal_dict


def get_api_usage_stats():
    """
    Aggregate overall API usage statistics:
      - total requests
      - successful requests
      - failed requests
      - most searched destination
      - most viewed deal
    """
    total_requests = db.session.query(db.func.count(ApiRequestLog.id)).scalar() or 0
    successful_requests = (
        db.session.query(db.func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.is_success.is_(True))
        .scalar()
        or 0
    )
    failed_requests = total_requests - successful_requests

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "most_searched_destination": get_most_searched_destination(),
        "most_viewed_deal": get_most_viewed_deal(),
    }