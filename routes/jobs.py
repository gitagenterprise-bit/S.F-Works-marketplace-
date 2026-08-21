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

from models.user import User
from models.job import Job, JobImage
from models.category import Category

from utils.default_categories import (
    ensure_default_categories
)

from utils.decorators import role_required


# ============================================================
# BLUEPRINT
# ============================================================

jobs_bp = Blueprint(
    "jobs",
    __name__
)


# ============================================================
# PUBLIC JOB LIST
# GET /api/jobs/
#
# Guest + Logged-in users can view jobs
# ============================================================

@jobs_bp.route(
    "/",
    methods=["GET"]
)
def public_jobs():

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

    # Safety limit
    if per_page < 1:
        per_page = 12

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

    min_budget = request.args.get(
        "min_budget",
        type=float
    )

    max_budget = request.args.get(
        "max_budget",
        type=float
    )

    # --------------------------------------------------------
    # BASE QUERY
    # --------------------------------------------------------

    query = Job.query.filter(
        Job.status == "open"
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Job.title.ilike(
                    search_pattern
                ),

                Job.description.ilike(
                    search_pattern
                ),

                Job.location.ilike(
                    search_pattern
                ),

                Job.city.ilike(
                    search_pattern
                )
            )
        )

    # --------------------------------------------------------
    # CITY
    # --------------------------------------------------------

    if city:

        query = query.filter(
            Job.city.ilike(
                f"%{city}%"
            )
        )

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if category_id:

        query = query.filter(
            Job.category_id == category_id
        )

    # --------------------------------------------------------
    # MINIMUM BUDGET
    # --------------------------------------------------------

    if min_budget is not None:

        query = query.filter(
            Job.budget_max >= min_budget
        )

    # --------------------------------------------------------
    # MAXIMUM BUDGET
    # --------------------------------------------------------

    if max_budget is not None:

        query = query.filter(
            Job.budget_min <= max_budget
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    query = query.order_by(
        Job.is_featured.desc(),
        Job.created_at.desc()
    )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

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

            "budget": {

                "min": (
                    float(job.budget_min)
                    if job.budget_min is not None
                    else None
                ),

                "max": (
                    float(job.budget_max)
                    if job.budget_max is not None
                    else None
                )
            },

            "location": job.location,

            "city": job.city,

            "state": job.state,

            "pincode": job.pincode,

            "status": job.status,

            "priority": job.priority,

            "is_featured": job.is_featured,

            "views": job.views,

            "category": {

                "id": job.category.id,

                "name": job.category.name,

                "slug": job.category.slug,

                "icon": job.category.icon

            } if job.category else None,

            "created_at": (
                job.created_at.isoformat()
                if job.created_at
                else None
            )
        })

    return jsonify({

        "status": "success",

        "data": jobs,

        "pagination": {

            "page": pagination.page,

            "per_page": pagination.per_page,

            "total": pagination.total,

            "pages": pagination.pages,

            "has_next": pagination.has_next,

            "has_prev": pagination.has_prev
        }

    }), 200


# ============================================================
# JOB DETAILS
# GET /api/jobs/<job_id>
#
# Public
# ============================================================

