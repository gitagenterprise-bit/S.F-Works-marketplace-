from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    get_jwt_identity
)

from sqlalchemy import func

from extensions import db

from models import (
    User,
    WorkerProfile,
    CustomerProfile,
    Job,
    JobApplication,
    Category,
    AgentProfile,
    AgentArea,
    AuditLog,
    ApprovalRecord
)

from utils.decorators import (
    admin_required
)


admin_bp = Blueprint(
    "admin",
    __name__
)


# =========================================================
# HELPERS
# =========================================================

def current_admin():

    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):

        return None

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return None

    if user.role != "admin":
        return None

    if not user.is_active:
        return None

    return user


def audit(
    actor,
    action,
    resource_type=None,
    resource_id=None,
    old_status=None,
    new_status=None,
    details=None
):

    log = AuditLog(
        actor_id=actor.id if actor else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_status=old_status,
        new_status=new_status,
        ip_address=request.remote_addr,
        user_agent=request.headers.get(
            "User-Agent"
        ),
        details=details
    )

    db.session.add(log)


def approval_record(
    actor,
    resource_type,
    resource_id,
    action,
    remarks=None
):

    record = ApprovalRecord(
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor.id,
        actor_role=actor.role,
        action=action,
        remarks=remarks
    )

    db.session.add(record)


def error_response(
    message,
    status_code=400
):

    return jsonify({
        "status": "error",
        "message": message
    }), status_code


# =========================================================
# ADMIN LOGIN
# =========================================================

@admin_bp.post("/login")
def admin_login():

    data = request.get_json(
        silent=True
    ) or {}

    email = str(
        data.get("email", "")
    ).strip().lower()

    password = str(
        data.get("password", "")
    )

    if not email or not password:

        return error_response(
            "Email and password are required.",
            400
        )

    user = User.query.filter(
        func.lower(User.email) == email
    ).first()

    if not user:

        return error_response(
            "Invalid administrator credentials.",
            401
        )

    if user.role != "admin":

        return error_response(
            "This account does not have administrator access.",
            403
        )

    if not user.is_active:

        return error_response(
            "Administrator account is inactive.",
            403
        )

    if not user.check_password(password):

        return error_response(
            "Invalid administrator credentials.",
            401
        )

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": "admin"
        }
    )

    response = jsonify({

        "status": "success",

        "message":
            "Administrator login successful.",

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

        "message":
            "Administrator logged out."

    })

    unset_jwt_cookies(
        response
    )

    return response


# =========================================================
# CURRENT ADMIN
# =========================================================

@admin_bp.get("/me")
@admin_required
def admin_me():

    admin = current_admin()

    if not admin:

        return error_response(
            "Administrator account not found.",
            401
        )

    return jsonify({

        "status": "success",

        "user": {

            "id":
                admin.id,

            "full_name":
                admin.full_name,

            "email":
                admin.email,

            "phone":
                admin.phone,

            "role":
                admin.role,

            "is_active":
                admin.is_active,

            "is_verified":
                admin.is_verified,

            "created_at":
                admin.created_at.isoformat()
                if admin.created_at
                else None
        }
    })


# =========================================================
# DASHBOARD
# =========================================================

@admin_bp.get("/dashboard")
@admin_required
def admin_dashboard():

    stats = {

        "total_users":
            User.query.count(),

        "total_customers":
            User.query.filter_by(
                role="customer"
            ).count(),

        "total_workers":
            User.query.filter_by(
                role="worker"
            ).count(),

        "total_agents":
            User.query.filter_by(
                role="agent"
            ).count(),

        "total_admins":
            User.query.filter_by(
                role="admin"
            ).count(),

        "active_users":
            User.query.filter_by(
                is_active=True
            ).count(),

        "inactive_users":
            User.query.filter_by(
                is_active=False
            ).count(),

        "pending_workers":
            WorkerProfile.query.filter_by(
                verification_status="pending"
            ).count(),

        "verified_workers":
            WorkerProfile.query.filter_by(
                verification_status="approved"
            ).count(),

        "total_jobs":
            Job.query.count(),

        "pending_jobs":
            Job.query.filter(
                Job.status.in_([
                    "pending_review",
                    "agent_review",
                    "admin_review"
                ])
            ).count(),

        "approved_jobs":
            Job.query.filter_by(
                status="approved"
            ).count(),

        "rejected_jobs":
            Job.query.filter_by(
                status="rejected"
            ).count(),

        "total_applications":
            JobApplication.query.count(),

        "pending_applications":
            JobApplication.query.filter(
                JobApplication.status.in_([
                    "pending",
                    "customer_approved",
                    "agent_review",
                    "admin_review"
                ])
            ).count(),

        "total_categories":
            Category.query.count(),

        "total_audit_logs":
            AuditLog.query.count()
    }

    return jsonify({

        "status": "success",

        "stats": stats

    })


