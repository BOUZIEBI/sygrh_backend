
from __future__ import annotations
import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Integer
from uuid import UUID



class LoginAttemptState(SQLModel, table=True):
    __tablename__ = "login_attempt_states"

    user_id: uuid.UUID = Field(
        foreign_key="users.uid",
        primary_key=True
    )
    failed_attempts: int = Field(
        default=0,
        sa_column=Column(
            Integer,
            nullable=False
        )
    )
    locked_until: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    