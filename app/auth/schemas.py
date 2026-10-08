import uuid
from datetime import datetime
from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, TypeAdapter, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID


T = TypeVar("T")


class RoleResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
    uid: UUID
    libelle: str
    code: str
    
    
class AgentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
    uid: UUID
    nom: str
    prenoms: str

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
    nombre_enfant: int 
    nom_prenoms_pere: str | None = None
    nom_prenoms_mere: str | None = None
    numero_piece_identite: str | None = None
            
    

class PermissionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
    uid: UUID
    libelle: str
    code: str
    

class MessageResponse_(BaseModel, Generic[T]):
    code: int
    success: bool
    message: str
    data: T | None = None
    
    
class LogoutResponse(BaseModel):
    code: int
    success: bool
    message: str

    
class MessageLogoutResponse(BaseModel):
    code: int
    success: bool
    message: str
   

class PermissionModel(BaseModel):
    uid: uuid.UUID
    autorise: bool


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    email: EmailStr
    username: str

    is_active: bool
    is_verified: bool
    is_superuser: bool

    role: RoleResponse | None = None
    agent: AgentResponse | None = None
    permissions: list[PermissionResponse] = Field(
        default_factory=list
    )
    cree_le: datetime | None = Field(
        validation_alias="cree_le"
    )
    modifie_le: datetime | None = Field(
        validation_alias="modifier_le"
    )

class LoginPayload(BaseModel):
    username: str = Field(max_length=40)
    password: str = Field(min_length=6)
   

class UserCreateModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    role_uid: UUID | None = None
    # AJOUT : Liste d'UUID pour les permissions (par défaut une liste vide)
    permissions: list[PermissionModel] = Field(default_factory=list)

    

class AffectationPermissionCreate(BaseModel):
    user_uid: uuid.UUID
    permissions: list[PermissionModel] = Field(default_factory=list)

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True) 
    uid: uuid.UUID
    email: EmailStr
    is_verified: bool
    password_hash: str = Field(exclude=True)
    cree_le: datetime
   
   
    

class UserCreate(BaseModel):
    email: EmailStr | None = None
    password: str = Field(min_length=6)
    role_uid: UUID | None = None
    # AJOUT : Liste d'UUID pour les permissions (par défaut une liste vide)
    permissions: list[PermissionModel] = Field(default_factory=list)
    @field_validator("email", mode="before")
    @classmethod
    def validate_champ_strength(cls, value: str) -> str:

        if value is None:
            raise ValueError(
                "Le champ 'email' ne doit pas être vide."
            )

        value = value.strip().lower()

        if not value:
            raise ValueError(
                "Le champ 'email' ne doit pas être vide."
            )

        try:
            value = str(
                TypeAdapter(EmailStr).validate_python(value)
            )
        except ValueError:
            raise ValueError(
                "Le champ 'email' doit être une adresse email valide."
            )

        return value


class LoginRequest(BaseModel):
    username: EmailStr = Field(
        ...,
        description="Adresse email de l'utilisateur",
        examples=["utilisateur@example.com"],
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Mot de passe de l'utilisateur",
        examples=["MotDePasse@2026"],
    )

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class EmailModel(BaseModel):
    addresses : List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str

class TokenResponse(BaseModel, Generic[T]):
    code:int
    success:bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    data: T | None = None 

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str
    all_devices: bool = False

class PasswordChangeRequest(BaseModel):
    email: EmailStr

class PasswordChangeConfirmRequest(BaseModel):
    token: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class MessageResponse(BaseModel):
    message: str
    debug_token:Optional[str] = None

class LogoutReauest(BaseModel):
    refresh_token: Optional[str]=None
    all_devices:bool=False
    
from uuid import UUID

from pydantic import BaseModel, EmailStr


class AuthenticatedUser(BaseModel):
    uid: UUID
    email: EmailStr


class LoginData(BaseModel):
    expires_in: int
    # Présents uniquement en développement
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None


class LoginResponse(BaseModel):
    code: int
    success: bool
    message: str
    data: LoginData | None
    
class ErrorLoginResponse(BaseModel):
    code: int
    success: bool
    message: str
    remaining:int
    data: LoginData | None
    
class AuthDependenciesResponse(BaseModel):
    code: int
    success: bool
    message: str
    user: UserModel | None = None
    is_access_token: bool
    
    
class LoginRequestData(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=255,
    )
    password: str = Field(
        min_length=1,
    )
    
    
    

