import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from uuid import UUID


class DocumentJustificatif(SQLModel, table=True):
    __tablename__ = "document_justificatifs"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    url: str | None = Field(default=None,max_length=50,nullable=True)
    taille: int = Field(default=0)
    nom_fichier: str | None = Field(default=None,nullable=True)
    extension: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

    type_document_justificatif_uid: UUID | None = Field(default=None,foreign_key="type_document_justificatifs.uid",nullable=True,index=True,)
