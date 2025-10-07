from decouple import config


class Settings:
    """
    Application settings class.
    Reads environment variables using python-decouple for configuration.
    """

    # General settings
    DEBUG = config("DEBUG", cast=bool)
    LOG_DIR = config("LOG_DIR")

    # Database settings
    DB_HOST = config("DB_HOST")
    DB_PORT = config("DB_PORT")
    DB_USER = config("DB_USER")
    DB_PASSWORD = config("DB_PASSWORD")
    DB_NAME = config("DB_NAME")

    # Broker settings
    BROKER_HOST = config("BROKER_HOST")
    BROKER_PORT = config("BROKER_PORT")
    BROKER_USER = config("BROKER_USER")
    BROKER_PASSWORD = config("BROKER_PASSWORD")

    # External API URLs
    JSON_PLACEHOLDER_URL = config("JSON_PLACEHOLDER_URL")
    FAKERAPI_URL = config("FAKERAPI_URL")

    @property
    def database_postgres_url(self):
        """
        DSN connection PostgreSQL.
        """
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def celery_broker_url(self):
        """
        DSN connection broker celery.
        """
        return f"amqp://{self.BROKER_USER}:{self.BROKER_PASSWORD}@{self.BROKER_HOST}:{self.BROKER_PORT}//"


settings = Settings()