# =========================================================
# USERS
# =========================================================

@admin_bp.get("/users")
@admin_required
def admin_users():

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
        25,
        type=int
    )

    per_page = min(
        max(per_page, 1),
        100
    )

    query = (
        User.query
        .order_by(
            User.created_at.desc()
        )
    )

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
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
                "created_at":
                    user.created_at.isoformat()
                    if user.created_at
                    else None
            }

            for user in pagination.items
        ],

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
    })


# =========================================================
# USER STATUS
# =========================================================

@admin_bp.patch(
    "/users/<int:user_id>/status"
)
@admin_required
def update_user_status(user_id):

    admin = current_admin()

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        return error_response(
            "User not found.",
            404
        )

    # Prevent admin from disabling himself.
    if user.id == admin.id:

        return error_response(
            "You cannot change your own administrator status.",
            403
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

        return error_response(
            "is_active must be boolean.",
            400
        )

    old_value = user.is_active

    user.is_active = is_active

    audit(
        admin,
        "USER_STATUS_CHANGED",
        "user",
        user.id,
        details={
            "old_is_active": old_value,
            "new_is_active": is_active
        }
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "User status updated successfully.",

        "user": {

            "id":
                user.id,

            "is_active":
                user.is_active
        }
    })


# =========================================================
# VERIFY USER
# =========================================================

@admin_bp.patch(
    "/users/<int:user_id>/verify"
)
@admin_required
def verify_user(user_id):

    admin = current_admin()

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        return error_response(
            "User not found.",
            404
        )

    user.is_verified = True

    audit(
        admin,
        "USER_VERIFIED",
        "user",
        user.id
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "User verified successfully."
    })


# =========================================================
# CREATE AGENT
# =========================================================

