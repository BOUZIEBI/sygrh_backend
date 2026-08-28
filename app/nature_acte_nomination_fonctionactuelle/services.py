from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.nature_acte_nomination_fonctionactuelle import NatureActeNominationFonctionactuelle
from sqlalchemy.orm import selectinload
from typing import Optional



class NatureActeNominationFonctionactuelleService:
    async def get_all_nature_acte_nomination_fonctionactuelles(
        self,
        session: AsyncSession
    ) -> list[NatureActeNominationFonctionactuelle]:

        statement = (
            select(NatureActeNominationFonctionactuelle)
            .order_by(
                desc(NatureActeNominationFonctionactuelle.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_nature_acte_nomination_fonctionactuelle(self, genre_uid: UUID, session: AsyncSession):
        statement = (
            select(NatureActeNominationFonctionactuelle)
            .where(NatureActeNominationFonctionactuelle.uid == genre_uid)
        )

        result = await session.exec(statement)
        nature_acte_nomination_fonctionactuelle = result.first()
        return nature_acte_nomination_fonctionactuelle
      

    async def get_nature_acte_nomination_fonctionactuelle_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[NatureActeNominationFonctionactuelle]:
        statement = select(NatureActeNominationFonctionactuelle).where(NatureActeNominationFonctionactuelle.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_nature_acte_nomination_fonctionactuelle_by_id(
        self,
        db: AsyncSession,
        nature_acte_nomination_fonctionactuelle_uid: UUID
    ) -> Optional[NatureActeNominationFonctionactuelle]:
        statement = select(NatureActeNominationFonctionactuelle).where(NatureActeNominationFonctionactuelle.uid == nature_acte_nomination_fonctionactuelle_uid)
        result = await db.exec(statement)
        return result.first()





