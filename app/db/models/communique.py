from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from app.db.models.user import User
from sqlmodel import Field, SQLModel




class Communique(SQLModel, table=True):
    __tablename__ = "communiques"

    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    #numéro officiel du communiqué, par exemple COM-2026-001
    # Informations principales
    reference: str | None = Field(
        default=None,
        max_length=100,
        unique=True,
        index=True,
    )
    titre: str | None = Field(default=None,max_length=255,nullable=True)
    slug: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True) 
    resume: str | None = Field(default=None, max_length=500)
    contenu: str

    # Document ou illustration
    image_url: str | None = Field(default=None, max_length=500)
    fichier_url: str | None = Field(default=None, max_length=500)

    # Statut communiqué : brouillon, publie ou archive
    statut: str = Field(default="brouillon", max_length=30, index=True)
    est_epingle: bool | None = Field(default=False, index=True)
    date_publication: datetime | None = Field(default=None, index=True)
    date_expiration: datetime | None = Field(default=None, index=True)
    fichier_key: str | None = Field(
        default=None,
        max_length=500,
    )
    # Auteur
    auteur_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        index=True,
    )

    # Statistiques
    nombre_vues: int = Field(
        default=0,
        nullable=True,
        index=True,
    )
    nombre_telechargements: int |None = Field(default=0, ge=0)

    # Traçabilité
    cree_le: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    modifie_le: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    cree_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    modifie_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )

    # Suppression logique
    is_deleted: bool = Field(default=False, index=True)
    supprime_le: datetime | None = None
    supprime_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )

    cree_par: User | None = Relationship(
        back_populates="communiques_crees",
        sa_relationship_kwargs={
            "foreign_keys": "[Communique.cree_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    modifie_par: User | None = Relationship(
        back_populates="communiques_modifies",
        sa_relationship_kwargs={
            "foreign_keys": "[Communique.modifie_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    supprime_par: User | None = Relationship(
        back_populates="communiques_supprimes",
        sa_relationship_kwargs={
            "foreign_keys": "[Communique.supprime_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    
