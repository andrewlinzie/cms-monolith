import os


class Settings:
    APP_NAME = "cms-monolith"
    APP_ENV = os.getenv("APP_ENV", "dev")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    PORT = int(os.getenv("PORT", "8002"))


settings = Settings()