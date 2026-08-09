from flask import (
    Blueprint,
    request,
    jsonify
)

from flask_jwt_extended import (
    get_jwt_identity
)

from sqlalchemy import or_

from extensions import db

from models.job import Job

from models.category import Category

from models.job_application import (
    JobApplication
)

from models.worker_profile import (
    WorkerProfile
)

from models.worker_skill import (
    WorkerSkill
)

from models.worker_portfolio import (
    WorkerPortfolio
)

from utils.decorators import role_required


worker_bp = Blueprint(
    "worker",
    __name__
)

@worker_bp.route(
    "/dashboard",
    methods=["GET"]
)
@role_required("worker")
def dashboard():

    worker_id = get_jwt_identity()

    total_applications = (
        JobApplication.query
        .filter_by(
            worker_id=int(worker_id)
        )
        .count()
    )

    pending_applications = (
        JobApplication.query
        .filter_by(
            worker_id=int(worker_id),
            status="pending"
        )
        .count()
    )

    accepted_applications = (
        JobApplication.query
        .filter_by(
            worker_id=int(worker_id),
            status="accepted"
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

            "accepted_applications":
                accepted_applications
        }

    }), 200

@worker_bp.route(
    "/jobs",
    methods=["GET"]
)
@role_required("worker")
def worker_jobs():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        12,
        type=int
    )

    if per_page > 50:
        per_page = 50

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
                Job.location.ilike(pattern)
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

            "id": job.id,

            "title": job.title,

            "description": job.description,

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

            "location": job.location,

            "city": job.city,

            "state": job.state,

            "priority": job.priority,

            "is_featured":
                job.is_featured,

            "views":
                job.views,

            "category": {

                "id": job.category.id,

                "name":
                    job.category.name,

                "slug":
                    job.category.slug,

                "icon":
                    job.category.icon

            } if job.category else None,

            "created_at":
                job.created_at.isoformat()
        })

    return jsonify({

        "status": "success",

        "jobs": jobs,

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

@worker_bp.route(
    "/jobs/<int:job_id>/apply",
    methods=["POST"]
)
@role_required("worker")
def apply_for_job(job_id):

    worker_id = get_jwt_identity()

    worker_id = int(worker_id)

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

    if job.status != "open":

        return jsonify({

            "status": "error",

            "message":
                "This job is no longer available"

        }), 400

    # Worker cannot apply to own job
    if job.customer_id == worker_id:

        return jsonify({

            "status": "error",

            "message":
                "You cannot apply to your own job"

        }), 403

    # Check duplicate application

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

    data = request.get_json()

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "Request body is required"

        }), 400

    proposed_amount = data.get(
        "proposed_amount"
    )

    message = data.get(
        "message"
    )

    availability = data.get(
        "availability"
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

    application = JobApplication(

        job_id=job.id,

        worker_id=worker_id,

        proposed_amount=
            proposed_amount,

        message=(
            message.strip()
            if message
            else None
        ),

        availability=(
            availability.strip()
            if availability
            else None
        ),

        status="pending"
    )

    db.session.add(
        application
    )

    db.session.commit()

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

@worker_bp.route(
    "/applications",
    methods=["GET"]
)
@role_required("worker")
def my_applications():

    worker_id = get_jwt_identity()

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

    status = request.args.get(
        "status",
        type=str
    )

    query = JobApplication.query.filter(
        JobApplication.worker_id ==
        int(worker_id)
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

                "category":
                    job.category.name
                    if job.category
                    else None
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

@worker_bp.route(
    "/applications/<int:application_id>",
    methods=["GET"]
)
@role_required("worker")
def application_details(
    application_id
):

    worker_id = get_jwt_identity()

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

    if application.worker_id != int(
        worker_id
    ):

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

@worker_bp.route(
    "/applications/<int:application_id>/withdraw",
    methods=["POST"]
)
@role_required("worker")
def withdraw_application(
    application_id
):

    worker_id = get_jwt_identity()

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

    if application.worker_id != int(
        worker_id
    ):

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

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Application withdrawn successfully"

    }), 200