@jobs_bp.route(
    "/<int:job_id>",
    methods=["GET"]
)
def job_details(job_id):

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

            "message": "This job is no longer available"

        }), 404

    # --------------------------------------------------------
    # INCREASE VIEW COUNT
    # --------------------------------------------------------

    job.views = (
        job.views or 0
    ) + 1

    db.session.commit()

    # --------------------------------------------------------
    # IMAGES
    # --------------------------------------------------------

    images = []

    for image in job.images:

        images.append({

            "id": image.id,

            "image_path": image.image_path

        })

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    response = {

        "id": job.id,

        "title": job.title,

        "description": job.description,

        "budget": {

            "min": (
                float(job.budget_min)
                if job.budget_min is not None
                else None
            ),

            "max": (
                float(job.budget_max)
                if job.budget_max is not None
                else None
            )
        },

        "location": job.location,

        "city": job.city,

        "state": job.state,

        "pincode": job.pincode,

        "latitude": (

            float(job.latitude)

            if job.latitude is not None

            else None
        ),

        "longitude": (

            float(job.longitude)

            if job.longitude is not None

            else None
        ),

        "status": job.status,

        "priority": job.priority,

        "is_featured": job.is_featured,

        "views": job.views,

        "category": {

            "id": job.category.id,

            "name": job.category.name,

            "slug": job.category.slug,

            "icon": job.category.icon

        } if job.category else None,

        "images": images,

        "created_at": (

            job.created_at.isoformat()

            if job.created_at

            else None
        )
    }

    return jsonify({

        "status": "success",

        "job": response

    }), 200


# ============================================================
# CREATE JOB
# POST /api/jobs/create
#
# AUTHENTICATED USERS ONLY
#
# Customer  -> allowed
# Worker    -> allowed
# Admin     -> allowed
#
# Guest     -> 401
# ============================================================

