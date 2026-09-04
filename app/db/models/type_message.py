import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from uuid import UUID




class TypeMessage(SQLModel, table=True):
    __tablename__ = "type_messages"
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
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

