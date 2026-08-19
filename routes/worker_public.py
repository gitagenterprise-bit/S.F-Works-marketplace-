from flask import (
    Blueprint,
    render_template,
    request
)

from sqlalchemy import or_

from extensions import db

from models.worker import WorkerProfile
from models.worker_skill import WorkerSkill



worker_public_bp = Blueprint(
    "worker_public",
    __name__
)


# ============================================================
# PUBLIC WORKERS
# GET /workers
# ============================================================

@worker_public_bp.route(
    "/workers",
    methods=["GET"]
)
def workers_page():

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

    profession = request.args.get(
        "profession",
        "",
        type=str
    ).strip()

    verified = request.args.get(
        "verified",
        "",
        type=str
    ).strip()

    query = (
        WorkerProfile.query
        .filter(
            WorkerProfile.profile_completed.is_(True)
        )
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:

        pattern = f"%{search}%"

        query = query.filter(
            or_(
                WorkerProfile.profession.ilike(pattern),
                WorkerProfile.headline.ilike(pattern),
                WorkerProfile.about.ilike(pattern),
                WorkerProfile.service_area.ilike(pattern),
                WorkerProfile.city.ilike(pattern)
            )
        )

    # --------------------------------------------------------
    # City
    # --------------------------------------------------------

    if city:

        query = query.filter(
            WorkerProfile.city.ilike(
                f"%{city}%"
            )
        )

    # --------------------------------------------------------
    # Profession
    # --------------------------------------------------------

    if profession:

        query = query.filter(
            WorkerProfile.profession.ilike(
                f"%{profession}%"
            )
        )

    # --------------------------------------------------------
    # Verified
    # --------------------------------------------------------

    if verified == "1":

        query = query.filter(
            WorkerProfile.is_verified.is_(True)
        )

    # --------------------------------------------------------
    # Ordering
    # --------------------------------------------------------

    workers = (
        query
        .order_by(
            WorkerProfile.is_verified.desc(),
            WorkerProfile.rating.desc(),
            WorkerProfile.total_reviews.desc(),
            WorkerProfile.created_at.desc()
        )
        .all()
    )

    return render_template(
        "public/workers.html",
        workers=workers,
        search=search,
        city=city,
        profession=profession,
        verified=verified
    )


# ============================================================
# PUBLIC WORKER PROFILE
# GET /workers/<worker_id>
# ============================================================

@worker_public_bp.route(
    "/workers/<int:worker_id>",
    methods=["GET"]
)
def worker_public_profile(worker_id):

    worker = db.session.get(
        WorkerProfile,
        worker_id
    )

    if not worker:

        return render_template(
            "errors/404.html"
        ), 404

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skills = (
        WorkerSkill.query
        .filter_by(
            worker_id=worker.id
        )
        .order_by(
            WorkerSkill.experience_years.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Portfolio
    # --------------------------------------------------------

    portfolio_items = (
        WorkerPortfolio.query
        .filter_by(
            worker_id=worker.id
        )
        .order_by(
            WorkerPortfolio.project_date.desc(),
            WorkerPortfolio.created_at.desc()
        )
        .all()
    )

    return render_template(
        "public/worker-details.html",
        worker=worker,
        skills=skills,
        portfolio_items=portfolio_items
  )
