from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt


admin_pages_bp = Blueprint(
    "admin_pages",
    __name__
)


@admin_pages_bp.route(
    "/admin/dashboard",
    methods=["GET"]
)
@jwt_required()
def admin_dashboard():

    claims = get_jwt()

    role = claims.get("role")

    if role != "admin":
        return "Access denied", 403

    return render_template(
        "admin/dashboard.html"
    )
