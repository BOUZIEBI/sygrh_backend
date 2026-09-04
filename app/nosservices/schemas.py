import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
T = TypeVar("T")



class NosservicesCreateModel(BaseModel):
    # Identification
    libelle: str = Field(max_length=255, index=True)
    # Présentation
    description_courte: str | None = Field(default=None,max_length=500,)
    description: str | None = None
    object_key : str | None = None
    # Publication
    statut: str
    ordre_affichage: int 
    
    @field_validator( "libelle","description",  mode="before") 
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
    
    
    
    

class NosservicesUpdateModel(BaseModel):
    # Identification
    libelle: str = Field(max_length=255, index=True)
    # Présentation
    description_courte: str | None = Field(default=None,max_length=500,)
    description: str | None = None
    fichier_key : str | None = None
    # Publication
    statut: str
    ordre_affichage: int 
    
    
    @field_validator( "libelle","description", mode="before")
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
     


class GenericResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    libelle: str | None= None
    code: str | None  = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    username: str
    email: EmailStr

    
class NosservicesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    
    # Identification
    libelle: str 
    code: str | None = None
    slug: str 
    # Présentation
    description_courte: str | None = None
    description: str | None = None
    image_url: str | None = None
    icone: str | None = None

    # Informations pratiques
    conditions_acces: str | None = None
    pieces_requises: str | None = None
    procedure: str | None = None
    delai_traitement: str | None = None
    cout: float | None = None
    lien_demande: str | None = None
    fichier_key: str | None = None
    
    # Contacts
    email: str | None = None
    telephone: str | None = None
    adresse: str | None = None
    horaires: str | None = None

    structure_uid: UUID | None = None
    responsable_uid: UUID | None = None

    # Publication
    statut: str
    ordre_affichage: int 

    # Traçabilité
    cree_le: datetime | None = None
    modifie_le: datetime | None = None

    # Suppression logique
    is_deleted: bool 
    supprime_le: datetime | None = None
    
    cree_par: UserResponse | None =None
    modifie_par: UserResponse | None =None
    supprime_par: UserResponse | None =None
    
    

class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[NosservicesResponse] = None
    

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | NosservicesResponse = None



