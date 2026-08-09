from flask import Blueprint, jsonify

from utils.decorators import role_required


admin_bp = Blueprint(
    "admin",
    __name__
)


@admin_bp.route(
    "/dashboard",
    methods=["GET"]
)
@role_required("admin")
def dashboard():

    return jsonify({
        "status": "success",
        "message": "Welcome to Admin Dashboard",
        "role": "admin"
    })
