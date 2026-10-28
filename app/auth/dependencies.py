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
from app.db.models.auth_session import AuthSession
from app.db.models.user import User
from typing import Any, Annotated
import time


#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)


from uuid import UUID



from uuid import UUID

from fastapi import Depends, Request, status
from jose import JWTError
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession



async def get_current_user(
    request: Request,
    bearer_token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthDependenciesResponse:

    message_echec = "Utilisateur non authentifié"
    message_success = "Utilisateur trouvé avec succès"

    def creer_reponse(
        success: bool,
        message: str,
        user: UserModel | None = None,
        is_access_token: bool = False,
        duree_minutes: float | None = None,
        code: int = status.HTTP_401_UNAUTHORIZED,
    ) -> AuthDependenciesResponse:
        return AuthDependenciesResponse(
            code=code,
            success=success,
            user=user,
            message=message,
            is_access_token=is_access_token,
            duree_minutes=duree_minutes,
        )

    # Récupérer le token depuis Authorization ou le cookie.
    token = bearer_token 

    if not token or not token.strip():
        return creer_reponse(
            success=False,
            message=message_echec,
        )

    # Accepter un token brut ou le format "Bearer <token>".
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    try:
        payload = decode_access_token(token)
        if not isinstance(payload, dict):
            return creer_reponse(
                success=False,
                message=message_echec,
            )

        iat = payload.get("iat")
        exp = payload.get("exp")
        
        temps_restant_minutes = max(
            0,
            (exp - time.time()) / 60,
        )
       
        if (
            isinstance(iat, bool)
            or not isinstance(iat, (int, float))
            or isinstance(exp, bool)
            or not isinstance(exp, (int, float))
            or exp <= iat
        ):
            return creer_reponse(
                success=False,
                message=message_echec,
            )

        duree_minutes = (exp - iat) / 60

        user_id = payload.get("sub")
        session_uid = payload.get("sid")
        token_type = payload.get("type")

        # Vérifier le type de token.
        if token_type != "access":
            return creer_reponse(
                success=False,
                message=message_echec,
            )

        # Vérifier les identifiants du token.
        if not isinstance(user_id, str) or not isinstance(
            session_uid, str
        ):
            return creer_reponse(
                success=False,
                message=message_echec,
            )

        user_uid = UUID(user_id)
        session_id = UUID(session_uid)

    except (JWTError, ValueError, TypeError, AttributeError):
        return creer_reponse(
            success=False,
            message=message_echec,
        )

    session_statement = select(AuthSession).where(
        AuthSession.uid == session_id,
        AuthSession.user_uid == user_uid,
    )
    session_result = await db.exec(session_statement)
    auth_session = session_result.one_or_none()

    if auth_session is None or auth_session.is_revoked:
        return creer_reponse(
            success=False,
            message=message_echec,
        )

    # Rechercher l'utilisateur avec son rôle et ses permissions.
    statement = (
        select(User)
        .options(
            selectinload(User.role),
            selectinload(User.permissions),
        )
        .where(User.uid == user_uid)
    )

    result = await db.exec(statement)
    user = result.one_or_none()

    if user is None:
        return creer_reponse(
            success=False,
            message=message_echec,
        )

    return creer_reponse(
        success=True,
        message=message_success,
        user=UserModel.model_validate(user),
        is_access_token=True,
        duree_minutes=duree_minutes,
        code=status.HTTP_200_OK,
    )



async def get_current_active_user(
    current_user=Depends(get_current_user)
):
   
    if not current_user.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
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




    