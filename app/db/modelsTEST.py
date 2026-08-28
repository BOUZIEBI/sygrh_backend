from __future__ import annotations
import uuid
import hashlib
import secrets
from datetime import date, datetime, UTC, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, Text, DateTime, Integer
from sqlalchemy.dialects import postgresql as pg
from uuid import UUID
from sqlalchemy.sql import func
from app.core.database import Base


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.modelsTEST import Eleve


class StatutAffectation(SQLModel, table=True):
    __tablename__ = "statut_affectations"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))



class StatutEleve(SQLModel, table=True):
    __tablename__ = "statut_eleves"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

class Genre(SQLModel, table=True):
    __tablename__ = "genres"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

class StatutEtablissement(SQLModel, table=True):
    __tablename__ = "statut_etablissements"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

class TypeEtablissement(SQLModel, table=True):
    __tablename__ = "type_etablissements"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    
class StatutJuridique(SQLModel, table=True):
    __tablename__ = "statut_juridiques"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

class StatutAnneescolaire(SQLModel, table=True):
    __tablename__ = "statut_anneescolaires"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

     
class Civilite(SQLModel, table=True):
    __tablename__ = "civilites"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_le: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
     

class Typecontrat(SQLModel, table=True):
    __tablename__ = "typecontrats"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

class Typematiere(SQLModel, table=True):
    __tablename__ = "typematieres"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
        
class Nationalite(SQLModel, table=True):
    __tablename__ = "nationalites"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
        

class Pays(SQLModel, table=True):
    __tablename__ = "pays"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    indicatif_telephonique: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    

class Ville(SQLModel, table=True):
    __tablename__ = "villes"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    pays_uid: UUID | None = Field(
        default=None,
        foreign_key="pays.uid",
        nullable=True,
        index=True,
    )


class Commune(SQLModel, table=True):
    __tablename__ = "communes"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    ville_uid: UUID | None = Field(
        default=None,
        foreign_key="villes.uid",
        nullable=True,
        index=True,
    )

class Situation_matrimoniales(SQLModel, table=True):
    __tablename__ = "situation_matrimoniales"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    description: str | None = Field(default=None,sa_column=Column(Text, nullable=True))
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    

class Fonction(SQLModel, table=True):
    __tablename__ = "fonctions"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    description: str | None = Field(default=None,sa_column=Column(Text, nullable=True))
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    


class Service(SQLModel, table=True):
    __tablename__ = "services"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    description: str | None = Field(default=None,sa_column=Column(Text, nullable=True))
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    

class Niveau_etude(SQLModel, table=True):
    __tablename__ = "niveau_etudes"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    description: str | None = Field(default=None,sa_column=Column(Text, nullable=True))
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    

class Decoupage_annee_scolaire(SQLModel, table=True):
    __tablename__ = "decoupage_annee_scolaires"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    
    is_mode: bool | None = Field(
            default=None,
            nullable=True
    )
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))

class Modulepermission(SQLModel, table=True):
    __tablename__ = "modulepermissions"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

class Anneescolaire(SQLModel, table=True):
    __tablename__ = "anneescolaires"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    date_entree_scolaire: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    date_fin_annee_entree_scolaire: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    debut_annee: str | None = Field(default=None,max_length=50,nullable=True)
    fin_annee: str | None = Field(default=None,max_length=50,nullable=True)
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )


