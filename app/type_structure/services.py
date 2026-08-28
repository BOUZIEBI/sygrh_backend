from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.type_structure.schemas import TypeStructureCreateModel, TypeStructureResponse, TypeStructureUpdateModel
from app.core.exceptions_metier import RaiseException
from app.db.models.type_structure import TypeStructure
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class TypestructureService:
    async def get_all_typestructures(
        self,
        session: AsyncSession
    ) -> list[TypeStructure]:

        statement = (
            select(TypeStructure)
            .order_by(
                desc(TypeStructure.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_typestructure(self, type_structure_uid: UUID, session: AsyncSession):
        statement = (
            select(TypeStructure)
            .where(TypeStructure.uid == type_structure_uid)
        )

        result = await session.exec(statement)
        type_structure = result.first()
        return type_structure
      

    async def get_typestructure_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[TypeStructure]:
        statement = select(TypeStructure).where(TypeStructure.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_typestructure_by_id(
        self,
        db: AsyncSession,
        typestructure_uid: UUID
    ) -> Optional[TypeStructure]:
        statement = select(TypeStructure).where(TypeStructure.uid == typestructure_uid)
        result = await db.exec(statement)
        return result.first()





