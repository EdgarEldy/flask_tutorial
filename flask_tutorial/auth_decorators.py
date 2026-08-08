from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from flask_tutorial.errors import ForbiddenError


def require_permission(resource: str, action: str):
    """Requires a valid JWT whose embedded permissions claim (set at login,
    see AuthService._resolve_permissions) includes "resource:action".

    The claim is a snapshot taken at login, not re-queried per request: a role/permission
    change (or an account being locked) takes effect only once the token expires or is
    blacklisted via logout, not immediately. Deliberate tradeoff given short-lived tokens
    and no refresh-token flow (see README's Authorization rules)."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            permissions = get_jwt().get("permissions", [])
            if f"{resource}:{action}" not in permissions:
                raise ForbiddenError(f"Missing permission: {resource}:{action}")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
