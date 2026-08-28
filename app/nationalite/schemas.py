import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
T = TypeVar("T")

class NationaliteCreateModel(BaseModel):
    libelle: str = Field(max_length=255)
    code: str = Field(max_length=25)

    model_config = {
        "json_schema_extra": {
            "example": {
                "libelle": "CNI",
                "code": "CNI",
            }
        }
    }


class Nationalite(BaseModel):
    uid: uuid.UUID
    libelle: str
    code: str | None = Field(default=None, max_length=255)
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    

class NationaliteUpdateModel(BaseModel):
    uid: uuid.UUID
    libelle: str
    code: str | None = Field(default=None, max_length=255)
    cree_le: datetime | None = Field(default=None)
    modifie_le: datetime | None = Field(default=None)
    supprime_le: datetime | None = Field(default=None)
    
    @field_validator("uid", "libelle", "code", mode="before")
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


class NationaliteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    libelle: str
    code: str | None = Field(default=None, max_length=255)
    cree_le: datetime | None
    modifie_le: datetime | None 
    supprime_le: datetime | None 


class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[NationaliteResponse] = None

class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | NationaliteResponse = None



