from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from app.db.models.user import User
from sqlmodel import Field, SQLModel, Relationship


class StatutService(str, Enum):
    BROUILLON = "brouillon"
    PUBLIE = "publie"
    SUSPENDU = "suspendu"
    ARCHIVE = "archive"


class Service(SQLModel, table=True):
    __tablename__ = "services"

    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    # Identification
    libelle: str = Field(max_length=255, index=True)
    code: str | None = Field(
        default=None,
        max_length=50,
        unique=True,
        index=True,
    )
    slug: str = Field(
        max_length=255,
        unique=True,
        index=True,
    )

    # Présentation
    description_courte: str | None = Field(
        default=None,
        max_length=500,
    )
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    icone: str | None = Field(default=None, max_length=100)

    # Informations pratiques
    delai_traitement: str | None = Field(default=None, max_length=100)
    cout: float | None = Field(default=None, ge=0)
    lien_demande: str | None = Field(default=None, max_length=500)

    fichier_key: str | None = Field(
        default=None,
        max_length=500,
    )
    # Contacts
    email: str | None = Field(default=None, max_length=255)
    telephone: str | None = Field(default=None, max_length=30)
    adresse: str | None = Field(default=None, max_length=500)
    horaires: str | None = Field(default=None, max_length=255)

    structure_uid: UUID | None = Field(
        default=None,
        foreign_key="structures.uid",
        index=True,
    )
    responsable_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        index=True,
    )

    # Publication
    statut: StatutService = Field(
        default=StatutService.BROUILLON,
        index=True,
    )
    ordre_affichage: int | None = Field(
        default=0, ge=0
    )

    # Traçabilité
    cree_le: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    modifie_le: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    statut_uid: UUID | None = Field(
        default=None,
        foreign_key="statut_services.uid",
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
        back_populates="services_crees",
        sa_relationship_kwargs={
            "foreign_keys": "[Service.cree_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    modifie_par: User | None = Relationship(
        back_populates="services_modifies",
        sa_relationship_kwargs={
            "foreign_keys": "[Service.modifie_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    supprime_par: User | None = Relationship(
        back_populates="services_supprimes",
        sa_relationship_kwargs={
            "foreign_keys": "[Service.supprime_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )