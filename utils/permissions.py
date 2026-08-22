from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity
)

from extensions import db
from models.user import User


SYSTEM_ROLES = {
    "user",
    "customer",
    "worker",
    "agent",
    "admin"
}


def get_current_user():

    identity = get_jwt_identity()

    try:
        user_id = int(identity)

    except (
        TypeError,
        ValueError
    ):

        return None

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return None

    if not user.is_active:
        return None

    return user


def get_current_role():

    claims = get_jwt()

    return claims.get(
        "role"
    )


def is_admin(user):

    return bool(
        user
        and user.role == "admin"
    )


def is_agent(user):

    return bool(
        user
        and user.role == "agent"
    )


def is_staff(user):

    return bool(
        user
        and user.role in {
            "admin",
            "agent"
        }
    )