@worker_bp.route(
    "/profile",
    methods=["GET"]
)
@role_required("worker")
def get_my_profile():

    worker_id = get_jwt_identity()

    profile = WorkerProfile.query.filter_by(
        user_id=int(worker_id)
    ).first()

    if not profile:

        return jsonify({
            "status": "success",
            "profile": None
        }), 200

    return jsonify({

        "status": "success",

        "profile": {

            "id": profile.id,

            "profession":
                profile.profession,

            "headline":
                profile.headline,

            "about":
                profile.about,

            "experience_years":
                profile.experience_years,

            "service_radius_km":
                profile.service_radius_km,

            "service_area":
                profile.service_area,

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

            "profile_image":
                profile.profile_image,

            "cover_image":
                profile.cover_image,

            "rating":
                float(profile.rating),

            "total_reviews":
                profile.total_reviews,

            "completed_jobs":
                profile.completed_jobs,

            "is_verified":
                profile.is_verified,

            "verification_status":
                profile.verification_status,

            "is_available":
                profile.is_available,

            "profile_completed":
                profile.profile_completed

        }

    }), 200

@worker_bp.route(
    "/profile",
    methods=["POST"]
)
@role_required("worker")
def save_profile():

    worker_id = get_jwt_identity()

    data = request.get_json()

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "Request body is required"

        }), 400

    profile = WorkerProfile.query.filter_by(
        user_id=int(worker_id)
    ).first()

    if not profile:

        profile = WorkerProfile(
            user_id=int(worker_id)
        )

        db.session.add(profile)

    if "profession" in data:

        profile.profession = (
            data["profession"].strip()
            if data["profession"]
            else None
        )

    if "headline" in data:

        profile.headline = (
            data["headline"].strip()
            if data["headline"]
            else None
        )

    if "about" in data:

        profile.about = (
            data["about"].strip()
            if data["about"]
            else None
        )

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

    if "service_radius_km" in data:

        profile.service_radius_km = (
            data["service_radius_km"]
        )

    if "service_area" in data:

        profile.service_area = (
            data["service_area"].strip()
            if data["service_area"]
            else None
        )

    if "hourly_rate" in data:

        profile.hourly_rate = (
            data["hourly_rate"]
        )

    if "minimum_charge" in data:

        profile.minimum_charge = (
            data["minimum_charge"]
        )

    if "availability" in data:

        profile.availability = (
            data["availability"].strip()
            if data["availability"]
            else None
        )

    if "is_available" in data:

        profile.is_available = bool(
            data["is_available"]
        )

    # Profile completion

    required_fields = [

        profile.profession,

        profile.headline,

        profile.about,

        profile.service_area

    ]

    profile.profile_completed = all(
        field not in (None, "")
        for field in required_fields
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Worker profile saved successfully",

        "profile_completed":
            profile.profile_completed

    }), 200

@worker_bp.route(
    "/profile/skills",
    methods=["POST"]
)
@role_required("worker")
def add_skill():

    worker_id = get_jwt_identity()

    profile = WorkerProfile.query.filter_by(
        user_id=int(worker_id)
    ).first()

    if not profile:

        return jsonify({

            "status": "error",

            "message":
                "Please create your profile first"

        }), 400

    data = request.get_json()

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "Request body is required"

        }), 400

    skill_name = data.get(
        "skill_name"
    )

    if not skill_name:

        return jsonify({

            "status": "error",

            "message":
                "Skill name is required"

        }), 400

    skill_name = skill_name.strip()

    existing = WorkerSkill.query.filter_by(
        worker_id=profile.id,
        skill_name=skill_name
    ).first()

    if existing:

        return jsonify({

            "status": "error",

            "message":
                "Skill already exists"

        }), 409

    skill = WorkerSkill(

        worker_id=profile.id,

        skill_name=skill_name,

        experience_years=
            data.get("experience_years")

    )

    db.session.add(skill)

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Skill added successfully",

        "skill": {

            "id":
                skill.id,

            "name":
                skill.skill_name,

            "experience_years":
                skill.experience_years

        }

    }), 201

