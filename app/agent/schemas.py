import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
from app.auth.schemas import PermissionModel
T = TypeVar("T")



class AgentCreateModel(BaseModel):
    nom: str = Field(max_length=255,nullable=False)
    prenoms: str | None = Field(max_length=255,nullable=False)
    matricule: str | None = None
    code: str | None = None
    date_naissance: datetime | None = None
    lieu_naissance: str | None = None
    telephone_principal: str | None = None
    telephone_secondaire: str | None = None
    email_professionnel: str | None = None
    email_personnel: str | None = None
    quartier: str | None = None
    nom_jeune_fille: str | None = None
    lieu_habitation: str | None = None
    date_recrutement: datetime | None = None
    date_depart: datetime | None = None
    nombre_enfant: int = Field(default=0)
    nom_prenoms_pere: str | None = None
    nom_prenoms_mere: str | None = None
    numero_piece_identite: str | None = None
    cree_le: datetime | None = None
    modifie_le: datetime | None = None 
    preinscrit_le: datetime | None = None 
    etat_handicap: bool | None = None
    is_mode: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    est_preinscrit: bool = Field(default=False)
    supprime_le: datetime | None = None
    date_premiere_prise_service_dans_structure: datetime | None = None   
  
    numero_acte_nomination_dans_emploi: str | None = None 
    date_signature_acte_nomination_dans_emploi: datetime | None = None
    date_premiere_prise_service_fonction_publique: datetime | None = None
    date_depart_retraite: datetime | None = None
    date_radiation: datetime | None = None
    date_depart_mouvement: datetime | None = None
    date_retour_mouvement: datetime | None = None
    adresse_bureau: str | None = None
    adresse_personnelle: str | None = None
    telephone_bureau: str | None = None
    telephone_domicile: str | None = None
    numero_telephone_1: str | None = None
    numero_telephone_2: str | None = None
    email_institutionnel: str | None = None
    designation_poste: str | None = None
    numero_acte_nomination_fonctionactuelle: str | None = None
    date_signature_acte_nomination_fonctionactuelle: datetime | None = None
        
    is_equivqlence: bool | None = None
    statut_situation_administrative_uid: UUID | None = None
    emploi_uid: UUID | None = None
    classe_situation_administrative_uid: UUID | None = None
    echelon_uid: UUID | None = None
    nature_acte_nomination_dans_emploi_uid: UUID | None = None
    nature_acte_nomination_dans_fonctionactuelle_uid: UUID | None = None
    diplome_uid: UUID | None = None
    position_administrative_uid: UUID | None = None
    position_militaire_uid: UUID | None = None
    fonction_actuelle_uid: UUID | None = None

    nom_conjoint: str | None = None
    prenoms_conjoint: str | None = None
    profession_conjoint: str | None = None
    matricule_cnps_conjoint: str | None = None
    
    cree_par_uid: UUID | None = None 
    modifie_par_uid: UUID | None = None
    supprime_par_uid: UUID | None = None
    nature_piece_identite_uid: UUID | None = None
    genre_uid: UUID | None = None
    type_agent_uid: UUID | None = None
    user_uid: UUID | None = None
    nationalite_uid: UUID | None = None
    type_recrutement_uid: UUID | None = None
    structure_uid: UUID | None = None
    fonction_uid: UUID | None = None
    situation_matrimoniale_uid: UUID | None = None
    specialite_uid: UUID | None = None
    situation_administrative_uid: UUID | None = None
    grade_uid: UUID | None = None
    statut_uid: UUID | None = None
    validation_fiche_uid: UUID | None = None
    role_uid: UUID | None = None
    permissions: list[PermissionModel] = Field(default_factory=list)
    
    @field_validator( "nom","prenoms","matricule", mode="before")
    @classmethod
    def validate_champ_strength(
        cls,
        value: str,
        info: ValidationInfo
    ) -> str:
    
        value = value.strip()
    
        if not value:
            raise ValueError(
                f"Le {info.field_name} ne doit pas être vide."
            )
    
        return value
    

