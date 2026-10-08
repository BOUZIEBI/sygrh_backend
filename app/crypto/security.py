from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import HTTPException, status


def validate_rsa_public_key(
    public_key_pem: str,
) -> RSAPublicKey:
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode("utf-8")
        )

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_PUBLIC_KEY",
                "message": "La clé publique RSA est invalide.",
            },
        ) from error

    if not isinstance(public_key, RSAPublicKey):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_KEY_TYPE",
                "message": (
                    "La clé fournie n'est pas une clé publique RSA."
                ),
            },
        )

    if public_key.key_size < 2048:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "RSA_KEY_TOO_SHORT",
                "message": (
                    "La clé RSA doit contenir au moins 2048 bits."
                ),
            },
        )

    return public_key