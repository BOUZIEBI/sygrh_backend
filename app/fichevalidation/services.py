from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.core.exceptions_metier import RaiseException
from app.db.models.fiche_validation import FicheValidation
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class FicheValidationService:
    async def get_all_fichevalidations(
        self,
        session: AsyncSession
    ) -> list[FicheValidation]:

        statement = (
            select(FicheValidation)
            .order_by(
                desc(FicheValidation.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_fichevalidation(self, fichevalidation_uid: UUID, session: AsyncSession):
        statement = (
            select(FicheValidation)
            .where(FicheValidation.uid == fichevalidation_uid)
        )

        result = await session.exec(statement)
        fichevalidation = result.first()
        return fichevalidation
      

    async def get_fichevalidation_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[FicheValidation]:
        statement = select(FicheValidation).where(FicheValidation.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_fichevalidation_by_id(
        self,
        db: AsyncSession,
        fichevalidation_uid: UUID
    ) -> Optional[FicheValidation]:
        statement = select(FicheValidation).where(FicheValidation.uid == fichevalidation_uid)
        result = await db.exec(statement)
        return result.first()





