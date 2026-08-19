from datetime import datetime

from extensions import db


class Job(db.Model):

    __tablename__ = "jobs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "categories.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    budget_min = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    budget_max = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    location = db.Column(
        db.String(255),
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    state = db.Column(
        db.String(100),
        nullable=True
    )

    pincode = db.Column(
        db.String(10),
        nullable=True
    )

    latitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    longitude = db.Column(
        db.Numeric(10, 7),
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="open",
        index=True
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="normal"
    )

    is_featured = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True
    )

    views = db.Column(
        db.Integer,
        nullable=False,
        default=0
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

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    customer = db.relationship(
        "User",
        back_populates="jobs",
        foreign_keys=[customer_id]
    )

    category = db.relationship(
        "Category",
        back_populates="jobs"
    )

    images = db.relationship(
        "JobImage",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    applications = db.relationship(
        "JobApplication",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):

        return f"<Job id={self.id} title={self.title}>"


class JobImage(db.Model):

    __tablename__ = "job_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "jobs.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    image_path = db.Column(
        db.String(500),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    job = db.relationship(
        "Job",
        back_populates="images"
    )

    def __repr__(self):

        return (
            f"<JobImage "
            f"id={self.id} "
            f"job_id={self.job_id}>"
        )
