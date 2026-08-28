from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.emploi.services import EmploiService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.emploi.schemas import Emploi, EmploiCreateModel, EmploiUpdateModel, EmploiResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


emploi_router = APIRouter()
emploi_service = EmploiService()

@emploi_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[EmploiResponse])
async def get_all_emploi(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
)->dict:
   
    emplois = await emploi_service.get_all_emplois(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Emplois trouvés avec succès",
        data=emplois
    )


@emploi_router.get("/{emploi_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[EmploiResponse])
async def get_un_emploi(
    emploi_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    emploi_trouve = await emploi_service.get_fonction(emploi_uid,session)

    if emploi_trouve is None:
            raise RaiseException(
                message="Emploi non trouvé",
                code=404,
                errors={
                    "emploi_uid": "Aucun emploi ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Emploi trouvé avec succès",
        data=emploi_trouve
    )



 



