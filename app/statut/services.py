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
from app.db.models.statut import Statut
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class StatutService:
    async def get_all_statuts(
        self,
        session: AsyncSession
    ) -> list[Statut]:

        statement = (
            select(Statut)
            .order_by(
                desc(Statut.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_statut(self, statut_uid: UUID, session: AsyncSession):
        statement = (
            select(Statut)
            .where(Statut.uid == statut_uid)
        )

        result = await session.exec(statement)
        statut = result.first()
        return statut
      

    async def get_statut_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Statut]:
        statement = select(Statut).where(Statut.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_statut_by_id(
        self,
        db: AsyncSession,
        statut_uid: UUID
    ) -> Optional[Statut]:
        statement = select(Statut).where(Statut.uid == statut_uid)
        result = await db.exec(statement)
        return result.first()





