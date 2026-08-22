from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request
)

from models.user import User


def permission_required(*allowed_roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            identity = get_jwt_identity()

            try:
                user_id = int(identity)
            except (
                TypeError,
                ValueError
            ):
                return jsonify({
                    "success": False,
                    "message": "Invalid authentication identity."
                }), 401

            user = User.query.get(user_id)

            if not user:

                return jsonify({
                    "success": False,
                    "message": "User not found."
                }), 401

            if not user.is_active:

                return jsonify({
                    "success": False,
                    "message": "Account is inactive."
                }), 403

            if user.role not in allowed_roles:

                return jsonify({
                    "success": False,
                    "message": "You do not have permission."
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(func):

    return permission_required("admin")(func)


def agent_or_admin_required(func):

    return permission_required(
        "agent",
        "admin"
    )(func)
