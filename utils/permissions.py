from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity
)

from extensions import db
from models.user import User
from sqlalchemy import and_, or_

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




def agent_can_access_location(
    agent,
    *,
    district=None,
    police_station=None,
    area=None,
    pincode=None
):
    """
    Returns True only when the requested location
    falls inside the agent's assigned scope.
    """

    if not agent or not agent.is_active:

        return False

    scopes = [
        agent
    ]

    active_areas = [
        item
        for item in agent.areas
        if item.is_active
    ]

    # ------------------------------------------------
    # Agent's primary scope
    # ------------------------------------------------

    def matches(scope):

        if (
            district
            and scope.district
            and district.lower()
            != scope.district.lower()
        ):
            return False

        if (
            police_station
            and scope.police_station
            and police_station.lower()
            != scope.police_station.lower()
        ):
            return False

        if (
            area
            and scope.area
            and area.lower()
            != scope.area.lower()
        ):
            return False

        if (
            pincode
            and scope.pincode
            and pincode
            != scope.pincode
        ):
            return False

        return True

    if matches(agent):

        return True

    for scope in active_areas:

        if matches(scope):

            return True

    return False
