from datetime import datetime

from extensions import db


class CustomerProfile(db.Model):

    __tablename__ = "customer_profiles"

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
        nullable=False
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

    bio = db.Column(
        db.Text
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

    user = db.relationship(
        "User",
        back_populates="customer_profile"
    )
