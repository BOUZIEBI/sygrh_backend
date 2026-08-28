import uuid
from datetime import datetime
from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, TypeAdapter, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID


T = TypeVar("T")


class RoleResponse(BaseModel):
    uid: UUID
    libelle: str
    code: str

class PermissionResponse(BaseModel):
    uid: UUID
    libelle: str
    code: str

class MessageResponse_(BaseModel, Generic[T]):
    code: int
    success: bool
    message: str
    data: T | None = None

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
    permissions: list[PermissionResponse] = Field(
        default_factory=list
    )
    cree_le: datetime | None = Field(
        validation_alias="cree_le"
    )
    modifie_le: datetime | None = Field(
        validation_alias="modifier_le"
    )


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
    uid: uuid.UUID
    email: EmailStr
    is_verified: bool
    password_hash: str = Field(exclude=True)
    cree_le: datetime
    modifie_le: datetime

class UserCreate(BaseModel):
    email: EmailStr
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

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

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

