from datetime import timedelta 
from fastapi import Request, HTTPException, status
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from sqlalchemy.exc import SQLAlchemyError
from app.phototheque.schemas import (
    PhotothequeCreateModel,
    PhotothequeResponse,
    PhotothequeUpdateModel,     
    MessageResponse,
    MessageAllResponse,
)    
from app.db.models.phototheque import Phototheque

from app.core.exceptions_metier import RaiseException
from app.core.generer_code import CodeGenerator
from app.db.models.service import Service
from slugify import slugify
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class PhotothequeService:
    async def get_all_phototheques(
        self,
        session: AsyncSession
    ) -> list[PhotothequeResponse]:

        statement = (
            select(Phototheque)
            .options(
                selectinload(Phototheque.categorie),
                selectinload(Phototheque.cree_par),
                selectinload(Phototheque.modifie_par),
                selectinload(Phototheque.supprime_par)
            )
            .where(
                Phototheque.is_deleted.is_(False)
            )
            .order_by(
                desc(Phototheque.titre)
            )
        )

        result = await session.exec(statement)
        return result.all()


    async def create_phototheque(
        self,
        session: AsyncSession,
        phototheque_data: PhotothequeCreateModel,
        current_user_uid: UUID,
    ) -> Phototheque:

        phototheque = Phototheque(
            titre=phototheque_data.titre,
            code=CodeGenerator.generer_code_numerique(12),
            slug=slugify(phototheque_data.titre),

            description=phototheque_data.description,
            fichier_key=phototheque_data.object_key,

            lieu=phototheque_data.lieu,
            date_evenement=phototheque_data.date_evenement,

            statut=phototheque_data.statut,
            categorie_uid=phototheque_data.categorie_uid,

            date_publication=datetime.now(),
            cree_le=datetime.now(),
            modifie_le=datetime.now(),
            cree_par_uid=current_user_uid,
            modifie_par_uid=current_user_uid,

            is_deleted=False,
            supprime_le=None,
            supprime_par_uid=None,
        )

        try:
            session.add(phototheque)
            await session.commit()

        except SQLAlchemyError:
            await session.rollback()
            raise

        phototheque_rechargee = (
            await self.recharger_phototheque(
                session=session,
                phototheque_uid=phototheque.uid,
            )
        )

        return phototheque_rechargee
    

    async def update_phototheque(
        self,
        session: AsyncSession,
        phototheque: Phototheque,
        phototheque_data: PhotothequeUpdateModel,
        current_user_uid: UUID,
    ) -> Phototheque:

        donnees = phototheque_data.model_dump(
            exclude_unset=True,
        )

        for champ, valeur in donnees.items():
            setattr(phototheque, champ, valeur)

        phototheque.slug = slugify(phototheque.titre)
        phototheque.modifie_le = datetime.now()
        phototheque.modifie_par_uid = current_user_uid

        try:
            session.add(phototheque)
            await session.commit()
            await session.refresh(phototheque)

        except Exception:
            await session.rollback()
            raise

        phototheque_rechargee = (
            await self.recharger_phototheque(
                session=session,
                phototheque_uid=phototheque.uid,
            )
        )
        
        return phototheque_rechargee


    async def delete_phototheque(self, phototheque_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la phototheque existante
        phototheque_to_delete = await self.recharger_phototheque(
            session,
            phototheque_uid
        )
        if phototheque_to_delete is None:
            raise RaiseException(
                message="Phototheque non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "phototheque_uid": "Aucune phototheque ne correspond à cet identifiant.",
                },
            )
        
        phototheque_to_delete.is_deleted = True
        phototheque_to_delete.supprime_le = datetime.now(timezone.utc).replace(tzinfo=None)
        phototheque_to_delete.supprime_par_uid = current_user_uid

        session.add(phototheque_to_delete)
        await session.commit()
        
        # =====================================================
        #  Recharger complètement la phototheque
        # =====================================================
        phototheque_recharge = await self.recharger_phototheque(
            session,
            phototheque_to_delete.uid
        )
        
        return phototheque_recharge 
    

    async def get_phototheque(self, service_uid: UUID, session: AsyncSession):
        statement = (
            select(Service)
            .options(
                selectinload(Service.cree_par),
                selectinload(Service.modifie_par),
                selectinload(Service.supprime_par)
            )
            .where(Service.uid == service_uid)
        )

        result = await session.exec(statement) 
        service = result.first()
        
        return service


    async def restore_phototheque(self, phototheque_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la phototeque existante
        phototheque_to_restore = await self.recharger_phototheque(
            session,
            phototheque_uid
        )
                
        if phototheque_to_restore is None:
            raise RaiseException(
                message="phototheque non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "service_uid": "Aucune phototheque ne correspond à cet identifiant.",
                },
            )
       
        phototheque_to_restore.is_deleted = False
        phototheque_to_restore.supprime_le = None
        phototheque_to_restore.supprime_par_uid = None
        phototheque_to_restore.modifie_par_uid = current_user_uid
        phototheque_to_restore.modifie_le = datetime.now(timezone.utc).replace(tzinfo=None)
    
        session.add(phototheque_to_restore)
        await session.commit()
            
        # Charger les relations
        statement = (
            select(Phototheque)
            .where(Phototheque.uid == phototheque_uid)
            .options(
                selectinload(Phototheque.categorie), 
                selectinload(Phototheque.cree_par), 
                selectinload(Phototheque.modifie_par),
                selectinload(Phototheque.supprime_par)
            )
        )
        result = await session.exec(statement)
        phototheque = result.one_or_none()
        return phototheque 
    
      

    async def get_phototheque_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Phototheque]:
        statement = select(Phototheque).where(Phototheque.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_phototheque_by_uid(
        self,
        session: AsyncSession,
        phototheque_uid: UUID
    ) -> Optional[Phototheque]:
        statement = select(Phototheque).where(Phototheque.uid == phototheque_uid)
        result = await session.exec(statement)
        return result.first()


    async def recharger_phototheque(
        self,
        session: AsyncSession,
        phototheque_uid: UUID,
    ):
        statement = (
            select(Phototheque)
            .options(
                selectinload(Phototheque.categorie),
                selectinload(Phototheque.cree_par),
                selectinload(Phototheque.modifie_par),
                selectinload(Phototheque.supprime_par),
            )
            .where(
                Phototheque.uid == phototheque_uid
            )
        )

        result = await session.execute(statement)

        phototheque = result.scalar_one_or_none()

        return phototheque


    async def incrementer_nombre_vues(
        self,
        session: AsyncSession,
        service_uid: UUID,
    ) -> int | None:

        statement = (
            update(Service)
            .where(
                Service.uid == service_uid,
                Service.is_deleted.is_(False),
            )
            .values(
                nombre_vues=Service.nombre_vues + 1
            )
            .returning(Service.nombre_vues)
        )

        resultat = await session.execute(statement)
        nombre_vues = resultat.scalar_one_or_none()

        if nombre_vues is None:
            await session.rollback()
            return None

        await session.commit()

        return nombre_vues


    async def verifier_libelle_unique(
        self,
        session: AsyncSession,
        libelle: str,
        service_uid: UUID | None = None,
    ) -> bool:

        statement = select(Service).where(
            Service.libelle == libelle
        ).where(
            Service.is_deleted.is_(False)
        )

        # Pour UPDATE : ne pas comparer le communique avec lui-même
        if service_uid is not None:
            statement = statement.where(
                Service.uid != service_uid
            )

        result = await session.exec(statement)

        service = result.first()

        return service is None





