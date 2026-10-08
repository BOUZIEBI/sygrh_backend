from pathlib import Path
import base64
import json
import os
import binascii
from typing import Any
from fastapi.encoders import jsonable_encoder
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)
from app.crypto.schemas import EncryptedPayload
from functools import lru_cache
from app.core.config import settings
from app.crypto.schemas import PublicKeyData, EncryptedPayload




BASE_DIR = Path(__file__).resolve().parents[2]

PRIVATE_KEY_PATH = BASE_DIR / "keys" / "private_key.pem"
PUBLIC_KEY_PATH = BASE_DIR / "keys" / "public_key.pem"


def load_pem_from_environment(variable_name: str) -> bytes:
    value = os.getenv(variable_name)

    if not value:
        raise RuntimeError(
            f"La variable {variable_name} doit être définie en production."
        )

    return value.replace("\\n", "\n").encode("utf-8")


# ============================================================
# Lecture des clés PEM
# ============================================================

if settings.DEBUG:
    # Local : fichiers PEM
    PRIVATE_KEY_PEM = PRIVATE_KEY_PATH.read_bytes()
    PUBLIC_KEY_PEM = PUBLIC_KEY_PATH.read_bytes()

else:
    # Production Railway : variables d'environnement
    PRIVATE_KEY_PEM = load_pem_from_environment("PRIVATE_KEY")
    PUBLIC_KEY_PEM = load_pem_from_environment("PUBLIC_KEY")


# ============================================================
# Conversion PEM vers objets cryptographiques
# ============================================================

PRIVATE_KEY = serialization.load_pem_private_key(
    PRIVATE_KEY_PEM,
    password=None,
)

PUBLIC_KEY = serialization.load_pem_public_key(
    PUBLIC_KEY_PEM,
)


# ============================================================
# Base64
# ============================================================

def decode_base64(value: str, field_name: str) -> bytes:
    try:
        return base64.b64decode(
            value,
            validate=True,
        )
    except Exception as exc:
        raise ValueError(
            f"Le champ {field_name} n'est pas un Base64 valide."
        ) from exc


# ============================================================
# RSA-OAEP
# ============================================================

def decrypt_rsa(encrypted_key: str) -> bytes:
    encrypted_key_bytes = decode_base64(
        encrypted_key,
        "encrypted_key",
    )

    try:
        aes_key = PRIVATE_KEY.decrypt(
            encrypted_key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256(),
                ),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except ValueError as exc:
        raise ValueError(
            "Impossible de déchiffrer la clé AES."
        ) from exc

    if len(aes_key) != 32:
        raise ValueError(
            "La clé AES doit contenir 32 octets."
        )

    return aes_key


# ============================================================
# AES-256-GCM
# ============================================================

def decrypt_aes(
    encrypted_data: str,
    iv: str,
    aes_key: bytes,
) -> dict:
    """
    encrypted_data doit contenir :
        ciphertext + tag GCM

    Web Crypto retourne déjà ces deux parties concaténées.
    """

    ciphertext_with_tag = decode_base64(
        encrypted_data,
        "encrypted_data",
    )

    iv_bytes = decode_base64(
        iv,
        "iv",
    )

    if len(iv_bytes) != 12:
        raise ValueError(
            "L'IV AES-GCM doit contenir exactement 12 octets."
        )

    if len(ciphertext_with_tag) < 16:
        raise ValueError(
            "Les données chiffrées ne contiennent pas de tag GCM valide."
        )

    try:
        decrypted_data = AESGCM(aes_key).decrypt(
            iv_bytes,
            ciphertext_with_tag,
            None,
        )
    except InvalidTag as exc:
        raise ValueError(
            "Le tag AES-GCM est invalide ou les données ont été modifiées."
        ) from exc

    try:
        result = json.loads(
            decrypted_data.decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "Les données déchiffrées ne contiennent pas un JSON valide."
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "Les données déchiffrées doivent être un objet JSON."
        )

    return result

def generate_aes_key() -> bytes:
    """
    Génère une nouvelle clé AES-256.

    Retourne une clé de 32 octets.
    """
    return AESGCM.generate_key(
        bit_length=256
    )
    
    
