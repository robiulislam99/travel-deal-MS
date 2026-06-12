# Allowed travel_type values as per assignment requirements
VALID_TRAVEL_TYPES = ["Budget", "Luxury", "Adventure", "Family"]


def validate_deal_data(data):
    """
    Validate incoming deal data.
    Returns (is_valid: bool, errors: dict)
    """
    errors = {}

    if data is None:
        return False, {"body": "Request body must be valid JSON"}

    # destination must not be empty
    destination = data.get("destination")
    if destination is None or str(destination).strip() == "":
        errors["destination"] = "destination cannot be empty"

    # price must be a positive number
    price = data.get("price")
    if price is None:
        errors["price"] = "price is required"
    else:
        try:
            price_val = float(price)
            if price_val <= 0:
                errors["price"] = "price must be positive"
        except (ValueError, TypeError):
            errors["price"] = "price must be a number"

    # rating must be between 1 and 5
    rating = data.get("rating")
    if rating is None:
        errors["rating"] = "rating is required"
    else:
        try:
            rating_val = float(rating)
            if rating_val < 1 or rating_val > 5:
                errors["rating"] = "rating must be between 1 and 5"
        except (ValueError, TypeError):
            errors["rating"] = "rating must be a number"

    # travel_type must be one of the allowed values
    travel_type = data.get("travel_type")
    if travel_type is None or str(travel_type).strip() == "":
        errors["travel_type"] = "travel_type is required"
    elif travel_type not in VALID_TRAVEL_TYPES:
        errors["travel_type"] = f"travel_type must be one of {VALID_TRAVEL_TYPES}"

    # platform is optional but cannot be empty string if provided
    platform = data.get("platform")
    if platform is not None and str(platform).strip() == "":
        errors["platform"] = "platform cannot be empty if provided"

    return (len(errors) == 0), errors


def validate_deal_id(deal_id):
    """Ensure the deal_id path param is a positive integer."""
    try:
        deal_id_int = int(deal_id)
        if deal_id_int <= 0:
            return False, None
        return True, deal_id_int
    except (ValueError, TypeError):
        return False, None