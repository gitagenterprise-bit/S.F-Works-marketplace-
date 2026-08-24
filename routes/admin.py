from secrets import token_urlsafe

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

from sqlalchemy import (
    func,
    or_
)

from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)

from extensions import db

from models import (
    User,
    WorkerProfile,
    Job,
    JobApplication,
    Category,

    AgentProfile,
    AgentArea,
    AgentAreaAssignment,
    AgentPermission,

    AuditLog,
    ApprovalRecord
)

from utils.decorators import (
    admin_required
)


# =========================================================
# ADMIN BLUEPRINT
# =========================================================

admin_bp = Blueprint(
    "admin",
    __name__
)


# =========================================================
# CONSTANTS
# =========================================================

DEFAULT_AGENT_PERMISSIONS = [

    "jobs.view",
    "jobs.review",

    "applications.view",
    "applications.review",

    "workers.view",
    "workers.review",

    "customers.view",

    "doctors.view",
    "chambers.view",

    "bookings.view",
    "bookings.review"
]


# =========================================================
# STANDARD ERROR RESPONSE
# =========================================================

def error_response(
    message,
    status_code=400
):

    return jsonify({
        "status": "error",
        "message": message
    }), status_code


# =========================================================
# CURRENT ADMIN
# =========================================================

def current_admin():

    identity = get_jwt_identity()

    try:
        user_id = int(identity)

    except (
        TypeError,
        ValueError
    ):
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


# =========================================================
# AUDIT LOG
# =========================================================

# =========================================================
# AUDIT LOG
# =========================================================

def write_audit_log(
    actor=None,
    action=None,
    resource_type=None,
    resource_id=None,
    old_status=None,
    new_status=None,
    description=None,
    details=None
):

    if actor is None:
        actor = current_admin()

    # -----------------------------------------------------
    # Build audit description
    # -----------------------------------------------------

    parts = []

    if description:
        parts.append(
            str(description)
        )

    if old_status is not None:
        parts.append(
            f"Old status: {old_status}"
        )

    if new_status is not None:
        parts.append(
            f"New status: {new_status}"
        )

    if details:
        try:
            import json

            details_text = json.dumps(
                details,
                ensure_ascii=False,
                default=str
            )

            parts.append(
                f"Details: {details_text}"
            )

        except Exception:
            parts.append(
                f"Details: {str(details)}"
            )

    final_description = "\n".join(
        parts
    ) or None

    # -----------------------------------------------------
    # Create AuditLog
    # -----------------------------------------------------

    log = AuditLog(

        actor_id=(
            actor.id
            if actor
            else None
        ),

        action=action,

        entity_type=resource_type,

        entity_id=resource_id,

        description=final_description,

        ip_address=(
            request.headers.get(
                "X-Forwarded-For",
                request.remote_addr
            ).split(",")[0].strip()
            if request.headers.get(
                "X-Forwarded-For"
            )
            else request.remote_addr
        ),

        user_agent=(
            request.headers.get(
                "User-Agent"
            )
        )
    )

    db.session.add(log)

    return log

# =========================================================
# APPROVAL RECORD
# =========================================================

