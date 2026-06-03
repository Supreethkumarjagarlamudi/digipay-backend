from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")
    MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID")

settings = Settings()