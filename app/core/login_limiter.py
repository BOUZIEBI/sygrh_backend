import redis.asyncio as redis

from app.core.config import settings


class LoginLimiter:

    MAX_ATTEMPTS = 5
    BLOCK_SECONDS = 900  # 15 minutes

    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    async def is_blocked(self, identifier: str) -> tuple[bool, int]:
        """
        Vérifie si un utilisateur est actuellement bloqué.

        identifier peut être :
        email + IP
        """

        block_key = f"login:block:{identifier}"

        ttl = await self.redis.ttl(block_key)

        if ttl > 0:
            return True, ttl

        return False, 0

    async def register_failed_attempt(
        self,
        identifier: str
    ) -> int:
        """
        Enregistre une tentative de connexion échouée.
        """

        attempt_key = f"login:attempts:{identifier}"
        block_key = f"login:block:{identifier}"

        attempts = await self.redis.incr(attempt_key)

        # Première tentative
        if attempts == 1:
            await self.redis.expire(
                attempt_key,
                self.BLOCK_SECONDS
            )

        # Limite atteinte
        if attempts >= self.MAX_ATTEMPTS:

            await self.redis.set(
                block_key,
                "1",
                ex=self.BLOCK_SECONDS
            )

        return attempts

    async def reset(self, identifier: str):
        """
        Réinitialise les tentatives après
        une connexion réussie.
        """

        await self.redis.delete(
            f"login:attempts:{identifier}",
            f"login:block:{identifier}"
        )

    async def get_attempts(self, identifier: str) -> int:
        """
        Retourne le nombre de tentatives.
        """

        value = await self.redis.get(
            f"login:attempts:{identifier}"
        )

        return int(value) if value else 0

    async def close(self):
        await self.redis.aclose()


login_limiter = LoginLimiter()