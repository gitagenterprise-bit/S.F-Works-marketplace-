import secrets
import string

from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    get_jwt_identity
)

from extensions import db

from models import (
    User,
    AgentProfile,
    AgentArea,
    AgentAreaAssignment,
    AgentPermission
)

from utils.decorators import (
    admin_required
)

from utils.audit import (
    create_audit_log
)


admin_agents_bp = Blueprint(
    "admin_agents",
    __name__,
    url_prefix="/api/admin/agents"
)


# =========================================================
# HELPERS
# =========================================================

def generate_employee_code():

    while True:

        code = (
            "AG-"
            + "".join(
                secrets.choice(
                    string.ascii_uppercase
                    + string.digits
                )
                for _ in range(8)
            )
        )

        exists = AgentProfile.query.filter_by(
            employee_code=code
        ).first()

        if not exists:
            return code


def generate_temp_password():

    return (
        secrets.token_urlsafe(12)
    )


# =========================================================
# CREATE AGENT
# =========================================================

@admin_agents_bp.post("")
@admin_required
def create_agent():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    full_name = (
        str(
            data.get(
                "full_name",
                ""
            )
        ).strip()
    )

    email = (
        str(
            data.get(
                "email",
                ""
            )
        )
        .strip()
        .lower()
    )

    phone = (
        str(
            data.get(
                "phone",
                ""
            )
        ).strip()
    )

    designation = (
        str(
            data.get(
                "designation",
                "Area Agent"
            )
        ).strip()
    )

    if not full_name:

        return jsonify({
            "status": "error",
            "message":
                "Full name is required."
        }), 400

    if not email:

        return jsonify({
            "status": "error",
            "message":
                "Email is required."
        }), 400

    if not phone:

        return jsonify({
            "status": "error",
            "message":
                "Phone is required."
        }), 400

    if User.query.filter_by(
        email=email
    ).first():

        return jsonify({
            "status": "error",
            "message":
                "Email already exists."
        }), 409

    if User.query.filter_by(
        phone=phone
    ).first():

        return jsonify({
            "status": "error",
            "message":
                "Phone already exists."
        }), 409

    admin_id = int(
        get_jwt_identity()
    )

    temp_password = (
        generate_temp_password()
    )

    employee_code = (
        generate_employee_code()
    )

    try:

        user = User(

            full_name=full_name,

            email=email,

            phone=phone,

            role="agent",

            is_active=True,

            is_verified=False
        )

        user.set_password(
            temp_password
        )

        db.session.add(user)

        db.session.flush()

        agent = AgentProfile(

            user_id=user.id,

            employee_code=employee_code,

            designation=(
                designation
                or "Area Agent"
            ),

            is_verified=False,

            verification_status="pending",

            force_password_change=True,

            created_by=admin_id
        )

        db.session.add(agent)

        db.session.flush()

        create_audit_log(

            actor_id=admin_id,

            action="AGENT_CREATED",

            entity_type="agent",

            entity_id=agent.id,

            description=(
                f"Agent {employee_code} "
                f"created by administrator."
            )
        )

        db.session.commit()

    except Exception:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message":
                "Unable to create agent."
        }), 500

    return jsonify({

        "status": "success",

        "message":
            "Agent created successfully.",

        "agent": {

            "id":
                agent.id,

            "user_id":
                user.id,

            "employee_code":
                agent.employee_code,

            "full_name":
                user.full_name,

            "email":
                user.email,

            "phone":
                user.phone,

            "role":
                user.role,

            "verification_status":
                agent.verification_status,

            "force_password_change":
                agent.force_password_change
        },

        # IMPORTANT:
        # Only returned once during creation.
        "temporary_password":
            temp_password

    }), 201

# =========================================================
# ASSIGN AREA
# =========================================================

@admin_agents_bp.post(
    "/<int:agent_id>/areas"
)
@admin_required
def assign_agent_area(agent_id):

    agent = db.session.get(
        AgentProfile,
        agent_id
    )

    if not agent:

        return jsonify({
            "status": "error",
            "message":
                "Agent not found."
        }), 404

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    area_id = data.get(
        "area_id"
    )

    if not isinstance(
        area_id,
        int
    ):

        return jsonify({
            "status": "error",
            "message":
                "Valid area_id is required."
        }), 400

    area = db.session.get(
        AgentArea,
        area_id
    )

    if not area or not area.is_active:

        return jsonify({
            "status": "error",
            "message":
                "Area not found or inactive."
        }), 404

    existing = AgentAreaAssignment.query.filter_by(
        agent_id=agent.id,
        area_id=area.id
    ).first()

    if existing:

        if existing.is_active:

            return jsonify({
                "status": "error",
                "message":
                    "This area is already assigned."
            }), 409

        existing.is_active = True

        assignment = existing

    else:

        assignment = AgentAreaAssignment(

            agent_id=agent.id,

            area_id=area.id,

            assigned_by=int(
                get_jwt_identity()
            ),

            is_active=True
        )

        db.session.add(
            assignment
        )

    create_audit_log(

        actor_id=int(
            get_jwt_identity()
        ),

        action="AGENT_AREA_ASSIGNED",

        entity_type="agent",

        entity_id=agent.id,

        description=(
            f"Area {area.id} "
            f"assigned to agent "
            f"{agent.employee_code}."
        )
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Area assigned successfully.",

        "assignment": {

            "id":
                assignment.id,

            "agent_id":
                agent.id,

            "area_id":
                area.id,

            "area_name":
                area.name,

            "area_type":
                area.area_type
        }

    }), 201

