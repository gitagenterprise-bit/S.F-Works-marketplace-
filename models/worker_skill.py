from extensions import db


class WorkerSkill(db.Model):

    __tablename__ = "worker_skills"

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

    skill_name = db.Column(
        db.String(100),
        nullable=False
    )

    experience_years = db.Column(
        db.Integer,
        nullable=True
    )

    # =====================================================
    # RELATIONSHIP
    # =====================================================

    worker = db.relationship(
        "WorkerProfile",
        back_populates="skills"
    )

    # =====================================================
    # CONSTRAINT
    # =====================================================

    __table_args__ = (
        db.UniqueConstraint(
            "worker_id",
            "skill_name",
            name="uq_worker_skill"
        ),
    )

    def __repr__(self):

        return (
            f"<WorkerSkill "
            f"id={self.id} "
            f"worker_id={self.worker_id} "
            f"name={self.skill_name}>"
        )
