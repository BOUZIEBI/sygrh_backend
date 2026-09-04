from fastapi import FastAPI, HTTPException
from app.core.config import settings
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
from app.redis.routes import redis_router
from app.nosservices import *
from app.phototheque import phototheque_router
from app.message import message_router
from fastapi.exceptions import RequestValidationError
from app.core.exception_handlers import validation_exception_handler
from app.core.exception_handlers import metier_exception_handler
from app.core.exceptions import http_exception_handler
from app.core.exceptions_metier import RaiseException



version = os.getenv("APP_VERSION", "")

app = FastAPI(
    version=version,
    title=os.getenv("APP_NAME", ""),
    description=os.getenv("APP_DESCRIPTION", ""), 
    contact={
        "name": "Inovel",
        "email": "contact@inovel.net"
    }
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




@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} running 🚀",
        "debug": settings.DEBUG
    }