@admin_bp.post("/agents")
@admin_required
def create_agent():

    admin = current_admin()

    data = request.get_json(
        silent=True
    ) or {}

    full_name = str(
        data.get("full_name", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip().lower()

    phone = str(
        data.get("phone", "")
    ).strip()

    password = str(
        data.get("password", "")
    )

    employee_code = str(
        data.get("employee_code", "")
    ).strip().upper()

    designation = str(
        data.get(
            "designation",
            "Area Agent"
        )
    ).strip()

    if not full_name:
        return error_response(
            "Full name is required."
        )

    if not email:
        return error_response(
            "Email is required."
        )

    if not phone:
        return error_response(
            "Phone is required."
        )

    if len(password) < 8:
        return error_response(
            "Password must contain at least 8 characters."
        )

    if not employee_code:
        return error_response(
            "Employee code is required."
        )

    existing = User.query.filter(
        (User.email == email) |
        (User.phone == phone)
    ).first()

    if existing:

        return error_response(
            "Email or phone is already registered.",
            409
        )

    existing_code = AgentProfile.query.filter_by(
        employee_code=employee_code
    ).first()

    if existing_code:

        return error_response(
            "Employee code already exists.",
            409
        )

    try:

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            role="agent",
            is_active=True,
            is_verified=True
        )

        user.set_password(
            password
        )

        db.session.add(user)

        db.session.flush()

        agent = AgentProfile(

            user_id=user.id,

            employee_code=
                employee_code,

            designation=
                designation
                or "Area Agent",

            status="active",

            created_by=admin.id
        )

        db.session.add(agent)

        audit(
            admin,
            "AGENT_CREATED",
            "agent",
            agent.id,
            details={
                "user_id": user.id,
                "employee_code": employee_code
            }
        )

        db.session.commit()

    except Exception:

        db.session.rollback()

        return error_response(
            "Unable to create agent.",
            500
        )

    return jsonify({

        "status": "success",

        "message":
            "Agent created successfully.",

        "agent": {

            "id":
                agent.id,

            "user_id":
                user.id,

            "full_name":
                user.full_name,

            "email":
                user.email,

            "phone":
                user.phone,

            "employee_code":
                agent.employee_code,

            "designation":
                agent.designation,

            "status":
                agent.status
        }

    }), 201


# =========================================================
# AGENT LIST
# =========================================================

@admin_bp.get("/agents")
@admin_required
def admin_agents():

    agents = (
        AgentProfile.query
        .join(
            User,
            AgentProfile.user_id == User.id
        )
        .order_by(
            AgentProfile.created_at.desc()
        )
        .all()
    )

    result = []

    for agent in agents:

        result.append({

            "id":
                agent.id,

            "user_id":
                agent.user_id,

            "full_name":
                agent.user.full_name,

            "email":
                agent.user.email,

            "phone":
                agent.user.phone,

            "employee_code":
                agent.employee_code,

            "designation":
                agent.designation,

            "status":
                agent.status,

            "is_active":
                agent.user.is_active,

            "areas": [

                {
                    "id":
                        area.id,

                    "district":
                        area.district,

                    "police_station":
                        area.police_station,

                    "area":
                        area.area,

                    "pincode":
                        area.pincode,

                    "is_active":
                        area.is_active
                }

                for area in agent.areas
            ]
        })

    return jsonify({

        "status": "success",

        "agents":
            result
    })


# =========================================================
# ASSIGN AGENT AREA
# =========================================================

@admin_bp.post(
    "/agents/<int:agent_id>/areas"
)
@admin_required
def assign_agent_area(agent_id):

    admin = current_admin()

    agent = db.session.get(
        AgentProfile,
        agent_id
    )

    if not agent:

        return error_response(
            "Agent not found.",
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    district = str(
        data.get("district", "")
    ).strip() or None

    police_station = str(
        data.get("police_station", "")
    ).strip() or None

    area = str(
        data.get("area", "")
    ).strip() or None

    pincode = str(
        data.get("pincode", "")
    ).strip() or None

    if not any([
        district,
        police_station,
        area,
        pincode
    ]):

        return error_response(
            "At least one area scope is required.",
            400
        )

    existing = AgentArea.query.filter_by(
        agent_id=agent.id,
        district=district,
        police_station=police_station,
        area=area,
        pincode=pincode
    ).first()

    if existing:

        return error_response(
            "This area is already assigned to the agent.",
            409
        )

    assigned_area = AgentArea(

        agent_id=agent.id,

        district=district,

        police_station=
            police_station,

        area=area,

        pincode=pincode,

        is_active=True
    )

    db.session.add(
        assigned_area
    )

    audit(
        admin,
        "AGENT_AREA_ASSIGNED",
        "agent_area",
        assigned_area.id,
        details={
            "agent_id": agent.id,
            "district": district,
            "police_station": police_station,
            "area": area,
            "pincode": pincode
        }
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Area assigned successfully.",

        "area": {

            "id":
                assigned_area.id,

            "district":
                assigned_area.district,

            "police_station":
                assigned_area.police_station,

            "area":
                assigned_area.area,

            "pincode":
                assigned_area.pincode
        }
    }), 201


# =========================================================
# REMOVE AGENT AREA
# =========================================================

@admin_bp.delete(
    "/agents/<int:agent_id>/areas/<int:area_id>"
)
@admin_required
def remove_agent_area(
    agent_id,
    area_id
):

    admin = current_admin()

    area = db.session.get(
        AgentArea,
        area_id
    )

    if not area:

        return error_response(
            "Assigned area not found.",
            404
        )

    if area.agent_id != agent_id:

        return error_response(
            "Area does not belong to this agent.",
            403
        )

    area.is_active = False

    audit(
        admin,
        "AGENT_AREA_DEACTIVATED",
        "agent_area",
        area.id
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Agent area deactivated successfully."
    })


