from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.naturepieceidentite.schemas import NaturepieceidentiteCreateModel, NaturepieceidentiteResponse, NaturepieceidentiteUpdateModel
from app.core.exceptions_metier import RaiseException
from app.db.models.type_agent import TypeAgent
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class TypeagentService:
    async def get_all_typeagents(
        self,
        session: AsyncSession
    ) -> list[TypeAgent]:

        statement = (
            select(TypeAgent)
            .order_by(
                desc(TypeAgent.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_typeagent(self, type_agent_uid: UUID, session: AsyncSession):
        statement = (
            select(TypeAgent)
            .where(TypeAgent.uid == type_agent_uid)
        )

        result = await session.exec(statement)
        type_agent = result.first()
        return type_agent
      

    async def get_typeagent_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[TypeAgent]:
        statement = select(TypeAgent).where(TypeAgent.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_typeagent_by_id(
        self,
        db: AsyncSession,
        typeagent_uid: UUID
    ) -> Optional[TypeAgent]:
        statement = select(TypeAgent).where(TypeAgent.uid == typeagent_uid)
        result = await db.exec(statement)
        return result.first()





