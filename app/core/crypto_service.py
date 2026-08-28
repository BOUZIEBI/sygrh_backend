from pathlib import Path
import base64
import json
import os

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


BASE_DIR = Path(__file__).resolve().parents[2]

PRIVATE_KEY_PATH = BASE_DIR / "keys" / "private_key.pem"
PUBLIC_KEY_PATH = BASE_DIR / "keys" / "public_key.pem"


# ============================================================
# Chargement des clés RSA
# ============================================================

with open(PRIVATE_KEY_PATH, "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None
    )


with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(
        f.read()
    )


# ============================================================
# RSA-OAEP
# ============================================================

def decrypt_rsa(encrypted_key: str) -> bytes:

    encrypted_key_bytes = base64.b64decode(
        encrypted_key
    )

    aes_key = PRIVATE_KEY.decrypt(
        encrypted_key_bytes,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return aes_key


# ============================================================
# AES-GCM
# ============================================================

def decrypt_aes(
    encrypted_data: str,
    iv: str,
    aes_key: bytes
) -> dict:

    ciphertext = base64.b64decode(
        encrypted_data
    )

    iv_bytes = base64.b64decode(iv)

    aesgcm = AESGCM(aes_key)

    decrypted = aesgcm.decrypt(
        iv_bytes,
        ciphertext,
        None
    )

    return json.loads(
        decrypted.decode("utf-8")
    )