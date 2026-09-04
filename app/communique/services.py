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
from app.communique.schemas import CommuniqueCreateModel, CommuniqueResponse, CommuniqueUpdateModel 
from app.core.exceptions_metier import RaiseException
from app.core.generer_code import CodeGenerator
from app.db.models.communique import Communique
from slugify import slugify
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class CommuniqueService:
    async def get_all_communiques(
        self,
        session: AsyncSession
    ) -> list[Communique]:

        statement = (
            select(Communique)
            .options(
                selectinload(Communique.cree_par),
                selectinload(Communique.modifie_par),
                selectinload(Communique.supprime_par)
            )
            .where(
                Communique.is_deleted.is_(False)
            )
            .order_by(
                desc(Communique.titre)
            )
        )

        result = await session.exec(statement)
        return result.all()


    async def create_communique(
        self,
        session: AsyncSession,
        communique_data: CommuniqueCreateModel,
        current_user_uid:UUID
    ):

        titre_existe = await self.verifier_titre_unique(
            session,
            communique_data.titre
        )

        if not titre_existe:
            raise RaiseException(
                message="Ce communiqué existe déjà.",
                code=status.HTTP_302_FOUND
            )

        # Créer le nouveau Communiqué
        communique = Communique(
           
            titre=communique_data.titre,
            code=CodeGenerator.generer_code_numerique(12), 
            slug=slugify(communique_data.titre),
            resume=communique_data.resume,
            contenu=communique_data.contenu,
            reference=communique_data.reference,

            image_url=None,
            fichier_key=communique_data.object_key,

            # Statut communiqué : brouillon, publie ou archive
            statut=communique_data.statut,
            est_epingle=True,
            date_publication=datetime.now(),
            date_expiration=communique_data.date_expiration,


            auteur_uid=current_user_uid,
            
            # Statistiques
            nombre_vues = 0,
            nombre_telechargements = 0,

            # Traçabilité
            cree_le = datetime.now(),
            modifie_le = datetime.now(),

            cree_par_uid=current_user_uid,
            modifie_par_uid= current_user_uid,
            est_deleted=False,
            is_deleted=False,
        )

        # Ajouter à la session
        session.add(communique)

        # Sauvegarder
        await session.commit()
        
        # Recharger communique
        communique_recharge = await self.recharger_communique(
            session,
            communique.uid
        )

        return communique_recharge
    

    async def update_communique(
        self,
        session: AsyncSession,
        communique: Communique,
        communique_data: CommuniqueUpdateModel,
        current_user_uid:UUID
    ):
        donnees = communique_data.model_dump(
            exclude_unset=True,
        )
        
        for champ, valeur in donnees.items():
            setattr(communique, champ, valeur)
        
        communique.slug = slugify(communique.titre)
        communique.modifie_le = datetime.now()
        communique.modifie_par_uid = current_user_uid
        
        try:
            session.add(communique)
            await session.commit()
            await session.refresh(communique)
    
        except Exception:
            await session.rollback()
            raise
    
        communique_recharge = (
            await self.recharger_communique(
                session=session,
                communique_uid=communique.uid,
            )
        )
            
        return communique_recharge 
    
    
        
    async def delete_communique(self, communique_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la communique existante
        communique_to_delete = await self.recharger_communique(
            session,
            communique_uid
        )
        if communique_to_delete is None:
            raise RaiseException(
                message="Communique non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "communique_uid": "Aucune communique ne correspond à cet identifiant.",
                },
            )
        
        communique_to_delete.is_deleted = True
        communique_to_delete.supprime_le = datetime.now(timezone.utc).replace(tzinfo=None)
        communique_to_delete.supprime_par_uid = current_user_uid

        session.add(communique_to_delete)
        await session.commit()
        
        # =====================================================
        #  Recharger complètement le communique 
        # =====================================================
        communique_recharge = await self.recharger_communique(
            session,
            communique_to_delete.uid
        )
        
        return communique_recharge 
    

    async def get_communique(self, communique_uid: UUID, session: AsyncSession):
        statement = (
            select(Communique)
            .options(
                selectinload(Communique.cree_par),
                selectinload(Communique.modifie_par),
                selectinload(Communique.supprime_par)
            )
            .where(Communique.uid == communique_uid)
        )

        result = await session.exec(statement) 
        communique = result.first()
        
        nombre_vues = await self.incrementer_nombre_vues(
            session,
            communique_uid,
        )
        
        return communique


    async def restore_communique(self, communique_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la communique existante
        communique_to_restore = await self.recharger_communique(
            session,
            communique_uid
        )
                
        if communique_to_restore is None:
            raise RaiseException(
                message="Communique non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "communique_uid": "Aucune communique ne correspond à cet identifiant.",
                },
            )
       
        communique_to_restore.is_deleted = False
        communique_to_restore.supprime_le = None
        communique_to_restore.supprime_par_uid = None
        communique_to_restore.modifie_par_uid = current_user_uid
        communique_to_restore.modifie_le = datetime.now(timezone.utc).replace(tzinfo=None)
    
        session.add(communique_to_restore)
        await session.commit()
            
        # Charger les relations
        statement = (
            select(Communique)
            .where(Communique.uid == communique_uid)
            .options(
                selectinload(Communique.cree_par), 
                selectinload(Communique.modifie_par),
                selectinload(Communique.supprime_par)
            )
        )
        result = await session.exec(statement)
        communique = result.one_or_none()
        return communique
    
      

    async def get_communique_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Communique]:
        statement = select(Communique).where(Communique.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_communique_by_uid(
        self,
        db: AsyncSession,
        communique_uid: UUID
    ) -> Optional[Communique]:
        statement = select(Communique).where(Communique.uid == communique_uid)
        result = await db.exec(statement)
        return result.first()


    async def recharger_communique(
        self,
        session: AsyncSession,
        communique_uid: UUID,
    ):
        statement = (
            select(Communique)
            .options(
                selectinload(Communique.cree_par),
                selectinload(Communique.modifie_par),
                selectinload(Communique.supprime_par),
            )
            .where(
                Communique.uid == communique_uid
            )
        )

        result = await session.execute(statement)

        communique = result.scalar_one_or_none()

        return communique


    async def incrementer_nombre_vues(
        self,
        session: AsyncSession,
        communique_uid: UUID,
    ) -> int | None:

        statement = (
            update(Communique)
            .where(
                Communique.uid == communique_uid,
                Communique.is_deleted.is_(False),
            )
            .values(
                nombre_vues=Communique.nombre_vues + 1
            )
            .returning(Communique.nombre_vues)
        )

        resultat = await session.execute(statement)
        nombre_vues = resultat.scalar_one_or_none()

        if nombre_vues is None:
            await session.rollback()
            return None

        await session.commit()

        return nombre_vues


    async def verifier_titre_unique(
        self,
        session: AsyncSession,
        titre: str,
        communique_uid: UUID | None = None,
    ) -> bool:

        statement = select(Communique).where(
            Communique.titre == titre
        ).where(
            Communique.is_deleted.is_(False)
        )

        # Pour UPDATE : ne pas comparer le communique avec lui-même
        if communique_uid is not None:
            statement = statement.where(
                Communique.uid != communique_uid
            )

        result = await session.exec(statement)

        communique = result.first()

        return communique is None





