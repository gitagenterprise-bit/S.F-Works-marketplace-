from datetime import datetime

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app
)

from flask_jwt_extended import get_jwt_identity

from sqlalchemy import or_

from extensions import db

from models.job import Job
from models.job_application import JobApplication
from models.worker import WorkerProfile
from models.worker_skill import WorkerSkill
from models.worker_portfolio import WorkerPortfolio

from utils.cloudinary_config import (
    upload_image,
    delete_image,
    validate_image
)

from utils.decorators import role_required


worker_bp = Blueprint(
    "worker",
    __name__
)


# =========================================================
# HELPERS
# =========================================================

def get_worker_user_id():

    identity = get_jwt_identity()

    try:
        return int(identity)
    except (TypeError, ValueError):
        return None


def get_worker_profile():

    user_id = get_worker_user_id()

    if user_id is None:
        return None

    return WorkerProfile.query.filter_by(
        user_id=user_id
    ).first()


def profile_to_dict(profile):

    if not profile:
        return None

    return {
        "id": profile.id,
        "user_id": profile.user_id,

        "profession": profile.profession,
        "headline": profile.headline,
        "about": profile.about,

        "profile_image": profile.profile_image,
        "cover_image": profile.cover_image,

        "experience_years":
            profile.experience_years,

        "service_area":
            profile.service_area,

        "service_radius_km":
            profile.service_radius_km,

        "address":
            profile.address,

        "city":
            profile.city,

        "state":
            profile.state,

        "pincode":
            profile.pincode,

        "latitude": (
            float(profile.latitude)
            if profile.latitude is not None
            else None
        ),

        "longitude": (
            float(profile.longitude)
            if profile.longitude is not None
            else None
        ),

        "hourly_rate": (
            float(profile.hourly_rate)
            if profile.hourly_rate is not None
            else None
        ),

        "minimum_charge": (
            float(profile.minimum_charge)
            if profile.minimum_charge is not None
            else None
        ),

        "availability":
            profile.availability,

        "is_available":
            profile.is_available,

        "is_verified":
            profile.is_verified,

        "verification_status":
            profile.verification_status,

        "rating": (
            float(profile.rating)
            if profile.rating is not None
            else 0.0
        ),

        "total_reviews":
            profile.total_reviews,

        "total_jobs":
            profile.total_jobs,

        "completed_jobs":
            profile.completed_jobs,

        "profile_completed":
            profile.profile_completed,

        "skills": [
            {
                "id": skill.id,
                "name": skill.skill_name,
                "experience_years":
                    skill.experience_years
            }
            for skill in profile.skills
        ],

        "portfolio": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "image":
                    item.image_path,
                "project_date": (
                    item.project_date.isoformat()
                    if item.project_date
                    else None
                )
            }
            for item in profile.portfolio_items
        ]
    }


# =========================================================
# DASHBOARD
# GET /worker/dashboard
# =========================================================

@worker_bp.route(
    "/dashboard",
    methods=["GET"]
)
@role_required("worker")
def dashboard():

    worker_id = get_worker_user_id()

    if worker_id is None:
        return jsonify({
            "status": "error",
            "message": "Invalid worker identity"
        }), 401

    total_applications = (
        JobApplication.query
        .filter_by(
            worker_id=worker_id
        )
        .count()
    )

    pending_applications = (
        JobApplication.query
        .filter_by(
            worker_id=worker_id,
            status="pending"
        )
        .count()
    )

    reviewing_applications = (
        JobApplication.query
        .filter_by(
            worker_id=worker_id,
            status="reviewing"
        )
        .count()
    )

    accepted_applications = (
        JobApplication.query
        .filter_by(
            worker_id=worker_id,
            status="accepted"
        )
        .count()
    )

    rejected_applications = (
        JobApplication.query
        .filter_by(
            worker_id=worker_id,
            status="rejected"
        )
        .count()
    )

    withdrawn_applications = (
        JobApplication.query
        .filter_by(
            worker_id=worker_id,
            status="withdrawn"
        )
        .count()
    )

    return jsonify({

        "status": "success",

        "dashboard": {

            "total_applications":
                total_applications,

            "pending_applications":
                pending_applications,

            "reviewing_applications":
                reviewing_applications,

            "accepted_applications":
                accepted_applications,

            "rejected_applications":
                rejected_applications,

            "withdrawn_applications":
                withdrawn_applications
        }

    }), 200


