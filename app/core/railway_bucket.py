# app/storage/railway_bucket_service.py

import secrets
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


class RailwayBucketService:

    TAILLE_MAXIMALE_IMAGE = 5 * 1024 * 1024   # 5 Mo
    TAILLE_MAXIMALE_PDF = 20 * 1024 * 1024    # 20 Mo

    TYPES_FICHIERS_AUTORISES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "application/pdf": ".pdf",
    }

    def __init__(self) -> None:
        self.bucket = settings.RAILWAY_BUCKET_NAME

        self.client = boto3.client(
            "s3",
            endpoint_url=settings.RAILWAY_ENDPOINT_URL,
            aws_access_key_id=settings.RAILWAY_ACCESS_KEY_ID,
            aws_secret_access_key=settings.RAILWAY_SECRET_ACCESS_KEY,
            region_name=settings.RAILWAY_REGION,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"},
            ),
        )

    def creer_cle_fichier(
        self,
        nom_fichier: str | None,
        dossier: str,
        content_type: str,
    ) -> str:
        extension = self.TYPES_FICHIERS_AUTORISES[content_type]

        if nom_fichier:
            extension_originale = Path(nom_fichier).suffix.lower()

            extensions_valides = {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
                ".gif",
                ".pdf",
            }

            if extension_originale in extensions_valides:
                extension = (
                    ".jpg"
                    if extension_originale == ".jpeg"
                    else extension_originale
                )

        nom_unique = (
            f"{uuid4().hex}-"
            f"{secrets.token_hex(4)}"
            f"{extension}"
        )

        dossier_normalise = dossier.strip("/")

        return f"{dossier_normalise}/{nom_unique}"
    

    
    def verifier_fichier(self, fichier: UploadFile) -> int:
        content_type = fichier.content_type or ""

        if content_type not in self.TYPES_FICHIERS_AUTORISES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    "Formats autorisés : "
                    "JPEG, PNG, WebP, GIF et PDF."
                ),
            )

        fichier.file.seek(0, 2)
        taille = fichier.file.tell()
        fichier.file.seek(0)

        if taille == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le fichier envoyé est vide.",
            )

        taille_maximale = (
            self.TAILLE_MAXIMALE_PDF
            if content_type == "application/pdf"
            else self.TAILLE_MAXIMALE_IMAGE
        )

        if taille > taille_maximale:
            taille_maximale_mo = taille_maximale // (1024 * 1024)

            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"La taille du fichier ne doit pas dépasser "
                    f"{taille_maximale_mo} Mo."
                ),
            )

        return taille
    

    def envoyer_fichier(
        self,
        fichier: UploadFile,
        dossier: str = "fichiers",
    ) -> str:
        self.verifier_fichier(fichier)

        content_type = fichier.content_type or ""

        object_key = self.creer_cle_fichier(
            nom_fichier=fichier.filename,
            dossier=dossier,
            content_type=content_type,
        )

        try:
            fichier.file.seek(0)

            self.client.upload_fileobj(
                Fileobj=fichier.file,
                Bucket=self.bucket,
                Key=object_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "CacheControl": "private, max-age=3600",
                },
            )

        except (BotoCoreError, ClientError) as exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de l’envoi du fichier.",
            ) from exception

        return object_key
    


    def generer_url_signee(
        self,
        object_key: str,
        expiration: int = 3600,
    ) -> str:
        try:
            return self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": object_key,
                },
                ExpiresIn=expiration,
            )

        except (BotoCoreError, ClientError) as exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Impossible de générer l’URL du fichier.",
            ) from exception

    def supprimer_fichier(self, object_key: str) -> None:
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=object_key,
            )

        except (BotoCoreError, ClientError) as exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la suppression du fichier.",
            ) from exception