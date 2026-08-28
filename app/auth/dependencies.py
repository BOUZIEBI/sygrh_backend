from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.jwt import decode_access_token
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.services import get_user_by_id
from app.core.database import get_db
from app.db.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


from uuid import UUID



async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    
    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication"
            )

        user_id_uuid = UUID(user_id)

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication"
        )
    
    user = await get_user_by_id(
        db,
        user_id_uuid
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # =====================================================
    # Charger User + Role + Permissions explicitement
    # =====================================================

    statement = (
        select(User)
        .options(
            selectinload(User.role),
            selectinload(User.permissions),
        )
        .where(User.uid == user_id_uuid)
    )

    result = await db.exec(statement)

    user = result.one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
        )

    # Maintenant ceci ne déclenche PAS de lazy loading
    

    return user

async def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


def require_permission(permission_code: str):

    async def checker(
        current_user=Depends(get_current_user),
    ):
        if not current_user.is_active:
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

        return current_user

    return checker




    