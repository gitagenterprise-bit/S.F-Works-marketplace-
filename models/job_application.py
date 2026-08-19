from datetime import datetime

from extensions import db


class JobApplication(db.Model):

    __tablename__ = "job_applications"

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

    # IMPORTANT:
    # This references users.id, NOT worker_profiles.id
    worker_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    proposed_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=True
    )

    availability = db.Column(
        db.String(100),
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending",
        index=True
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

    job = db.relationship(
        "Job",
        back_populates="applications"
    )

    worker = db.relationship(
        "User",
        back_populates="job_applications",
        foreign_keys=[worker_id]
    )

    # =====================================================
    # CONSTRAINTS
    # =====================================================

    __table_args__ = (
        db.UniqueConstraint(
            "job_id",
            "worker_id",
            name="uq_job_worker_application"
        ),
    )

    def __repr__(self):

        return (
            f"<JobApplication "
            f"id={self.id} "
            f"job_id={self.job_id} "
            f"worker_id={self.worker_id}>"
        )
