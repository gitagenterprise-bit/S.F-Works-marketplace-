from flask import (
    Blueprint,
    render_template
)


job_pages_bp = Blueprint(
    "job_pages",
    __name__
)


# ============================================================
# PUBLIC JOBS PAGE
# ============================================================

@job_pages_bp.route(
    "/jobs",
    methods=["GET"]
)
def jobs_page():

    return render_template(
        "public/jobs.html"
    )


# ============================================================
# JOB DETAILS PAGE
# ============================================================

@job_pages_bp.route(
    "/jobs/<int:job_id>",
    methods=["GET"]
)
def job_details_page(job_id):

    return render_template(
        "public/job-details.html",
        job_id=job_id
    )


# ============================================================
# POST JOB PAGE
# ============================================================

@job_pages_bp.route(
    "/post-job",
    methods=["GET"]
)
def post_job_page():

    return render_template(
        "customer/post-job.html"
    )
