import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
T = TypeVar("T")



class StructureCreateModel(BaseModel):
    libelle: str = Field(max_length=255,nullable=False)
    abreviation: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    description: str | None = Field(default=None)
    slug: str | None = Field(default=None)
    code: str | None = Field(default=None)
    personne_contact: str | None = Field(default=None)
    telephone_personne_contact: str | None = Field(default=None,max_length=255)
    anneecreation: str | None = Field(default=None,max_length=255,nullable=True)
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    adressecomplete: str | None = Field(default=None,max_length=255,nullable=True)
    email: str | None = Field(default=None,max_length=255,nullable=True)
    telephone: str | None = Field(default=None,max_length=255,nullable=True)
    siteweb: str | None = Field(default=None,max_length=255,nullable=True)
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    type_structure_uid: UUID | None = None
    
    @field_validator( "libelle", mode="before")
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


class Structure(BaseModel):
    uid: uuid.UUID
    libelle: str = Field(max_length=255,nullable=False)
    abreviation: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    is_mode: bool | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    description: str | None = Field(default=None)
    slug: str | None = Field(default=None)
    code: str | None = Field(default=None)
    personne_contact: str | None = Field(default=None)
    telephone_personne_contact: str | None = Field(default=None,max_length=255)
    anneecreation: str | None = Field(default=None,max_length=255,nullable=True)
    quartier: str | None = Field(default=None,max_length=255,nullable=True)
    adressecomplete: str | None = Field(default=None,max_length=255,nullable=True)
    email: str | None = Field(default=None,max_length=255,nullable=True)
    telephone: str | None = Field(default=None,max_length=255,nullable=True)
    siteweb: str | None = Field(default=None,max_length=255,nullable=True)
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    type_structure_uid: UUID | None = None
    
    

class StructureUpdateModel(BaseModel):
    uid: uuid.UUID
    libelle: str = Field(max_length=255,nullable=False)
    abreviation: str | None = Field(default=None,max_length=255,nullable=True)
    code: str | None = Field(default=None,max_length=50,nullable=True)
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    is_mode: bool | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    description: str | None = None
    slug: str | None = Field(default=None)
    code: str | None = Field(default=None)
    personne_contact: str | None = None
    telephone_personne_contact: str | None = None
    anneecreation: str | None = None
    quartier: str | None = None
    adressecomplete: str | None = None
    email: str | None = None
    telephone: str | None = None
    siteweb: str | None = None
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    type_structure_uid: UUID | None = None
    
    
    
    @field_validator("uid", "libelle", mode="before")
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


class TypeStructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    libelle: str = Field(max_length=255,nullable=False)
    code: str | None  = Field(default=None, max_length=255,nullable=True)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    username: str
    email: EmailStr
    

class StructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    libelle: str 
    abreviation: str | None = None
    cree_le: datetime | None = None
    modifie_le: datetime | None = None
    supprime_le: datetime | None = None
    description: str | None =None
    slug: str | None =None
    code: str | None = None
    personne_contact: str | None = None
    telephone_personne_contact: str | None 
    anneecreation: str | None = None
    quartier: str | None = None
    adressecomplete: str | None = None
    email: str | None = None
    telephone: str | None = None
    siteweb: str | None = None
    is_mode: bool | None = None
    is_deleted: bool | None =None
    typestructure: TypeStructureResponse | None =None
    cree_par: UserResponse | None =None
    modifie_par: UserResponse | None =None
    supprime_par: UserResponse | None =None
    


class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[StructureResponse] = None

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | StructureResponse = None



