from fastapi import APIRouter
from app.core.redis import redis_client

redis_router = APIRouter()


@redis_router.get("/redis-test")
async def redis_test():

    await redis_client.set(
        "test:formation",
        "Redis fonctionne pour 5 minutes",
        ex=300
    )

    valeur = await redis_client.get(
        "test:formation"
    )
    redis_client.set("nationalites:all", valeur, 3600)
    redis_client.get("nationalites:all")
    redis_client.delete("nationalites:all")
    return {
        "success": True,
        "value": valeur
    }

@redis_router.get("/recuperer-test")
async def recuperer_test():
    valeur = await redis_client.get(
        "test:formation"
    )

    ttl = await redis_client.ttl("test:formation")
    return {
        "success": True,
        "value": ttl
    }