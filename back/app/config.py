from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    TRAFFIC_API_KEY: str
    WEATHER_API_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ROUTE_MODEL_PATH: str = "models/route_model.pkl"
    INVENTORY_MODEL_PATH: str = "models/inventory_model.pkl"
    TRAFFIC_API_URL: str
    WEATHER_API_URL: str

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }

    def validate_api_keys(self):
        if not self.TRAFFIC_API_KEY:
            raise ValueError(
                "TRAFFIC_API_KEY is missing. Please configure it in the environment variables."
            )
        if not self.WEATHER_API_KEY:
            raise ValueError(
                "WEATHER_API_KEY is missing. Please configure it in the environment variables."
            )

    def validate_model_paths(self):
        if not self.ROUTE_MODEL_PATH:
            raise ValueError("ROUTE_MODEL_PATH is not defined.")
        if not self.INVENTORY_MODEL_PATH:
            raise ValueError("INVENTORY_MODEL_PATH is not defined.")


settings = Settings()
try:
    settings.validate_api_keys()
    settings.validate_model_paths()
except ValueError as e:
    print(f"Configuration error: {e}")
    raise
