from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from sqlalchemy import or_

from extensions import db
from models.user import User
from models.customer import CustomerProfile
from models.worker import WorkerProfile


auth_bp = Blueprint(
    "auth",
    __name__
)
