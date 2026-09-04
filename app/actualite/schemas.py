import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
T = TypeVar("T")



class ActualiteCreateModel(BaseModel):
    titre: str | None = Field(default=None,max_length=255,nullable=True)
    slug: str | None = Field(default=None,max_length=255,nullable=True)
    resume: str | None = Field(default=None, max_length=500)
    contenu: str 
    categorie_uid: UUID | None = Field(default=None,foreign_key="categorie_actualites.uid",index=True,)
    #statut actualite: brouillon, publie ou archive
    statut: str = Field(default="brouillon", max_length=30, index=True)
    est_a_la_une: bool = Field(default=False, index=True)
    date_publication: datetime | None = Field(default=None, index=True)
    object_key : str | None = None
    
    @field_validator( "titre","contenu", mode="before") 
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
    
    
    
    

class ActualiteUpdateModel(BaseModel):
    titre: str | None = Field(default=None,max_length=255,nullable=True)
    slug: str | None = Field(default=None,max_length=255,nullable=True)
    resume: str | None = Field(default=None, max_length=500)
    contenu: str 
    categorie_uid: UUID | None = Field(default=None,foreign_key="categorie_actualites.uid",index=True,)
    #statut actualite: brouillon, publie ou archive
    statut: str = Field(default="brouillon", max_length=30, index=True)
    est_a_la_une: bool = Field(default=False, index=True)
    date_publication: datetime | None = Field(default=None, index=True)
    fichier_key : str | None = None
    
    @field_validator( "titre","contenu", mode="before")
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

class CategorieActualiteResponse(BaseModel):
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

    
class ActualiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    
    titre: str | None = None
    slug: str | None = None
        
    resume: str | None = None
    contenu: str

    fichier_key : str | None = None
    image_alt: str | None = None

    auteur_uid: UUID | None = None

    categorie_uid: UUID | None = None
    
    #statut actualite: brouillon, publie ou archive
    statut: str 
    est_a_la_une: bool 
    nombre_vues: int 

    date_publication: datetime | None = None
    cree_le: datetime 
    modifie_le: datetime 
    is_deleted: bool 
    supprime_le: datetime | None = None
    
    categorie_actualite: CategorieActualiteResponse | None = None
    
    cree_par: UserResponse | None =None
    modifie_par: UserResponse | None =None
    supprime_par: UserResponse | None =None
    
    

class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[ActualiteResponse] = None
    

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | ActualiteResponse = None



