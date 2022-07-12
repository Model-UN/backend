from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str
    discord_applications_webhook_url: str
    discord_chief_of_staff_id: str
    discord_steering_committee_id: str


settings = Settings()