class ConjointCreateModel(BaseModel):
    nom_conjoint: str | None = None
    prenoms_conjoint: str | None = None
    profession_conjoint: str | None = None
    matricule_cnps_conjoint: str | None = None


class SituationAdministrativeCreateModel(BaseModel):
    numero_acte_nomination_dans_emploi: str | None = None 
    date_signature_acte_nomination_dans_emploi: datetime | None = None
    date_premiere_prise_service_fonction_publique: datetime | None = None
    date_depart_retraite: datetime | None = None
    date_radiation: datetime | None = None
    date_depart_mouvement: datetime | None = None
    date_retour_mouvement: datetime | None = None
    adresse_bureau: str | None = None
    adresse_personnelle: str | None = None
    telephone_bureau: str | None = None
    telephone_domicile: str | None = None
    numero_telephone_1: str | None = None
    numero_telephone_2: str | None = None
    email_institutionnel: str | None = None
    designation_poste: str | None = None
    numero_acte_nomination_fonctionactuelle: str | None = None
    date_signature_acte_nomination_fonctionactuelle: datetime | None = None
    is_equivqlence: bool | None = None
    statut_situation_administrative_uid: UUID | None = None
    emploi_uid: UUID | None = None
    classe_situation_administrative_uid: UUID | None = None
    echelon_uid: UUID | None = None
    nature_acte_nomination_dans_emploi_uid: UUID | None = None
    nature_acte_nomination_dans_fonctionactuelle_uid: UUID | None = None
    diplome_uid: UUID | None = None
    position_administrative_uid: UUID | None = None
    position_militaire_uid: UUID | None = None
    fonction_actuelle_uid: UUID | None = None
    


class Agent(BaseModel):
    uid: uuid.UUID
    nom: str = Field(max_length=255,nullable=False)
    prenoms: str | None = Field(max_length=255,nullable=False)
    matricule: str | None = None
    code: str | None = None
    date_naissance: datetime | None = None
    lieu_naissance: str | None = None
    telephone_principal: str | None = None
    telephone_secondaire: str | None = None
    email_professionnel: str | None = None
    email_personnel: str | None = None
    quartier: str | None = None
    nom_jeune_fille: str | None = None
    lieu_habitation: str | None = None
    date_recrutement: datetime | None = None
    date_depart: datetime | None = None
    nombre_enfant: int = Field(default=0)
    nom_prenoms_pere: str | None = None
    nom_prenoms_mere: str | None = None
    numero_piece_identite: str | None = None
    cree_le: datetime | None = None
    modifie_le: datetime | None = None 
    preinscrit_le: datetime | None = None 
    etat_handicap: bool | None = None
    is_mode: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    est_preinscrit: bool = Field(default=False)
    supprime_le: datetime | None = None
    date_premiere_prise_service_dans_structure: datetime | None = None   
    date_premiere_prise_service_fonction_publique: datetime | None = None
    conjoint_uid: UUID | None = None
    cree_par_uid: UUID | None = None 
    cree_par_uid: UUID | None = None
    modifie_par_uid: UUID | None = None
    supprime_par_uid: UUID | None = None
    nature_piece_identite_uid: UUID | None = None
    genre_uid: UUID | None = None
    nature_acte_nomination_fonctionactuelle_uid: UUID | None = None
    type_agent_uid: UUID | None = None
    user_uid: UUID | None = None
    nationalite_uid: UUID | None = None
    type_recrutement_uid: UUID | None = None
    structure_uid: UUID | None = None
    fonction_uid: UUID | None = None
    situation_matrimoniale_uid: UUID | None = None
    specialite_uid: UUID | None = None
    situation_administrative_uid: UUID | None = None
    grade_uid: UUID | None = None
    statut_uid: UUID | None = None
    validation_fiche_uid: UUID | None = None
    
    
    

