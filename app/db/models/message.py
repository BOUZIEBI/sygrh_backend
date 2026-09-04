from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field, SQLModel



class Message(SQLModel, table=True):
    __tablename__ = "messages"

    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    # Contenu
    objet: str | None = Field(default=None, max_length=255)
    contenu: str
    email: str | None = Field(default=None, max_length=255)
    nom_prenoms_expediteur: str | None = Field(default=None, max_length=255)
    service_expediteur: str | None = Field(default=None, max_length=255)
    # Expéditeur et destinataire
    expediteur_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        index=True,
    )
    destinataire_uid: UUID | None= Field(
        default=None,
        foreign_key="users.uid",
        index=True,
    )

    code: str | None = Field(default=None,max_length=255,nullable=True)
    
    # États
    est_important: bool | None = Field(default=True, index=True)
    est_epingle: bool | None = Field(default=None)
    est_lu: bool | None = Field(default=False, index=True)

    # Dates
    envoye_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    
    # Suppression logique
    is_deleted: bool | None = Field(default=False, index=True)
    
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    archive_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    lu_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
    )

    #Les types de message : TEXTE = "texte", INFORMATION = "information", ALERTE = "alerte", NOTIFICATION = "notification"
    type_message_uid: UUID | None = Field(
        default=None,
        foreign_key="type_messages.uid",
        nullable=True,
        index=True
    )

    #Les statuts de message : BROUILLON = "brouillon", ENVOYE = "envoye", LIVRE = "livre", LU = "lu", ARCHIVE = "archive"
    statut_message_uid: UUID | None = Field(
        default=None,
        foreign_key="statut_messages.uid",
        nullable=True,
        index=True
    )