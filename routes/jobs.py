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


jobs_bp = Blueprint(
    "jobs",
    __name__
)

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

    query = Job.query.filter(
        Job.status == "open"
    )

    # -------------------------------
    # Search
    # -------------------------------

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
                )
            )
        )

    # -------------------------------
    # City
    # -------------------------------

    if city:

        query = query.filter(
            Job.city.ilike(
                f"%{city}%"
            )
        )

    # -------------------------------
    # Category
    # -------------------------------

    if category_id:

        query = query.filter(
            Job.category_id == category_id
        )

    # -------------------------------
    # Budget
    # -------------------------------

    if min_budget is not None:

        query = query.filter(
            Job.budget_max >= min_budget
        )

    if max_budget is not None:

        query = query.filter(
            Job.budget_min <= max_budget
        )

    # -------------------------------
    # Featured First
    # -------------------------------

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

    # Increase view count
    job.views += 1

    db.session.commit()

    images = []

    for image in job.images:

        images.append({
            "id": image.id,
            "image_path": image.image_path
        })

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
        )
    }

    return jsonify({
        "status": "success",
        "job": response
    }), 200

@jobs_bp.route(
    "/create",
    methods=["POST"]
)
@role_required("customer")
def create_job():

    user_id = get_jwt_identity()

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "Request body is required"
        }), 400

    title = data.get("title")
    description = data.get("description")
    category_id = data.get("category_id")
    location = data.get("location")

    budget_min = data.get(
        "budget_min"
    )

    budget_max = data.get(
        "budget_max"
    )

    city = data.get("city")
    state = data.get("state")
    pincode = data.get("pincode")

    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )
    allowed_priorities = {
        "normal",
        "high",
        "urgent"
    }

    priority = data.get(
        "priority",
        "normal"
    )
    if priority not in allowed_priorities:

        return jsonify({
            "status": "error",
            "message": "Invalid priority"
        }), 400

    # -------------------------------
    # Validation
    # -------------------------------

    if not title:

        return jsonify({
            "status": "error",
            "message": "Job title is required"
        }), 400

    if not description:

        return jsonify({
            "status": "error",
            "message": "Job description is required"
        }), 400

    if not category_id:

        return jsonify({
            "status": "error",
            "message": "Category is required"
        }), 400

    if not location:

        return jsonify({
            "status": "error",
            "message": "Location is required"
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
            "message": "This category is currently unavailable"
        }), 400

    # -------------------------------
    # Budget Validation
    # -------------------------------

    if (
        budget_min is not None
        and budget_max is not None
    ):

        if float(budget_min) > float(budget_max):

            return jsonify({
                "status": "error",
                "message": "Minimum budget cannot exceed maximum budget"
            }), 400

    # -------------------------------
    # Create Job
    # -------------------------------

    job = Job(

        customer_id=int(user_id),

        category_id=category.id,

        title=title.strip(),

        description=description.strip(),

        budget_min=budget_min,

        budget_max=budget_max,

        location=location.strip(),

        city=city.strip()
        if city else None,

        state=state.strip()
        if state else None,

        pincode=pincode.strip()
        if pincode else None,

        latitude=latitude,

        longitude=longitude,

        priority=priority,

        status="open"
    )

    db.session.add(job)

    db.session.commit()

    return jsonify({

        "status": "success",

        "message": "Job posted successfully",

        "job": {
            "id": job.id,
            "title": job.title,
            "status": job.status,
            "category": category.name
        }

    }), 201

@jobs_bp.route(
    "/<int:job_id>",
    methods=["PUT"]
)
@role_required("customer")
def update_job(job_id):

    user_id = get_jwt_identity()

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return jsonify({
            "status": "error",
            "message": "Job not found"
        }), 404

    if job.customer_id != int(user_id):

        return jsonify({
            "status": "error",
            "message": "You can only edit your own jobs"
        }), 403

    if job.status != "open":

        return jsonify({
            "status": "error",
            "message": "Only open jobs can be edited"
        }), 400

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "Request body is required"
        }), 400

    if "title" in data:

        if not data["title"].strip():

            return jsonify({
                "status": "error",
                "message": "Title cannot be empty"
            }), 400

        job.title = data["title"].strip()

    if "description" in data:

        if not data["description"].strip():

            return jsonify({
                "status": "error",
                "message": "Description cannot be empty"
            }), 400

        job.description = (
            data["description"].strip()
        )

    if "category_id" in data:

        category = db.session.get(
            Category,
            data["category_id"]
        )

        if not category:

            return jsonify({
                "status": "error",
                "message": "Invalid category"
            }), 400

        job.category_id = category.id

    if "budget_min" in data:

        job.budget_min = data[
            "budget_min"
        ]

    if "budget_max" in data:

        job.budget_max = data[
            "budget_max"
        ]

    if "location" in data:

        job.location = (
            data["location"].strip()
        )

    if "city" in data:

        job.city = (
            data["city"].strip()
            if data["city"]
            else None
        )

    if "state" in data:

        job.state = (
            data["state"].strip()
            if data["state"]
            else None
        )

    if "pincode" in data:

        job.pincode = (
            data["pincode"].strip()
            if data["pincode"]
            else None
        )

    if "latitude" in data:

        job.latitude = data["latitude"]

    if "longitude" in data:

        job.longitude = data["longitude"]

    if "priority" in data:

        job.priority = data[
            "priority"
        ]

    db.session.commit()

    return jsonify({

        "status": "success",

        "message": "Job updated successfully",

        "job": {
            "id": job.id,
            "title": job.title,
            "status": job.status
        }

    }), 200

@jobs_bp.route(
    "/<int:job_id>",
    methods=["DELETE"]
)
@role_required("customer")
def delete_job(job_id):

    user_id = get_jwt_identity()

    job = db.session.get(
        Job,
        job_id
    )

    if not job:

        return jsonify({
            "status": "error",
            "message": "Job not found"
        }), 404

    if job.customer_id != int(user_id):

        return jsonify({
            "status": "error",
            "message": "You can only delete your own jobs"
        }), 403

    if job.status != "open":

        return jsonify({
            "status": "error",
            "message": "Only open jobs can be deleted"
        }), 400

    db.session.delete(job)

    db.session.commit()

    return jsonify({

        "status": "success",

        "message": "Job deleted successfully"

    }), 200

# ============================================================
# ACTIVE CATEGORIES
# GET /categories
# ============================================================

@jobs_bp.route(
    "/categories",
    methods=["GET"]
)
def categories():

    try:

        # ----------------------------------------------------
        # Make sure default categories exist
        # ----------------------------------------------------

        ensure_default_categories()

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

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "status": "error",

            "message": (
                "Unable to load categories"
            )

        }), 500

