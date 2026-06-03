from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql://isyshell:isyshell@postgres:5432/isyshell"
    admin_token: str = "supersecret"
    admin_password: str = "admin123"
    scripts_dir: str = "/scripts"

settings = Settings()
