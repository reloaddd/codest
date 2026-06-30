from pydantic_settings import BaseSettings, SettingsConfigDict
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    database_url:str
    secret_key:str

    model_config=SettingsConfigDict(env_file=ENV_FILE_PATH, extra="ignore")

settings=Settings()
