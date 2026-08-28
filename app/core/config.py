import os
from dotenv import load_dotenv

load_dotenv()

def _as_bool(value:str, default:bool=False) -> bool:
    if value is None:
        return default
    return str(value).lower() in {"1","true", "yes", "on"}

class Settings:
    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME", "edutel API")
        self.DEBUG = _as_bool(os.getenv("DEBUG", "False"))
        self.DATABASE_URL = os.getenv("DATABASE_URL", "") 
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")    
        self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.REFRESH_TOKEN_EXPIRE_DAYS= int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES","10"))
        self.LOGIN_MAX_ATTEMPTS=int(os.getenv("LOGIN_MAX_ATTEMPTS","5"))
        self.LOGIN_LOCK_MINUTES=int(os.getenv("LOGIN_LOCK_MINUTES","5"))
        self.SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")     
        self.EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@example.com")
        self.FRONTEND_URL=os.getenv("FRONTEND_URL","")
        self.MAIL_HOST = os.getenv("MAIL_HOST", "")
        self.MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
        self.MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
        self.MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
        self.MAIL_FROM = os.getenv("MAIL_FROM", "")
        self.REDIS_HOST = os.getenv("REDIS_HOST", "redis")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_URL = os.getenv("REDIS_URL", "")


    FRONTEND_URL: str = "http://localhost:3000"

    def validate(self) -> None:
        if not self.DEBUG and self.SECRET_KEY.strip() in {"", "your-secret-key"}:
            raise ValueError("SECRET_KEY must be set in production.")

settings = Settings()
settings.validate()
