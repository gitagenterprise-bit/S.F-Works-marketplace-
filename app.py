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


def sync_worker_profiles_columns():

    required_columns = {

        "headline": "VARCHAR(255)",
        "about": "TEXT",
        "profile_image": "VARCHAR(500)",
        "cover_image": "VARCHAR(500)",
        "experience_years": "INTEGER DEFAULT 0",

        "service_area": "VARCHAR(255)",
        "service_radius_km": "INTEGER",
        "address": "VARCHAR(255)",

        "city": "VARCHAR(100)",
        "state": "VARCHAR(100)",
        "pincode": "VARCHAR(10)",

        "latitude": "NUMERIC(10,7)",
        "longitude": "NUMERIC(10,7)",

        "hourly_rate": "NUMERIC(10,2)",
        "minimum_charge": "NUMERIC(10,2)",

        "availability": "VARCHAR(100)",
        "is_available": "BOOLEAN DEFAULT TRUE",

        "is_verified": "BOOLEAN DEFAULT FALSE",
        "verification_status":
            "VARCHAR(30) DEFAULT 'pending'",

        "rating": "NUMERIC(3,2) DEFAULT 0.00",

        "total_reviews": "INTEGER DEFAULT 0",
        "total_jobs": "INTEGER DEFAULT 0",
        "completed_jobs": "INTEGER DEFAULT 0",

        "profile_completed":
            "BOOLEAN DEFAULT FALSE",

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

        "updated_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }

    inspector = inspect(db.engine)

    if "worker_profiles" not in inspector.get_table_names():

        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(
            "worker_profiles"
        )
    }

    for column_name, column_type in required_columns.items():

        if column_name not in existing_columns:

            db.session.execute(
                text(
                    f"""
                    ALTER TABLE worker_profiles
                    ADD COLUMN {column_name} {column_type}
                    """
                )
            )

            print(
                f"[DB SYNC] Added column: "
                f"worker_profiles.{column_name}"
            )

    db.session.commit()


def create_app():

    app = Flask(__name__)

    # Configuration

    app.config.from_object(Config)

    # Extensions

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Models

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

    # Database

    with app.app_context():

        db.create_all()

        sync_worker_profiles_columns()

    # ------------------------------
    # Blueprints
    # ------------------------------

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

    from routes.customer import (
        customer_bp
    )

    app.register_blueprint(
        customer_bp,
        url_prefix="/api/customer"
    )

    from routes.worker import (
        worker_bp
    )

    app.register_blueprint(
        worker_bp,
        url_prefix="/api/worker"
    )

    from routes.worker_pages import (
        worker_pages_bp
    )

    app.register_blueprint(
        worker_pages_bp
    )

    from routes.jobs import (
        jobs_bp
    )

    app.register_blueprint(
        jobs_bp,
        url_prefix="/api/jobs"
    )

    from routes.admin import (
        admin_bp
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/api/admin"
    )

    # ------------------------------
    # Job Pages
    # ------------------------------

    from routes.job_pages import (
        job_pages_bp
    )

    app.register_blueprint(
        job_pages_bp
    )

    @app.route("/")
    def home():

        return render_template(
            "public/home.html"
        )

    @app.route("/health")
    def health():

        return jsonify({

            "status": "success",

            "message":
                "S. F Works Marketplace API is running",

            "service":
                "sf-works-marketplace"

        })

    @app.route("/api")
    def api_root():

        return jsonify({

            "name":
                "S. F Works Marketplace",

            "version":
                "1.0.0",

            "status":
                "online"

        })

    return app
