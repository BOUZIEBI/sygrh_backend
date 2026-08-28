from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.grade.services import GradeService
from app.db.main import get_session
from app.auth.dependencies import get_current_active_user, require_permission
from app.grade.schemas import GradeCreateModel, GradeUpdateModel, GradeResponse, MessageAllResponse, MessageResponse
from app.core.exceptions_metier import RaiseException


grade_router = APIRouter()
grade_service = GradeService()

@grade_router.get("/all",status_code=status.HTTP_200_OK, response_model=MessageAllResponse[GradeResponse])
async def get_all_grade(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
)->dict:
   
    grades = await grade_service.get_all_grades(session)
    
    return MessageAllResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Grades trouvés avec succès",
        data=grades
    )


@grade_router.get("/{grade_uid}",status_code=status.HTTP_200_OK,response_model=MessageResponse[GradeResponse])
async def get_un_grade(
    grade_uid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user),
) -> dict:
    current_user_uid=current_user.uid
    grade_trouve = await grade_service.get_grade(grade_uid,session)

    if grade_trouve is None:
            raise RaiseException(
                message="Grade non trouvé",
                code=404,
                errors={
                    "grade_uid": "Aucun grade ne correspond à cet identifiant."
                }
            ) 
    
    return MessageResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="Grade trouvé avec succès",
        data=grade_trouve
    )



 



