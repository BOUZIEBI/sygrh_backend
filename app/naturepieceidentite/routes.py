from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.naturepieceidentite.services import NaturepieceidentiteService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.naturepieceidentite.schemas import Naturepieceidentite, NaturepieceidentiteCreateModel, NaturepieceidentiteUpdateModel, NaturepieceidentiteResponse, GetNaturepieceidentiteModel, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


naturepieceidentite_router = APIRouter()
naturepieceidentite_service = NaturepieceidentiteService()

@naturepieceidentite_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[NaturepieceidentiteResponse])
async def get_all_naturepieceidentites(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
)->dict:
   
    naturepieceidentites = await naturepieceidentite_service.get_all_naturepieceidentites(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Natures pièce identités trouvées avec succès",
        data=naturepieceidentites
    )


@naturepieceidentite_router.get("/{naturepieceidentite_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[NaturepieceidentiteResponse])
async def get_une_naturepieceidentite(
    naturepieceidentite_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    naturepieceidentite_trouve = await naturepieceidentite_service.get_naturepieceidentite(naturepieceidentite_uid,session)

    if naturepieceidentite_trouve is None:
            raise RaiseException(
                message="Nature pièce identité non trouvée",
                code=404,
                errors={
                    "naturepieceidentite_uid": "Aucune nature pièce identité ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Nature pièce identité trouvée avec succès",
        data=naturepieceidentite_trouve
    )



 