class Niveauscolaire(SQLModel, table=True):
    __tablename__ = "niveauscolaires"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    code: str | None = Field(default=None,max_length=50,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

class Cycle_enseignement(SQLModel, table=True):
    __tablename__ = "cycle_enseignements"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    code: str | None = Field(default=None,max_length=50,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

class Filiere(SQLModel, table=True):
    __tablename__ = "filieres"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    code: str | None = Field(default=None,max_length=50,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

class Salleclasse(SQLModel, table=True):
    __tablename__ = "salleclasses"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    abreviation: str | None = Field(default=None,max_length=50,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    nombreplace: int = Field(
        default=0,
        nullable=False
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

class Diplome(SQLModel, table=True):
    __tablename__ = "diplomes"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    code: str | None = Field(default=None,max_length=50,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

class Etablissement(SQLModel, table=True):
    __tablename__ = "etablissements"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    abreviation: str | None = Field(default=None,max_length=255,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    identifiantofficiel: str | None = Field(default=None,max_length=255,nullable=True)
    slug: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
    personne_contact: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_personne_contact: str | None = Field(default=None,max_length=255,nullable=True)
    anneecreation: str | None = Field(default=None,max_length=255,nullable=True)
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    adressecomplete: str | None = Field(default=None,max_length=255,nullable=True)
    email: str | None = Field(default=None,max_length=255,nullable=True)
    telephone: str | None = Field(default=None,max_length=255,nullable=True)
    siteweb: str | None = Field(
        default=None,
        max_length=255,
        nullable=True
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    annee_scolaire_uid: UUID | None = Field(
        default=None,
        foreign_key="anneescolaires.uid",
        nullable=True,
        index=True,
    )
    pays_uid: UUID | None = Field(
        default=None,
        foreign_key="pays.uid",
        nullable=True,
        index=True,
    )
    ville_uid: UUID | None = Field(
        default=None,
        foreign_key="villes.uid",
        nullable=True,
        index=True,
    )
    commune_uid: UUID | None = Field(
        default=None,
        foreign_key="communes.uid",
        nullable=True,
        index=True,
    )
    responsable_etablissement_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    statut_etablissement: str | None = Field(
        default=None,
        nullable=True
    )
    type_etablissement: str | None = Field(
        default=None,
        nullable=True
    )
    statut_juridique: str | None = Field(
        default=None,
        nullable=True,
    )
    #eleves: list["Eleve"] = Relationship(
   #     back_populates="etablissement",
    #    sa_relationship_kwargs={
    #        "foreign_keys": "[Eleve.etablissement_uid]"
    #    }
    #)



class Matiere(SQLModel, table=True):
    __tablename__ = "matieres"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    typematiere_uid: UUID | None = Field(
        default=None,
        foreign_key="typematieres.uid",
        nullable=True,
        index=True,
    )
    etablissement_uid: UUID | None = Field(
        default=None,
        foreign_key="etablissements.uid",
        nullable=True,
        index=True,
    )


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"
    
    role_uid: UUID = Field(
        foreign_key="roles.uid",
        primary_key=True,
        nullable=False
    )

    permission_uid: UUID = Field(
        foreign_key="permissions.uid",
        primary_key=True,
        nullable=False
    )
    

class UserPermission(SQLModel, table=True):
    __tablename__ = "user_permissions"
    user_uid: uuid.UUID = Field(
        foreign_key="users.uid",
        primary_key=True,
        nullable=False,
    )

    permission_uid: uuid.UUID = Field(
        foreign_key="permissions.uid",
        primary_key=True,
        nullable=False,
    )
    

class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
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
        sa_column=Column(pg.VARCHAR, nullable=False), exclude=True
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    
    #permissions: list[Permission] = Relationship(
    #    back_populates="users", link_model=UserPermission
    #)
    role: Role | None = Relationship(
        back_populates="users",
        sa_relationship_kwargs={
            "foreign_keys": "[User.role_uid]"
        },
    )
    eleves_crees: list["Eleve"] = Relationship(
        back_populates="cree_par",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.cree_par_uid]"
        }
    )

    eleves_modifies: list["Eleve"] = Relationship(
        back_populates="modifie_par",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.modifie_par_uid]"
        }
    )
    
    def __repr__(self):
        return f"<User {self.username}>"

class Permission(SQLModel, table=True):
    __tablename__ = "permissions"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    ordre: int | None = Field(
        default=None,
        nullable=True
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
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    supprime_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

    #users: list[User] = Relationship(
    #    back_populates="permissions", link_model=UserPermission
    #)



class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    #books: List["Book"] = Relationship(
    #    link_model=BookTag,
    #    back_populates="tags",
    #    sa_relationship_kwargs={"lazy": "selectin"},
    #)

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class Book(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    #user: Optional[User] = Relationship(back_populates="books")
    #reviews: List["Review"] = Relationship(
    #    back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    #)

    def __repr__(self):
        return f"<Book {self.title}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(lt=5)
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    #user: Optional[User] = Relationship(back_populates="reviews")
    #book: Optional[Book] = Relationship(back_populates="reviews")


class AuthSession(SQLModel, table=True):
    __tablename__ = "auth_sessions"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    refresh_token_hash: str
    is_revoked: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    revoked_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    expires_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    replaced_by_session_id: Optional[str] = None


class LoginAttemptState(SQLModel, table=True):
    __tablename__ = "login_attempt_states"

    user_id: uuid.UUID = Field(
        foreign_key="users.uid",
        primary_key=True
    )
    failed_attempts: int = Field(
        default=0,
        sa_column=Column(
            Integer,
            nullable=False
        )
    )
    locked_until: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )
    )

class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    user_id: UUID = Field(
        foreign_key="users.uid",
        nullable=False,
        index=True
    )
    token_hash: str
    expires_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    used_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )
    )

class Eleve(SQLModel, table=True):
    __tablename__ = "eleves"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    nom: str = Field(max_length=255, nullable=False)
    prenoms: str = Field(max_length=255, nullable=False)
    matricule: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
    date_naissance: datetime | None = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    lieu_naissance: str | None = Field(default=None,max_length=255,nullable=True)
    numero_table: str | None = Field(default=None,max_length=255,nullable=True)

    statut_affectation_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="pays.uid",
    )
    statut_eleve_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="pays.uid",
    )
    statut_anneescolaire_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="pays.uid",
    )
    is_active: bool = Field(
        default=True,
        nullable=False
    )
    is_mode: bool = Field(
        default=True,
        nullable=False
    )
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    etablissement_origine: str | None = Field(default=None,max_length=255,nullable=True)
    genre_uid: UUID | None = Field(
        default=None,
        foreign_key="genres.uid",
        nullable=True,
        index=True
    )
    user_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    nationalite_uid: UUID | None = Field(
        default=None,
        foreign_key="nationalites.uid",
        nullable=True,
        index=True,
    )
    pays_uid: UUID | None = Field(
        default=None,
        foreign_key="pays.uid",
        nullable=True,
        index=True,
    )
    ville_uid: UUID | None = Field(
        default=None,
        foreign_key="villes.uid",
        nullable=True,
        index=True,
    )
    commune_uid: UUID | None = Field(
        default=None,
        foreign_key="communes.uid",
        nullable=True,
        index=True,
    )
    etablissement_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="etablissements.uid",
        index=True
    )
    classe_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="pays.uid",
        index=True
    )
    role_uid: UUID | None = Field(
        default=None,
        foreign_key="roles.uid",
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
    #etablissement: "Etablissement" = Relationship(
    #    back_populates="eleves"
    #)
    role: Role | None = Relationship(
        back_populates="eleves"
    )
    
    cree_par: User | None = Relationship(
        back_populates="eleves_crees",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.cree_par_uid]",
            "uselist": False
        }
    )

    modifie_par: User | None = Relationship(
        back_populates="eleves_modifies",
        sa_relationship_kwargs={
            "foreign_keys": "[Eleve.modifie_par_uid]",
            "uselist": False
        }
    )
    
