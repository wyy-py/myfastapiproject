from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    DB: str
    COLLECTION: str
    USER_COLLECTION: str

    class Config:
        env_file = ".env"


config = Settings()
