from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlmodel.ext.asyncio.session import AsyncSession
from app.agent.services import AgentService
from typing import List, Annotated
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.agent.schemas import AgentCreateModel, AgentUpdateModel, AgentResponse, MessageResponse, MessageAllResponse
from app.core.exceptions_metier import RaiseException
from app.crypto.schemas import EncryptedResponse, EncryptedPayload
from app.crypto.services import encrypt_response_for_react
from app.crypto.services import decrypt_client_payload
from app.core.redis import redis_client
from app.crypto.session_redis_store import SessionRedisStore
from app.auth.csrf import verify_csrf_token
from app.core.railway_bucket import RailwayBucketService
from pydantic import ValidationError
from app.auth.schemas import (
    ErrorLoginResponse,
)


agent_router = APIRouter()
agent_service = AgentService()
railway_bucket_service=RailwayBucketService()
crypto_session_store = SessionRedisStore(redis_client)


async def encrypt_agent_response(
    data: object,
    crypto_session_id: str,
) -> dict[str, str]:
   
    try:
        session_uid = UUID(crypto_session_id)
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CRYPTO_SESSION",
                "message": "L'identifiant de session cryptographique est invalide.",
            },
        ) from error

    client_public_key = await crypto_session_store.get_client_public_key(
        session_uid
    )
            
 
    if client_public_key is None:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "CLIENT_PUBLIC_KEY_REQUIRED",
                "message": (
                    "La clé publique RSA de React est absente "
                    "ou la session cryptographique a expiré."
                ),
            },
        )

    try:
        
        data_encrypted=encrypt_response_for_react(
            data=data,
            client_public_key_pem=client_public_key,
        )
       
        return data_encrypted
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "RESPONSE_ENCRYPTION_FAILED",
                "message": str(error),
            },
        ) from error



@agent_router.get(
    "/all",
    status_code=status.HTTP_200_OK, 
    #response_model=MessageAllResponse[AgentResponse]
    response_model=EncryptedResponse,
)
async def get_all_agents(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    dependencies=[
        Depends(verify_csrf_token),
    ],
    #user_verifie=Depends(require_permission("VOIRLISTESTRUCTURE"))
)->dict:
    agents = await agent_service.get_all_agents(session)
    response_data = MessageAllResponse[AgentResponse](
        code=status.HTTP_200_OK,
        success=True,
        message="Agents trouvés avec succès",
        data=agents
    )
    
    encrypt_data_auth=await encrypt_agent_response(response_data, crypto_session_id)
    return encrypt_data_auth


@agent_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    #response_model=MessageResponse[AgentResponse],
    response_model=EncryptedResponse,
)
async def create_un_agent(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    #agent_data: AgentCreateModel,
    agent_data: EncryptedPayload,  
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    #current_user=Depends(require_permission("CREERAGENT"))
) -> dict:
   
    # 1. Déchiffrer les données envoyées par React
    try:
        decrypted_data = decrypt_client_payload(agent_data)
        
    except ValueError as error:
        
        response_data=ErrorLoginResponse(
            code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Impossible de déchiffrer les données d’authentification.",
            remaining=0
        )
        encrypt_data_auth=await encrypt_agent_response(response_data, crypto_session_id)
        return encrypt_data_auth
        
    except RuntimeError as error:
        # Problème avec la clé privée FastAPI
        response_data = ErrorLoginResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            message="La configuration cryptographique du serveur est invalide.",
            remaining=0
        )
        encrypt_data_auth=await encrypt_agent_response(response_data, crypto_session_id)
        return encrypt_data_auth
    
    # 2. Valider les données déchiffrées
    try:
        agent_data_decrypted = (
            AgentCreateModel.model_validate(
                decrypted_data
            )
        )
    except ValidationError as error:
        
        response_data= ErrorLoginResponse(
            code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            success=False,
            message="Les données d’authentification sont invalides.",
            remaining=0
        )
        
        encrypt_data_auth=await encrypt_agent_response(response_data, crypto_session_id)
        return encrypt_data_auth
    
    current_user_uid= current_user.user.uid
    nouvel_agent = await agent_service.create_agent(session,agent_data_decrypted,current_user_uid)
    
    if nouvel_agent.success==False:
        encrypt_data_auth=await encrypt_agent_response(nouvel_agent, crypto_session_id)
        return encrypt_data_auth
    
    
    encrypt_data_auth=await encrypt_agent_response(nouvel_agent, crypto_session_id)
    return encrypt_data_auth


@agent_router.get("/{agent_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[AgentResponse])
async def get_un_agent(
    agent_uid: UUID,
    session: AsyncSession = Depends(get_session), 
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CONSULTERAGENT"))
) -> dict:
    current_user_uid=current_user.user.uid
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
    current_user_uid=current_user.user.uid
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
    agent_to_delete = await agent_service.delete_agent(agent_uid, current_user.user.uid, session)
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
 



