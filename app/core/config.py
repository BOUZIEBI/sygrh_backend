import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class Settings:

    def __init__(self):

        # Application
        self.APP_NAME = os.getenv(
            "APP_NAME",
            "edutel API",
        )
     
        self.DEBUG = _as_bool(
            os.getenv("DEBUG"),
            False,
        )

        # --------------------------------------------------
        # DATABASE
        # --------------------------------------------------

        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "",
        ).strip()



        if self.DATABASE_URL.startswith("postgresql+psycopg://"):

            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql+psycopg://",
                "postgresql+asyncpg://",
                1,
            )

        elif self.DATABASE_URL.startswith("postgresql://"):

            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )
            # --------------------------------------------------
            # SECURITY
            # --------------------------------------------------

        self.SECRET_KEY = os.getenv(
            "SECRET_KEY",
            "",
        ).strip()

        self.JWT_SECRET_KEY = os.getenv(
                "JWT_SECRET_KEY",
                "",
        ).strip()

        self.JWT_ALGORITHM = os.getenv(
                "JWT_ALGORITHM",
                "HS256",
        )

        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
                os.getenv(
                    "ACCESS_TOKEN_EXPIRE_MINUTES",
                    "30",
                )
        )

        self.REFRESH_TOKEN_EXPIRE_DAYS = int(
                os.getenv(
                    "REFRESH_TOKEN_EXPIRE_DAYS",
                    "7",
                )
        )

        self.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
                os.getenv(
                    "PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
                    "10",
                )
        )

        # --------------------------------------------------
        # LOGIN SECURITY
        # --------------------------------------------------

        self.LOGIN_MAX_ATTEMPTS = int(
            os.getenv(
                "LOGIN_MAX_ATTEMPTS",
                "5",
            )
        )

        self.LOGIN_LOCK_MINUTES = int(
            os.getenv(
                "LOGIN_LOCK_MINUTES",
                "5",
            )
        )

        # --------------------------------------------------
        # HOST / CORS
        # --------------------------------------------------

        self.ALLOWED_HOSTS = [
            host.strip()
            for host in os.getenv(
                "ALLOWED_HOSTS",
                "*",
            ).split(",")
            if host.strip()
        ]

        self.CORS_ORIGINS = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "*",
            ).split(",")
            if origin.strip()
        ]

        # --------------------------------------------------
        # FRONTEND
        # --------------------------------------------------

        self.FRONTEND_URL = os.getenv(
            "FRONTEND_URL",
            "http://localhost:3000",
        ).strip()

        # --------------------------------------------------
        # SMTP
        # --------------------------------------------------

        self.SMTP_SERVER = os.getenv(
            "SMTP_SERVER",
            "",
        )

        self.SMTP_PORT = int(
            os.getenv(
                "SMTP_PORT",
                "587",
            )
        )

        self.SMTP_USERNAME = os.getenv(
            "SMTP_USERNAME",
            "",
        )

        self.SMTP_PASSWORD = os.getenv(
            "SMTP_PASSWORD",
            "",
        )

        self.EMAIL_FROM = os.getenv(
            "EMAIL_FROM",
            "",
        )

        # --------------------------------------------------
        # MAIL
        # --------------------------------------------------

        self.MAIL_HOST = os.getenv(
            "MAIL_HOST",
            "",
        )

        self.MAIL_PORT = int(
            os.getenv(
                "MAIL_PORT",
                "587",
            )
        )

        self.MAIL_USERNAME = os.getenv(
            "MAIL_USERNAME",
            "",
        )

        self.MAIL_PASSWORD = os.getenv(
            "MAIL_PASSWORD",
            "",
        )

        self.MAIL_FROM = os.getenv(
            "MAIL_FROM",
            "",
        )

        # --------------------------------------------------
        # REDIS
        # --------------------------------------------------

        self.REDIS_HOST = os.getenv(
            "REDIS_HOST",
            "redis",
        )

        self.REDIS_PORT = int(
            os.getenv(
                "REDIS_PORT",
                "6379",
            )
        )

        self.REDIS_DB = int(
            os.getenv(
                "REDIS_DB",
                "0",
            )
        )

        self.REDIS_URL = os.getenv(
            "REDIS_URL",
            "",
        ).strip()

        # En local, si REDIS_URL n'est pas définie, 
        # # on construit automatiquement l'URL Docker. 
        if self.DEBUG and not self.REDIS_URL: 
            self.REDIS_URL = ( 
                f"redis://{self.REDIS_HOST}:" 
                f"{self.REDIS_PORT}/" 
                f"{self.REDIS_DB}" 
            )

    def validate(self) -> None:

        # DATABASE
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL must be set."
            )

        # Production security
        if not self.DEBUG:

            if not self.SECRET_KEY:
                raise ValueError(
                    "SECRET_KEY must be set in production."
                )


            if self.SECRET_KEY == "your-secret-key":
                raise ValueError(
                    "Default SECRET_KEY cannot be used in production."
                )



settings = Settings()
settings.validate()