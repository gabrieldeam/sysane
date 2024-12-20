from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configurações do banco de dados
    DATABASE_URL: str
    FRONTEND_URL: str

    # Configurações do email
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_USE_TLS: bool

    class Config:
        env_file = ".env"

# Instância global de configurações
settings = Settings()
