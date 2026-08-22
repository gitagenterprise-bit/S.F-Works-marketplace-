from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)

from extensions import db

from models.user import User


def _get_current_user():

    identity = get_jwt_identity()

    try:
        user_id = int(identity)

    except (
        TypeError,
        ValueError
    ):

        return None

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return None

    if not user.is_active:
        return None

    return user


# =========================================================
# ROLE REQUIRED
# =========================================================

def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            token_role = claims.get(
                "role"
            )

            if token_role not in allowed_roles:

                return jsonify({
                    "status": "error",
                    "message":
                        "You do not have permission."
                }), 403

            user = _get_current_user()

            if not user:

                return jsonify({
                    "status": "error",
                    "message":
                        "Account is invalid or inactive."
                }), 403

            # IMPORTANT:
            # Never trust JWT role alone.
            if user.role != token_role:

                return jsonify({
                    "status": "error",
                    "message":
                        "Session authorization mismatch."
                }), 401

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

    return role_required(
        "admin"
    )(function)


# =========================================================
# AGENT REQUIRED
# =========================================================

def agent_required(function):

    return role_required(
        "agent"
    )(function)


# =========================================================
# AGENT PERMISSION
# =========================================================

def agent_permission(permission):

    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            if claims.get("role") != "agent":

                return jsonify({
                    "status": "error",
                    "message":
                        "Agent access required."
                }), 403

            user = _get_current_user()

            if not user:

                return jsonify({
                    "status": "error",
                    "message":
                        "Agent account is inactive."
                }), 403

            if user.role != "agent":

                return jsonify({
                    "status": "error",
                    "message":
                        "Invalid agent session."
                }), 401

            agent = user.agent_profile

            if not agent:

                return jsonify({
                    "status": "error",
                    "message":
                        "Agent profile not found."
                }), 403

            if not agent.has_permission(
                permission
            ):

                return jsonify({
                    "status": "error",
                    "message":
                        "This agent does not have "
                        "the required permission."
                }), 403

            if not agent.is_verified:

                return jsonify({
                    "status": "error",
                    "message":
                        "Agent verification required."
                }), 403

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator
