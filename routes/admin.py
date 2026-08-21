from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)

from extensions import db

from models import (
    User,
    WorkerProfile,
    CustomerProfile,
    Job,
    JobApplication,
    Category
)

from utils.admin_security import admin_required


admin_bp = Blueprint(
    "admin",
    __name__
)


# =========================================================
# ADMIN LOGIN
# =========================================================

@admin_bp.post("/login")
def admin_login():

    data = request.get_json(
        silent=True
    ) or {}

    email = (
        str(data.get("email", ""))
        .strip()
        .lower()
    )

    password = str(
        data.get("password", "")
    )

    if not email or not password:

        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:

        return jsonify({
            "status": "error",
            "message": "Invalid administrator credentials."
        }), 401

    if user.role != "admin":

        return jsonify({
            "status": "error",
            "message": "This account does not have administrator access."
        }), 403

    if not user.is_active:

        return jsonify({
            "status": "error",
            "message": "Administrator account is inactive."
        }), 403

    if not user.check_password(password):

        return jsonify({
            "status": "error",
            "message": "Invalid administrator credentials."
        }), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": "admin"
        }
    )

    response = jsonify({
        "status": "success",
        "message": "Administrator login successful.",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    })

    set_access_cookies(
        response,
        access_token
    )

    return response


# =========================================================
# ADMIN LOGOUT
# =========================================================

@admin_bp.post("/logout")
@admin_required
def admin_logout():

    response = jsonify({
        "status": "success",
        "message": "Administrator logged out."
    })

    unset_jwt_cookies(response)

    return response


# =========================================================
# CURRENT ADMIN
# =========================================================

@admin_bp.get("/me")
@admin_required
def admin_me():

    from flask_jwt_extended import get_jwt_identity

    user = User.query.get(
        get_jwt_identity()
    )

    return jsonify({
        "status": "success",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at
                else None
            )
        }
    })


# =========================================================
# DASHBOARD STATS
# =========================================================

@admin_bp.get("/dashboard")
@admin_required
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

    active_users = User.query.filter_by(
        is_active=True
    ).count()

    inactive_users = User.query.filter_by(
        is_active=False
    ).count()

    pending_workers = WorkerProfile.query.filter_by(
        verification_status="pending"
    ).count()

    verified_workers = WorkerProfile.query.filter_by(
        verification_status="approved"
    ).count()

    total_jobs = Job.query.count()

    total_applications = JobApplication.query.count()

    total_categories = Category.query.count()

    return jsonify({

        "status": "success",

        "stats": {

            "total_users": total_users,

            "total_customers": total_customers,

            "total_workers": total_workers,

            "total_admins": total_admins,

            "active_users": active_users,

            "inactive_users": inactive_users,

            "pending_workers": pending_workers,

            "verified_workers": verified_workers,

            "total_jobs": total_jobs,

            "total_applications":
                total_applications,

            "total_categories":
                total_categories
        }
    })


# =========================================================
# USERS
# =========================================================

@admin_bp.get("/users")
@admin_required
def admin_users():

    users = (
        User.query
        .order_by(
            User.created_at.desc()
        )
        .limit(100)
        .all()
    )

    return jsonify({

        "status": "success",

        "users": [

            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                )
            }

            for user in users
        ]
    })


# =========================================================
# ACTIVATE / DEACTIVATE USER
# =========================================================

@admin_bp.patch("/users/<int:user_id>/status")
@admin_required
def update_user_status(user_id):

    user = User.query.get_or_404(
        user_id
    )

    data = request.get_json(
        silent=True
    ) or {}

    is_active = data.get(
        "is_active"
    )

    if not isinstance(
        is_active,
        bool
    ):

        return jsonify({
            "status": "error",
            "message": "is_active must be boolean."
        }), 400

    user.is_active = is_active

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "User status updated successfully.",

        "user": {
            "id": user.id,
            "is_active": user.is_active
        }
    })


# =========================================================
# VERIFY USER
# =========================================================

@admin_bp.patch("/users/<int:user_id>/verify")
@admin_required
def verify_user(user_id):

    user = User.query.get_or_404(
        user_id
    )

    user.is_verified = True

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "User verified successfully."
    })


# =========================================================
# WORKER VERIFICATION
# =========================================================

@admin_bp.patch(
    "/workers/<int:worker_id>/verification"
)
@admin_required
def update_worker_verification(
    worker_id
):

    worker = WorkerProfile.query.get_or_404(
        worker_id
    )

    data = request.get_json(
        silent=True
    ) or {}

    status = str(
        data.get(
            "status",
            ""
        )
    ).lower().strip()

    allowed = {
        "pending",
        "approved",
        "rejected"
    }

    if status not in allowed:

        return jsonify({
            "status": "error",
            "message":
                "Invalid verification status."
        }), 400

    worker.verification_status = status

    worker.is_verified = (
        status == "approved"
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Worker verification updated.",

        "verification_status":
            worker.verification_status,

        "is_verified":
            worker.is_verified
    })


# =========================================================
# JOBS
# =========================================================

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
        25,
        type=int
    )


    if per_page < 1:

        per_page = 25


    if per_page > 100:

        per_page = 100


    query = (
        Job.query
        .join(
            User,
            Job.customer_id == User.id
        )
        .order_by(
            Job.created_at.desc()
        )
    )


    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


    jobs = []


    for job in pagination.items:

        user = db.session.get(
            User,
            job.customer_id
        )


        jobs.append({

            "id": job.id,

            "title": job.title,

            "description": job.description,

            "status": job.status,

            "priority": job.priority,

            "is_featured": job.is_featured,

            "views": job.views,

            "budget": {

                "min":
                    float(job.budget_min)
                    if job.budget_min is not None
                    else None,

                "max":
                    float(job.budget_max)
                    if job.budget_max is not None
                    else None
            },

            "location": job.location,

            "city": job.city,

            "state": job.state,

            "pincode": job.pincode,

            "category": {

                "id":
                    job.category.id
                    if job.category
                    else None,

                "name":
                    job.category.name
                    if job.category
                    else None
            },

            "posted_by": {

                "id":
                    user.id
                    if user
                    else None,

                "name":
                    user.full_name
                    if user
                    else "Unknown",

                "phone":
                    user.phone
                    if user
                    else None,

                "email":
                    user.email
                    if user
                    else None,

                "role":
                    user.role
                    if user
                    else None
            },

            "created_at":
                job.created_at.isoformat()
                if job.created_at
                else None
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



# =========================================================
# CATEGORIES
# =========================================================

@admin_bp.get("/categories")
@admin_required
def admin_categories():

    categories = (
        Category.query
        .order_by(
            Category.id.desc()
        )
        .all()
    )

    return jsonify({

        "status": "success",

        "categories": [

            {
                "id": category.id,

                "name":
                    getattr(
                        category,
                        "name",
                        ""
                    )
            }

            for category in categories
        ]
    })
