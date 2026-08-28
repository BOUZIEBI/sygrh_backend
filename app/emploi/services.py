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
from app.emploi.schemas import EmploiCreateModel, EmploiUpdateModel, EmploiResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException
from app.db.models.emploi import Emploi
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class EmploiService:
    async def get_all_emplois(
        self,
        session: AsyncSession
    ) -> list[Emploi]:

        statement = (
            select(Emploi)
            .order_by(
                desc(Emploi.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_fonction(self, emploi_uid: UUID, session: AsyncSession):
        statement = (
            select(Emploi)
            .where(Emploi.uid == emploi_uid)
        )

        result = await session.exec(statement)
        fonction = result.first()
        return fonction
      

    async def get_emploi_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Emploi]:
        statement = select(Emploi).where(Emploi.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_emploi_by_id(
        self,
        db: AsyncSession,
        emploi_uid: UUID
    ) -> Optional[Emploi]:
        statement = select(Emploi).where(Emploi.uid == emploi_uid)
        result = await db.exec(statement)
        return result.first()