# =========================================================
# AGENT STATUS
# =========================================================

@admin_bp.patch(
    "/agents/<int:agent_id>/status"
)
@admin_required
def update_agent_status(agent_id):

    admin = current_admin()

    agent = db.session.get(
        AgentProfile,
        agent_id
    )

    if not agent:

        return error_response(
            "Agent not found.",
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    status = str(
        data.get("status", "")
    ).strip().lower()

    if status not in {
        "active",
        "suspended"
    }:

        return error_response(
            "Invalid agent status.",
            400
        )

    old_status = agent.status

    agent.status = status

    agent.user.is_active = (
        status == "active"
    )

    audit(
        admin,
        "AGENT_STATUS_CHANGED",
        "agent",
        agent.id,
        old_status=old_status,
        new_status=status
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Agent status updated.",

        "agent": {

            "id":
                agent.id,

            "status":
                agent.status,

            "is_active":
                agent.user.is_active
        }
    })


# =========================================================
# JOB LIST
# =========================================================

@admin_bp.get("/jobs")
@admin_required
def admin_jobs():

    page = max(
        request.args.get(
            "page",
            1,
            type=int
        ),
        1
    )

    per_page = min(
        max(
            request.args.get(
                "per_page",
                25,
                type=int
            ),
            1
        ),
        100
    )

    status = request.args.get(
        "status"
    )

    query = Job.query

    if status:

        query = query.filter(
            Job.status == status
        )

    pagination = (
        query
        .order_by(
            Job.created_at.desc()
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
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

            "status":
                job.status,

            "priority":
                job.priority,

            "is_featured":
                job.is_featured,

            "views":
                job.views,

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

            "location":
                job.location,

            "city":
                job.city,

            "state":
                job.state,

            "pincode":
                job.pincode,

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

            "customer": {

                "id":
                    job.customer.id
                    if job.customer
                    else None,

                "name":
                    job.customer.full_name
                    if job.customer
                    else None,

                "email":
                    job.customer.email
                    if job.customer
                    else None
            },

            "created_at":
                job.created_at.isoformat()
                if job.created_at
                else None
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
    })


# =========================================================
# FINAL JOB APPROVAL
# =========================================================

@admin_bp.patch(
    "/jobs/<int:job_id>/approval"
)
@admin_required
def admin_job_approval(job_id):

    admin = current_admin()

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return error_response(
            "Job not found.",
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    action = str(
        data.get("action", "")
    ).strip().lower()

    remarks = str(
        data.get("remarks", "")
    ).strip() or None

    if action not in {
        "approve",
        "reject"
    }:

        return error_response(
            "Action must be approve or reject.",
            400
        )

    old_status = job.status

    if action == "approve":

        job.status = "approved"

        approval_action = "approved"

    else:

        job.status = "rejected"

        approval_action = "rejected"

    approval_record(
        admin,
        "job",
        job.id,
        approval_action,
        remarks
    )

    audit(
        admin,
        "JOB_FINAL_APPROVAL",
        "job",
        job.id,
        old_status=old_status,
        new_status=job.status,
        details={
            "remarks": remarks
        }
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Job approval status updated.",

        "job": {

            "id":
                job.id,

            "status":
                job.status
        }
    })


# =========================================================
# JOB SOFT DELETE
# =========================================================

@admin_bp.delete(
    "/jobs/<int:job_id>"
)
@admin_required
def delete_job(job_id):

    admin = current_admin()

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return error_response(
            "Job not found.",
            404
        )

    old_status = job.status

    # Do NOT physically delete the job.
    job.status = "deleted"

    audit(
        admin,
        "JOB_SOFT_DELETED",
        "job",
        job.id,
        old_status=old_status,
        new_status="deleted"
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Job removed successfully."
    })


# =========================================================
# APPLICATIONS
# =========================================================