def create_approval_record(
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

    return record


# =========================================================
# GENERATE UNIQUE EMPLOYEE CODE
# =========================================================

def generate_employee_code():

    for _ in range(20):

        code = (
            "AG-"
            + token_urlsafe(6)
            .replace("-", "")
            .replace("_", "")
            .upper()
        )

        existing = (
            AgentProfile.query
            .filter_by(
                employee_code=code
            )
            .first()
        )

        if not existing:
            return code

    raise RuntimeError(
        "Unable to generate unique agent employee code."
    )


# =========================================================
# NORMALIZE AREA
# =========================================================

def normalize_area(item):

    if not isinstance(
        item,
        dict
    ):
        raise ValueError(
            "Each area must be an object."
        )

    name = str(
        item.get(
            "name",
            ""
        )
    ).strip()

    area_type = str(
        item.get(
            "area_type",
            "locality"
        )
    ).strip().lower()

    district = (
        str(
            item.get(
                "district",
                ""
            )
        ).strip()
        or None
    )

    police_station = (
        str(
            item.get(
                "police_station",
                ""
            )
        ).strip()
        or None
    )

    locality = (
        str(
            item.get(
                "locality",
                ""
            )
        ).strip()
        or None
    )

    pincode = (
        str(
            item.get(
                "pincode",
                ""
            )
        ).strip()
        or None
    )

    state = (
        str(
            item.get(
                "state",
                ""
            )
        ).strip()
        or None
    )

    if not name:

        # Backward compatibility:
        # allow "area" from old frontend payload.

        name = (
            locality
            or police_station
            or district
        )

    if not name:

        raise ValueError(
            "Area name is required."
        )

    if not area_type:

        raise ValueError(
            "Area type is required."
        )

    if pincode:

        if (
            not pincode.isdigit()
            or len(pincode) != 6
        ):

            raise ValueError(
                "Pincode must contain exactly 6 digits."
            )

    return {

        "name":
            name,

        "area_type":
            area_type,

        "district":
            district,

        "police_station":
            police_station,

        "locality":
            locality,

        "pincode":
            pincode,

        "state":
            state
    }


# =========================================================
# FIND OR CREATE AREA
# =========================================================

def get_or_create_area(
    normalized
):

    area = (
        AgentArea.query
        .filter_by(

            name=
                normalized["name"],

            area_type=
                normalized["area_type"],

            district=
                normalized["district"],

            police_station=
                normalized["police_station"],

            locality=
                normalized["locality"],

            pincode=
                normalized["pincode"]
        )
        .first()
    )

    if area:

        if not area.is_active:
            area.is_active = True

        return area

    area = AgentArea(

        name=
            normalized["name"],

        area_type=
            normalized["area_type"],

        district=
            normalized["district"],

        police_station=
            normalized["police_station"],

        locality=
            normalized["locality"],

        pincode=
            normalized["pincode"],

        state=
            normalized["state"],

        is_active=True
    )

    db.session.add(area)

    db.session.flush()

    return area


# =========================================================
# SERIALIZE AREA
# =========================================================

def serialize_area(
    area,
    assignment=None
):

    return {

        "id":
            area.id,

        "name":
            area.name,

        "area_type":
            area.area_type,

        "district":
            area.district,

        "police_station":
            area.police_station,

        "locality":
            area.locality,

        "pincode":
            area.pincode,

        "state":
            area.state,

        "is_active":
            (
                assignment.is_active
                if assignment
                else area.is_active
            ),

        "assignment_id":
            (
                assignment.id
                if assignment
                else None
            )
    }


# =========================================================
# SERIALIZE AGENT
# =========================================================

def serialize_agent(
    agent,
    include_permissions=True
):

    user = agent.user

    areas = []

    for assignment in agent.areas:

        if not assignment.area:
            continue

        areas.append(
            serialize_area(
                assignment.area,
                assignment
            )
        )

    data = {

        "id":
            agent.id,

        "employee_code":
            agent.employee_code,

        "designation":
            agent.designation,

        "is_verified":
            agent.is_verified,

        "verification_status":
            agent.verification_status,

        "force_password_change":
            agent.force_password_change,

        "last_login_at": (

            agent.last_login_at.isoformat()

            if agent.last_login_at

            else None
        ),

        "created_at": (

            agent.created_at.isoformat()

            if agent.created_at

            else None
        ),

        "updated_at": (

            agent.updated_at.isoformat()

            if agent.updated_at

            else None
        ),

        "user": {

            "id":
                user.id
                if user
                else None,

            "full_name":
                user.full_name
                if user
                else None,

            "email":
                user.email
                if user
                else None,

            "phone":
                user.phone
                if user
                else None,

            "role":
                user.role
                if user
                else None,

            "is_active":
                user.is_active
                if user
                else False,

            "is_verified":
                user.is_verified
                if user
                else False
        },

        "areas":
            areas
    }

    if include_permissions:

        data["permissions"] = [

            {
                "id":
                    permission.id,

                "permission":
                    permission.permission,

                "is_allowed":
                    permission.is_allowed
            }

            for permission
            in agent.permissions
        ]

    return data


# =========================================================
# ADMIN LOGIN
# POST /api/admin/login
# =========================================================

@admin_bp.post("/login")
def admin_login():

    data = request.get_json(
        silent=True
    ) or {}

    email = str(
        data.get(
            "email",
            ""
        )
    ).strip().lower()

    password = str(
        data.get(
            "password",
            ""
        )
    )

    if not email or not password:

        return error_response(
            "Email and password are required.",
            400
        )

    user = (
        User.query
        .filter(
            func.lower(
                User.email
            ) == email
        )
        .first()
    )

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

    if not user.check_password(
        password
    ):

        return error_response(
            "Invalid administrator credentials.",
            401
        )

    access_token = create_access_token(

        identity=str(
            user.id
        ),

        additional_claims={
            "role": "admin"
        }
    )

    response = jsonify({

        "status":
            "success",

        "message":
            "Administrator login successful.",

        "user": {

            "id":
                user.id,

            "full_name":
                user.full_name,

            "email":
                user.email,

            "role":
                user.role
        }
    })

    set_access_cookies(
        response,
        access_token
    )

    return response


# =========================================================
# ADMIN LOGOUT
# POST /api/admin/logout
# =========================================================

@admin_bp.post("/logout")
@admin_required
def admin_logout():

    response = jsonify({

        "status":
            "success",

        "message":
            "Administrator logged out."
    })

    unset_jwt_cookies(
        response
    )

    return response


# =========================================================
# ADMIN ME
# GET /api/admin/me
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

        "status":
            "success",

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

            "created_at": (

                admin.created_at.isoformat()

                if admin.created_at

                else None
            )
        }
    })


