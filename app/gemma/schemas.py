# app/gemma/schemas.py

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=4000,
    )