@worker_bp.route(
    "/profile/skills/<int:skill_id>",
    methods=["DELETE"]
)
@role_required("worker")
def delete_skill(skill_id):

    worker_id = get_jwt_identity()

    profile = WorkerProfile.query.filter_by(
        user_id=int(worker_id)
    ).first()

    if not profile:

        return jsonify({

            "status": "error",

            "message":
                "Profile not found"

        }), 404

    skill = db.session.get(
        WorkerSkill,
        skill_id
    )

    if not skill:

        return jsonify({

            "status": "error",

            "message":
                "Skill not found"

        }), 404

    if skill.worker_id != profile.id:

        return jsonify({

            "status": "error",

            "message":
                "You cannot delete this skill"

        }), 403

    db.session.delete(skill)

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Skill deleted successfully"

    }), 200

@worker_bp.route(
    "/profile/portfolio",
    methods=["POST"]
)
@role_required("worker")
def add_portfolio():

    worker_id = get_jwt_identity()

    profile = WorkerProfile.query.filter_by(
        user_id=int(worker_id)
    ).first()

    if not profile:

        return jsonify({

            "status": "error",

            "message":
                "Please create your profile first"

        }), 400

    data = request.get_json()

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "Request body is required"

        }), 400

    title = data.get(
        "title"
    )

    if not title:

        return jsonify({

            "status": "error",

            "message":
                "Portfolio title is required"

        }), 400

    portfolio = WorkerPortfolio(

        worker_id=profile.id,

        title=title.strip(),

        description=(
            data.get("description").strip()
            if data.get("description")
            else None
        ),

        image_path=
            data.get("image_path")

    )

    db.session.add(portfolio)

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Portfolio item added",

        "portfolio": {

            "id":
                portfolio.id,

            "title":
                portfolio.title,

            "description":
                portfolio.description,

            "image_path":
                portfolio.image_path

        }

    }), 201

@worker_bp.route(
    "/profile/portfolio/<int:portfolio_id>",
    methods=["DELETE"]
)
@role_required("worker")
def delete_portfolio(
    portfolio_id
):

    worker_id = get_jwt_identity()

    profile = WorkerProfile.query.filter_by(
        user_id=int(worker_id)
    ).first()

    if not profile:

        return jsonify({

            "status": "error",

            "message":
                "Profile not found"

        }), 404

    portfolio = db.session.get(
        WorkerPortfolio,
        portfolio_id
    )

    if not portfolio:

        return jsonify({

            "status": "error",

            "message":
                "Portfolio item not found"

        }), 404

    if portfolio.worker_id != profile.id:

        return jsonify({

            "status": "error",

            "message":
                "You cannot delete this portfolio item"

        }), 403

    db.session.delete(
        portfolio
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Portfolio item deleted"

    }), 200

@worker_bp.route(
    "/<int:worker_id>",
    methods=["GET"]
)
def public_worker_profile(worker_id):

    profile = WorkerProfile.query.filter_by(
        user_id=worker_id
    ).first()

    if not profile:

        return jsonify({

            "status": "error",

            "message":
                "Worker profile not found"

        }), 404

    user = profile.user

    skills = []

    for skill in profile.skills:

        skills.append({

            "id":
                skill.id,

            "name":
                skill.skill_name,

            "experience_years":
                skill.experience_years

        })

    portfolio = []

    for item in profile.portfolio_items:

        portfolio.append({

            "id":
                item.id,

            "title":
                item.title,

            "description":
                item.description,

            "image":
                item.image_path,

            "project_date":
                (
                    item.project_date.isoformat()
                    if item.project_date
                    else None
                )

        })

    return jsonify({

        "status": "success",

        "worker": {

            "id":
                user.id,

            "name":
                user.full_name,

            "profile_image":
                profile.profile_image,

            "cover_image":
                profile.cover_image,

            "profession":
                profile.profession,

            "headline":
                profile.headline,

            "about":
                profile.about,

            "experience_years":
                profile.experience_years,

            "service_area":
                profile.service_area,

            "service_radius_km":
                profile.service_radius_km,

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

            "rating":
                float(profile.rating),

            "total_reviews":
                profile.total_reviews,

            "completed_jobs":
                profile.completed_jobs,

            "is_verified":
                profile.is_verified,

            "is_available":
                profile.is_available,

            "skills":
                skills,

            "portfolio":
                portfolio

        }

    }), 200



