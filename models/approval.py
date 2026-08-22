from datetime import datetime

from extensions import db


class ApprovalRecord(db.Model):

    __tablename__ = "approval_records"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    resource_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    resource_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
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

    actor_role = db.Column(
        db.String(30),
        nullable=False
    )

    action = db.Column(
        db.String(30),
        nullable=False
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    actor = db.relationship(
        "User",
        foreign_keys=[actor_id]
    )

    def __repr__(self):

        return (
            f"<ApprovalRecord "
            f"id={self.id} "
            f"resource={self.resource_type}:{self.resource_id}>"
  )
