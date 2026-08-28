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
from app.naturepieceidentite.schemas import NaturepieceidentiteCreateModel, NaturepieceidentiteResponse, NaturepieceidentiteUpdateModel
from app.core.exceptions_metier import RaiseException
from app.db.models.nature_piece_identite import NaturePieceidentite
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class NaturepieceidentiteService:
    async def get_all_naturepieceidentites(
        self,
        session: AsyncSession
    ) -> list[NaturePieceidentite]:

        statement = (
            select(NaturePieceidentite)
            .order_by(
                desc(NaturePieceidentite.libelle)
            )
        )

        result = await session.exec(statement)

        return result.all()
    

    async def get_naturepieceidentite(self, naturepieceidentite_uid: UUID, session: AsyncSession):
        statement = (
            select(NaturePieceidentite)
            .where(NaturePieceidentite.uid == naturepieceidentite_uid)
        )

        result = await session.exec(statement)
        naturepieceidentite = result.first()
        return naturepieceidentite
      

    async def get_naturepieceidentite_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[NaturePieceidentite]:
        statement = select(NaturePieceidentite).where(NaturePieceidentite.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_naturepieceidentite_by_id(
        self,
        db: AsyncSession,
        naturepieceidentite_uid: UUID
    ) -> Optional[NaturePieceidentite]:
        statement = select(NaturePieceidentite).where(NaturePieceidentite.uid == naturepieceidentite_uid)
        result = await db.exec(statement)
        return result.first()





