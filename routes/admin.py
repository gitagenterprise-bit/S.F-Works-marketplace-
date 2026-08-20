from flask import (
    Blueprint,
    request,
    jsonify,
    render_template
)

from sqlalchemy import func

from flask_jwt_extended import (
    get_jwt_identity
)

from extensions import db

from models.user import User
from models.job import Job
from models import WorkerProfile
from models.job_application import JobApplication
from models.category import Category

from utils.decorators import role_required


admin_bp = Blueprint(
    "admin",
    __name__
)

@admin_bp.route("/dashboard-page")
def admin_dashboard_page():
    return render_template(
        "admin/dashboard.html"
    )
    
@admin_bp.route(
    "/dashboard",
    methods=["GET"]
)
@role_required("admin")
def admin_dashboard():

    total_users = User.query.count()

    total_customers = User.query.filter_by(
        role="customer"
    ).count()

    total_workers = User.query.filter_by(
        role="worker"
    ).count()

    total_admins = User.query.filter_by(
        role="admin"
    ).count()

    total_jobs = Job.query.count()

    open_jobs = Job.query.filter_by(
        status="open"
    ).count()

    assigned_jobs = Job.query.filter_by(
        status="assigned"
    ).count()

    completed_jobs = Job.query.filter_by(
        status="completed"
    ).count()

    total_applications = (
        JobApplication.query.count()
    )

    pending_applications = (
        JobApplication.query
        .filter_by(
            status="pending"
        )
        .count()
    )

    accepted_applications = (
        JobApplication.query
        .filter_by(
            status="accepted"
        )
        .count()
    )

    rejected_applications = (
        JobApplication.query
        .filter_by(
            status="rejected"
        )
        .count()
    )

    verified_workers = (
        WorkerProfile.query
        .filter_by(
            is_verified=True
        )
        .count()
    )

    pending_verification = (
        WorkerProfile.query
        .filter(
            WorkerProfile.verification_status.in_(
                [
                    "submitted",
                    "under_review"
                ]
            )
        )
        .count()
    )

    return jsonify({

        "status": "success",

        "dashboard": {

            "users": {

                "total":
                    total_users,

                "customers":
                    total_customers,

                "workers":
                    total_workers,

                "admins":
                    total_admins
            },

            "jobs": {

                "total":
                    total_jobs,

                "open":
                    open_jobs,

                "assigned":
                    assigned_jobs,

                "completed":
                    completed_jobs
            },

            "applications": {

                "total":
                    total_applications,

                "pending":
                    pending_applications,

                "accepted":
                    accepted_applications,

                "rejected":
                    rejected_applications
            },

            "workers": {

                "verified":
                    verified_workers,

                "pending_verification":
                    pending_verification
            }

        }

    }), 200


@admin_bp.route(
    "/customers",
    methods=["GET"]
)
@role_required("admin")
def admin_customers():

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

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    query = User.query.filter_by(
        role="customer"
    )

    if search:

        pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
                User.phone.ilike(pattern)
            )
        )

    query = query.order_by(
        User.created_at.desc()
    )

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    customers = []

    for user in pagination.items:

        customers.append({

            "id":
                user.id,

            "name":
                user.full_name,

            "email":
                user.email,

            "phone":
                user.phone,

            "is_active":
                user.is_active,

            "created_at":
                user.created_at.isoformat()

        })

    return jsonify({

        "status": "success",

        "customers":
            customers,

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
    "/customers/<int:user_id>/status",
    methods=["PATCH"]
)
@role_required("admin")
def update_customer_status(user_id):

    customer = User.query.filter_by(
        id=user_id,
        role="customer"
    ).first()

    if not customer:

        return jsonify({

            "status": "error",

            "message":
                "Customer not found"

        }), 404

    data = request.get_json()

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "Request body is required"

        }), 400

    is_active = data.get(
        "is_active"
    )

    if not isinstance(
        is_active,
        bool
    ):

        return jsonify({

            "status": "error",

            "message":
                "is_active must be boolean"

        }), 400

    customer.is_active = is_active

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Customer status updated",

        "customer": {

            "id":
                customer.id,

            "is_active":
                customer.is_active

        }

    }), 200


