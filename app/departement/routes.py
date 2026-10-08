from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter,Header, HTTPException, Request, Depends, status, File, Form, UploadFile
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.departement.services import DepartementService
from app.auth.csrf import generate_csrf_token, verify_csrf_token
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.departement.schemas import Departement, DepartementCreateModel, DepartementUpdateModel, DepartementResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException
from app.crypto.schemas import EncryptedResponse


departement_router = APIRouter()
departement_service = DepartementService()

@departement_router.get(
    "/all",
    status_code=status.HTTP_200_OK, 
    #response_model=MessageAllResponse[DepartementResponse],
    response_model=EncryptedResponse,
    
)
async def get_all_departements(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    session: AsyncSession = Depends(get_session),
    dependencies=[
        Depends(verify_csrf_token),
    ],
    #current_user=Depends(get_current_active_user),
    #user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
   
    departements = await departement_service.get_all_departements(session)
    
    response_data = MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Departements trouvés avec succès",
        data=departements
    )
    #return response_data;
    encrypt_data_departement=await departement_service.encrypt_departement_response(response_data, crypto_session_id)
    return encrypt_data_departement 


@departement_router.get(
    "/{departement_uid}",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse[DepartementResponse]
)
async def get_un_departement(
    departement_uid: UUID,
    session: AsyncSession = Depends(get_session),
    #current_user=Depends(get_current_active_user),
) -> dict:
    #current_user_uid=current_user.uid
    departement_trouve = await departement_service.get_departement(departement_uid,session)

    if departement_trouve is None:
        raise RaiseException(
            message="Departement non trouvée",
            code=404,
            errors={
                "departement_uid": "Aucun departement ne correspond à cet identifiant."
            }
        ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Departement trouvé avec succès",
        data=departement_trouve
    )



 



