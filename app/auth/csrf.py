# app/core/csrf.py

import secrets
from hmac import compare_digest

from fastapi import (
    Cookie,
    Header,
    HTTPException,
    Response,
    status,
)

from app.core.config import settings


CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_MAX_AGE = 60 * 60  # 1 heure


def generate_csrf_token() -> str:
    """
    Génère un token CSRF aléatoire sécurisé.
    """
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


def set_csrf_cookie(
    response: Response,
    csrf_token: str,
) -> None:
    """
    Ajoute le token CSRF dans un cookie.

    httponly=False permet au frontend de lire le token
    et de l'envoyer dans l'en-tête X-CSRF-Token.
    """
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=CSRF_TOKEN_MAX_AGE,
        expires=CSRF_TOKEN_MAX_AGE,
        path="/",
        secure=settings.DEBUG ,
        httponly=False,
        samesite="none" if settings.is_production else "lax",
    )


def delete_csrf_cookie(response: Response) -> None:
    """
    Supprime le cookie CSRF.
    """
    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=settings.is_production,
        httponly=False,
        samesite="none" if settings.is_production else "lax",
    )


async def verify_csrf_token(
    csrf_cookie: str | None = Cookie(
        default=None,
        alias=CSRF_COOKIE_NAME,
    ),
    csrf_header: str | None = Header(
        default=None,
        alias=CSRF_HEADER_NAME,
    ),
) -> None:
    """
    Vérifie que le token présent dans le cookie correspond
    au token envoyé dans l'en-tête X-CSRF-Token.
    """
    if not csrf_cookie or not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CSRF_TOKEN_MISSING",
                "message": (
                    "Le token CSRF est absent du cookie "
                    "ou de l'en-tête X-CSRF-Token."
                ),
            },
        )
    
    if not compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CSRF_TOKEN_INVALID",
                "message": "Le token CSRF est invalide.",
            },
        )
