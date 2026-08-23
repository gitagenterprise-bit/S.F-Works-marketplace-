from flask import (
    Flask,
    jsonify,
    render_template
)

from sqlalchemy import (
    inspect,
    text
)

from sqlalchemy.exc import (
    SQLAlchemyError
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
# DATABASE COMPATIBILITY SYNCHRONIZATION
# ============================================================

def sync_database_schema():
    """
    Synchronize important model columns with an existing
    PostgreSQL database.

    This compatibility layer is intended for deployments where
    the database already existed before newer model fields were
    introduced.

    IMPORTANT:
    This is NOT a replacement for Flask-Migrate.

    Flask-Migrate should remain the authoritative schema
    migration system in production.
    """

    print(
        "[DB SYNC] Starting database compatibility synchronization..."
    )

    inspector = inspect(db.engine)

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    required_columns = {

        # ====================================================
        # WORKER PROFILES
        # ====================================================

        "worker_profiles": {

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
        },


        # ====================================================
        # JOBS
        # ====================================================

        "jobs": {

            "district":
                "VARCHAR(100)",

            "police_station":
                "VARCHAR(100)",

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
                "INTEGER"
        },


        # ====================================================
        # JOB APPLICATIONS
        # ====================================================

        "job_applications": {

            "customer_reviewed_at":
                "TIMESTAMP",

            "customer_reviewed_by":
                "INTEGER",

            "agent_reviewed_at":
                "TIMESTAMP",

            "agent_reviewed_by":
                "INTEGER",

            "admin_reviewed_at":
                "TIMESTAMP",

            "admin_reviewed_by":
                "INTEGER",

            "rejection_reason":
                "TEXT",

            "deleted_at":
                "TIMESTAMP",

            "created_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

            "updated_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        },


        # ====================================================
        # AUDIT LOGS
        # ====================================================

        "audit_logs": {

            "entity_type":
                "VARCHAR(50)",

            "entity_id":
                "INTEGER",

            "description":
                "TEXT",

            "ip_address":
                "VARCHAR(45)",

            "user_agent":
                "VARCHAR(500)",

            "created_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        },


        # ====================================================
        # AGENT PROFILES
        # ====================================================

        "agent_profiles": {

            "designation":
                "VARCHAR(100) DEFAULT 'Area Agent'",

            "is_verified":
                "BOOLEAN DEFAULT FALSE",

            "verification_status":
                "VARCHAR(30) DEFAULT 'pending'",

            "force_password_change":
                "BOOLEAN DEFAULT TRUE",

            "last_login_at":
                "TIMESTAMP",

            "created_by":
                "INTEGER",

            "created_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

            "updated_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        },


        # ====================================================
        # AGENT AREAS
        #
        # NOTE:
        # This corresponds to the AgentArea model inside
        # models/agent.py.
        # ====================================================

        "agent_areas": {

            "name":
                "VARCHAR(150)",

            "area_type":
                "VARCHAR(30)",

            "district":
                "VARCHAR(100)",

            "police_station":
                "VARCHAR(100)",

            "locality":
                "VARCHAR(150)",

            "pincode":
                "VARCHAR(10)",

            "state":
                "VARCHAR(100)",

            "is_active":
                "BOOLEAN DEFAULT TRUE",

            "created_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        },


        # ====================================================
        # AGENT AREA ASSIGNMENTS
        # ====================================================

        "agent_area_assignments": {

            "agent_id":
                "INTEGER",

            "area_id":
                "INTEGER",

            "assigned_by":
                "INTEGER",

            "is_active":
                "BOOLEAN DEFAULT TRUE",

            "created_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        },


        # ====================================================
        # AGENT PERMISSIONS
        # ====================================================

        "agent_permissions": {

            "agent_id":
                "INTEGER",

            "permission":
                "VARCHAR(100)",

            "is_allowed":
                "BOOLEAN DEFAULT FALSE",

            "granted_by":
                "INTEGER",

            "created_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

            "updated_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
    }


    changed = False

    # ========================================================
    # EXISTING TABLES
    # ========================================================

    existing_tables = set(
        inspector.get_table_names()
    )

    # ========================================================
    # PROCESS EVERY TABLE
    # ========================================================

    for table_name, columns in required_columns.items():

        # ----------------------------------------------------
        # TABLE DOES NOT EXIST
        # ----------------------------------------------------

        if table_name not in existing_tables:

            print(
                f"[DB SYNC] {table_name} table does not exist. "
                f"Skipping column synchronization."
            )

            continue

        # ----------------------------------------------------
        # EXISTING COLUMNS
        # ----------------------------------------------------

        current_columns = {
            column["name"]
            for column in inspector.get_columns(
                table_name
            )
        }

        # ----------------------------------------------------
        # ADD MISSING COLUMNS
        # ----------------------------------------------------

        for column_name, column_type in columns.items():

            if column_name in current_columns:
                continue

            try:

                db.session.execute(
                    text(
                        f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN {column_name} {column_type}
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
                    f"{table_name}.{column_name}: "
                    f"{exc}"
                )

                raise

    # ========================================================
    # COMMIT
    # ========================================================

    if changed:

        db.session.commit()

        print(
            "[DB SYNC] Database compatibility "
            "synchronization completed."
        )

    else:

        print(
            "[DB SYNC] Database schema is already "
            "up to date."
        )


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app():

    # ========================================================
    # CREATE APPLICATION
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
    # All models must be registered before queries are executed.
    # ========================================================

    from models import (

        User,

        CustomerProfile,

        WorkerProfile,

        WorkerPortfolio,

        WorkerSkill,

        Category,

        Job,

        JobImage,

        JobApplication,

        AgentProfile,

        AgentArea,

        AgentAreaAssignment,

        AgentPermission,

        AuditLog,

        ApprovalRecord
    )


    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    with app.app_context():

        # ----------------------------------------------------
        # CREATE MISSING TABLES
        # ----------------------------------------------------

        try:

            db.create_all()

            print(
                "[DB SYNC] Database tables verified."
            )

        except SQLAlchemyError as exc:

            db.session.rollback()

            print(
                "[DB ERROR] db.create_all() failed:"
            )

            print(exc)

            raise


        # ----------------------------------------------------
        # COMPATIBILITY SYNC
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
        # LATEST OPEN / ACTIVE JOBS
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

            .filter(
                Job.deleted_at.is_(None)
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


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = create_app()


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
