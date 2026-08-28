from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.type_agent.services import TypeagentService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.type_agent.schemas import TypeAgent, TypeAgentCreateModel, TypeAgentUpdateModel, TypeAgentResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


typeagent_router = APIRouter()
typeagent_service =TypeagentService()

@typeagent_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[TypeAgentResponse])
async def get_all_typeagents(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    #user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
   
    genres = await typeagent_service.get_all_typeagents(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Types agent trouvés avec succès",
        data=genres
    )


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



 



