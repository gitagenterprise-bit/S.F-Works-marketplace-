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
    Job,
    JobApplication
)

from utils.decorators import (
    agent_permission
)

from utils.agent_scope import (
    agent_can_access_location
)


agent_bp = Blueprint(
    "agent",
    __name__,
    url_prefix="/api/agent"
)


# =========================================================
# AGENT ME
# =========================================================

@agent_bp.get("/me")
@agent_permission("jobs.view")
def agent_me():

    user = db.session.get(
        User,
        int(get_jwt_identity())
    )

    agent = user.agent_profile

    return jsonify({

        "status": "success",

        "agent": {

            "id":
                agent.id,

            "employee_code":
                agent.employee_code,

            "designation":
                agent.designation,

            "full_name":
                user.full_name,

            "email":
                user.email,

            "phone":
                user.phone,

            "verification_status":
                agent.verification_status,

            "areas": [

                {
                    "id":
                        assignment.area.id,

                    "name":
                        assignment.area.name,

                    "type":
                        assignment.area.area_type,

                    "district":
                        assignment.area.district,

                    "police_station":
                        assignment.area.police_station,

                    "locality":
                        assignment.area.locality,

                    "pincode":
                        assignment.area.pincode

                }

                for assignment
                in agent.areas

                if (
                    assignment.is_active
                    and assignment.area
                    and assignment.area.is_active
                )
            ],

            "permissions": [

                permission.permission

                for permission
                in agent.permissions

                if permission.is_allowed

            ]
        }

    }), 200


# =========================================================
# AREA-SCOPED JOBS
# =========================================================

@agent_bp.get("/jobs")
@agent_permission("jobs.view")
def agent_jobs():

    user = db.session.get(
        User,
        int(get_jwt_identity())
    )

    agent = user.agent_profile

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

    page = max(
        page,
        1
    )

    per_page = min(
        max(per_page, 1),
        100
    )

    query = (
        Job.query
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

        allowed = agent_can_access_location(

            agent,

            district=job.district,

            police_station=(
                getattr(
                    job,
                    "police_station",
                    None
                )
            ),

            city=job.city,

            pincode=job.pincode
        )

        if not allowed:
            continue

        jobs.append({

            "id":
                job.id,

            "title":
                job.title,

            "status":
                job.status,

            "priority":
                job.priority,

            "location":
                job.location,

            "district":
                job.district,

            "police_station":
                getattr(
                    job,
                    "police_station",
                    None
                ),

            "city":
                job.city,

            "pincode":
                job.pincode,

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
                pagination.total

        }

    }), 200
