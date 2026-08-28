from datetime import timedelta
from uuid import uuid4
from sqlmodel import select
from app.core.config import settings
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.db.models.login_attempt_state import LoginAttemptState
from app.db.models.password_reset_token import PasswordResetToken 
from app.auth.schemas import UserCreate, PermissionModel
from sqlalchemy.orm import selectinload
from app.db.models.user import User
from app.db.models.role import Role
from app.db.models.permission import Permission
from app.db.models.user_permission import UserPermission
from app.core.security import hash_password
from uuid import UUID
from datetime import date, datetime, UTC, timezone
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession




async def create_user(
    db: AsyncSession,
    user: UserCreate
) -> User:

    db_user = User(
        email=user.email,
        username=user.email,
        password_hash=hash_password(user.password),
        is_active=True,
        cree_le=datetime.now(timezone.utc)
    )

    # Ajouter l'utilisateur
    db.add(db_user)

    # Enregistrer
    await db.commit()

    # Recharger les valeurs générées
    await db.refresh(db_user)

    # ============================
    # Affecter le rôle
    # ============================

    if user.role_uid is not None:

        await affecter_role(
            session=db,
            user_uid=db_user.uid,
            role_uid=user.role_uid
        )

    # ============================
    # Affecter les permissions
    # ============================

    if user.permissions is not None:

        await affecter_permissions(
            session=db,
            user_uid=db_user.uid,
            permissions=user.permissions
        )

    # ============================
    # Recharger User + relations
    # ============================

    user_ajoute = await recharger_user(
        db,
        db_user.uid
    )

    if user_ajoute is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur créé mais impossible à recharger"
        )

    return user_ajoute



async def recharger_user(
    session: AsyncSession,
    user_uid: UUID,
) -> User | None:

    statement = (
        select(User)
        .where(User.uid == user_uid)
        .options(
            selectinload(User.role),
            selectinload(User.permissions),
        )
    )

    result = await session.exec(statement)

    return result.one_or_none()

async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:

    statement = select(User).where(
        User.email == email
    )

    result = await session.exec(statement)
    utilisateur_trouve = result.first()

    if utilisateur_trouve is None:
        return None

    return utilisateur_trouve
  

async def get_user_by_id(db: AsyncSession, user_uid: UUID) -> User:
    
    statement = select(User).where(
            User.uid == user_uid
        )
    
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    return user
  

async def affecter_role(
    session: AsyncSession,
    user_uid: UUID,
    role_uid: UUID,
    commit: bool = True,
) -> User:

    # Vérifier l'utilisateur
    user = await session.get(User, user_uid)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )

    # Vérifier le rôle
    role = await session.get(Role, role_uid)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rôle introuvable"
        )

    # Affecter le rôle
    user.role_uid = role.uid

    # add() n'est PAS awaitable
    session.add(user)

    if commit:
        await session.commit()
        await session.refresh(user)
    else:
        # Rend la modification disponible dans la transaction en cours sans
        # valider les autres opérations de l'appelant.
        await session.flush()

    # Recharger avec role + permissions
    user = await recharger_user(
        session,
        user.uid
    )

    return user



async def affecter_permissions(
    session: AsyncSession,
    user_uid: UUID,
    permissions: list[PermissionModel],
    commit: bool = True,
) -> User:

    # Récupérer l'utilisateur
    user = await session.get(User, user_uid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    for permission_model in permissions:

        permission_uid = permission_model.uid

        # Récupérer la permission
        permission = await session.get(
            Permission,
            permission_uid
        )

        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission {permission_uid} introuvable"
            )

        # Chercher si la permission est déjà affectée
        statement = select(UserPermission).where(
            UserPermission.user_uid == user_uid,
            UserPermission.permission_uid == permission_uid
        )

        result = await session.execute(statement)

        user_permission = result.scalar_one_or_none()

        # ==========================================
        # autorise = True → AJOUTER
        # ==========================================
        if permission_model.autorise:

            if not user_permission:
                session.add(
                    UserPermission(
                        user_uid=user_uid,
                        permission_uid=permission_uid
                    )
                )

        # ==========================================
        # autorise = False → SUPPRIMER
        # ==========================================
        else:

            if user_permission:
                await session.delete(user_permission)

    if commit:
        await session.commit()
    else:
        await session.flush()

    # Actualiser l'utilisateur
    user_recharge=await recharger_user(session, user.uid)

    return user_recharge


def _normalize_now_for(value):
    now = utcnow()
    if value is None:
        return now
    if getattr(value, "tzinfo", None) is None and getattr(now, "tzinfo", None) is not None:
        return now.replace(tzinfo=None)
    return now


def _is_expired(value) -> bool:
    if value is None:
        return False
    now = _normalize_now_for(value)
    return value <= now


def _is_future(value) -> bool:
    if value is None:
        return False
    now = _normalize_now_for(value)
    return value > now


def generate_session_id() -> str:
    return uuid4().hex


