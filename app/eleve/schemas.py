import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
from app.auth.schemas import PermissionModel
from app.auth.schemas import PermissionResponse
T = TypeVar("T")


class Eleve(BaseModel):
    uid: uuid.UUID
    nom: str
    prenoms: str
    matricule: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=255)
    date_naissance: datetime | None = Field(default=None)
    lieu_naissance: str | None = Field(default=None, max_length=255)
    numero_table: str | None = Field(default=None, max_length=255)
    statut_affectation_uid: UUID | None = None
    statut_anneescolaire_uid: UUID | None = None
    is_active: bool | None = Field(default=None)
    is_mode: bool | None = Field(default=None)
    is_deleted: bool | None = Field(default=None)
    quartier: str | None = Field(default=None, max_length=255)
    etablissement_origine: str | None = Field(default=None, max_length=255)
    genre_uid: UUID | None = None
    user_uid: UUID | None = None
    nationalite_uid: UUID | None = None
    pays_uid: UUID | None = None
    ville_uid: UUID | None = None
    commune_uid: UUID | None = None
    structure_uid: UUID | None = None
    classe_uid: UUID | None = None
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    cree_par: UUID | None = None
    modifie_par: UUID | None = None
    supprime_par: UUID | None = None
    statut_affectation_uid: UUID | None = None
    statut_anneescolaire_uid: UUID | None = None
    statut_juridique_uid: UUID | None = None
    role_uid: UUID | None = None


class GetEleveModel(BaseModel):
    eleve_uid: str


class EleveCreateModel(BaseModel):
    nom: str
    prenoms: str
    matricule: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=255)
    date_naissance: datetime | None = Field(default=None)
    lieu_naissance: str | None = Field(default=None, max_length=255)
    numero_table: str | None = Field(default=None, max_length=255)
    is_active: bool | None = Field(default=None)
    is_mode: bool | None = Field(default=None)
    is_deleted: bool | None = Field(default=None)
    etablissement_origine: str | None = Field(default=None, max_length=255)
    genre_uid: UUID | None = None
    user_uid: UUID | None = None
    nationalite_uid: UUID | None = None
    pays_uid: UUID | None = None
    ville_uid: UUID | None = None
    commune_uid: UUID | None = None
    structure_uid: UUID | None = None
    classe_uid: UUID | None = None
    role_uid: UUID | None = None
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    cree_par_uid: UUID | None = None
    modifie_par_uid: UUID | None = None
    supprime_par_uid: UUID | None = None
    statut_affectation_uid: UUID | None = None
    statut_anneescolaire_uid: UUID | None = None
    type_structure_uid: UUID | None = None
    statut_juridique_uid: UUID | None = None
    permissions: list[PermissionModel] = Field(default_factory=list)


class EleveUpdateModel(BaseModel):
    uid: uuid.UUID
    nom: str
    prenoms: str
    matricule: str | None = Field(default=None, max_length=255)
    date_naissance: datetime | None = Field(default=None)
    lieu_naissance: str | None = Field(default=None, max_length=255)
    numero_table: str | None = Field(default=None, max_length=255)
    is_active: bool | None = Field(default=None)
    is_mode: bool | None = Field(default=None)
    is_deleted: bool | None = Field(default=None)
    genre_uid: UUID | None = None
    classe_uid: UUID | None = None
    role_uid: UUID | None = None
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    cree_par_uid: UUID | None = None
    modifie_par_uid: UUID | None = None
    supprime_par_uid: UUID | None = None
    statut_affectation_uid: UUID | None = None
    permissions: list[PermissionModel] = Field(default_factory=list)
  
    @field_validator("uid", "nom", "prenoms", mode="before")
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

        if len(value) >= 255:
            raise ValueError(
                f"Le {info.field_name} doit contenir moins de 255 caractères."
            )

        return value

class GenericResponse(BaseModel):
    uid: UUID
    libelle: str
    code: str

class RoleResponse(BaseModel):
    uid: UUID
    libelle: str
    code: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    username: str
    email: EmailStr
    permissions: list[PermissionResponse] = Field(
        default_factory=list
    )

class EleveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    nom: str
    prenoms: str
    matricule: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=255)
    date_naissance: datetime | None 
    lieu_naissance: str | None = Field(default=None, max_length=255)
    numero_table: str | None = Field(default=None, max_length=255)
    statut_anneescolaire: str | None = Field(default=None, max_length=255)
    is_active: bool | None 
    is_mode: bool | None 
    is_deleted: bool | None 
    quartier: str | None = Field(default=None, max_length=255)
    etablissement_origine: str | None = Field(default=None, max_length=255)
    genre: GenericResponse | None = None
    user: UserResponse | None = None
    nationalite_uid: GenericResponse | None = None
    pays_uid: GenericResponse | None = None
    ville_uid: GenericResponse | None = None
    commune_uid: GenericResponse | None = None
    classe_uid: GenericResponse | None = None
    role: RoleResponse | None = None
    cree_le: datetime | None
    modifie_le: datetime | None 
    supprime_le: datetime | None 
    cree_par: UserResponse | None = None
    modifie_par: UserResponse | None = None
    supprime_par: UserResponse | None = None
    structure: GenericResponse | None = None
    statut_etablissement: GenericResponse | None = None


class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[EleveResponse] = None

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | EleveResponse = None



