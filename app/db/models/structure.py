import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Text
from app.db.models.user import User
from typing import TYPE_CHECKING, Optional
from app.db.models.type_structure import TypeStructure
from uuid import UUID


if TYPE_CHECKING:
    from app.db.models.eleve import Eleve 
    from app.db.models.agent import Agent
  

class Structure(SQLModel, table=True):
    __tablename__ = "structures"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    libelle: str | None = Field(unique=True,default=None,max_length=255,nullable=True)
    abreviation: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    is_mode: bool | None = Field(default=None,nullable=True)
    is_deleted: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    slug: str | None = Field(default=None,max_length=255,nullable=True)
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
    type_structure_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="type_structures.uid",
        index=True,
    )

    cree_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )

    typestructure: TypeStructure | None = Relationship(
        back_populates="structures",
        sa_relationship_kwargs={
            "foreign_keys": "[Structure.type_structure_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )

    cree_par: User | None = Relationship(
        back_populates="structures_crees",
        sa_relationship_kwargs={
            "foreign_keys": "[Structure.cree_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    modifie_par: User | None = Relationship(
        back_populates="structures_modifies",
        sa_relationship_kwargs={
            "foreign_keys": "[Structure.modifie_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    supprime_par: User | None = Relationship(
        back_populates="structures_supprimes",
        sa_relationship_kwargs={
            "foreign_keys": "[Structure.supprime_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    
    eleves: list["Eleve"] = Relationship(
        back_populates="structure",
        sa_relationship_kwargs={
            "foreign_keys": "Eleve.structure_uid"
        }
    )

    agents_structure: list["Agent"] = Relationship(
        back_populates="structure",
        sa_relationship_kwargs={
            "foreign_keys": "Agent.structure_uid"
        }
    )



        

