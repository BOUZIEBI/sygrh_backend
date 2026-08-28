from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.type_structure.services import TypestructureService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.type_structure.schemas import TypeStructure, TypeStructureCreateModel, TypeStructureUpdateModel, TypeStructureResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


typstructure_router = APIRouter()
typestructure_service =TypestructureService()

@typstructure_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[TypeStructureResponse])
async def get_all_typestructures(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    #user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
   
    typestructures = await typestructure_service.get_all_typestructures(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Types structure trouvés avec succès",
        data=typestructures
    )


@typstructure_router.get("/{typestructure_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[TypeStructureResponse])
async def get_un_typestructure(
    typestructure_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    typestructure_trouve = await typestructure_service.get_typestructure(typestructure_uid,session)

    if typestructure_trouve is None:
            raise RaiseException(
                message="Type de structure non trouvé",
                code=404,
                errors={
                    "typestructure_uid": "Aucun type de structure ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Type agent trouvé trouvé avec succès",
        data=typestructure_trouve
    )



 



