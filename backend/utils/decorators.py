from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps
from flask import jsonify

def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()

            if user["role"] not in allowed_roles:
                return jsonify({"error": "Access denied"}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator