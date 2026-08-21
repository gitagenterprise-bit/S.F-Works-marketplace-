from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    request,
    jsonify
)

from flask_jwt_extended import (
    get_jwt_identity
)

from sqlalchemy import (
    or_,
    func
)

from extensions import db

from models.user import User
from models.job import (
    Job,
    JobImage
)
from models.job_application import JobApplication
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
# CONSTANTS
# ============================================================

JOB_STATUSES = {
    "open",
    "paused",
    "assigned",
    "completed",
    "cancelled",
    "closed"
}

PRIORITIES = {
    "normal",
    "high",
    "urgent"
}

APPLICATION_STATUSES = {
    "pending",
    "shortlisted",
    "accepted",
    "rejected",
    "withdrawn"
}

MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5000
MAX_LOCATION_LENGTH = 255
MAX_IMAGES_PER_JOB = 10


# ============================================================
# HELPERS
# ============================================================

def json_error(
    message,
    status_code=400
):

    return jsonify({

        "status": "error",

        "message": message

    }), status_code


def get_current_user():

    identity = get_jwt_identity()

    try:

        user_id = int(identity)

    except (
        TypeError,
        ValueError
    ):

        return None

    return db.session.get(
        User,
        user_id
    )


def decimal_value(
    value,
    field_name,
    allow_none=True
):

    if value is None:

        if allow_none:

            return None

        raise ValueError(
            f"{field_name} is required"
        )

    try:

        amount = Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError
    ):

        raise ValueError(
            f"Invalid {field_name}"
        )

    if amount < 0:

        raise ValueError(
            f"{field_name} cannot be negative"
        )

    return amount


def coordinate_value(
    value,
    field_name,
    minimum,
    maximum
):

    if value is None:

        return None

    try:

        coordinate = Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError
    ):

        raise ValueError(
            f"Invalid {field_name}"
        )

    if (
        coordinate < Decimal(str(minimum))
        or coordinate > Decimal(str(maximum))
    ):

        raise ValueError(
            f"Invalid {field_name}"
        )

    return coordinate


def clean_optional_text(
    value,
    max_length=None
):

    if not isinstance(
        value,
        str
    ):

        return None

    value = value.strip()

    if not value:

        return None

    if (
        max_length
        and len(value) > max_length
    ):

        raise ValueError(
            "Text value is too long"
        )

    return value


def serialize_category(category):

    if not category:

        return None

    return {

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
    }


def serialize_job_image(image):

    return {

        "id": image.id,

        "image_path": image.image_path
    }

def serialize_job(
    job,
    include_description=True,
    include_images=False,
    include_owner=False
):

    data = {

        "id": job.id,

        "title": job.title,

        "description": (
            job.description
            if include_description
            else None
        ),

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

        "budget_display": (
            f"₹{job.budget_min:,.0f} - ₹{job.budget_max:,.0f}"
            if (
                job.budget_min is not None
                and job.budget_max is not None
            )
            else (
                f"₹{job.budget_min:,.0f}"
                if job.budget_min is not None
                else (
                    f"₹{job.budget_max:,.0f}"
                    if job.budget_max is not None
                    else "Budget not specified"
                )
            )
        ),

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

        "is_featured": bool(
            job.is_featured
        ),

        "views": job.views or 0,

        "category": serialize_category(
            job.category
        ),

        "created_at": (
            job.created_at.isoformat()
            if job.created_at
            else None
        ),

        "updated_at": (
            job.updated_at.isoformat()
            if job.updated_at
            else None
        )
    }

    if include_images:

        data["images"] = [

            serialize_job_image(image)

            for image in job.images
        ]

    if include_owner and job.customer:

        data["posted_by"] = {

            "id": job.customer.id,

            "name": job.customer.full_name,

            "role": job.customer.role
        }

    return data


def serialize_application(
    application,
    include_job=False
):

    worker = application.worker

    data = {

        "id": application.id,

        "job_id": application.job_id,

        "worker_id": application.worker_id,

        "proposed_amount": (
            float(application.proposed_amount)
            if application.proposed_amount is not None
            else None
        ),

        "message": application.message,

        "availability": application.availability,

        "status": application.status,

        "created_at": (
            application.created_at.isoformat()
            if application.created_at
            else None
        ),

        "updated_at": (
            application.updated_at.isoformat()
            if application.updated_at
            else None
        )
    }

    if worker:

        data["worker"] = {

            "id": worker.id,

            "name": worker.full_name,

            "role": worker.role
        }

    if include_job and application.job:

        data["job"] = {

            "id": application.job.id,

            "title": application.job.title,

            "status": application.job.status
        }

    return data


# ============================================================
# PUBLIC JOB LIST
# GET /api/jobs/
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

    page = max(
        page,
        1
    )

    per_page = min(
        max(per_page, 1),
        50
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

    state = request.args.get(
        "state",
        "",
        type=str
    ).strip()

    category_id = request.args.get(
        "category_id",
        type=int
    )

    min_budget = request.args.get(
        "min_budget",
        type=str
    )

    max_budget = request.args.get(
        "max_budget",
        type=str
    )

    priority = request.args.get(
        "priority",
        "",
        type=str
    ).strip().lower()

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

        pattern = f"%{search}%"

        query = query.filter(

            or_(

                Job.title.ilike(pattern),

                Job.description.ilike(pattern),

                Job.location.ilike(pattern),

                Job.city.ilike(pattern),

                Job.state.ilike(pattern)
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
    # STATE
    # --------------------------------------------------------

    if state:

        query = query.filter(
            Job.state.ilike(
                f"%{state}%"
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
    # PRIORITY
    # --------------------------------------------------------

    if priority:

        if priority not in PRIORITIES:

            return json_error(
                "Invalid priority"
            )

        query = query.filter(
            Job.priority == priority
        )

    # --------------------------------------------------------
    # BUDGET
    # --------------------------------------------------------

    try:

        if min_budget is not None:

            min_budget = decimal_value(
                min_budget,
                "minimum budget"
            )

        if max_budget is not None:

            max_budget = decimal_value(
                max_budget,
                "maximum budget"
            )

    except ValueError as exc:

        return json_error(
            str(exc)
        )

    if (
        min_budget is not None
        and max_budget is not None
        and min_budget > max_budget
    ):

        return json_error(
            "Minimum budget cannot exceed maximum budget"
        )

    if min_budget is not None:

        query = query.filter(
            Job.budget_max >= min_budget
        )

    if max_budget is not None:

        query = query.filter(
            Job.budget_min <= max_budget
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    query = query.order_by(

        Job.is_featured.desc(),

        Job.priority.desc(),

        Job.created_at.desc(),

        Job.id.desc()
    )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    pagination = query.paginate(

        page=page,

        per_page=per_page,

        error_out=False
    )

    jobs = [

        serialize_job(
            job,
            include_description=False,
            include_images=False
        )

        for job in pagination.items
    ]

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

        return json_error(
            "Job not found",
            404
        )

    if job.status != "open":

        return json_error(
            "This job is no longer available",
            404
        )

    # --------------------------------------------------------
    # VIEW COUNT
    # --------------------------------------------------------

    try:

        db.session.execute(

            db.update(Job)
            .where(Job.id == job.id)
            .values(
                views=(
                    func.coalesce(
                        Job.views,
                        0
                    ) + 1
                )
            )
        )

        db.session.commit()

        db.session.refresh(job)

    except Exception as exc:

        db.session.rollback()

        print(
            "[JOB VIEW ERROR]",
            exc
        )

    return jsonify({

        "status": "success",

        "job": serialize_job(

            job,

            include_description=True,

            include_images=True,

            include_owner=True
        )

    }), 200


# ============================================================
# CREATE JOB
# POST /api/jobs/create
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

    user = get_current_user()

    if not user:

        return json_error(
            "User not found",
            401
        )

    if not user.is_active:

        return json_error(
            "Your account has been disabled",
            403
        )

    data = request.get_json(
        silent=True
    )

    if not isinstance(
        data,
        dict
    ):

        return json_error(
            "Request body is required"
        )

    # ========================================================
    # BASIC INPUTS
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

    # ========================================================
    # TITLE
    # ========================================================

    if (
        not isinstance(title, str)
        or not title.strip()
    ):

        return json_error(
            "Job title is required"
        )

    title = title.strip()

    if len(title) < 3:

        return json_error(
            "Job title must contain at least 3 characters"
        )

    if len(title) > MAX_TITLE_LENGTH:

        return json_error(
            "Job title cannot exceed 200 characters"
        )

    # ========================================================
    # DESCRIPTION
    # ========================================================

    if (
        not isinstance(description, str)
        or not description.strip()
    ):

        return json_error(
            "Job description is required"
        )

    description = description.strip()

    if len(description) > MAX_DESCRIPTION_LENGTH:

        return json_error(
            "Job description cannot exceed 5000 characters"
        )

    # ========================================================
    # CATEGORY
    # ========================================================

    try:

        category_id = int(
            category_id
        )

    except (
        TypeError,
        ValueError
    ):

        return json_error(
            "Invalid category"
        )

    category = db.session.get(
        Category,
        category_id
    )

    if not category:

        return json_error(
            "Invalid category"
        )

    if not category.is_active:

        return json_error(
            "This category is currently unavailable"
        )

    # ========================================================
    # LOCATION
    # ========================================================

    if (
        not isinstance(location, str)
        or not location.strip()
    ):

        return json_error(
            "Location is required"
        )

    location = location.strip()

    if len(location) > MAX_LOCATION_LENGTH:

        return json_error(
            "Location cannot exceed 255 characters"
        )

    # ========================================================
    # BUDGET
    # ========================================================

    try:

        budget_min = decimal_value(
            data.get("budget_min"),
            "minimum budget"
        )

        budget_max = decimal_value(
            data.get("budget_max"),
            "maximum budget"
        )

    except ValueError as exc:

        return json_error(
            str(exc)
        )

    if (
        budget_min is not None
        and budget_max is not None
        and budget_min > budget_max
    ):

        return json_error(
            "Minimum budget cannot exceed maximum budget"
        )

    # ========================================================
    # OPTIONAL LOCATION DATA
    # ========================================================

    try:

        city = clean_optional_text(
            data.get("city"),
            100
        )

        state = clean_optional_text(
            data.get("state"),
            100
        )

        pincode = clean_optional_text(
            data.get("pincode"),
            10
        )

        latitude = coordinate_value(
            data.get("latitude"),
            "latitude",
            -90,
            90
        )

        longitude = coordinate_value(
            data.get("longitude"),
            "longitude",
            -180,
            180
        )

    except ValueError as exc:

        return json_error(
            str(exc)
        )

    # ========================================================
    # PRIORITY
    # ========================================================

    priority = str(
        data.get(
            "priority",
            "normal"
        )
    ).strip().lower()

    if priority not in PRIORITIES:

        return json_error(
            "Invalid priority"
        )

    # ========================================================
    # CREATE
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

        status="open",

        is_featured=False,

        views=0
    )

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

        return json_error(
            "Unable to create job. Please try again.",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Job posted successfully",

        "job": serialize_job(

            job,

            include_description=True,

            include_images=True,

            include_owner=True
        )

    }), 201


# ============================================================
# UPDATE JOB
# PUT /api/jobs/<job_id>
# PATCH /api/jobs/<job_id>
# ============================================================

@jobs_bp.route(
    "/<int:job_id>",
    methods=["PUT", "PATCH"]
)
@role_required(
    "customer",
    "worker",
    "admin"
)
def update_job(job_id):

    user = get_current_user()

    if not user:

        return json_error(
            "User not found",
            401
        )

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return json_error(
            "Job not found",
            404
        )

    # ========================================================
    # OWNERSHIP
    #
    # Admin can edit any job.
    # Normal users can edit only their own job.
    # ========================================================

    if (
        user.role != "admin"
        and job.customer_id != user.id
    ):

        return json_error(
            "You can only edit your own jobs",
            403
        )

    if job.status not in {
        "open",
        "paused"
    }:

        return json_error(
            "Only active jobs can be edited"
        )

    data = request.get_json(
        silent=True
    )

    if not isinstance(
        data,
        dict
    ):

        return json_error(
            "Request body is required"
        )

    # ========================================================
    # TITLE
    # ========================================================

    if "title" in data:

        title = data.get(
            "title"
        )

        if (
            not isinstance(title, str)
            or not title.strip()
        ):

            return json_error(
                "Title cannot be empty"
            )

        title = title.strip()

        if len(title) < 3:

            return json_error(
                "Title must contain at least 3 characters"
            )

        if len(title) > MAX_TITLE_LENGTH:

            return json_error(
                "Title cannot exceed 200 characters"
            )

        job.title = title

    # ========================================================
    # DESCRIPTION
    # ========================================================

    if "description" in data:

        description = data.get(
            "description"
        )

        if (
            not isinstance(description, str)
            or not description.strip()
        ):

            return json_error(
                "Description cannot be empty"
            )

        description = description.strip()

        if len(description) > MAX_DESCRIPTION_LENGTH:

            return json_error(
                "Description cannot exceed 5000 characters"
            )

        job.description = description

    # ========================================================
    # CATEGORY
    # ========================================================

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

            return json_error(
                "Invalid category"
            )

        category = db.session.get(
            Category,
            category_id
        )

        if not category:

            return json_error(
                "Invalid category"
            )

        if not category.is_active:

            return json_error(
                "This category is currently unavailable"
            )

        job.category_id = category.id

    # ========================================================
    # BUDGET
    # ========================================================

    try:

        if "budget_min" in data:

            job.budget_min = decimal_value(
                data.get("budget_min"),
                "minimum budget"
            )

        if "budget_max" in data:

            job.budget_max = decimal_value(
                data.get("budget_max"),
                "maximum budget"
            )

    except ValueError as exc:

        return json_error(
            str(exc)
        )

    if (
        job.budget_min is not None
        and job.budget_max is not None
        and job.budget_min > job.budget_max
    ):

        return json_error(
            "Minimum budget cannot exceed maximum budget"
        )

    # ========================================================
    # LOCATION
    # ========================================================

    if "location" in data:

        location = data.get(
            "location"
        )

        if (
            not isinstance(location, str)
            or not location.strip()
        ):

            return json_error(
                "Location cannot be empty"
            )

        location = location.strip()

        if len(location) > MAX_LOCATION_LENGTH:

            return json_error(
                "Location cannot exceed 255 characters"
            )

        job.location = location

    # ========================================================
    # CITY
    # ========================================================

    if "city" in data:

        try:

            job.city = clean_optional_text(
                data.get("city"),
                100
            )

        except ValueError as exc:

            return json_error(
                str(exc)
            )

    # ========================================================
    # STATE
    # ========================================================

    if "state" in data:

        try:

            job.state = clean_optional_text(
                data.get("state"),
                100
            )

        except ValueError as exc:

            return json_error(
                str(exc)
            )

    # ========================================================
    # PINCODE
    # ========================================================

    if "pincode" in data:

        try:

            job.pincode = clean_optional_text(
                data.get("pincode"),
                10
            )

        except ValueError as exc:

            return json_error(
                str(exc)
            )

    # ========================================================
    # COORDINATES
    # ========================================================

    try:

        if "latitude" in data:

            job.latitude = coordinate_value(
                data.get("latitude"),
                "latitude",
                -90,
                90
            )

        if "longitude" in data:

            job.longitude = coordinate_value(
                data.get("longitude"),
                "longitude",
                -180,
                180
            )

    except ValueError as exc:

        return json_error(
            str(exc)
        )

    # ========================================================
    # PRIORITY
    # ========================================================

    if "priority" in data:

        priority = str(
            data.get(
                "priority"
            )
        ).strip().lower()

        if priority not in PRIORITIES:

            return json_error(
                "Invalid priority"
            )

        job.priority = priority

    # ========================================================
    # STATUS
    #
    # Only admin can directly set arbitrary status.
    # Owner can pause/reopen their own job.
    # ========================================================

    if "status" in data:

        requested_status = str(
            data.get(
                "status"
            )
        ).strip().lower()

        if requested_status not in JOB_STATUSES:

            return json_error(
                "Invalid job status"
            )

        if user.role != "admin":

            allowed_owner_statuses = {
                "open",
                "paused"
            }

            if requested_status not in allowed_owner_statuses:

                return json_error(
                    "You are not allowed to set this job status",
                    403
                )

        job.status = requested_status

    # ========================================================
    # SAVE
    # ========================================================

    try:

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[UPDATE JOB ERROR]",
            exc
        )

        return json_error(
            "Unable to update job. Please try again.",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Job updated successfully",

        "job": serialize_job(

            job,

            include_description=True,

            include_images=True,

            include_owner=True
        )

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
    "customer",
    "worker",
    "admin"
)
def delete_job(job_id):

    user = get_current_user()

    if not user:

        return json_error(
            "User not found",
            401
        )

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return json_error(
            "Job not found",
            404
        )

    if (
        user.role != "admin"
        and job.customer_id != user.id
    ):

        return json_error(
            "You can only delete your own jobs",
            403
        )

    if (
        user.role != "admin"
        and job.status not in {
            "open",
            "paused"
        }
    ):

        return json_error(
            "Only active jobs can be deleted"
        )

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

        return json_error(
            "Unable to delete job. Please try again.",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Job deleted successfully"

    }), 200


# ============================================================
# JOB IMAGES
# POST /api/jobs/<job_id>/images
#
# Accepts already uploaded image URLs/paths.
# Cloudinary upload can be connected separately.
# ============================================================

@jobs_bp.route(
    "/<int:job_id>/images",
    methods=["POST"]
)
@role_required(
    "customer",
    "worker",
    "admin"
)
def add_job_images(job_id):

    user = get_current_user()

    if not user:

        return json_error(
            "User not found",
            401
        )

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return json_error(
            "Job not found",
            404
        )

    if (
        user.role != "admin"
        and job.customer_id != user.id
    ):

        return json_error(
            "You can only add images to your own job",
            403
        )

    data = request.get_json(
        silent=True
    )

    if not isinstance(
        data,
        dict
    ):

        return json_error(
            "Request body is required"
        )

    images = data.get(
        "images"
    )

    if not isinstance(
        images,
        list
    ):

        return json_error(
            "images must be an array"
        )

    if not images:

        return json_error(
            "At least one image is required"
        )

    current_count = len(
        job.images
    )

    if (
        current_count + len(images)
        > MAX_IMAGES_PER_JOB
    ):

        return json_error(
            f"A job can have maximum {MAX_IMAGES_PER_JOB} images"
        )

    created_images = []

    for image_path in images:

        if not isinstance(
            image_path,
            str
        ):

            continue

        image_path = image_path.strip()

        if not image_path:

            continue

        if len(image_path) > 1000:

            return json_error(
                "Image URL is too long"
            )

        image = JobImage(

            job_id=job.id,

            image_path=image_path
        )

        db.session.add(
            image
        )

        created_images.append(
            image
        )

    if not created_images:

        return json_error(
            "No valid images were provided"
        )

    try:

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[JOB IMAGE ERROR]",
            exc
        )

        return json_error(
            "Unable to save job images",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Job images added successfully",

        "images": [

            serialize_job_image(
                image
            )

            for image in created_images
        ]

    }), 201


# ============================================================
# DELETE JOB IMAGE
# DELETE /api/jobs/<job_id>/images/<image_id>
# ============================================================

@jobs_bp.route(
    "/<int:job_id>/images/<int:image_id>",
    methods=["DELETE"]
)
@role_required(
    "customer",
    "worker",
    "admin"
)
def delete_job_image(
    job_id,
    image_id
):

    user = get_current_user()

    if not user:

        return json_error(
            "User not found",
            401
        )

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return json_error(
            "Job not found",
            404
        )

    if (
        user.role != "admin"
        and job.customer_id != user.id
    ):

        return json_error(
            "You can only modify your own job",
            403
        )

    image = JobImage.query.filter_by(

        id=image_id,

        job_id=job.id

    ).first()

    if not image:

        return json_error(
            "Job image not found",
            404
        )

    try:

        db.session.delete(
            image
        )

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[DELETE JOB IMAGE ERROR]",
            exc
        )

        return json_error(
            "Unable to delete image",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Job image deleted successfully"

    }), 200


# ============================================================
# CREATE APPLICATION
# POST /api/jobs/<job_id>/apply
#
# Worker only
# ============================================================

@jobs_bp.route(
    "/<int:job_id>/apply",
    methods=["POST"]
)
@role_required(
    "worker"
)
def apply_for_job(job_id):

    worker = get_current_user()

    if not worker:

        return json_error(
            "Worker not found",
            401
        )

    if not worker.is_active:

        return json_error(
            "Your account has been disabled",
            403
        )

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return json_error(
            "Job not found",
            404
        )

    if job.status != "open":

        return json_error(
            "This job is no longer accepting applications",
            400
        )

    # --------------------------------------------------------
    # Prevent owner from applying to own job
    # --------------------------------------------------------

    if job.customer_id == worker.id:

        return json_error(
            "You cannot apply to your own job",
            403
        )

    data = request.get_json(
        silent=True
    )

    if not isinstance(
        data,
        dict
    ):

        return json_error(
            "Request body is required"
        )

    # --------------------------------------------------------
    # DUPLICATE APPLICATION
    # --------------------------------------------------------

    existing = JobApplication.query.filter_by(

        job_id=job.id,

        worker_id=worker.id

    ).first()

    if existing:

        return json_error(
            "You have already applied for this job",
            409
        )

    # --------------------------------------------------------
    # AMOUNT
    # --------------------------------------------------------

    try:

        proposed_amount = decimal_value(
            data.get(
                "proposed_amount"
            ),
            "proposed amount",
            allow_none=False
        )

    except ValueError as exc:

        return json_error(
            str(exc)
        )

    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    message = data.get(
        "message"
    )

    if message is not None:

        if not isinstance(
            message,
            str
        ):

            return json_error(
                "Invalid message"
            )

        message = message.strip()

        if len(message) > 3000:

            return json_error(
                "Application message cannot exceed 3000 characters"
            )

        if not message:

            message = None

    # --------------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------------

    availability = data.get(
        "availability"
    )

    if availability is not None:

        if not isinstance(
            availability,
            str
        ):

            return json_error(
                "Invalid availability"
            )

        availability = availability.strip()

        if len(availability) > 100:

            return json_error(
                "Availability cannot exceed 100 characters"
            )

        if not availability:

            availability = None

    application = JobApplication(

        job_id=job.id,

        worker_id=worker.id,

        proposed_amount=proposed_amount,

        message=message,

        availability=availability,

        status="pending"
    )

    try:

        db.session.add(
            application
        )

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[APPLICATION ERROR]",
            exc
        )

        return json_error(
            "Unable to submit application. Please try again.",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Application submitted successfully",

        "application": serialize_application(
            application,
            include_job=True
        )

    }), 201


# ============================================================
# MY APPLICATIONS
# GET /api/jobs/my-applications
# ============================================================

@jobs_bp.route(
    "/my-applications",
    methods=["GET"]
)
@role_required(
    "worker"
)
def my_applications():

    worker = get_current_user()

    if not worker:

        return json_error(
            "Worker not found",
            401
        )

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
                12,
                type=int
            ),
            1
        ),
        50
    )

    query = (

        JobApplication.query

        .filter(
            JobApplication.worker_id
            == worker.id
        )

        .order_by(
            JobApplication.created_at.desc()
        )
    )

    pagination = query.paginate(

        page=page,

        per_page=per_page,

        error_out=False
    )

    return jsonify({

        "status": "success",

        "applications": [

            serialize_application(
                application,
                include_job=True
            )

            for application in pagination.items
        ],

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
# JOB APPLICATIONS
# GET /api/jobs/<job_id>/applications
#
# Job owner + admin
# ============================================================

@jobs_bp.route(
    "/<int:job_id>/applications",
    methods=["GET"]
)
@role_required(
    "customer",
    "worker",
    "admin"
)
def job_applications(job_id):

    user = get_current_user()

    if not user:

        return json_error(
            "User not found",
            401
        )

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return json_error(
            "Job not found",
            404
        )

    if (
        user.role != "admin"
        and job.customer_id != user.id
    ):

        return json_error(
            "You are not allowed to view these applications",
            403
        )

    applications = (

        JobApplication.query

        .filter(
            JobApplication.job_id
            == job.id
        )

        .order_by(
            JobApplication.created_at.desc()
        )

        .all()
    )

    return jsonify({

        "status": "success",

        "job": {

            "id": job.id,

            "title": job.title,

            "status": job.status
        },

        "applications": [

            serialize_application(
                application
            )

            for application in applications
        ],

        "count": len(
            applications
        )

    }), 200


# ============================================================
# UPDATE APPLICATION STATUS
# PATCH /api/jobs/applications/<application_id>
#
# Job owner OR admin
# ============================================================

@jobs_bp.route(
    "/applications/<int:application_id>",
    methods=["PATCH"]
)
@role_required(
    "customer",
    "admin"
)
def update_application_status(
    application_id
):

    user = get_current_user()

    if not user:

        return json_error(
            "User not found",
            401
        )

    application = db.session.get(
        JobApplication,
        application_id
    )

    if not application:

        return json_error(
            "Application not found",
            404
        )

    job = application.job

    if not job:

        return json_error(
            "Related job not found",
            404
        )

    if (
        user.role != "admin"
        and job.customer_id != user.id
    ):

        return json_error(
            "You are not allowed to update this application",
            403
        )

    data = request.get_json(
        silent=True
    )

    if not isinstance(
        data,
        dict
    ):

        return json_error(
            "Request body is required"
        )

    new_status = str(
        data.get(
            "status",
            ""
        )
    ).strip().lower()

    if new_status not in APPLICATION_STATUSES:

        return json_error(
            "Invalid application status"
        )

    # --------------------------------------------------------
    # Accepted application
    # --------------------------------------------------------

    if new_status == "accepted":

        if job.status != "open":

            return json_error(
                "Only open jobs can accept an application"
            )

        # Reject other pending/shortlisted applications
        # after successful acceptance.

        application.status = "accepted"

        job.status = "assigned"

        JobApplication.query.filter(

            JobApplication.job_id == job.id,

            JobApplication.id != application.id,

            JobApplication.status.in_([
                "pending",
                "shortlisted"
            ])

        ).update(

            {
                JobApplication.status: "rejected"
            },

            synchronize_session=False
        )

    else:

        application.status = new_status

    try:

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[APPLICATION STATUS ERROR]",
            exc
        )

        return json_error(
            "Unable to update application",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Application status updated successfully",

        "application": serialize_application(
            application,
            include_job=True
        )

    }), 200


