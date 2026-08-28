import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from uuid import UUID


if TYPE_CHECKING:
    from app.db.models.agent import Agent


class NaturePieceidentite(SQLModel, table=True):
    __tablename__ = "nature_pieceidentites"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    is_mode: bool | None = Field(default=None,nullable=True)
    is_delete: bool | None = Field(default=None,nullable=True)
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

    agents_nature_piece_identite: Optional["Agent"] = Relationship(
        back_populates="nature_piece_identite",
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.nature_piece_identite_uid]"
        }
    )
