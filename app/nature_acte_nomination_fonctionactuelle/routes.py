from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.nature_acte_nomination_fonctionactuelle.services import NatureActeNominationFonctionactuelleService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.nature_acte_nomination_fonctionactuelle.schemas import NatureActeNominationFonctionactuelleCreateModel, NatureActeNominationFonctionactuelleUpdateModel, NatureActeNominationFonctionactuelleResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


nature_acte_nomination_fonctionactuelle_router = APIRouter()
nature_acte_nomination_fonctionactuelle_service = NatureActeNominationFonctionactuelleService()

@nature_acte_nomination_fonctionactuelle_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[NatureActeNominationFonctionactuelleResponse])
async def get_all_nature_acte_nomination_fonctionactuelles(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
)->dict:
   
    nature_acte_nomination_fonctionactuelle = await nature_acte_nomination_fonctionactuelle_service.get_all_nature_acte_nomination_fonctionactuelles(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Natures acte nomination fonction actuelle trouvées avec succès",
        data=nature_acte_nomination_fonctionactuelle
    )


@nature_acte_nomination_fonctionactuelle_router.get("/{nature_acte_nomination_fonctionactuelle_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[NatureActeNominationFonctionactuelleResponse])
async def nature_acte_nomination_fonctionactuelle(
    nature_acte_nomination_fonctionactuelle_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    nature_acte_nomination_fonctionactuelle_trouve = await nature_acte_nomination_fonctionactuelle_service.get_nature_acte_nomination_fonctionactuelle(nature_acte_nomination_fonctionactuelle_uid,session)

    if nature_acte_nomination_fonctionactuelle_trouve is None:
            raise RaiseException(
                message="Nature acte nomination fonction publiaue non trouvée",
                code=404,
                errors={
                    "nature_acte_nomination_fonctionpublique_uid": "Aucune nature acte de nomination fonction publique ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Nature acte nomination fonction actuelle trouvé avec succès",
        data=nature_acte_nomination_fonctionactuelle_trouve
    )



 



