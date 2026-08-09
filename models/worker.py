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
        unique=True,
        nullable=False,
        index=True
    )

    profession = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    experience_years = db.Column(
        db.Integer,
        default=0
    )

    service_area = db.Column(
        db.String(255)
    )

    hourly_rate = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    about = db.Column(
        db.Text
    )

    address = db.Column(
        db.String(255)
    )

    city = db.Column(
        db.String(100),
        index=True
    )

    state = db.Column(
        db.String(100)
    )

    pincode = db.Column(
        db.String(10)
    )

    latitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    longitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    is_available = db.Column(
        db.Boolean,
        default=True
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )

    verification_status = db.Column(
        db.String(30),
        default="pending"
    )

    rating = db.Column(
        db.Numeric(3, 2),
        default=0.00
    )

    total_reviews = db.Column(
        db.Integer,
        default=0
    )

    total_jobs = db.Column(
        db.Integer,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # --------------------------------
    # Relationships
    # --------------------------------

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

        return f"<WorkerProfile user={self.user_id}>"