@admin_bp.get("/applications")
@admin_required
def admin_applications():

    page = max(
        request.args.get(
            "page",
            1,
            type=int
        ),
        1
    )

    per_page = min(
        max(
            request.args.get(
                "per_page",
                25,
                type=int
            ),
            1
        ),
        100
    )

    status = request.args.get(
        "status"
    )

    query = JobApplication.query

    if status:

        query = query.filter(
            JobApplication.status == status
        )

    pagination = (
        query
        .order_by(
            JobApplication.created_at.desc()
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    applications = []

    for application in pagination.items:

        applications.append({

            "id":
                application.id,

            "job_id":
                application.job_id,

            "job_title":
                application.job.title
                if application.job
                else None,

            "worker_id":
                application.worker_id,

            "worker_name":
                application.worker.full_name
                if application.worker
                else None,

            "proposed_amount":
                float(
                    application.proposed_amount
                )
                if application.proposed_amount is not None
                else None,

            "message":
                application.message,

            "availability":
                application.availability,

            "status":
                application.status,

            "created_at":
                application.created_at.isoformat()
                if application.created_at
                else None
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
    })


# =========================================================
# FINAL APPLICATION APPROVAL
# =========================================================

@admin_bp.patch(
    "/applications/<int:application_id>/approval"
)
@admin_required
def admin_application_approval(
    application_id
):

    admin = current_admin()

    application = db.session.get(
        JobApplication,
        application_id
    )

    if not application:

        return error_response(
            "Application not found.",
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    action = str(
        data.get("action", "")
    ).strip().lower()

    remarks = str(
        data.get("remarks", "")
    ).strip() or None

    if action not in {
        "approve",
        "reject"
    }:

        return error_response(
            "Action must be approve or reject.",
            400
        )

    old_status = application.status

    if action == "approve":

        application.status = "hired"

    else:

        application.status = "rejected"

    approval_record(
        admin,
        "job_application",
        application.id,
        action,
        remarks
    )

    audit(
        admin,
        "APPLICATION_FINAL_APPROVAL",
        "job_application",
        application.id,
        old_status=old_status,
        new_status=application.status,
        details={
            "remarks": remarks
        }
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Application final status updated.",

        "application": {

            "id":
                application.id,

            "status":
                application.status
        }
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

    admin = current_admin()

    worker = db.session.get(
        WorkerProfile,
        worker_id
    )

    if not worker:

        return error_response(
            "Worker profile not found.",
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    status = str(
        data.get(
            "status",
            ""
        )
    ).strip().lower()

    if status not in {
        "pending",
        "approved",
        "rejected"
    }:

        return error_response(
            "Invalid verification status.",
            400
        )

    old_status = worker.verification_status

    worker.verification_status = status

    worker.is_verified = (
        status == "approved"
    )

    audit(
        admin,
        "WORKER_VERIFICATION_CHANGED",
        "worker",
        worker.id,
        old_status=old_status,
        new_status=status
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
                "id":
                    category.id,

                "name":
                    category.name,

                "slug":
                    category.slug,

                "description":
                    category.description,

                "icon":
                    category.icon,

                "image":
                    category.image,

                "is_active":
                    category.is_active
            }

            for category in categories
        ]
    })


# =========================================================
# AUDIT LOGS
# =========================================================

@admin_bp.get("/audit-logs")
@admin_required
def admin_audit_logs():

    page = max(
        request.args.get(
            "page",
            1,
            type=int
        ),
        1
    )

    per_page = min(
        max(
            request.args.get(
                "per_page",
                50,
                type=int
            ),
            1
        ),
        100
    )

    pagination = (
        AuditLog.query
        .order_by(
            AuditLog.created_at.desc()
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({

        "status": "success",

        "logs": [

            {
                "id":
                    log.id,

                "actor_id":
                    log.actor_id,

                "action":
                    log.action,

                "resource_type":
                    log.resource_type,

                "resource_id":
                    log.resource_id,

                "old_status":
                    log.old_status,

                "new_status":
                    log.new_status,

                "ip_address":
                    log.ip_address,

                "details":
                    log.details,

                "created_at":
                    log.created_at.isoformat()
                    if log.created_at
                    else None
            }

            for log in pagination.items
        ],

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
    })
