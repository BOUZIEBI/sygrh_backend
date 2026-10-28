from pwdlib import PasswordHash
import re

from secrets import compare_digest
from typing import Annotated
from fastapi import Header, HTTPException, status
from app.core.config import settings


password_hash = PasswordHash.recommended()



def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def validate_password_strength(password: str) -> bool:
    if len(password) < 6:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


async def verify_env_csrf_token(
    x_csrf_token: Annotated[
        str | None,
        Header(alias="X-CSRF-TOKEN"),
    ] = None,
) -> None:
    print(x_csrf_token)
    if not x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CSRF_TOKEN_MISSING",
                "message": "Le token CSRF est absent.",
            },
        )

    if not settings.X_CSRF_TOKEN:
        raise RuntimeError(
            "La variable X_CSRF_TOKEN n’est pas configurée."
        )

    if not compare_digest(
        x_csrf_token,
        settings.X_CSRF_TOKEN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INVALID_CSRF_TOKEN",
                "message": "Le token CSRF est invalide.",
            },
        )


