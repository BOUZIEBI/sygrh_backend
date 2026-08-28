import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from uuid import UUID
from typing import TYPE_CHECKING, Optional
from app.db.models.role import Role
from app.db.models.user_permission import UserPermission



if TYPE_CHECKING:
    from app.db.models.eleve import Eleve
    from app.db.models.permission import Permission
    from app.db.models.structure import Structure
    from app.db.models.agent import Agent
    

class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    username: str = Field(max_length=255)
    email: str = Field(max_length=255)
    role_uid: UUID | None = Field(
        default=None,
        foreign_key="roles.uid",
        nullable=True,
        index=True,
    ) 
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    password_hash: str = Field(
        nullable=False,
        exclude=True
    )
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifier_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

   
    role: Role | None = Relationship(
        back_populates="users",
        sa_relationship_kwargs={
            "foreign_keys": "[User.role_uid]" # Encapsulé dans une chaîne/liste pour SQLAlchemy
        }
    )

    # Relation Un à Un vers Eleve
    # uselist=False force SQLAlchemy à retourner un seul objet (pas une liste)
    # foreign_keys lève l'ambiguïté s'il y a d'autres clés étrangères (ex: cree_par)
    eleve: Optional["Eleve"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Eleve.user_uid",
            "cascade": "all, delete-orphan"  # Supprime l'élève si le User est supprimé
        }
    )
    # Relation Un à Un vers Agent
    # uselist=False force SQLAlchemy à retourner un seul objet (pas une liste)
    # foreign_keys lève l'ambiguïté s'il y a d'autres clés étrangères (ex: cree_par)
    agent: Optional["Agent"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Agent.user_uid",
            "cascade": "all, delete-orphan"  # Supprime l'agent si le User est supprimé
        }
    )
    eleve_cree: Optional["Eleve"] = Relationship(
        back_populates="cree_par",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Eleve.cree_par_uid",
            "cascade": "all, delete-orphan"  # Supprime l'élève si le User est supprimé
        }
    )
    eleve_modifie: Optional["Eleve"] = Relationship(
        back_populates="modifie_par",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Eleve.modifie_par_uid",
            "cascade": "all, delete-orphan"  # Supprime l'élève si le User est supprimé
        }
    )
    eleve_supprime: Optional["Eleve"] = Relationship(
        back_populates="supprime_par",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Eleve.supprime_par_uid",
            "cascade": "all, delete-orphan"  # Supprime l'élève si le User est supprimé
        }
    )

    structures_crees: list["Structure"] = Relationship(
        back_populates="cree_par",
        sa_relationship_kwargs={
            "foreign_keys": "Structure.cree_par_uid",
        }
    )
    structures_modifies: list["Structure"] = Relationship(
        back_populates="modifie_par",
        sa_relationship_kwargs={
            "foreign_keys": "Structure.modifie_par_uid",
        }
    )
    structures_supprimes: list["Structure"] = Relationship(
        back_populates="supprime_par",
        sa_relationship_kwargs={
            "foreign_keys": "Structure.supprime_par_uid",
        }
    )

    agents_crees: list["Agent"] = Relationship(
        back_populates="cree_par",
        sa_relationship_kwargs={
            "foreign_keys": "Agent.cree_par_uid",
        }
    )
    agents_modifies: list["Agent"] = Relationship(
        back_populates="modifie_par",
        sa_relationship_kwargs={
            "foreign_keys": "Agent.modifie_par_uid",
        }
    )
    agents_supprimes: list["Agent"] = Relationship(
        back_populates="supprime_par",
        sa_relationship_kwargs={
            "foreign_keys": "Agent.supprime_par_uid",
        }
    )

    permissions: list["Permission"] = Relationship(
        back_populates="users",
        link_model=UserPermission
    )

    


    
    