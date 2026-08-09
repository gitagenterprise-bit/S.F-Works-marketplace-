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


customer_bp = Blueprint(
    "customer",
    __name__
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