@admin_bp.route(
    "/workers",
    methods=["GET"]
)
@role_required("admin")
def admin_workers():

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

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    verified = request.args.get(
        "verified",
        type=str
    )

    query = (
        WorkerProfile.query
        .join(User)
    )

    if search:

        pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                User.full_name.ilike(pattern),
                WorkerProfile.profession.ilike(pattern),
                WorkerProfile.service_area.ilike(pattern)
            )
        )

    if verified == "true":

        query = query.filter(
            WorkerProfile.is_verified.is_(True)
        )

    elif verified == "false":

        query = query.filter(
            WorkerProfile.is_verified.is_(False)
        )

    query = query.order_by(
        WorkerProfile.created_at.desc()
    )

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    workers = []

    for profile in pagination.items:

        user = profile.user

        workers.append({

            "id":
                user.id,

            "name":
                user.full_name,

            "email":
                user.email,

            "phone":
                user.phone,

            "profession":
                profile.profession,

            "experience_years":
                profile.experience_years,

            "rating":
                float(profile.rating),

            "completed_jobs":
                profile.completed_jobs,

            "is_verified":
                profile.is_verified,

            "verification_status":
                profile.verification_status,

            "is_available":
                profile.is_available,

            "created_at":
                profile.created_at.isoformat()

        })

    return jsonify({

        "status": "success",

        "workers":
            workers,

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
    "/workers/<int:user_id>/status",
    methods=["PATCH"]
)
@role_required("admin")
def update_worker_status(user_id):

    worker = User.query.filter_by(
        id=user_id,
        role="worker"
    ).first()

    if not worker:

        return jsonify({

            "status": "error",

            "message":
                "Worker not found"

        }), 404

    data = request.get_json()

    is_active = data.get(
        "is_active"
    )

    if not isinstance(
        is_active,
        bool
    ):

        return jsonify({

            "status": "error",

            "message":
                "is_active must be boolean"

        }), 400

    worker.is_active = is_active

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Worker status updated"

    }), 200


@admin_bp.route(
    "/workers/verification",
    methods=["GET"]
)
@role_required("admin")
def verification_queue():

    status = request.args.get(
        "status",
        "under_review"
    )

    profiles = (
        WorkerProfile.query
        .filter_by(
            verification_status=status
        )
        .order_by(
            WorkerProfile.created_at.asc()
        )
        .all()
    )

    workers = []

    for profile in profiles:

        user = profile.user

        workers.append({

            "worker_id":
                user.id,

            "name":
                user.full_name,

            "phone":
                user.phone,

            "email":
                user.email,

            "profession":
                profile.profession,

            "experience_years":
                profile.experience_years,

            "verification_status":
                profile.verification_status,

            "created_at":
                profile.created_at.isoformat()

        })

    return jsonify({

        "status": "success",

        "workers":
            workers,

        "total":
            len(workers)

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

    elif action == "review":

        profile.verification_status = (
            "under_review"
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


@admin_bp.route(
    "/jobs",
    methods=["GET"]
)
@role_required("admin")
def admin_jobs():

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

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    query = Job.query

    if status:

        query = query.filter(
            Job.status == status
        )

    if search:

        pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                Job.title.ilike(pattern),
                Job.description.ilike(pattern),
                Job.city.ilike(pattern)
            )
        )

    query = query.order_by(
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

            "status":
                job.status,

            "priority":
                job.priority,

            "city":
                job.city,

            "category":
                job.category.name
                if job.category
                else None,

            "customer_id":
                job.customer_id,

            "views":
                job.views,

            "is_featured":
                job.is_featured,

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
                pagination.pages

        }

    }), 200


@admin_bp.route(
    "/jobs/<int:job_id>/status",
    methods=["PATCH"]
)
@role_required("admin")
def admin_job_status(job_id):

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

    data = request.get_json()

    new_status = data.get(
        "status"
    )

    allowed_statuses = {

        "open",
        "assigned",
        "in_progress",
        "completed",
        "cancelled",
        "closed"

    }

    if new_status not in allowed_statuses:

        return jsonify({

            "status": "error",

            "message":
                "Invalid job status"

        }), 400

    job.status = new_status

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Job status updated",

        "job": {

            "id":
                job.id,

            "status":
                job.status

        }

    }), 200


