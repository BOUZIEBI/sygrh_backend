from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from jose.exceptions import (
    ExpiredSignatureError,
    JWTClaimsError,
    JWTError,
)
from uuid import UUID
from jose import JWTError, jwt
TokenType = Literal["access", "refresh"]
from app.core.config import settings


ALGORITHM = settings.JWT_ALGORITHM


def _create_token(
    data: dict[str, Any],
    token_type: str,
    expires_delta: timedelta,
    expires_at: int | None = None,
) -> str:
    now = datetime.now(UTC)
    if expires_at is not None and expires_at <= int(now.timestamp()):
        raise ValueError("La date d’expiration du token est dépassée.")

    expire = now + expires_delta

    payload = data.copy()

    payload.update(
        {
            "iat": now,
            "exp": expires_at if expires_at is not None else expire,
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
    expires_at: int | None = None,
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
        expires_at=expires_at,
    )



def _decode_token(
    token: str,
    expected_token_type: TokenType,
) -> dict[str, Any]:
    if not isinstance(token, str):
        raise JWTError(
            "Le token doit être une chaîne de caractères."
        )

    normalized_token = token.strip()

    if normalized_token.lower().startswith("bearer "):
        normalized_token = normalized_token[7:].strip()

    if not normalized_token:
        raise JWTError("Le token est absent.")

    try:
        payload = jwt.decode(
            normalized_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
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

    except ExpiredSignatureError:
        # Conserver ce type d'exception permet aux routes
        # de distinguer un token expiré d'un token invalide.
        raise

    except JWTClaimsError as error:
        raise JWTError(
            "Les informations contenues dans le token "
            "sont invalides."
        ) from error

    except JWTError as error:
        raise JWTError(
            "Le token est invalide ou sa signature "
            "ne peut pas être vérifiée."
        ) from error

    if not isinstance(payload, dict):
        raise JWTError(
            "Le contenu du token est invalide."
        )

    token_type = payload.get("type")

    if token_type != expected_token_type:
        raise JWTError(
            f"Type de token invalide : "
            f"'{expected_token_type}' attendu."
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

    # Vérifier que l'identifiant utilisateur est un UUID.
    try:
        UUID(subject)
    except (ValueError, TypeError, AttributeError) as error:
        raise JWTError(
            "L'identifiant utilisateur du token "
            "n'est pas un UUID valide."
        ) from error

    # Vérifier la présence et le format du SID si ton
    # architecture impose un identifiant de session.
    session_id = payload.get("sid")

    if session_id is not None:
        try:
            UUID(session_id)
        except (ValueError, TypeError, AttributeError) as error:
            raise JWTError(
                "L'identifiant de session est invalide."
            ) from error

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