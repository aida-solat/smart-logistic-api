from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    # External APIs are optional; endpoints that need them must call
    # require_traffic_api() / require_weather_api() at request time.
    TRAFFIC_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ROUTE_MODEL_PATH: str = "models/route_model.pkl"
    INVENTORY_MODEL_PATH: str = "models/inventory_model.pkl"
    TRAFFIC_API_URL: str = ""
    WEATHER_API_URL: str = ""

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }

    def require_traffic_api(self):
        if not self.TRAFFIC_API_KEY:
            raise ValueError(
                "TRAFFIC_API_KEY is missing. Configure it in environment variables."
            )

    def require_weather_api(self):
        if not self.WEATHER_API_KEY:
            raise ValueError(
                "WEATHER_API_KEY is missing. Configure it in environment variables."
            )


settings = Settings()
