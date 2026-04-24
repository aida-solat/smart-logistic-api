"""Pytest fixtures for the smart logistics backend."""
import os
import pytest

# Ensure required env vars exist before `app.config` imports.
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("TRAFFIC_API_KEY", "test-traffic")
os.environ.setdefault("WEATHER_API_KEY", "test-weather")
os.environ.setdefault("TRAFFIC_API_URL", "https://example.invalid/traffic")
os.environ.setdefault("WEATHER_API_URL", "https://example.invalid/weather")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)