@admin_bp.route(
    "/jobs/<int:job_id>/featured",
    methods=["PATCH"]
)
@role_required("admin")
def toggle_featured_job(job_id):

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

    data = request.get_json()

    featured = data.get(
        "is_featured"
    )

    if not isinstance(
        featured,
        bool
    ):

        return jsonify({

            "status": "error",

            "message":
                "is_featured must be boolean"

        }), 400

    job.is_featured = featured

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Featured status updated",

        "job": {

            "id":
                job.id,

            "is_featured":
                job.is_featured

        }

    }), 200


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
            JobApplication.status == status
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

            "worker": {

                "id":
                    worker.id,

                "name":
                    worker.full_name,

                "verified":
                    worker.worker_profile.is_verified
                    if worker.worker_profile
                    else False

            },

            "job": {

                "id":
                    job.id,

                "title":
                    job.title,

                "city":
                    job.city

            },

            "created_at":
                application.created_at.isoformat()

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

    new_status = data.get(
        "status"
    )

    allowed = {

        "pending",
        "reviewing",
        "shortlisted",
        "accepted",
        "rejected",
        "withdrawn",
        "completed"

    }

    if new_status not in allowed:

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
    "/categories",
    methods=["POST"]
)
@role_required("admin")
def create_category():

    data = request.get_json()

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "Request body is required"

        }), 400

    name = data.get(
        "name"
    )

    slug = data.get(
        "slug"
    )

    if not name or not slug:

        return jsonify({

            "status": "error",

            "message":
                "Name and slug are required"

        }), 400

    existing = Category.query.filter(
        db.or_(
            Category.name.ilike(name),
            Category.slug == slug
        )
    ).first()

    if existing:

        return jsonify({

            "status": "error",

            "message":
                "Category already exists"

        }), 409

    category = Category(

        name=name.strip(),

        slug=slug.strip().lower(),

        description=(
            data.get("description")
        ),

        icon=(
            data.get("icon")
        ),

        image=(
            data.get("image")
        ),

        is_active=True
    )

    db.session.add(
        category
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Category created successfully",

        "category": {

            "id":
                category.id,

            "name":
                category.name,

            "slug":
                category.slug

        }

    }), 201


@admin_bp.route(
    "/categories/<int:category_id>/status",
    methods=["PATCH"]
)
@role_required("admin")
def category_status(category_id):

    category = db.session.get(
        Category,
        category_id
    )

    if not category:

        return jsonify({

            "status": "error",

            "message":
                "Category not found"

        }), 404

    data = request.get_json()

    is_active = data.get(
        "is_active"
    )

    if not isinstance(
        is_active,
        bool
    ):

        return jsonify({

            "status": "error",

            "message":
                "is_active must be boolean"

        }), 400

    category.is_active = is_active

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Category status updated"

    }), 200
@admin_bp.route(
    "/create-first-admin",
    methods=["POST"]
)
def create_first_admin():

    # ----------------------------------------
    # SECURITY KEY
    # ----------------------------------------

    setup_key = request.headers.get(
        "X-Admin-Setup-Key"
    )

    if setup_key != "SFWORKS-ADMIN-SETUP-2026":
        return jsonify({
            "status": "error",
            "message": "Invalid setup key"
        }), 403

    # ----------------------------------------
    # CHECK EXISTING ADMIN
    # ----------------------------------------

    existing_admin = User.query.filter_by(
        role="admin"
    ).first()

    if existing_admin:

        return jsonify({
            "status": "error",
            "message": "An admin user already exists"
        }), 409

    # ----------------------------------------
    # ADMIN DETAILS
    # ----------------------------------------

    email = "admin@sfworks.com"
    password = "Admin@12345"

    # ----------------------------------------
    # CHECK EMAIL
    # ----------------------------------------

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:

        existing_user.role = "admin"
        existing_user.is_active = True
        existing_user.set_password(password)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Existing user converted to admin",
            "admin": {
                "id": existing_user.id,
                "email": existing_user.email,
                "role": existing_user.role
            }
        }), 200

    # ----------------------------------------
    # CREATE ADMIN
    # ----------------------------------------

    admin = User(
        full_name="S F Works Admin",
        email=email,
        phone="9999999999",
        role="admin",
        is_active=True
    )

    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "First admin created successfully",
        "admin": {
            "id": admin.id,
            "full_name": admin.full_name,
            "email": admin.email,
            "role": admin.role,
            "is_active": admin.is_active
        }
    }), 201

