import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from uuid import UUID


if TYPE_CHECKING:
    from app.db.models.eleve import Eleve
    from app.db.models.agent import Agent


class Conjoint(SQLModel, table=True):
    __tablename__ = "conjoints"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    nom: str | None = Field(default=None,max_length=255,nullable=True)
    prenoms: str | None = Field(default=None,max_length=255,nullable=True)
    matricule_cnps: str | None = Field(default=None,max_length=255,nullable=True)
    profession: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

    agent_conjoint: Optional["Agent"] = Relationship(
        back_populates="conjoint",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Agent.conjoint_uid",
            "cascade": "all, delete-orphan"  # Supprime l'agent si le User est supprimé
        }
    )