def encrypt_response_with_aes_gcm(
    data: Any,
    aes_key: bytes,
) -> dict[str, str]:
    """
    Chiffre des données avec AES-256-GCM.

    Args:
        data:
            Données à chiffrer : dictionnaire,
            liste, modèle Pydantic, UUID, etc.

        aes_key:
            Clé AES-256 de 32 octets.

    Returns:
        encrypted_data:
            Données chiffrées avec le tag GCM,
            encodées en Base64.

        iv:
            Vecteur d'initialisation unique,
            encodé en Base64.
    """

    if len(aes_key) != 32:
        raise ValueError(
            "Une clé AES-256 doit contenir "
            "exactement 32 octets."
        )

    # Convertir UUID, datetime, Enum et
    # modèles Pydantic en données JSON
    json_compatible_data = jsonable_encoder(
        data
    )

    plaintext = json.dumps(
        json_compatible_data,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    # Générer un IV unique de 12 octets
    iv = os.urandom(12)

    aes_gcm = AESGCM(aes_key)

    # Le résultat contient :
    # ciphertext + tag d'authentification GCM
    encrypted_data = aes_gcm.encrypt(
        nonce=iv,
        data=plaintext,
        associated_data=None,
    )

    return {
        "encrypted_data": (
            base64.b64encode(
                encrypted_data
            ).decode("utf-8")
        ),
        "iv": (
            base64.b64encode(iv)
            .decode("utf-8")
        ),
    }
    
    
def encrypt_aes_key_with_rsa(
    aes_key: bytes,
    client_public_key_pem: str,
) -> str:
    """
    Chiffre une clé AES-256 avec la clé publique
    RSA de React.

    Args:
        aes_key:
            Clé AES-256 de 32 octets.

        client_public_key_pem:
            Clé publique RSA de React au
            format PEM.

    Returns:
        Clé AES chiffrée avec RSA-OAEP,
        encodée en Base64.
    """

    if len(aes_key) != 32:
        raise ValueError(
            "Une clé AES-256 doit contenir "
            "exactement 32 octets."
        )

    try:
        public_key = (
            serialization.load_pem_public_key(
                client_public_key_pem.encode(
                    "utf-8"
                )
            )
        )

    except (ValueError, TypeError) as error:
        raise ValueError(
            "La clé publique RSA de React "
            "est invalide."
        ) from error

    if not isinstance(
        public_key,
        rsa.RSAPublicKey,
    ):
        raise ValueError(
            "La clé fournie n’est pas une "
            "clé publique RSA."
        )

    if public_key.key_size < 2048:
        raise ValueError(
            "La clé RSA doit avoir une taille "
            "minimale de 2048 bits."
        )

    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return base64.b64encode(
        encrypted_aes_key
    ).decode("utf-8")
    
    
def encrypt_response_for_react(
    data: Any,
    client_public_key_pem: str,
) -> dict[str, str]:
    """
    Chiffre une réponse destinée à React.

    Étapes :
    1. Générer une nouvelle clé AES-256.
    2. Chiffrer les données avec AES-GCM.
    3. Chiffrer la clé AES avec la clé
       publique RSA de React.
    """

    # 1. Générer une nouvelle clé AES-256
    aes_key = generate_aes_key()

    # 2. Chiffrer les données avec AES-GCM
    encrypted_response = (
        encrypt_response_with_aes_gcm(
            data=data,
            aes_key=aes_key,
        )
    )

    # 3. Chiffrer la clé AES avec RSA
    encrypted_aes_key = (
        encrypt_aes_key_with_rsa(
            aes_key=aes_key,
            client_public_key_pem=(
                client_public_key_pem
            ),
        )
    )

    return {
        "encrypted_key": encrypted_aes_key,
        "encrypted_data": encrypted_response[
            "encrypted_data"
        ],
        "iv": encrypted_response["iv"],
    }
    
    
    
@lru_cache(maxsize=1)
def load_fastapi_private_key() -> rsa.RSAPrivateKey:
    """
    Développement :
        charge /app/keys/private_key.pem.

    Production Railway :
        charge RSA_PRIVATE_KEY_BASE64 depuis les variables Railway.
    """

    if settings.is_production :
        encoded_private_key = (
            settings.RSA_PRIVATE_KEY_BASE64
        )

        if not encoded_private_key:
            raise RuntimeError(
                "RSA_PRIVATE_KEY_BASE64 est absente "
                "des variables Railway."
            )

        try:
            normalized_key = (
                encoded_private_key
                .strip()
                .strip("\"'")
                .replace(" ", "")
                .replace("\n", "")
                .replace("\r", "")
            )

            private_key_pem = base64.b64decode(
                normalized_key,
                validate=True,
            )
        except (ValueError, TypeError, binascii.Error) as error:
            raise RuntimeError(
                "RSA_PRIVATE_KEY_BASE64 n’est pas "
                "correctement encodée."
            ) from error

    else:
        private_key_path = Path( PRIVATE_KEY_PATH )

        if not private_key_path.is_file():
            raise RuntimeError(
                "Clé privée RSA locale introuvable : "
                f"{private_key_path}"
            )

        try:
            private_key_pem = private_key_path.read_bytes()
        except OSError as error:
            raise RuntimeError(
                "Impossible de lire la clé privée RSA locale."
            ) from error

    try:
        private_key = (
            serialization.load_pem_private_key(
                private_key_pem,
                password=None,
            )
        )
    except (ValueError, TypeError) as error:
        raise RuntimeError(
            "La clé privée RSA FastAPI est invalide."
        ) from error

    if not isinstance(
        private_key,
        rsa.RSAPrivateKey,
    ):
        raise RuntimeError(
            "La clé privée chargée n’est pas une clé RSA."
        )

    return private_key



def decrypt_client_payload(
    payload: EncryptedPayload,
) -> dict[str, Any]:
    private_key = load_fastapi_private_key()

    # 1. Décoder les trois valeurs Base64
    try:
        encrypted_aes_key = base64.b64decode(
            payload.encrypted_key,
            validate=True,
        )

        encrypted_data = base64.b64decode(
            payload.encrypted_data,
            validate=True,
        )

        iv = base64.b64decode(
            payload.iv,
            validate=True,
        )
    except (
        ValueError,
        TypeError,
        binascii.Error,
    ) as error:
        raise ValueError(
            "Le payload contient une valeur Base64 invalide."
        ) from error

    # AES-GCM recommande un IV de 12 octets
    if len(iv) != 12:
        raise ValueError(
            "L’IV AES-GCM doit contenir exactement 12 octets."
        )

    # 2. Déchiffrer la clé AES avec la clé privée RSA FastAPI
    try:
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256(),
                ),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except ValueError as error:
        raise ValueError(
            "Impossible de déchiffrer la clé AES. "
            "Vérifiez que React utilise la clé publique "
            "correspondant à la clé privée FastAPI."
        ) from error

    # Une clé AES-256 doit faire 32 octets
    if len(aes_key) != 32:
        raise ValueError(
            "La clé obtenue n’est pas une clé AES-256."
        )

    # 3. Déchiffrer les données avec AES-GCM
    try:
        decrypted_bytes = AESGCM(
            aes_key
        ).decrypt(
            iv,
            encrypted_data,
            None,
        )
    except InvalidTag as error:
        raise ValueError(
            "Le payload AES-GCM est invalide, corrompu "
            "ou a été modifié."
        ) from error
    except ValueError as error:
        raise ValueError(
            "Impossible de déchiffrer les données AES-GCM."
        ) from error

    # 4. Convertir les octets déchiffrés en objet Python
    try:
        decrypted_payload = json.loads(
            decrypted_bytes.decode("utf-8")
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        raise ValueError(
            "Le contenu déchiffré n’est pas un JSON valide."
        ) from error

    if not isinstance(decrypted_payload, dict):
        raise ValueError(
            "Le contenu déchiffré doit être un objet JSON."
        )

    return decrypted_payload