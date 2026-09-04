import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
T = TypeVar("T")



class MessageCreateModel(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    contenu: str
    nom_prenoms_expediteur: str | None = Field(default=None, max_length=255)
    service_expediteur: str | None = Field(default=None, max_length=255)
    
    @field_validator( "email","contenu","nom_prenoms_expediteur","service_expediteur", mode="before") 
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
    
    
    
    

class MessageUpdateModel(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    contenu: str
    nom_prenoms_expediteur: str | None = Field(default=None, max_length=255)
    service_expediteur: str | None = Field(default=None, max_length=255)
        
    @field_validator( "email","contenu","nom_prenoms_expediteur","service_expediteur", mode="before") 
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

    
class _MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    
    # Identification
    email: str 
    code: str | None = None
    contenu: str | None = None
    nom_prenoms_expediteur: str | None = None
    service_expediteur: str | None = None

    # Traçabilité
    cree_le: datetime | None = None
    modifie_le: datetime | None = None

    # Suppression logique
    is_deleted: bool 
    supprime_le: datetime | None = None
    
    

class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[_MessageResponse] = None
    

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | _MessageResponse = None



