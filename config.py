import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    # ========================================
    # FLASK
    # ========================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )


    # ========================================
    # SQLALCHEMY
    # ========================================

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ========================================
    # JWT
    # ========================================

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY"
    )

    # ----------------------------------------
    # JWT Location
    # ----------------------------------------

    JWT_TOKEN_LOCATION = [
        "cookies"
    ]

    # ----------------------------------------
    # Access Token
    # ----------------------------------------

    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60

    # ----------------------------------------
    # Refresh Token
    # ----------------------------------------

    JWT_REFRESH_TOKEN_EXPIRES = (
        30 * 24 * 60 * 60
    )

    # ----------------------------------------
    # Cookie Security
    # ----------------------------------------

    JWT_COOKIE_SECURE = True

    JWT_COOKIE_HTTPONLY = True

    JWT_COOKIE_SAMESITE = "Lax"

    # ----------------------------------------
    # CSRF
    # ----------------------------------------

    JWT_COOKIE_CSRF_PROTECT = False


    # ========================================
    # UPLOAD
    # ========================================

    MAX_CONTENT_LENGTH = (
        10 * 1024 * 1024
    )

    UPLOAD_FOLDER = os.path.join(
        os.getcwd(),
        "uploads"
    )
