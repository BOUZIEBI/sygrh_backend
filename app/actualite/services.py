from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.actualite.schemas import ActualiteCreateModel, ActualiteResponse, ActualiteUpdateModel
from app.core.exceptions_metier import RaiseException
from app.core.generer_code import CodeGenerator
from app.db.models.actualite import Actualite
from slugify import slugify
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional

from app.core.redis import redis_client
from app.crypto.schemas import EncryptedResponse
from app.crypto.services import encrypt_response_for_react
from app.crypto.session_redis_store import SessionRedisStore

crypto_session_store = SessionRedisStore(redis_client)



class ActualiteService:
    async def get_all_actualites(
        self,
        session: AsyncSession
    ) -> list[Actualite]:

        statement = (
            select(Actualite)
            .options(
                selectinload(Actualite.categorie_actualite),
                selectinload(Actualite.cree_par),
                selectinload(Actualite.modifie_par),
                selectinload(Actualite.supprime_par)
            )
            .where(
                Actualite.is_deleted.is_(False)
            )
            .order_by(
                desc(Actualite.titre)
            )
        )

        result = await session.exec(statement)
        return result.all()


    async def create_actualite(
        self,
        session: AsyncSession,
        actualite_data: ActualiteCreateModel,
        current_user_uid:UUID
    ):

        # Créer la nouvelle actualite
        actualite = Actualite(
           
            titre=actualite_data.titre,
            code=CodeGenerator.generer_code_numerique(12), 
            slug=slugify(actualite_data.titre),
            resume=actualite_data.resume,
            contenu=actualite_data.contenu,
            fichier_key=actualite_data.object_key,

            # Statut communiqué : brouillon, publie ou archive
            statut=actualite_data.statut,
            est_a_la_une=actualite_data.est_a_la_une,
            date_publication=actualite_data.date_publication,

            categorie_uid=actualite_data.categorie_uid,
            auteur_uid=current_user_uid,
            
            # Statistiques
            nombre_vues = 0,
            nombre_telechargements = 0,

            # Traçabilité
            cree_le = datetime.now(),
            modifie_le = datetime.now(),

            cree_par_uid=current_user_uid,
            modifie_par_uid= current_user_uid,
            is_deleted=False,
        )

        # Ajouter à la session
        session.add(actualite)

        # Sauvegarder
        await session.commit()
        
        # Recharger communique
        actualite_recharge = await self.recharger_actualite(
            session,
            actualite.uid
        )

        return actualite_recharge
    
        
        

    async def update_actualite(
        self,
        session: AsyncSession,
        actualite: Actualite,
        actualite_data: ActualiteUpdateModel,
        current_user_uid:UUID
    ):
        donnees = actualite_data.model_dump(
            exclude_unset=True,
        )
        
        for champ, valeur in donnees.items():
            setattr(actualite, champ, valeur)
        
        actualite.slug = slugify(actualite.titre)
        actualite.modifie_le = datetime.now()
        actualite.modifie_par_uid = current_user_uid
        
        try:
            session.add(actualite)
            await session.commit()
            await session.refresh(actualite)
    
        except Exception:
            await session.rollback()
            raise
    
        actualite_recharge = (
            await self.recharger_actualite(
                session=session,
                actualite_uid=actualite.uid,
            )
        )
            
        return actualite_recharge 
            
        


    async def delete_actualite(self, actualite_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la actualite existante
        actualite_to_delete = await self.recharger_actualite(
            session,
            actualite_uid
        )
        if actualite_to_delete is None:
            raise RaiseException(
                message="Actualité non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "actualite_uid": "Aucune actualité ne correspond à cet identifiant.",
                },
            )
        
        actualite_to_delete.is_deleted = True
        actualite_to_delete.supprime_le = datetime.now(timezone.utc).replace(tzinfo=None)
        actualite_to_delete.supprime_par_uid = current_user_uid

        session.add(actualite_to_delete)
        await session.commit()
        
        # =====================================================
        #  Recharger complètement le communique 
        # =====================================================
        actualite_recharge = await self.recharger_actualite(
            session,
            actualite_to_delete.uid
        )
        
        return actualite_recharge 
    

    async def get_actualite(self, actualite_uid: UUID, session: AsyncSession):
        statement = (
            select(Actualite)
            .options(
                selectinload(Actualite.categorie_actualite),
                selectinload(Actualite.cree_par),
                selectinload(Actualite.modifie_par),
                selectinload(Actualite.supprime_par)
            )
            .where(Actualite.uid == actualite_uid)
        )

        result = await session.exec(statement) 
        actualite = result.first()
        
        nombre_vues = await self.incrementer_nombre_vues(
            session,
            actualite_uid,
        )
        
        return actualite


    async def restore_actualite(self, actualite_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la actualite existante
        actualite_to_restore = await self.recharger_actualite(
            session,
            actualite_uid
        )
                
        if actualite_to_restore is None:
            raise RaiseException(
                message="Actualité non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "actualite_uid": "Aucune actualité ne correspond à cet identifiant.",
                },
            )
       
        actualite_to_restore.is_deleted = False
        actualite_to_restore.supprime_le = None
        actualite_to_restore.supprime_par_uid = None
        actualite_to_restore.modifie_par_uid = current_user_uid
        actualite_to_restore.modifie_le = datetime.now(timezone.utc).replace(tzinfo=None)
    
        session.add(actualite_to_restore)
        await session.commit()
            
        # Charger les relations
        statement = (
            select(Actualite)
            .where(Actualite.uid == actualite_uid)
            .options(
                selectinload(Actualite.cree_par), 
                selectinload(Actualite.modifie_par),
                selectinload(Actualite.supprime_par)
            )
        )
        result = await session.exec(statement)
        actualite = result.one_or_none()
        return actualite
    
      

    async def get_actualite_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Actualite]:
        statement = select(Actualite).where(Actualite.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_actualite_by_uid(
        self,
        db: AsyncSession,
        actualite_uid: UUID
    ) -> Optional[Actualite]:
        statement = select(Actualite).where(Actualite.uid == actualite_uid)
        result = await db.exec(statement)
        return result.first()


    async def recharger_actualite(
        self,
        session: AsyncSession,
        actualite_uid: UUID,
    ):
        statement = (
            select(Actualite)
            .options(
                selectinload(Actualite.categorie_actualite),
                selectinload(Actualite.cree_par),
                selectinload(Actualite.modifie_par),
                selectinload(Actualite.supprime_par),
            )
            .where(
                Actualite.uid == actualite_uid
            )
        )

        result = await session.execute(statement)

        actualite = result.scalar_one_or_none()

        return actualite


    async def incrementer_nombre_vues(
        self,
        session: AsyncSession,
        actualite_uid: UUID,
    ) -> int | None:

        statement = (
            update(Actualite)
            .where(
                Actualite.uid == actualite_uid,
                Actualite.is_deleted.is_(False),
            )
            .values(
                nombre_vues=Actualite.nombre_vues + 1
            )
            .returning(Actualite.nombre_vues)
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
        actualite_uid: UUID | None = None,
    ) -> bool:

        statement = select(Actualite).where(
            Actualite.titre == titre
        ).where(
            Actualite.is_deleted.is_(False)
        )

        # Pour UPDATE : ne pas comparer le communique avec lui-même
        if actualite_uid is not None:
            statement = statement.where(
                Actualite.uid != actualite_uid
            )

        result = await session.exec(statement)

        actualite = result.first()

        return actualite is None
    
    
    async def encrypt_actualite_response(
        self,
        data: object,
        crypto_session_id: str,
    ) -> dict[str, str]:
    
        try:
            session_uid = UUID(crypto_session_id)
        except (TypeError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CRYPTO_SESSION",
                    "message": "L'identifiant de session cryptographique est invalide.",
                },
            ) from error

        client_public_key = await crypto_session_store.get_client_public_key(
            session_uid
        )
                
    
        if client_public_key is None:
            raise HTTPException(
                status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                detail={
                    "code": "CLIENT_PUBLIC_KEY_REQUIRED",
                    "message": (
                        "La clé publique RSA de React est absente "
                        "ou la session cryptographique a expiré."
                    ),
                },
            )

        try:
            
            data_encrypted=encrypt_response_for_react(
                data=data,
                client_public_key_pem=client_public_key,
            )
        
            return data_encrypted
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "RESPONSE_ENCRYPTION_FAILED",
                    "message": str(error),
                },
            ) from error
        
        






