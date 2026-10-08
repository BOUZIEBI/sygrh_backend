# app/crypto/session_store.py

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4
from app.core.config import settings
from redis.exceptions import RedisError
from redis.asyncio import Redis


class SessionRedisStore:

    EXPIRATION_SECONDS = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _redis_key(
        session_uid: UUID | str,
    ) -> str:
        return f"crypto:session:{session_uid}"

    async def create(
        self,
        adresse_ip: str,
        user_agent: str | None,
        session_uid: UUID | str | None = None,
        public_key: str | None = None,
    ) -> UUID:
        session_uid = UUID(str(session_uid)) if session_uid else uuid4()

        session_data = {
            "session_uid": str(session_uid),
            "adresse_ip": adresse_ip,
            "client_public_key": public_key,
            "user_agent": user_agent,
            "created_at": datetime.now(
                UTC
            ).isoformat(),
        }

        await self.redis.set(
            name=self._redis_key(session_uid),
            value=json.dumps(session_data),
            ex=self.EXPIRATION_SECONDS,
        )

        return session_uid

    async def get(
        self,
        session_uid: UUID | str,
    ) -> dict | None:
        value = await self.redis.get(
            self._redis_key(session_uid)
        )

        if value is None:
            return None

        return json.loads(value)


    async def set_client_public_key(
        self,
        session_uid: UUID | str,
        public_key: str,
    ) -> bool:
        session_data = await self.get(session_uid)

        if session_data is None:
            return False

        session_data["client_public_key"] = public_key
        session_data["updated_at"] = datetime.now(
            UTC
        ).isoformat()

        await self.redis.set(
            name=self._redis_key(session_uid),
            value=json.dumps(session_data),
            ex=self.EXPIRATION_SECONDS,
        )

        return True

    async def get_client_public_key(
        self,
        session_uid: UUID | str,
    ) -> str | None:
        session_data = await self.get(session_uid)

        if session_data is None:
            return None

        public_key = session_data.get("client_public_key")
        if not isinstance(public_key, str) or not public_key.strip():
            return None

        return public_key.strip()
    
    
    async def get_session_redis_id(
        self,
        session_uid: UUID | str,
    ) -> str | None:
        """
        Recherche une session cryptographique dans Redis.

        Retourne le session_uid si la session existe,
        sinon retourne None.
        """

        try:
            parsed_session_uid = UUID(
                str(session_uid)
            )
        except (ValueError, TypeError, AttributeError):
            return None

        redis_key = self._redis_key(
            parsed_session_uid
        )

        try:
            session_exists = await self.redis.exists(
                redis_key
            )
        except RedisError as error:
            raise RuntimeError(
                "Impossible de consulter la session Redis."
            ) from error

        if not session_exists:
            return None

        return str(parsed_session_uid)
    
    

    async def refresh(
        self,
        session_uid: UUID | str,
    ) -> bool:
        return bool(
            await self.redis.expire(
                self._redis_key(session_uid),
                self.EXPIRATION_SECONDS,
            )
        )

    async def delete(
        self,
        session_uid: UUID | str,
    ) -> None:
        await self.redis.delete(
            self._redis_key(session_uid)
        )
