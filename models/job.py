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
        db.Numeric(10, 2)
    )

    budget_max = db.Column(
        db.Numeric(10, 2)
    )

    location = db.Column(
        db.String(255),
        nullable=False
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

    status = db.Column(
        db.String(30),
        default="open",
        nullable=False,
        index=True
    )

    priority = db.Column(
        db.String(20),
        default="normal"
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    views = db.Column(
        db.Integer,
        default=0
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
        cascade="all, delete-orphan"
    )

    def __repr__(self):

        return (
            f"<Job {self.title}>"
        )


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
        nullable=False
    )

    image_path = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    job = db.relationship(
        "Job",
        back_populates="images"
  )
