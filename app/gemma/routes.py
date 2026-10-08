# app/gemma/routes.py

from fastapi import APIRouter, Depends, status

from app.gemma.schemas import AssistantRequest
from app.gemma.services import gemma_service
from app.auth.dependencies import get_current_active_user


assistant_router = APIRouter(
    prefix="/assistant",
    tags=["Assistant IA"],
)


@assistant_router.post(
    "/question",
    status_code=status.HTTP_200_OK,
)
async def ask_assistant(
    payload: AssistantRequest,
    current_user=Depends(get_current_active_user),
):
    answer = await gemma_service.generate_response(
        question=payload.question,
    )

    return {
        "code": 200,
        "success": True,
        "message": "Réponse générée avec succès.",
        "data": {
            "question": payload.question,
            "answer": answer,
        },
    }