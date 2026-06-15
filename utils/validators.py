VALID_TRAVEL_TYPES = ["Budget", "Luxury", "Adventure", "Family"]
VALID_SORT_FIELDS = ["price", "rating", "destination", "platform", "travel_type", "created_at"]
VALID_ORDERS = ["asc", "desc"]

#------------Part 1: Validation Functions------------#
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


#------------Part 2: Validation Functions------------#

def validate_search_params(args):
    """
    Validate query params for GET /deals/search
    Returns (is_valid: bool, errors: dict)
    """
    errors = {}
 
    destination = args.get("destination")
    platform = args.get("platform")
    travel_type = args.get("travel_type")
 
    # Edge case: empty search -> at least one param must be provided & non-empty
    if not any([
        destination and destination.strip(),
        platform and platform.strip(),
        travel_type and travel_type.strip(),
    ]):
        errors["query"] = "Provide at least one search parameter: destination, platform or travel_type"
 
    # Edge case: unknown travel type
    if travel_type and travel_type not in VALID_TRAVEL_TYPES:
        errors["travel_type"] = f"travel_type must be one of {VALID_TRAVEL_TYPES}"
 
    return (len(errors) == 0), errors
 
 
def validate_filter_params(args):
    """
    Validate query params for GET /deals/filter
    Returns (is_valid: bool, errors: dict, min_price: float|None, max_price: float|None)
    """
    errors = {}
    min_price_raw = args.get("min_price")
    max_price_raw = args.get("max_price")
 
    if min_price_raw is None and max_price_raw is None:
        errors["query"] = "Provide at least one of min_price or max_price"
        return False, errors, None, None
 
    min_price = None
    max_price = None
 
    if min_price_raw is not None:
        try:
            min_price = float(min_price_raw)
            if min_price < 0:
                errors["min_price"] = "min_price cannot be negative"
        except ValueError:
            errors["min_price"] = "min_price must be a number"
 
    if max_price_raw is not None:
        try:
            max_price = float(max_price_raw)
            if max_price < 0:
                errors["max_price"] = "max_price cannot be negative"
        except ValueError:
            errors["max_price"] = "max_price must be a number"
 
    if (
        min_price is not None
        and max_price is not None
        and "min_price" not in errors
        and "max_price" not in errors
        and max_price < min_price
    ):
        errors["max_price"] = "max_price cannot be smaller than min_price"
 
    return (len(errors) == 0), errors, min_price, max_price
 
 
def validate_sort_params(args):
    """
    Validate query params for GET /deals/sort
    Returns (is_valid: bool, errors: dict, sort_by: str|None, order: str)
    """
    errors = {}
    sort_by = args.get("sort_by")
    order = args.get("order", "asc")
 
    if order:
        order = order.lower()
 
    if not sort_by:
        errors["sort_by"] = "sort_by is required"
    elif sort_by not in VALID_SORT_FIELDS:
        errors["sort_by"] = f"sort_by must be one of {VALID_SORT_FIELDS}"
 
    if order not in VALID_ORDERS:
        errors["order"] = f"order must be one of {VALID_ORDERS}"
 
    return (len(errors) == 0), errors, sort_by, order
 
