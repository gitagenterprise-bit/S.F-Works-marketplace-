from flask import (
    Flask,
    jsonify,
    render_template
)

from sqlalchemy import (
    inspect,
    text
)

from config import Config

from extensions import (
    db,
    migrate,
    jwt
)

from utils.cloudinary_config import (
    init_cloudinary
)


# ============================================================
# DATABASE COMPATIBILITY HELPERS
# ============================================================

def _get_existing_columns(table_name):
    """
    Return existing column names for a database table.
    """

    inspector = inspect(db.engine)

    if table_name not in inspector.get_table_names():
        return set()

    return {
        column["name"]
        for column in inspector.get_columns(table_name)
    }


def _add_missing_columns(
    table_name,
    required_columns
):
    """
    Add missing columns to an existing table.

    This helper is intentionally used only for backward
    compatibility with an existing production database.
    """

    existing_columns = _get_existing_columns(
        table_name
    )

    if not existing_columns:
        inspector = inspect(db.engine)

        if table_name not in inspector.get_table_names():
            print(
                f"[DB SYNC] {table_name} table does not exist. "
                f"Skipping."
            )

            return

    changed = False

    for (
        column_name,
        column_definition
    ) in required_columns.items():

        if column_name in existing_columns:
            continue

        try:

            db.session.execute(
                text(
                    f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN {column_name}
                    {column_definition}
                    """
                )
            )

            changed = True

            print(
                f"[DB SYNC] Added column: "
                f"{table_name}.{column_name}"
            )

        except Exception as exc:

            db.session.rollback()

            print(
                f"[DB SYNC ERROR] "
                f"{table_name}.{column_name}: {exc}"
            )

            raise

    if changed:

        db.session.commit()

        print(
            f"[DB SYNC] {table_name} "
            f"schema synchronization completed."
        )

    else:

        print(
            f"[DB SYNC] {table_name} "
            f"schema is already up to date."
        )


# ============================================================
# WORKER PROFILES SYNC
# ============================================================

def sync_worker_profiles_columns():
    """
    Synchronize missing WorkerProfile columns.
    """

    required_columns = {

        "headline":
            "VARCHAR(255)",

        "about":
            "TEXT",

        "profile_image":
            "VARCHAR(500)",

        "cover_image":
            "VARCHAR(500)",

        "experience_years":
            "INTEGER DEFAULT 0",

        "service_area":
            "VARCHAR(255)",

        "service_radius_km":
            "INTEGER",

        "address":
            "VARCHAR(255)",

        "city":
            "VARCHAR(100)",

        "state":
            "VARCHAR(100)",

        "pincode":
            "VARCHAR(10)",

        "latitude":
            "NUMERIC(10,7)",

        "longitude":
            "NUMERIC(10,7)",

        "hourly_rate":
            "NUMERIC(10,2)",

        "minimum_charge":
            "NUMERIC(10,2)",

        "availability":
            "VARCHAR(100)",

        "is_available":
            "BOOLEAN DEFAULT TRUE",

        "is_verified":
            "BOOLEAN DEFAULT FALSE",

        "verification_status":
            "VARCHAR(30) DEFAULT 'pending'",

        "rating":
            "NUMERIC(3,2) DEFAULT 0.00",

        "total_reviews":
            "INTEGER DEFAULT 0",

        "total_jobs":
            "INTEGER DEFAULT 0",

        "completed_jobs":
            "INTEGER DEFAULT 0",

        "profile_completed":
            "BOOLEAN DEFAULT FALSE",

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

        "updated_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }

    _add_missing_columns(
        "worker_profiles",
        required_columns
    )


# ============================================================
# JOBS SCHEMA SYNC
# ============================================================

def sync_jobs_columns():
    """
    Synchronize the existing jobs table with the current
    Job model.

    Important:
    db.create_all() does NOT add columns to an existing table.
    Therefore these compatibility columns are added manually.
    """

    required_columns = {

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        "category_id":
            "INTEGER",

        # ----------------------------------------------------
        # BASIC INFORMATION
        # ----------------------------------------------------

        "title":
            "VARCHAR(200)",

        "description":
            "TEXT",

        # ----------------------------------------------------
        # BUDGET
        # ----------------------------------------------------

        "budget_min":
            "NUMERIC(10,2)",

        "budget_max":
            "NUMERIC(10,2)",

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        "location":
            "VARCHAR(255)",

        "city":
            "VARCHAR(100)",

        "district":
            "VARCHAR(100)",

        "police_station":
            "VARCHAR(100)",

        "state":
            "VARCHAR(100)",

        "pincode":
            "VARCHAR(10)",

        "latitude":
            "NUMERIC(10,7)",

        "longitude":
            "NUMERIC(10,7)",

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        "status":
            "VARCHAR(30) DEFAULT 'open'",

        "priority":
            "VARCHAR(20) DEFAULT 'normal'",

        "is_featured":
            "BOOLEAN DEFAULT FALSE",

        # ----------------------------------------------------
        # VIEWS
        # ----------------------------------------------------

        "views":
            "INTEGER DEFAULT 0",

        # ----------------------------------------------------
        # AGENT
        # ----------------------------------------------------

        "agent_id":
            "INTEGER",

        # ----------------------------------------------------
        # MODERATION
        # ----------------------------------------------------

        "reviewed_by":
            "INTEGER",

        "reviewed_at":
            "TIMESTAMP",

        "rejection_reason":
            "TEXT",

        # ----------------------------------------------------
        # SOFT DELETE
        # ----------------------------------------------------

        "deleted_at":
            "TIMESTAMP",

        "deleted_by":
            "INTEGER",

        # ----------------------------------------------------
        # TIMESTAMPS
        # ----------------------------------------------------

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

        "updated_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }

    _add_missing_columns(
        "jobs",
        required_columns
    )


# ============================================================
# JOB IMAGES SCHEMA SYNC
# ============================================================

def sync_job_images_columns():
    """
    Synchronize job_images table.
    """

    required_columns = {

        "job_id":
            "INTEGER",

        "image_path":
            "VARCHAR(500)",

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }

    _add_missing_columns(
        "job_images",
        required_columns
    )


# ============================================================
# APPLICATION SCHEMA SYNC
# ============================================================

def sync_job_applications_columns():
    """
    Synchronize job_applications table with the current
    JobApplication model.

    Only add columns here that are actually present in your
    JobApplication model.
    """

    inspector = inspect(db.engine)

    if "job_applications" not in inspector.get_table_names():

        print(
            "[DB SYNC] job_applications table "
            "does not exist. Skipping."
        )

        return

    print(
        "[DB SYNC] job_applications "
        "table exists."
    )


# ============================================================
# MAIN DATABASE COMPATIBILITY SYNC
# ============================================================

def sync_database_schema():
    """
    Run all compatibility schema synchronizations.
    """

    print(
        "[DB SYNC] Starting database "
        "compatibility synchronization..."
    )

    sync_worker_profiles_columns()

    sync_jobs_columns()

    sync_job_images_columns()

    sync_job_applications_columns()

    print(
        "[DB SYNC] Database compatibility "
        "synchronization completed."
    )


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app():

    # ========================================================
    # CREATE FLASK APPLICATION
    # ========================================================

    app = Flask(
        __name__
    )

    # ========================================================
    # CONFIGURATION
    # ========================================================

    app.config.from_object(
        Config
    )

    # ========================================================
    # DATABASE
    # ========================================================

    db.init_app(
        app
    )

    # ========================================================
    # MIGRATION
    # ========================================================

    migrate.init_app(
        app,
        db
    )

    # ========================================================
    # JWT
    # ========================================================

    jwt.init_app(
        app
    )

    # ========================================================
    # CLOUDINARY
    # ========================================================

    init_cloudinary()

    # ========================================================
    # IMPORT ALL MODELS
    #
    # IMPORTANT:
    # Every model must be imported before mapper
    # configuration and db.create_all().
    # ========================================================

    from models import (

        User,

        CustomerProfile,

        WorkerProfile,

        WorkerPortfolio,

        Category,

        Job,

        JobImage,

        JobApplication,

        AgentProfile,

        AgentArea,

        AgentAreaAssignment,

        AgentPermission,

        AuditLog
    )

    # Prevent unused import optimization / lint issues
    _ = (
        User,
        CustomerProfile,
        WorkerProfile,
        WorkerPortfolio,
        Category,
        Job,
        JobImage,
        JobApplication,
        AgentProfile,
        AgentArea,
        AgentAreaAssignment,
        AgentPermission,
        AuditLog
    )

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    with app.app_context():

        # ----------------------------------------------------
        # Create missing tables
        # ----------------------------------------------------

        db.create_all()

        # ----------------------------------------------------
        # Synchronize existing tables
        # ----------------------------------------------------

        sync_database_schema()

    # ========================================================
    # AUTH ROUTES
    # ========================================================

    from routes.auth import (
        auth_bp,
        auth_pages_bp
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        auth_pages_bp
    )

    # ========================================================
    # CUSTOMER API
    # ========================================================

    from routes.customer import (
        customer_bp
    )

    app.register_blueprint(
        customer_bp,
        url_prefix="/api/customer"
    )

    # ========================================================
    # CUSTOMER PAGES
    # ========================================================

    from routes.customer_pages import (
        customer_page_bp
    )

    app.register_blueprint(
        customer_page_bp
    )

    # ========================================================
    # WORKER API
    # ========================================================

    from routes.worker import (
        worker_bp
    )

    app.register_blueprint(
        worker_bp,
        url_prefix="/api/worker"
    )

    # ========================================================
    # WORKER PAGES
    # ========================================================

    from routes.worker_pages import (
        worker_pages_bp
    )

    app.register_blueprint(
        worker_pages_bp
    )

    # ========================================================
    # JOB API
    # ========================================================

    from routes.jobs import (
        jobs_bp
    )

    app.register_blueprint(
        jobs_bp,
        url_prefix="/api/jobs"
    )

    # ========================================================
    # ADMIN API
    # ========================================================

    from routes.admin import (
        admin_bp
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/api/admin"
    )

    # ========================================================
    # ADMIN PAGES
    # ========================================================

    from routes.admin_pages import (
        admin_pages_bp
    )

    app.register_blueprint(
        admin_pages_bp
    )

    # ========================================================
    # JOB PAGES
    # ========================================================

    from routes.job_pages import (
        job_pages_bp
    )

    app.register_blueprint(
        job_pages_bp
    )

    # ========================================================
    # PUBLIC WORKERS
    # ========================================================

    from routes.worker_public import (
        worker_public_bp
    )

    app.register_blueprint(
        worker_public_bp
    )

    # ========================================================
    # HOME PAGE
    # ========================================================

    @app.route("/")
    def home():

        # ====================================================
        # FEATURED WORKERS
        # ====================================================

        workers = (

            WorkerProfile.query

            .filter(
                WorkerProfile.profile_completed.is_(True)
            )

            .order_by(

                WorkerProfile.is_verified.desc(),

                WorkerProfile.is_available.desc(),

                WorkerProfile.rating.desc(),

                WorkerProfile.total_reviews.desc(),

                WorkerProfile.created_at.desc()
            )

            .limit(8)

            .all()
        )

        # ====================================================
        # LATEST JOBS
        # ====================================================

        jobs = (

            Job.query

            .filter(
                Job.deleted_at.is_(None)
            )

            .filter(
                Job.status.in_([
                    "open",
                    "OPEN",
                    "active",
                    "ACTIVE"
                ])
            )

            .order_by(
                Job.created_at.desc()
            )

            .limit(8)

            .all()
        )

        # ====================================================
        # RENDER
        # ====================================================

        return render_template(

            "public/home.html",

            workers=workers,

            jobs=jobs
        )

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    @app.route("/health")
    def health():

        return jsonify({

            "status":
                "success",

            "message":
                "S. F Works Marketplace API is running",

            "service":
                "sf-works-marketplace"

        }), 200

    # ========================================================
    # API ROOT
    # ========================================================

    @app.route("/api")
    def api_root():

        return jsonify({

            "name":
                "S. F Works Marketplace",

            "version":
                "1.0.0",

            "status":
                "online"

        }), 200

    # ========================================================
    # RETURN APP
    # ========================================================

    return app
