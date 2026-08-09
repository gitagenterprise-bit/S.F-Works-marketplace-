from flask import Flask, jsonify, render_template

from config import Config
from extensions import db, migrate, jwt


def create_app():

    app = Flask(
        __name__
    )

    # --------------------------------
    # Configuration
    # --------------------------------

    app.config.from_object(
        Config
    )

    # --------------------------------
    # Extensions
    # --------------------------------

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    jwt.init_app(
        app
    )

    # --------------------------------
    # Import Models
    # --------------------------------

    from models import (
        User,
        CustomerProfile,
        WorkerProfile,
        Category,
        Job,
        JobImage
    )

    # --------------------------------
    # Register Blueprints
    # --------------------------------

    from routes.auth import auth_bp
    from routes.customer import customer_bp
    from routes.worker import worker_bp
    from routes.jobs import jobs_bp
    from routes.admin import admin_bp

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        customer_bp,
        url_prefix="/api/customer"
    )

    app.register_blueprint(
        worker_bp,
        url_prefix="/api/worker"
    )

    app.register_blueprint(
        jobs_bp,
        url_prefix="/api/jobs"
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/api/admin"
    )

    # --------------------------------
    # Home
    # --------------------------------

    @app.route("/")
    def home():
        return render_template("index.html")

    # --------------------------------
    # Health Check
    # --------------------------------

    @app.route("/health")
    def health():

        return jsonify({
            "status": "success",
            "message": "S. F Works Marketplace API is running",
            "service": "sf-works-marketplace"
        })

    # --------------------------------
    # API Root
    # --------------------------------

    @app.route("/api")
    def api_root():

        return jsonify({
            "name": "S. F Works Marketplace",
            "version": "1.0.0",
            "status": "online"
        })

    return app
