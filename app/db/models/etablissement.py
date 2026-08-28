import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Text
from typing import TYPE_CHECKING, Optional
from uuid import UUID


if TYPE_CHECKING:
    from app.db.models.eleve import Eleve


class Etablissement(SQLModel, table=True):
    __tablename__ = "etablissements"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    abreviation: str | None = Field(default=None,max_length=255,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    identifiantofficiel: str | None = Field(default=None,max_length=255,nullable=True)
    slug: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
    personne_contact: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_personne_contact: str | None = Field(default=None,max_length=255,nullable=True)
    anneecreation: str | None = Field(default=None,max_length=255,nullable=True)
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    adressecomplete: str | None = Field(default=None,max_length=255,nullable=True)
    email: str | None = Field(default=None,max_length=255,nullable=True)
    telephone: str | None = Field(default=None,max_length=255,nullable=True)
    siteweb: str | None = Field(
        default=None,
        max_length=255,
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
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

    responsable_etablissement_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    statut_etablissement: str | None = Field(
        default=None,
        nullable=True
    )
    type_etablissement: str | None = Field(
        default=None,
        nullable=True
    )
    
    eleves: Optional["Eleve"] = Relationship(
        back_populates="etablissement",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.etablissement_uid]"
        }
    )

