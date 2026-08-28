import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from uuid import UUID
from app.db.models.user import User
from app.db.models.genre import Genre
from app.db.models.structure import Structure


class Eleve(SQLModel, table=True):
    __tablename__ = "eleves"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    nom: str = Field(max_length=255, nullable=False)
    prenoms: str = Field(max_length=255, nullable=False)
    matricule: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
    date_naissance: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    lieu_naissance: str | None = Field(default=None,max_length=255,nullable=True)
    numero_table: str | None = Field(default=None,max_length=255,nullable=True)

    statut_affectation_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="statut_affectations.uid",
    )
    statut_eleve_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="statut_eleves.uid",
    )
    genre_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="genres.uid",
    )
    groupe_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="groupes.uid",
    )
   
    structure_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="structures.uid",
    )
    is_active: bool = Field(
        default=True,
        nullable=False
    )
    is_mode: bool = Field(
        default=True,
        nullable=False
    )
 
    user_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
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
    is_deleted: bool | None = Field(
        default=None,
        nullable=False
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

    # One-to-One: Relation inverse vers User
    user: User = Relationship(
        back_populates="eleve",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.user_uid]"
        }
    )   

    cree_par: User | None = Relationship(
        back_populates="eleve_cree",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.cree_par_uid]"
        }
    )
    modifie_par: User | None= Relationship(
        back_populates="eleve_modifie",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.modifie_par_uid]"
        }
    )
    supprime_par: User | None= Relationship(
        back_populates="eleve_supprime",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.supprime_par_uid]"
        }
    )
    
    structure: Structure | None = Relationship(
        back_populates="eleves",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.structure_uid]"
        }
    )

    genre: Genre | None = Relationship(
        back_populates="eleves",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.genre_uid]"
        }
    )
 

