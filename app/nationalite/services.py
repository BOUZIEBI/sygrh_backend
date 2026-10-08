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
from app.nationalite.schemas import NationaliteCreateModel, NationaliteResponse, NationaliteUpdateModel
from app.core.exceptions_metier import RaiseException
from app.db.models.nationalite import Nationalite
from app.db.models.nationalite import Nationalite
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional

from app.core.redis import redis_client
from app.crypto.schemas import EncryptedResponse
from app.crypto.services import encrypt_response_for_react
from app.crypto.session_redis_store import SessionRedisStore

crypto_session_store = SessionRedisStore(redis_client)



class NationaliteService:
    async def get_all_nationalites(
        self,
        session: AsyncSession
    ) -> list[Nationalite]:

        statement = (
            select(Nationalite).order_by(Nationalite.libelle.asc())
        )

        result = await session.exec(statement)
        return result.all()
    

    async def get_nationalite(self, nationalite_uid: UUID, session: AsyncSession):
        statement = (
            select(Nationalite)
            .where(Nationalite.uid == nationalite_uid)
        )

        result = await session.exec(statement)
        nationalite = result.first()
        return nationalite
      

    async def get_nationalite_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Nationalite]:
        statement = select(Nationalite).where(Nationalite.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_nationalite_by_id(
        self,
        db: AsyncSession,
        nationalite_uid: UUID
    ) -> Optional[Nationalite]:
        statement = select(Nationalite).where(Nationalite.uid == nationalite_uid)
        result = await db.exec(statement)
        return result.first()
    
    
    async def encrypt_nationalite_response(
            self,
            data: object,
            crypto_session_id: str,
        ) -> dict[str, str]:
            
            try:
                session_uid = UUID(crypto_session_id)
            except (TypeError, ValueError) as error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_CRYPTO_SESSION",
                        "message": "L'identifiant de session cryptographique est invalide.",
                    },
                ) from error
        
            client_public_key = await crypto_session_store.get_client_public_key(
                session_uid
            )
                    
            if client_public_key is None:
                raise HTTPException(
                    status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                    detail={
                        "code": "CLIENT_PUBLIC_KEY_REQUIRED",
                        "message": (
                            "La clé publique RSA de React est absente "
                            "ou la session cryptographique a expiré."
                        ),
                    },
                )
        
            try:
                
                data_encrypted=encrypt_response_for_react(
                    data=data,
                    client_public_key_pem=client_public_key,
                )
            
                return data_encrypted
            except ValueError as error:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": "RESPONSE_ENCRYPTION_FAILED",
                        "message": str(error),
                    },
                ) from error
        





