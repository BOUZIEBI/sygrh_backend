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
from app.structure.schemas import StructureCreateModel, StructureResponse, StructureUpdateModel
from app.core.exceptions_metier import RaiseException
from app.db.models.type_structure import TypeStructure
from app.db.models.structure import Structure
from slugify import slugify
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional



class StructureService:
    async def get_all_structures(
        self,
        session: AsyncSession
    ) -> list[Structure]:

        statement = (
            select(Structure)
            .options(
                selectinload(Structure.typestructure),
                selectinload(Structure.cree_par),
                selectinload(Structure.modifie_par),
                selectinload(Structure.supprime_par)
            )
            .where(
                Structure.is_deleted.is_(False)
            )
            .order_by(
                desc(Structure.libelle)
            )
        )

        result = await session.exec(statement)
        return result.all()


    async def create_structure(
        self,
        session: AsyncSession,
        structure_data: StructureCreateModel,
        current_user_uid:UUID
    ):

        libelle_existe = await self.verifier_libelle_unique(
            session,
            structure_data.libelle
        )

        if not libelle_existe:
            raise RaiseException(
                message="Cette structure existe déjà.",
                code=status.HTTP_302_FOUND
            )

        # Recharger le TypeStructure depuis la BDD
        typestructure = await self.recharger_typestructure(
            session,
            structure_data.type_structure_uid
        )

        # Vérifier que le TypeStructure existe
        if typestructure is None:
            raise ValueError(
                f"TypeStructure introuvable : "
                f"{structure_data.typestructure_uid}"
            )

        # Créer la Structure
        structure = Structure(
            uid=uuid4(),
            libelle=structure_data.libelle,
            code=structure_data.code,
            slug=slugify(structure_data.libelle),
            description=structure_data.description,
            personne_contact=structure_data.description,
            telephone_personne_contact=structure_data.telephone_personne_contact,
            anneecreation=structure_data.anneecreation,
            quartier=structure_data.quartier,
            adressecomplete=structure_data.adressecomplete,
            email=structure_data.email,
            telephone=structure_data.telephone,
            siteweb=structure_data.siteweb,
            cree_le = datetime.now(),
            type_structure_uid=typestructure.uid,
            cree_par_uid=current_user_uid,
            is_mode=True,
            is_deleted=False,
        )

        # Ajouter à la session
        session.add(structure)

        # Sauvegarder
        await session.commit()

        if structure :
            structure = await self.recharger_structure(
                session,
                structure.uid
            )

        return structure

    

    async def update_structure(
        self,
        session: AsyncSession,
        structure_data: StructureUpdateModel,
        current_user_uid:UUID
    ):
        # Recharger la structure existante
        structure = await self.recharger_structure(
            session,
            structure_data.uid
        )

        if structure is None:
            raise RaiseException(
                message="Cette structure n'existe déjà.",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "structure_uid":"Cet identifant ne corespond à aucune structure"
                }
            )

        libelle_existe = await self.verifier_libelle_unique(
            session,
            structure_data.libelle,
            structure.uid
        )

        if not libelle_existe:
            raise RaiseException(
                message="Cette structure existe déjà.",
                code=status.HTTP_302_FOUND
            ) 

        # Mettre à jour les champs simples
        if structure_data.libelle is not None:
            structure.libelle = structure_data.libelle
            structure.slug = slugify(structure_data.libelle)
            structure_data.description=structure_data.description 
            structure.personne_contact=structure_data.personne_contact
            structure.telephone_personne_contact=structure_data.telephone_personne_contact
            structure.anneecreation=structure_data.anneecreation
            structure.quartier=structure_data.quartier
            structure.adressecomplete=structure_data.adressecomplete
            structure.email=structure_data.email
            structure.telephone=structure_data.telephone
            structure.siteweb=structure_data.siteweb
            structure.is_mode = True
            structure.is_deleted = True
            structure.modifie_le = datetime.now()
            structure.modifie_par_uid=current_user_uid

        if structure_data.code is not None:
            structure.code = structure_data.code

        # Si le TypeStructure change,
        # recharger le nouveau TypeStructure
        if structure_data.type_structure_uid is not None:

            typestructure = await self.recharger_typestructure(
                session,
                structure_data.type_structure_uid
            )

        if typestructure is not None:
            structure.type_structure_uid = typestructure.uid
            

        # Sauvegarder
        session.add(structure)

        await session.commit()

        # Recharger avec TypeStructure
        structure_recharge = await self.recharger_structure(
            session,
            structure.uid
        )

        return structure_recharge


    async def delete_structure(self, structure_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        structure_to_delete = await self.get_structure_by_id( session, structure_uid)

        if structure_to_delete is None:
            raise RaiseException(
                message="Structure non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "structure_uid": "Aucune structure ne correspond à cet identifiant.",
                },
            )
        structure_to_delete.is_mode = False
        structure_to_delete.is_deleted = True
        structure_to_delete.supprime_le = datetime.now(timezone.utc)
        structure_to_delete.supprime_par_uid = current_user_uid

        session.add(structure_to_delete)
        await session.commit()
        
        # =====================================================
        #  Recharger complètement l'élève
        # =====================================================
        structure_recharge = await self.recharger_structure(
            session,
            structure_to_delete.uid
        )
        
        return structure_recharge 
    

    async def get_structure(self, structure_uid: UUID, session: AsyncSession):
        statement = (
            select(Structure)
            .options(
                selectinload(Structure.typestructure),
                selectinload(Structure.cree_par),
                selectinload(Structure.modifie_par),
                selectinload(Structure.modifie_par)
            )
            .where(Structure.uid == structure_uid)
        )

        result = await session.exec(statement)
        structure = result.first()
        return structure


    async def restore_structure(self, structure_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        structure_to_restore= await self.get_structure_by_id( session, structure_uid)
    
        if structure_to_restore is None:
            raise RaiseException(
                message="Structure non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "structure_uid": "Aucune structure ne correspond à cet identifiant.",
                },
            )
        structure_to_restore.is_mode = True
        structure_to_restore.is_deleted = False
        structure_to_restore.supprime_le = None
        structure_to_restore.supprime_par_uid = None
        structure_to_restore.modifie_par_uid = current_user_uid
        structure_to_restore.modifie_le = datetime.now(timezone.utc)
    
        session.add(structure_to_restore)
        await session.commit()
            
        # Charger les relations
        statement = (
            select(Structure)
            .where(Structure.uid == structure_uid)
            .options(
                selectinload(Structure.typestructure),
                selectinload(Structure.cree_par), 
                selectinload(Structure.modifie_par),
                selectinload(Structure.supprime_par)
            )
        )
        result = await session.exec(statement)
        structure = result.one_or_none()
        return structure
    
      

    async def get_structure_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Structure]:
        statement = select(Structure).where(Structure.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_structure_by_id(
        self,
        db: AsyncSession,
        structure_uid: UUID
    ) -> Optional[Structure]:
        statement = select(Structure).where(Structure.uid == structure_uid)
        result = await db.exec(statement)
        return result.first()



    async def recharger_typestructure(
        self,
        session: AsyncSession,
        typestructure_uid: UUID,
    ) -> Structure:

        statement = select(TypeStructure).where(
            TypeStructure.uid == typestructure_uid
        )

        result = await session.execute(statement)

        typestructure = result.scalar_one_or_none()

        return typestructure


    async def recharger_structure(
        self,
        session: AsyncSession,
        structure_uid: UUID,
    ):
        statement = (
            select(Structure)
            .options(
                selectinload(Structure.typestructure),
                selectinload(Structure.cree_par),
                selectinload(Structure.modifie_par),
                selectinload(Structure.supprime_par),
            )
            .where(
                Structure.uid == structure_uid
            )
        )

        result = await session.execute(statement)

        structure = result.scalar_one_or_none()

        return structure


    async def verifier_libelle_unique(
        self,
        session: AsyncSession,
        libelle: str,
        structure_uid: UUID | None = None,
    ) -> bool:

        statement = select(Structure).where(
            Structure.libelle == libelle
        )

        # Pour UPDATE : ne pas comparer la structure avec elle-même
        if structure_uid is not None:
            statement = statement.where(
                Structure.uid != structure_uid
            )

        result = await session.exec(statement)

        structure = result.first()

        return structure is None





