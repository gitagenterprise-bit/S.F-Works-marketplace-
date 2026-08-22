from datetime import datetime

from extensions import db


class AuditLog(db.Model):

    __tablename__ = "audit_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    action = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    resource_type = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    resource_id = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    old_status = db.Column(
        db.String(50),
        nullable=True
    )

    new_status = db.Column(
        db.String(50),
        nullable=True
    )

    ip_address = db.Column(
        db.String(45),
        nullable=True
    )

    user_agent = db.Column(
        db.String(500),
        nullable=True
    )

    details = db.Column(
        db.JSON,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    actor = db.relationship(
        "User",
        foreign_keys=[actor_id]
    )

    def __repr__(self):

        return (
            f"<AuditLog "
            f"id={self.id} "
            f"action={self.action}>"
  )
