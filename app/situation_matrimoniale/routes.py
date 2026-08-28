from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.situation_matrimoniale.services import SituationMatrimonialeService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.situation_matrimoniale.schemas import SituationMatrimonialeCreateModel, SituationMatrimonialeUpdateModel, SituationMatrimonialeResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


situationmatrimoniale_router = APIRouter()
situationmatrimoniale_service = SituationMatrimonialeService()

@situationmatrimoniale_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[SituationMatrimonialeResponse])
async def get_all_situationmatrimoniales(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
)->dict:
   
    situationmatrimoniales = await situationmatrimoniale_service.get_all_situationmatrimoniales(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Situations matrimoniales trouvées avec succès",
        data=situationmatrimoniales
    )


@situationmatrimoniale_router.get("/{situationmatrimoniale_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[SituationMatrimonialeResponse])
async def get_un_situationmatrimonial(
    situationmatrimoniale_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    situationmotrimoniale_trouve = await situationmatrimoniale_service.get_situationmatrimoniale(situationmatrimoniale_uid,session)

    if situationmotrimoniale_trouve is None:
            raise RaiseException(
                message="Situation matrimoniale non trouvée",
                code=404,
                errors={
                    "situationmatrimoniale_uid": "Aucune situation matrimoniale ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Situation motrimoniale trouvé avec succès",
        data=situationmotrimoniale_trouve
    )



 



