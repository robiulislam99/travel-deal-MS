from database.db import get_connection


def create_deal(data):
    """Insert a new travel deal into the database and return it."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO deals (destination, price, platform, rating, travel_type)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                data.get("destination").strip(),
                data.get("price"),
                data.get("platform"),
                data.get("rating"),
                data.get("travel_type"),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        return get_deal_by_id(new_id)
    finally:
        cur.close()
        conn.close()


def get_all_deals(filters=None):
    """Return all travel deals, optionally filtered by travel_type or platform."""
    filters = filters or {}
    query = "SELECT id, destination, price, platform, rating, travel_type, created_at FROM deals"
    conditions = []
    params = []

    if filters.get("travel_type"):
        conditions.append("travel_type = ?")
        params.append(filters["travel_type"])

    if filters.get("platform"):
        conditions.append("platform = ?")
        params.append(filters["platform"])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id ASC;"

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        cur.close()
        conn.close()


def get_deal_by_id(deal_id):
    """Return a single deal by id, or None if not found."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, destination, price, platform, rating, travel_type, created_at "
            "FROM deals WHERE id = ?;",
            (deal_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()