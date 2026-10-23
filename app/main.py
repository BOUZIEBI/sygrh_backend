# app/main.py

import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.exception_handlers import (
    metier_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import http_exception_handler
from app.core.exceptions_metier import RaiseException

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
from app.nature_acte_nomination_fonctionactuelle.routes import (
    nature_acte_nomination_fonctionactuelle_router,
)
from app.agent.routes import agent_router
from app.communique.routes import communique_router
from app.actualite.routes import actualite_router
from app.crypto.routes import crypto_router
from app.departement.routes import departement_router
from app.redis.routes import redis_router

from app.nosservices import service_router
from app.phototheque import phototheque_router
from app.message import message_router
from app.visiteur_session import visiteur_session_router


# Lecture des listes depuis les variables d'environnement
def get_env_list(
    name: str,
    default: str = "",
) -> list[str]:
    value = os.getenv(name, default)

    return list(
        dict.fromkeys(
            item.strip()
            for item in value.split(",")
            if item.strip()
        )
    )


# Métadonnées
APP_VERSION = os.getenv("APP_VERSION", "").strip() or "v1"
APP_NAME = os.getenv("APP_NAME", "").strip() or "SYGRH API"
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "").strip()

VERSION_PREFIX = f"/api/{APP_VERSION}"


# Hôtes autorisés : sans protocole ni chemin
ALLOWED_HOSTS = get_env_list(
    "ALLOWED_HOSTS",
    (
        "sygrhbackend-production.up.railway.app,"
        "localhost,"
        "127.0.0.1"
    ),
)


# Origines de confiance pour ta protection CSRF
# Cette liste doit être utilisée par ta vérification CSRF.
CSRF_TRUSTED_ORIGINS = get_env_list(
    "CSRF_TRUSTED_ORIGINS",
    (
        "https://sygrh-frontend-fastapi-production.up.railway.app,"
        "http://localhost:5173"
    ),
)


# Origines autorisées à appeler l'API depuis un navigateur
CORS_ALLOWED_ORIGINS = get_env_list(
    "CORS_ALLOWED_ORIGINS",
    (
        "https://sygrh-frontend-fastapi-production.up.railway.app," 
        "http://localhost:5173"
    ),
)


# Application
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    contact={
        "name": "Inovel",
        "email": "contact@inovel.net",
    },
)


# Vérification de l'en-tête Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS,
    www_redirect=False,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "X-Crypto-Session-ID",
    ],
    expose_headers=[
        "Authorization",
        "X-CSRF-Token",
        "X-Crypto-Session-ID",
    ],
    max_age=600,
)


# Gestionnaires d'exceptions
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RaiseException,
    metier_exception_handler,
)


# Routes
routers = [
    (auth_router, "auth", "auth"),
    (typeagent_router, "typeagent", "typeagent"),
    (
        naturepieceidentite_router,
        "nature-piece-identite",
        "naturepieceidentite",
    ),
    (genre_router, "genre", "genre"),
    (nationalite_router, "nationalite", "nationalite"),
    (typstructure_router, "typestructure", "typestructure"),
    (structure_router, "structure", "structure"),
    (fonction_router, "fonction", "fonction"),
    (
        situationmatrimoniale_router,
        "situationmatrimoniale",
        "situationmatrimoniale",
    ),
    (emploi_router, "emploi", "emploi"),
    (grade_router, "grade", "grade"),
    (statut_router, "statut", "statut"),
    (
        fichevalidation_router,
        "fichevalidation",
        "fichevalidation",
    ),
    (
        nature_acte_nomination_fonctionactuelle_router,
        "nature-acte-nomination-fonctionactuelle",
        "natureactenominationfonctionactuelle",
    ),
    (agent_router, "agent", "agent"),
    (crypto_router, "crypto", "crypto"),
    (redis_router, "redis", "redis"),
    (communique_router, "communique", "communique"),
    (actualite_router, "actualite", "actualite"),
    (service_router, "service", "service"),
    (phototheque_router, "phototheque", "phototheque"),
    (message_router, "message", "message"),
    (
        visiteur_session_router,
        "visiteursession",
        "visiteursession",
    ),
    (departement_router, "departement", "departement"),
]

for router, path, tag in routers:
    app.include_router(
        router,
        prefix=f"{VERSION_PREFIX}/{path}",
        tags=[tag],
    )


@app.get("/", tags=["Accueil"])
async def root():
    return {
        "success": True,
        "message": f"{APP_NAME} running",
        "version": APP_VERSION,
    }


@app.get("/health", tags=["Santé"])
async def health():
    return {"status": "ok"}


@app.get("/cors-test", tags=["Diagnostic"])
async def cors_test(request: Request):
    origin = request.headers.get("origin")

    return {
        "success": True,
        "origin": origin,
        "origin_allowed": (
            origin in CORS_ALLOWED_ORIGINS
            if origin
            else False
        ),
    }