from flask import (
    Flask,
    jsonify,
    render_template
)

from config import Config

from extensions import (
    db,
    migrate,
    jwt
)


def create_app():

    app = Flask(
        __name__
    )

    # ==================================================
    # Configuration
    # ==================================================

    app.config.from_object(
        Config
    )

    # ==================================================
    # Extensions
    # ==================================================

    db.init_app(
        app
    )

    migrate.init_app(
        app,
        db
    )

    jwt.init_app(
        app
    )

    

    # ==================================================
    # Import ALL Models
    #
    # IMPORTANT:
    # Models must be imported before db.create_all()
    # ==================================================

    from models import (
        User,
        CustomerProfile,
        WorkerProfile,
        Category,
        Job,
        JobImage,
        JobApplication
    )

    # ==================================================
    # Automatically Create Database Tables
    #
    # This creates missing tables automatically on
    # first Render startup.
    #
    # Existing tables are NOT deleted.
    # ==================================================

    with app.app_context():

        db.create_all()

    # ==================================================
    # Register Blueprints
    # ==================================================

    # ------------------------------
    # Authentication
    # ------------------------------

    from routes.auth import (
        auth_bp,
        auth_pages_bp
    )

    from routes.worker import worker_bp

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        auth_pages_bp
    )

    app.register_blueprint(
        worker_bp
    )

    # ------------------------------
    # Customer API
    # ------------------------------

    from routes.customer import (
        customer_bp
    )

    app.register_blueprint(
        customer_bp,
        url_prefix="/api/customer"
    )

    # ------------------------------
    # Worker API
    # ------------------------------

    from routes.worker import (
        worker_bp
    )

    app.register_blueprint(
        worker_bp,
        url_prefix="/api/worker"
    )

    # ------------------------------
    # Jobs API
    # ------------------------------

    from routes.jobs import (
        jobs_bp
    )

    app.register_blueprint(
        jobs_bp,
        url_prefix="/api/jobs"
    )

    # ------------------------------
    # Admin API
    # ------------------------------

    from routes.admin import (
        admin_bp
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/api/admin"
    )

    # ==================================================
    # Home Page
    # ==================================================

    @app.route("/")
    def home():

        return render_template(
            "public/home.html"
        )

    # ==================================================
    # Health Check
    # ==================================================

    @app.route("/health")
    def health():

        return jsonify({

            "status":
                "success",

            "message":
                "S. F Works Marketplace API is running",

            "service":
                "sf-works-marketplace"

        })

    # ==================================================
    # API Root
    # ==================================================

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

    # ==================================================
    # Return Flask Application
    # ==================================================

    return app
