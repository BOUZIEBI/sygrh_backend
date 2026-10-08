from typing import List, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime, UTC, timezone
from fastapi import APIRouter, HTTPException, Request, Depends, status, File, Form, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from app.visiteur_session.services import VisiteurSessionService
from datetime import datetime, timezone
from starlette.concurrency import run_in_threadpool
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission

from app.visiteur_session.schemas import VisiteurSessionResponse, VisiteurSessionCreateModel, MessageAllResponse, MessageResponse

from app.core.exceptions_metier import RaiseException
from app.core.railway_bucket import RailwayBucketService
from app.db.models.visiteur_session import VisiteurSession



visiteur_session_router = APIRouter()
visiteur_session_service = VisiteurSessionService()
railway_bucket_service = RailwayBucketService()

@visiteur_session_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[VisiteurSessionResponse])
async def get_all_visiteur_sessions(
    session: AsyncSession = Depends(get_session),
)->dict:
    visiteur_sessions = await visiteur_session_service.get_all_visiteur_sessions(session)
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Visiteurs session trouvées avec succès",
        data=visiteur_sessions
    )


@visiteur_session_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse[VisiteurSessionResponse],
)
async def create_un_visiteur_session(
    request: Request,
    visiteur_session_data: VisiteurSessionCreateModel,
    session: AsyncSession = Depends(get_session),
) -> MessageResponse[VisiteurSessionResponse]:

    maintenant = datetime.now(UTC)
    nouveau_visiteur_session = await visiteur_session_service.create_visiteur_session(request, session, visiteur_session_data)

    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Visiteur session créée avec succès.",
        data=nouveau_visiteur_session,
    )



    
@visiteur_session_router.get("/{visiteur_session_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[VisiteurSessionResponse])
async def get_un_visiteur_session(
    visiteur_session_uid: UUID,
    session: AsyncSession = Depends(get_session), 
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CONSULTERSTRUCTURE"))
) -> dict:
    current_user_uid=current_user.uid
    visiteur_session_trouve = await visiteur_session_service.get_visiteur_session(visiteur_session_uid,session)

    if visiteur_session_trouve is None:
            raise RaiseException(
                message="Visiteur session non trouvée",
                code=404,
                errors={
                    "visiteur_session_uid": "Aucun visiteur session ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Visiteur session trouvé avec succès",
        data=visiteur_session_trouve
    )

 



