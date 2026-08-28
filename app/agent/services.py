from datetime import timedelta 
from fastapi import Request, HTTPException, status
import secrets
from uuid import uuid4
from app.core.config import settings
from datetime import date, datetime, UTC, timezone
from sqlmodel import desc, select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.auth_session import AuthSession, generate_raw_token, hash_token, utcnow
from app.auth.schemas import UserCreate
from app.db.models.login_attempt_state import LoginAttemptState
from app.db.models.password_reset_token import PasswordResetToken
from app.agent.schemas import AgentCreateModel, AgentUpdateModel,ConjointCreateModel ,SituationAdministrativeCreateModel,AgentResponse
from app.core.exceptions_metier import RaiseException
from app.db.models.nature_acte_nomination_fonctionactuelle import NatureActeNominationFonctionactuelle
from app.db.models.agent import Agent
from app.db.models.nature_piece_identite import NaturePieceidentite
from app.db.models.genre import Genre
from app.db.models.type_agent import TypeAgent
from app.db.models.nationalite import Nationalite
from app.db.models.type_recrutement import TypeRecrutement
from app.db.models.structure import Structure
from app.db.models.fonction import Fonction
from app.db.models.situation_matrimoniale import SituationMatrimoniale
from app.db.models.specialite import Specialite
from app.db.models.situation_administrative import SituationAdministrative
from app.db.models.emploi import Emploi
from app.db.models.grade import Grade
from app.db.models.statut import Statut
from app.db.models.validation_fiche import ValidationFiche
from app.db.models.statut_situation_administrative import StatutSituationAdministrative
from app.db.models.echelon import Echelon
from app.db.models.classe_situation_administrative import ClasseSituationAdministrative
from app.db.models.nature_acte_nomination_dans_emploi import NatureActeNominationDansEmploi
from app.db.models.nature_acte_nomination_fonctionactuelle import NatureActeNominationFonctionactuelle
from app.db.models.diplome import Diplome
from app.db.models.position_administrative import PositionAdministrative
from app.db.models.positionmilitaire import PositionMilitaire
from app.db.models.fonction_actuelle import FonctionActuelle
from app.db.models.conjoint import Conjoint
from app.db.models.user import User
from app.auth.services import create_user
from slugify import slugify
from sqlalchemy.orm import selectinload
from typing import TYPE_CHECKING, Optional
from app.core.security import hash_password
from app.auth.services import affecter_role, affecter_permissions



