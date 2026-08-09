from flask import (
    Blueprint,
    render_template
)


worker_pages_bp = Blueprint(
    "worker_pages",
    __name__
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
    "/worker/profile"
)
def worker_profile_page():

    return render_template(
        "worker/profile.html"
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
