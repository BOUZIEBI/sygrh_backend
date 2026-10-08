from pydantic import BaseModel, ConfigDict, Field, field_validator

class PublicKeyResponse(BaseModel):
    public_key: str = Field(
        description="Clé publique RSA au format PEM",
        examples=[
            (
                "-----BEGIN PUBLIC KEY-----\n"
                "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...\n"
                "-----END PUBLIC KEY-----"
            )
        ],
    )
    
    
class EncryptedPayload(BaseModel):
    # Clé AES chiffrée avec la clé publique RSA FastAPI
    encrypted_key: str = Field(
        min_length=1,
    )

    # Données chiffrées avec AES-GCM
    encrypted_data: str = Field(
        min_length=1,
    )

    # IV utilisé par AES-GCM
    iv: str = Field(
        min_length=1,
    )


class PublicKeyData(BaseModel):
    public_key: str = Field(
        min_length=1,
    )
    
class EncryptedPayload(BaseModel):
    encrypted_key: str = Field(
        min_length=1
    )
    encrypted_data: str = Field(
        min_length=1
    )
    iv: str = Field(
        min_length=1
    )
    

class EncryptedResponse(BaseModel):
    encrypted_data: str = Field(
        description="Réponse JSON chiffrée par AES-256-GCM, tag inclus, en Base64.",
    )
    encrypted_key: str = Field(
        description="Clé AES chiffrée par RSA-OAEP SHA-256, en Base64.",
    )
    iv: str = Field(
        description="Vecteur d'initialisation AES-GCM de 12 octets, en Base64.",
    )
    
    
    
class PublicKeyRequest(BaseModel):
    public_key: str = Field(
        ...,
        min_length=100,
        max_length=10_000,
        description="Clé publique RSA du client au format PEM.",
        examples=[
            (
                "-----BEGIN PUBLIC KEY-----\n"
                "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...\n"
                "-----END PUBLIC KEY-----"
            )
        ],
    )

    @field_validator("public_key")
    @classmethod
    def validate_public_key_format(cls, value: str) -> str:
        public_key = value.strip()

        if not public_key.startswith(
            "-----BEGIN PUBLIC KEY-----"
        ):
            raise ValueError(
                "La clé doit commencer par "
                "'-----BEGIN PUBLIC KEY-----'."
            )

        if not public_key.endswith(
            "-----END PUBLIC KEY-----"
        ):
            raise ValueError(
                "La clé doit se terminer par "
                "'-----END PUBLIC KEY-----'."
            )

        return public_key

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "public_key": (
                    "-----BEGIN PUBLIC KEY-----\n"
                    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...\n"
                    "-----END PUBLIC KEY-----"
                )
            }
        },
    )
