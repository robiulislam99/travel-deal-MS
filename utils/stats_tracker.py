from functools import wraps
from flask import request


def track_api_usage(func):
    """
    Decorator that records every request to the wrapped route into ApiRequestLog,
    based on the actual HTTP status code returned by the view function.
    Keeps statistics tracking out of route bodies entirely (reusable, DRY).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from services import stats_service

        response = func(*args, **kwargs)

        if isinstance(response, tuple):
            status_code = response[1] if len(response) > 1 else 200
        else:
            status_code = getattr(response, "status_code", 200)

        try:
            stats_service.log_api_request(
                endpoint=request.path,
                method=request.method,
                status_code=status_code,
            )
        except Exception:
            pass

        return response

    return wrapper