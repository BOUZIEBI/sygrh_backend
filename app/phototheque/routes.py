from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Depends, status, File, Form, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from app.phototheque.services import PhotothequeService
from datetime import datetime, timezone
from starlette.concurrency import run_in_threadpool
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.phototheque.schemas import PhotothequeCreateModel, PhotothequeUpdateModel, PhotothequeResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException
from app.core.railway_bucket import RailwayBucketService


phototheque_router = APIRouter()
phototheque_service = PhotothequeService()
railway_bucket_service = RailwayBucketService()

@phototheque_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[PhotothequeResponse])
async def get_all_phototheques(
    session: AsyncSession = Depends(get_session),
)->dict:
    phototheques = await phototheque_service.get_all_phototheques(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Photothèques trouvées avec succès",
        data=phototheques
    )


@phototheque_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse[PhotothequeResponse],
)
async def create_une_phototheque(
    request: Request,
    fichier: Annotated[
        UploadFile,
        File(description="Image de couverture de la photothèque"),
    ],
    titre: Annotated[
        str,
        Form(min_length=3, max_length=255),
    ],
    description: Annotated[
        str | None,
        Form(),
    ] = None,
    lieu: Annotated[
        str | None,
        Form(max_length=255),
    ] = None,
    date_evenement: Annotated[
        datetime | None,
        Form(),
    ] = None,
    categorie_uid: Annotated[
        UUID | None,
        Form(),
    ] = None,
    statut: Annotated[
        str | None,
        Form(max_length=255),
    ] = None,

    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    _permission=Depends(
        require_permission("CREERPHOTOTHEQUE")
    ),
) -> MessageResponse[PhotothequeResponse]:

    current_user_uid = current_user.uid

    # Envoi de l’image vers Railway Bucket
    object_key = await run_in_threadpool( 
        railway_bucket_service.envoyer_fichier,
        fichier,
        "phototheques/images",
    )

    phototheque_data = PhotothequeCreateModel(
        titre=titre,
        description=description,
        lieu=lieu,
        date_evenement=date_evenement,
        object_key=object_key,
        categorie_uid=categorie_uid,
        statut=statut,
    )

    try:
        nouvelle_phototheque = (
            await phototheque_service.create_phototheque(
                session=session,
                phototheque_data=phototheque_data,
                current_user_uid=current_user_uid,
            )
        )

    except Exception:
        # Si l’enlichissement:\/\/... échoue en base,
        # supprimer l’image déjà envoyée dans le bucket.
        try:
            nouvelle_phototheque = (
                await phototheque_service.create_phototheque(
                    session=session,
                    phototheque_data=phototheque_data,
                    current_user_uid=current_user_uid,
                )
            )

        except Exception:
            # Si l’enlichissement:\/\/... échoue en base,
            # supprimer l’image déjà envoyée dans le bucket.
            try:
                await run_in_threadpool(
                    railway_bucket_service.supprimer_fichier,
                    object_key,
                )
            except Exception:
                pass

        raise

    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Photothèque créée avec succès.",
        data=nouvelle_phototheque,
    )




@phototheque_router.patch("/{phototheque_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[PhotothequeResponse])
async def update_une_phototheque(
    request: Request,
    phototheque_uid: UUID,
    fichier: Annotated[
        UploadFile | None,
        File(description="Nouvelle image de couverture"),
    ] = None,
    titre: Annotated[
        str | None,
        Form(min_length=3, max_length=255),
    ] = None,
    description: Annotated[str | None, Form()] = None,
    lieu: Annotated[
        str | None,
        Form(max_length=255),
    ] = None,
    date_evenement: Annotated[
        datetime | None,
        Form(),
    ] = None,
    categorie_uid: Annotated[
        UUID | None,
        Form(),
    ] = None,
    statut: Annotated[
        str | None,
        Form(alias="statut"),
    ] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    _permission=Depends(
        require_permission("MODIFIERPHOTOTHEQUE")
    ),
) -> MessageResponse[PhotothequeResponse]:

    # Récupérer la photothèque avant la modification.
    phototheque_existante = (
        await phototheque_service.get_phototheque_by_uid(
            session=session,
            phototheque_uid=phototheque_uid,
        )
    )

    if phototheque_existante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photothèque introuvable.",
        )

    ancienne_cle = phototheque_existante.fichier_key
    nouvelle_cle: str | None = None

    # Envoyer une nouvelle image uniquement si elle est fournie.
    if fichier is not None:
        nouvelle_cle = await run_in_threadpool(
            railway_bucket_service.envoyer_fichier,
            fichier,
            "phototheques/images",
        )

    # Ajouter uniquement les champs effectivement renseignés.
    donnees_modification: dict = {}

    if titre is not None:
        donnees_modification["titre"] = titre

    if description is not None:
        donnees_modification["description"] = description

    if lieu is not None:
        donnees_modification["lieu"] = lieu

    if date_evenement is not None:
        donnees_modification["date_evenement"] = date_evenement

    if categorie_uid is not None:
        donnees_modification["categorie_uid"] = categorie_uid

    if statut is not None:
        donnees_modification["statut"] = statut

    if nouvelle_cle is not None:
        donnees_modification["fichier_key"] = nouvelle_cle

    phototheque_data = PhotothequeUpdateModel(
        **donnees_modification
    )

    try:
        phototheque_modifiee = (
            await phototheque_service.update_phototheque(
                session=session,
                phototheque=phototheque_existante,
                phototheque_data=phototheque_data,
                current_user_uid=current_user.uid,
            )
        )

    except Exception:
        # La base de données n’a pas été modifiée :
        # supprimer uniquement le nouveau fichier.
        if nouvelle_cle is not None:
            try:
                await run_in_threadpool(
                    railway_bucket_service.supprimer_fichier,
                    nouvelle_cle,
                )
            except Exception:
                pass

        raise

    # La modification en base est terminée :
    # supprimer l’ancienne image remplacée.
    if (
        nouvelle_cle is not None
        and ancienne_cle is not None
        and ancienne_cle != nouvelle_cle
    ):
        try:
            await run_in_threadpool(
                railway_bucket_service.supprimer_fichier,
                ancienne_cle,
            )
        except Exception:
            # La modification reste valide même si la suppression
            # de l’ancien fichier échoue.
            pass

    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Photothèque modifiée avec succès.",
        data=phototheque_modifiee,
    )
    
    

@phototheque_router.delete(
    "/{phototheque_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[PhotothequeResponse]
)
async def delete_phototheque(
    phototheque_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERPHOTOTHEQUE"))
)->dict:
    phototheque_to_delete = await phototheque_service.delete_phototheque(phototheque_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Photothèque supprimée avec succès",
        data=phototheque_to_delete
    )

@phototheque_router.get(
    "/restaurer/{phototheque_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[PhotothequeResponse]
)
async def restore_phototheque(
    phototheque_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERPHOTOTHEQUE"))
)->dict:
    phototheque_to_restore = await phototheque_service.restore_phototheque(phototheque_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Photothèque restaurée avec succès",
        data=phototheque_to_restore
    )
 



