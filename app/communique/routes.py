from typing import List, Annotated
from fastapi import APIRouter, HTTPException, Request, Depends, status, File, Form, UploadFile
from uuid import UUID
from datetime import datetime
from starlette.concurrency import run_in_threadpool
from sqlmodel.ext.asyncio.session import AsyncSession
from app.communique.services import CommuniqueService
from app.core.railway_bucket import RailwayBucketService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.communique.schemas import CommuniqueCreateModel, CommuniqueUpdateModel, CommuniqueResponse, MessageResponse, MessageAllResponse
from app.core.exceptions_metier import RaiseException


communique_router = APIRouter()
communique_service = CommuniqueService()
railway_bucket_service=RailwayBucketService()

@communique_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[CommuniqueResponse])
async def get_all_communiques(
    session: AsyncSession = Depends(get_session),
)->dict:
    communiques = await communique_service.get_all_communiques(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True, 
        message="Communiqués trouvés avec succès",
        data=communiques
    )


@communique_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[CommuniqueResponse])
async def create_un_communique(
    request: Request,
    fichier: Annotated[
        UploadFile,
        File(description="Fichier de communique"),
    ],
    reference: Annotated[
        str,
        Form(min_length=3, max_length=255),
    ],
    titre: Annotated[
        str,
        Form(min_length=3, max_length=255),
    ],
    contenu: Annotated[
        str,
        Form(min_length=3, max_length=255),
    ],
    resume: Annotated[
        str,
        Form(min_length=3, max_length=255),
    ],
    statut: Annotated[
        str,
        Form(min_length=3, max_length=255),
    ],
    date_expiration: Annotated[
        str,
        Form(min_length=3, max_length=255),
    ],
        
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CREERCOMMUNIQUE"))
) -> dict:
    current_user_uid=current_user.uid
    
    # Envoi de l’image vers Railway Bucket
    object_key = await run_in_threadpool( 
        railway_bucket_service.envoyer_fichier,
        fichier,
        "communiques/images",
    )
    
    communique_data = CommuniqueCreateModel(
            titre=titre,
            contenu=contenu,
            resume=resume,
            object_key=object_key,
            statut=statut,
            date_expiration=date_expiration
    )
    
    try:
        nouvelle_phototheque = (
            await communique_service.create_communique(
                session=session,
                communique_data=communique_data,
                current_user_uid=current_user_uid,
            )
        )

    except Exception:
        # Si l’enlichissement:\/\/... échoue en base,
        # supprimer l’image déjà envoyée dans le bucket.
        try:
            nouvelle_phototheque = (
                await communique_service.create_communique(
                    session=session,
                    communique_data=communique_data,
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


@communique_router.get("/{communique_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[CommuniqueResponse])
async def get_un_communique(
    communique_uid: UUID,
    session: AsyncSession = Depends(get_session)
) -> dict:
    communique_trouve = await communique_service.get_communique(communique_uid, session)

    if communique_trouve is None:
            raise RaiseException(
                message="Communiqué non trouvé",
                code=404,
                errors={
                    "communique_uid": "Aucun communiqué ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Communiqué trouvé avec succès",
        data=communique_trouve
    )



@communique_router.patch("/{communique_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[CommuniqueResponse])
async def update_un_communique(
    communique_uid: UUID,
    fichier: Annotated[
        UploadFile | None,
        File(description="Nouveau fichier du communiqué"),
    ] = None,
    reference: Annotated[
        str | None,
        Form(min_length=3, max_length=100),
    ] = None,
    titre: Annotated[
        str | None,
        Form(min_length=3, max_length=255),
    ] = None,
    contenu: Annotated[
        str | None,
        Form(min_length=3),
    ] = None,
    resume: Annotated[
        str | None,
        Form(min_length=3, max_length=500),
    ] = None,
    statut: Annotated[
        str | None,
        Form(alias="statut"),
    ] = None,
    date_expiration: Annotated[
        datetime | None,
        Form(),
    ] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    _permission=Depends(
        require_permission("MODIFIERCOMMUNIQUE")
    ),
) -> MessageResponse[CommuniqueResponse]:

    communique_existant = (
        await communique_service.get_communique_by_uid(
            db=session,
            communique_uid=communique_uid,
        )
    )

    if communique_existant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Communiqué introuvable.",
        )

    ancienne_cle = communique_existant.fichier_key
    nouvelle_cle: str | None = None

    # Envoyer le nouveau fichier uniquement s’il est fourni.
    if fichier is not None:
        nouvelle_cle = await run_in_threadpool(
            railway_bucket_service.envoyer_fichier,
            fichier,
            "communiques/fichiers",
        )

    donnees_modification: dict = {}

    if reference is not None:
        donnees_modification["reference"] = reference

    if titre is not None:
        donnees_modification["titre"] = titre

    if contenu is not None:
        donnees_modification["contenu"] = contenu

    if resume is not None:
        donnees_modification["resume"] = resume

    if statut is not None:
        donnees_modification["statut"] = statut

    if date_expiration is not None:
        donnees_modification["date_expiration"] = (
            date_expiration
        )

    if nouvelle_cle is not None:
        donnees_modification["fichier_key"] = nouvelle_cle

    if not donnees_modification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à modifier.",
        )

    communique_data = CommuniqueUpdateModel(
        **donnees_modification
    )

    try:
        communique_modifie = (
            await communique_service.update_communique(
                session=session,
                communique=communique_existant,
                communique_data=communique_data,
                current_user_uid=current_user.uid,
            )
        )

    except Exception:
        # L’enregistrement en base a échoué :
        # supprimer le nouveau fichier du Bucket.
        if nouvelle_cle is not None:
            try:
                await run_in_threadpool(
                    railway_bucket_service.supprimer_fichier,
                    nouvelle_cle,
                )
            except Exception:
                pass

        raise

    # La modification a réussi :
    # supprimer l’ancien fichier remplacé.
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
            # Ne pas annuler une modification réussie uniquement
            # parce que l’ancien fichier n’a pas pu être supprimé.
            pass

    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Communiqué modifié avec succès.",
        data=communique_modifie,
    )    


@communique_router.delete(
    "/{communique_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[CommuniqueResponse]
)
async def delete_communique(
    communique_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERCOMMUNIQUE"))
)->dict:
    communique_to_delete = await communique_service.delete_communique(communique_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Communiqué supprimé avec succès",
        data=communique_to_delete
    )

@communique_router.get(
    "/restaurer/{communique_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[CommuniqueResponse]
)
async def restore_communique(
    communique_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERCOMMUNIQUE"))
)->dict:
    communique_to_restore = await communique_service.restore_communique(communique_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Communiqué restauré avec succès",
        data=communique_to_restore
    )
 



