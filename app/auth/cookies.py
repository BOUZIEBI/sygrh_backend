# app/auth/cookies.py

from fastapi import Response

from app.core.config import settings


ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
CSRF_COOKIE = "csrf_token"
CRYPTO_SESSION_COOKIE = "crypto_session_id"


def set_access_token_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    
    
def set_crypto_session_cookie(
    response: Response,
    session_uid: str,
) -> None:
    
    response.set_cookie(
        key=CRYPTO_SESSION_COOKIE,
        value=session_uid,
        max_age=24 * 60 * 60,
        httponly=True,
        #secure=settings.COOKIE_SECURE,
        secure=True,
        #samesite=settings.COOKIE_SAMESITE,
        samesite="lax",
        path="/",
    )


def set_refresh_token_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        #secure=settings.COOKIE_SECURE,
        #samesite=settings.COOKIE_SAMESITE,
       
        secure=True,
        samesite="none",
        path="/api/v1/auth",
    )


def set_csrf_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=CSRF_COOKIE,
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )


def delete_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE,
        path="/",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

    response.delete_cookie(
        key=REFRESH_COOKIE,
        path="/api/v1/auth",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

    response.delete_cookie(
        key=CSRF_COOKIE,
        path="/",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    
