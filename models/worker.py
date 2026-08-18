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

    # =====================================================
    # BASIC PROFILE
    # =====================================================

    profession = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    headline = db.Column(
        db.String(255),
        nullable=True
    )

    about = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================================
    # IMAGES
    # =====================================================

    profile_image = db.Column(
        db.String(500),
        nullable=True
    )

    cover_image = db.Column(
        db.String(500),
        nullable=True
    )

    # =====================================================
    # EXPERIENCE
    # =====================================================

    experience_years = db.Column(
        db.Integer,
        default=0
    )

    # =====================================================
    # LOCATION
    # =====================================================

    service_area = db.Column(
        db.String(255),
        nullable=True
    )

    service_radius_km = db.Column(
        db.Integer,
        nullable=True
    )

    address = db.Column(
        db.String(255),
        nullable=True
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

    # =====================================================
    # PRICING
    # =====================================================

    hourly_rate = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    minimum_charge = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    # =====================================================
    # AVAILABILITY
    # =====================================================

    availability = db.Column(
        db.String(100),
        nullable=True
    )

    is_available = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =====================================================
    # VERIFICATION
    # =====================================================

    is_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    verification_status = db.Column(
        db.String(30),
        default="pending"
    )

    # =====================================================
    # RATINGS
    # =====================================================

    rating = db.Column(
        db.Numeric(3, 2),
        default=0.00
    )

    total_reviews = db.Column(
        db.Integer,
        default=0
    )

    # =====================================================
    # JOB STATS
    # =====================================================

    total_jobs = db.Column(
        db.Integer,
        default=0
    )

    completed_jobs = db.Column(
        db.Integer,
        default=0
    )

    # =====================================================
    # PROFILE COMPLETION
    # =====================================================

    profile_completed = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

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

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

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

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<WorkerProfile user={self.user_id}>"
        )
