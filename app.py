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

def sync_worker_profiles_columns():
    """
    Add missing worker_profiles columns to an existing database.

    This is a compatibility helper for deployments where the
    database already exists but the WorkerProfile model has
    newer fields.
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


    # ========================================================
    # DATABASE INSPECTOR
    # ========================================================

    inspector = inspect(
        db.engine
    )


    # ========================================================
    # CHECK TABLE
    # ========================================================

    if "worker_profiles" not in (
        inspector.get_table_names()
    ):

        print(
            "[DB SYNC] worker_profiles table "
            "does not exist. Skipping sync."
        )

        return


    # ========================================================
    # EXISTING COLUMNS
    # ========================================================

    existing_columns = {

        column["name"]

        for column in inspector.get_columns(
            "worker_profiles"
        )
    }


    changed = False


    # ========================================================
    # ADD MISSING COLUMNS
    # ========================================================

    for (
        column_name,
        column_type
    ) in required_columns.items():

        if column_name in existing_columns:
            continue


        try:

            db.session.execute(

                text(
                    f"""
                    ALTER TABLE worker_profiles
                    ADD COLUMN {column_name} {column_type}
                    """
                )
            )


            changed = True


            print(
                f"[DB SYNC] Added column: "
                f"worker_profiles.{column_name}"
            )


        except Exception as exc:

            db.session.rollback()


            print(
                f"[DB SYNC ERROR] "
                f"worker_profiles.{column_name}: "
                f"{exc}"
            )


            raise


    # ========================================================
    # COMMIT CHANGES
    # ========================================================

    if changed:

        db.session.commit()

        print(
            "[DB SYNC] worker_profiles "
            "schema synchronization completed."
        )

    else:

        print(
            "[DB SYNC] worker_profiles "
            "schema is already up to date."
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
    # INITIALIZE DATABASE
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
    # Import models before db.create_all() and migrations.
    # ========================================================

    from models import (

        User,

        CustomerProfile,

        WorkerProfile,

        WorkerPortfolio,

        Category,

        Job,

        JobImage,

        JobApplication
    )


    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    with app.app_context():

        # Create missing tables
        db.create_all()

        # Synchronize WorkerProfile columns
        sync_worker_profiles_columns()


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


    # ============================================================
    # HOME PAGE
    # ============================================================

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
        #
        # Only open / active jobs are displayed.
        # ====================================================

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


        # ====================================================
        # RENDER HOME PAGE
        # ====================================================

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
    # RETURN APPLICATION
    # ========================================================

    return app