# ============================================================
# WITHDRAW APPLICATION
# DELETE /api/jobs/applications/<application_id>
#
# Worker only
# ============================================================

@jobs_bp.route(
    "/applications/<int:application_id>",
    methods=["DELETE"]
)
@role_required(
    "worker"
)
def withdraw_application(
    application_id
):

    worker = get_current_user()

    if not worker:

        return json_error(
            "Worker not found",
            401
        )

    application = db.session.get(
        JobApplication,
        application_id
    )

    if not application:

        return json_error(
            "Application not found",
            404
        )

    if application.worker_id != worker.id:

        return json_error(
            "You can only withdraw your own application",
            403
        )

    if application.status in {
        "accepted",
        "rejected"
    }:

        return json_error(
            "This application cannot be withdrawn"
        )

    application.status = "withdrawn"

    try:

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[WITHDRAW APPLICATION ERROR]",
            exc
        )

        return json_error(
            "Unable to withdraw application",
            500
        )

    return jsonify({

        "status": "success",

        "message": "Application withdrawn successfully"

    }), 200


# ============================================================
# ACTIVE CATEGORIES
# GET /api/jobs/categories
# ============================================================

@jobs_bp.route(
    "/categories",
    methods=["GET"]
)
def categories():

    try:

        ensure_default_categories()

        category_list = (

            Category.query

            .filter(
                Category.is_active.is_(True)
            )

            .order_by(
                Category.name.asc()
            )

            .all()
        )

        data = [

            serialize_category(
                category
            )

            for category in category_list
        ]

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

        return json_error(
            "Unable to load categories",
            500
        )
