from datetime import datetime

from extensions import db


class Job(db.Model):

    __tablename__ = "jobs"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # CUSTOMER
    # =====================================================

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # =====================================================
    # CATEGORY
    # =====================================================

    category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "categories.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    # =====================================================
    # JOB BASIC INFORMATION
    # =====================================================

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    # =====================================================
    # BUDGET
    # =====================================================

    budget_min = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    budget_max = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    # =====================================================
    # LOCATION
    # =====================================================

    location = db.Column(
        db.String(255),
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    district = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    police_station = db.Column(
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

    # =====================================================
    # JOB STATUS
    # =====================================================

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

    # =====================================================
    # JOB VIEWS
    # =====================================================

    views = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # =====================================================
    # AGENT ASSIGNMENT
    # =====================================================

    agent_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "agent_profiles.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    # =====================================================
    # REVIEW / MODERATION
    # =====================================================

    reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    reviewed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    rejection_reason = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================================
    # SOFT DELETE
    # =====================================================

    deleted_at = db.Column(
        db.DateTime,
        nullable=True,
        index=True
    )

    deleted_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

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

    # -----------------------------------------------------
    # Customer who created the job
    # -----------------------------------------------------

    customer = db.relationship(
        "User",
        back_populates="jobs",
        foreign_keys=[customer_id]
    )

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------

    category = db.relationship(
        "Category",
        back_populates="jobs"
    )

    # -----------------------------------------------------
    # Assigned Agent
    # -----------------------------------------------------

    agent = db.relationship(
        "AgentProfile",
        foreign_keys=[agent_id],
        back_populates="jobs"
    )

    # -----------------------------------------------------
    # User who reviewed the job
    # -----------------------------------------------------

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewed_by]
    )

    # -----------------------------------------------------
    # User who deleted the job
    # -----------------------------------------------------

    deleter = db.relationship(
        "User",
        foreign_keys=[deleted_by]
    )

    # -----------------------------------------------------
    # Job Images
    # -----------------------------------------------------

    images = db.relationship(
        "JobImage",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # -----------------------------------------------------
    # Job Applications
    # -----------------------------------------------------

    job_applications = db.relationship(
        "JobApplication",
        foreign_keys="JobApplication.worker_id",
        back_populates="worker",
        lazy="selectin"
    )
    # =====================================================
    # HELPER METHODS
    # =====================================================

    @property
    def is_deleted(self):
        """
        Returns True when the job has been soft deleted.
        """
        return self.deleted_at is not None

    @property
    def is_reviewed(self):
        """
        Returns True when the job has been reviewed.
        """
        return self.reviewed_at is not None

    # =====================================================
    # SOFT DELETE
    # =====================================================

    def soft_delete(self, user_id=None):
        """
        Soft delete the job instead of physically
        deleting the database record.
        """

        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id

    # =====================================================
    # RESTORE
    # =====================================================

    def restore(self):
        """
        Restore a soft-deleted job.
        """

        self.deleted_at = None
        self.deleted_by = None

    # =====================================================
    # REVIEW
    # =====================================================

    def mark_reviewed(
        self,
        reviewer_id,
        approved=True,
        rejection_reason=None
    ):
        """
        Mark job as reviewed.

        approved=True:
            Job approved.

        approved=False:
            Job rejected.
        """

        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()

        if approved:
            self.status = "open"
            self.rejection_reason = None

        else:
            self.status = "rejected"
            self.rejection_reason = rejection_reason

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<Job "
            f"id={self.id} "
            f"title={self.title} "
            f"status={self.status}>"
        )


# =========================================================
# JOB IMAGE MODEL
# =========================================================

class JobImage(db.Model):

    __tablename__ = "job_images"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # JOB
    # =====================================================

    job_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "jobs.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # =====================================================
    # IMAGE
    # =====================================================

    image_path = db.Column(
        db.String(500),
        nullable=False
    )

    # =====================================================
    # TIMESTAMP
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # =====================================================
    # RELATIONSHIP
    # =====================================================

    job = db.relationship(
        "Job",
        back_populates="images"
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<JobImage "
            f"id={self.id} "
            f"job_id={self.job_id}>"
    )
