from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    get_jwt_identity
)

from extensions import db

from models.job import Job

from utils.decorators import role_required
from models.job_application import (
    JobApplication
)


customer_bp = Blueprint(
    "customer",
    __name__
)



@customer_bp.route(
    "/dashboard"
)
def dashboard():

    return render_template(
        "customer/dashboard.html"
)

@customer_bp.route(
    "/jobs",
    methods=["GET"]
)
@role_required("customer")
def my_jobs():

    user_id = get_jwt_identity()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int
    )

    query = Job.query.filter(
        Job.customer_id == int(user_id)
    ).order_by(
        Job.created_at.desc()
    )

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    jobs = []

    for job in pagination.items:

        jobs.append({

            "id": job.id,

            "title": job.title,

            "description": job.description,

            "status": job.status,

            "priority": job.priority,

            "location": job.location,

            "city": job.city,

            "state": job.state,

            "budget_min": (
                float(job.budget_min)
                if job.budget_min is not None
                else None
            ),

            "budget_max": (
                float(job.budget_max)
                if job.budget_max is not None
                else None
            ),

            "views": job.views,

            "category": (
                job.category.name
                if job.category
                else None
            ),

            "created_at": (
                job.created_at.isoformat()
            )
        })

    return jsonify({

        "status": "success",

        "jobs": jobs,

        "pagination": {

            "page": pagination.page,

            "per_page":
                pagination.per_page,

            "total":
                pagination.total,

            "pages":
                pagination.pages
        }

    }), 200

@customer_bp.route(
    "/jobs/<int:job_id>/applications",
    methods=["GET"]
)
@role_required("customer")
def job_applications(job_id):

    customer_id = get_jwt_identity()

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return jsonify({

            "status": "error",

            "message":
                "Job not found"

        }), 404

    if job.customer_id != int(
        customer_id
    ):

        return jsonify({

            "status": "error",

            "message":
                "You can only view applications for your own jobs"

        }), 403

    applications = (
        JobApplication.query
        .filter_by(
            job_id=job.id
        )
        .order_by(
            JobApplication.created_at.desc()
        )
        .all()
    )

    data = []

    for application in applications:

        worker = application.worker

        worker_profile = (
            worker.worker_profile
            if worker
            else None
        )

        data.append({

            "id":
                application.id,

            "status":
                application.status,

            "proposed_amount":
                float(
                    application.proposed_amount
                ),

            "message":
                application.message,

            "availability":
                application.availability,

            "created_at":
                application.created_at.isoformat(),

            "worker": {

                "id":
                    worker.id,

                "full_name":
                    worker.full_name,

                "profile_image":
                    worker.profile_image,

                "is_verified":
                    worker.is_verified,

                "profession":
                    worker_profile.profession
                    if worker_profile
                    else None,

                "experience_years":
                    worker_profile.experience_years
                    if worker_profile
                    else None,

                "rating":
                    float(
                        worker_profile.rating
                    )
                    if (
                        worker_profile
                        and worker_profile.rating
                        is not None
                    )
                    else 0,

                "total_reviews":
                    worker_profile.total_reviews
                    if worker_profile
                    else 0
            }

        })

    return jsonify({

        "status": "success",

        "job": {

            "id":
                job.id,

            "title":
                job.title,

            "status":
                job.status
        },

        "applications":
            data,

        "total":
            len(data)

    }), 200