class Role(SQLModel, table=True):
    __tablename__ = "roles"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    cree_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    modifie_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    supprime_par: UUID | None = Field(default=None,foreign_key="users.uid",nullable=True,index=True,)
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    
    eleves: list["Eleve"] = Relationship(
        back_populates="role"
    )

    
    #lasse: Optional[Classe] = Relationship(
    #    back_populates="eleves"
    #)


    #classe: Classe | None = Relationship(
    #    back_populates="eleves"
    #)

    #Dans la classe Classe
    #eleves: list[Eleve] = Relationship(
    #    back_populates="classe"
    #)

    #user: Optional[User] = Relationship(back_populates="books")
    #reviews: List["Review"] = Relationship(
    #    back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    #)
    #tags: List[Tag] = Relationship(
    #    link_model=BookTag,
    #    back_populates="books",
    #    sa_relationship_kwargs={"lazy": "selectin"},
    #)

class Enseignant(SQLModel, table=True):
    __tablename__ = "enseignants"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    nom: str | None = Field(default=None,max_length=255,nullable=True)
    prenoms: str | None = Field(default=None,max_length=255,nullable=True)
    matricule: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
    date_naissance: datetime | None = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    lieu_naissance: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_principal: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_secondaire: str | None = Field(default=None,max_length=255,nullable=True)
    email_professionnel: str | None = Field(default=None,max_length=255,nullable=True)
    email_personneö: str | None = Field(default=None,max_length=255,nullable=True)
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    lieu_habitation: str | None = Field(default=None,max_length=255,nullable=True)
    date_recrutement: datetime | None = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    date_depart: datetime | None = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    nombre_enfant: int | None = Field(default=None,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
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
    genre_uid: UUID | None = Field(
        default=None,
        nullable=True
    )
    user_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    nationalite_uid: UUID | None = Field(
        default=None,
        foreign_key="nationalites.uid",
        nullable=True,
        index=True,
    )
    pays_uid: UUID | None = Field(
        default=None,
        foreign_key="pays.uid",
        nullable=True,
        index=True,
    )
    ville_uid: UUID | None = Field(
        default=None,
        foreign_key="villes.uid",
        nullable=True,
        index=True,
    )
    commune_uid: UUID | None = Field(
        default=None,
        foreign_key="communes.uid",
        nullable=True,
        index=True,
    )
    situation_matrimoniale_uid: UUID | None = Field(
        default=None,
        foreign_key="situation_matrimoniales.uid",
        nullable=True,
        index=True,
    )
    typecontrat_uid: UUID | None = Field(
        default=None,
        foreign_key="typecontrats.uid",
        nullable=True,
        index=True,
    )  
    service_uid: UUID | None = Field(
        default=None,
        foreign_key="services.uid",
        nullable=True,
        index=True,
    )  
    civilite_uid: UUID | None = Field(
        default=None,
        foreign_key="civilites.uid",
        nullable=True,
        index=True,
    )  
    fonction_uid: UUID | None = Field(
        default=None,
        foreign_key="fonctions.uid",
        nullable=True,
        index=True,
    )  
    role_uid: UUID | None = Field(
        default=None,
        foreign_key="roles.uid",
        nullable=True,
        index=True,
    ) 
    etablissement_uid: UUID | None = Field(
        default=None,
        foreign_key="etablissements.uid",
        nullable=True,
        index=True,
    )  
    diplome_eleve_uid: UUID | None = Field(
        default=None,
        foreign_key="diplomes.uid",
        nullable=True,
        index=True,
    ) 


class Personneladministratif(SQLModel, table=True):
    __tablename__ = "personneladministratifs"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    nom: str | None = Field(default=None,max_length=255,nullable=True)
    prenoms: str | None = Field(default=None,max_length=255,nullable=True)
    matricule: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
    date_naissance: datetime | None = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    lieu_naissance: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_principal: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_secondaire: str | None = Field(default=None,max_length=255,nullable=True)
    email_professionnel: str | None = Field(default=None,max_length=255,nullable=True)
    email_personneö: str | None = Field(default=None,max_length=255,nullable=True)
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    lieu_habitation: str | None = Field(default=None,max_length=255,nullable=True)
    date_recrutement: datetime | None = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    date_depart: datetime | None = Field(sa_column=Column(pg.TIMESTAMP, default=None))
    nombre_enfant: int | None = Field(default=None,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
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
    genre_uid: UUID | None = Field(
        default=None,
        nullable=True,
    )
    user_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    nationalite_uid: UUID | None = Field(
        default=None,
        foreign_key="nationalites.uid",
        nullable=True,
        index=True,
    )
    pays_uid: UUID | None = Field(
        default=None,
        foreign_key="pays.uid",
        nullable=True,
        index=True,
    )
    ville_uid: UUID | None = Field(
        default=None,
        foreign_key="villes.uid",
        nullable=True,
        index=True,
    )
    commune_uid: UUID | None = Field(
        default=None,
        foreign_key="communes.uid",
        nullable=True,
        index=True,
    )
    etablissement_uid: UUID | None = Field(
        default=None,
        foreign_key="etablissements.uid",
        nullable=True,
        index=True,
    )

    situation_matrimoniale_uid: UUID | None = Field(
        default=None,
        foreign_key="situation_matrimoniales.uid",
        nullable=True,
        index=True,
    )
    typecontrat_uid: UUID | None = Field(
        default=None,
        foreign_key="typecontrats.uid",
        nullable=True,
        index=True,
    )  
    service_uid: UUID | None = Field(
        default=None,
        foreign_key="services.uid",
        nullable=True,
        index=True,
    )  
    civilite_uid: UUID | None = Field(
        default=None,
        foreign_key="civilites.uid",
        nullable=True,
        index=True,
    )  
    fonction_uid: UUID | None = Field(
        default=None,
        foreign_key="fonctions.uid",
        nullable=True,
        index=True,
    )  
    role_uid: UUID | None = Field(
        default=None,
        foreign_key="roles.uid",
        nullable=True,
        index=True,
    )  
    etablissement_uid: UUID | None = Field(
        default=None,
        foreign_key="etablissements.uid",
        nullable=True,
        index=True,
    )  
    diplome_eleve_uid: UUID | None = Field(
        default=None,
        foreign_key="diplomes.uid",
        nullable=True,
        index=True,
    ) 


class Classe(SQLModel, table=True):
    __tablename__ = "classes"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    libelle: str | None = Field(default=None,max_length=255,nullable=True)
    abreviation: str | None = Field(default=None,max_length=255,nullable=True)
    description: str | None = Field(default=None,sa_column=Column(Text, nullable=True))
    slug: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
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
    cree_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    modifie_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True,
    )
    supprime_par: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
            nullable=True,
            index=True,
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
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

    statut_affectation_uid: UUID | None = Field(
        default=None,
        nullable=True
    )
    statut_eleve_uid: UUID | None = Field(
        default=None,
        nullable=True
    )
    statut_anneescolaire_uid: UUID | None = Field(
        default=None,
        nullable=True
    )
    
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    etablissement_origine: str | None = Field(default=None,max_length=255,nullable=True)
    
    niveauscolaire_uid: UUID | None = Field(
        default=None,
        foreign_key="niveauscolaires.uid",
        nullable=True,
        index=True,
    )
    cycle_enseignement_uid: UUID | None = Field(
        default=None,
        foreign_key="cycle_enseignements.uid",
        nullable=True,
        index=True,
    )
    filiere_uid: UUID | None = Field(
        default=None,
        foreign_key="filieres.uid",
        nullable=True,
        index=True,
    )
    etablissement_uid: UUID | None = Field(
        default=None,
        foreign_key="etablissements.uid",
        nullable=True,
        index=True,
    )
    enseignant_principal_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        nullable=True,
        index=True
    )
    personnel_encadreur_uid: UUID | None = Field(
        default=None,
        nullable=True,
        index=True
    )
    salleclasse_uid: UUID | None = Field(
        default=None,
        foreign_key="salleclasses.uid",
        nullable=True,
        index=True
    )

    
    #etablissement: Optional[Etablissement] = Relationship(
    #    back_populates="classes"
    #)
    #enseignant_principal: Optional[Enseignant] = Relationship(
    #    back_populates="classes"
    #)
    #personnel_encadreur: Optional[Personneladministratif] = Relationship(
    #    back_populates="classes"
    #)
    #salleclasse: Optional[Salleclasse] = Relationship(
    #    back_populates="classes"
    #)


def generate_raw_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def utcnow() -> datetime:
    return datetime.now(UTC)

