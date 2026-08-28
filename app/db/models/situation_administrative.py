import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from app.db.models.statut_situation_administrative import StatutSituationAdministrative
from app.db.models.emploi import Emploi
from app.db.models.classe_situation_administrative import ClasseSituationAdministrative
from app.db.models.echelon import Echelon
from app.db.models.nature_acte_nomination_dans_emploi import NatureActeNominationDansEmploi
from app.db.models.nature_acte_nomination_fonctionactuelle import NatureActeNominationFonctionactuelle
from app.db.models.diplome import Diplome
from app.db.models.position_administrative import PositionAdministrative
from app.db.models.positionmilitaire import PositionMilitaire
from app.db.models.fonction_actuelle import FonctionActuelle



if TYPE_CHECKING:
    from app.db.models.agent import Agent


class SituationAdministrative(SQLModel, table=True):
    __tablename__ = "situation_administratives"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    numero_acte_nomination_dans_emploi: str | None = Field(default=None,max_length=50,nullable=True)
    date_signature_acte_nomination_dans_emploi: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    date_premiere_prise_service_fonction_publique: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    date_premiere_prise_service_structure: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    date_depart_retraite: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    date_radiation: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    date_depart_mouvement: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    date_retour_mouvement: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    adresse_bureau: str | None = Field(default=None,max_length=50,nullable=True)
    adresse_personnelle: str | None = Field(default=None,max_length=50,nullable=True)
    telephone_bureau: str | None = Field(default=None,max_length=50,nullable=True)
    telephone_domicile: str | None = Field(default=None,max_length=50,nullable=True)
    numero_telephone_1: str | None = Field(default=None,max_length=50,nullable=True)
    numero_telephone_2: str | None = Field(default=None,max_length=50,nullable=True)
    email_institutionnel: str | None = Field(default=None,max_length=50,nullable=True)
    email_personnel: str | None = Field(default=None,max_length=50,nullable=True)
    designation_poste: str | None = Field(default=None,max_length=50,nullable=True)
    numero_acte_nomination_fonctionactuelle: str | None = Field(default=None,max_length=50,nullable=True)
    date_signature_acte_nomination_fonctionactuelle: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    is_mode: bool | None = Field(default=None,nullable=True)
    modifie_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    supprime_le: datetime | None = Field(default=None,sa_column=Column(DateTime(timezone=True),nullable=True))
    is_equivqlence: bool | None = Field(
        default=None,
        nullable=False
    )
    statut_situation_administrative_uid: UUID | None = Field(
        default=None,
        foreign_key="statut_situation_administratives.uid",
        nullable=True,
        index=True,
    ) 
    emploi_uid: UUID | None = Field(
        default=None,
        foreign_key="emplois.uid",
        nullable=True,
        index=True,
    ) 
    classe_situation_administrative_uid: UUID | None = Field(
        default=None,
        foreign_key="classe_situation_administratives.uid",
        nullable=True,
        index=True,
    ) 
    echelon_uid: UUID | None = Field(
        default=None,
        foreign_key="echelons.uid",
        nullable=True,
        index=True,
    ) 
    nature_acte_nomination_dans_emploi_uid: UUID | None = Field(
        default=None,
        foreign_key="nature_acte_nomination_dans_emplois.uid",
        nullable=True,
        index=True,
    ) 
    nature_acte_nomination_dans_fonctionactuelle_uid: UUID | None = Field(
        default=None,
        foreign_key="nature_acte_nomination_fonctionactuelles.uid",
        nullable=True,
        index=True,
    ) 
    diplome_uid: UUID | None = Field(
        default=None,
        foreign_key="diplomes.uid",
        nullable=True,
        index=True,
    )
    position_administrative_uid: UUID | None = Field(
        default=None,
        foreign_key="position_administratives.uid",
        nullable=True,
        index=True,
    )
    position_militaire_uid: UUID | None = Field(
        default=None,
        foreign_key="position_militaires.uid",
        nullable=True,
        index=True,
    )
    fonction_actuelle_uid: UUID | None = Field(
        default=None,
        foreign_key="fonction_actuelles.uid",
        nullable=True,
        index=True,
    )

    statut: StatutSituationAdministrative | None = Relationship(
        back_populates="situation_administratives_statut", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.statut_situation_administrative_uid]"
        }
    )
    emploi: Emploi | None = Relationship(
        back_populates="situation_administratives_emploi", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.emploi_uid]"
        }
    )
    classe_situation_administrative: ClasseSituationAdministrative | None = Relationship(
        back_populates="situation_administratives_classe", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.classe_situation_administrative_uid]"
        }
    )
    echelon: Echelon | None = Relationship(
        back_populates="situation_administratives_echelon", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.echelon_uid]"
        }
    )
    nature_acte_nomination_dans_emploi: NatureActeNominationDansEmploi | None = Relationship(
        back_populates="situation_administratives_nature_acte_nomination_dans_emploi", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.nature_acte_nomination_dans_emploi_uid]"
        }
    )
    nature_acte_nomination_dans_fonctionactuelle: NatureActeNominationFonctionactuelle | None = Relationship(
        back_populates="situation_administratives_nature_acte_nomination_dans_fonctionactuelle", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.nature_acte_nomination_dans_fonctionactuelle_uid]"
        }
    )
    diplome: Diplome | None = Relationship(
        back_populates="situation_administratives_diplome", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.diplome_uid]"
        }
    )
    position_administrative: PositionAdministrative | None = Relationship(
        back_populates="situation_administratives", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.position_administrative_uid]"
        }
    )
    position_militaire: PositionMilitaire | None = Relationship(
        back_populates="situation_administratives_position_militaire", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.position_militaire_uid]"
        }
    )
    fonction_actuelle: FonctionActuelle | None = Relationship(
        back_populates="situation_administratives_fonction_actuelle", 
        sa_relationship_kwargs={
            "foreign_keys": "[SituationAdministrative.fonction_actuelle_uid]"
        }
    )

    agents_situation_administrative: Optional["Agent"] = Relationship(
        back_populates="situation_administrative",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Agent.situation_administrative_uid",
            "cascade": "all, delete-orphan"  # Supprime l'agent si le User est supprimé
        }
    )
