from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the bot.
    """
    # Bot token
    token: str
    # Bot prefix
    prefix: str

    class Config:
        env_prefix = "discord_"


settings = Settings()
