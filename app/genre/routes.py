from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter,Header, HTTPException, Request, Depends, status, File, Form, UploadFile
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.genre.services import GenreService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.genre.schemas import Genre, GenreCreateModel, GenreUpdateModel, GenreResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException
from app.crypto.schemas import EncryptedResponse
from app.auth.csrf import generate_csrf_token, verify_csrf_token



genre_router = APIRouter()
genre_service = GenreService()

@genre_router.get(
    "/all",
    status_code=status.HTTP_200_OK, 
    #response_model=MessageAllResponse[GenreResponse],
    response_model=EncryptedResponse, 
)
async def get_all_genres(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    session: AsyncSession = Depends(get_session),
    #current_user=Depends(get_current_active_user),
    dependencies=[
        Depends(verify_csrf_token),
    ],
    #user_verifie=Depends(require_permission("EDITERAGENT"))
)->dict:
   
    genres = await genre_service.get_all_genres(session)
    
    response_data = MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Genres trouvés avec succès",
        data=genres
    )
    
    encrypt_data_genre=await genre_service.encrypt_genre_response(response_data, crypto_session_id)
    return encrypt_data_genre 


@genre_router.get("/{genre_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[GenreResponse])
async def get_un_genre(
    genre_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    genre_trouve = await genre_service.get_genre(genre_uid,session)

    if genre_trouve is None:
            raise RaiseException(
                message="Genre non trouvée",
                code=404,
                errors={
                    "genre_uid": "Aucun genre ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Genre trouvé avec succès",
        data=genre_trouve
    )



 



