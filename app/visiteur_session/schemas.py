import uuid
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationInfo, field_validator
from uuid import UUID
T = TypeVar("T")



class VisiteurSessionCreateModel(BaseModel):
    session_uid: UUID | None = None
    adresse_ip: str 
    user_agent: str | None = None
    cree_le: datetime 
    derniere_activite_le: datetime 
    expire_le: datetime 
    est_active: bool 
    
    @field_validator( "adresse_ip", mode="before")
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
    

class VisiteurSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    session_uid: UUID | None = None
    adresse_ip: str 
    user_agent: str | None = None
    cree_le: datetime 
    derniere_activite_le: datetime 
    expire_le: datetime 
    est_active: bool 
    

class MessageAllResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | List[VisiteurSessionResponse] = None


class MessageResponse(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool = True
    data: T | None | VisiteurSessionResponse = None



