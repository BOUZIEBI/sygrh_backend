from pathlib import Path
import base64
import json
import os
from app.core.config import settings
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


BASE_DIR = Path(__file__).resolve().parents[2] 
PRIVATE_KEY_PATH = BASE_DIR / "keys" / "private_key.pem" 
PUBLIC_KEY_PATH = BASE_DIR / "keys" / "public_key.pem" 


if not settings.DEBUG: 
    # ================================================ 
    # # PRODUCTION → Railway 
    # # ================================================
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "") 
    PUBLIC_KEY = os.getenv("PUBLIC_KEY", "") 
    if not PRIVATE_KEY: 
        raise ValueError( "PRIVATE_KEY must be set in production." ) 
    if not PUBLIC_KEY: 
        raise ValueError( "PUBLIC_KEY must be set in production." )

    # Railway peut contenir \n sous forme de texte
    PRIVATE_KEY = PRIVATE_KEY.replace("\\n", "\n") 
    PUBLIC_KEY = PUBLIC_KEY.replace("\\n", "\n")

else: 
    # ================================================ 
    # # LOCAL → fichiers PEM 
    # # ================================================
    with open(PRIVATE_KEY_PATH, "rb") as f: 
        PRIVATE_KEY = f.read()
    with open(PUBLIC_KEY_PATH, "rb") as f: 
        PUBLIC_KEY = f.read()


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