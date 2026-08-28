from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.fichevalidation.services import FicheValidationService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.fichevalidation.schemas import FicheValidationCreateModel, FicheValidationUpdateModel, FicheValidationResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


fichevalidation_router = APIRouter()
fichevalidation_service = FicheValidationService()

@fichevalidation_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[FicheValidationResponse])
async def get_all_fichevalidations(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
)->dict:
   
    fichevalidations = await fichevalidation_service.get_all_fichevalidations(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Fiches validation trouvées avec succès",
        data=fichevalidations
    )


@fichevalidation_router.get("/{fichevalidation_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[FicheValidationResponse])
async def get_un_grade(
    fichevalidation_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    fichevalidation_trouve = await fichevalidation_service.get_fichevalidation(fichevalidation_uid,session)

    if fichevalidation_trouve is None:
            raise RaiseException(
                message="Fiche validation non trouvée",
                code=404,
                errors={
                    "fichevalidation_uid": "Aucune fiche validation ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="fiche validation trouvé avec succès",
        data=fichevalidation_trouve
    )



 



