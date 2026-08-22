from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt
)

from utils.permissions import (
    get_current_user
)


def role_required(*allowed_roles):

    allowed_roles = set(
        allowed_roles
    )

    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            user = get_current_user()

            if not user:

                return jsonify({
                    "status": "error",
                    "message": "Authentication required."
                }), 401

            claims = get_jwt()

            token_role = claims.get(
                "role"
            )

            # ------------------------------------------------
            # JWT role must match database role.
            # Prevents stale/manipulated privilege.
            # ------------------------------------------------

            if token_role != user.role:

                return jsonify({
                    "status": "error",
                    "message": "Security validation failed."
                }), 401

            if user.role not in allowed_roles:

                return jsonify({
                    "status": "error",
                    "message": "You do not have permission."
                }), 403

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator


def admin_required(function):

    @wraps(function)
    @jwt_required()
    def wrapper(*args, **kwargs):

        user = get_current_user()

        if not user:

            return jsonify({
                "status": "error",
                "message": "Authentication required."
            }), 401

        claims = get_jwt()

        if claims.get("role") != "admin":

            return jsonify({
                "status": "error",
                "message": "Administrator access required."
            }), 403

        if user.role != "admin":

            return jsonify({
                "status": "error",
                "message": "Administrator access required."
            }), 403

        return function(
            *args,
            **kwargs
        )

    return wrapper


def agent_required(function):

    @wraps(function)
    @jwt_required()
    def wrapper(*args, **kwargs):

        user = get_current_user()

        if not user:

            return jsonify({
                "status": "error",
                "message": "Authentication required."
            }), 401

        if user.role != "agent":

            return jsonify({
                "status": "error",
                "message": "Agent access required."
            }), 403

        if not user.agent_profile:

            return jsonify({
                "status": "error",
                "message": "Agent profile not configured."
            }), 403

        if not user.agent_profile.is_active:

            return jsonify({
                "status": "error",
                "message": "Agent account is inactive."
            }), 403

        claims = get_jwt()

        if claims.get("role") != "agent":

            return jsonify({
                "status": "error",
                "message": "Security validation failed."
            }), 401

        return function(
            *args,
            **kwargs
        )

    return wrapper
