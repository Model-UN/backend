from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str
    staff_application_id: str

    discord_applications_webhook_url: str
    discord_registrations_webhook_url: str
    discord_chief_of_staff_id: str
    discord_steering_committee_id: str
    discord_usg_admin_id: str


settings = Settings()
