from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field, Relationship, SQLModel
from app.db.models.user import User



class ClientPublicKey(SQLModel, table=True):
    __tablename__ = "client_public_keys"

    uid: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )
    
    session_uid: UUID = Field(
        nullable=False,
        unique=True,
        index=True,
    )

    # La clé est enregistrée avant l'authentification de l'utilisateur :
    # elle appartient d'abord à la session cryptographique anonyme.
    user_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
        unique=True,
        ondelete="CASCADE",
    )

    public_key: str = Field(
        sa_column=Column(
            Text,
            nullable=False,
        )
    )

    algorithme: str = Field(
        default="RSA-OAEP-256",
        max_length=50,
        nullable=False,
    )

    taille_cle: int = Field(
        default=2048,
        nullable=False,
    )

    is_active: bool = Field(
        default=True,
        nullable=False,
        index=True,
    )

    cree_le: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

    modifie_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
    )
    
    user: User | None = Relationship(
        back_populates="client_public_key",
        sa_relationship_kwargs={
            "foreign_keys": "[ClientPublicKey.user_uid]"
        }
    )
