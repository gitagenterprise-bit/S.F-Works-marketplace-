from flask import request

from extensions import db

from models.audit_log import AuditLog


def create_audit_log(
    *,
    actor_id,
    action,
    entity_type=None,
    entity_id=None,
    description=None
):

    log = AuditLog(

        actor_id=actor_id,

        action=action,

        entity_type=entity_type,

        entity_id=entity_id,

        description=description,

        ip_address=(
            request.headers.get(
                "X-Forwarded-For",
                request.remote_addr
            )
        ),

        user_agent=(
            request.headers.get(
                "User-Agent"
            )[:500]
            if request.headers.get(
                "User-Agent"
            )
            else None
        )
    )

    db.session.add(log)

    return log
