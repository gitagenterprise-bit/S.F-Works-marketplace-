from flask import (
    Blueprint,
    request,
    jsonify
)

from extensions import db

from models.job_application import (
    JobApplication
)

from utils.decorators import role_required


admin_bp = Blueprint(
    "admin",
    __name__
)


@admin_bp.route(
    "/dashboard",
    methods=["GET"]
)
@role_required("admin")
def dashboard():

    return jsonify({
        "status": "success",
        "message": "Welcome to Admin Dashboard",
        "role": "admin"
    })


@admin_bp.route(
    "/applications",
    methods=["GET"]
)
@role_required("admin")
def all_applications():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        20,
        type=int
    )

    status = request.args.get(
        "status",
        type=str
    )

    query = JobApplication.query

    if status:

        query = query.filter(
            JobApplication.status ==
            status
        )

    query = query.order_by(
        JobApplication.created_at.desc()
    )

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    applications = []

    for application in pagination.items:

        worker = application.worker
        job = application.job

        applications.append({

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

                "name":
                    worker.full_name,

                "phone":
                    worker.phone,

                "email":
                    worker.email,

                "verified":
                    worker.is_verified
            },

            "job": {

                "id":
                    job.id,

                "title":
                    job.title,

                "city":
                    job.city,

                "status":
                    job.status
            }

        })

    return jsonify({

        "status": "success",

        "applications":
            applications,

        "pagination": {

            "page":
                pagination.page,

            "per_page":
                pagination.per_page,

            "total":
                pagination.total,

            "pages":
                pagination.pages
        }

    }), 200


@admin_bp.route(
    "/applications/<int:application_id>/status",
    methods=["PATCH"]
)
@role_required("admin")
def update_application_status(
    application_id
):

    application = db.session.get(
        JobApplication,
        application_id
    )

    if not application:

        return jsonify({

            "status": "error",

            "message":
                "Application not found"

        }), 404

    data = request.get_json()

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "Request body is required"

        }), 400

    new_status = data.get(
        "status"
    )

    allowed_statuses = {

        "pending",
        "reviewing",
        "shortlisted",
        "accepted",
        "rejected",
        "withdrawn",
        "completed"

    }

    if new_status not in allowed_statuses:

        return jsonify({

            "status": "error",

            "message":
                "Invalid application status"

        }), 400

    application.status = new_status

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Application status updated",

        "application": {

            "id":
                application.id,

            "status":
                application.status

        }

    }), 200
@admin_bp.route(
    "/workers/<int:worker_id>/verify",
    methods=["PATCH"]
)
@role_required("admin")
def verify_worker(worker_id):

    profile = WorkerProfile.query.filter_by(
        user_id=worker_id
    ).first()

    if not profile:

        return jsonify({

            "status": "error",

            "message":
                "Worker profile not found"

        }), 404

    data = request.get_json()

    action = data.get(
        "action"
    )

    if action == "approve":

        profile.is_verified = True

        profile.verification_status = (
            "approved"
        )

    elif action == "reject":

        profile.is_verified = False

        profile.verification_status = (
            "rejected"
        )

    else:

        return jsonify({

            "status": "error",

            "message":
                "Invalid verification action"

        }), 400

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Worker verification updated",

        "worker": {

            "id":
                worker_id,

            "is_verified":
                profile.is_verified,

            "verification_status":
                profile.verification_status

        }

    }), 200