class AgentUpdateModel(BaseModel):
    agent_uid: uuid.UUID
    nom: str = Field(max_length=255,nullable=False)
    prenoms: str | None = Field(max_length=255,nullable=False)
    matricule: str | None = None
    code: str | None = None
    date_naissance: datetime | None = None
    lieu_naissance: str | None = None
    telephone_principal: str | None = None
    telephone_secondaire: str | None = None
    email_professionnel: str | None = None
    email_personnel: str | None = None
    quartier: str | None = None
    nom_jeune_fille: str | None = None
    lieu_habitation: str | None = None
    date_recrutement: datetime | None = None
    date_depart: datetime | None = None
    nombre_enfant: int = Field(default=0)
    nom_prenoms_pere: str | None = None
    nom_prenoms_mere: str | None = None
    numero_piece_identite: str | None = None
    cree_le: datetime | None = None
    modifie_le: datetime | None = None 
    preinscrit_le: datetime | None = None 
    etat_handicap: bool | None = None
    est_preinscrit: bool = Field(default=False)
    supprime_le: datetime | None = None
    date_premiere_prise_service_dans_structure: datetime | None = None   
      
    numero_acte_nomination_dans_emploi: str | None = None 
    date_signature_acte_nomination_dans_emploi: datetime | None = None
    date_premiere_prise_service_fonction_publique: datetime | None = None
    date_depart_retraite: datetime | None = None
    date_radiation: datetime | None = None
    date_depart_mouvement: datetime | None = None
    date_retour_mouvement: datetime | None = None
    adresse_bureau: str | None = None
    adresse_personnelle: str | None = None
    telephone_bureau: str | None = None
    telephone_domicile: str | None = None
    numero_telephone_1: str | None = None
    numero_telephone_2: str | None = None
    email_institutionnel: str | None = None
    designation_poste: str | None = None
    numero_acte_nomination_fonctionactuelle: str | None = None
    date_signature_acte_nomination_fonctionactuelle: datetime | None = None
            
    is_equivqlence: bool | None = None
    statut_situation_administrative_uid: UUID | None = None
    emploi_uid: UUID | None = None
    classe_situation_administrative_uid: UUID | None = None
    echelon_uid: UUID | None = None
    nature_acte_nomination_dans_emploi_uid: UUID | None = None
    nature_acte_nomination_dans_fonctionactuelle_uid: UUID | None = None
    diplome_uid: UUID | None = None
    position_administrative_uid: UUID | None = None
    position_militaire_uid: UUID | None = None
    fonction_actuelle_uid: UUID | None = None
    
    nom_conjoint: str | None = None
    prenoms_conjoint: str | None = None
    profession_conjoint: str | None = None
    matricule_cnps_conjoint: str | None = None
        
    cree_par_uid: UUID | None = None 
    modifie_par_uid: UUID | None = None
    supprime_par_uid: UUID | None = None
    nature_piece_identite_uid: UUID | None = None
    genre_uid: UUID | None = None
    type_agent_uid: UUID | None = None
    user_uid: UUID | None = None
    nationalite_uid: UUID | None = None
    type_recrutement_uid: UUID | None = None
    structure_uid: UUID | None = None
    fonction_uid: UUID | None = None
    situation_matrimoniale_uid: UUID | None = None
    specialite_uid: UUID | None = None
    situation_administrative_uid: UUID | None = None
    grade_uid: UUID | None = None
    statut_uid: UUID | None = None
    validation_fiche_uid: UUID | None = None
    role_uid: UUID | None = None
    permissions: list[PermissionModel] = Field(default_factory=list)
        
    @field_validator( "nom","prenoms","matricule", mode="before")
    @classmethod
    def validate_champ_strength(
        cls,
        value: str,
        info: ValidationInfo
    ) -> str:
        
        value = value.strip()
        
        if not value:
            raise ValueError(
                f"Le {info.field_name} ne doit pas être vide."
            )
        
        return value

    
class RoleResponse(BaseModel):
    uid: UUID
    libelle: str
    code: str

class GenericResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    libelle: str | None= None
    code: str | None  = None


class TypeStructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    libelle: str = Field(max_length=255,nullable=False)
    code: str | None  = Field(default=None, max_length=255,nullable=True)


class StructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    libelle: str = Field(max_length=255,nullable=False)
    code: str | None  = Field(default=None, max_length=255,nullable=True)
    typestructure: TypeStructureResponse | None = None

