from __future__ import annotations
import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from typing import List, Optional, TYPE_CHECKING
import hashlib
import secrets


class AuthSession(SQLModel, table=True):
    __tablename__ = "auth_sessions"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    refresh_token_hash: str
    is_revoked: bool = Field(default=False)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )
    replaced_by_session_id: Optional[str] = None


def generate_raw_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def utcnow() -> datetime:
    return datetime.now(UTC)
