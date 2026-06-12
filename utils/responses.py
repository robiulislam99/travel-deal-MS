from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """Build a consistent success JSON response."""
    payload = {"status": "success", "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error_response(message="Error", errors=None, status_code=400):
    """Build a consistent error JSON response."""
    payload = {"status": "error", "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code