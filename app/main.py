from fastapi import FastAPI, HTTPException
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
import os
from app.auth.routes import auth_router
from app.structure.routes import structure_router
from app.type_structure.routes import typstructure_router
from app.nationalite.routes import nationalite_router
from app.naturepieceidentite.routes import naturepieceidentite_router
from app.type_agent.routes import typeagent_router
from app.genre.routes import genre_router
from app.fonction.routes import fonction_router
from app.situation_matrimoniale.routes import situationmatrimoniale_router
from app.emploi.routes import emploi_router
from app.grade.routes import grade_router
from app.statut.routes import statut_router
from app.fichevalidation.routes import fichevalidation_router
from app.nature_acte_nomination_fonctionactuelle.routes import nature_acte_nomination_fonctionactuelle_router
from app.agent.routes import agent_router
from app.communique.routes import communique_router 
from app.actualite.routes import actualite_router
from app.crypto.routes import crypto_router
from app.departement.routes import departement_router
from app.redis.routes import redis_router
from app.nosservices import *
from app.phototheque import phototheque_router
from app.message import message_router
from app.visiteur_session import visiteur_session_router
from fastapi.exceptions import RequestValidationError
from app.core.exception_handlers import validation_exception_handler
from app.core.exception_handlers import metier_exception_handler
from app.core.exceptions import http_exception_handler
from app.core.exceptions_metier import RaiseException



version = os.getenv("APP_VERSION", "")

RAILWAY_FRONTEND = (
    "https://mesrssitevitrine-production.up.railway.app"
)

app = FastAPI(
    version=version,
    title=os.getenv("APP_NAME", ""),
    description=os.getenv("APP_DESCRIPTION", ""), 
    contact={
        "name": "Inovel",
        "email": "contact@inovel.net"
    }
)

origins: list[str] = []

if settings.DEBUG:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    # Permet également de tester le frontend déployé
    # depuis l’environnement local.
    if settings.FRONTEND_URL:
        origins.append(
            str(settings.FRONTEND_URL)
            .rstrip("/")
        )

else:
    if not settings.FRONTEND_URL:
        raise RuntimeError(
            "FRONTEND_URL doit être définie "
            "en production."
        )

    origins.append(settings.FRONTEND_URL)

# Suppression des valeurs vides et des doublons
origins = list(dict.fromkeys(origins))


"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "X-Crypto-Session-ID",
    ],
)
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "X-Crypto-Session-ID",
    ],
    max_age=600,
)


#Pour les exceptions de validation des requestes
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

#Pour les exceptions globales : erreur serveur, body endpoint absent etc
app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

#Pour les exception portant sur les objets non trouves etc
app.add_exception_handler(
    RaiseException,
    metier_exception_handler
)

version_prefix =f"/api/{version}"

@app.get("/cors-test")
async def cors_test():
    return {
        "success": True,
        "allowed_origin": RAILWAY_FRONTEND,
    }

app.include_router(typeagent_router, prefix=f"{version_prefix}/typeagent", tags=["typeagent"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(naturepieceidentite_router, prefix=f"{version_prefix}/nature-piece-identite", tags=["naturepieceidentite"])
app.include_router(genre_router, prefix=f"{version_prefix}/genre", tags=["genre"])
app.include_router(nationalite_router, prefix=f"{version_prefix}/nationalite", tags=["nationalite"])
app.include_router(typstructure_router, prefix=f"{version_prefix}/typestructure", tags=["typestructure"])
app.include_router(structure_router, prefix=f"{version_prefix}/structure", tags=["structure"])
app.include_router(fonction_router, prefix=f"{version_prefix}/fonction", tags=["fonction"])
app.include_router(situationmatrimoniale_router, prefix=f"{version_prefix}/situationmatrimoniale", tags=["situationmatrimoniale"])
app.include_router(emploi_router, prefix=f"{version_prefix}/emploi", tags=["emploi"])
app.include_router(grade_router, prefix=f"{version_prefix}/grade", tags=["grade"])
app.include_router(statut_router, prefix=f"{version_prefix}/statut", tags=["statut"])
app.include_router(fichevalidation_router, prefix=f"{version_prefix}/fichevalidation", tags=["statut"])
app.include_router(nature_acte_nomination_fonctionactuelle_router, prefix=f"{version_prefix}/nature-acte-nomination-fonctionactuelle", tags=["natureactenominationfonctionactuelle"])
app.include_router(agent_router, prefix=f"{version_prefix}/agent", tags=["agent"])
app.include_router(crypto_router, prefix=f"{version_prefix}/crypto", tags=["crypto"])
app.include_router(redis_router, prefix=f"{version_prefix}/redis", tags=["crypto"])
app.include_router(communique_router, prefix=f"{version_prefix}/communique", tags=["communique"])
app.include_router(actualite_router, prefix=f"{version_prefix}/actualite", tags=["actualite"])
app.include_router(service_router, prefix=f"{version_prefix}/service", tags=["service"])
app.include_router(phototheque_router, prefix=f"{version_prefix}/phototheque", tags=["phototheque"])
app.include_router(message_router, prefix=f"{version_prefix}/message", tags=["message"])
app.include_router(visiteur_session_router, prefix=f"{version_prefix}/visiteursession", tags=["visiteursession"])

app.include_router(departement_router, prefix=f"{version_prefix}/departement", tags=["departement"])




@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} running 🚀",
        "debug": settings.DEBUG
    }
