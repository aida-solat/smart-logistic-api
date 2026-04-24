import pickle
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from geopy.distance import geodesic
from app.utils import get_traffic_data, get_weather_data
from datetime import datetime
from app.config import settings
import logging

# Initialize logger
logger = logging.getLogger("ai")

ROUTE_MODEL_PATH = settings.ROUTE_MODEL_PATH
INVENTORY_MODEL_PATH = settings.INVENTORY_MODEL_PATH


def train_route_model(data):
    """Train a RandomForestRegressor to predict route delays."""
    try:
        X = data[["distance", "hour_of_day", "weather_conditions"]]
        y = data["delay_minutes"]
        model = RandomForestRegressor()
        model.fit(X, y)
        with open(ROUTE_MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
        logger.info("Route model trained and saved.")
    except Exception as e:
        logger.error(f"Failed to train route model: {e}")


def predict_route_delay(distance: float, weather_conditions: int, hour_of_day: int):
    """Predict route delays using a pre-trained model."""
    try:
        with open(ROUTE_MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        prediction = model.predict([[distance, hour_of_day, weather_conditions]])
        return {"distance": distance, "hour_of_day": hour_of_day, "weather_conditions": weather_conditions, "predicted_delay": prediction[0]}
    except FileNotFoundError:
        logger.error("Route model not found.")
        return {"error": "Route model not found."}
    except Exception as e:
        logger.error(f"Error predicting route delay: {e}")
        return {"error": str(e)}


def ai_optimize_route(start, destinations, traffic_api_key, weather_api_key):
    """Optimize route using AI-based delay predictions."""
    enriched_destinations = []
    for dest in destinations:
        try:
            # Get traffic and weather data
            traffic = get_traffic_data(start, (dest.lat, dest.lon), traffic_api_key)
            weather = get_weather_data((dest.lat, dest.lon), weather_api_key)

            # Predict delay
            delay_prediction = predict_route_delays(
                [
                    traffic["distance"],  # Distance in meters
                    datetime.utcnow().hour,
                    weather.get(
                        "conditions", 0
                    ),  # Handle missing weather conditions gracefully
                ]
            )

            enriched_destinations.append(
                {
                    "lat": dest.lat,
                    "lon": dest.lon,
                    "predicted_delay": delay_prediction,
                    "traffic": traffic,
                    "weather": weather,
                }
            )
        except Exception as e:
            logger.error(f"Error processing destination {dest}: {e}")
            enriched_destinations.append(
                {"lat": dest.lat, "lon": dest.lon, "error": str(e)}
            )

    return sorted(
        enriched_destinations, key=lambda x: x.get("predicted_delay", float("inf"))
    )


def load_route_model():
    """Load the trained route model from disk."""
    try:
        with open(ROUTE_MODEL_PATH, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        raise ValueError("Route model not found. Train the model first.")


### Train and Predict Inventory Model


def train_inventory_model(data):
    """Train a RandomForestRegressor for inventory demand prediction."""
    try:
        X = np.array(data["days"]).reshape(-1, 1)
        y = np.array(data["stock"])
        model = RandomForestRegressor()
        model.fit(X, y)
        with open(INVENTORY_MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
        logger.info("Inventory model trained and saved.")
    except Exception as e:
        logger.error(f"Failed to train inventory model: {e}")


def predict_stock(days_from_now):
    """Predict stock levels using the trained inventory model."""
    try:
        with open(INVENTORY_MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        return model.predict([[days_from_now]])
    except FileNotFoundError:
        logger.error("Inventory model file not found.")
        return None
    except Exception as e:
        logger.error(f"Error predicting stock: {e}")
        return None


def predict_inventory_demand(item_name: str, days_from_now: int):
    """Predict future inventory demand using a pre-trained model."""
    try:
        with open(INVENTORY_MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        prediction = model.predict([[days_from_now]])
        return {"item_name": item_name, "days_from_now": days_from_now, "predicted_demand": prediction[0]}
    except FileNotFoundError:
        logger.error("Inventory model not found.")
        return {"error": "Inventory model not found."}
    except Exception as e:
        logger.error(f"Error predicting inventory demand: {e}")
        return {"error": str(e)}
