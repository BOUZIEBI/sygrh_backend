
import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING, Optional
from app.db.models.user import User
from app.db.models.genre import Genre
from app.db.models.nature_acte_nomination_fonctionactuelle import NatureActeNominationFonctionactuelle
from app.db.models.nature_piece_identite import NaturePieceidentite
from app.db.models.type_agent import TypeAgent
from app.db.models.nationalite import Nationalite
from app.db.models.structure import Structure
from app.db.models.fonction import Fonction
from app.db.models.situation_matrimoniale import SituationMatrimoniale
from app.db.models.grade import Grade
from app.db.models.specialite import Specialite
from app.db.models.situation_administrative import SituationAdministrative
from app.db.models.statut import Statut
from app.db.models.conjoint import Conjoint
from app.db.models.type_recrutement import TypeRecrutement
from app.db.models.validation_fiche import ValidationFiche
from uuid import UUID

class Agent(SQLModel, table=True):
    __tablename__ = "agents"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
            nullable=False,
    )
    nom: str | None = Field(default=None,max_length=255,nullable=True)
    prenoms: str | None = Field(default=None,max_length=255,nullable=True)
    matricule: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
    date_naissance: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    lieu_naissance: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_principal: str | None = Field(default=None,max_length=255,nullable=True)
    telephone_secondaire: str | None = Field(default=None,max_length=255,nullable=True)
    email_professionnel: str | None = Field(default=None,max_length=255,nullable=True)
    email_personnel: str | None = Field(default=None,max_length=255,nullable=True)
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    nom_jeune_fille: str | None = Field(default=None,max_length=255,nullable=True)
    lieu_habitation: str | None = Field(default=None,max_length=255,nullable=True)
    date_recrutement: datetime | None = Field(default=None, sa_column=Column( DateTime(timezone=True), nullable=True))
    date_depart: datetime | None = Field(default=None, sa_column=Column( DateTime(timezone=True), nullable=True ))
    nombre_enfant: int = Field(default=0)
    nom_prenoms_pere: str | None = Field(default=None,max_length=255,nullable=True)
    nom_prenoms_mere: str | None = Field(default=None,max_length=255,nullable=True)
    numero_piece_identite: str | None = Field(default=None,max_length=255,nullable=True)
        
    cree_le: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
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
    preinscrit_le: datetime | None = Field(
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
    conjoint_uid: UUID | None = Field(
        default=None,
        foreign_key="conjoints.uid",
        nullable=True,
        index=True,
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
    etat_handicap: bool | None = Field(
        default=None,
        nullable=True
    )
    is_mode: bool | None = Field(
        default=None,
        nullable=True
    )
    is_deleted: bool | None = Field(
        default=None,
        nullable=False
    )
    est_preinscrit: bool | None = Field(
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
    date_premiere_prise_service_dans_structure: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    date_premiere_prise_service_fonction_publique: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    nature_piece_identite_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="nature_pieceidentites.uid",
        index=True
    )
    genre_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="genres.uid",
        index=True
    )
    type_agent_uid: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="type_agents.uid",
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
    
    type_recrutement_uid: UUID | None = Field(
        default=None,
        foreign_key="type_recrutements.uid",
        nullable=True,
        index=True,
    )  
    structure_uid: UUID | None = Field(
        default=None,
        foreign_key="structures.uid",
        nullable=True,
        index=True,
    )  
    
    fonction_uid: UUID | None = Field(
        default=None,
        foreign_key="fonctions.uid",
        nullable=True,
        index=True,
    )  
     
    situation_matrimoniale_uid: UUID | None = Field(
        default=None,
        foreign_key="situation_matrimoniales.uid",
        nullable=True,
        index=True,
    ) 
    specialite_uid: UUID | None = Field(
        default=None,
        foreign_key="specialites.uid",
        nullable=True,
        index=True,
    ) 
    situation_administrative_uid: UUID | None = Field(
        default=None,
        foreign_key="situation_administratives.uid",
        nullable=True,
        index=True,
    ) 
   
    grade_uid: UUID | None = Field(
        default=None,
        foreign_key="grades.uid",
        nullable=True,
        index=True,
    ) 
    statut_uid: UUID | None = Field(
        default=None,
        foreign_key="statuts.uid",
        nullable=True,
        index=True,
    ) 
    validation_fiche_uid: UUID | None = Field(
        default=None,
        foreign_key="validation_fiches.uid",
        nullable=True,
        index=True,
    )

    cree_par: User | None = Relationship(
        back_populates="agents_crees",
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.cree_par_uid]"
        }
    )
    modifie_par: User | None= Relationship(
        back_populates="agents_modifies",
        sa_relationship_kwargs={
                "foreign_keys": "[Agent.modifie_par_uid]"
        }
    )
    supprime_par: User | None= Relationship(
        back_populates="agents_supprimes",
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.supprime_par_uid]"
        }
    )
    genre: Genre | None= Relationship(
        back_populates="agents_genre", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.genre_uid]"
        }
    ) 
    nature_piece_identite: NaturePieceidentite | None= Relationship(
        back_populates="agents_nature_piece_identite", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.nature_piece_identite_uid]"
        }
    )
    type_agent: TypeAgent | None = Relationship(
        back_populates="agents_type_agent", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.type_agent_uid]"
        }
    )
    # One-to-One: Relation inverse vers User
    user: User = Relationship(
        back_populates="agent",
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.user_uid]"
        }
    ) 
    nationalite: Nationalite | None = Relationship(
        back_populates="agents_nationalite", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.nationalite_uid]"
        }
    )
    fonction: Fonction | None = Relationship(
        back_populates="agents_fonction", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.fonction_uid]"
        }
    )
    structure: Structure | None = Relationship(
        back_populates="agents_structure", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.structure_uid]"
        }
    )
    situation_matrimoniale: SituationMatrimoniale | None = Relationship(
        back_populates="agents_situation_matrimoniale", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.situation_matrimoniale_uid]"
        }
    )

    grade: Grade | None = Relationship(
        back_populates="agents", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.grade_uid]"
        }
    )
    specialite: Specialite | None = Relationship(
        back_populates="agents_specialite", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.specialite_uid]"
        }
    )
    situation_administrative: SituationAdministrative | None = Relationship(
        back_populates="agents_situation_administrative", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.situation_administrative_uid]"
        }
    )
    conjoint: Conjoint | None = Relationship(
        back_populates="agent_conjoint", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.conjoint_uid]"
        }
    )
    statut: Statut | None = Relationship(
        back_populates="agents_statut", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.statut_uid]"
        }
    )
    validation_fiche: ValidationFiche | None = Relationship(
        back_populates="agents_validation_fiche", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.validation_fiche_uid]"
        }
    )
    type_recrutement: TypeRecrutement | None = Relationship(
        back_populates="agent_type_recrutement", 
        sa_relationship_kwargs={
            "foreign_keys": "[Agent.type_recrutement_uid]" 
        }
    )

     


