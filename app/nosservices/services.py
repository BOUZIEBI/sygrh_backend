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
from app.nosservices.schemas import (
    NosservicesCreateModel,
    NosservicesResponse,
    NosservicesUpdateModel,
    MessageResponse,
    MessageAllResponse,
)

from app.core.exceptions_metier import RaiseException
from app.core.generer_code import CodeGenerator
from app.db.models.service import Service
from slugify import slugify
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class NosservicesService:
    async def get_all_services(
        self,
        session: AsyncSession
    ) -> list[NosservicesResponse]:

        statement = (
            select(Service)
            .options(
                selectinload(Service.cree_par),
                selectinload(Service.modifie_par),
                selectinload(Service.supprime_par)
            )
            .where(
                Service.is_deleted.is_(False)
            )
            .order_by(
                desc(Service.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()


    async def create_service(
        self,
        session: AsyncSession,
        nosservice_data: NosservicesCreateModel,
        current_user_uid:UUID
    ):

        service = Service(
            libelle=nosservice_data.libelle,
            code=CodeGenerator.generer_code_numerique(12),
            slug=slugify(nosservice_data.libelle),
            description_courte=nosservice_data.description_courte,
            description=nosservice_data.description,
            fichier_key=nosservice_data.object_key,

            statut=nosservice_data.statut,
    
            cree_le=datetime.now(),
            modifie_le=datetime.now(),
            cree_par_uid=current_user_uid,
            modifie_par_uid=current_user_uid,

            is_deleted=False,
            supprime_le=None,
            supprime_par_uid=None,
        )

        try:
            session.add(service)
            await session.commit()

        except SQLAlchemyError:
            await session.rollback()
            raise

        service_recharge = (
            await self.recharger_service(
                session=session,
                service_uid=service.uid,
            )
        )

        return service_recharge
    
        

    async def update_service(
        self,
        session: AsyncSession,
        service: Service,
        service_data: NosservicesUpdateModel,
        current_user_uid:UUID
    ):
        
        donnees = service_data.model_dump(
            exclude_unset=True,
        )

        for champ, valeur in donnees.items():
            setattr(service, champ, valeur)

        service.slug = slugify(service.libelle)
        service.modifie_le = datetime.now()
        service.modifie_par_uid = current_user_uid

        try:
            session.add(service)
            await session.commit()
            await session.refresh(service)

        except Exception:
            await session.rollback()
            raise

        service_recharge = (
            await self.recharger_service(
                session=session,
                service_uid=service.uid,
            )
        )
        
        return service_recharge


    async def delete_service(self, service_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la service existante
        service_to_delete = await self.recharger_service(
            session,
            service_uid
        )
        if service_to_delete is None:
            raise RaiseException(
                message="Service non trouvé",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "service_uid": "Aucun service ne correspond à cet identifiant.",
                },
            )
        
        service_to_delete.is_deleted = True
        service_to_delete.supprime_le = datetime.now(timezone.utc).replace(tzinfo=None)
        service_to_delete.supprime_par_uid = current_user_uid

        session.add(service_to_delete)
        await session.commit()
        
        # =====================================================
        #  Recharger complètement le communique 
        # =====================================================
        service_recharge = await self.recharger_service(
            session,
            service_to_delete.uid
        )
        
        return service_recharge 
    

    async def get_service(self, service_uid: UUID, session: AsyncSession):
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


    async def restore_service(self, service_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        
        # Recharger la service existante
        service_to_restore = await self.recharger_service(
            session,
            service_uid
        )
                
        if service_to_restore is None:
            raise RaiseException(
                message="Service non trouvé",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "service_uid": "Aucun service ne correspond à cet identifiant.",
                },
            )
       
        service_to_restore.is_deleted = False
        service_to_restore.supprime_le = None
        service_to_restore.supprime_par_uid = None
        service_to_restore.modifie_par_uid = current_user_uid
        service_to_restore.modifie_le = datetime.now(timezone.utc).replace(tzinfo=None)
    
        session.add(service_to_restore)
        await session.commit()
            
        # Charger les relations
        statement = (
            select(Service)
            .where(Service.uid == service_uid)
            .options(
                selectinload(Service.cree_par), 
                selectinload(Service.modifie_par),
                selectinload(Service.supprime_par)
            )
        )
        result = await session.exec(statement)
        service = result.one_or_none()
        return service
    
      

    async def get_service_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Service]:
        statement = select(Service).where(Service.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_service_by_id(
        self,
        session: AsyncSession,
        service_uid: UUID
    ) -> Optional[Service]:
        statement = select(Service).where(Service.uid == service_uid)
        result = await session.exec(statement)
        return result.first()


    async def recharger_service(
        self,
        session: AsyncSession,
        service_uid: UUID,
    ):
        statement = (
            select(Service)
            .options(
                selectinload(Service.cree_par),
                selectinload(Service.modifie_par),
                selectinload(Service.supprime_par),
            )
            .where(
                Service.uid == service_uid
            )
        )

        result = await session.execute(statement)

        service = result.scalar_one_or_none()

        return service


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





