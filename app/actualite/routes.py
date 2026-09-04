from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Depends, status, File, Form, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from app.actualite.services import ActualiteService
from app.db.main import get_session
from starlette.concurrency import run_in_threadpool
from app.core.railway_bucket import RailwayBucketService
from typing import List, Annotated
from app.auth.dependencies import get_current_active_user, require_permission
from app.actualite.schemas import ActualiteCreateModel, ActualiteUpdateModel, ActualiteResponse, MessageResponse, MessageAllResponse
from app.core.exceptions_metier import RaiseException


actualite_router = APIRouter()
actualite_service = ActualiteService()
railway_bucket_service=RailwayBucketService()

@actualite_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[ActualiteResponse])
async def get_all_actualites(
    session: AsyncSession = Depends(get_session),
)->dict:
    actualites = await actualite_service.get_all_actualites(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Actualités trouvées avec succès",
        data=actualites
    )


@actualite_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[ActualiteResponse])
async def create_une_actualite(
    request: Request,
    fichier: Annotated[UploadFile,File(description="Fichier de actualite"),],
    titre: Annotated[str,Form(min_length=3, max_length=255),],
    contenu: Annotated[str,Form(min_length=3, max_length=255),],
    resume: Annotated[str,Form(min_length=3, max_length=255),],
    statut: Annotated[str,Form(min_length=3, max_length=255),],
    est_a_la_une: Annotated[bool,Form(),],
    date_publication: Annotated[str,Form(min_length=3, max_length=255),],
    categorie_uid: Annotated[UUID | None,Form(),] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    _permission=Depends(require_permission("CREERACTUALITE"))
) -> dict:
    current_user_uid=current_user.uid
    
    # Envoi de l’image vers Railway Bucket
    object_key = await run_in_threadpool( 
        railway_bucket_service.envoyer_fichier,
        fichier,
        "actualites/images",
    )
    
    actualite_data = ActualiteCreateModel(
        titre=titre,
        contenu=contenu,
        resume=resume,
        object_key=object_key,
        statut=statut,
        est_a_la_une=est_a_la_une,
        categorie_uid=categorie_uid,
        date_publication=date_publication
    )
    
    try:
        nouvelle_actualite = (
            await actualite_service.create_actualite(
                session=session,
                actualite_data=actualite_data,
                current_user_uid=current_user_uid,
            )
        )

    except Exception:
        # Si l’enlichissement:\/\/... échoue en base,
        # supprimer l’image déjà envoyée dans le bucket.
        try:
            nouvelle_actualite = (
                await actualite_service.create_actualite(
                    session=session,
                    actualite_data=actualite_data,
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
        message="Actualite créée avec succès.",
        data=nouvelle_actualite,
    )


@actualite_router.get("/{actualite_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[ActualiteResponse])
async def get_une_actualite(
    actualite_uid: UUID,
    session: AsyncSession = Depends(get_session)
) -> dict:
    actualite_trouve = await actualite_service.get_actualite(actualite_uid, session)

    if actualite_trouve is None:
            raise RaiseException(
                message="Actualité non trouvée",
                code=404,
                errors={
                    "actualite_uid": "Aucune actualité ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Actualité trouvée avec succès",
        data=actualite_trouve
    )



@actualite_router.patch("/{actualite_uid}",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[ActualiteResponse])
async def update_une_actualite(
    actualite_uid: UUID,
    request: Request,
    fichier: Annotated[UploadFile,File(description="Fichier de communique"),],
    titre: Annotated[str,Form(min_length=3, max_length=255),],
    contenu: Annotated[str,Form(min_length=3, max_length=255),],
    resume: Annotated[str,Form(min_length=3, max_length=255),],
    statut: Annotated[str,Form(min_length=3, max_length=255),],
    est_a_la_une: Annotated[bool,Form(),],
    date_publication: Annotated[str,Form(min_length=3, max_length=255),],
    categorie_uid: Annotated[UUID | None,Form(),] = None,
    
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("MODIFIERACTUALITE"))
) -> dict:
    current_user_uid=current_user.uid
    
    actualite_existante = (
        await actualite_service.get_actualite_by_uid(
            db=session,
            actualite_uid=actualite_uid,
        )
    )

    if actualite_existante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actualité introuvable.",
        )

    ancienne_cle = actualite_existante.fichier_key
    nouvelle_cle: str | None = None

    # Envoyer le nouveau fichier uniquement s’il est fourni.
    if fichier is not None:
        nouvelle_cle = await run_in_threadpool(
            railway_bucket_service.envoyer_fichier,
            fichier,
            "communiques/fichiers",
        )

    donnees_modification: dict = {}

    if categorie_uid is not None:
        donnees_modification["categorie_uid"] = categorie_uid

    if titre is not None:
        donnees_modification["titre"] = titre

    if contenu is not None:
        donnees_modification["contenu"] = contenu

    if resume is not None:
        donnees_modification["resume"] = resume

    if statut is not None:
        donnees_modification["statut"] = statut
        
    if est_a_la_une is not None:
            donnees_modification["est_a_la_une"] = est_a_la_une

    if date_publication is not None:
        donnees_modification["date_publication"] = (
            date_publication
        )

    if nouvelle_cle is not None:
        donnees_modification["fichier_key"] = nouvelle_cle

    if not donnees_modification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à modifier.",
        )

    actualite_data = ActualiteUpdateModel(
        **donnees_modification
    )

    try:
        actualite_modifie = (
            await actualite_service.update_actualite(
                session=session,
                actualite=actualite_existante,
                actualite_data=actualite_data,
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
        message="Actualité modifié avec succès.",
        data=actualite_modifie,
    )
    


@actualite_router.delete(
    "/{actualite_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[ActualiteResponse]
)
async def delete_actualite(
    actualite_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERACTUALITE"))
)->dict:
    actualite_to_delete = await actualite_service.delete_actualite(actualite_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Actualité supprimée avec succès",
        data=actualite_to_delete
    )

@actualite_router.get(
    "/restaurer/{actualite_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[ActualiteResponse]
)
async def restore_actualite(
    actualite_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERACTUALITE"))
)->dict:
    actualite_to_restore = await actualite_service.restore_actualite(actualite_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Actualité restaurée avec succès",
        data=actualite_to_restore
    )
 



