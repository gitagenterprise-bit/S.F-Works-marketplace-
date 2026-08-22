from sqlalchemy import or_

from models.agent import AgentArea


def agent_can_access_location(
    agent,
    *,
    district=None,
    police_station=None,
    city=None,
    pincode=None
):

    if not agent:
        return False

    active_assignments = [
        assignment
        for assignment in agent.areas
        if assignment.is_active
        and assignment.area
        and assignment.area.is_active
    ]

    if not active_assignments:
        return False

    district = (
        str(district).strip().lower()
        if district
        else None
    )

    police_station = (
        str(police_station).strip().lower()
        if police_station
        else None
    )

    city = (
        str(city).strip().lower()
        if city
        else None
    )

    pincode = (
        str(pincode).strip()
        if pincode
        else None
    )

    for assignment in active_assignments:

        area = assignment.area

        area_district = (
            area.district.strip().lower()
            if area.district
            else None
        )

        area_station = (
            area.police_station
            .strip()
            .lower()
            if area.police_station
            else None
        )

        area_locality = (
            area.locality
            .strip()
            .lower()
            if area.locality
            else None
        )

        area_pincode = (
            area.pincode.strip()
            if area.pincode
            else None
        )

        # -------------------------------------------------
        # DISTRICT SCOPE
        # -------------------------------------------------

        if area.area_type == "district":

            if (
                district
                and area_district == district
            ):
                return True

        # -------------------------------------------------
        # POLICE STATION SCOPE
        # -------------------------------------------------

        elif area.area_type == "police_station":

            if (
                district
                and police_station
                and area_district == district
                and area_station == police_station
            ):
                return True

        # -------------------------------------------------
        # LOCALITY SCOPE
        # -------------------------------------------------

        elif area.area_type == "locality":

            if (
                district
                and area_district == district
                and city
                and area_locality == city
            ):
                return True

        # -------------------------------------------------
        # PINCODE SCOPE
        # -------------------------------------------------

        elif area.area_type == "pincode":

            if (
                pincode
                and area_pincode == pincode
            ):
                return True

    return False
