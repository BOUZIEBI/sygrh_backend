from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exception_handlers import validation_exception_handler

app = FastAPI()

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)