class AgentService:
    async def get_all_agents(
        self,
        session: AsyncSession
    ) -> list[Agent]:

        # Récupérer tous les UID des agents
        statement = (
            select(Agent.uid)
            .where(
                Agent.is_deleted == False
            )
            .order_by(
                desc(Agent.nom)
            )
        )

        result = await session.execute(statement)

        agent_uids = result.scalars().all()

        # Recharger chaque agent avec toutes ses relations
        agents = []

        for agent_uid in agent_uids:

            agent = await self.recharger_agent(
                session,
                agent_uid
            )

            if agent is not None:
                agents.append(agent)

        return agents


    async def create_agent(
        self,
        session: AsyncSession,
        agent_data: AgentCreateModel,
        current_user_uid:UUID
    ):

        matricule_existe = await self.verifier_matricule_unique(
            session,
            agent_data.matricule
        )

        if not matricule_existe:
            raise RaiseException(
                message="Cet agent existe déjà.",
                code=status.HTTP_302_FOUND
            )
        
        nature_acte_nomination_fonctionactuelle_uid=None
        if agent_data.nature_acte_nomination_dans_fonctionactuelle_uid is not None:
            # Recharger le nature acte de nomination fonction actuelle depuis la BDD
            nature_acte_nomination_fonctionactuelle = await self.recharger_nature_acte_nomination_fonctionactuelle(
                session,
                agent_data.nature_acte_nomination_dans_fonctionactuelle_uid
            )
            nature_acte_nomination_fonctionactuelle_uid = nature_acte_nomination_fonctionactuelle.uid if nature_acte_nomination_fonctionactuelle else None

        nature_piece_identite_uid=None
        if agent_data.nature_piece_identite_uid is not None:
            # Recharger la nature piece identite depuis la BDD
            nature_piece_identite = await self.recharger_nature_piece_identite(
                session,
                agent_data.nature_piece_identite_uid
            )
            nature_piece_identite_uid = nature_piece_identite.uid if nature_piece_identite else None

        genre_uid=None
        if agent_data.genre_uid is not None:
            # Recharger le genre depuis la BDD
            genre = await self.recharger_genre(
                session,
                agent_data.genre_uid
            )
            genre_uid = genre.uid if genre else None
            
        type_agent_uid=None
        if agent_data.type_agent_uid is not None:
            # Recharger le type agent depuis la BDD
            type_agent = await self.recharger_type_agent(
                session,
                agent_data.type_agent_uid
            )
            type_agent_uid=type_agent.uid if type_agent else None

        nationalite_uid=None
        if agent_data.nationalite_uid is not None:
            # Recharger la nationalite depuis la BDD
            nationalite = await self.recharger_nationalite(
                session,
                agent_data.nationalite_uid
            )
            nationalite_uid=nationalite.uid if nationalite else None

        structure_uid=None
        if agent_data.structure_uid is not None:
            # Recharger la structure depuis la BDD
            structure = await self.recharger_structure(
                session,
                agent_data.structure_uid
            )
            structure_uid=structure.uid if structure else None

        fonction_uid=None
        if agent_data.fonction_uid is not None:
            # Recharger la fonction depuis la BDD
            fonction = await self.recharger_fonction(
                session,
                agent_data.fonction_uid
            )
            fonction_uid=fonction.uid if fonction else None

        situation_matrimoniale_uid=None
        if agent_data.situation_matrimoniale_uid is not None:
            #Recharger la situation matrimoniale depuis la BD
            situation_matrimoniale=await self.recharger_situation_matrimoniale(
                session,
                agent_data.situation_matrimoniale_uid
            )
            situation_matrimoniale_uid= situation_matrimoniale.uid if situation_matrimoniale else None

        specialite_uid=None
        if agent_data.specialite_uid is not None:
            #Recharger la specialite depuis la BD
            specialite=await self.recharger_specialite(
                session,
                agent_data.specialite_uid
            )
            specialite_uid=specialite.uid if specialite else None


        conjoint_uid=None
        if agent_data.nom_conjoint is not None and agent_data.prenoms_conjoint is not None :
            conjoint_data={
                "nom": agent_data.nom_conjoint,
                "prenoms": agent_data.prenoms_conjoint,
                "matricule_cnps": agent_data.matricule_cnps_conjoint,
                "profession" : agent_data.profession_conjoint
            }


        situation_administrative_uid = None
        if agent_data.statut_situation_administrative_uid is not None:

            situation_administrative_data = SituationAdministrativeCreateModel(
                numero_acte_nomination_dans_emploi=(
                    agent_data.numero_acte_nomination_dans_emploi
                ),

                date_signature_acte_nomination_dans_emploi=(
                    agent_data.date_signature_acte_nomination_dans_emploi
                ),

                date_premiere_prise_service_fonction_publique=(
                    agent_data.date_premiere_prise_service_fonction_publique
                ),

                date_depart_retraite=(
                    agent_data.date_depart_retraite
                ),

                date_radiation=(
                    agent_data.date_radiation
                ),

                date_depart_mouvement=(
                    agent_data.date_depart_mouvement
                ),

                date_retour_mouvement=(
                    agent_data.date_retour_mouvement
                ),

                adresse_bureau=(
                    agent_data.adresse_bureau
                ),

                adresse_personnelle=(
                    agent_data.adresse_personnelle
                ),

                telephone_bureau=(
                    agent_data.telephone_bureau
                ),

                telephone_domicile=(
                    agent_data.telephone_domicile
                ),

                numero_telephone_1=(
                    agent_data.numero_telephone_1
                ),

                numero_telephone_2=(
                    agent_data.numero_telephone_2
                ),

                email_institutionnel=(
                    agent_data.email_institutionnel
                ),

                designation_poste=(
                    agent_data.designation_poste
                ),

                numero_acte_nomination_fonctionactuelle=(
                    agent_data.numero_acte_nomination_fonctionactuelle
                ),

                date_signature_acte_nomination_fonctionactuelle=(
                    agent_data.date_signature_acte_nomination_fonctionactuelle
                ),

                is_equivqlence=(
                    agent_data.is_equivqlence
                ),

                statut_situation_administrative_uid=(
                    agent_data.statut_situation_administrative_uid
                ),

                emploi_uid=agent_data.emploi_uid,

                classe_situation_administrative_uid=(
                    agent_data.classe_situation_administrative_uid
                ),

                echelon_uid=agent_data.echelon_uid,

                nature_acte_nomination_dans_emploi_uid=(
                    agent_data.nature_acte_nomination_dans_emploi_uid
                ),

                nature_acte_nomination_dans_fonctionactuelle_uid=(
                    agent_data.nature_acte_nomination_dans_fonctionactuelle_uid
                ),

                diplome_uid=agent_data.diplome_uid,

                position_administrative_uid=(
                    agent_data.position_administrative_uid
                ),

                position_militaire_uid=(
                    agent_data.position_militaire_uid
                ),

                fonction_actuelle_uid=(
                    agent_data.fonction_actuelle_uid
                ),
            )

            # Créer la situation administrative
            situation_administrative = (
                await self.creer_situation_administrative(
                    session,
                    situation_administrative_data
                )
            )

            # Récupérer son UID
            situation_administrative_uid = (
                situation_administrative.uid
                if situation_administrative
                else None
            )

        emploi_uid=None
        if agent_data.emploi_uid is not None:
            #Recharger l'emploi depuis la BD
            emploi=await self.recharger_emploi(
                session,
                agent_data.emploi_uid
            )
            emploi_uid=emploi.uid if emploi else None

        grade_uid=None
        if agent_data.grade_uid is not None:
            #Recharger le grade depuis la BD
            grade=await self.recharger_grade(
                session,
                agent_data.grade_uid
            )
            grade_uid=grade.uid if grade else None

        statut_uid=None
        if agent_data.statut_uid is not None:
            #Recharger le statut depuis la BD
            statut=await self.recharger_statut(
                session,
                agent_data.statut_uid
            )
            statut_uid=statut.uid if statut else None

        validation_fiche_uid=None
        if agent_data.validation_fiche_uid is not None:
            #Recharger la validation de fiche depuis la BD
            validation_fiche=await self.recharger_validation_fiche(
                session,
                agent_data.validation_fiche_uid
            )
            validation_fiche_uid=validation_fiche.uid if validation_fiche else None
                
        
        #Creer User
        user_data = UserCreate(
            email= agent_data.email_personnel,
            role_uid=agent_data.role_uid,
            permissions=agent_data.permissions,
            password= '123456',
            #password= hash_password(
            #    ''.join(secrets.choice("0123456789")for _ in range(12))
            #), 

        )
        user_cree= await create_user(
            session,
            user_data
        )

        # Créer l'agent
        agent = Agent(
            uid=uuid4(),
            nom=agent_data.nom,
            prenoms=agent_data.prenoms,
            matricule=agent_data.matricule,
            code = ''.join(secrets.choice("0123456789")for _ in range(12)),
            date_naissance = datetime.now(),
            lieu_naissance = agent_data.lieu_naissance,
            telephone_principal = agent_data.telephone_principal,
            telephone_secondaire = agent_data.telephone_secondaire,
            email_professionnel = agent_data.email_professionnel, 
            email_personnel = agent_data.email_personnel,
            quartier = agent_data.quartier,
            nom_jeune_fille = agent_data.nom_jeune_fille,
            lieu_habitation = agent_data.lieu_habitation,
            date_recrutement = agent_data.date_recrutement,
            date_depart = agent_data.date_depart,
            nombre_enfant = agent_data.nombre_enfant,
            nom_prenoms_pere = agent_data.nom_prenoms_pere,
            nom_prenoms_mere = agent_data.nom_prenoms_mere,
            numero_piece_identite = agent_data.numero_piece_identite,
            cree_le = datetime.now(),
            modifie_le = datetime.now(),
            preinscrit_le = None ,
            etat_handicap = agent_data.etat_handicap,
            is_mode = True,
            is_deleted = False,
            est_preinscrit= False,
            supprime_le = None,
            date_premiere_prise_service_dans_structure = agent_data.date_premiere_prise_service_dans_structure,
            date_premiere_prise_service_fonction_publique = agent_data.date_premiere_prise_service_fonction_publique,

            conjoint_uid = None,
            cree_par_uid = current_user_uid,
            modifie_par_uid = current_user_uid,
            supprime_par_uid= None,
            nature_piece_identite_uid = nature_piece_identite_uid,
            genre_uid = genre_uid,
            nature_acte_nomination_fonctionactuelle_uid = nature_acte_nomination_fonctionactuelle_uid,
            type_agent_uid =  type_agent_uid,
            user_uid = user_cree.uid,
            nationalite_uid = nationalite_uid,
            structure_uid = structure_uid,
            fonction_uid = fonction_uid,
            situation_matrimoniale_uid = situation_matrimoniale_uid,
            specialite_uid = specialite_uid,
            situation_administrative_uid = situation_administrative_uid,
            emploi_uid = emploi_uid,
            grade_uid = grade_uid,
            statut_uid= statut_uid,
            validation_fiche_uid = validation_fiche_uid
        )

        # Ajouter à la session
        session.add(agent)

        # Sauvegarder
        await session.commit()

        agent_recharge=None
        if agent :
            agent_recharge = await self.recharger_agent(
                session,
                agent.uid
            )

        return agent_recharge

    
    async def update_agent(
        self,
        session: AsyncSession,
        agent_uid: UUID,
        agent_data: AgentUpdateModel,
        current_user_uid: UUID
    ) -> Agent:

        # =====================================================
        # 1. Recharger l'agent
        # =====================================================
        agent = await self.recharger_agent(
            session,
            agent_uid
        )

        if agent is None:
            raise RaiseException(
                message="Cet agent existe déjà.",
                code=status.HTTP_302_FOUND
            )

        # =====================================================
        # 2. Modifier les informations de l'agent
        # =====================================================

        agent.nom = agent_data.nom
        agent.prenoms = agent_data.prenoms
        agent.matricule = agent_data.matricule
        agent.date_naissance = agent_data.date_naissance
        agent.lieu_naissance = agent_data.lieu_naissance
        agent.telephone_principal = agent_data.telephone_principal
        agent.telephone_secondaire = agent_data.telephone_secondaire
        agent.email_professionnel = agent_data.email_professionnel
        agent.email_personnel = agent_data.email_personnel
        agent.quartier = agent_data.quartier
        agent.nom_jeune_fille = agent_data.nom_jeune_fille
        agent.lieu_habitation = agent_data.lieu_habitation
        agent.date_recrutement = agent_data.date_recrutement
        agent.date_depart = agent_data.date_depart
        agent.nombre_enfant = agent_data.nombre_enfant
        agent.nom_prenoms_pere = agent_data.nom_prenoms_pere
        agent.nom_prenoms_mere = agent_data.nom_prenoms_mere
        agent.numero_piece_identite = agent_data.numero_piece_identite
        agent.etat_handicap = agent_data.etat_handicap

        # =====================================================
        # 3. Clés étrangères de l'agent
        # =====================================================

        agent.nature_piece_identite_uid = (
            agent_data.nature_piece_identite_uid
        )

        agent.genre_uid = (
            agent_data.genre_uid
        )

        agent.type_agent_uid = (
            agent_data.type_agent_uid
        )

        agent.user_uid = (
            agent_data.user_uid
        )

        agent.nationalite_uid = (
            agent_data.nationalite_uid
        )

        agent.type_recrutement_uid = (
            agent_data.type_recrutement_uid
        )

        agent.structure_uid = (
            agent_data.structure_uid
        )

        agent.fonction_uid = (
            agent_data.fonction_uid
        )

        agent.situation_matrimoniale_uid = (
            agent_data.situation_matrimoniale_uid
        )

        agent.specialite_uid = (
            agent_data.specialite_uid
        )

        agent.grade_uid = (
            agent_data.grade_uid
        )

        agent.statut_uid = (
            agent_data.statut_uid
        )

        # =====================================================
        # 4. Gestion du conjoint
        # =====================================================

        if (
            agent_data.nom_conjoint is not None
            and agent_data.prenoms_conjoint is not None
        ):

            if agent.conjoint is not None:

                # Modifier le conjoint existant
                agent.conjoint.nom = (
                    agent_data.nom_conjoint
                )

                agent.conjoint.prenoms = (
                    agent_data.prenoms_conjoint
                )

                agent.conjoint.profession = (
                    agent_data.profession_conjoint
                )

                agent.conjoint.matricule_cnps = (
                    agent_data.matricule_cnps_conjoint
                )

            else:

                # Créer un nouveau conjoint
                conjoint = Conjoint(
                    uid=uuid4(),
                    nom=agent_data.nom_conjoint,
                    prenoms=agent_data.prenoms_conjoint,
                    profession=agent_data.profession_conjoint,
                    matricule_cnps=agent_data.matricule_cnps_conjoint
                )

                session.add(conjoint)

                await session.flush()

                agent.conjoint_uid = conjoint.uid

        elif agent.conjoint is not None:

            # Aucun conjoint fourni :
            # supprimer la relation
            agent.conjoint_uid = None

        # =====================================================
        # 5. Situation administrative
        # =====================================================

        if agent_data.statut_situation_administrative_uid is not None:

            situation_administrative_data = (
                SituationAdministrativeCreateModel(
                    numero_acte_nomination_dans_emploi=(
                        agent_data.numero_acte_nomination_dans_emploi
                    ),

                    date_signature_acte_nomination_dans_emploi=(
                        agent_data.date_signature_acte_nomination_dans_emploi
                    ),

                    date_premiere_prise_service_fonction_publique=(
                        agent_data.date_premiere_prise_service_fonction_publique
                    ),

                    date_depart_retraite=(
                        agent_data.date_depart_retraite
                    ),

                    date_radiation=(
                        agent_data.date_radiation
                    ),

                    date_depart_mouvement=(
                        agent_data.date_depart_mouvement
                    ),

                    date_retour_mouvement=(
                        agent_data.date_retour_mouvement
                    ),

                    adresse_bureau=(
                        agent_data.adresse_bureau
                    ),

                    adresse_personnelle=(
                        agent_data.adresse_personnelle
                    ),

                    telephone_bureau=(
                        agent_data.telephone_bureau
                    ),

                    telephone_domicile=(
                        agent_data.telephone_domicile
                    ),

                    numero_telephone_1=(
                        agent_data.numero_telephone_1
                    ),

                    numero_telephone_2=(
                        agent_data.numero_telephone_2
                    ),

                    email_institutionnel=(
                        agent_data.email_institutionnel
                    ),

                    designation_poste=(
                        agent_data.designation_poste
                    ),

                    numero_acte_nomination_fonctionactuelle=(
                        agent_data.numero_acte_nomination_fonctionactuelle
                    ),

                    date_signature_acte_nomination_fonctionactuelle=(
                        agent_data.date_signature_acte_nomination_fonctionactuelle
                    ),

                    is_equivqlence=(
                        agent_data.is_equivqlence
                    ),

                    statut_situation_administrative_uid=(
                        agent_data.statut_situation_administrative_uid
                    ),

                    emploi_uid=agent_data.emploi_uid,

                    classe_situation_administrative_uid=(
                        agent_data.classe_situation_administrative_uid
                    ),

                    echelon_uid=agent_data.echelon_uid,

                    nature_acte_nomination_dans_emploi_uid=(
                        agent_data.nature_acte_nomination_dans_emploi_uid
                    ),

                    nature_acte_nomination_dans_fonctionactuelle_uid=(
                        agent_data
                        .nature_acte_nomination_dans_fonctionactuelle_uid
                    ),

                    diplome_uid=agent_data.diplome_uid,

                    position_administrative_uid=(
                        agent_data.position_administrative_uid
                    ),

                    position_militaire_uid=(
                        agent_data.position_militaire_uid
                    ),

                    fonction_actuelle_uid=(
                        agent_data.fonction_actuelle_uid
                    )
                )
            )

            # ---------------------------------------------
            # Situation existante
            # ---------------------------------------------

            if agent.situation_administrative is not None:

                situation = agent.situation_administrative

                situation.numero_acte_nomination_dans_emploi = (
                    situation_administrative_data
                    .numero_acte_nomination_dans_emploi
                )

                situation.date_signature_acte_nomination_dans_emploi = (
                    situation_administrative_data
                    .date_signature_acte_nomination_dans_emploi
                )

                situation.date_premiere_prise_service_fonction_publique = (
                    situation_administrative_data
                    .date_premiere_prise_service_fonction_publique
                )

                situation.date_depart_retraite = (
                    situation_administrative_data
                    .date_depart_retraite
                )

                situation.date_radiation = (
                    situation_administrative_data.date_radiation
                )

                situation.date_depart_mouvement = (
                    situation_administrative_data.date_depart_mouvement
                )

                situation.date_retour_mouvement = (
                    situation_administrative_data.date_retour_mouvement
                )

                situation.adresse_bureau = (
                    situation_administrative_data.adresse_bureau
                )

                situation.adresse_personnelle = (
                    situation_administrative_data.adresse_personnelle
                )

                situation.telephone_bureau = (
                    situation_administrative_data.telephone_bureau
                )

                situation.telephone_domicile = (
                    situation_administrative_data.telephone_domicile
                )

                situation.numero_telephone_1 = (
                    situation_administrative_data.numero_telephone_1
                )

                situation.numero_telephone_2 = (
                    situation_administrative_data.numero_telephone_2
                )

                situation.email_institutionnel = (
                    situation_administrative_data.email_institutionnel
                )

                situation.designation_poste = (
                    situation_administrative_data.designation_poste
                )

                situation.numero_acte_nomination_fonctionactuelle = (
                    situation_administrative_data
                    .numero_acte_nomination_fonctionactuelle
                )

                situation.date_signature_acte_nomination_fonctionactuelle = (
                    situation_administrative_data
                    .date_signature_acte_nomination_fonctionactuelle
                )

                situation.is_equivqlence = (
                    situation_administrative_data.is_equivqlence
                )

                situation.statut_situation_administrative_uid = (
                    situation_administrative_data
                    .statut_situation_administrative_uid
                )

                situation.emploi_uid = (
                    situation_administrative_data.emploi_uid
                )

                situation.classe_situation_administrative_uid = (
                    situation_administrative_data
                    .classe_situation_administrative_uid
                )

                situation.echelon_uid = (
                    situation_administrative_data.echelon_uid
                )

                situation.nature_acte_nomination_dans_emploi_uid = (
                    situation_administrative_data
                    .nature_acte_nomination_dans_emploi_uid
                )

                situation.nature_acte_nomination_dans_fonctionactuelle_uid = (
                    situation_administrative_data
                    .nature_acte_nomination_dans_fonctionactuelle_uid
                )

                situation.diplome_uid = (
                    situation_administrative_data.diplome_uid
                )

                situation.position_administrative_uid = (
                    situation_administrative_data
                    .position_administrative_uid
                )

                situation.position_militaire_uid = (
                    situation_administrative_data
                    .position_militaire_uid
                )

                situation.fonction_actuelle_uid = (
                    situation_administrative_data
                    .fonction_actuelle_uid
                )

            # ---------------------------------------------
            # Aucune situation existante
            # ---------------------------------------------

            else:

                situation = await self.creer_situation_administrative(
                    session,
                    situation_administrative_data
                )

                agent.situation_administrative_uid = situation.uid

        # -----------------------------
        # Mettre à jour le rôle
        # -----------------------------
        if agent_data.role_uid is not None:
            await self.affecter_role(
                session=session,
                user_uid=agent.user_uid,
                role_uid=agent_data.role_uid
            )

        # -----------------------------
        # Mettre à jour les permissions
        # -----------------------------
        if agent_data.permissions is not None:

            await self.affecter_permission(
                session=session,
                user_uid=agent.user_uid,
                permission_uids=agent_data.permissions
            )

        # =====================================================
        # 6. Utilisateur qui modifie
        # =====================================================

        agent.modifie_par_uid = current_user_uid

        # =====================================================
        # 7. Sauvegarder
        # =====================================================

        await session.flush()

        # =====================================================
        # 8. Recharger l'agent avec toutes ses relations
        # =====================================================

        agent = await self.recharger_agent(
            session,
            agent_uid
        )

        return agent


    async def delete_agent(self, agent_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        agent_to_delete = await self.get_agent_by_id( session, agent_uid)

        if agent_to_delete is None:
            raise RaiseException(
                message="Agent non trouvé",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "agent_uid": "Aucun agent ne correspond à cet identifiant.",
                },
            )
        agent_to_delete.is_mode = False
        agent_to_delete.is_deleted = True
        agent_to_delete.supprime_le = datetime.now(timezone.utc)
        agent_to_delete.supprime_par_uid = current_user_uid

        session.add(agent_to_delete)
        await session.commit()
        
        # =====================================================
        #  Recharger complètement agent
        # =====================================================
        agent_recharge = await self.recharger_agent(
            session,
            agent_to_delete.uid
        )
        
        return agent_recharge 
    

    async def get_agent(self, agent_uid: UUID, session: AsyncSession):

        agent= await self.recharger_agent(
            session,
            agent_uid
        )

        return agent


    async def restore_agent(self, agent_uid: UUID, current_user_uid:UUID, session: AsyncSession):
        agent_to_restore= await self.get_agent_by_id( session, agent_uid)
    
        if agent_to_restore is None:
            raise RaiseException(
                message="Agent non trouvée",
                code=status.HTTP_404_NOT_FOUND,
                errors={
                    "agent_uid": "Aucun agent ne correspond à cet identifiant.",
                },
            )
        agent_to_restore.is_mode = True
        agent_to_restore.is_deleted = False
        agent_to_restore.supprime_le = None
        agent_to_restore.supprime_par_uid = None
        agent_to_restore.modifie_par_uid = current_user_uid
        agent_to_restore.modifie_le = datetime.now(timezone.utc)
    
        session.add(agent_to_restore)
        await session.commit()

        agent= await self.recharger_agent(
            session,
            agent_uid
        )

        return agent
    
      

    async def get_agent_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Agent]:
        statement = select(Agent).where(Agent.code == code)
        result = await db.exec(statement)
        return result.first()
    

    async def get_agent_by_id(
        self,
        db: AsyncSession,
        agent_uid: UUID
    ) -> Optional[Agent]:
        statement = select(Agent).where(Agent.uid == agent_uid)
        result = await db.exec(statement)
        return result.first()


    async def recharger_nature_piece_identite(
        self,
        session: AsyncSession,
        naturepieceidentite_uid: UUID,
    ) -> NaturePieceidentite:

        statement = select(NaturePieceidentite).where(
            NaturePieceidentite.uid == naturepieceidentite_uid
        )

        result = await session.execute(statement)
        naturepieceidentite = result.scalar_one_or_none()
        return naturepieceidentite

    async def recharger_genre(
        self,
        session: AsyncSession,
        genre_uid: UUID,
    ) -> Genre:

        statement = select(Genre).where(
            Genre.uid == genre_uid
        )

        result = await session.execute(statement)
        genre = result.scalar_one_or_none()
        return genre

    async def recharger_type_agent(
        self,
        session: AsyncSession,
        type_agent_uid: UUID,
    ) -> Genre:

        statement = select(TypeAgent).where(
            TypeAgent.uid == type_agent_uid
        )

        result = await session.execute(statement)
        type_agent = result.scalar_one_or_none()
        return type_agent

    async def recharger_nationalite(
        self,
        session: AsyncSession,
        nationalite_uid: UUID,
    ) -> Genre:

        statement = select(Nationalite).where(
            Nationalite.uid == nationalite_uid
        )

        result = await session.execute(statement)
        nationalite = result.scalar_one_or_none()
        return nationalite

    async def recharger_agent(
        self,
        session: AsyncSession,
        agent_uid: UUID,
    ) -> Agent:

        statement = (
            select(Agent)
            .options(

                # =========================
                # STRUCTURE
                # =========================
                selectinload(
                    Agent.structure
                ),

                # =========================
                # SITUATION ADMINISTRATIVE
                # =========================
                selectinload(
                    Agent.situation_administrative
                ),
                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.emploi
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.classe_situation_administrative
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.echelon
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.nature_acte_nomination_dans_emploi
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.nature_acte_nomination_dans_fonctionactuelle
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.diplome
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.position_administrative
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.position_militaire
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.fonction_actuelle
                ),

                selectinload(
                    Agent.situation_administrative
                ).selectinload(
                    SituationAdministrative.statut
                ),

                selectinload(
                    Agent.conjoint
                ),

                selectinload(
                    Agent.cree_par
                ).selectinload(
                    User.role
                ),
                selectinload(
                    Agent.cree_par
                ).selectinload(
                    User.permissions
                ),

                selectinload(
                    Agent.modifie_par
                ).selectinload(
                    User.role
                ),
                selectinload(
                    Agent.modifie_par
                ).selectinload(
                    User.permissions
                ),
                selectinload(
                    Agent.supprime_par
                ).selectinload(
                    User.role
                ),
                selectinload(
                    Agent.supprime_par
                ).selectinload(
                    User.permissions
                ),

                selectinload(
                    Agent.nature_piece_identite
                ),

                selectinload(
                    Agent.genre
                ),

                selectinload(
                    Agent.type_agent
                ),

                selectinload(
                    Agent.nationalite
                ),

                selectinload(
                    Agent.type_recrutement
                ),

                selectinload(
                    Agent.fonction
                ),

                selectinload(
                    Agent.situation_matrimoniale
                ),

                selectinload(
                    Agent.specialite
                ),

                selectinload(
                    Agent.grade
                ),

                selectinload(
                    Agent.statut
                ),
                selectinload(
                    Agent.validation_fiche
                ),
                # =========================
                # ROLE ET PERMISSIONS
                # =========================
                
                selectinload(
                    Agent.user
                ).selectinload(
                    User.role
                ),
                selectinload(
                    Agent.user
                ).selectinload(
                    User.permissions
                ),
            )
            .where(
                Agent.uid == agent_uid
            )
        )

        result = await session.execute(statement)

        agent = result.scalar_one_or_none()

        return agent


    async def recharger_structure(
        self,
        session: AsyncSession,
        structure_uid: UUID,
    ):
        statement = (
            select(Structure)
            .options(
                selectinload(Structure.typestructure),
            )
            .where(
                Structure.uid == structure_uid
            )
        )

        result = await session.execute(statement)
        structure = result.scalar_one_or_none()
        return structure

    async def recharger_fonction(
        self,
        session: AsyncSession,
        fonction_uid: UUID,
    ):
        statement = (
            select(Fonction)
            .where(
                Fonction.uid == fonction_uid
            )
        )

        result = await session.execute(statement)
        fonction = result.scalar_one_or_none()
        return fonction 


    async def recharger_situation_matrimoniale(
        self,
        session: AsyncSession,
        situation_matrimoniale_uid: UUID,
    ):
        statement = (
            select(SituationMatrimoniale)
            .where(
                SituationMatrimoniale.uid == situation_matrimoniale_uid
            )
        )

        result = await session.execute(statement)
        situation_matrimoniale = result.scalar_one_or_none()
        return situation_matrimoniale  


    async def creer_conjoint(
        self,
        session: AsyncSession,
        conjoint_data:ConjointCreateModel,
    ):
        # Créer situation administrative
        conjoint_cree = Conjoint(
            uid=uuid4(),
            nom=conjoint_data.nom_conjoint,
            prenoms=conjoint_data.prenoms_conjoint,
            matricule_cnps=conjoint_data.matricule_cnps_conjoint,
            profession=conjoint_data.profession_conjoint,
            code = ''.join(secrets.choice("0123456789")for _ in range(12)),
            cree_le = datetime.now(),
            modifie_le = datetime.now(),
            is_mode = True,
            supprime_le = datetime.now(),
        )
                
        # Ajouter à la session
        session.add(conjoint_cree)
                
        # Sauvegarder
        await session.commit()
        await session.refresh(conjoint_cree)
        
        return conjoint_cree
                

    async def creer_situation_administrative(
        self,
        session: AsyncSession,
        situation_administrative_data: SituationAdministrativeCreateModel
    ):
        # Créer la situation administrative
        situation_administrative_cree = SituationAdministrative(
            numero_acte_nomination_dans_emploi=(
                situation_administrative_data.numero_acte_nomination_dans_emploi
            ),

            date_signature_acte_nomination_dans_emploi=(
                situation_administrative_data.date_signature_acte_nomination_dans_emploi
            ),

            date_premiere_prise_service_fonction_publique=(
                situation_administrative_data.date_premiere_prise_service_fonction_publique
            ),

            date_depart_retraite=(
                situation_administrative_data.date_depart_retraite
            ),

            date_radiation=(
                situation_administrative_data.date_radiation
            ),

            date_depart_mouvement=(
                situation_administrative_data.date_depart_mouvement
            ),

            date_retour_mouvement=(
                situation_administrative_data.date_retour_mouvement
            ),

            adresse_bureau=(
                situation_administrative_data.adresse_bureau
            ),

            adresse_personnelle=(
                situation_administrative_data.adresse_personnelle
            ),

            telephone_bureau=(
                situation_administrative_data.telephone_bureau
            ),

            telephone_domicile=(
                situation_administrative_data.telephone_domicile
            ),

            numero_telephone_1=(
                situation_administrative_data.numero_telephone_1
            ),

            numero_telephone_2=(
                situation_administrative_data.numero_telephone_2
            ),

            email_institutionnel=(
                situation_administrative_data.email_institutionnel
            ),

            designation_poste=(
                situation_administrative_data.designation_poste
            ),

            numero_acte_nomination_fonctionactuelle=(
                situation_administrative_data.numero_acte_nomination_fonctionactuelle
            ),

            date_signature_acte_nomination_fonctionactuelle=(
                situation_administrative_data.date_signature_acte_nomination_fonctionactuelle
            ),

            is_equivqlence=(
                situation_administrative_data.is_equivqlence
            ),

            statut_situation_administrative_uid=(
                situation_administrative_data.statut_situation_administrative_uid
            ),

            emploi_uid=(
                situation_administrative_data.emploi_uid
            ),

            classe_situation_administrative_uid=(
                situation_administrative_data.classe_situation_administrative_uid
            ),

            echelon_uid=(
                situation_administrative_data.echelon_uid
            ),

            nature_acte_nomination_dans_emploi_uid=(
                situation_administrative_data.nature_acte_nomination_dans_emploi_uid
            ),

            nature_acte_nomination_dans_fonctionactuelle_uid=(
                situation_administrative_data.nature_acte_nomination_dans_fonctionactuelle_uid
            ),

            diplome_uid=(
                situation_administrative_data.diplome_uid
            ),

            position_administrative_uid=(
                situation_administrative_data.position_administrative_uid
            ),

            position_militaire_uid=(
                situation_administrative_data.position_militaire_uid
            ),

            fonction_actuelle_uid=(
                situation_administrative_data.fonction_actuelle_uid
            )
        )

        # Ajouter à la session
        session.add(situation_administrative_cree)

        # Envoyer vers la BDD sans valider toute la transaction
        await session.flush()

        return situation_administrative_cree
        

    async def recharger_situation_administrative(
        self,
        session: AsyncSession,
        situation_administrative_uid: UUID,
    ):
        statement = (
            select(SituationAdministrative)
            .where(
                SituationAdministrative.uid == situation_administrative_uid
            )
        )

        result = await session.execute(statement)
        situation_administrative = result.scalar_one_or_none()
        return situation_administrative  

    
    async def recharger_specialite(
        self,
        session: AsyncSession,
        specialite_uid: UUID,
    ):
        statement = (
            select(Specialite)
            .where(
                Specialite.uid == specialite_uid
            )
        )

        result = await session.execute(statement)
        specialite = result.scalar_one_or_none()
        return specialite  

    async def recharger_emploi(
        self,
        session: AsyncSession,
        emploi_uid: UUID,
    ):
        statement = (
            select(Emploi)
            .where(
                Emploi.uid == emploi_uid
            )
        )

        result = await session.execute(statement)
        emploi = result.scalar_one_or_none()
        return emploi

    async def recharger_grade(
        self,
        session: AsyncSession,
        grade_uid: UUID,
    ):
        statement = (
            select(Grade)
            .where(
                Grade.uid == grade_uid
            )
        )

        result = await session.execute(statement)
        grade = result.scalar_one_or_none()
        return grade

    async def recharger_statut(
        self,
        session: AsyncSession,
        statut_uid: UUID,
    ):
        statement = (
            select(Statut)
            .where(
                Statut.uid == statut_uid
            )
        )

        result = await session.execute(statement)
        statut = result.scalar_one_or_none()
        return statut 

    async def recharger_nature_acte_nomination_fonctionactuelle(
        self,
        session: AsyncSession,
        nature_acte_nomination_fonctionactuelle_uid: UUID,
    ):
        statement = (
            select(NatureActeNominationFonctionactuelle)
            .where(
                NatureActeNominationFonctionactuelle.uid == nature_acte_nomination_fonctionactuelle_uid
            )
        )

        result = await session.execute(statement)
        nature_acte_nomination_fonctionactuelle = result.scalar_one_or_none()
        return nature_acte_nomination_fonctionactuelle

        #"fonction_actuelle_uid" : agent_data.fonction_actuelle_uid

    async def recharger_validation_fiche(
        self,
        session: AsyncSession,
        validation_fiche_uid: UUID,
    ):
        statement = (
            select(ValidationFiche)
            .where(
                ValidationFiche.uid == validation_fiche_uid 
            )
        )

        result = await session.execute(statement)
        validation_fiche = result.scalar_one_or_none()
        return validation_fiche

    async def recharger_statut_situation_administrative(
            self,
            session: AsyncSession,
            statut_situation_administrative_uid: UUID,
        ):
            statement = (
                select(StatutSituationAdministrative)
                .where(
                    StatutSituationAdministrative.uid == statut_situation_administrative_uid 
                )
            )
    
            result = await session.execute(statement)
            statut_situation_administrative = result.scalar_one_or_none()
            return statut_situation_administrative

    async def recharger_classe_situation_administrative(
        self,
        session: AsyncSession,
        classe_situation_administrative_uid: UUID,
    ):
        statement = (
            select(ClasseSituationAdministrative)
            .where(
                ClasseSituationAdministrative.uid == classe_situation_administrative_uid 
            )
        )
        
        result = await session.execute(statement)
        classe_situation_administrative = result.scalar_one_or_none()
        return classe_situation_administrative 


    async def recharger_echelon(
        self,
        session: AsyncSession,
        echelon_uid: UUID,
    ):
        statement = (
            select(Echelon)
            .where(
                Echelon.uid == echelon_uid 
            )
        )
        
        result = await session.execute(statement)
        echelon = result.scalar_one_or_none()
        return echelon

   
    async def recharger_nature_acte_nomination_dans_emploi(
        self,
        session: AsyncSession,
        nature_acte_nomination_dans_emploi_uid: UUID,
    ):
        statement = (
            select(NatureActeNominationDansEmploi)
            .where(
                NatureActeNominationDansEmploi.uid == nature_acte_nomination_dans_emploi_uid 
            )
        )
        
        result = await session.execute(statement)
        nature_acte_nomination_dans_emploi = result.scalar_one_or_none()
        return nature_acte_nomination_dans_emploi


    async def nature_acte_nomination_dans_fonctionactuelle(
        self,
        session: AsyncSession,
        nature_acte_nomination_dans_fonctionactuelle_uid: UUID,
    ):
        statement = (
            select(NatureActeNominationFonctionactuelle)
            .where(
                NatureActeNominationFonctionactuelle.uid == nature_acte_nomination_dans_fonctionactuelle_uid 
            )
        )
        
        result = await session.execute(statement)
        nature_acte_nomination_dans_fonctionactuelle = result.scalar_one_or_none()
        return nature_acte_nomination_dans_fonctionactuelle


    async def position_militaire(
        self,
        session: AsyncSession,
        position_militaire_uid: UUID,
    ):
        statement = (
            select(PositionMilitaire)
            .where(
                PositionMilitaire.uid == position_militaire_uid 
            )
        )
        
        result = await session.execute(statement)
        position_militaire = result.scalar_one_or_none()
        return position_militaire 

    
    async def diplome(
        self,
        session: AsyncSession,
        diplome_uid: UUID,
    ):
        statement = (
            select(Diplome)
            .where(
                Diplome.uid == diplome_uid 
            )
        )
        
        result = await session.execute(statement)
        diplome = result.scalar_one_or_none()
        return diplome 

    async def position_administrative(
        self,
        session: AsyncSession,
        position_administrative_uid: UUID,
    ):
        statement = (
            select(PositionAdministrative)
            .where(
                PositionAdministrative.uid == position_administrative_uid 
            )
        )
        
        result = await session.execute(statement)
        position_administrative = result.scalar_one_or_none()
        return position_administrative 

    async def fonction_actuelle(
        self,
        session: AsyncSession,
        fonction_actuelle_uid: UUID,
    ):
        statement = (
            select(FonctionActuelle)
            .where(
                FonctionActuelle.uid == fonction_actuelle_uid 
            )
        )
        
        result = await session.execute(statement)
        fonction_actuelle = result.scalar_one_or_none()
        return fonction_actuelle
    

    async def verifier_matricule_unique(
        self,
        session: AsyncSession,
        matricule: str,
        agent_uid: UUID | None = None,
    ) -> bool:

        statement = select(Agent).where(
            Agent.matricule == matricule
        )

        # Pour UPDATE : ne pas comparer l'agent avec lui-même
        if agent_uid is not None:
            statement = statement.where(
                Agent.uid != agent_uid
            )

        result = await session.exec(statement)

        agent = result.first()

        return agent is None





