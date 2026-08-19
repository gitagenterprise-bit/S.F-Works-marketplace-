from datetime import datetime

from extensions import db


class WorkerPortfolio(db.Model):

    __tablename__ = "worker_portfolio"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "worker_profiles.id",
            ondelete="CASCADE"
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
        nullable=True
    )

    image_path = db.Column(
        db.String(500),
        nullable=True
    )

    project_date = db.Column(
        db.Date,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # =====================================================
    # RELATIONSHIP
    # =====================================================

    worker = db.relationship(
        "WorkerProfile",
        back_populates="portfolio_items"
    )

    def __repr__(self):

        return (
            f"<WorkerPortfolio "
            f"id={self.id} "
            f"worker_id={self.worker_id}>"
        )
