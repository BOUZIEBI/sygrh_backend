from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter,Header, HTTPException, Request, Depends, status, File, Form, UploadFile
from app.statut.services import StatutService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.statut.schemas import StatutCreateModel, StatutUpdateModel, StatutResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException
from app.crypto.schemas import EncryptedResponse
from app.auth.csrf import generate_csrf_token, verify_csrf_token



statut_router = APIRouter()
statut_service = StatutService()

@statut_router.get(
    "/all",
    status_code=status.HTTP_200_OK, 
    #response_model=MessageAllResponse[StatutResponse],
    response_model=EncryptedResponse, 
)
async def get_all_statuts(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    dependencies=[
        Depends(verify_csrf_token),
    ],
    session: AsyncSession = Depends(get_session),
    #current_user=Depends(get_current_active_user)
)->dict:
   
    statuts = await statut_service.get_all_statuts(session)
    
    response_data = MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Statuts trouvés avec succès",
        data=statuts
    )
    
    encrypt_data_statuts=await statut_service.encrypt_statut_response(response_data, crypto_session_id)
    return encrypt_data_statuts


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
    
    
    



 



