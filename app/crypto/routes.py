from fastapi import APIRouter
from cryptography.hazmat.primitives import serialization
from app.crypto.services import PUBLIC_KEY


crypto_router = APIRouter()


@crypto_router.get("/public-key")
async def get_public_key():

    public_key = PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return {
        "public_key": public_key
    }