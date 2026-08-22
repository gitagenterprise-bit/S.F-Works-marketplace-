from flask import (
    Blueprint,
    render_template
)

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity
)


# ============================================================
# Customer Web Pages Blueprint
# ============================================================

customer_page_bp = Blueprint(
    "customer_pages",
    __name__,
    url_prefix="/customer"
)


# ============================================================
# CUSTOMER DASHBOARD
# GET /customer/dashboard
# ============================================================

@customer_page_bp.route(
    "/dashboard",
    methods=["GET"]
)
def dashboard():

    # --------------------------------------------------------
    # Page-level authentication
    #
    # JWT cookie থাকলে verify হবে।
    # Authentication না থাকলে login page-এ পাঠানো হবে
    # frontend JavaScript দ্বারা।
    # --------------------------------------------------------

    try:

        verify_jwt_in_request(
            locations=["cookies"]
        )

        user_id = get_jwt_identity()

    except Exception:

        user_id = None

    return render_template(
        "customer/dashboard.html",
        user_id=user_id
    )
