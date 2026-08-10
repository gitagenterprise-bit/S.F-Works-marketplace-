from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from extensions import db
from models.user import User


worker_pages_bp = Blueprint(
    "worker_pages",
    __name__
)


# =========================================================
# WORKER DASHBOARD
# =========================================================

@worker_pages_bp.route(
    "/worker/dashboard",
    methods=["GET"]
)
@jwt_required()
def worker_dashboard_page():

    identity = get_jwt_identity()

    if not identity:
        return redirect(
            url_for("auth.login")
        )

    user_id = int(identity)

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return redirect(
            url_for("auth.login")
        )

    if user.role != "worker":
        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "worker/dashboard.html",
        user=user,
        worker=user.worker_profile
    )


# =========================================================
# WORKER PROFILE
# =========================================================

@worker_pages_bp.route(
    "/worker/profile",
    methods=["GET"]
)
@jwt_required()
def worker_profile_page():

    # ---------------------------------------------
    # JWT IDENTITY
    # ---------------------------------------------

    identity = get_jwt_identity()

    if not identity:
        return redirect(
            url_for("auth.login")
        )


    # ---------------------------------------------
    # USER ID
    # ---------------------------------------------

    try:

        user_id = int(identity)

    except (
        TypeError,
        ValueError
    ):

        return redirect(
            url_for("auth.login")
        )


    # ---------------------------------------------
    # LOAD USER
    # ---------------------------------------------

    user = db.session.get(
        User,
        user_id
    )


    if not user:

        return redirect(
            url_for("auth.login")
        )


    # ---------------------------------------------
    # ROLE CHECK
    # ---------------------------------------------

    if user.role != "worker":

        return redirect(
            url_for("auth.login")
        )


    # ---------------------------------------------
    # WORKER PROFILE
    # ---------------------------------------------

    worker = user.worker_profile


    if not worker:

        return redirect(
            url_for(
                "worker_pages.worker_dashboard_page"
            )
        )


    # ---------------------------------------------
    # RENDER
    # ---------------------------------------------

    return render_template(
        "worker/profile.html",
        user=user,
        worker=worker
    )


@worker_pages_bp.route(
    "/worker/dashboard"
)
def worker_dashboard_page():

    return render_template(
        "worker/dashboard.html"
    )


@worker_pages_bp.route(
    "/worker/jobs"
)
def worker_jobs_page():

    return render_template(
        "worker/jobs.html"
    )



@worker_pages_bp.route(
    "/worker/applications"
)
def worker_applications_page():

    return render_template(
        "worker/applications.html"
    )


@worker_pages_bp.route(
    "/worker/settings"
)
def worker_settings_page():

    return render_template(
        "worker/settings.html"
    )
