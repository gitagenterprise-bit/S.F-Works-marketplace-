from datetime import datetime

from extensions import db


class JobApplication(db.Model):

    __tablename__ = "job_applications"

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
    # WORKER
    #
    # IMPORTANT:
    # worker_id references users.id
    # NOT worker_profiles.id
    # =====================================================

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # =====================================================
    # APPLICATION DETAILS
    # =====================================================

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

    # =====================================================
    # APPLICATION STATUS
    # =====================================================

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending",
        index=True
    )

    # =====================================================
    # CUSTOMER REVIEW
    # =====================================================

    customer_reviewed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    customer_reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    # =====================================================
    # AGENT REVIEW
    # =====================================================

    agent_reviewed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    agent_reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "agents.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    # =====================================================
    # ADMIN REVIEW
    # =====================================================

    admin_reviewed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    admin_reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    # =====================================================
    # REJECTION
    # =====================================================

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
    # Job
    # -----------------------------------------------------
    job = db.relationship(
        "Job",
        foreign_keys=[job_id],
        back_populates="job_applications"
    )
    
    # -----------------------------------------------------
    # Worker
    #
    # worker_id -> users.id
    # -----------------------------------------------------

    worker = db.relationship(
        "User",
        back_populates="job_applications",
        foreign_keys=[worker_id]
    )

    # -----------------------------------------------------
    # Customer Reviewer
    #
    # customer_reviewed_by -> users.id
    # -----------------------------------------------------

    customer_reviewer = db.relationship(
        "User",
        foreign_keys=[customer_reviewed_by]
    )

    # -----------------------------------------------------
    # Agent Reviewer
    #
    # agent_reviewed_by -> agents.id
    # -----------------------------------------------------

    agent_reviewer = db.relationship(
        "Agent",
        foreign_keys=[agent_reviewed_by]
    )

    # -----------------------------------------------------
    # Admin Reviewer
    #
    # admin_reviewed_by -> users.id
    # -----------------------------------------------------

    admin_reviewer = db.relationship(
        "User",
        foreign_keys=[admin_reviewed_by]
    )

    # =====================================================
    # TABLE CONSTRAINTS
    # =====================================================

    __table_args__ = (
        db.UniqueConstraint(
            "job_id",
            "worker_id",
            name="uq_job_worker_application"
        ),
    )

    # =====================================================
    # HELPER PROPERTIES
    # =====================================================

    @property
    def is_deleted(self):
        """
        Returns True if application is soft deleted.
        """

        return self.deleted_at is not None

    @property
    def is_customer_reviewed(self):
        """
        Returns True if customer has reviewed
        the application.
        """

        return self.customer_reviewed_at is not None

    @property
    def is_agent_reviewed(self):
        """
        Returns True if agent has reviewed
        the application.
        """

        return self.agent_reviewed_at is not None

    @property
    def is_admin_reviewed(self):
        """
        Returns True if admin has reviewed
        the application.
        """

        return self.admin_reviewed_at is not None

    @property
    def is_fully_reviewed(self):
        """
        Returns True when all three review stages
        have been completed.
        """

        return (
            self.customer_reviewed_at is not None
            and
            self.agent_reviewed_at is not None
            and
            self.admin_reviewed_at is not None
        )

    # =====================================================
    # CUSTOMER REVIEW
    # =====================================================

    def mark_customer_reviewed(
        self,
        reviewer_id
    ):
        """
        Mark application as reviewed by customer.
        """

        self.customer_reviewed_by = reviewer_id
        self.customer_reviewed_at = datetime.utcnow()

    # =====================================================
    # AGENT REVIEW
    # =====================================================

    def mark_agent_reviewed(
        self,
        agent_id
    ):
        """
        Mark application as reviewed by agent.
        """

        self.agent_reviewed_by = agent_id
        self.agent_reviewed_at = datetime.utcnow()

    # =====================================================
    # ADMIN REVIEW
    # =====================================================

    def mark_admin_reviewed(
        self,
        admin_id
    ):
        """
        Mark application as reviewed by admin.
        """

        self.admin_reviewed_by = admin_id
        self.admin_reviewed_at = datetime.utcnow()

    # =====================================================
    # REJECT APPLICATION
    # =====================================================

    def reject(
        self,
        reason=None
    ):
        """
        Reject application with optional reason.
        """

        self.status = "rejected"
        self.rejection_reason = reason

    # =====================================================
    # SOFT DELETE
    # =====================================================

    def soft_delete(self):
        """
        Soft delete application.

        The record remains in database.
        """

        self.deleted_at = datetime.utcnow()

    # =====================================================
    # RESTORE
    # =====================================================

    def restore(self):
        """
        Restore soft-deleted application.
        """

        self.deleted_at = None

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<JobApplication "
            f"id={self.id} "
            f"job_id={self.job_id} "
            f"worker_id={self.worker_id} "
            f"status={self.status}>"
    )
