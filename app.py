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
# DATABASE COMPATIBILITY SYNC
# ============================================================

def sync_table_columns(
    table_name,
    required_columns
):
    """
    Safely add missing columns to an existing PostgreSQL table.

    This is intended for compatibility with an existing Render
    PostgreSQL database where SQLAlchemy models have gained
    new columns after the original tables were created.
    """

    inspector = inspect(db.engine)

    # --------------------------------------------------------
    # TABLE CHECK
    # --------------------------------------------------------

    if table_name not in inspector.get_table_names():

        print(
            f"[DB SYNC] {table_name} table does not exist. "
            f"Skipping sync."
        )

        return


    # --------------------------------------------------------
    # EXISTING COLUMNS
    # --------------------------------------------------------

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(
            table_name
        )
    }


    changed = False


    # --------------------------------------------------------
    # ADD MISSING COLUMNS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

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
# WORKER PROFILE SCHEMA
# ============================================================

def sync_worker_profiles_columns():

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


    sync_table_columns(
        "worker_profiles",
        required_columns
    )


# ============================================================
# JOBS SCHEMA
# ============================================================

def sync_jobs_columns():

    required_columns = {

        "customer_id":
            "INTEGER",

        "category_id":
            "INTEGER",

        "title":
            "VARCHAR(255)",

        "description":
            "TEXT",

        "budget_min":
            "NUMERIC(12,2)",

        "budget_max":
            "NUMERIC(12,2)",

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

        "status":
            "VARCHAR(30) DEFAULT 'open'",

        "priority":
            "VARCHAR(30) DEFAULT 'normal'",

        "is_featured":
            "BOOLEAN DEFAULT FALSE",

        "views":
            "INTEGER DEFAULT 0",

        "agent_id":
            "INTEGER",

        "reviewed_by":
            "INTEGER",

        "reviewed_at":
            "TIMESTAMP",

        "rejection_reason":
            "TEXT",

        "deleted_at":
            "TIMESTAMP",

        "deleted_by":
            "INTEGER",

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

        "updated_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }


    sync_table_columns(
        "jobs",
        required_columns
    )


# ============================================================
# JOB APPLICATION SCHEMA
# ============================================================

def sync_job_applications_columns():

    required_columns = {

        "job_id":
            "INTEGER",

        "worker_id":
            "INTEGER",

        "proposed_amount":
            "NUMERIC(12,2)",

        "message":
            "TEXT",

        "availability":
            "VARCHAR(255)",

        "status":
            "VARCHAR(30) DEFAULT 'pending'",

        # ----------------------------------------------------
        # CUSTOMER REVIEW
        # ----------------------------------------------------

        "customer_reviewed_at":
            "TIMESTAMP",

        "customer_reviewed_by":
            "INTEGER",

        # ----------------------------------------------------
        # AGENT REVIEW
        # ----------------------------------------------------

        "agent_reviewed_at":
            "TIMESTAMP",

        "agent_reviewed_by":
            "INTEGER",

        # ----------------------------------------------------
        # ADMIN REVIEW
        # ----------------------------------------------------

        "admin_reviewed_at":
            "TIMESTAMP",

        "admin_reviewed_by":
            "INTEGER",

        # ----------------------------------------------------
        # REJECTION
        # ----------------------------------------------------

        "rejection_reason":
            "TEXT",

        # ----------------------------------------------------
        # SOFT DELETE
        # ----------------------------------------------------

        "deleted_at":
            "TIMESTAMP",

        # ----------------------------------------------------
        # TIMESTAMPS
        # ----------------------------------------------------

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

        "updated_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }


    sync_table_columns(
        "job_applications",
        required_columns
    )


# ============================================================
# DATABASE COMPATIBILITY SYNC
# ============================================================

def sync_database_schema():

    print(
        "[DB SYNC] Starting database schema "
        "compatibility synchronization..."
    )

    sync_worker_profiles_columns()

    sync_jobs_columns()

    sync_job_applications_columns()

    print(
        "[DB SYNC] Database schema "
        "compatibility synchronization completed."
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
    # FLASK-MIGRATE
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
    # Import every model before db.create_all().
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


    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    with app.app_context():

        # ----------------------------------------------------
        # Create missing tables
        # ----------------------------------------------------

        db.create_all()


        # ----------------------------------------------------
        # Existing database compatibility sync
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

        # ----------------------------------------------------
        # FEATURED WORKERS
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # LATEST OPEN JOBS
        # ----------------------------------------------------

        jobs = (

            Job.query

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


        # ----------------------------------------------------
        # RENDER
        # ----------------------------------------------------

        return render_template(
            "public/home.html",
            workers=workers,
            jobs=jobs
        )


    # ========================================================
    # HEALTH CHECK
    # ========================================================

    @app.route(
        "/health"
    )
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

    @app.route(
        "/api"
    )
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
