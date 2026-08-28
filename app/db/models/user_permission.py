import uuid
from datetime import date, datetime, UTC, timezone
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID


class UserPermission(SQLModel, table=True):
    __tablename__ = "user_permissions"
    user_uid: uuid.UUID = Field(
        foreign_key="users.uid",
        primary_key=True,
        nullable=False,
    )

    permission_uid: uuid.UUID = Field(
        foreign_key="permissions.uid",
        primary_key=True,
        nullable=False,
    )