# =========================================================
# DASHBOARD
# GET /api/admin/dashboard
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

        "status":
            "success",

        "stats":
            stats
    })


# =========================================================
# USERS
# GET /api/admin/users
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

    pagination = (
        User.query
        .order_by(
            User.created_at.desc()
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({

        "status":
            "success",

        "users": [

            {
                "id":
                    user.id,

                "full_name":
                    user.full_name,

                "email":
                    user.email,

                "phone":
                    user.phone,

                "role":
                    user.role,

                "is_active":
                    user.is_active,

                "is_verified":
                    user.is_verified,

                "created_at": (

                    user.created_at.isoformat()

                    if user.created_at

                    else None
                )
            }

            for user
            in pagination.items
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
# PATCH /api/admin/users/<id>/status
# =========================================================

@admin_bp.patch(
    "/users/<int:user_id>/status"
)
@admin_required
def update_user_status(
    user_id
):

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

    if old_value == is_active:

        return jsonify({

            "status":
                "success",

            "message":
                "User status is already up to date.",

            "user": {

                "id":
                    user.id,

                "is_active":
                    user.is_active
            }
        })

    user.is_active = is_active

    write_audit_log(

        actor=admin,

        action=(
            "user.activated"
            if is_active
            else "user.suspended"
        ),

        resource_type="user",

        resource_id=user.id,

        old_status=str(
            old_value
        ),

        new_status=str(
            is_active
        )
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to update user status.",
            500
        )

    return jsonify({

        "status":
            "success",

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
# PATCH /api/admin/users/<id>/verify
# =========================================================

@admin_bp.patch(
    "/users/<int:user_id>/verify"
)
@admin_required
def verify_user(user_id):

    admin = current_admin()

    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        return error_response(
            "User not found.",
            404
        )

    # -----------------------------------------------------
    # ALREADY VERIFIED
    # -----------------------------------------------------

    if user.is_verified:

        return jsonify({

            "status":
                "success",

            "message":
                "User is already verified."
        })

    # -----------------------------------------------------
    # VERIFY USER
    # -----------------------------------------------------

    user.is_verified = True

    # -----------------------------------------------------
    # VERIFY WORKER PROFILE
    # -----------------------------------------------------

    worker = user.worker_profile

    if worker:

        worker.is_verified = True

        worker.verification_status = (
            "approved"
        )

    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    write_audit_log(

        actor=admin,

        action="user.verified",

        resource_type="user",

        resource_id=user.id
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to verify user.",
            500
        )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "status":
            "success",

        "message":
            "User verified successfully.",

        "user": {

            "id":
                user.id,

            "is_verified":
                user.is_verified
        },

        "worker": (

            {

                "id":
                    worker.id,

                "is_verified":
                    worker.is_verified,

                "verification_status":
                    worker.verification_status
            }

            if worker
            else None
        )
    })
# =========================================================
# CREATE AGENT
# POST /api/admin/agents
# =========================================================

@admin_bp.post("/agents")
@admin_required
def create_agent():

    admin = current_admin()

    if not admin:

        return error_response(
            "Administrator account not found.",
            401
        )

    data = request.get_json(
        silent=True
    ) or {}

    full_name = str(
        data.get(
            "full_name",
            ""
        )
    ).strip()

    email = str(
        data.get(
            "email",
            ""
        )
    ).strip().lower()

    phone = str(
        data.get(
            "phone",
            ""
        )
    ).strip()

    password = str(
        data.get(
            "password",
            ""
        )
    )

    designation = str(
        data.get(
            "designation",
            ""
        )
    ).strip()

    areas = data.get(
        "areas",
        []
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not full_name:

        return error_response(
            "Full name is required.",
            400
        )

    if len(full_name) > 150:

        return error_response(
            "Full name is too long.",
            400
        )

    if not email:

        return error_response(
            "Email is required.",
            400
        )

    if not phone:

        return error_response(
            "Phone is required.",
            400
        )

    if len(password) < 10:

        return error_response(
            "Password must contain at least 10 characters.",
            400
        )

    if not isinstance(
        areas,
        list
    ):

        return error_response(
            "Areas must be an array.",
            400
        )

    if len(areas) > 100:

        return error_response(
            "Maximum 100 service areas can be assigned at once.",
            400
        )

    # -----------------------------------------------------
    # NORMALIZE AREAS
    # -----------------------------------------------------

    normalized_areas = []
    area_keys = set()

    try:

        for item in areas:

            normalized = normalize_area(
                item
            )

            key = (

                normalized["name"].lower(),

                normalized["area_type"].lower(),

                (
                    normalized["district"]
                    or ""
                ).lower(),

                (
                    normalized["police_station"]
                    or ""
                ).lower(),

                (
                    normalized["locality"]
                    or ""
                ).lower(),

                normalized["pincode"]
                or ""
            )

            if key in area_keys:

                return error_response(
                    "Duplicate service area provided.",
                    409
                )

            area_keys.add(key)

            normalized_areas.append(
                normalized
            )

    except ValueError as exc:

        return error_response(
            str(exc),
            400
        )

    # -----------------------------------------------------
    # DUPLICATE USER
    # -----------------------------------------------------

    existing = (
        User.query
        .filter(
            or_(
                func.lower(
                    User.email
                ) == email,

                User.phone == phone
            )
        )
        .first()
    )

    if existing:

        return error_response(
            "Email or phone already exists.",
            409
        )

    # -----------------------------------------------------
    # TRANSACTION
    # -----------------------------------------------------

    try:

        # -------------------------------------------------
        # USER
        # -------------------------------------------------

        user = User(

            full_name=
                full_name,

            email=
                email,

            phone=
                phone,

            role=
                "agent",

            is_active=
                True,

            is_verified=
                True
        )

        user.set_password(
            password
        )

        db.session.add(
            user
        )

        db.session.flush()

        # -------------------------------------------------
        # AGENT PROFILE
        # -------------------------------------------------

        agent = AgentProfile(

            user_id=
                user.id,

            employee_code=
                generate_employee_code(),

            designation=(
                designation
                or "Area Agent"
            ),

            is_verified=
                True,

            verification_status=
                "approved",

            force_password_change=
                True,

            created_by=
                admin.id
        )

        db.session.add(
            agent
        )

        db.session.flush()

        # -------------------------------------------------
        # AREAS
        # -------------------------------------------------

        for normalized in normalized_areas:

            area = get_or_create_area(
                normalized
            )

            existing_assignment = (
                AgentAreaAssignment.query
                .filter_by(

                    agent_id=
                        agent.id,

                    area_id=
                        area.id
                )
                .first()
            )

            if existing_assignment:

                existing_assignment.is_active = True

            else:

                assignment = AgentAreaAssignment(

                    agent_id=
                        agent.id,

                    area_id=
                        area.id,

                    assigned_by=
                        admin.id,

                    is_active=
                        True
                )

                db.session.add(
                    assignment
                )

        # -------------------------------------------------
        # DEFAULT PERMISSIONS
        # -------------------------------------------------

        for permission_name in (
            DEFAULT_AGENT_PERMISSIONS
        ):

            db.session.add(
                AgentPermission(

                    agent_id=
                        agent.id,

                    permission=
                        permission_name,

                    is_allowed=
                        True,

                    granted_by=
                        admin.id
                )
            )

        # -------------------------------------------------
        # AUDIT
        # -------------------------------------------------
        write_audit_log(

            actor=admin,

            action=
                "agent.created",

            resource_type=
                "agent",

            resource_id=
                agent.id,

            new_status=
                "active",

            description=(
                f"Agent "
                f"{agent.employee_code} "
                f"created by administrator."
            ),

            details={

                "employee_code":
                    agent.employee_code,

                "user_id":
                    user.id,

                "areas_count":
                    len(
                        normalized_areas
                    )
            }
    )
        # -------------------------------------------------
        # COMMIT
        # -------------------------------------------------

        db.session.commit()

    except IntegrityError:

        db.session.rollback()

        return error_response(
            "Unable to create agent. Email, phone, employee code, or another unique value already exists.",
            409
        )

    except SQLAlchemyError as exc:

        db.session.rollback()

        return error_response(
            "Unable to create agent.",
            500
        )

    except Exception as exc:

        db.session.rollback()

        return error_response(
            "Unexpected error while creating agent.",
            500
        )

    # -----------------------------------------------------
    # SUCCESS RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "status":
            "success",

        "message":
            "Agent created successfully.",

        "agent":
            serialize_agent(
                agent
            )
    }), 201
# =========================================================
# AGENT LIST
# GET /api/admin/agents
# =========================================================

@admin_bp.get("/agents")
@admin_required
def admin_agents():

    agents = (
        AgentProfile.query
        .order_by(
            AgentProfile.created_at.desc()
        )
        .all()
    )

    return jsonify({

        "status":
            "success",

        "agents": [

            serialize_agent(
                agent
            )

            for agent
            in agents
        ]
    })


# =========================================================
# AGENT STATUS
# PATCH /api/admin/agents/<id>/status
# =========================================================

@admin_bp.patch(
    "/agents/<int:agent_id>/status"
)
@admin_required
def update_agent_status(
    agent_id
):

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

    user = agent.user

    if not user:

        return error_response(
            "Agent user account not found.",
            500
        )

    old_status = user.is_active

    if old_status == is_active:

        return jsonify({

            "status":
                "success",

            "message":
                "Agent status is already up to date.",

            "agent": {

                "id":
                    agent.id,

                "employee_code":
                    agent.employee_code,

                "is_active":
                    user.is_active
            }
        })

    user.is_active = is_active

    write_audit_log(

        actor=admin,

        action=(
            "agent.activated"
            if is_active
            else "agent.suspended"
        ),

        resource_type=
            "agent",

        resource_id=
            agent.id,

        old_status=(
            "active"
            if old_status
            else "suspended"
        ),

        new_status=(
            "active"
            if is_active
            else "suspended"
        )
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to update agent status.",
            500
        )

    return jsonify({

        "status":
            "success",

        "message":
            "Agent status updated successfully.",

        "agent": {

            "id":
                agent.id,

            "employee_code":
                agent.employee_code,

            "is_active":
                user.is_active
        }
    })


# =========================================================
# ADD AGENT AREA
# POST /api/admin/agents/<id>/areas
# =========================================================

@admin_bp.post(
    "/agents/<int:agent_id>/areas"
)
@admin_required
def add_agent_area(
    agent_id
):

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

    try:

        normalized = normalize_area(
            data
        )

    except ValueError as exc:

        return error_response(
            str(exc),
            400
        )

    try:

        area = get_or_create_area(
            normalized
        )

        assignment = (
            AgentAreaAssignment.query
            .filter_by(

                agent_id=
                    agent.id,

                area_id=
                    area.id
            )
            .first()
        )

        if assignment:

            if assignment.is_active:

                return error_response(
                    "This area is already assigned to this agent.",
                    409
                )

            assignment.is_active = True
            assignment.assigned_by = admin.id

            action = (
                "agent.area_reactivated"
            )

            message = (
                "Previously assigned area reactivated."
            )

        else:

            assignment = AgentAreaAssignment(

                agent_id=
                    agent.id,

                area_id=
                    area.id,

                assigned_by=
                    admin.id,

                is_active=
                    True
            )

            db.session.add(
                assignment
            )

            action = (
                "agent.area_added"
            )

            message = (
                "Agent area assigned successfully."
            )

        db.session.flush()

        write_audit_log(

            actor=admin,

            action=action,

            resource_type=
                "agent_area_assignment",

            resource_id=
                assignment.id,

            new_status=
                "active",

            details={

                "agent_id":
                    agent.id,

                "area_id":
                    area.id,

                "district":
                    area.district,

                "police_station":
                    area.police_station,

                "locality":
                    area.locality,

                "pincode":
                    area.pincode
            }
        )

        db.session.commit()

    except IntegrityError:

        db.session.rollback()

        return error_response(
            "This area is already assigned to this agent.",
            409
        )

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to assign agent area.",
            500
        )

    return jsonify({

        "status":
            "success",

        "message":
            message,

        "area":
            serialize_area(
                area,
                assignment
            )
    }), 201


# =========================================================
# AGENT AREA STATUS
# PATCH /api/admin/agents/<agent_id>/areas/<area_id>/status
# =========================================================

@admin_bp.patch(
    "/agents/<int:agent_id>/areas/<int:area_id>/status"
)
@admin_required
def update_agent_area_status(
    agent_id,
    area_id
):

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

    assignment = (
        AgentAreaAssignment.query
        .filter_by(

            agent_id=
                agent.id,

            area_id=
                area_id
        )
        .first()
    )

    if not assignment:

        return error_response(
            "Agent area assignment not found.",
            404
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

    if assignment.is_active == is_active:

        return jsonify({

            "status":
                "success",

            "message":
                "Area status is already up to date.",

            "is_active":
                assignment.is_active
        })

    old_status = assignment.is_active

    assignment.is_active = is_active

    write_audit_log(

        actor=admin,

        action=(
            "agent.area_activated"
            if is_active
            else "agent.area_deactivated"
        ),

        resource_type=
            "agent_area_assignment",

        resource_id=
            assignment.id,

        old_status=(
            "active"
            if old_status
            else "inactive"
        ),

        new_status=(
            "active"
            if is_active
            else "inactive"
        )
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to update area status.",
            500
        )

    return jsonify({

        "status":
            "success",

        "message":
            "Agent area status updated.",

        "area": {

            "id":
                assignment.area_id,

            "assignment_id":
                assignment.id,

            "is_active":
                assignment.is_active
        }
    })


# =========================================================
# REMOVE AGENT AREA
# DELETE /api/admin/agents/<id>/areas/<area_id>
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

    agent = db.session.get(
        AgentProfile,
        agent_id
    )

    if not agent:

        return error_response(
            "Agent not found.",
            404
        )

    assignment = (
        AgentAreaAssignment.query
        .filter_by(

            agent_id=
                agent.id,

            area_id=
                area_id
        )
        .first()
    )

    if not assignment:

        return error_response(
            "Agent area assignment not found.",
            404
        )

    if not assignment.is_active:

        return jsonify({

            "status":
                "success",

            "message":
                "Agent area is already inactive."
        })

    assignment.is_active = False

    write_audit_log(

        actor=admin,

        action=
            "agent.area_deactivated",

        resource_type=
            "agent_area_assignment",

        resource_id=
            assignment.id,

        old_status=
            "active",

        new_status=
            "inactive"
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to deactivate agent area.",
            500
        )

    return jsonify({

        "status":
            "success",

        "message":
            "Agent area deactivated successfully."
    })


# =========================================================
# JOB LIST
# GET /api/admin/jobs
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

                "min": (
                    float(
                        job.budget_min
                    )
                    if job.budget_min is not None
                    else None
                ),

                "max": (
                    float(
                        job.budget_max
                    )
                    if job.budget_max is not None
                    else None
                )
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

                "id": (
                    job.category.id
                    if job.category
                    else None
                ),

                "name": (
                    job.category.name
                    if job.category
                    else None
                )
            },

            "customer": {

                "id": (
                    job.customer.id
                    if job.customer
                    else None
                ),

                "name": (
                    job.customer.full_name
                    if job.customer
                    else None
                ),

                "email": (
                    job.customer.email
                    if job.customer
                    else None
                )
            },

            "created_at": (

                job.created_at.isoformat()

                if job.created_at

                else None
            )
        })

    return jsonify({

        "status":
            "success",

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
def admin_job_approval(
    job_id
):

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
        data.get(
            "action",
            ""
        )
    ).strip().lower()

    remarks = str(
        data.get(
            "remarks",
            ""
        )
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

    job.status = (
        "approved"
        if action == "approve"
        else "rejected"
    )

    create_approval_record(
        admin,
        "job",
        job.id,
        action,
        remarks
    )

    write_audit_log(

        actor=admin,

        action=
            "job.final_approval",

        resource_type=
            "job",

        resource_id=
            job.id,

        old_status=
            old_status,

        new_status=
            job.status,

        details={
            "remarks":
                remarks
        }
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to update job approval.",
            500
        )

    return jsonify({

        "status":
            "success",

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
def delete_job(
    job_id
):

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

    if job.status == "deleted":

        return jsonify({

            "status":
                "success",

            "message":
                "Job is already deleted."
        })

    old_status = job.status

    job.status = "deleted"

    write_audit_log(

        actor=admin,

        action=
            "job.soft_deleted",

        resource_type=
            "job",

        resource_id=
            job.id,

        old_status=
            old_status,

        new_status=
            "deleted"
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to delete job.",
            500
        )

    return jsonify({

        "status":
            "success",

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

            "job_title": (
                application.job.title
                if application.job
                else None
            ),

            "worker_id":
                application.worker_id,

            "worker_name": (
                application.worker.full_name
                if application.worker
                else None
            ),

            "proposed_amount": (

                float(
                    application.proposed_amount
                )

                if application.proposed_amount
                is not None

                else None
            ),

            "message":
                application.message,

            "availability":
                application.availability,

            "status":
                application.status,

            "created_at": (

                application.created_at.isoformat()

                if application.created_at

                else None
            )
        })

    return jsonify({

        "status":
            "success",

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
# WORKERS
# GET /api/admin/workers
# =========================================================

@admin_bp.get("/workers")
@admin_required
def admin_workers():

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    status = (
        request.args.get(
            "status",
            ""
        )
        .strip()
        .lower()
    )

    search = (
        request.args.get(
            "search",
            ""
        )
        .strip()
    )

    is_active = request.args.get(
        "is_active"
    )

    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------

    query = (
        WorkerProfile.query
        .join(
            User,
            WorkerProfile.user_id == User.id
        )
    )

    # -----------------------------------------------------
    # VERIFICATION STATUS
    # -----------------------------------------------------

    if status:

        if status not in {
            "pending",
            "approved",
            "rejected"
        }:

            return error_response(
                "Invalid worker verification status.",
                400
            )

        query = query.filter(
            func.lower(
                WorkerProfile.verification_status
            ) == status
        )

    # -----------------------------------------------------
    # ACTIVE / INACTIVE
    # -----------------------------------------------------

    if is_active is not None:

        normalized_active = (
            str(is_active)
            .strip()
            .lower()
        )

        if normalized_active not in {
            "true",
            "false"
        }:

            return error_response(
                "is_active must be true or false.",
                400
            )

        query = query.filter(
            User.is_active
            ==
            (
                normalized_active == "true"
            )
        )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        search_pattern = (
            f"%{search}%"
        )

        query = query.filter(

            or_(

                User.full_name.ilike(
                    search_pattern
                ),

                User.email.ilike(
                    search_pattern
                ),

                User.phone.ilike(
                    search_pattern
                )
            )
        )

    # -----------------------------------------------------
    # ORDER + PAGINATION
    # -----------------------------------------------------

    pagination = (
        query
        .order_by(
            WorkerProfile.id.desc()
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    # -----------------------------------------------------
    # SERIALIZE
    # -----------------------------------------------------

    workers = []

    for worker in pagination.items:

        user = worker.user

        workers.append({

            # =============================================
            # WORKER
            # =============================================

            "id":
                worker.id,

            "user_id":
                worker.user_id,

            "verification_status":
                worker.verification_status,

            "is_verified":
                worker.is_verified,

            # =============================================
            # USER
            # =============================================

            "user": {

                "id": (
                    user.id
                    if user
                    else None
                ),

                "full_name": (
                    user.full_name
                    if user
                    else None
                ),

                "email": (
                    user.email
                    if user
                    else None
                ),

                "phone": (
                    user.phone
                    if user
                    else None
                ),

                "role": (
                    user.role
                    if user
                    else None
                ),

                "is_active": (
                    user.is_active
                    if user
                    else False
                ),

                "is_verified": (
                    user.is_verified
                    if user
                    else False
                ),

                "created_at": (

                    user.created_at.isoformat()

                    if user
                    and user.created_at

                    else None
                )
            },

            # =============================================
            # WORKER PROFILE
            # =============================================

            "profile": {

                "id":
                    worker.id,

                "verification_status":
                    worker.verification_status,

                "is_verified":
                    worker.is_verified,

                "created_at": (

                    worker.created_at.isoformat()

                    if worker.created_at

                    else None
                ),

                "updated_at": (

                    worker.updated_at.isoformat()

                    if worker.updated_at

                    else None
                )
            }
        })

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "status":
            "success",

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
                pagination.pages,

            "has_next":
                pagination.has_next,

            "has_prev":
                pagination.has_prev
        },

        "filters": {

            "status":
                status or None,

            "search":
                search or None,

            "is_active": (

                (
                    is_active
                    if is_active
                    else None
                )
            )
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
        data.get(
            "action",
            ""
        )
    ).strip().lower()

    remarks = str(
        data.get(
            "remarks",
            ""
        )
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

    application.status = (
        "hired"
        if action == "approve"
        else "rejected"
    )

    create_approval_record(

        admin,

        "job_application",

        application.id,

        action,

        remarks
    )

    write_audit_log(

        actor=admin,

        action=
            "application.final_approval",

        resource_type=
            "job_application",

        resource_id=
            application.id,

        old_status=
            old_status,

        new_status=
            application.status,

        details={
            "remarks":
                remarks
        }
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to update application status.",
            500
        )

    return jsonify({

        "status":
            "success",

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

    write_audit_log(

        actor=admin,

        action=
            "worker.verification_changed",

        resource_type=
            "worker",

        resource_id=
            worker.id,

        old_status=
            old_status,

        new_status=
            status
    )

    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return error_response(
            "Unable to update worker verification.",
            500
        )

    return jsonify({

        "status":
            "success",

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

        "status":
            "success",

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

            for category
            in categories
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

        "status":
            "success",

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

                "created_at": (

                    log.created_at.isoformat()

                    if log.created_at

                    else None
                )
            }

            for log
            in pagination.items
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
