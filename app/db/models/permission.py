import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Text
from app.db.models.user_permission import UserPermission
from typing import TYPE_CHECKING
from uuid import UUID


if TYPE_CHECKING:
    from app.db.models.user import User
    

class Permission(SQLModel, table=True):
    __tablename__ = "permissions"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    ordre: int | None = Field(
        default=None,
        nullable=True
    )
    cree_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    modifie_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

    #Liste des utilisateurs qui possèdent une même rôle
    users: list["User"] = Relationship(
        back_populates="permissions",
        link_model=UserPermission
    )