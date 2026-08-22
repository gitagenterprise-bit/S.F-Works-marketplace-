from datetime import datetime

from extensions import db


class AgentProfile(db.Model):

    __tablename__ = "agent_profiles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    employee_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    designation = db.Column(
        db.String(100),
        nullable=False,
        default="Area Agent"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="active",
        index=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="agent_profile"
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by]
    )

    areas = db.relationship(
        "AgentArea",
        back_populates="agent",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):

        return (
            f"<AgentProfile "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"code={self.employee_code}>"
  )
