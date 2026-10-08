from fastapi import Header, Cookie, HTTPException, Response, Request, APIRouter, status, Depends
from uuid import uuid4
from uuid import UUID
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.main import get_session
from app.auth.csrf import verify_csrf_token
from app.crypto.key_store import public_key_store
from app.crypto.schemas import PublicKeyRequest, EncryptedPayload, PublicKeyData
from app.crypto.security import validate_rsa_public_key
from app.core.redis import redis_client
from app.crypto.session_redis_store import SessionRedisStore
from pydantic import ValidationError
from app.crypto.services import decrypt_client_payload
from app.auth.cookies import (
    CRYPTO_SESSION_COOKIE,
    set_crypto_session_cookie,
)



crypto_router = APIRouter()
session_redis_store = SessionRedisStore(
    redis=redis_client
)

    
    
@crypto_router.post(
    "/session",
    status_code=status.HTTP_201_CREATED,
)
async def initialize_crypto_session(
    request: Request,
):
    adresse_ip = (
        request.headers
        .get("x-forwarded-for", "")
        .split(",")[0]
        .strip()
    )

    if not adresse_ip and request.client:
        adresse_ip = request.client.host

    session_uid = await session_redis_store.create(
        adresse_ip=adresse_ip or "0.0.0.0",
        user_agent=request.headers.get(
            "user-agent"
        ),
    )

    return {
        "code": 201,
        "success": True,
        "message": (
            "Session cryptographique initialisée."
        ),
        "data": {
            "session_uid": str(session_uid),
            "expires_in": 15 * 60,
        },
    }
    


@crypto_router.post(
    "/public-key",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf_token)],
)
async def register_public_key(
    request: Request,
    payload: EncryptedPayload,  
    crypto_session_id: Annotated[
        str | None,
        Header(alias="X-Crypto-Session-ID"),
    ] = None,
    csrf_token: Annotated[
        str | None,
        Cookie(alias="csrf_token"),
    ] = None,
):
    #  Vérifier l’existence de l’identifiant de session
    session_redis_id=await session_redis_store.get_session_redis_id(crypto_session_id)
    
    if not crypto_session_id:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "CRYPTO_SESSION_REQUIRED",
                "message": (
                    "La session cryptographique doit "
                    "d’abord être initialisée."
                ),
            },
        )

    try:
        header_session_uid = UUID(
            crypto_session_id.strip()
        )
    except (
        ValueError,
        TypeError,
        AttributeError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CRYPTO_SESSION",
                "message": (
                    "L’identifiant de session "
                    "cryptographique est invalide."
                ),
            },
        ) from error
        
    # Récupérer l’identifiant enregistré dans Redis
    try:
        session_redis_id = (
            await session_redis_store
            .get_session_redis_id(
                header_session_uid
            )
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "REDIS_UNAVAILABLE",
                "message": (
                    "Impossible de vérifier la session "
                    "cryptographique."
                ),
            },
        ) from error
        
    
    # La session n’existe pas ou a expiré
    if session_redis_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CRYPTO_SESSION_NOT_FOUND",
                "message": (
                    "La session cryptographique est "
                    "introuvable ou a expiré."
                ),
            },
        )
        
        
    # Valider l’identifiant provenant de Redis
    try:
        redis_session_uid = UUID(
            str(session_redis_id)
        )
    except (
        ValueError,
        TypeError,
        AttributeError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INVALID_REDIS_SESSION",
                "message": (
                    "La session enregistrée dans Redis "
                    "est invalide."
                ),
            },
        ) from error
        
        
    # Comparer les deux UUID
    """
    if header_session_uid != redis_session_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CRYPTO_SESSION_MISMATCH",
                "message": (
                    "La session envoyée ne correspond pas "
                    "à la session enregistrée."
                ),
            },
        )
    """
    
    # Valider l’identifiant provenant de Redis
    try:
        redis_session_uid = UUID(
            str(session_redis_id)
        )
    except (
        ValueError,
        TypeError,
        AttributeError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INVALID_REDIS_SESSION",
                "message": (
                    "La session enregistrée dans Redis "
                    "est invalide."
                ),
            },
        ) from error


    #  Vérifier que l’identifiant est un UUID
    try:
        session_uid = UUID(
            crypto_session_id.strip()
        )
    except (ValueError, TypeError, AttributeError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CRYPTO_SESSION",
                "message": (
                    "L’identifiant de la session "
                    "cryptographique est invalide."
                ),
            },
        ) from error

    #  Déchiffrer le payload envoyé par React
    try:
        decrypted_payload = decrypt_client_payload(
            payload
        )
        
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "PAYLOAD_DECRYPTION_FAILED",
                "message": str(error),
            },
        ) from error
    except RuntimeError as error:
        # Problème de configuration de la clé privée FastAPI
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "RSA_PRIVATE_KEY_ERROR",
                "message": (
                    "La configuration cryptographique "
                    "du serveur est invalide."
                ),
            },
        ) from error

    # decrypted_payload doit maintenant contenir :
    # {
    #     "public_key": "-----BEGIN PUBLIC KEY-----..."
    # }

    # 4. Valider les données déchiffrées avec Pydantic
    try:
        public_key_data = PublicKeyData.model_validate(
            decrypted_payload
        )
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_PUBLIC_KEY_PAYLOAD",
                "message": (
                    "Le contenu déchiffré ne contient pas "
                    "une clé publique valide."
                ),
                "errors": error.errors(),
            },
        ) from error

    client_public_key = (
        public_key_data.public_key.strip()
    )

    #  Vérifier que la valeur est réellement une clé RSA
    try:
        validate_rsa_public_key(
            client_public_key
        )
    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_RSA_PUBLIC_KEY",
                "message": str(error),
            },
        ) from error

    #  Enregistrer la clé publique React dans Redis
    public_key_registered = (
        await session_redis_store.set_client_public_key(
            session_uid=session_uid,
            public_key=client_public_key,
        )
    )

    if not public_key_registered:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "CRYPTO_SESSION_REQUIRED",
                "message": (
                    "La session cryptographique est "
                    "introuvable ou inexistant."
                ),
            },
        )

    #  Réponse
    return {
        "code": status.HTTP_201_CREATED,
        "success": True,
        "message": "Clé publique RSA enregistrée.",
        "data": {
            "session_uid": str(session_uid),
            "expires_in": (
                session_redis_store
                .EXPIRATION_SECONDS
            ),
        },
    }
    


    
