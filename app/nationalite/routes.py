from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter,Header, HTTPException, Request, Depends, status, File, Form, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from app.nationalite.services import NationaliteService
from app.auth.csrf import generate_csrf_token, verify_csrf_token
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.nationalite.schemas import Nationalite, NationaliteCreateModel, NationaliteUpdateModel, NationaliteResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException
from app.crypto.schemas import EncryptedResponse



nationalite_router = APIRouter()
nationalite_service = NationaliteService()

@nationalite_router.get(
    "/all",
    status_code=status.HTTP_200_OK, 
    #response_model=MessageAllResponse[NationaliteResponse],
    response_model=EncryptedResponse,
)
async def get_all_nationalites(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    session: AsyncSession = Depends(get_session),
    dependencies=[
        Depends(verify_csrf_token),
    ],
    #current_user=Depends(get_current_active_user),
    #user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
   
    nationalites = await nationalite_service.get_all_nationalites(session)
    
    response_data = MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Nationalités trouvées avec succès",
        data=nationalites
    )
    
    #return response_data;
    encrypt_data_nationalite=await nationalite_service.encrypt_nationalite_response(response_data, crypto_session_id)
    return encrypt_data_nationalite 


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



 



