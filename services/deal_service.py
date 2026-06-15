from database.db import db
from database.models import Deal, RecentView


# -------------------- Part 01: Core CRUD --------------------

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


# -------------------- Part 02: Reusable Query Builder --------------------

def build_deal_query(filters=None):
    """
    Build a single reusable SQLAlchemy query for the Deal model.

    Supported filter keys (all optional):
      - destination  : partial, case-insensitive match
      - platform     : partial, case-insensitive match
      - travel_type  : exact match
      - min_price    : price >= min_price
      - max_price    : price <= max_price
      - sort_by      : column name to order by
      - order        : 'asc' or 'desc'

    This single function is shared by search, filter and sort endpoints
    to avoid duplicate filtering logic.
    """
    filters = filters or {}
    query = Deal.query

    if filters.get("destination"):
        query = query.filter(Deal.destination.ilike(f"%{filters['destination']}%"))

    if filters.get("platform"):
        query = query.filter(Deal.platform.ilike(f"%{filters['platform']}%"))

    if filters.get("travel_type"):
        query = query.filter(Deal.travel_type == filters["travel_type"])

    if filters.get("min_price") is not None:
        query = query.filter(Deal.price >= filters["min_price"])

    if filters.get("max_price") is not None:
        query = query.filter(Deal.price <= filters["max_price"])

    sort_by = filters.get("sort_by")
    if sort_by:
        column = getattr(Deal, sort_by)
        column = column.desc() if filters.get("order") == "desc" else column.asc()
        query = query.order_by(column)

    return query


# -------------------- Part 02: Search / Filter / Sort --------------------

def search_deals(filters):
    """Search deals by destination/platform/travel_type (partial, case-insensitive)."""
    query = build_deal_query(filters)
    return [deal.to_dict() for deal in query.all()]


def filter_deals_by_price(min_price, max_price):
    """Filter deals by price range."""
    filters = {"min_price": min_price, "max_price": max_price}
    query = build_deal_query(filters)
    return [deal.to_dict() for deal in query.all()]


def sort_deals(sort_by, order):
    """Return all deals sorted by the given field and order."""
    filters = {"sort_by": sort_by, "order": order}
    query = build_deal_query(filters)
    return [deal.to_dict() for deal in query.all()]


# -------------------- Part 02: Recently Viewed --------------------

def record_deal_view(deal_id):
    """Record that a deal was viewed (called from GET /deals/<id>)."""
    view = RecentView(deal_id=deal_id)
    db.session.add(view)
    db.session.commit()


def get_recently_viewed_deals(limit=5):
    """Return the most recently viewed deals (most recent first, no duplicates)."""
    subquery = (
        db.session.query(
            RecentView.deal_id,
            db.func.max(RecentView.viewed_at).label("last_viewed"),
        )
        .group_by(RecentView.deal_id)
        .order_by(db.desc("last_viewed"))
        .limit(limit)
        .subquery()
    )

    results = (
        db.session.query(Deal, subquery.c.last_viewed)
        .join(subquery, Deal.id == subquery.c.deal_id)
        .order_by(subquery.c.last_viewed.desc())
        .all()
    )

    deals = []
    for deal, last_viewed in results:
        deal_dict = deal.to_dict()
        deal_dict["last_viewed_at"] = last_viewed.isoformat() if last_viewed else None
        deals.append(deal_dict)

    return deals