from datetime import timedelta
from app.core.email import send_password_reset_email
from fastapi import (
    Request,
    Header,
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    status,
)
from app.auth.cookies import (
    set_access_token_cookie,
    set_refresh_token_cookie,
)
from app.auth.cookies import (
    ACCESS_COOKIE,
    REFRESH_COOKIE,
    delete_auth_cookies,
    set_access_token_cookie,
    set_csrf_cookie,
    set_refresh_token_cookie,
)
from app.auth.csrf import generate_csrf_token, verify_csrf_token
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from typing import List, Annotated
from app.core.login_limiter import login_limiter
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from pydantic import ValidationError
from app.core.config import settings
from app.db.main import get_session
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token, decode_access_token
from app.core.security import hash_password, validate_password_strength, verify_password
from app.auth.dependencies import get_current_active_user
from app.auth.schemas import (
    LogoutRequest,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    LoginResponse,
    LoginData,
    LoginRequestData,
    ErrorLoginResponse,
    MessageLogoutResponse,
    LoginPayload
)
from fastapi.security import OAuth2PasswordBearer
from app.auth.schemas import UserCreate, AffectationPermissionCreate, UserResponse, MessageResponse_,LogoutResponse, LoginRequest
from app.auth.services import recharger_user, consume_password_reset_token,create_auth_session, encrypt_auth_response, create_password_reset_token, generate_session_id,is_user_login_locked, register_failed_login, reset_failed_logins, revoke_all_auth_sessions, revoke_auth_session, rotate_refresh_session, validate_refresh_session
from app.crypto.schemas import EncryptedResponse, EncryptedPayload
from app.auth.services import affecter_role, affecter_permissions, create_user, get_user_by_email, get_user_by_id
from app.crypto.services import decrypt_client_payload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
auth_router = APIRouter()


@auth_router.get("/csrf")
async def get_csrf_token(response: Response):
    csrf_token = generate_csrf_token()

    set_csrf_cookie(response, csrf_token)

    return {
        "success": True,
        "message": "Jeton CSRF généré.",
        "csrf_token": csrf_token,
    }