@jobs_bp.route(
    "/create",
    methods=["POST"]
)
@role_required(
    "customer",
    "worker",
    "admin"
)
def create_job():

    # ========================================================
    # CURRENT USER
    # ========================================================

    user_id = get_jwt_identity()

    try:

        user_id = int(user_id)

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "status": "error",

            "message": "Invalid user identity"

        }), 401

    # ========================================================
    # USER
    # ========================================================

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        return jsonify({

            "status": "error",

            "message": "User not found"

        }), 401

    # ========================================================
    # ACTIVE ACCOUNT
    # ========================================================

    if not user.is_active:

        return jsonify({

            "status": "error",

            "message": "Your account has been disabled"

        }), 403

    # ========================================================
    # REQUEST BODY
    # ========================================================

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "status": "error",

            "message": "Request body is required"

        }), 400

    # ========================================================
    # INPUTS
    # ========================================================

    title = data.get(
        "title"
    )

    description = data.get(
        "description"
    )

    category_id = data.get(
        "category_id"
    )

    location = data.get(
        "location"
    )

    budget_min = data.get(
        "budget_min"
    )

    budget_max = data.get(
        "budget_max"
    )

    city = data.get(
        "city"
    )

    state = data.get(
        "state"
    )

    pincode = data.get(
        "pincode"
    )

    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )

    priority = data.get(
        "priority",
        "normal"
    )

    # ========================================================
    # PRIORITY
    # ========================================================

    allowed_priorities = {

        "normal",

        "high",

        "urgent"
    }

    if priority not in allowed_priorities:

        return jsonify({

            "status": "error",

            "message": "Invalid priority"

        }), 400

    # ========================================================
    # TITLE
    # ========================================================

    if (
        not isinstance(
            title,
            str
        )
        or not title.strip()
    ):

        return jsonify({

            "status": "error",

            "message": "Job title is required"

        }), 400

    title = title.strip()

    if len(title) < 3:

        return jsonify({

            "status": "error",

            "message": (
                "Job title must contain "
                "at least 3 characters"
            )

        }), 400

    if len(title) > 200:

        return jsonify({

            "status": "error",

            "message": (
                "Job title cannot exceed "
                "200 characters"
            )

        }), 400

    # ========================================================
    # DESCRIPTION
    # ========================================================

    if (
        not isinstance(
            description,
            str
        )
        or not description.strip()
    ):

        return jsonify({

            "status": "error",

            "message": "Job description is required"

        }), 400

    description = description.strip()

    if len(description) > 5000:

        return jsonify({

            "status": "error",

            "message": (
                "Job description cannot exceed "
                "5000 characters"
            )

        }), 400

    # ========================================================
    # CATEGORY ID
    # ========================================================

    if category_id is None:

        return jsonify({

            "status": "error",

            "message": "Category is required"

        }), 400

    try:

        category_id = int(
            category_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "status": "error",

            "message": "Invalid category"

        }), 400

    # ========================================================
    # CATEGORY
    # ========================================================

    category = db.session.get(
        Category,
        category_id
    )

    if not category:

        return jsonify({

            "status": "error",

            "message": "Invalid category"

        }), 400

    if not category.is_active:

        return jsonify({

            "status": "error",

            "message": (
                "This category is currently unavailable"
            )

        }), 400

    # ========================================================
    # LOCATION
    # ========================================================

    if (
        not isinstance(
            location,
            str
        )
        or not location.strip()
    ):

        return jsonify({

            "status": "error",

            "message": "Location is required"

        }), 400

    location = location.strip()

    if len(location) > 255:

        return jsonify({

            "status": "error",

            "message": (
                "Location cannot exceed "
                "255 characters"
            )

        }), 400

    # ========================================================
    # BUDGET
    # ========================================================

    try:

        if budget_min is not None:

            budget_min = float(
                budget_min
            )

        if budget_max is not None:

            budget_max = float(
                budget_max
            )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "status": "error",

            "message": "Invalid budget amount"

        }), 400

    if (
        budget_min is not None
        and budget_min < 0
    ):

        return jsonify({

            "status": "error",

            "message": (
                "Minimum budget cannot "
                "be negative"
            )

        }), 400

    if (
        budget_max is not None
        and budget_max < 0
    ):

        return jsonify({

            "status": "error",

            "message": (
                "Maximum budget cannot "
                "be negative"
            )

        }), 400

    if (
        budget_min is not None
        and budget_max is not None
        and budget_min > budget_max
    ):

        return jsonify({

            "status": "error",

            "message": (
                "Minimum budget cannot "
                "exceed maximum budget"
            )

        }), 400

    # ========================================================
    # OPTIONAL TEXT FIELDS
    # ========================================================

    if isinstance(
        city,
        str
    ):

        city = city.strip()

        if not city:

            city = None

    else:

        city = None

    if isinstance(
        state,
        str
    ):

        state = state.strip()

        if not state:

            state = None

    else:

        state = None

    if isinstance(
        pincode,
        str
    ):

        pincode = pincode.strip()

        if not pincode:

            pincode = None

    else:

        pincode = None

    # ========================================================
    # CREATE JOB
    # ========================================================
    #
    # NOTE:
    # Existing Job model uses customer_id as the user FK.
    # We keep that field so no database migration is required.
    #
    # It stores the ID of the authenticated user who posted
    # the job, regardless of whether the role is customer,
    # worker, or admin.
    # ========================================================

    job = Job(

        customer_id=user.id,

        category_id=category.id,

        title=title,

        description=description,

        budget_min=budget_min,

        budget_max=budget_max,

        location=location,

        city=city,

        state=state,

        pincode=pincode,

        latitude=latitude,

        longitude=longitude,

        priority=priority,

        status="open"
    )

    # ========================================================
    # DATABASE TRANSACTION
    # ========================================================

    try:

        db.session.add(
            job
        )

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[CREATE JOB ERROR]",
            exc
        )

        return jsonify({

            "status": "error",

            "message": (
                "Unable to create job. "
                "Please try again."
            )

        }), 500

    # ========================================================
    # SUCCESS RESPONSE
    # ========================================================

    return jsonify({

        "status": "success",

        "message": "Job posted successfully",

        "job": {

            "id": job.id,

            "title": job.title,

            "status": job.status,

            "category": {

                "id": category.id,

                "name": category.name,

                "slug": category.slug
            },

            "posted_by": {

                "id": user.id,

                "name": user.full_name,

                "phone": user.phone,

                "role": user.role
            },

            "location": job.location,

            "city": job.city,

            "state": job.state,

            "pincode": job.pincode,

            "created_at": (

                job.created_at.isoformat()

                if job.created_at

                else None
            )
        }

    }), 201


