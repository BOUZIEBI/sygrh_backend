# app/services/gemma_service.py

from google import genai
from google.genai import types

from app.core.config import settings


class GemmaService:

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

    async def generate_response(self, question: str) -> str:
        response = await self.client.aio.models.generate_content(
            model=settings.GEMMA_MODEL,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Tu es Assistant DRH-MESRS. "
                    "Tu réponds en français, clairement et précisément. "
                    "Tu n'inventes jamais les dates des concours. "
                    "Si une information officielle n'est pas disponible, "
                    "tu le signales explicitement."
                ),
                temperature=0.3,
                max_output_tokens=1000,
            ),
        )

        return response.text or "Aucune réponse générée."


gemma_service = GemmaService()