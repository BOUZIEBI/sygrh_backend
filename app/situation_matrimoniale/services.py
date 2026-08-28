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
from app.situation_matrimoniale.schemas import SituationMatrimonialeCreateModel, SituationMatrimonialeResponse, SituationMatrimonialeUpdateModel
from app.core.exceptions_metier import RaiseException
from app.db.models.situation_matrimoniale import SituationMatrimoniale
from app.db.models.genre import Genre
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class SituationMatrimonialeService:
    async def get_all_situationmatrimoniales(
        self,
        session: AsyncSession
    ) -> list[Genre]:

        statement = (
            select(SituationMatrimoniale)
            .order_by(
                desc(SituationMatrimoniale.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_situationmatrimoniale(self, situationmatrimoniale_uid: UUID, session: AsyncSession):
        statement = (
            select(SituationMatrimoniale)
            .where(SituationMatrimoniale.uid == situationmatrimoniale_uid)
        )

        result = await session.exec(statement)
        situationmatrimoniale = result.first()
        return situationmatrimoniale
      

    async def get_situationmatrimoniale_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Genre]:
        statement = select(SituationMatrimoniale).where(SituationMatrimoniale.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_situationmatrimoniale_by_id(
        self,
        db: AsyncSession,
        situationmatrimoniale_uid: UUID
    ) -> Optional[SituationMatrimoniale]:
        statement = select(SituationMatrimoniale).where(SituationMatrimoniale.uid == situationmatrimoniale_uid)
        result = await db.exec(statement)
        return result.first()





