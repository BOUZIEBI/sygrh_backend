from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    errors = {}

    if isinstance(exc.detail, dict):
        field = exc.detail.get("field")
        message = exc.detail.get("message")

        if field and message:
            errors[field] = message
        else:
            errors = exc.detail

    else:
        errors = {
            "general": str(exc.detail)
        }

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "success": False,
            "message": "Erreur",
            "errors": errors,
        },
    )