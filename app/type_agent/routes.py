from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter,Header, HTTPException, Request, Depends, status, File, Form, UploadFile
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.type_agent.services import TypeagentService
from app.auth.csrf import generate_csrf_token, verify_csrf_token
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.type_agent.schemas import TypeAgent, TypeAgentCreateModel, TypeAgentUpdateModel, TypeAgentResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException
from app.crypto.schemas import EncryptedResponse


typeagent_router = APIRouter()
typeagent_service =TypeagentService()

@typeagent_router.get(
    "/all",
    status_code=status.HTTP_200_OK, 
    #response_model=MessageAllResponse[TypeAgentResponse]
    response_model=EncryptedResponse,
)
async def get_all_typeagents(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    dependencies=[
        Depends(verify_csrf_token),
    ],
    #user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
   
    typeagents = await typeagent_service.get_all_typeagents(session)

    response_data = MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Types agent trouvés avec succès",
        data=typeagents
    )

    encrypt_data_typeagents=await typeagent_service.encrypt_typeagent_response(response_data, crypto_session_id)
    return encrypt_data_typeagents


@typeagent_router.get("/{typeagent_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[TypeAgentResponse])
async def get_un_typeagente(
    typeagent_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    typeagent_trouve = await typeagent_service.get_typeagent(typeagent_uid,session)

    if typeagent_trouve is None:
            raise RaiseException(
                message="Type agent non trouvée",
                code=404,
                errors={
                    "genre_uid": "Aucun type agent ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Type agent trouvé trouvé avec succès",
        data=typeagent_trouve
    )



 



