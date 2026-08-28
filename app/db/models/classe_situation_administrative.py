import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from uuid import UUID



if TYPE_CHECKING:
    from app.db.models.situation_administrative import SituationAdministrative



class ClasseSituationAdministrative(SQLModel, table=True):
    __tablename__ = "classe_situation_administratives"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

    situation_administratives_classe: Optional["SituationAdministrative"] = Relationship(
        back_populates="classe_situation_administrative",
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.classe_situation_administrative_uid]"
        }
    )

