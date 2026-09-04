from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from app.db.models.user import User
from sqlmodel import Field, SQLModel, Relationship
from app.db.models.categorie_phototheque import CategoriePhototheque



class StatutPhototheque(str, Enum):
    BROUILLON = "brouillon"
    PUBLIE = "publie"
    ARCHIVE = "archive"


class Phototheque(SQLModel, table=True):
    __tablename__ = "phototheques"

    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    # Informations de l’album
    titre: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    description: str | None = None

    # Image représentant l’album
    image_couverture_url: str | None = Field(
        default=None,
        max_length=500,
    )

    # Informations sur l’événement
    lieu: str | None = Field(default=None, max_length=255)
    date_evenement: datetime | None = Field(default=None, index=True)

    # Classement
    categorie_uid: UUID | None = Field(
        default=None,
        foreign_key="categories_phototheques.uid",
        index=True,
    )

    #statut actualite: brouillon, publie ou archive
    statut: str = Field(default="brouillon", max_length=30, index=True)
    
    est_mis_en_avant: bool | None = Field(default=False, index=True)
    ordre_affichage: int | None = Field(default=0, ge=0)
    date_publication: datetime | None = Field(default=None, index=True)
    fichier_key: str | None = Field(
        default=None,
        max_length=500,
    )

    # Statistiques
    nombre_vues: int | None = Field(default=0, ge=0)

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
    supprime_le: datetime | None = Field(default=None, index=True)
    supprime_par_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    
    categorie: CategoriePhototheque | None = Relationship(
        back_populates="phototheques",
        sa_relationship_kwargs={
            "foreign_keys": "[Phototheque.categorie_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    
    cree_par: User | None = Relationship(
        back_populates="phototheques_crees",
        sa_relationship_kwargs={
            "foreign_keys": "[Phototheque.cree_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    modifie_par: User | None = Relationship(
        back_populates="phototheques_modifies",
        sa_relationship_kwargs={
            "foreign_keys": "[Phototheque.modifie_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )
    supprime_par: User | None = Relationship(
        back_populates="phototheques_supprimes",
        sa_relationship_kwargs={
            "foreign_keys": "[Phototheque.supprime_par_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )