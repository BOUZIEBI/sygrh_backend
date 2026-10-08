from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from jose.exceptions import (
    ExpiredSignatureError,
    JWTClaimsError,
    JWTError,
)
from jose import JWTError, jwt
TokenType = Literal["access", "refresh"]
from app.core.config import settings


ALGORITHM = settings.JWT_ALGORITHM


def _create_token(
    data: dict[str, Any],
    token_type: str,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(UTC)
    expire = now + expires_delta

    payload = data.copy()

    payload.update(
        {
            "iat": now,
            "exp": expire,
            "type": token_type,
        }
    )

    return jwt.encode(
        claims=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    lifetime = (
        expires_delta
        if expires_delta is not None
        else timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return _create_token(
        data=data,
        token_type="access",
        expires_delta=lifetime,
    )


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    lifetime = (
        expires_delta
        if expires_delta is not None
        else timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    return _create_token(
        data=data,
        token_type="refresh",
        expires_delta=lifetime,
    )



def _decode_token(
    token: str,
    expected_token_type: TokenType,
) -> dict[str, Any]:
    if not isinstance(token, str):
        raise JWTError(
            "Le token doit être une chaîne de caractères."
        )

    normalized_token = (
        token
        .removeprefix("Bearer ")
        .strip()
    )

    if not normalized_token:
        raise JWTError(
            "Le token est absent."
        )

    try:
        payload: dict[str, Any] = jwt.decode(
            normalized_token,
            settings.JWT_SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_sub": True,
                "require_exp": True,
                "require_iat": True,
                "require_sub": True,
            },
        )

    except ExpiredSignatureError as error:
        raise JWTError(
            "Le token a expiré."
        ) from error

    except JWTClaimsError as error:
        raise JWTError(
            "Les informations contenues dans "
            "le token sont invalides."
        ) from error

    except JWTError as error:
        raise JWTError(
            "Le token est invalide."
        ) from error

    token_type = payload.get("type")

    if not isinstance(token_type, str):
        raise JWTError(
            "Le token ne contient pas de type valide."
        )

    if token_type != expected_token_type:
        raise JWTError(
            "Type de token invalide : "
            f"'{expected_token_type}' attendu, "
            f"'{token_type}' reçu."
        )

    subject = payload.get("sub")

    if (
        not isinstance(subject, str)
        or not subject.strip()
    ):
        raise JWTError(
            "Le token ne contient pas un identifiant "
            "utilisateur valide."
        )

    return payload



def decode_access_token(
    token: str,
) -> dict[str, Any]:
    return _decode_token(
        token=token,
        expected_token_type="access",
    )


def decode_refresh_token(
    token: str,
) -> dict[str, Any]:
    return _decode_token(
        token=token,
        expected_token_type="refresh",
    )