from geopy.distance import geodesic
import requests
from functools import lru_cache
from app.config import settings
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def optimize_route(start, destinations):
    distances = [geodesic(start, (dest.lat, dest.lon)).km for dest in destinations]
    sorted_destinations = [
        destinations[i]
        for i in sorted(range(len(destinations)), key=lambda k: distances[k])
    ]
    return [{"lat": d.lat, "lon": d.lon} for d in sorted_destinations]


@lru_cache(maxsize=128)
def get_traffic_data(start, destination, api_key):
    url = settings.TRAFFIC_API_URL
    if not url:
        raise ValueError("TRAFFIC_API_URL is not defined in the environment variables.")

    params = {
        "origins": f"{start[0]},{start[1]}",
        "destinations": f"{destination[0]},{destination[1]}",
        "key": api_key,
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch traffic data: {response.text}")

    data = response.json()
    try:
        distance = data["rows"][0]["elements"][0]["distance"]["value"]
        duration = data["rows"][0]["elements"][0]["duration"]["value"]
        return {"distance": distance, "duration": duration}
    except (KeyError, IndexError) as e:
        raise ValueError(f"Unexpected traffic data structure: {data}") from e


def get_weather_data(location, api_key, retries=3):
    url = settings.WEATHER_API_URL
    params = {
        "lat": location[0],
        "lon": location[1],
        "appid": api_key,
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                raise ValueError(f"Failed to fetch weather data: {response.text}")
        except requests.RequestException as e:
            if attempt < retries - 1:
                continue
            else:
                raise ValueError(
                    f"Error fetching weather data after {retries} attempts: {e}"
                )


def notify_slack(message: str):
    try:
        client = WebClient(token="YOUR_SLACK_BOT_TOKEN")
        client.chat_postMessage(channel="#alerts", text=message)
    except SlackApiError as e:
        logging.error(f"Slack notification failed: {e}")
