from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.structure.services import StructureService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.structure.schemas import Structure, StructureCreateModel, StructureUpdateModel, StructureResponse, MessageResponse, MessageAllResponse
from app.core.exceptions_metier import RaiseException


structure_router = APIRouter()
structure_service = StructureService()

@structure_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[StructureResponse])
async def get_all_structures(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("VOIRLISTESTRUCTURE"))
)->dict:
    structures = await structure_service.get_all_structures(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Structures trouvées avec succès",
        data=structures
    )


@structure_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[StructureResponse])
async def create_une_structure(
    structure_data: StructureCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CREERSTRUCTURE"))
) -> dict:
    current_user_uid=current_user.uid
    nouvelle_structure = await structure_service.create_structure(session,structure_data,current_user_uid)
    
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structure créée avec succès",
        data=nouvelle_structure
    )

@structure_router.get("/{structure_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[StructureResponse])
async def get_une_structure(
    structure_uid: UUID,
    session: AsyncSession = Depends(get_session), 
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CONSULTERSTRUCTURE"))
) -> dict:
    current_user_uid=current_user.uid
    structure_trouve = await structure_service.get_structure(structure_uid,session)

    if structure_trouve is None:
            raise RaiseException(
                message="Structure non trouvée",
                code=404,
                errors={
                    "structure_uid": "Aucune structure ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Élève trouvé avec succès",
        data=structure_trouve
    )

@structure_router.patch("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[StructureResponse])
async def update_une_structure(
    structure_data: StructureUpdateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("MODIFIERSTRUCTURE"))
) -> dict:
    current_user_uid=current_user.uid
    structure_modifie = await structure_service.update_structure(session,structure_data,current_user_uid)   

    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structure modifiée avec succès",
        data=structure_modifie
    )


@structure_router.delete(
    "/{structure_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[StructureResponse]
)
async def delete_structure(
    structure_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERSTRUCTURE"))
)->dict:
    structure_to_delete = await structure_service.delete_structure(structure_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structuure supprimée avec succès",
        data=structure_to_delete
    )

@structure_router.get(
    "/restaurer/{structure_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[StructureResponse]
)
async def restore_structure(
    structure_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("MODIFIERSTRUCTURE"))
)->dict:
    structure_to_restore = await structure_service.restore_structure(structure_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structure restaurée avec succès",
        data=structure_to_restore
    )
 



