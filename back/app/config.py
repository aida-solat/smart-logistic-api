from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    These settings are loaded from the environment variables specified in the `.env` file.
    """

    SECRET_KEY: str
    DATABASE_URL: str
    TRAFFIC_API_KEY: str
    WEATHER_API_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ROUTE_MODEL_PATH: str = "models/route_model.pkl"
    INVENTORY_MODEL_PATH: str = "models/inventory_model.pkl"
    TRAFFIC_API_URL: str  # Base URL for traffic data API
    WEATHER_API_URL: str  # Base URL for weather data API
    


    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",  # allow unrelated env vars (POSTGRES_*, REDIS_URL, etc.)
    }

    def validate_api_keys(self):
        """
        Validate the presence of critical API keys.
        Raises a ValueError if any required API key is missing.
        """
        if not self.TRAFFIC_API_KEY:
            raise ValueError(
                "TRAFFIC_API_KEY is missing. Please configure it in the environment variables."
            )
        if not self.WEATHER_API_KEY:
            raise ValueError(
                "WEATHER_API_KEY is missing. Please configure it in the environment variables."
            )

    def validate_model_paths(self):
        """
        Validate the presence of model paths.
        Raises a ValueError if any model path is not set.
        """
        if not self.ROUTE_MODEL_PATH:
            raise ValueError("ROUTE_MODEL_PATH is not defined.")
        if not self.INVENTORY_MODEL_PATH:
            raise ValueError("INVENTORY_MODEL_PATH is not defined.")


# Instantiate settings and validate critical configurations
settings = Settings()
try:
    settings.validate_api_keys()
    settings.validate_model_paths()
except ValueError as e:
    print(f"Configuration error: {e}")
    raise
