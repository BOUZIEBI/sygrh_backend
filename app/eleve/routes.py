from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.eleve.services import EleveService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user
from .schemas import Eleve, EleveCreateModel, EleveUpdateModel,MessageResponse, MessageAllResponse, EleveResponse, GetEleveModel
from app.core.exceptions_metier import RaiseException


eleve_router = APIRouter()
eleve_service = EleveService()


@eleve_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[EleveResponse])
async def get_all_eleves(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
)->dict:
    
    eleves = await eleve_service.get_all_eleves(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Élèves trouvés avec succès",
        data=eleves
    )


@eleve_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[EleveResponse])
async def create_un_eleve(
    eleve_data: EleveCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    nouvel_eleve = await eleve_service.create_eleve(session,eleve_data,current_user_uid)
    
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Élève créé avec succès",
        data=nouvel_eleve
    )

@eleve_router.get("/{eleve_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[EleveResponse])
async def get_un_eleve(
    eleve_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    eleve_trouve = await eleve_service.get_eleve(eleve_uid,session)

    if eleve_trouve is None:
            raise RaiseException(
                message="Élève non trouvé",
                code=404,
                errors={
                    "eleve_uid": "Aucun élève ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Élève trouvé avec succès",
        data=eleve_trouve
    )

@eleve_router.patch("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[EleveResponse])
async def update_un_eleve(
    eleve_data: EleveUpdateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    eleve_modifie = await eleve_service.update_eleve(session,eleve_data,current_user_uid)   

    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Élève trouvé avec succès",
        data=eleve_modifie
    )


@eleve_router.delete(
    "/{eleve_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[EleveResponse]
)
async def delete_eleve(
    eleve_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
)->dict:
    eleve_to_delete = await eleve_service.delete_eleve(eleve_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Élève supprimé avec succès",
        data=eleve_to_delete
    )

@eleve_router.get(
    "/restaurer/{eleve_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[EleveResponse]
)
async def restore_eleve(
    eleve_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
)->dict:
    eleve_to_restore = await eleve_service.restore_eleve(eleve_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Élève restauré avec succès",
        data=eleve_to_restore
    )
 



