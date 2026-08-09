from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)

from extensions import db
from models.user import User


def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            role = claims.get("role")

            if role not in allowed_roles:

                return jsonify({
                    "status": "error",
                    "message": "You do not have permission"
                }), 403

            user_id = get_jwt_identity()

            user = db.session.get(
                User,
                int(user_id)
            )

            if not user:

                return jsonify({
                    "status": "error",
                    "message": "User not found"
                }), 404

            if not user.is_active:

                return jsonify({
                    "status": "error",
                    "message": "Account is disabled"
                }), 403

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator
