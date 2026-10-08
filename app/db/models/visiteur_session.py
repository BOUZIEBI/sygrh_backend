from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel


class VisiteurSession(SQLModel, table=True):
    __tablename__ = "visiteur_sessions"

    uid: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )

    session_uid: UUID | None = Field(
        default_factory=uuid4,
        unique=True,
        index=True,
        nullable=False,
    )

    adresse_ip: str = Field(
        sa_column=Column(
            String(45),
            nullable=False,
            index=True,
        ),
    )

    user_agent: str | None = Field(
        default=None,
        sa_column=Column(
            String(500),
            nullable=True,
        ),
    )

    cree_le: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

    derniere_activite_le: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
            index=True,
        ),
    )

    expire_le: datetime |None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
            index=True,
        ),
    )

    est_active: bool = Field(
        default=True,
        nullable=False,
        index=True,
    )