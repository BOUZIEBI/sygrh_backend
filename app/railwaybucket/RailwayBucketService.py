from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)
from fastapi import UploadFile

from app.core.config import settings


class RailwayBucketService:
    MAX_FILE_SIZE = 5 * 1024 * 1024

    ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "application/pdf",
    }

    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=(
                settings.BUCKET_ENDPOINT
            ),
            aws_access_key_id=(
                settings.BUCKET_ACCESS_KEY_ID
            ),
            aws_secret_access_key=(
                settings.BUCKET_SECRET_ACCESS_KEY
            ),
            region_name=(
                settings.BUCKET_REGION
            ),
            config=Config(
                signature_version="s3v4",
            ),
        )

        self.bucket_name = (
            settings.BUCKET_NAME
        )


    async def upload_file(
        self,
        fichier: UploadFile,
        dossier: str,
    ) -> str:
        if fichier.content_type not in (
            self.ALLOWED_CONTENT_TYPES
        ):
            raise ValueError(
                "Le type de fichier n’est pas autorisé."
            )

        contenu = await fichier.read()

        if not contenu:
            raise ValueError(
                "Le fichier est vide."
            )

        if len(contenu) > self.MAX_FILE_SIZE:
            raise ValueError(
                "Le fichier dépasse 5 Mo."
            )

        extension = Path(
            fichier.filename or ""
        ).suffix.lower()

        fichier_key = (
            f"{dossier}/{uuid4()}{extension}"
        )

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=fichier_key,
                Body=contenu,
                ContentType=(
                    fichier.content_type
                    or "application/octet-stream"
                ),
            )
        except (
            BotoCoreError,
            ClientError,
        ) as error:
            raise RuntimeError(
                "Impossible d’envoyer le fichier "
                "vers Railway Bucket."
            ) from error
        finally:
            await fichier.close()

        return fichier_key

    def generate_presigned_url(
        self,
        fichier_key: str,
        expiration: int = 3600,
    ) -> str:
        try:
            return self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": fichier_key,
                },
                ExpiresIn=expiration,
            )
        except (
            BotoCoreError,
            ClientError,
        ) as error:
            raise RuntimeError(
                "Impossible de générer l’URL "
                "temporaire du fichier."
            ) from error


railway_bucket_service = RailwayBucketService()