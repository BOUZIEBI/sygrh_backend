from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.agent.services import AgentService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.agent.schemas import AgentCreateModel, AgentUpdateModel, AgentResponse, MessageResponse, MessageAllResponse
from app.core.exceptions_metier import RaiseException


agent_router = APIRouter()
agent_service = AgentService()

@agent_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[AgentResponse])
async def get_all_agents(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("VOIRLISTESTRUCTURE"))
)->dict:
    agents = await agent_service.get_all_agents(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Agents trouvés avec succès",
        data=agents
    )


@agent_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[AgentResponse])
async def create_un_agent(
    agent_data: AgentCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CREERAGENT"))
) -> dict:
    current_user_uid=current_user.uid
    nouvel_agent = await agent_service.create_agent(session,agent_data,current_user_uid)
    
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Agent créé avec succès",
        data=nouvel_agent
    )


@agent_router.get("/{agent_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[AgentResponse])
async def get_un_agent(
    agent_uid: UUID,
    session: AsyncSession = Depends(get_session), 
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CONSULTERAGENT"))
) -> dict:
    current_user_uid=current_user.uid
    agent_trouve = await agent_service.get_agent(agent_uid,session)

    if agent_trouve is None:
            raise RaiseException(
                message="Agent non trouvé",
                code=404,
                errors={
                    "agent_uid": "Aucun agent ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Agent trouvé avec succès",
        data=agent_trouve
    )



@agent_router.patch("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[AgentResponse])
async def update_une_agent(
    agent_data: AgentUpdateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("EDITERAGENT"))
) -> dict:
    current_user_uid=current_user.uid
    agent_modifie = await agent_service.update_agent(session, agent_data.agent_uid, agent_data, current_user_uid)   

    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Agent modifié avec succès",
        data=agent_modifie
    )


@agent_router.delete(
    "/{agent_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[AgentResponse]
)
async def delete_agent(
    agent_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERAGENT"))
)->dict:
    agent_to_delete = await agent_service.delete_agent(agent_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Agent supprimé avec succès",
        data=agent_to_delete
    )

@agent_router.get(
    "/restaurer/{agent_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[AgentResponse]
)
async def restore_agent(
    agent_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
    agent_to_restore = await agent_service.restore_agent(agent_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Agent restauré avec succès",
        data=agent_to_restore
    )
 



