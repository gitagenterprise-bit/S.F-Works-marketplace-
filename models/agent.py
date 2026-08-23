from datetime import datetime

from extensions import db


class AgentProfile(db.Model):

    __tablename__ = "agent_profiles"

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
        nullable=False,
        index=True
    )

    employee_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    designation = db.Column(
        db.String(100),
        nullable=False,
        default="Area Agent"
    )

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True
    )

    verification_status = db.Column(
        db.String(30),
        nullable=False,
        default="pending",
        index=True
    )

    force_password_change = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    last_login_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True,
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

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="agent_profile",
        uselist=False
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by]
    )

    areas = db.relationship(
        "AgentAreaAssignment",
        back_populates="agent",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    permissions = db.relationship(
        "AgentPermission",
        back_populates="agent",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    def has_permission(self, permission):
        """
        Server-side permission check.
        """

        return any(
            item.permission == permission
            and item.is_allowed
            for item in self.permissions
        )

    def __repr__(self):

        return (
            f"<AgentProfile "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"code={self.employee_code}>"
        )


class AgentArea(db.Model):

    __tablename__ = "agent_areas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    area_type = db.Column(
        db.String(30),
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

    locality = db.Column(
        db.String(150),
        nullable=True,
        index=True
    )

    pincode = db.Column(
        db.String(10),
        nullable=True,
        index=True
    )

    state = db.Column(
        db.String(100),
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

    assignments = db.relationship(
        "AgentAreaAssignment",
        back_populates="area",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "name",
            "area_type",
            "district",
            "police_station",
            "locality",
            "pincode",
            name="uq_agent_area_identity"
        ),
    )

    def __repr__(self):

        return (
            f"<AgentArea "
            f"id={self.id} "
            f"name={self.name} "
            f"type={self.area_type}>"
        )


class AgentAreaAssignment(db.Model):

    __tablename__ = "agent_area_assignments"

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

    area_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "agent_areas.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    assigned_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
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

    area = db.relationship(
        "AgentArea",
        back_populates="assignments"
    )

    assigner = db.relationship(
        "User",
        foreign_keys=[assigned_by]
    )

    __table_args__ = (
        db.UniqueConstraint(
            "agent_id",
            "area_id",
            name="uq_agent_area_assignment"
        ),
    )

    def __repr__(self):

        return (
            f"<AgentAreaAssignment "
            f"agent={self.agent_id} "
            f"area={self.area_id}>"
        )


class AgentPermission(db.Model):

    __tablename__ = "agent_permissions"

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

    permission = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    is_allowed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    granted_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
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

    agent = db.relationship(
        "AgentProfile",
        back_populates="permissions"
    )

    granter = db.relationship(
        "User",
        foreign_keys=[granted_by]
    )

    jobs = db.relationship(
        "Job",
        foreign_keys="Job.agent_id",
        back_populates="agent",
        lazy="selectin"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "agent_id",
            "permission",
            name="uq_agent_permission"
        ),
    )

    def __repr__(self):

        return (
            f"<AgentPermission "
            f"agent={self.agent_id} "
            f"permission={self.permission}>"
    )
