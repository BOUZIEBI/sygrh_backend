# app/crypto/key_store.py

from datetime import UTC, datetime
from uuid import UUID
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
from app.core.redis import redis_client
from app.db.models.client_public_key import ClientPublicKey


class PublicKeyStore:
    REDIS_EXPIRATION_SECONDS = 15 * 60

    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _redis_key(
        session_uid: UUID | str,
    ) -> str:
        return f"crypto:public-key:{session_uid}"

    async def save(
        self,
        session: AsyncSession,
        #session_uid: UUID,
        public_key: str,
    ) -> None:
        if not public_key.strip():
            raise ValueError(
                "La clé publique RSA ne peut pas être vide."
            )

        if settings.DEBUG:
            await self._save_in_redis(
                #session_uid=session_uid,
                public_key=public_key,
            )
            return

        await self._save_in_database(
            session=session,
            #session_uid=session_uid,
            public_key=public_key,
        )

    async def get(
        self,
        session: AsyncSession,
        session_uid: UUID,
    ) -> str | None:
        if settings.is_production:
            return await self.redis.get(
                self._redis_key(session_uid)
            )

        statement = select(ClientPublicKey).where(
            ClientPublicKey.session_uid == session_uid,
            ClientPublicKey.is_active.is_(True),
        )

        result = await session.exec(statement)
        stored_key = result.first()

        if not stored_key:
            return None

        return stored_key.public_key

    async def delete(
        self,
        session: AsyncSession,
        session_uid: UUID,
    ) -> None:
        if settings.is_production:
            await self.redis.delete(
                self._redis_key(session_uid)
            )
            return

        statement = select(ClientPublicKey).where(
            ClientPublicKey.session_uid == session_uid
        )

        result = await session.exec(statement)
        stored_key = result.first()

        if not stored_key:
            return

        await session.delete(stored_key)
        await session.commit()

    async def _save_in_redis(
        self,
        #session_uid: UUID,
        public_key: str,
    ) -> None:
        await self.redis.setex(
            #name=self._redis_key(session_uid),
            time=self.REDIS_EXPIRATION_SECONDS,
            value=public_key.strip(),
        )

    @staticmethod
    async def _save_in_database(
        session: AsyncSession,
        #session_uid: UUID,
        public_key: str,
    ) -> None:
        statement = select(ClientPublicKey).where(
            ClientPublicKey.session_uid == session_uid
        )

        result = await session.exec(statement)
        stored_key = result.first()

        now = datetime.now(UTC)

        if stored_key:
            stored_key.public_key = public_key.strip()
            stored_key.modifie_le = now
            stored_key.is_active = True

        else:
            stored_key = ClientPublicKey(
                session_uid=session_uid,
                public_key=public_key.strip(),
                is_active=True,
            )

        session.add(stored_key)

        await session.commit()
        await session.refresh(stored_key)


public_key_store = PublicKeyStore(redis_client)