import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
from app.auth.schemas import PermissionModel
T = TypeVar("T")



class CommuniqueCreateModel(BaseModel):
   
    #numéro officiel du communiqué, par exemple COM-2026-001
    reference: str | None = Field(
        default=None,
        max_length=100,
        nullable=True,
        unique=True,
        index=True,
    )
    titre: str | None = Field(able=True)            
    resume: str | None = Field(default=None, max_length=500)
    contenu: str
    statut : str | None = Field(able=True)  
    date_expiration : datetime | None = None
    object_key : str | None = None
    
    
    @field_validator( "titre","reference","contenu", mode="before")
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
    
    
    
    

class CommuniqueUpdateModel(BaseModel):
   
    #numéro officiel du communiqué, par exemple COM-2026-001
    reference: str | None = Field(
        default=None,
        max_length=100,
        nullable=True,
        unique=True,
        index=True,
    )
    titre: str | None = Field(default=None,max_length=255,nullable=True)
    slug: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=255,nullable=True)
                    
    resume: str | None = Field(default=None, max_length=500)
    contenu: str
    
    # Document ou illustration
    image_url: str | None = Field(default=None, max_length=500)
    fichier_key: str | None = Field(default=None, max_length=500)
    
    # Statut communiqué : brouillon, publie ou archive
    statut: str  
    est_epingle: bool = Field(default=False, index=True)
    date_publication: datetime | None = Field(default=None, index=True)
    date_expiration: datetime | None = Field(default=None, index=True)
    object_key : str | None = None
    
    # Auteur
    auteur_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid",
        index=True,
    )
    
    # Statistiques
    nombre_vues: int = Field(default=0, ge=0)
    nombre_telechargements: int = Field(default=0, ge=0)
    
    # Traçabilité
    cree_le: datetime | None = None
    modifie_le: datetime | None = None 
    cree_par_uid: UUID | None = None
    modifie_par_uid: UUID | None = None
       
    # Suppression logique
    is_deleted: bool = Field(default=False, index=True)
    supprime_le: datetime | None = None
    supprime_par_uid: UUID | None = None

    @field_validator( "titre","reference","contenu", mode="before")
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

    
class CommuniqueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID

    #numéro officiel du communiqué, par exemple COM-2026-001
    reference: str | None = None
    titre: str | None = None
    slug: str | None = None
    code: str | None = None   
             
    resume: str | None = None
    contenu: str
    
    # Document ou illustration
    image_url: str | None = None
    fichier_key: str | None = None
    
    # Statut communiqué : brouillon, publie ou archive
    statut: str  
    est_epingle: bool 
    date_publication: datetime | None = None
    date_expiration: datetime | None = None
    
    # Auteur
    auteur_uid: UUID | None = None
    
    # Statistiques
    nombre_vues: int 
    nombre_telechargements: int 
    
    # Traçabilité
    cree_le: datetime | None = None
    modifie_le: datetime | None = None 

    # Suppression logique
    is_deleted: bool 
    supprime_le: datetime | None = None
    supprime_par_uid: UUID | None = None

    cree_par: UserResponse | None =None
    modifie_par: UserResponse | None =None
    supprime_par: UserResponse | None =None
    
    

class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[CommuniqueResponse] = None

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | CommuniqueResponse = None



