import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from uuid import UUID


if TYPE_CHECKING:
    from app.db.models.eleve import Eleve
    from app.db.models.agent import Agent


class Genre(SQLModel, table=True):
    __tablename__ = "genres"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

    eleves: Optional["Eleve"] = Relationship(
        back_populates="genre",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.genre_uid]"
        }
    )

    agents_genre: Optional["Agent"] = Relationship(
        back_populates="genre",
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.genre_uid]"
        }
    )