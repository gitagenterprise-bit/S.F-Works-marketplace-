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


# =========================================================
# WORKER PAGES BLUEPRINT
# =========================================================

worker_pages_bp = Blueprint(
    "worker_pages",
    __name__
)


# =========================================================
# CURRENT WORKER HELPER
# =========================================================

def get_current_worker():

    identity = get_jwt_identity()

    if identity is None:
        return None, None


    try:

        user_id = int(identity)

    except (
        TypeError,
        ValueError
    ):

        return None, None


    user = db.session.get(
        User,
        user_id
    )


    if user is None:
        return None, None


    if user.role != "worker":
        return None, None


    worker = user.worker_profile


    return user, worker


# =========================================================
# WORKER DASHBOARD
# =========================================================

@worker_pages_bp.route(
    "/worker/dashboard",
    methods=["GET"]
)
@jwt_required()
def worker_dashboard_page():

    user, worker = get_current_worker()


    if user is None:
        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "worker/dashboard.html",
        user=user,
        worker=worker
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

    user, worker = get_current_worker()


    if user is None:
        return redirect(
            url_for("auth.login")
        )


    if worker is None:

        return redirect(
            url_for(
                "worker_pages.worker_dashboard_page"
            )
        )


    return render_template(
        "worker/profile.html",
        user=user,
        worker=worker
    )


# =========================================================
# WORKER JOBS
# =========================================================

@worker_pages_bp.route(
    "/worker/jobs",
    methods=["GET"]
)
@jwt_required()
def worker_jobs_page():

    user, worker = get_current_worker()


    if user is None:
        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "worker/jobs.html",
        user=user,
        worker=worker
    )


# =========================================================
# WORKER APPLICATIONS
# =========================================================

@worker_pages_bp.route(
    "/worker/applications",
    methods=["GET"]
)
@jwt_required()
def worker_applications_page():

    user, worker = get_current_worker()


    if user is None:
        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "worker/applications.html",
        user=user,
        worker=worker
    )


# =========================================================
# WORKER SETTINGS
# =========================================================

@worker_pages_bp.route(
    "/worker/settings",
    methods=["GET"]
)
@jwt_required()
def worker_settings_page():

    user, worker = get_current_worker()


    if user is None:
        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "worker/settings.html",
        user=user,
        worker=worker
    )