def create_auth_session(db: AsyncSession, user_id: int, session_id: str, refresh_token: str, expires_in_days: int) -> AuthSession:
    expires_at = utcnow() + timedelta(days=expires_in_days)
    session = AuthSession(
        uid=session_id,
        user_uid=user_id,
        refresh_token_hash=hash_token(refresh_token),
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_auth_session(db: AsyncSession, session_id: str) -> AuthSession | None:
    return db.query(AuthSession).filter(AuthSession.uid == session_id).first()


def validate_refresh_session(db: AsyncSession, session_id: str, refresh_token: str) -> AuthSession | None:
    session = get_auth_session(db, session_id)
    
    if session is None:
        return None
    
    if session.is_revoked or _is_expired(session.expires_at):
        return None

    if session.refresh_token_hash != hash_token(refresh_token):
        # Token reuse/tampering attempt: revoke all sessions for that user.
        revoke_all_auth_sessions(db, session.user_id)
        return None

    return session


def revoke_auth_session(db: AsyncSession, session_id: str, replaced_by_session_id: str | None = None) -> bool:
    session = get_auth_session(db, session_id)
    if session is None:
        return False

    session.is_revoked = True
    session.revoked_at = utcnow()
    if replaced_by_session_id:
        session.replaced_by_session_id = replaced_by_session_id
    db.commit()
    return True


def revoke_all_auth_sessions(db: AsyncSession, user_id: int) -> int:
    sessions = db.query(AuthSession).filter(
        AuthSession.user_uid == user_id,
        AuthSession.is_revoked.is_(False),
    ).all()
    now = utcnow()
    for session in sessions:
        session.is_revoked = True
        session.revoked_at = now
    db.commit()
    return len(sessions)


def rotate_refresh_session(
    db: AsyncSession,
    current_session: AuthSession,
    new_session_id: str,
    new_refresh_token: str,
) -> AuthSession:
    current_session.is_revoked = True
    current_session.revoked_at = utcnow()
    current_session.replaced_by_session_id = new_session_id

    new_session = AuthSession(
        id=new_session_id,
        user_id=current_session.user_uid,
        refresh_token_hash=hash_token(new_refresh_token),
        expires_at=utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


async def get_or_create_login_state(
    db: AsyncSession,
    user_id: UUID
) -> LoginAttemptState:

    statement = select(LoginAttemptState).where(
        LoginAttemptState.user_id == user_id
    )

    result = await db.exec(statement)

    state = result.first()

    if state is None:
        state = LoginAttemptState(
            user_id=user_id,
            failed_attempts=0
        )

        db.add(state)

        await db.commit()
        await db.refresh(state)

    return state


async def is_user_login_locked(db: AsyncSession, user_id: int) -> bool:
    state =await get_or_create_login_state(db, user_id)
    return _is_future(state.locked_until)


async def register_failed_login(db: AsyncSession, user_id: int) -> LoginAttemptState:
    state = await get_or_create_login_state(db, user_id)
    if _is_future(state.locked_until):
        return state

    state.failed_attempts += 1
    if state.failed_attempts >= settings.LOGIN_MAX_ATTEMPTS:
        state.failed_attempts = 0
        state.locked_until = utcnow() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)

    await db.commit()
    await db.refresh(state)
    return state


async def reset_failed_logins(db: AsyncSession, user_id: str) -> LoginAttemptState:
    state = get_or_create_login_state(db, user_id)
    state.failed_attempts = 0
    state.locked_until = None
    await db.commit()
    await db.refresh(state)
    return state


async def create_password_reset_token(db: AsyncSession, user_id: int) -> str:
    raw_token = generate_raw_token()
    token = PasswordResetToken(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )
    await db.add(token)
    await db.commit()
    return raw_token


async def consume_password_reset_token(
    db: AsyncSession,
    raw_token: str
) -> PasswordResetToken | None:

    hashed = hash_token(raw_token)

    statement = select(PasswordResetToken).where(
        PasswordResetToken.token_hash == hashed,
        PasswordResetToken.used_at.is_(None),
    )

    result = await db.exec(statement)

    token = result.first()

    if token is None:
        return None

    if _is_expired(token.expires_at):
        return None

    token.used_at = utcnow()

    await db.commit()
    await db.refresh(token)

    return token



async def assign_permission_to_user(
    session: AsyncSession,
    user_uid: UUID,
    permission_uid: UUID,
):

    # Vérifier l'utilisateur
    user = await session.get(User, user_uid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "user_uid",
                "message": "Utilisateur introuvable."
            }
        )

    # Vérifier la permission
    permission = await session.get(
        Permission,
        permission_uid
    )

    if not permission:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "permission_uid",
                "message": "Permission introuvable."
            }
        )

    # Vérifier si elle est déjà attribuée
    statement = select(UserPermission).where(
        UserPermission.user_uid == user_uid,
        UserPermission.permission_uid == permission_uid,
    )

    result = await session.exec(statement)

    existing = result.first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "field": "permission_uid",
                "message": (
                    "Cette permission est déjà "
                    "attribuée à cet utilisateur."
                )
            }
        )

    # Créer la liaison
    user_permission = UserPermission(
        user_uid=user_uid,
        permission_uid=permission_uid,
    )

    session.add(user_permission)

    await session.commit()
    await session.refresh(user_permission)

    return user_permission