# ============================================================
# UPDATE JOB
# PUT /api/jobs/<job_id>
#
# Currently only the original customer can edit.
# ============================================================

@jobs_bp.route(
    "/<int:job_id>",
    methods=["PUT"]
)
@role_required(
    "customer"
)
def update_job(job_id):

    user_id = get_jwt_identity()

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "status": "error",

            "message": "Invalid user identity"

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

    if job.customer_id != user_id:

        return jsonify({

            "status": "error",

            "message": (
                "You can only edit "
                "your own jobs"
            )

        }), 403

    if job.status != "open":

        return jsonify({

            "status": "error",

            "message": (
                "Only open jobs can be edited"
            )

        }), 400

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "status": "error",

            "message": "Request body is required"

        }), 400

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if "title" in data:

        title = data.get(
            "title"
        )

        if (
            not isinstance(
                title,
                str
            )
            or not title.strip()
        ):

            return jsonify({

                "status": "error",

                "message": "Title cannot be empty"

            }), 400

        title = title.strip()

        if len(title) < 3:

            return jsonify({

                "status": "error",

                "message": (
                    "Title must contain "
                    "at least 3 characters"
                )

            }), 400

        if len(title) > 200:

            return jsonify({

                "status": "error",

                "message": (
                    "Title cannot exceed "
                    "200 characters"
                )

            }), 400

        job.title = title

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    if "description" in data:

        description = data.get(
            "description"
        )

        if (
            not isinstance(
                description,
                str
            )
            or not description.strip()
        ):

            return jsonify({

                "status": "error",

                "message": (
                    "Description cannot be empty"
                )

            }), 400

        description = description.strip()

        if len(description) > 5000:

            return jsonify({

                "status": "error",

                "message": (
                    "Description cannot exceed "
                    "5000 characters"
                )

            }), 400

        job.description = description

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if "category_id" in data:

        try:

            category_id = int(
                data.get(
                    "category_id"
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "status": "error",

                "message": "Invalid category"

            }), 400

        category = db.session.get(
            Category,
            category_id
        )

        if not category:

            return jsonify({

                "status": "error",

                "message": "Invalid category"

            }), 400

        if not category.is_active:

            return jsonify({

                "status": "error",

                "message": (
                    "This category is currently unavailable"
                )

            }), 400

        job.category_id = category.id

    # --------------------------------------------------------
    # BUDGET
    # --------------------------------------------------------

    if "budget_min" in data:

        try:

            job.budget_min = (
                float(
                    data.get(
                        "budget_min"
                    )
                )
                if data.get(
                    "budget_min"
                ) is not None
                else None
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "status": "error",

                "message": (
                    "Invalid minimum budget"
                )

            }), 400

    if "budget_max" in data:

        try:

            job.budget_max = (
                float(
                    data.get(
                        "budget_max"
                    )
                )
                if data.get(
                    "budget_max"
                ) is not None
                else None
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "status": "error",

                "message": (
                    "Invalid maximum budget"
                )

            }), 400

    if (
        job.budget_min is not None
        and job.budget_min < 0
    ):

        return jsonify({

            "status": "error",

            "message": (
                "Minimum budget cannot "
                "be negative"
            )

        }), 400

    if (
        job.budget_max is not None
        and job.budget_max < 0
    ):

        return jsonify({

            "status": "error",

            "message": (
                "Maximum budget cannot "
                "be negative"
            )

        }), 400

    if (
        job.budget_min is not None
        and job.budget_max is not None
        and job.budget_min > job.budget_max
    ):

        return jsonify({

            "status": "error",

            "message": (
                "Minimum budget cannot "
                "exceed maximum budget"
            )

        }), 400

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    if "location" in data:

        location = data.get(
            "location"
        )

        if (
            not isinstance(
                location,
                str
            )
            or not location.strip()
        ):

            return jsonify({

                "status": "error",

                "message": (
                    "Location cannot be empty"
                )

            }), 400

        job.location = location.strip()

    # --------------------------------------------------------
    # CITY
    # --------------------------------------------------------

    if "city" in data:

        city = data.get(
            "city"
        )

        job.city = (

            city.strip()

            if isinstance(
                city,
                str
            )
            and city.strip()

            else None
        )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    if "state" in data:

        state = data.get(
            "state"
        )

        job.state = (

            state.strip()

            if isinstance(
                state,
                str
            )
            and state.strip()

            else None
        )

    # --------------------------------------------------------
    # PINCODE
    # --------------------------------------------------------

    if "pincode" in data:

        pincode = data.get(
            "pincode"
        )

        job.pincode = (

            pincode.strip()

            if isinstance(
                pincode,
                str
            )
            and pincode.strip()

            else None
        )

    # --------------------------------------------------------
    # COORDINATES
    # --------------------------------------------------------

    if "latitude" in data:

        job.latitude = data.get(
            "latitude"
        )

    if "longitude" in data:

        job.longitude = data.get(
            "longitude"
        )

    # --------------------------------------------------------
    # PRIORITY
    # --------------------------------------------------------

    if "priority" in data:

        priority = data.get(
            "priority"
        )

        if priority not in {
            "normal",
            "high",
            "urgent"
        }:

            return jsonify({

                "status": "error",

                "message": "Invalid priority"

            }), 400

        job.priority = priority

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[UPDATE JOB ERROR]",
            exc
        )

        return jsonify({

            "status": "error",

            "message": (
                "Unable to update job"
            )

        }), 500

    return jsonify({

        "status": "success",

        "message": (
            "Job updated successfully"
        ),

        "job": {

            "id": job.id,

            "title": job.title,

            "status": job.status
        }

    }), 200


