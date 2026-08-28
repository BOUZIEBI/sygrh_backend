from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.db.models.login_attempt_state import LoginAttemptState
from app.db.models.password_reset_token import PasswordResetToken
from app.eleve.schemas import EleveCreateModel, EleveResponse, EleveUpdateModel
from app.core.exceptions_metier import RaiseException
from app.auth.services import affecter_permissions, affecter_role
from app.db.models.eleve import Eleve
from app.db.models.user import User
from app.core.security import hash_password
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class EleveService:
    async def get_all_eleves(self, session: AsyncSession):
        statement = (
            select(Eleve)
            .options(
                selectinload(Eleve.user)
                    .selectinload(User.permissions),

                selectinload(Eleve.cree_par)
                    .selectinload(User.permissions),

                selectinload(Eleve.modifie_par)
                    .selectinload(User.permissions),

                selectinload(Eleve.supprime_par)
                    .selectinload(User.permissions),
            )
        )

        result = await session.exec(statement)
        return result.all()
    


    async def create_eleve(
        self,
        db: AsyncSession,
        eleve_data: EleveCreateModel,
        current_user_id: UUID
    ) -> Eleve:

        # =====================================================
        # 1. Récupérer uniquement les champs envoyés
        # =====================================================

        payload = eleve_data.model_dump(
            exclude_unset=True,
            exclude={
                "permissions",
                "role_uid",
                "cree_le",
                "modifie_le",
                "supprime_le",
                "cree_par_uid",
                "modifie_par_uid",
                "supprime_par_uid",
                "is_active",
                "is_mode",
                "is_deleted",
            }
        )

        unsupported_fields = set(payload) - set(Eleve.model_fields)
        if unsupported_fields:
            raise RaiseException(
                message="Certains champs ne peuvent pas être enregistrés pour un élève",
                code=422,
                errors={field: "Champ non pris en charge." for field in unsupported_fields},
            )

        data = {
            field: value
            for field, value in payload.items()
            if field in Eleve.model_fields
        }

        # =====================================================
        # 2. Valeurs gérées automatiquement
        # =====================================================

        data["cree_par_uid"] = current_user_id
        data["cree_le"] = utcnow()

        # Valeurs par défaut
        data["is_deleted"] = False
        data["is_active"] = True
        data["is_mode"] = True

        if (
            eleve_data.user_uid is None
            and (
                eleve_data.role_uid is not None
                or "permissions" in eleve_data.model_fields_set
            )
        ):
            raise RaiseException(
                message="Un utilisateur est requis pour affecter un rôle ou des permissions",
                code=422,
            )

        # La création de l'élève et les droits de son utilisateur forment une
        # seule opération : en cas d'erreur, aucun élève incomplet ne subsiste.
        try:
            user = None
            if eleve_data.user_uid is not None:
                user = await db.get(User, eleve_data.user_uid)
                if not user:
                    raise RaiseException(
                        message="Utilisateur de l'élève introuvable",
                        code=404,
                    )

            eleve = Eleve(**data)
            db.add(eleve)
            await db.flush()

            if eleve.user_uid is not None:
                if eleve_data.role_uid is not None:
                    await affecter_role(
                        session=db,
                        user_uid=user.uid,
                        role_uid=eleve_data.role_uid,
                        commit=False,
                    )

                if "permissions" in eleve_data.model_fields_set:
                    await affecter_permissions(
                        session=db,
                        user_uid=user.uid,
                        permissions=eleve_data.permissions,
                        commit=False,
                    )

            await db.commit()
            await db.refresh(eleve)
        except Exception:
            await db.rollback()
            raise

        # =====================================================
        # 7. Recharger complètement l'élève
        #    avec User + rôle + permissions
        # =====================================================

        eleve = await self.recharger_eleve(
            db,
            eleve.uid
        )

        return eleve


        

    async def get_eleve(self, eleve_uid: UUID, session: AsyncSession):

        statement = (
            select(Eleve)
            .where(Eleve.uid == eleve_uid)
            .options(
                selectinload(Eleve.user).selectinload(User.permissions),
                selectinload(Eleve.modifie_par).selectinload(User.permissions),
            )
        )

        result = await session.exec(statement)
        eleve = result.first()
        return eleve


    async def update_eleve(
        self,
        session: AsyncSession,
        eleve_data: EleveUpdateModel,
        current_user_uid: UUID
    ) -> Eleve:

        # =====================================================
        # 1. Récupérer l'élève avec les relations nécessaires
        # =====================================================

        statement = (
            select(Eleve)
            .options(
                selectinload(Eleve.user)
                    .selectinload(User.role),

                selectinload(Eleve.user)
                    .selectinload(User.permissions),

                selectinload(Eleve.cree_par)
                    .selectinload(User.role),

                selectinload(Eleve.cree_par)
                    .selectinload(User.permissions),

                selectinload(Eleve.modifie_par)
                    .selectinload(User.role),

                selectinload(Eleve.modifie_par)
                    .selectinload(User.permissions),

                selectinload(Eleve.supprime_par)
                    .selectinload(User.role),

                selectinload(Eleve.supprime_par)
                    .selectinload(User.permissions),
            )
            .where(Eleve.uid == eleve_data.uid)
        )

        result = await session.exec(statement)
        eleve = result.one_or_none()

        # =====================================================
        # Vérifier l'existence
        # =====================================================

        if not eleve:
            raise RaiseException(
                message="Élève non trouvé",
                code=404,
                errors={
                    "eleve_uid": "Aucun élève ne correspond à cet identifiant."
                },
            )

        # =====================================================
        # Récupérer uniquement les champs envoyés
        # =====================================================

        data = eleve_data.model_dump(
            exclude_unset=True,
            exclude={
                "permissions",
                "role_uid"
            }
        )

        # =====================================================
        # 4. Modifier les champs de l'élève
        # =====================================================

        for field, value in data.items():
            setattr(eleve, field, value)

        eleve.modifie_le = utcnow()
        eleve.modifie_par_uid = current_user_uid

        session.add(eleve)

        await session.commit()

        # =====================================================
        # 5. Récupérer le User
        # =====================================================

        if eleve.user_uid is not None:

            user = await session.get(User, eleve.user_uid)

            if not user:
                raise RaiseException(
                    message="Utilisateur de l'élève introuvable",
                    code=404
                )

            # =================================================
            # Modifier le rôle
            # =================================================

            if eleve_data.role_uid is not None:

                await affecter_role(
                    session=session,
                    user_uid=user.uid,
                    role_uid=eleve_data.role_uid
                )

            # =================================================
            #  Modifier les permissions
            # =================================================

            if "permissions" in eleve_data.model_fields_set:

                await affecter_permissions(
                    session=session,
                    user_uid=user.uid,
                    permissions=eleve_data.permissions
                )

        # =====================================================
        #  Recharger complètement l'élève
        # =====================================================
        eleve = await self.recharger_eleve(
            session,
            eleve.uid
        )

        return eleve



    async def delete_eleve(self, eleve_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        eleve_to_delete = await self.get_eleve_by_id( session, eleve_uid)

        if eleve_to_delete is None:
            raise RaiseException(
                message="Élève non trouvé",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "eleve_uid": "Aucun élève ne correspond à cet identifiant.",
                },
            )
        
        eleve_to_delete.is_deleted = True
        eleve_to_delete.supprime_le = datetime.now(timezone.utc)
        eleve_to_delete.supprime_par_uid = current_user_uid

        session.add(eleve_to_delete)
        await session.commit()
        
        # =====================================================
        #  Recharger complètement l'élève
        # =====================================================
        eleve_recharge = await self.recharger_eleve(
            session,
            eleve_to_delete.uid
        )
        
        return eleve_recharge

    async def restore_eleve(self, eleve_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        eleve_to_restore= await self.get_eleve_by_id( session, eleve_uid)
    
        if eleve_to_restore is None:
            raise RaiseException(
                message="Élève non trouvé",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "eleve_uid": "Aucun élève ne correspond à cet identifiant.",
                },
            )
            
        eleve_to_restore.is_deleted = False
        eleve_to_restore.supprime_le = None
        eleve_to_restore.supprime_par_uid = None
        eleve_to_restore.modifie_par_uid = current_user_uid
        eleve_to_restore.modifie_le = datetime.now(timezone.utc)
    
        session.add(eleve_to_restore)
        await session.commit()
            
        # Charger les relations
        statement = (
            select(Eleve)
            .where(Eleve.uid == eleve_uid)
            .options(
                selectinload(Eleve.user),
                selectinload(Eleve.cree_par), 
                selectinload(Eleve.modifie_par),
                selectinload(Eleve.supprime_par),
                selectinload(Eleve.genre),
            )
        )
        result = await session.exec(statement)
        eleve = result.one_or_none()
        return eleve
      

    async def get_eleve_by_matricule(
        self,
        db: AsyncSession,
        matricule: str
    ) -> Optional[Eleve]:
        statement = select(Eleve).where(Eleve.matricule == matricule)
        result = await db.exec(statement)
        return result.first()
    

    async def get_eleve_by_id(
        self,
        db: AsyncSession,
        eleve_uid: UUID
    ) -> Optional[Eleve]:
        statement = select(Eleve).where(Eleve.uid == eleve_uid)
        result = await db.exec(statement)
        return result.first()


    async def recharger_eleve(
        self,
        db: AsyncSession,
        eleve_uid: UUID,
    ) -> Eleve | None:

        statement = (
            select(Eleve)
            .where(Eleve.uid == eleve_uid)
            .options(

                # user
                selectinload(Eleve.user).selectinload(User.role),
                selectinload(Eleve.user).selectinload(User.permissions),

                # cree_par
                selectinload(Eleve.cree_par).selectinload(User.role),
                selectinload(Eleve.cree_par).selectinload(User.permissions),

                # modifie_par
                selectinload(Eleve.modifie_par).selectinload(User.role),
                selectinload(Eleve.modifie_par).selectinload(User.permissions),

                # supprime_par
                selectinload(Eleve.supprime_par).selectinload(User.role),
                selectinload(Eleve.supprime_par).selectinload(User.permissions),
            )
        )

        result = await db.exec(statement)

        return result.one_or_none()


