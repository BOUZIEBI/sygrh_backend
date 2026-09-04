from typing import List
from typing import List, Annotated
from uuid import UUID
from starlette.concurrency import run_in_threadpool
from fastapi import APIRouter, HTTPException, Request, Depends, status, File, Form, UploadFile
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.nosservices.services import NosservicesService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.nosservices.schemas import NosservicesCreateModel, NosservicesUpdateModel, MessageResponse, MessageAllResponse, NosservicesResponse
from app.core.exceptions_metier import RaiseException
from app.core.railway_bucket import RailwayBucketService


service_router = APIRouter()
service_service = NosservicesService()
railway_bucket_service = RailwayBucketService()

@service_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[NosservicesResponse])
async def get_all_services(
    session: AsyncSession = Depends(get_session),
)->dict:
    services = await service_service.get_all_services(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Services trouvés avec succès",
        data=services
    )


@service_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[NosservicesResponse])
async def create_une_service(
    request: Request,
    fichier: Annotated[
        UploadFile,
        File(description="Image de couverture de la photothèque"),
    ],
    libelle: Annotated[
        str,
        Form(min_length=1, max_length=255),
    ],
    description_courte: Annotated[
        str | None,
        Form(),
    ] = None,
    description: Annotated[
        str | None,
        Form(),
    ] = None,
    ordre_affichage: Annotated[
        int | None,
        Form(),
    ] = None,
    statut: Annotated[
        str | None,
        Form(max_length=255),
    ] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    _permission=Depends(require_permission("CREERSERVICE"))
) -> dict:
    current_user_uid=current_user.uid
    
    # Envoi de l’image vers Railway Bucket
    object_key = await run_in_threadpool( 
        railway_bucket_service.envoyer_fichier,
        fichier,
        "services/images",
    )

    service_data = NosservicesCreateModel(
        libelle=libelle,
        description_courte=description_courte,
        description=description,
        object_key=object_key,
        statut=statut,
        ordre_affichage=ordre_affichage
    )

    try:
        nouveau_service = (
            await service_service.create_service(
                session=session,
                nosservice_data=service_data,
                current_user_uid=current_user_uid,
            )
        )

    except Exception:
        # Si l’enlichissement:\/\/... échoue en base,
        # supprimer l’image déjà envoyée dans le bucket.
        try:
            nouveau_service = (
                await service_service.create_service(
                    session=session,
                    service_data=service_data,
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
        message="Service créée avec succès.",
        data=nouveau_service
    )
    


@service_router.get("/{service_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[NosservicesResponse])
async def get_un_service(
    service_uid: UUID,
    session: AsyncSession = Depends(get_session)
) -> dict:
    service_trouve = await service_service.get_service(service_uid, session)

    if service_trouve is None:
            raise RaiseException(
                message="Service non trouvé",
                code=404,
                errors={
                    "service_uid": "Aucun service ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Service trouvé avec succès",
        data=service_trouve
    )



@service_router.patch("/{service_uid}",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[NosservicesResponse])
async def update_un_service(
    service_uid: UUID,
    request: Request,
    fichier: Annotated[
        UploadFile,
        File(description="Image de service"),
    ],
    libelle: Annotated[
        str,
        Form(min_length=1, max_length=255),
    ],
    description_courte: Annotated[
        str | None,
        Form(),
    ] = None,
    description: Annotated[
        str | None,
        Form(),
    ] = None,
    ordre_affichage: Annotated[
        int | None,
        Form(),
    ] = None,
    statut: Annotated[
        str | None,
        Form(max_length=255),
    ] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("MODIFIERSERVICE"))
) -> dict:
    current_user_uid=current_user.uid
    
    # Récupérer le service avant la modification.
    service_existant = (
        await service_service.get_service_by_id(
            session=session,
            service_uid=service_uid,
        )
    )

    if service_existant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service introuvable.",
        )

    ancienne_cle = service_existant.fichier_key
    nouvelle_cle: str | None = None

    # Envoyer une nouvelle image uniquement si elle est fournie.
    if fichier is not None:
        nouvelle_cle = await run_in_threadpool(
            railway_bucket_service.envoyer_fichier,
            fichier,
            "services/images",
        )
    print("------------ Image service -------------")
    print(nouvelle_cle)
    print("-----------------------------------------")
    # Ajouter uniquement les champs effectivement renseignés.
    donnees_modification: dict = {}

    if libelle is not None:
        donnees_modification["libelle"] = libelle
        
    if description_courte is not None:
        donnees_modification["description_courte"] = description_courte

    if description is not None:
        donnees_modification["description"] = description

    if statut is not None:
        donnees_modification["statut"] = statut

    if ordre_affichage is not None:
        donnees_modification["ordre_affichage"] = ordre_affichage

    if nouvelle_cle is not None:
        donnees_modification["fichier_key"] = nouvelle_cle

    service_data = NosservicesUpdateModel(
        **donnees_modification
    )

    try:
        service_modifie = (
            await service_service.update_service(
                session=session,
                service=service_existant,
                service_data=service_data,
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
        message="Service modifié avec succès.",
        data=service_modifie,
    )
    


@service_router.delete(
    "/{service_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[NosservicesResponse]
)
async def delete_service(
    service_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERSERVICE"))
)->dict:
    service_to_delete = await service_service.delete_service(service_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Service supprimé avec succès",
        data=service_to_delete
    )

@service_router.get(
    "/restaurer/{service_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[NosservicesResponse]
)
async def restore_service(
    service_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERSERVICE"))
)->dict:
    service_to_restore = await service_service.restore_service(service_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Service restauré avec succès",
        data=service_to_restore
    )
 



