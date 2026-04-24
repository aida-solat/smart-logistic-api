from app.ai import train_inventory_model, train_route_model
import pandas as pd

def train_and_save_models():
    # Training data for inventory prediction
    inventory_data = {
        "days": [1, 2, 3, 4, 5],
        "stock": [100, 90, 80, 70, 60]
    }
    train_inventory_model(inventory_data)
    print("Inventory model trained and saved successfully.")

    # Training data for route prediction
    route_data = pd.DataFrame({
        "distance": [10, 20, 30, 40, 50],
        "hour_of_day": [8, 12, 16, 20, 0],
        "weather_conditions": [1, 2, 3, 2, 1],
        "delay_minutes": [5, 10, 15, 20, 25]
    })
    train_route_model(route_data)
    print("Route model trained and saved successfully.")

if __name__ == "__main__":
    train_and_save_models()
