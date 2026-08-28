from datetime import timedelta
from app.core.email import send_password_reset_email
from fastapi import Request, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
#from sqlalchemy.orm import Session
from app.core.login_limiter import login_limiter
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from app.core.config import settings
from app.core.database import get_db
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.security import hash_password, validate_password_strength, verify_password
from app.auth.dependencies import get_current_active_user
from app.auth.schemas import (
    LogoutRequest,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.auth.schemas import UserCreate, AffectationPermissionCreate, UserResponse, MessageResponse_
from app.auth.services import recharger_user, consume_password_reset_token,create_auth_session, create_password_reset_token, generate_session_id,is_user_login_locked, register_failed_login, reset_failed_logins, revoke_all_auth_sessions, revoke_auth_session, rotate_refresh_session, validate_refresh_session

from app.auth.services import affecter_role, affecter_permissions, create_user, get_user_by_email, get_user_by_id



auth_router = APIRouter()


@auth_router.post(
    "/register",
    response_model=MessageResponse_[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    
    try:
        validate_password_strength(user.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "field": "email",
                "message": "Cette adresse email est déjà utilisée."
            }
        )

    nouvel_utilisateur=await create_user(db, user)

    return MessageResponse_(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Utilisateur créé avec succès",
        data=nouvel_utilisateur
    )


@auth_router.post("/login", response_model=TokenResponse)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    # IP du client
    client_ip = request.client.host

    # Identifiant unique
    identifier = (
        f"{form_data.username.lower().strip()}:{client_ip}"
    )

    # Vérifier le blocage
    blocked, remaining = await login_limiter.is_blocked(
        identifier
    )

    if blocked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Trop de tentatives de connexion.",
                "retry_after": remaining
            }
        )

    user = await get_user_by_email(db, form_data.username)
   
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    user_uid=str(user.uid)

    if user is None or not verify_password(form_data.password, user.password_hash):

        attempts = await login_limiter.register_failed_attempt(
            identifier
        )

        remaining_attempts = max(
            0,
            login_limiter.MAX_ATTEMPTS - attempts
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Identifiants incorrects.",
                "remaining_attempts": remaining_attempts
            }
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    # Connexion réussie
    await login_limiter.reset(identifier)

    access_token = create_access_token(data={"sub": str(user_uid)})
    session_id = generate_session_id()

    refresh_token = create_refresh_token(
        data={"sub": str(user_uid), "sid": session_id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    
    create_auth_session(
        db=db,
        user_id=user_uid,
        session_id=session_id,
        refresh_token=refresh_token,
        expires_in_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )



@auth_router.post(
    "/affecter-permission",
    response_model=MessageResponse_[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def affecterPermission(user_data: AffectationPermissionCreate, db: AsyncSession = Depends(get_db)):
    
    nouvel_utilisateur=await affecter_permissions(db, user_data.user_uid, user_data.permissions)

    return MessageResponse_(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Utilisateur créé avec succès",
        data=nouvel_utilisateur
    )

@auth_router.get("/me", response_model=MessageResponse_[UserResponse])
async def getUser(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    
    user_recharge=await recharger_user(session=db, user_uid=current_user.uid)
    return MessageResponse_(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Utilisateur trouvé avec succès",
        data=user_recharge
    )



@auth_router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        decoded = decode_refresh_token(payload.refresh_token)
        user_id = UUID(decoded.get("sub"))
        session_id = decoded.get("sid")
        
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalided refresh token")

    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    session = validate_refresh_session(db, session_id=session_id, refresh_token=payload.refresh_token)
    
    if session is None or session.user_uid != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_session_id = generate_session_id()
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.uid), "sid": new_session_id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    rotate_refresh_session(
        db=db,
        current_session=session,
        new_session_id=new_session_id,
        new_refresh_token=new_refresh_token,
    )

    new_access_token = create_access_token(data={"sub": str(user.uid)})
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@auth_router.post("/logout", response_model=MessageResponse)
def logout(
    payload: LogoutRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.all_devices:
        count = revoke_all_auth_sessions(db, current_user.uid)
        return MessageResponse(message=f"Logged out from {count} active session(s)")

    if payload.refresh_token:
        try:
            decoded = decode_refresh_token(payload.refresh_token)
            sub = decoded.get("sub")
            session_id = decoded.get("sid")
        except (JWTError, TypeError, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        user_id = UUID(sub)
        if user_id != current_user.uid or not session_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        revoke_auth_session(db, session_id)
        return MessageResponse(message="Logged out from current session")

    revoke_all_auth_sessions(db, current_user.uid)
    return MessageResponse(message="Logged out from all sessions")


@auth_router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    debug_token = None

    if user and user.is_active:
        token = create_password_reset_token(db, user.uid)
       
        if settings.DEBUG:
            debug_token = token

        reset_link = (
            f"{settings.FRONTEND_URL}/reset-password"
            f"?token={token}"
        )

        #await send_password_reset_email(
        #    email="trayemarc@gmail.com",
        #    reset_link=reset_link
        #)

    return MessageResponse(
        message="If this account exists, a reset link has been sent",
        debug_token=debug_token,
    )


@auth_router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    try:
        validate_password_strength(payload.new_password)
        
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    token = consume_password_reset_token(db, payload.token)

    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user = get_user_by_id(db, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user")

    user.password_hash = hash_password(payload.new_password)
    db.commit()

    revoke_all_auth_sessions(db, user.uid)

    return MessageResponse(message="Password updated successfully")
