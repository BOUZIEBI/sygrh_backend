import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
T = TypeVar("T")



class PhotothequeCreateModel(BaseModel):
    
    titre: str = Field(max_length=255, index=True)
    description: str | None = None
    lieu: str | None = None
    date_evenement: datetime | None = None
    categorie_uid: UUID | None = None
    statut: str 
    object_key : str | None = None

    
    @field_validator( "titre","description",  mode="before") 
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
    
    
    

class PhotothequeUpdateModel(BaseModel):
    titre: str = Field(max_length=255, index=True)
    description: str | None = None
    lieu: str | None = None
    date_evenement: datetime | None = None
    categorie_uid: UUID | None = None
    statut: str 
    fichier_key : str | None = None
    
    @field_validator( "titre","description", mode="before")
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

    
class PhotothequeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    
    titre: str 
    slug: str | None=None
    description: str | None = None

    # Image représentant l’album
    image_couverture_url: str | None = None
    # Informations sur l’événement
    lieu: str | None = None
    date_evenement: datetime | None = None

    # Classement
    categorie_uid: UUID | None = None
    #statut actualite: brouillon, publie ou archive
    statut: str 
    
    est_mis_en_avant: bool 
    ordre_affichage: int 
    date_publication: datetime | None = None
    # Statistiques
    nombre_vues: int 
    
    fichier_key: str | None = None

    categorie: GenericResponse | None = None
    # Traçabilité
    cree_le: datetime 
    modifie_le: datetime 
    cree_par: UserResponse | None = None
    modifie_par: UserResponse | None = None

    # Suppression logique
    is_deleted: bool 
    supprime_le: datetime | None = None
    supprime_par: UserResponse | None = None
    
    

class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[PhotothequeResponse] = None
    

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | PhotothequeResponse = None



