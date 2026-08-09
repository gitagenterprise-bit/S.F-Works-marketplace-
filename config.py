import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    # --------------------------------
    # Flask
    # --------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    # --------------------------------
    # SQLAlchemy
    # --------------------------------

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --------------------------------
    # JWT
    # --------------------------------

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY"
    )

    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60

    JWT_REFRESH_TOKEN_EXPIRES = 30 * 24 * 60 * 60

    # --------------------------------
    # Upload
    # --------------------------------

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(
        os.getcwd(),
        "uploads"
    )
