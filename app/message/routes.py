from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.message.services import MessageService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission

from app.message.schemas import MessageCreateModel, MessageUpdateModel, _MessageResponse, MessageResponse, MessageAllResponse
from app.core.exceptions_metier import RaiseException


message_router = APIRouter()
message_service = MessageService()

@message_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[_MessageResponse])
async def get_all_structures(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("VOIRLISTEMESSAGE"))
)->dict:
    messages = await message_service.get_all_messages(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Messages trouvés avec succès",
        data=messages
    )


@message_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[_MessageResponse])
async def create_un_message(
    message_data: MessageCreateModel,
    session: AsyncSession = Depends(get_session),
) -> dict:
   
    nouveau_message = await message_service.create_message(session,message_data)
    
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Message créé avec succès",
        data=nouveau_message
    )

@message_router.get("/{message_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[_MessageResponse])
async def get_un_message(
    message_uid: UUID,
    session: AsyncSession = Depends(get_session), 
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERMESSAGE"))
) -> dict:
    current_user_uid=current_user.uid
    message_trouve = await message_service.get_message(message_uid,session)

    if message_trouve is None:
            raise RaiseException(
                message="Message non trouvé",
                code=404,
                errors={
                    "message_uid": "Aucun message ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Message trouvé avec succès",
        data=message_trouve
    )



@message_router.delete(
    "/{message_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[_MessageResponse]
)
async def delete_message(
    message_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERMESSAGE"))
)->dict:
    message_to_delete = await message_service.delete_message(message_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Message supprimé avec succès",
        data=message_to_delete
    )

@message_router.get(
    "/restaurer/{message_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[_MessageResponse]
)
async def restore_message(
    message_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERMESSAGE"))
)->dict:
    message_to_restore = await message_service.restore_message(message_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Message restauré avec succès",
        data=message_to_restore
    )
 



