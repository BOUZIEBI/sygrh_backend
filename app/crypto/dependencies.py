from uuid import UUID

from fastapi import Cookie, HTTPException, status

from app.auth.cookies import CRYPTO_SESSION_COOKIE


async def get_crypto_session_uid(
    crypto_session_id: str | None = Cookie(
        default=None,
        alias=CRYPTO_SESSION_COOKIE,
    ),
) -> UUID:
    if not crypto_session_id:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "CRYPTO_SESSION_REQUIRED",
                "message": (
                    "La session cryptographique doit "
                    "d'abord être initialisée."
                ),
            },
        )

    try:
        return UUID(crypto_session_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CRYPTO_SESSION",
                "message": (
                    "La session cryptographique est invalide."
                ),
            },
        ) from error