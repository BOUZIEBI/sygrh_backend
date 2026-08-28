from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.nationalite.services import NationaliteService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.nationalite.schemas import Nationalite, NationaliteCreateModel, NationaliteUpdateModel, NationaliteResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


nationalite_router = APIRouter()
nationalite_service = NationaliteService()

@nationalite_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[NationaliteResponse])
async def get_all_nationalites(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    #user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
   
    nationalites = await nationalite_service.get_all_nationalites(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Nationalités trouvées avec succès",
        data=nationalites
    )


@nationalite_router.get("/{nationalite_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[NationaliteResponse])
async def get_une_nationalite(
    nationalite_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    nationalite_trouve = await nationalite_service.get_nationalite(nationalite_uid,session)

    if nationalite_trouve is None:
            raise RaiseException(
                message="Nationalité non trouvée",
                code=404,
                errors={
                    "nationalite_uid": "Aucune nationalité ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Nationalité trouvée avec succès",
        data=nationalite_trouve
    )



 



