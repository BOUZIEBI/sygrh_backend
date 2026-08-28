from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.statut.services import StatutService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.statut.schemas import StatutCreateModel, StatutUpdateModel, StatutResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


statut_router = APIRouter()
statut_service = StatutService()

@statut_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[StatutResponse])
async def get_all_statuts(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
)->dict:
   
    statuts = await statut_service.get_all_statuts(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Statuts trouvés avec succès",
        data=statuts
    )


@statut_router.get("/{statut_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[StatutResponse])
async def get_un_statut(
    statut_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    statut_trouve = await statut_service.get_statut(statut_uid,session)

    if statut_trouve is None:
            raise RaiseException(
                message="Statut non trouvé",
                code=404,
                errors={
                    "statut_uid": "Aucun statut ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Statut trouvé avec succès",
        data=statut_trouve
    )



 



