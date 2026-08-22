from datetime import datetime

from extensions import db


class AgentArea(db.Model):

    __tablename__ = "agent_areas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    agent_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "agent_profiles.id",
            ondelete="CASCADE"
        ),
        nullable=False,
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

    area = db.Column(
        db.String(150),
        nullable=True,
        index=True
    )

    pincode = db.Column(
        db.String(10),
        nullable=True,
        index=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    agent = db.relationship(
        "AgentProfile",
        back_populates="areas"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "agent_id",
            "district",
            "police_station",
            "area",
            "pincode",
            name="uq_agent_area_scope"
        ),
    )

    def __repr__(self):

        return (
            f"<AgentArea "
            f"id={self.id} "
            f"agent_id={self.agent_id}>"
  )
