from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.exceptions_metier import RaiseException

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = {}

    for error in exc.errors():

        loc = error.get("loc", [])
        error_type = error.get("type")
        field = str(loc[-1]) if loc else "general"

        # -----------------------------------
        # Messages personnalisés en français
        # -----------------------------------

        if error_type == "missing":
            message = f"Le champ {field} est obligatoire."

        elif error_type in (
            "value_error",
            "value_error.email",
        ):
            if field == "email":
                message = (
                    "Le champ 'email' doit être une "
                    "adresse email valide."
                )
            else:
                message = error.get("msg", "Valeur invalide.")

        elif error_type == "string_type":
            message = f"Le champ {field} doit être une chaîne de caractères."

        elif error_type == "string_too_short":
            message = f"Le champ {field} est trop court."

        elif error_type == "string_too_long":
            message = f"Le champ {field} est trop long."

        elif error_type == "int_type":
            message = f"Le champ {field} doit être un nombre entier."

        elif error_type == "bool_type":
            message = f"Le champ {field} doit être un booléen."

        elif error_type == "uuid_parsing":
            message = f"Le champ {field} doit être un UUID valide."

        else:
            message = error.get("msg", "Valeur invalide.")

        # Supprimer "Value error, "
        if message.startswith("Value error, "):
            message = message.replace(
                "Value error, ",
                "",
                1
            )    

        errors[field] = message

    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "success": False,
            "message": "Erreur de validation",
            "errors": errors,
        },
    )


async def metier_exception_handler(
    request: Request,
    exc: RaiseException
):
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "success": False,
            "message": exc.message,
            "errors": exc.errors,
        },
    )