class RoleResponse(BaseModel):
    uid: UUID
    libelle: str
    code: str


class PermissionResponse(BaseModel):
    uid: UUID
    libelle: str
    code: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    username: str
    email: EmailStr
    role: RoleResponse | None = None
    permissions: list[PermissionResponse] = Field(
        default_factory=list
    )

class ConjointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    nom: str | None = None
    prenoms: str | None = None
    matricule_cnps: str | None = None
    profession: str | None = None
    code: str | None = None
    cree_le: datetime | None = None
    modifie_le: datetime | None = None
    is_mode: bool | None = None
    modifie_le: datetime | None = None
    supprime_le: datetime | None = None

class SituationAdministrativeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    numero_acte_nomination_dans_emploi: str | None = None 
    date_signature_acte_nomination_dans_emploi: datetime | None = None
    date_premiere_prise_service_fonction_publique: datetime | None = None
    date_depart_retraite: datetime | None = None
    date_radiation: datetime | None = None
    date_depart_mouvement: datetime | None = None
    date_retour_mouvement: datetime | None = None
    adresse_bureau: str | None = None
    adresse_personnelle: str | None = None
    telephone_bureau: str | None = None
    telephone_domicile: str | None = None
    numero_telephone_1: str | None = None
    numero_telephone_2: str | None = None
    email_institutionnel: str | None = None
    designation_poste: str | None = None
    numero_acte_nomination_fonctionactuelle: str | None = None
    date_signature_acte_nomination_fonctionactuelle: datetime | None = None
    is_equivqlence: bool | None = None
    statut_situation_administrative: GenericResponse | None = None
    emploi: GenericResponse | None = None
    classe_situation_administrative: GenericResponse | None = None
    echelon: GenericResponse | None = None
    nature_acte_nomination_dans_emploi: GenericResponse | None = None
    nature_acte_nomination_dans_fonctionactuelle: GenericResponse | None = None
    diplome: GenericResponse | None = None
    position_administrative: GenericResponse | None = None
    position_militaire: GenericResponse | None = None
    fonction_actuelle: GenericResponse | None = None

    
class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    nom: str 
    prenoms: str 
    matricule: str 
    code: str | None = None
    date_naissance: datetime | None = None
    lieu_naissance: str | None = None
    telephone_principal: str | None = None
    telephone_secondaire: str | None = None
    email_professionnel: str | None = None
    email_personnel: str | None = None
    quartier: str | None = None
    nom_jeune_fille: str | None = None
    lieu_habitation: str | None = None
    date_recrutement: datetime | None = None
    date_depart: datetime | None = None
    nombre_enfant: int = Field(default=0)
    nom_prenoms_pere: str | None = None
    nom_prenoms_mere: str | None = None
    numero_piece_identite: str | None = None
    cree_le: datetime | None = None
    modifie_le: datetime | None = None 
    preinscrit_le: datetime | None = None 
    etat_handicap: bool | None = None
    is_mode: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    est_preinscrit: bool = Field(default=False)
    supprime_le: datetime | None = None
    date_premiere_prise_service_dans_structure: datetime | None = None   
    date_premiere_prise_service_fonction_publique: datetime | None = None
    conjoint: ConjointResponse | None = None 
    nature_piece_identite: GenericResponse | None = None
    genre: GenericResponse | None = None
    nature_acte_nomination_fonctionactuelle: GenericResponse | None = None
    type_agent: GenericResponse | None = None
    user: UserResponse | None = None
    nationalite: GenericResponse | None = None
    structure: GenericResponse | None = None
    fonction: GenericResponse | None = None
    situation_matrimoniale: GenericResponse | None = None
    specialite: GenericResponse | None = None
    situation_administrative: SituationAdministrativeResponse | None = None
    grade: GenericResponse | None = None
    statut: GenericResponse | None = None
    validation_fiche: GenericResponse | None = None
    typestructure: TypeStructureResponse | None =None
    cree_par: UserResponse | None =None
    modifie_par: UserResponse | None =None
    supprime_par: UserResponse | None =None
    
    

class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[AgentResponse] = None

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | AgentResponse = None



