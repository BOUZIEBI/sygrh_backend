from fastapi import Depends, HTTPException, status, Request, Header 
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.jwt import decode_access_token, decode_refresh_token
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.auth.schemas import AuthDependenciesResponse, UserModel
from sqlalchemy.orm import selectinload
from app.auth.services import get_user_by_id
from app.core.database import get_db
from app.db.models.user import User
from typing import Any, Annotated


#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)


from uuid import UUID


async def get_current_user(
    request: Request, 
    bearer_token: str | None = Depends(
        oauth2_scheme
    ),
    db: AsyncSession = Depends(get_db),
) -> AuthDependenciesResponse:
    
    token = bearer_token

    is_access_token = False 
    user= None
    message_echec="Utilisateur non authentifié"
    message_success="Utilisateur trouvé avec succès"
    is_access_token = False
    
    if not token:
        response_data= AuthDependenciesResponse(
            code=status.HTTP_200_OK,
            success=True,
            user=user,
            message=message_echec,
            is_access_token=is_access_token,
        )
        return response_data 

    # Supporte aussi un cookie contenant "Bearer <token>".
    token = token.removeprefix("Bearer ").strip()

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")
        session_id= UUID(payload.get("sid"))
       
        token_type = payload.get("type")

        if not isinstance(user_id, str):
            response_data= AuthDependenciesResponse(
                code=status.HTTP_200_OK,
                success=True,
                user=user,
                message=message_echec, 
                is_access_token=is_access_token,
            )           
            return response_data 
        
        if token_type != "access": 
            response_data= AuthDependenciesResponse(
                code=status.HTTP_200_OK,
                success=True,
                user=user,
                message=message_echec,
                is_access_token=is_access_token,
            )  
            return response_data 
            
        user_id_uuid = UUID(user_id)
        is_access_token = True

    except (JWTError, ValueError, TypeError) as error:
        response_data= AuthDependenciesResponse(
            code=status.HTTP_200_OK,
            success=True,
            user=user,
            message=message_echec,
            is_access_token=is_access_token,
        )
        return response_data 

    statement = (
        select(User).options(
            selectinload(User.role),
            selectinload(User.permissions),
        ).where(
            User.uid == user_id_uuid,
        )
    )

    result = await db.exec(statement)
    user = result.one_or_none()

    if user is None:
        response_data= AuthDependenciesResponse(
            code=status.HTTP_200_OK,
                success=True,
                user=user,
                message=message_echec,
                is_access_token=is_access_token,
        )
        return response_data 
    
    response_data= AuthDependenciesResponse(
        code=status.HTTP_200_OK,
        success=True,
        user=UserModel.model_validate(user),
        message=message_success,
        is_access_token=is_access_token,
    )
    return response_data 



async def get_current_active_user(
    current_user=Depends(get_current_user)
):
    #if not current_user.user:
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user



def require_permission(permission_code: str):

    async def checker(
        current_user=Depends(get_current_user),
    ):
        if current_user.code==status.HTTP_401_UNAUTHORIZED and current_user.success==False : 
            return current_user
       
        """ 
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilisateur inactif",
            )

        if not current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Aucune permission attribuée",
            )

        permission_codes = {
            permission.code
            for permission in current_user.permissions
        }

        if permission_code not in permission_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_code}' refusée",
            )
        """

        return current_user

    return checker




    