# =========================================================
# CREATE AREA
# =========================================================

@admin_agents_bp.post(
    "/areas"
)
@admin_required
def create_area():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    name = str(
        data.get(
            "name",
            ""
        )
    ).strip()

    area_type = str(
        data.get(
            "area_type",
            ""
        )
    ).strip().lower()

    district = str(
        data.get(
            "district",
            ""
        )
    ).strip() or None

    police_station = str(
        data.get(
            "police_station",
            ""
        )
    ).strip() or None

    locality = str(
        data.get(
            "locality",
            ""
        )
    ).strip() or None

    pincode = str(
        data.get(
            "pincode",
            ""
        )
    ).strip() or None

    state = str(
        data.get(
            "state",
            ""
        )
    ).strip() or None

    allowed_types = {
        "district",
        "police_station",
        "locality",
        "pincode"
    }

    if area_type not in allowed_types:

        return jsonify({
            "status": "error",
            "message":
                "Invalid area type."
        }), 400

    if not name:

        return jsonify({
            "status": "error",
            "message":
                "Area name is required."
        }), 400

    if (
        area_type == "district"
        and not district
    ):

        district = name

    if (
        area_type == "police_station"
        and (
            not district
            or not police_station
        )
    ):

        return jsonify({
            "status": "error",
            "message":
                "District and police station "
                "are required."
        }), 400

    if (
        area_type == "locality"
        and (
            not district
            or not locality
        )
    ):

        return jsonify({
            "status": "error",
            "message":
                "District and locality "
                "are required."
        }), 400

    if (
        area_type == "pincode"
        and not pincode
    ):

        return jsonify({
            "status": "error",
            "message":
                "PIN code is required."
        }), 400

    area = AgentArea(

        name=name,

        area_type=area_type,

        district=district,

        police_station=police_station,

        locality=locality,

        pincode=pincode,

        state=state,

        is_active=True
    )

    db.session.add(area)

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message":
                "Area already exists or "
                "could not be created."
        }), 409

    create_audit_log(

        actor_id=int(
            get_jwt_identity()
        ),

        action="AREA_CREATED",

        entity_type="area",

        entity_id=area.id,

        description=(
            f"Area {area.name} "
            f"created."
        )
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Area created successfully.",

        "area": {

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
                area.state
        }

    }), 201

@admin_agents_bp.put(
    "/<int:agent_id>/permissions"
)
@admin_required
def update_agent_permissions(agent_id):

    agent = db.session.get(
        AgentProfile,
        agent_id
    )

    if not agent:

        return jsonify({
            "status": "error",
            "message":
                "Agent not found."
        }), 404

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    permissions = data.get(
        "permissions"
    )

    if not isinstance(
        permissions,
        list
    ):

        return jsonify({
            "status": "error",
            "message":
                "permissions must be a list."
        }), 400

    allowed_permissions = {

        "jobs.view",

        "jobs.review",

        "applications.view",

        "applications.review",

        "workers.view",

        "workers.review",

        "doctors.view",

        "doctors.review",

        "chambers.view",

        "chambers.review",

        "bookings.view",

        "bookings.review"
    }

    requested = set(
        str(item).strip()
        for item in permissions
    )

    invalid = (
        requested
        - allowed_permissions
    )

    if invalid:

        return jsonify({

            "status": "error",

            "message":
                "Invalid permissions.",

            "invalid_permissions":
                sorted(invalid)

        }), 400

    admin_id = int(
        get_jwt_identity()
    )

    existing = {
        item.permission: item
        for item in agent.permissions
    }

    for permission in allowed_permissions:

        record = existing.get(
            permission
        )

        should_allow = (
            permission in requested
        )

        if record:

            record.is_allowed = (
                should_allow
            )

            record.granted_by = (
                admin_id
            )

        else:

            db.session.add(

                AgentPermission(

                    agent_id=agent.id,

                    permission=permission,

                    is_allowed=should_allow,

                    granted_by=admin_id
                )
            )

    create_audit_log(

        actor_id=admin_id,

        action="AGENT_PERMISSIONS_UPDATED",

        entity_type="agent",

        entity_id=agent.id,

        description=(
            f"Permissions updated "
            f"for {agent.employee_code}."
        )
    )

    db.session.commit()

    return jsonify({

        "status": "success",

        "message":
            "Agent permissions updated.",

        "permissions":
            sorted(requested)

    }), 200

