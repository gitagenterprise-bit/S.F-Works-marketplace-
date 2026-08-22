from flask import request

from extensions import db
from models.audit_log import AuditLog


def create_audit_log(
    *,
    user_id=None,
    action,
    entity_type,
    entity_id=None,
    old_status=None,
    new_status=None,
    description=None
):
    """
    Creates a security/audit record.

    This function intentionally does not commit.
    The calling transaction controls commit/rollback.
    """

    ip_address = None

    if request:

        forwarded = request.headers.get(
            "X-Forwarded-For"
        )

        if forwarded:

            ip_address = (
                forwarded
                .split(",")[0]
                .strip()
            )

        else:

            ip_address = request.remote_addr

    user_agent = request.headers.get(
        "User-Agent",
        ""
    )[:500]

    log = AuditLog(

        user_id=user_id,

        action=action,

        entity_type=entity_type,

        entity_id=entity_id,

        old_status=old_status,

        new_status=new_status,

        description=description,

        ip_address=ip_address,

        user_agent=user_agent
    )

    db.session.add(log)

    return log
