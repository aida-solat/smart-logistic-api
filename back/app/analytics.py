import pandas as pd
import numpy as np
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def analyze_inventory_usage(data: List[Dict]) -> Dict:
    if not data or not all("item_name" in d and "stock" in d for d in data):
        logger.error("Invalid data for inventory usage analysis.")
        raise ValueError("Each record must contain 'item_name' and 'stock'.")

    df = pd.DataFrame(data)
    avg_usage = df.groupby("item_name")["stock"].mean()
    logger.info(f"Calculated average usage: {avg_usage}")
    return avg_usage.to_dict()


def analyze_route_performance(data: List[Dict]) -> Dict:
    if not all("route_id" in d and "delay_minutes" in d for d in data):
        logger.error("Invalid data for route performance analysis.")
        raise ValueError("Each record must contain 'route_id' and 'delay_minutes'.")

    df = pd.DataFrame(data)
    df["delay_minutes"] = pd.to_numeric(df["delay_minutes"], errors="coerce").fillna(0)
    df["delay_minutes"] = df["delay_minutes"].replace([np.inf, -np.inf], 0)

    delays = df.groupby("route_id")["delay_minutes"].mean()
    logger.info(f"Calculated route delays: {delays}")
    return delays.to_dict()


def analyze_inventory_trend(data: List[Dict]) -> Dict:
    if not data or "date" not in data[0]:
        logger.error("Invalid data for inventory trend analysis.")
        raise ValueError("'date' column is required in the input data.")

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    trend = df.groupby("date")["stock"].sum().pct_change().fillna(0)
    logger.info(f"Calculated inventory trends: {trend}")
    return trend.to_dict()


def analyze_route_delays(data: List[Dict]) -> Dict:
    if not all("route_id" in d and "delay_minutes" in d for d in data):
        logger.error("Invalid data for route delay analysis.")
        raise ValueError("Each record must contain 'route_id' and 'delay_minutes'.")

    df = pd.DataFrame(data)
    delays = df.groupby("route_id")["delay_minutes"].describe().to_dict()
    logger.info(f"Calculated route delay statistics: {delays}")
    return delays


def analyze_rolling_inventory_trend(data: List[Dict], window: int = 7) -> Dict:
    if not data or "date" not in data[0]:
        logger.error("Invalid data for rolling inventory trend analysis.")
        raise ValueError("'date' column is required in the input data.")

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    rolling_avg = df["stock"].rolling(window=window).mean().fillna(0)
    logger.info(f"Calculated rolling inventory trends: {rolling_avg}")
    return rolling_avg.to_dict()


def analyze_high_traffic_routes(data: List[Dict]) -> List[Dict]:
    if not data or "distance" not in data[0] or "duration" not in data[0]:
        logger.error("Invalid data for high traffic route analysis.")
        raise ValueError(
            "'distance' and 'duration' columns are required in the input data."
        )

    df = pd.DataFrame(data)
    df = df[df["duration"] > 0]
    df["traffic_density"] = df["distance"] / df["duration"]

    threshold = df["traffic_density"].quantile(0.9)
    high_traffic_routes = df[df["traffic_density"] > threshold]
    logger.info(f"Identified high traffic routes: {high_traffic_routes}")
    return high_traffic_routes.to_dict(orient="records")


def get_inventory_data_from_db():
    try:
        result = db.query(Inventory).all()
        inventory_data = [
            {
                "item_name": item.item_name,
                "stock": item.stock,
                "date": item.created_at if hasattr(item, "created_at") else None,
            }
            for item in result
        ]
        logger.info(f"Fetched inventory data: {inventory_data}")
        return inventory_data
    except Exception as e:
        logger.error(f"Error fetching inventory data: {e}")
        raise


def inventory_analytics():
    try:
        db_data = get_inventory_data_from_db()
        return analyze_inventory_usage(db_data)
    except Exception as e:
        logger.error(f"Error in inventory analytics: {e}")
        raise
