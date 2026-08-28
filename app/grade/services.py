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
from app.core.exceptions_metier import RaiseException
from app.db.models.grade import Grade
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class GradeService:
    async def get_all_grades(
        self,
        session: AsyncSession
    ) -> list[Grade]:

        statement = (
            select(Grade)
            .order_by(
                desc(Grade.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_grade(self, grade_uid: UUID, session: AsyncSession):
        statement = (
            select(Grade)
            .where(Grade.uid == grade_uid)
        )

        result = await session.exec(statement)
        grade = result.first()
        return grade
      

    async def get_grade_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Grade]:
        statement = select(Grade).where(Grade.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_grade_by_id(
        self,
        db: AsyncSession,
        grade_uid: UUID
    ) -> Optional[Grade]:
        statement = select(Grade).where(Grade.uid == grade_uid)
        result = await db.exec(statement)
        return result.first()





