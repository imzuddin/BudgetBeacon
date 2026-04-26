from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from api.db_connecter import Base


class SpaceType(StrEnum):
    PERSONAL = "personal"
    SHARED = "shared"


class SpaceRole(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class Space(Base):
    __tablename__ = "spaces"

    __table_args__ = (
        CheckConstraint("type IN ('personal','shared')", name="ck_spaces_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SpaceType.PERSONAL.value
    )
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SpaceMember(Base):
    __tablename__ = "space_members"

    __table_args__ = (
        UniqueConstraint(
            "space_id", "user_id", name="uq_space_members_space_id_user_id"
        ),
        CheckConstraint(
            "role IN ('owner','editor','viewer')",
            name="ck_space_members_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    space_id: Mapped[int] = mapped_column(
        ForeignKey("spaces.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SpaceRole.VIEWER.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
