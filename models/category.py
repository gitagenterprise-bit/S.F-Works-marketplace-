from datetime import datetime

from extensions import db


class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    slug = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    icon = db.Column(
        db.String(100)
    )

    image = db.Column(
        db.String(255)
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    jobs = db.relationship(
        "Job",
        back_populates="category"
    )

    def __repr__(self):

        return (
            f"<Category {self.name}>"
  )