# =========================================================
# JOBS
# GET /worker/jobs
# =========================================================

@worker_bp.route(
    "/jobs",
    methods=["GET"]
)
@role_required("worker")
def worker_jobs():

    page = max(
        request.args.get(
            "page",
            1,
            type=int
        ),
        1
    )

    per_page = request.args.get(
        "per_page",
        12,
        type=int
    )

    per_page = max(
        min(per_page, 50),
        1
    )

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    city = request.args.get(
        "city",
        "",
        type=str
    ).strip()

    category_id = request.args.get(
        "category_id",
        type=int
    )

    query = Job.query.filter(
        Job.status == "open"
    )

    if search:

        pattern = f"%{search}%"

        query = query.filter(
            or_(
                Job.title.ilike(pattern),
                Job.description.ilike(pattern),
                Job.location.ilike(pattern),
                Job.city.ilike(pattern)
            )
        )

    if city:

        query = query.filter(
            Job.city.ilike(
                f"%{city}%"
            )
        )

    if category_id:

        query = query.filter(
            Job.category_id == category_id
        )

    query = query.order_by(
        Job.is_featured.desc(),
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

            "id":
                job.id,

            "title":
                job.title,

            "description":
                job.description,

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

            "location":
                job.location,

            "city":
                job.city,

            "state":
                job.state,

            "priority":
                job.priority,

            "is_featured":
                job.is_featured,

            "views":
                job.views,

            "category": (
                {
                    "id": job.category.id,
                    "name": job.category.name,
                    "slug": job.category.slug,
                    "icon": job.category.icon
                }
                if job.category
                else None
            ),

            "created_at":
                job.created_at.isoformat()
        })

    return jsonify({

        "status": "success",

        "jobs":
            jobs,

        "pagination": {

            "page":
                pagination.page,

            "per_page":
                pagination.per_page,

            "total":
                pagination.total,

            "pages":
                pagination.pages,

            "has_next":
                pagination.has_next,

            "has_prev":
                pagination.has_prev
        }

    }), 200


# =========================================================
# APPLY JOB
# POST /worker/jobs/<job_id>/apply
# =========================================================

@worker_bp.route(
    "/jobs/<int:job_id>/apply",
    methods=["POST"]
)
@role_required("worker")
def apply_for_job(job_id):

    worker_id = get_worker_user_id()

    if worker_id is None:
        return jsonify({
            "status": "error",
            "message": "Invalid worker identity"
        }), 401

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return jsonify({
            "status": "error",
            "message": "Job not found"
        }), 404

    if job.status != "open":

        return jsonify({
            "status": "error",
            "message":
                "This job is no longer available"
        }), 400

    if job.customer_id == worker_id:

        return jsonify({
            "status": "error",
            "message":
                "You cannot apply to your own job"
        }), 403

    existing = (
        JobApplication.query
        .filter_by(
            job_id=job.id,
            worker_id=worker_id
        )
        .first()
    )

    if existing:

        return jsonify({

            "status": "error",

            "message":
                "You have already applied for this job",

            "application_id":
                existing.id

        }), 409

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "status": "error",
            "message":
                "Request body is required"
        }), 400

    proposed_amount = data.get(
        "proposed_amount"
    )

    if proposed_amount is None:

        return jsonify({
            "status": "error",
            "message":
                "Proposed amount is required"
        }), 400

    try:

        proposed_amount = float(
            proposed_amount
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "status": "error",
            "message":
                "Invalid proposed amount"
        }), 400

    if proposed_amount <= 0:

        return jsonify({
            "status": "error",
            "message":
                "Proposed amount must be greater than zero"
        }), 400

    message = data.get(
        "message"
    )

    availability = data.get(
        "availability"
    )

    application = JobApplication(

        job_id=job.id,

        worker_id=worker_id,

        proposed_amount=proposed_amount,

        message=(
            str(message).strip()
            if message
            else None
        ),

        availability=(
            str(availability).strip()
            if availability
            else None
        ),

        status="pending"
    )

    db.session.add(
        application
    )

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Job application creation failed"
        )

        return jsonify({
            "status": "error",
            "message":
                "Unable to submit application"
        }), 500

    return jsonify({

        "status": "success",

        "message":
            "Application submitted successfully",

        "application": {

            "id":
                application.id,

            "job_id":
                application.job_id,

            "status":
                application.status,

            "proposed_amount":
                float(
                    application.proposed_amount
                ),

            "created_at":
                application.created_at.isoformat()
        }

    }), 201


