from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class InformationContact(SQLModel, table=True):
    __tablename__ = "information_contacts"

    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    # Identification
    libelle: str = Field(
        default="Contact principal",
        max_length=150,
        index=True,
    )
    description: str | None = Field(default=None, max_length=500)

    # Coordonnées
    adresse: str | None = Field(default=None, max_length=500)
    boite_postale: str | None = Field(default=None, max_length=100)
    ville: str | None = Field(default=None, max_length=150)
    pays: str | None = Field(default=None, max_length=150)

    telephone_principal: str | None = Field(default=None, max_length=30)
    telephone_secondaire: str | None = Field(default=None, max_length=30)
    whatsapp: str | None = Field(default=None, max_length=30)

    email_principal: str | None = Field(default=None, max_length=255)
    email_secondaire: str | None = Field(default=None, max_length=255)
    site_web: str | None = Field(default=None, max_length=500)

    # Localisation géographique
    latitude: float | None = None
    longitude: float | None = None
    lien_google_maps: str | None = Field(default=None, max_length=500)

    # Horaires
    horaires_ouverture: str | None = Field(default=None, max_length=500)

    # Réseaux sociaux
    facebook_url: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)
    instagram_url: str | None = Field(default=None, max_length=500)
    youtube_url: str | None = Field(default=None, max_length=500)
    x_url: str | None = Field(default=None, max_length=500)
    tiktok_url: str | None = Field(default=None, max_length=500)

    # Relations facultatives
    structure_uid: UUID | None = Field(
        default=None,
        foreign_key="structures.uid",
        index=True,
    )

    # Affichage
    est_principal: bool = Field(default=False, index=True)
    est_active: bool = Field(default=True, index=True)
    ordre_affichage: int = Field(default=0, ge=0)

    # Traçabilité
    cree_le: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    modifie_le: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )

    # Suppression logique
    is_deleted: bool = Field(default=False, index=True)
    supprime_le: datetime | None = None
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    type_information_uid: UUID | None = Field(
        default=None,
        foreign_key="type_information_contacts.uid",
    )