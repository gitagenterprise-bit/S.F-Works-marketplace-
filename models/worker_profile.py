from datetime import datetime

from extensions import db


class WorkerProfile(db.Model):

    __tablename__ = "worker_profiles"

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

    profession = db.Column(
        db.String(150),
        nullable=True
    )

    headline = db.Column(
        db.String(200),
        nullable=True
    )

    about = db.Column(
        db.Text,
        nullable=True
    )

    experience_years = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    service_radius_km = db.Column(
        db.Integer,
        nullable=True
    )

    service_area = db.Column(
        db.String(255),
        nullable=True
    )

    hourly_rate = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    minimum_charge = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    availability = db.Column(
        db.String(100),
        nullable=True
    )

    profile_image = db.Column(
        db.String(500),
        nullable=True
    )

    cover_image = db.Column(
        db.String(500),
        nullable=True
    )

    rating = db.Column(
        db.Numeric(3, 2),
        nullable=False,
        default=0
    )

    total_reviews = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    completed_jobs = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True
    )

    verification_status = db.Column(
        db.String(30),
        nullable=False,
        default="not_submitted"
    )

    is_available = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    profile_completed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="worker_profile"
    )

    skills = db.relationship(
        "WorkerSkill",
        back_populates="worker",
        cascade="all, delete-orphan"
    )

    portfolio_items = db.relationship(
        "WorkerPortfolio",
        back_populates="worker",
        cascade="all, delete-orphan"
    )

    def __repr__(self):

        return (
            f"<WorkerProfile "
            f"user={self.user_id}>"
  )
