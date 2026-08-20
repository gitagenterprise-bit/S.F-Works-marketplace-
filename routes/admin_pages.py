from flask import (
    Blueprint,
    render_template
)


admin_pages_bp = Blueprint(
    "admin_pages",
    __name__
)


# =========================================================
# ADMIN LOGIN PAGE
# =========================================================

@admin_pages_bp.get("/admin/login")
def admin_login_page():

    return render_template(
        "admin/login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_pages_bp.get("/admin")
@admin_pages_bp.get("/admin/dashboard")
def admin_dashboard_page():

    return render_template(
        "admin/dashboard.html"
    )
