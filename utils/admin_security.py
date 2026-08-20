from functools import wraps

from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt,
    get_jwt_identity
)

from models import User


def admin_required(fn):

    @wraps(fn)
    def decorated(*args, **kwargs):

        try:

            verify_jwt_in_request()

            claims = get_jwt()

            role = str(
                claims.get("role", "")
            ).lower()

            if role != "admin":

                return jsonify({
                    "status": "error",
                    "message": "Admin access required."
                }), 403

            identity = get_jwt_identity()

            user = User.query.get(identity)

            if not user:

                return jsonify({
                    "status": "error",
                    "message": "Admin account not found."
                }), 401

            if not user.is_active:

                return jsonify({
                    "status": "error",
                    "message": "Admin account is inactive."
                }), 403

            if user.role != "admin":

                return jsonify({
                    "status": "error",
                    "message": "Unauthorized administrator."
                }), 403

            return fn(*args, **kwargs)

        except Exception:

            return jsonify({
                "status": "error",
                "message": "Authentication required."
            }), 401

    return decorated
