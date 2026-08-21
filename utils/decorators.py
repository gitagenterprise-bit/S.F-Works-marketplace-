from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)

from extensions import db
from models.user import User


# =========================================================
# ROLE REQUIRED
# =========================================================

def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            # -------------------------------------------------
            # JWT CLAIMS
            # -------------------------------------------------

            claims = get_jwt()

            role = claims.get("role")


            # -------------------------------------------------
            # ROLE CHECK
            # -------------------------------------------------

            if role not in allowed_roles:

                return jsonify({
                    "status": "error",
                    "message": "You do not have permission"
                }), 403


            # -------------------------------------------------
            # CURRENT USER
            # -------------------------------------------------

            user_id = get_jwt_identity()

            try:

                user_id = int(user_id)

            except (TypeError, ValueError):

                return jsonify({
                    "status": "error",
                    "message": "Invalid user identity"
                }), 401


            user = db.session.get(
                User,
                user_id
            )


            # -------------------------------------------------
            # USER NOT FOUND
            # -------------------------------------------------

            if not user:

                return jsonify({
                    "status": "error",
                    "message": "User not found"
                }), 404


            # -------------------------------------------------
            # ACTIVE ACCOUNT CHECK
            # -------------------------------------------------

            if not user.is_active:

                return jsonify({
                    "status": "error",
                    "message": "Account is disabled"
                }), 403


            # -------------------------------------------------
            # EXECUTE ROUTE
            # -------------------------------------------------

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator


# =========================================================
# ADMIN REQUIRED
# =========================================================

def admin_required(function):

    @wraps(function)
    @jwt_required()
    def wrapper(*args, **kwargs):

        # -------------------------------------------------
        # JWT CLAIMS
        # -------------------------------------------------

        claims = get_jwt()

        role = claims.get("role")


        # -------------------------------------------------
        # ADMIN ROLE CHECK
        # -------------------------------------------------

        if role != "admin":

            return jsonify({
                "status": "error",
                "message": "Administrator access required"
            }), 403


        # -------------------------------------------------
        # CURRENT USER
        # -------------------------------------------------

        user_id = get_jwt_identity()

        try:

            user_id = int(user_id)

        except (TypeError, ValueError):

            return jsonify({
                "status": "error",
                "message": "Invalid user identity"
            }), 401


        user = db.session.get(
            User,
            user_id
        )


        # -------------------------------------------------
        # USER NOT FOUND
        # -------------------------------------------------

        if not user:

            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404


        # -------------------------------------------------
        # ACTIVE ACCOUNT CHECK
        # -------------------------------------------------

        if not user.is_active:

            return jsonify({
                "status": "error",
                "message": "Account is disabled"
            }), 403


        # -------------------------------------------------
        # EXECUTE ADMIN ROUTE
        # -------------------------------------------------

        return function(
            *args,
            **kwargs
        )

    return wrapper
