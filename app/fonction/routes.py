from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.fonction.services import FonctionService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.fonction.schemas import Fonction, FonctionCreateModel, FonctionUpdateModel, FonctionResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


fonction_router = APIRouter()
fonction_service = FonctionService()

@fonction_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[FonctionResponse])
async def get_all_fonctions(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
)->dict:
   
    fonctions = await fonction_service.get_all_fonctions(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Fonctions trouvées avec succès",
        data=fonctions
    )


@fonction_router.get("/{fonction_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[FonctionResponse])
async def get_un_fonction(
    fonction_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    fonction_trouve = await fonction_service.get_fonction(fonction_uid,session)

    if fonction_trouve is None:
            raise RaiseException(
                message="Fonction non trouvée",
                code=404,
                errors={
                    "fonction_uid": "Aucune fonction ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Fonction trouvée avec succès",
        data=fonction_trouve
    )



 



