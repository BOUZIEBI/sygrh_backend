from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi import APIRouter,Header, HTTPException, Request, Depends, status, File, Form, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from app.structure.services import StructureService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.structure.schemas import Structure, StructureCreateModel, StructureUpdateModel, StructureResponse, MessageResponse, MessageAllResponse
from app.core.exceptions_metier import RaiseException
from app.crypto.schemas import EncryptedResponse
from app.auth.csrf import generate_csrf_token, verify_csrf_token


structure_router = APIRouter()
structure_service = StructureService()

@structure_router.get(
    "/all",
    status_code=status.HTTP_200_OK, 
    #response_model=MessageAllResponse[StructureResponse],
    response_model=EncryptedResponse, 
)
async def get_all_structures(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    dependencies=[
        Depends(verify_csrf_token),
    ],
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("VOIRLISTESTRUCTURE"))
)->dict:
    
    if user_verifie.code==status.HTTP_401_UNAUTHORIZED and user_verifie.success==False :
        response_data = MessageAllResponse(
            code=user_verifie.code,
            success=user_verifie.success,
            message=user_verifie.message,
            data=None
        ) 
        
    if user_verifie.code==status.HTTP_200_OK and user_verifie.success==True :
        structures = await structure_service.get_all_structures(session)
        response_data = MessageAllResponse(
            code=status.HTTP_200_OK,
            success=True,
            message="Structures trouvées avec succès",
            data=structures
        )
   
    encrypt_data_typeagents=await structure_service.encrypt_structure_response(response_data, crypto_session_id)
    return encrypt_data_typeagents


@structure_router.post("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[StructureResponse])
async def create_une_structure(
    structure_data: StructureCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CREERSTRUCTURE"))
) -> dict:
    current_user_uid=current_user.uid
    nouvelle_structure = await structure_service.create_structure(session,structure_data,current_user_uid)
    
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structure créée avec succès",
        data=nouvelle_structure
    )

@structure_router.get("/{structure_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[StructureResponse])
async def get_une_structure(
    structure_uid: UUID,
    session: AsyncSession = Depends(get_session), 
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("CONSULTERSTRUCTURE"))
) -> dict:
    current_user_uid=current_user.uid
    structure_trouve = await structure_service.get_structure(structure_uid,session)

    if structure_trouve is None:
            raise RaiseException(
                message="Structure non trouvée",
                code=404,
                errors={
                    "structure_uid": "Aucune structure ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Élève trouvé avec succès",
        data=structure_trouve
    )



@structure_router.patch("/",status_code=status.HTTP_201_CREATED,response_model=MessageResponse[StructureResponse])
async def update_une_structure(
    structure_data: StructureUpdateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("MODIFIERSTRUCTURE"))
) -> dict:
    current_user_uid=current_user.uid
    structure_modifie = await structure_service.update_structure(session,structure_data,current_user_uid)   

    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structure modifiée avec succès",
        data=structure_modifie
    )


@structure_router.delete(
    "/{structure_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[StructureResponse]
)
async def delete_structure(
    structure_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("SUPPRIMERSTRUCTURE"))
)->dict:
    structure_to_delete = await structure_service.delete_structure(structure_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structuure supprimée avec succès",
        data=structure_to_delete
    )

@structure_router.get(
    "/restaurer/{structure_uid}", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse[StructureResponse]
)
async def restore_structure(
    structure_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
    user_verifie=Depends(require_permission("MODIFIERSTRUCTURE"))
)->dict:
    structure_to_restore = await structure_service.restore_structure(structure_uid, current_user.uid, session)
    return MessageResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Structure restaurée avec succès",
        data=structure_to_restore
    )
 