# =========================================================
# MY APPLICATIONS
# GET /worker/applications
# =========================================================

@worker_bp.route(
    "/applications",
    methods=["GET"]
)
@role_required("worker")
def my_applications():

    worker_id = get_worker_user_id()

    if worker_id is None:
        return jsonify({
            "status": "error",
            "message": "Invalid worker identity"
        }), 401

    page = max(
        request.args.get(
            "page",
            1,
            type=int
        ),
        1
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int
    )

    per_page = max(
        min(per_page, 50),
        1
    )

    status = request.args.get(
        "status",
        type=str
    )

    query = JobApplication.query.filter(
        JobApplication.worker_id ==
        worker_id
    )

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

            "job": {

                "id":
                    job.id,

                "title":
                    job.title,

                "status":
                    job.status,

                "city":
                    job.city,

                "location":
                    job.location,

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

                "category": (
                    job.category.name
                    if job.category
                    else None
                )
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
                pagination.pages,

            "has_next":
                pagination.has_next,

            "has_prev":
                pagination.has_prev
        }

    }), 200


# =========================================================
# APPLICATION DETAILS
# GET /worker/applications/<id>
# =========================================================

@worker_bp.route(
    "/applications/<int:application_id>",
    methods=["GET"]
)
@role_required("worker")
def application_details(application_id):

    worker_id = get_worker_user_id()

    application = db.session.get(
        JobApplication,
        application_id
    )

    if not application:

        return jsonify({
            "status": "error",
            "message": "Application not found"
        }), 404

    if application.worker_id != worker_id:

        return jsonify({
            "status": "error",
            "message":
                "You can only view your own application"
        }), 403

    job = application.job

    return jsonify({

        "status": "success",

        "application": {

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

            "updated_at":
                application.updated_at.isoformat()
                if application.updated_at
                else None,

            "job": {

                "id":
                    job.id,

                "title":
                    job.title,

                "description":
                    job.description,

                "location":
                    job.location,

                "city":
                    job.city,

                "state":
                    job.state,

                "status":
                    job.status
            }
        }

    }), 200


# =========================================================
# WITHDRAW APPLICATION
# POST /worker/applications/<id>/withdraw
# =========================================================

@worker_bp.route(
    "/applications/<int:application_id>/withdraw",
    methods=["POST"]
)
@role_required("worker")
def withdraw_application(application_id):

    worker_id = get_worker_user_id()

    application = db.session.get(
        JobApplication,
        application_id
    )

    if not application:

        return jsonify({
            "status": "error",
            "message": "Application not found"
        }), 404

    if application.worker_id != worker_id:

        return jsonify({
            "status": "error",
            "message":
                "You can only withdraw your own application"
        }), 403

    if application.status not in (
        "pending",
        "reviewing"
    ):

        return jsonify({
            "status": "error",
            "message":
                "This application cannot be withdrawn"
        }), 400

    application.status = "withdrawn"

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Application withdrawal failed"
        )

        return jsonify({
            "status": "error",
            "message":
                "Unable to withdraw application"
        }), 500

    return jsonify({
        "status": "success",
        "message":
            "Application withdrawn successfully"
    }), 200


# =========================================================
# GET MY PROFILE
# GET /worker/profile
# =========================================================

@worker_bp.route(
    "/profile",
    methods=["GET"]
)
@role_required("worker")
def get_my_profile():

    profile = get_worker_profile()

    return jsonify({

        "status": "success",

        "profile":
            profile_to_dict(profile)

    }), 200


# =========================================================
# CREATE / UPDATE PROFILE
# POST /worker/profile
# =========================================================

