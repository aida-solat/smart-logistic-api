from geopy.distance import geodesic
from datetime import datetime
import logging

logger = logging.getLogger("alerts")


async def send_real_time_alert(alert):
    event = {
        "type": "inventory_alert",
        "alert": alert,
    }
    await broadcast_notification(event)


def check_inventory_threshold(inventory, threshold=10):
    try:
        alerts = [
            {
                "item": item,
                "timestamp": datetime.utcnow(),
                "message": f"Low stock for {item['item_name']}!",
            }
            for item in inventory
            if item["stock"] < threshold
        ]
        for alert in alerts:
            asyncio.create_task(send_real_time_alert(alert))
        return alerts
    except Exception as e:
        logging.error(f"Error in inventory threshold check: {e}")
        return []


def check_route_deviation(actual_route, planned_route, deviation_tolerance=5.0):
    deviations = []
    try:
        for actual, planned in zip(actual_route, planned_route):
            if geodesic(actual, planned).km > deviation_tolerance:
                deviations.append({"actual": actual, "planned": planned})
        logger.info(f"Found {len(deviations)} route deviations.")
        return deviations
    except Exception as e:
        logger.error(f"Error checking route deviations: {e}")
        return deviations


def check_inventory_overstock(inventory, max_threshold=100):
    try:
        overstocked_items = [
            item for item in inventory if item["stock"] > max_threshold
        ]
        logger.info(f"Generated {len(overstocked_items)} overstock alerts.")
        return overstocked_items
    except KeyError as e:
        logger.error(f"Missing key in inventory data: {e}")
        return []
    except Exception as e:
        logger.error(f"Error checking inventory overstock: {e}")
        return []


def alert_route_delays(routes, delay_threshold=30):
    try:
        alerts = [
            {
                "route_id": route["route_id"],
                "message": f"Route delay exceeds {delay_threshold} minutes!",
            }
            for route in routes
            if route.get("predicted_delay", 0) > delay_threshold
        ]
        for alert in alerts:
            asyncio.create_task(send_real_time_alert(alert))
        return alerts
    except Exception as e:
        logging.error(f"Error in route delay alerting: {e}")
        return []


def alert_delay_deviation(actual_delays, predicted_delays, deviation_threshold=15):
    deviations = []
    try:
        for actual, predicted in zip(actual_delays, predicted_delays):
            if abs(actual - predicted) > deviation_threshold:
                deviations.append({"actual": actual, "predicted": predicted})
        logger.info(f"Found {len(deviations)} delay deviations.")
        return deviations
    except Exception as e:
        logger.error(f"Error checking delay deviations: {e}")
        return deviations
