from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.db.models.phototheque import Phototheque


class CategoriePhototheque(SQLModel, table=True):
    __tablename__ = "categories_phototheques"

    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    libelle: str = Field(
        max_length=255,
        unique=True,
        index=True,
    )
    code: str = Field(
        max_length=50,
        unique=True,
        index=True,
    )

    est_active: bool | None = Field(default=True, index=True)

    cree_le: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    modifie_le: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )

    is_deleted: bool | None = Field(default=False, index=True)
    supprime_le: datetime | None = None
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )
    
    phototheques: list["Phototheque"] = Relationship(
        back_populates="categorie",
        sa_relationship_kwargs={
            "foreign_keys": "[Phototheque.categorie_uid]" 
        }
    )