from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.db.models.login_attempt_state import LoginAttemptState
from app.db.models.password_reset_token import PasswordResetToken
from app.nationalite.schemas import NationaliteCreateModel, NationaliteResponse, NationaliteUpdateModel
from app.core.exceptions_metier import RaiseException
from app.db.models.nationalite import Nationalite
from app.db.models.nationalite import Nationalite
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class NationaliteService:
    async def get_all_nationalites(
        self,
        session: AsyncSession
    ) -> list[Nationalite]:

        statement = (
            select(Nationalite)
            .order_by(
                desc(Nationalite.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_nationalite(self, nationalite_uid: UUID, session: AsyncSession):
        statement = (
            select(Nationalite)
            .where(Nationalite.uid == nationalite_uid)
        )

        result = await session.exec(statement)
        nationalite = result.first()
        return nationalite
      

    async def get_nationalite_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Nationalite]:
        statement = select(Nationalite).where(Nationalite.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_nationalite_by_id(
        self,
        db: AsyncSession,
        nationalite_uid: UUID
    ) -> Optional[Nationalite]:
        statement = select(Nationalite).where(Nationalite.uid == nationalite_uid)
        result = await db.exec(statement)
        return result.first()





