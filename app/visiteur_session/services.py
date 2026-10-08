from datetime import timedelta 
from fastapi import Request, HTTPException, status
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.db.models.login_attempt_state import LoginAttemptState
from app.db.models.password_reset_token import PasswordResetToken
from app.structure.schemas import StructureCreateModel, StructureResponse, StructureUpdateModel

from app.visiteur_session.schemas import VisiteurSessionCreateModel

from app.core.exceptions_metier import RaiseException
from app.db.models.type_structure import TypeStructure
from app.db.models.visiteur_session import VisiteurSession
from slugify import slugify
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4






class VisiteurSessionService:
    async def get_all_visiteur_sessions(
        self,
        session: AsyncSession
    ) -> list[VisiteurSession]:

        statement = (
            select(VisiteurSession)
            .where(
                VisiteurSession.is_active.is_(True)
            )
            .order_by(
                desc(VisiteurSession.adresse_ip)
            )
        )

        result = await session.exec(statement)
        return result.all()


    async def create_visiteur_session(
        self,
        request: Request,
        session: AsyncSession,
        visiteur_data_data: VisiteurSessionCreateModel,
    ):

        adresse_ip=self.get_client_ip(request)

        # Créer le visiteur_session
        visiteur_session = VisiteurSession(
            uid=uuid4(),
            session_uid=visiteur_data_data.adresse_ip,
            adresse_ip=adresse_ip,
            user_agent=visiteur_data_data.user_agent,
            cree_le=datetime.now(),
            derniere_activite_le=datetime.now(),
            expire_le=None,
            is_active=True,
        )

        # Ajouter à la session
        session.add(visiteur_session)

        # Sauvegarder
        await session.commit()
        await session.refresh(visiteur_session)

        return visiteur_session

    
    async def get_visiteur_session(self, visiteur_session_uid: UUID, session: AsyncSession):
        statement = (
            select(VisiteurSession)
            .where(VisiteurSession.uid == visiteur_session_uid)
        )

        result = await session.exec(statement)
        structure = result.first()
        return structure

    
    
    async def get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get(
            "x-forwarded-for"
        )

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")

        if real_ip:
            return real_ip.strip()

        if request.client:
            return request.client.host

        return "0.0.0.0"







