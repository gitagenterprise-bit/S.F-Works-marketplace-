from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="customer",
        index=True
    )

    profile_image = db.Column(
        db.String(255),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    is_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # --------------------------------
    # Relationships
    # --------------------------------

    customer_profile = db.relationship(
        "CustomerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    worker_profile = db.relationship(
        "WorkerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    jobs = db.relationship(
        "Job",
        back_populates="customer",
        foreign_keys="Job.customer_id"
    )

    job_applications = db.relationship(
        "JobApplication",
        back_populates="worker",
        cascade="all, delete-orphan"
    )
    agent_profile = db.relationship(
        "AgentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    audit_logs = db.relationship(
        "AuditLog",
        back_populates="user",
        passive_deletes=True
    )

    # --------------------------------
    # Password
    # --------------------------------

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):

        return f"<User {self.email}>"