@worker_bp.route(
    "/profile",
    methods=["POST"]
)
@role_required("worker")
def save_profile():

    worker_id = get_worker_user_id()

    if worker_id is None:

        return jsonify({
            "status": "error",
            "message":
                "Invalid worker identity"
        }), 401

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "status": "error",
            "message":
                "Request body is required"
        }), 400

    profile = WorkerProfile.query.filter_by(
        user_id=worker_id
    ).first()

    if not profile:

        profile = WorkerProfile(
            user_id=worker_id,
            profession=""
        )

        db.session.add(
            profile
        )

    # =====================================================
    # BASIC
    # =====================================================

    if "profession" in data:

        profession = data["profession"]

        profile.profession = (
            str(profession).strip()
            if profession is not None
            else ""
        )

    if "headline" in data:

        value = data["headline"]

        profile.headline = (
            str(value).strip()
            if value
            else None
        )

    if "about" in data:

        value = data["about"]

        profile.about = (
            str(value).strip()
            if value
            else None
        )

    # =====================================================
    # EXPERIENCE
    # =====================================================

    if "experience_years" in data:

        try:

            experience = int(
                data["experience_years"]
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({
                "status": "error",
                "message":
                    "Invalid experience years"
            }), 400

        if experience < 0:

            return jsonify({
                "status": "error",
                "message":
                    "Experience cannot be negative"
            }), 400

        profile.experience_years = experience

    # =====================================================
    # LOCATION
    # =====================================================

    if "service_radius_km" in data:

        try:

            radius = int(
                data["service_radius_km"]
            )

            if radius < 0:
                raise ValueError

            profile.service_radius_km = radius

        except (
            TypeError,
            ValueError
        ):

            return jsonify({
                "status": "error",
                "message":
                    "Invalid service radius"
            }), 400

    if "service_area" in data:

        value = data["service_area"]

        profile.service_area = (
            str(value).strip()
            if value
            else None
        )

    if "address" in data:

        value = data["address"]

        profile.address = (
            str(value).strip()
            if value
            else None
        )

    if "city" in data:

        value = data["city"]

        profile.city = (
            str(value).strip()
            if value
            else None
        )

    if "state" in data:

        value = data["state"]

        profile.state = (
            str(value).strip()
            if value
            else None
        )

    if "pincode" in data:

        value = data["pincode"]

        profile.pincode = (
            str(value).strip()
            if value
            else None
        )

    # =====================================================
    # PRICING
    # =====================================================

    if "hourly_rate" in data:

        value = data["hourly_rate"]

        if value in (
            None,
            ""
        ):

            profile.hourly_rate = None

        else:

            try:

                value = float(value)

                if value < 0:
                    raise ValueError

                profile.hourly_rate = value

            except (
                TypeError,
                ValueError
            ):

                return jsonify({
                    "status": "error",
                    "message":
                        "Invalid hourly rate"
                }), 400

    if "minimum_charge" in data:

        value = data["minimum_charge"]

        if value in (
            None,
            ""
        ):

            profile.minimum_charge = None

        else:

            try:

                value = float(value)

                if value < 0:
                    raise ValueError

                profile.minimum_charge = value

            except (
                TypeError,
                ValueError
            ):

                return jsonify({
                    "status": "error",
                    "message":
                        "Invalid minimum charge"
                }), 400

    # =====================================================
    # AVAILABILITY
    # =====================================================

    if "availability" in data:

        value = data["availability"]

        profile.availability = (
            str(value).strip()
            if value
            else None
        )

    if "is_available" in data:

        value = data["is_available"]

        if not isinstance(
            value,
            bool
        ):

            return jsonify({
                "status": "error",
                "message":
                    "is_available must be boolean"
            }), 400

        profile.is_available = value

    # =====================================================
    # PROFILE COMPLETION
    # =====================================================

    profile.update_profile_completion()

    # =====================================================
    # DATABASE
    # =====================================================

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Worker profile save failed"
        )

        return jsonify({
            "status": "error",
            "message":
                "Unable to save worker profile"
        }), 500

    return jsonify({

        "status": "success",

        "message":
            "Worker profile saved successfully",

        "profile":
            profile_to_dict(profile)

    }), 200
