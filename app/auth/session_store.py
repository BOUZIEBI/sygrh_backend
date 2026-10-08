# app/auth/session_store.py

import json
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from redis.asyncio import Redis


class AuthSessionStore:

    EXPIRATION_SECONDS = 8 * 60 * 60  # 8 heures

    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _redis_key(session_uid: UUID | str) -> str:
        return f"auth:session:{session_uid}"

    async def create(
        self,
        user_uid: UUID,
        adresse_ip: str,
        user_agent: str | None,
    ) -> tuple[UUID, datetime]:
        session_uid = uuid4()

        expire_le = (
            datetime.now(UTC)
            + timedelta(
                seconds=self.EXPIRATION_SECONDS
            )
        )

        session_data = {
            "session_uid": str(session_uid),
            "user_uid": str(user_uid),
            "adresse_ip": adresse_ip,
            "user_agent": user_agent,
            "cree_le": datetime.now(UTC).isoformat(),
            "expire_le": expire_le.isoformat(),
        }

        await self.redis.set(
            name=self._redis_key(session_uid),
            value=json.dumps(session_data),
            ex=self.EXPIRATION_SECONDS,
        )

        return session_uid, expire_le

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