@auth_router.post(
    "/register",
    response_model=MessageResponse_[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(user: UserCreate, db: AsyncSession = Depends(get_session)):
    
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


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    #response_model=EncryptedResponse,
    response_model=LoginResponse
)
async def login(
    #crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    request: Request,
    response: Response,
    #auth_data: EncryptedPayload,
    auth_data: LoginRequest,
    db: AsyncSession = Depends(
        get_session
    ),
) -> dict:
    
    # 1. Déchiffrer les données envoyées par React
    """ 
    try:
        decrypted_data = decrypt_client_payload(auth_data)
    except ValueError as error:
        
        response_data=ErrorLoginResponse(
            code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Impossible de déchiffrer les données d’authentification.",
            remaining=0
        )
        #encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        #return encrypt_data_auth
        
    except RuntimeError as error:
        # Problème avec la clé privée FastAPI
        response_data = ErrorLoginResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            message="La configuration cryptographique du serveur est invalide.",
            remaining=0
        )
        #encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        #return encrypt_data_auth
    """
    """ 
    # 2. Valider les données déchiffrées
    try:
        credentials = (
            LoginRequestData.model_validate(
                decrypted_data
            )
        )
    except ValidationError as error:
        
        response_data= ErrorLoginResponse(
            code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            success=False,
            message="Les données d’authentification sont invalides.",
            remaining=0
        )
        #encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        #return encrypt_data_auth
    """

    email = (
        #credentials.username
        auth_data.username
        .lower()
        .strip()
    )

    # 3. Récupérer l’adresse IP
    forwarded_for = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded_for:
        client_ip = (
            forwarded_for
            .split(",", maxsplit=1)[0]
            .strip()
        )
    elif request.client:
        client_ip = request.client.host
    else:
        client_ip = "0.0.0.0"

    identifier = f"{email}:{client_ip}"

    #4. Vérifier le blocage
    blocked, remaining = (
        await login_limiter.is_blocked(
            identifier
        )
    )

    if blocked:
        response_data= ErrorLoginResponse(
            code=status.HTTP_429_TOO_MANY_REQUESTS,
            success=False,
            message="Trop de tentatives de connexion.",
            data=None,
            remaining=remaining
        )
        return response_data
        #encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        #return encrypt_data_auth

    # 5. Rechercher et authentifier l’utilisateur
    user = await get_user_by_email(db,email,)

    credentials_are_valid = (
        user is not None
        and verify_password(
            #credentials.password,
            auth_data.password,
            user.password_hash,
        )
    )

    if not credentials_are_valid:
        attempts = (
            await login_limiter
            .register_failed_attempt(
                identifier
            )
        )

        remaining_attempts = max(
            0,
            login_limiter.MAX_ATTEMPTS
            - attempts,
        )
        
        response_data= ErrorLoginResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            message="Adresse e-mail ou mot de passe incorrect.",
            data=None,
            remaining=0
        )
        return response_data
        #encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        #return encrypt_data_auth


    # Ici, user ne peut plus être None
    if not user.is_active:
        response_data= ErrorLoginResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            message="Ce compte utilisateur est inactif.",
            data=None,
            remaining=0
        )
        return response_data
        #encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        #return encrypt_data_auth

    user_uid = user.uid
    session_id = generate_session_id()

    # 6. Générer les jetons
    access_token = create_access_token(
        data={
            "sub": str(user_uid),
            "sid": str(session_id),
        },
        expires_delta=timedelta(
            days=(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        ),
    )

    refresh_token = create_refresh_token(
        data={
            "sub": str(user_uid),
            "sid": str(session_id),
        },
        expires_delta=timedelta(
            days=(
                settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        ),
    )

    # 7. Enregistrer la session d’authentification
    await create_auth_session(
        db=db,
        user_id=user_uid,
        session_id=session_id,
        refresh_token=refresh_token,
        expires_in_days=(
            settings
            .REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )

    # Réinitialiser les tentatives après succès complet
    await login_limiter.reset(
        identifier
    )

    # 8. Construire la réponse
    token_data = LoginData(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=(
            settings
            .ACCESS_TOKEN_EXPIRE_MINUTES
            * 60
        ),
    )

    response_data= LoginResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Connexion réussie.",
        data=token_data,
    )
    return response_data
    #encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
    #return encrypt_data_auth
    


@auth_router.post(
    "/affecter-permission",
    response_model=MessageResponse_[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def affecterPermission(user_data: AffectationPermissionCreate, db: AsyncSession = Depends(get_session)):
    
    nouvel_utilisateur=await affecter_permissions(db, user_data.user_uid, user_data.permissions)

    return MessageResponse_(
        code=status.HTTP_201_CREATED,
        success=True,
        message="Utilisateur créé avec succès",
        data=nouvel_utilisateur
    )


@auth_router.get(
    "/me", 
    response_model=EncryptedResponse,
    #response_model=MessageResponse_,
    dependencies=[
        Depends(verify_csrf_token),
    ],
)
async def getUser(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
)->EncryptedResponse:
    
    user_recharge=await recharger_user(session=db, user_uid=current_user.user.uid)
    user_response = UserResponse.model_validate(user_recharge)
    response_data = MessageResponse_(
        code=current_user.code,
        success=current_user.success,
        message=current_user.message,
        data=user_response
    )
    #return response_data#
    encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
    return encrypt_data_auth



@auth_router.post(
    "/refresh", 
    #response_model=TokenResponse,
    response_model=EncryptedResponse,
    dependencies=[
        Depends(verify_csrf_token),
    ],
)
async def refresh_tokens(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    request: Request,
    payload: str | None = Depends(
        oauth2_scheme
    ),
    db: AsyncSession = Depends(get_session)
)->TokenResponse:
    refresh_token = payload
   
    try:
        refresh_token = (
            payload
            .removeprefix("Bearer ")
            .strip()
        )
        decoded = decode_refresh_token(refresh_token)
        user_id = UUID(decoded.get("sub"))
        session_id = decoded.get("sid")
        
    except (JWTError, TypeError, ValueError):
        response_data= ErrorLoginResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            message="Invalid refresh token.",
            remaining=0
        )
        encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        return encrypt_data_auth
        
    if not session_id:
        response_data= ErrorLoginResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            message="Invalid refresh token.",
            remaining=0
        )
        encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        return encrypt_data_auth


    session = await validate_refresh_session(db, session_id=session_id, refresh_token=refresh_token)
        
    if session is None or session.user_uid != user_id:
        response_data= ErrorLoginResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            message="Invalid refresh token.",
            remaining=0
        )
        encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        return encrypt_data_auth

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        response_data= ErrorLoginResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            message="User not found or inactive.",
            remaining=0
        )
        encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
        return encrypt_data_auth

    new_session_id = generate_session_id()
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.uid), "sid": new_session_id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    await rotate_refresh_session(
        db=db,
        current_session=session,
        new_session_id=new_session_id,
        new_refresh_token=new_refresh_token,
    )

    new_access_token = create_access_token(data={"sub": str(user.uid)})
    response_data = TokenResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    #return response_data

    encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
    return encrypt_data_auth



@auth_router.post(
    "/deconnexion", 
    #response_model=MessageResponse
    response_model=EncryptedResponse,
    dependencies=[
        Depends(verify_csrf_token),
    ],
)
async def logout(
    crypto_session_id: Annotated[str, Header(alias="X-Crypto-Session-ID")],
    payload: str | None = Depends(
        oauth2_scheme
    ),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
)->EncryptedResponse:
    if payload:
        try:
            access_token = (
                payload
                .removeprefix("Bearer ")
                .strip()
            )
            
            decoded = decode_access_token(access_token)
            sub = decoded.get("sub")
            session_id = decoded.get("sid")
        except (JWTError, TypeError, ValueError):
            response_data = MessageResponse(message="Logged out from all sessions")
            encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
            return encrypt_data_auth

        user_id = UUID(sub)
        if user_id != current_user["user"].uid or not session_id:
            response_data = MessageResponse(message="Logged out from all sessions")
            encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
            return encrypt_data_auth

        await revoke_auth_session(db, session_id)

    await revoke_all_auth_sessions(db, current_user["user"].uid)
    response_data = MessageResponse(message="Logged out from all sessions")
    #return MessageResponse(message="Logged out from all sessions")
    encrypt_data_auth=await encrypt_auth_response(response_data, crypto_session_id)
    return encrypt_data_auth



@auth_router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(payload: PasswordResetRequest, db: AsyncSession = Depends(get_session)):
    user = await get_user_by_email(db, payload.email)
    debug_token = None

    if user and user.is_active:
        token = await create_password_reset_token(db, user.uid)
       
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
async def reset_password(payload: PasswordResetConfirm, db: AsyncSession = Depends(get_session)):
    try:
        validate_password_strength(payload.new_password)
        
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    token = await consume_password_reset_token(db, payload.token)

    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user = await get_user_by_id(db, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user")

    user.password_hash = hash_password(payload.new_password)
    await db.commit()

    await revoke_all_auth_sessions(db, user.uid)

    return MessageResponse(message="Password updated successfully")
