from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.db.models.login_attempt_state import LoginAttemptState
from app.db.models.password_reset_token import PasswordResetToken
from app.core.generer_code import CodeGenerator
from app.message.schemas import MessageCreateModel, MessageUpdateModel, MessageAllResponse, MessageResponse

from app.core.exceptions_metier import RaiseException
from app.db.models.type_structure import TypeStructure
from app.db.models.message import Message
from slugify import slugify
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class MessageService:
    async def get_all_messages(
        self,
        session: AsyncSession
    ) -> list[Message]:

        statement = (
            select(Message)
            .where(
                Message.is_deleted.is_(False)
            )
            .order_by(
                desc(Message.nom_prenoms_expediteur)
            )
        )

        result = await session.exec(statement)
        return result.all()


    async def create_message(
        self,
        session: AsyncSession,
        message_data: MessageCreateModel,
    ):

        # Créer le message
        message = Message(
            uid=uuid4(),
                
            email=message_data.email,
            code=CodeGenerator.generer_code_numerique(12),
            
            contenu=message_data.contenu,
            nom_prenoms_expediteur=message_data.nom_prenoms_expediteur,
            service_expediteur=message_data.service_expediteur,
                        
            cree_le = datetime.now(),
 
            is_deleted=False,
        )

        # Ajouter à la session
        session.add(message)

        # Sauvegarder
        await session.commit()
        await session.refresh(message)

        return message

    

    async def update_message(
        self,
        session: AsyncSession,
        message_data: MessageUpdateModel,
        current_user_uid:UUID
    ):
        pass



    async def delete_message(self, message_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        message_to_delete = await self.get_message_by_id( session, message_uid)

        if message_to_delete is None:
            raise RaiseException(
                message="Structure non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "structure_uid": "Aucune structure ne correspond à cet identifiant.",
                },
            )
        message_to_delete.is_deleted = True
        message_to_delete.supprime_le = datetime.now(timezone.utc)
        
        session.add(message_to_delete)
        await session.commit()
        await session.refresh(message_to_delete)
        
        return message_to_delete 
    

    async def get_message(self, message_uid: UUID, session: AsyncSession):
        statement = (
            select(Message)
            .where(Message.uid == message_uid)
        )

        result = await session.exec(statement)
        message = result.first()
        return message


    async def restore_message(self, message_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        message_to_restore= await self.get_message_by_id( session, message_uid)
    
        if message_to_restore is None:
            raise RaiseException(
                message="Message non trouvé",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "message_uid": "Aucun message ne correspond à cet identifiant.",
                },
            )
        message_to_restore.is_deleted = False
        message_to_restore.supprime_le = None
        message_to_restore.modifie_le = datetime.now(timezone.utc)
    
        session.add(message_to_restore)
        await session.commit()
        await session.refresh(message_to_restore)  

        return message_to_restore
    
      

    async def get_message_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Message]:
        statement = select(Message).where(Message.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_message_by_id(
        self,
        db: AsyncSession,
        message_uid: UUID
    ) -> Optional[Message]:
        statement = select(Message).where(Message.uid == message_uid)
        result = await db.exec(statement)
        return result.first()







