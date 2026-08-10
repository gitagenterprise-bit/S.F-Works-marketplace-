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


@worker_pages_bp.route("/worker/profile")
def worker_profile_page():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(
            url_for("auth.login")
        )

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return redirect(
            url_for("auth.login")
        )

    worker = user.worker_profile

    if not worker:
        return redirect(
            url_for("worker_pages.worker_dashboard_page")
        )

    return render_template(
        "worker/profile.html",
        user=user,
        worker=worker
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
