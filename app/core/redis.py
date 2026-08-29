from redis.asyncio import Redis

from app.core.config import settings




if settings.REDIS_URL:
    print(
        "REDIS SCHEME :",
        settings.REDIS_URL.split("://")[0]
        if "://" in settings.REDIS_URL
        else "AUCUN"
    )
else:
    print("REDIS_URL est VIDE")


redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)