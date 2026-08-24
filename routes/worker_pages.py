import os
import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    current_app,
    flash
)

from utils.cloudinary_config import (
    upload_image,
    delete_image,
    validate_image
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from werkzeug.utils import secure_filename

from extensions import db

from models.user import User
from models.worker import WorkerProfile


# =========================================================
# WORKER PAGES BLUEPRINT
# =========================================================

worker_pages_bp = Blueprint(
    "worker_pages",
    __name__
)


# =========================================================
# ALLOWED IMAGE TYPES
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


# =========================================================
# IMAGE VALIDATION
# =========================================================

def allowed_image(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    return extension in ALLOWED_IMAGE_EXTENSIONS


# =========================================================
# SAVE WORKER IMAGE
# =========================================================

def save_worker_image(file, folder):

    if not file:
        return None

    if not file.filename:
        return None

    if not allowed_image(file.filename):

        return None

    extension = (
        file.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    filename = (
        f"{uuid.uuid4().hex}"
        f".{extension}"
    )

    upload_dir = os.path.join(
        current_app.static_folder,
        "uploads",
        "workers",
        folder
    )

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    filepath = os.path.join(
        upload_dir,
        filename
    )

    file.save(filepath)

    return (
        f"/static/uploads/workers/"
        f"{folder}/{filename}"
    )


# =========================================================
# DELETE OLD IMAGE
# =========================================================

def delete_worker_image(image_path):

    if not image_path:
        return

    if not image_path.startswith(
        "/static/uploads/workers/"
    ):
        return

    relative_path = image_path.lstrip("/")

    filepath = os.path.join(
        current_app.root_path,
        relative_path
    )

    try:

        if os.path.exists(filepath):
            os.remove(filepath)

    except OSError:

        pass


# =========================================================
# CURRENT WORKER HELPER
# =========================================================

def get_current_worker():

    identity = get_jwt_identity()

    if identity is None:
        return None, None

    try:

        user_id = int(identity)

    except (
        TypeError,
        ValueError
    ):

        return None, None

    user = db.session.get(
        User,
        user_id
    )

    if user is None:
        return None, None

    if user.role != "worker":
        return None, None

    worker = user.worker_profile

    return user, worker


# =========================================================
# WORKER DASHBOARD
# =========================================================

@worker_pages_bp.route(
    "/worker/dashboard",
    methods=["GET"]
)
@jwt_required()
def worker_dashboard_page():

    user, worker = get_current_worker()

    if user is None:

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "worker/dashboard.html",
        user=user,
        worker=worker
    )


# =========================================================
# WORKER PROFILE
# =========================================================

@worker_pages_bp.route(
    "/worker/profile",
    methods=["GET"]
)
@jwt_required()
def worker_profile_page():

    user, worker = get_current_worker()

    if user is None:

        return redirect(
            url_for("auth.login")
        )

    if worker is None:

        return redirect(
            url_for(
                "worker_pages.worker_dashboard_page"
            )
        )

    return render_template(
        "worker/profile.html",
        user=user,
        worker=worker
    )


# =========================================================
# EDIT WORKER PROFILE
# =========================================================
@worker_pages_bp.route(
    "/worker/profile/edit",
    methods=["GET", "POST"]
)
@jwt_required()
def edit_profile():

    user_id = get_jwt_identity()

    try:

        user_id = int(user_id)

    except (
        TypeError,
        ValueError
    ):

        return redirect(
            url_for("auth.login")
        )

    user = db.session.get(
        User,
        user_id
    )

    if user is None:

        return redirect(
            url_for("auth.login")
        )

    if user.role != "worker":

        return redirect(
            url_for("auth.login")
        )

    worker = WorkerProfile.query.filter_by(
        user_id=user.id
    ).first()

    if worker is None:

        worker = WorkerProfile(
            user_id=user.id,
            profession=""
        )

        db.session.add(worker)

        db.session.commit()


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # BASIC INFORMATION
        # -------------------------------------------------

        user.full_name = (
            request.form.get(
                "full_name",
                ""
            ).strip()
        )

        worker.profession = (
            request.form.get(
                "profession",
                ""
            ).strip()
        )

        worker.headline = (
            request.form.get(
                "headline",
                ""
            ).strip()
            or None
        )

        worker.about = (
            request.form.get(
                "about",
                ""
            ).strip()
            or None
        )


        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        worker.address = (
            request.form.get(
                "address",
                ""
            ).strip()
            or None
        )

        worker.city = (
            request.form.get(
                "city",
                ""
            ).strip()
            or None
        )

        worker.state = (
            request.form.get(
                "state",
                ""
            ).strip()
            or None
        )

        worker.pincode = (
            request.form.get(
                "pincode",
                ""
            ).strip()
            or None
        )

        worker.service_area = (
            request.form.get(
                "service_area",
                ""
            ).strip()
            or None
        )


        # -------------------------------------------------
        # EXPERIENCE
        # -------------------------------------------------

        experience = request.form.get(
            "experience_years"
        )

        if experience:

            try:

                experience = int(
                    experience
                )

                if experience < 0:
                    experience = 0

                worker.experience_years = (
                    experience
                )

            except ValueError:

                worker.experience_years = 0


        # -------------------------------------------------
        # HOURLY RATE
        # -------------------------------------------------

        hourly_rate = request.form.get(
            "hourly_rate"
        )

        if hourly_rate:

            try:

                worker.hourly_rate = float(
                    hourly_rate
                )

            except ValueError:

                worker.hourly_rate = None

        else:

            worker.hourly_rate = None


        # -------------------------------------------------
        # MINIMUM CHARGE
        # -------------------------------------------------

        minimum_charge = request.form.get(
            "minimum_charge"
        )

        if minimum_charge:

            try:

                worker.minimum_charge = float(
                    minimum_charge
                )

            except ValueError:

                worker.minimum_charge = None

        else:

            worker.minimum_charge = None


        # -------------------------------------------------
        # AVAILABILITY
        # -------------------------------------------------

        worker.availability = (
            request.form.get(
                "availability",
                ""
            ).strip()
            or None
        )

        worker.is_available = (
            request.form.get(
                "is_available"
            ) == "on"
        )


        # =================================================
        # PROFILE IMAGE — CLOUDINARY
        # =================================================

        profile_file = request.files.get(
            "profile_image"
        )

        if (
            profile_file
            and profile_file.filename
        ):

            if not validate_image(
                profile_file
            ):

                flash(
                    "Invalid profile image. "
                    "Use JPG, JPEG, PNG or WEBP "
                    "under 8MB.",
                    "error"
                )

            else:

                try:

                    result = upload_image(
                        profile_file,
                        "sfworks/workers/profile"
                    )

                    if result:

                        old_image = (
                            worker.profile_image
                        )

                        worker.profile_image = (
                            result["secure_url"]
                        )

                        if old_image:

                            delete_image(
                                old_image
                            )

                except Exception:

                    current_app.logger.exception(
                        "Profile image upload failed"
                    )

                    flash(
                        "Profile image upload failed.",
                        "error"
                    )


        # =================================================
        # COVER IMAGE — CLOUDINARY
        # =================================================

        cover_file = request.files.get(
            "cover_image"
        )

        if (
            cover_file
            and cover_file.filename
        ):

            if not validate_image(
                cover_file
            ):

                flash(
                    "Invalid cover image. "
                    "Use JPG, JPEG, PNG or WEBP "
                    "under 8MB.",
                    "error"
                )

            else:

                try:

                    result = upload_image(
                        cover_file,
                        "sfworks/workers/cover"
                    )

                    if result:

                        old_image = (
                            worker.cover_image
                        )

                        worker.cover_image = (
                            result["secure_url"]
                        )

                        if old_image:

                            delete_image(
                                old_image
                            )

                except Exception:

                    current_app.logger.exception(
                        "Cover image upload failed"
                    )

                    flash(
                        "Cover image upload failed.",
                        "error"
                    )


        # =================================================
        # PROFILE COMPLETION
        # =================================================

        required_fields = [

            worker.profession,

            worker.headline,

            worker.about,

            worker.service_area

        ]

        worker.profile_completed = all(
            field not in (None, "")
            for field in required_fields
        )


        # =================================================
        # SAVE DATABASE
        # =================================================

        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "Worker profile database update failed"
            )

            flash(
                "Unable to save profile.",
                "error"
            )

            return redirect(
                url_for(
                    "worker_pages.edit_profile"
                )
            )


        flash(
            "Your profile has been updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "worker_pages.worker_profile_page"
            )
        )


    # =====================================================
    # GET
    # =====================================================

    return render_template(
        "worker/edit_profile.html",
        user=user,
        worker=worker
        )

            
         
            
# =========================================================
# WORKER JOBS
# =========================================================

@worker_pages_bp.route(
    "/worker/jobs",
    methods=["GET"]
)
@jwt_required()
def worker_jobs_page():

    user, worker = get_current_worker()

    if user is None:

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "worker/jobs.html",
        user=user,
        worker=worker
    )


# =========================================================
# WORKER APPLICATIONS
# =========================================================

@worker_pages.route("/worker/applications")
@jwt_required()
def worker_applications_page():

    user = get_current_user()

    worker = WorkerProfile.query.filter_by(
        user_id=user.id
    ).first()

    if not worker:
        abort(404)

    applications = []

    # এখানে আপনার Application model অনুযায়ী
    # authenticated worker-এর applications query করবেন।

    return render_template(
        "worker/applications.html",
        user=user,
        worker=worker,
        applications=applications
    )


# =========================================================
# WORKER SETTINGS
# =========================================================

@worker_pages_bp.route(
    "/worker/settings",
    methods=["GET"]
)
@jwt_required()
def worker_settings_page():

    user, worker = get_current_worker()

    if user is None:

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "worker/settings.html",
        user=user,
        worker=worker
    )
