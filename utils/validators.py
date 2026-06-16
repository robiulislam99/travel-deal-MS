VALID_TRAVEL_TYPES = ["Budget", "Luxury", "Adventure", "Family"]
VALID_SORT_FIELDS = ["price", "rating", "destination", "platform", "travel_type", "created_at"]
VALID_ORDERS = ["asc", "desc"]


# -------------------- Field-level validators (reusable building blocks) --------------------

def _validate_destination(value):
    if value is None or str(value).strip() == "":
        return "destination cannot be empty"
    return None


def _validate_price(value):
    if value is None:
        return "price is required"
    try:
        price_val = float(value)
        if price_val <= 0:
            return "price must be positive"
    except (ValueError, TypeError):
        return "price must be a number"
    return None


def _validate_rating(value):
    if value is None:
        return "rating is required"
    try:
        rating_val = float(value)
        if rating_val < 1 or rating_val > 5:
            return "rating must be between 1 and 5"
    except (ValueError, TypeError):
        return "rating must be a number"
    return None


def _validate_travel_type(value):
    if value is None or str(value).strip() == "":
        return "travel_type is required"
    if value not in VALID_TRAVEL_TYPES:
        return f"travel_type must be one of {VALID_TRAVEL_TYPES}"
    return None


def _validate_platform(value):
    if value is not None and str(value).strip() == "":
        return "platform cannot be empty if provided"
    return None


# Maps each deal field to its validator function.
# Reused identically by both create (all required) and update (only provided fields checked).
FIELD_VALIDATORS = {
    "destination": _validate_destination,
    "price": _validate_price,
    "rating": _validate_rating,
    "travel_type": _validate_travel_type,
    "platform": _validate_platform,
}


# -------------------- Part 01: Create Validation --------------------

def validate_deal_data(data):
    """
    Validate incoming deal data for creating a deal.
    All fields are required. Returns (is_valid: bool, errors: dict)
    """
    if data is None:
        return False, {"body": "Request body must be valid JSON"}

    errors = {}
    for field, validator in FIELD_VALIDATORS.items():
        error = validator(data.get(field))
        if error:
            errors[field] = error

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


# -------------------- Part 03: Update Validation (reuses same field validators) --------------------

def validate_deal_update_data(data):
    """
    Validate incoming deal data for updating a deal.
    Only the fields present in the request body are validated, using the
    SAME field-level rules as create (FIELD_VALIDATORS), so update validation
    always stays in sync with create validation.
    Returns (is_valid: bool, errors: dict)
    """
    if data is None:
        return False, {"body": "Request body must be valid JSON"}

    if len(data) == 0:
        return False, {"body": "At least one field must be provided to update"}

    errors = {}
    for field, value in data.items():
        validator = FIELD_VALIDATORS.get(field)
        if validator is None:
            errors[field] = f"'{field}' is not a recognized or updatable field"
            continue
        error = validator(value)
        if error:
            errors[field] = error

    return (len(errors) == 0), errors


# -------------------- Part 02: Search/Filter/Sort Validators --------------------

def validate_search_params(args):
    """
    Validate query params for GET /deals/search
    Returns (is_valid: bool, errors: dict)
    """
    errors = {}

    destination = args.get("destination")
    platform = args.get("platform")
    travel_type = args.get("travel_type")

    if not any([
        destination and destination.strip(),
        platform and platform.strip(),
        travel_type and travel_type.strip(),
    ]):
        errors["query"] = "Provide at least one search parameter: destination, platform or travel_type"

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