# ============================================================
# DELETE JOB
# DELETE /api/jobs/<job_id>
# ============================================================

@jobs_bp.route(
    "/<int:job_id>",
    methods=["DELETE"]
)
@role_required(
    "customer"
)
def delete_job(job_id):

    user_id = get_jwt_identity()

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "status": "error",

            "message": "Invalid user identity"

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

    if job.customer_id != user_id:

        return jsonify({

            "status": "error",

            "message": (
                "You can only delete "
                "your own jobs"
            )

        }), 403

    if job.status != "open":

        return jsonify({

            "status": "error",

            "message": (
                "Only open jobs can be deleted"
            )

        }), 400

    try:

        db.session.delete(
            job
        )

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[DELETE JOB ERROR]",
            exc
        )

        return jsonify({

            "status": "error",

            "message": (
                "Unable to delete job"
            )

        }), 500

    return jsonify({

        "status": "success",

        "message": (
            "Job deleted successfully"
        )

    }), 200


# ============================================================
# ACTIVE CATEGORIES
# GET /api/jobs/categories
#
# Public
# ============================================================

@jobs_bp.route(
    "/categories",
    methods=["GET"]
)
def categories():

    try:

        # ----------------------------------------------------
        # Ensure default categories exist
        # ----------------------------------------------------

        ensure_default_categories()

        # ----------------------------------------------------
        # Active categories
        # ----------------------------------------------------

        categories = (

            Category.query

            .filter(
                Category.is_active.is_(True)
            )

            .order_by(
                Category.name.asc()
            )

            .all()
        )

        data = []

        for category in categories:

            data.append({

                "id": category.id,

                "name": category.name,

                "slug": category.slug,

                "description": (
                    category.description
                    or ""
                ),

                "icon": (
                    category.icon
                    or "✦"
                ),

                "image": (
                    category.image
                    or ""
                )
            })

        return jsonify({

            "status": "success",

            "categories": data,

            "count": len(data)

        }), 200

    except Exception as exc:

        db.session.rollback()

        print(
            "[CATEGORY ERROR]",
            exc
        )

        return jsonify({

            "status": "error",

            "message": (
                "Unable to load categories"
            )

        }), 500
