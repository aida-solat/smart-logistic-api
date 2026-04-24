import asyncio
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, crud, schemas
from app.models import User, Role, Permission
from app.schemas import UserCreate
from app.auth import (
    oauth2_scheme,
    verify_token,
    create_access_token,
    require_role,
    get_current_user,
    get_password_hash,
    require_permission,
)
from app.utils import optimize_route
from app.config import settings
from app.ai import (
    ai_optimize_route,
    predict_inventory_demand,
    predict_route_delay,
)
from app.analytics import analyze_inventory_usage, analyze_route_performance
from app.causal import router as causal_router  # APIRouter instance
from app.optimizer import router as optim_router  # APIRouter instance
from app.simulator import router as sim_router  # APIRouter instance
from prometheus_client import Counter, Histogram, make_asgi_app
from typing import List, Dict, Optional
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import logging
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import StreamingResponse, Response
from datetime import datetime, timedelta
from app.models import Inventory, Route
from app.schemas import (
    InventoryItem,
    RouteRequest,
    RouteResponse,
    InventoryAnalyticsRequest,
    AdminDataRequest,
    PredictiveInventoryRequest,
    PredictiveRouteRequest,
    PredictiveResponse,
    TokenRequest,
)
import pandas as pd
from app.analytics import analyze_high_traffic_routes
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from app.analytics import analyze_high_traffic_routes
from sklearn.cluster import KMeans
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

connected_clients = []


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

logger.info("Starting Smart Logistics API...")

# Initialize database
models.Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(
    title="Smart Logistics — Causal Decision Copilot",
    description="Prescriptive, causal, risk-aware decision engine for logistics.",
    version="0.1.0",
)
app.include_router(causal_router)
app.include_router(optim_router)
app.include_router(sim_router)


@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    content = {"detail": str(exc)}

    # Ensure content is JSON-serializable
    for key, value in content.items():
        if isinstance(value, bytes):
            content[key] = value.decode("utf-8")

    return JSONResponse(content=content, status_code=500)


# Prometheus metrics
REQUEST_COUNT = Counter(
    "api_requests_total", "Total API requests", ["endpoint", "method"]
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Request latency", ["endpoint"]
)


# Prometheus middleware
@app.middleware("http")
async def add_metrics(request, call_next):
    endpoint = request.url.path
    method = request.method
    REQUEST_COUNT.labels(endpoint=endpoint, method=method).inc()
    with REQUEST_LATENCY.labels(endpoint=endpoint).time():
        response = await call_next(request)
        if isinstance(response, Response):
            logging.info(f"Processed response: {response.status_code}")
        return response


# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Logistics API!"}


@app.get("/monitor-models")
def monitor_models():
    """
    Check the status of the trained models and notify if retraining is required.

    Returns:
        dict: Status of the route and inventory models.
    """
    try:
        # Check route model status
        route_model_path = Path(settings.ROUTE_MODEL_PATH)
        inventory_model_path = Path(settings.INVENTORY_MODEL_PATH)

        route_model_status = "Available" if route_model_path.exists() else "Not Found"
        inventory_model_status = (
            "Available" if inventory_model_path.exists() else "Not Found"
        )

        # Check model freshness
        route_model_age = None
        inventory_model_age = None
        retrain_message = []

        if route_model_path.exists():
            route_model_age = (
                datetime.now()
                - datetime.fromtimestamp(route_model_path.stat().st_mtime)
            ).days
            if route_model_age > 30:
                retrain_message.append("Route model is older than 30 days.")

        if inventory_model_path.exists():
            inventory_model_age = (
                datetime.now()
                - datetime.fromtimestamp(inventory_model_path.stat().st_mtime)
            ).days
            if inventory_model_age > 30:
                retrain_message.append("Inventory model is older than 30 days.")

        # Send Slack notification if retraining is needed
        if retrain_message:
            notify_slack("\n".join(retrain_message))

        return {
            "route_model_status": route_model_status,
            "route_model_age_days": route_model_age,
            "inventory_model_status": inventory_model_status,
            "inventory_model_age_days": inventory_model_age,
            "retrain_message": retrain_message or "Models are up-to-date.",
        }

    except Exception as e:
        logger.error(f"Error monitoring models: {e}")
        raise HTTPException(status_code=500, detail="Failed to monitor models.")


def notify_slack(message: str):
    """
    Send a notification to a Slack channel.

    Args:
        message (str): The message to send.
    """
    try:
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel="#alerts", text=message)
        logger.info("Slack notification sent.")
    except SlackApiError as e:
        logger.error(f"Slack notification failed: {e}")


@app.post("/generate-token")
def generate_token(request: TokenRequest):
    # Default the role to "user" if it's missing or empty
    role = request.role or "user"

    # Generate the token
    access_token = create_access_token(data={"role": role})

    # Return the token along with the role
    return {"access_token": access_token, "token_type": "bearer", "role": role}


@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, hashed_password=hashed_password, role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.put("/users/{user_id}/assign-role/")
def assign_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role_id = role_id
    db.commit()
    return {"status": "success", "message": "Role assigned successfully"}


def check_permissions(user: User, required_permission: str):
    if required_permission not in user.role.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")


def require_permission(permission: str):
    def permission_dependency(user: User = Depends(get_current_user)):
        check_permissions(user, permission)

    return Depends(permission_dependency)


@app.get("/inventory", response_model=List[schemas.InventoryItem])
def read_inventory(db: Session = Depends(get_db)):
    return crud.get_inventory(db)


@app.post("/inventory", response_model=List[schemas.InventoryItem])
def create_inventory(items: List[schemas.InventoryItem], db: Session = Depends(get_db)):
    saved_items = []
    for item in items:
        try:
            saved_item = crud.create_inventory_item(db, item)
            saved_items.append(saved_item)
        except Exception as e:
            # Log error and continue with other items
            logging.error(f"Error saving item {item}: {e}")
    return saved_items


@app.put("/inventory/{item_id}")
def update_inventory(
    item_id: int, updates: schemas.InventoryUpdateRequest, db: Session = Depends(get_db)
):
    return crud.update_inventory_item(db, item_id, updates.dict(exclude_unset=True))


@app.get("/inventory-analytics")
def inventory_analytics(
    request: InventoryAnalyticsRequest = Depends(), db: Session = Depends(get_db)
):
    # Fetch inventory data from DB
    data = get_inventory_data_from_db(db)

    # Filter data by date range if specified
    if request.start_date or request.end_date:
        data = [
            record
            for record in data
            if (request.start_date is None or record["date"] >= request.start_date)
            and (request.end_date is None or record["date"] <= request.end_date)
        ]

    # Filter by item name if specified
    if request.item_name:
        data = [record for record in data if record["item_name"] == request.item_name]

    # Analyze filtered data
    return analyze_inventory_usage(data)


def get_inventory_data_from_db(db: Session):
    """Fetch inventory data from the database and serialize it."""
    result = db.query(Inventory).all()  # Query the Inventory table
    return [
        {
            "item_name": item.item_name,
            "stock": item.stock,
            "date": item.created_at if hasattr(item, "created_at") else None,
        }
        for item in result
    ]


@app.post("/optimize-route", response_model=schemas.RouteResponse)
def optimize_route_endpoint(request: RouteRequest, db: Session = Depends(get_db)):
    optimized_route = ai_optimize_route(
        start=(request.start.lat, request.start.lon),
        destinations=request.destinations,
        traffic_api_key=settings.TRAFFIC_API_KEY,
        weather_api_key=settings.WEATHER_API_KEY,
    )
    crud.save_route(db, request, optimized_route)
    return {"optimized_route": optimized_route}
    broadcast_notification({"type": "route_optimized", "route": optimized_route})
    return {"optimized_route": optimized_route}


@app.get("/route-analytics")
def route_analytics(db: Session = Depends(get_db)):
    routes = crud.get_all_routes(db)

    # Serialize routes into dictionaries
    serialized_routes = [
        {
            "route_id": route.route_id,
            "delay_minutes": (
                route.delay_minutes if hasattr(route, "delay_minutes") else 0
            ),
        }
        for route in routes
    ]

    # Log input data
    logging.info("Input Data for Route Analytics: %s", serialized_routes)

    try:
        return analyze_route_performance(serialized_routes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/routes/{route_id}")
def delete_route(route_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.route_id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")

    # Perform soft delete or actual delete
    route.deleted_at = datetime.utcnow()  # Soft delete
    db.commit()
    return {"message": f"Route {route_id} successfully deleted"}


@app.get(
    "/analytics/high-traffic-routes",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
def high_traffic_routes(db: Session = Depends(get_db)):
    routes = crud.get_all_routes(db)

    # Serialize the route data
    serialized_routes = [
        {
            "route_id": route.route_id,
            "distance": route.distance if hasattr(route, "distance") else 0,
            "duration": (
                route.duration if hasattr(route, "duration") else 1
            ),  # Avoid division by zero
        }
        for route in routes
    ]

    if not serialized_routes:
        raise HTTPException(status_code=404, detail="No routes available for analysis.")

    try:
        return analyze_high_traffic_routes(serialized_routes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/admin-data/", dependencies=[require_permission("view_reports")])
def get_admin_data():
    return {"message": "Admin data"}


@app.get(
    "/manager-dashboard", dependencies=[Depends(require_role(["manager", "admin"]))]
)
def manager_dashboard():
    # Example endpoint for manager or admin access
    return {"message": "Welcome to the manager dashboard!"}


@app.get(
    "/viewer-content",
    dependencies=[Depends(require_role(["viewer", "manager", "admin"]))],
)
def viewer_content():
    # Example endpoint accessible by all roles
    return {"message": "Content for all users with appropriate roles."}


@app.get("/sensitive-data", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
def sensitive_data(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    logging.info(f"Sensitive data accessed by user: {user.get('sub')}")
    return {"message": "Highly sensitive data"}


@app.get("/secure-data", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def secure_data(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Protected data (rate-limited)"}


@app.get("/rate-limited-data", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def rate_limited_data():
    return {"message": "This endpoint is rate-limited"}


@app.get("/docs", include_in_schema=False)
async def get_swagger_ui_html():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="API Docs")


@app.get("/redoc", include_in_schema=False)
async def get_redoc_html():
    return get_redoc_html(openapi_url=app.openapi_url, title="ReDoc")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = Redis.from_url(redis_url, decode_responses=True)
    await FastAPILimiter.init(redis)


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logging.error(f"Global error: {exc}")
    return JSONResponse(content={"detail": str(exc)}, status_code=500)


# WebSocket route monitoring
@app.websocket("/ws/routes")
async def websocket_routes(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate real-time updates
            await asyncio.sleep(5)  # Delay for simulation
            data = {
                "route_id": "example_route",
                "current_location": {"lat": 40.7128, "lon": -74.0060},
                "status": "on_time",
            }
            await websocket.send_json(data)
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")


@app.post("/predictive-insights", response_model=PredictiveResponse)
def predictive_insights(
    inventory_request: Optional[PredictiveInventoryRequest] = None,
    route_request: Optional[PredictiveRouteRequest] = None,
):
    """
    Provide predictive insights for inventory demand and route delays.
    """
    inventory_prediction = None
    route_prediction = None

    if inventory_request:
        inventory_prediction = predict_inventory_demand(
            inventory_request.item_name, inventory_request.days_from_now
        )

    if route_request:
        route_prediction = predict_route_delay(
            route_request.distance,
            route_request.weather_conditions,
            route_request.hour_of_day,
        )

    return {
        "inventory_prediction": inventory_prediction,
        "route_prediction": route_prediction,
    }


@app.post("/train-models")
def train_models():
    from app.ai import train_inventory_model, train_route_model
    import pandas as pd

    # Inventory training data
    inventory_data = {"days": [1, 2, 3, 4, 5], "stock": [100, 90, 80, 70, 60]}
    train_inventory_model(inventory_data)

    # Route training data
    route_data = pd.DataFrame(
        {
            "distance": [10, 20, 30, 40, 50],
            "hour_of_day": [8, 12, 16, 20, 0],
            "weather_conditions": [1, 2, 3, 2, 1],
            "delay_minutes": [5, 10, 15, 20, 25],
        }
    )
    train_route_model(route_data)

    return {"message": "Models trained and saved successfully"}


@app.post("/retrain-models")
def retrain_models():
    try:
        from app.ai import train_inventory_model, train_route_model

        # Retraining inventory model
        inventory_data = {"days": [1, 2, 3, 4, 5], "stock": [100, 90, 80, 70, 60]}
        train_inventory_model(inventory_data)

        # Retraining route model
        route_data = pd.DataFrame(
            {
                "distance": [10, 20, 30, 40, 50],
                "hour_of_day": [8, 12, 16, 20, 0],
                "weather_conditions": [1, 2, 3, 2, 1],
                "delay_minutes": [5, 10, 15, 20, 25],
            }
        )
        train_route_model(route_data)

        return {"status": "success", "message": "Models retrained successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/model-status")
def model_status():
    from pathlib import Path

    route_model_status = Path(settings.ROUTE_MODEL_PATH).exists()
    inventory_model_status = Path(settings.INVENTORY_MODEL_PATH).exists()

    return {
        "route_model": "Available" if route_model_status else "Not Found",
        "inventory_model": "Available" if inventory_model_status else "Not Found",
    }


@app.get("/data-summary")
def data_summary(db: Session = Depends(get_db)):
    # Fetch inventory summary
    inventory_items = crud.get_inventory(db)
    inventory_summary = [
        {"item_name": item.item_name, "stock": item.stock, "location": item.location}
        for item in inventory_items
    ]

    # Fetch active routes summary
    active_routes = crud.get_active_routes(db)
    route_summary = [
        {
            "route_id": route.route_id,
            "distance": route.distance,
            "duration": route.duration,
        }
        for route in active_routes
    ]

    return {"inventory_summary": inventory_summary, "route_summary": route_summary}


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # This can be replaced with actual alert-generating logic
            alert_data = {
                "type": "inventory",
                "message": "Low stock detected for item ABC",
                "timestamp": datetime.utcnow().isoformat(),
            }
            await websocket.send_json(alert_data)
            await asyncio.sleep(10)  # Example interval for sending alerts
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected for alerts")


# analytics endpoint for trend forecasting
@app.get("/analytics/forecast")
def trend_forecasting(db: Session = Depends(get_db)):
    try:
        inventory_data = crud.get_inventory(db)
        inventory_df = pd.DataFrame(
            [
                {
                    "date": item.created_at,
                    "stock": item.stock,
                }
                for item in inventory_data
            ]
        )
        inventory_df["date"] = pd.to_datetime(inventory_df["date"])
        inventory_df.sort_values("date", inplace=True)
        inventory_df.set_index("date", inplace=True)

        # Time series forecasting using ARIMA
        model = ARIMA(inventory_df["stock"], order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=10)  # Forecast next 10 steps

        return {"forecast": forecast.tolist()}
    except Exception as e:
        logger.error(f"Error in trend forecasting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# analytics endpoint for clustering
@app.get("/analytics/clustering")
def clustering_analysis(by: str = "location", db: Session = Depends(get_db)):
    try:
        inventory_data = crud.get_inventory(db)
        inventory_df = pd.DataFrame(
            [
                {
                    "item_name": item.item_name,
                    "stock": item.stock,
                    "location": item.location,
                }
                for item in inventory_data
            ]
        )

        if by == "location":
            data = inventory_df[["location", "stock"]]
            data["location"] = data["location"].astype("category").cat.codes
        elif by == "category":
            data = inventory_df[["item_name", "stock"]]
            data["item_name"] = data["item_name"].astype("category").cat.codes
        else:
            raise HTTPException(status_code=400, detail="Invalid clustering parameter.")

        # Clustering using K-Means
        kmeans = KMeans(n_clusters=3, random_state=42)
        inventory_df["cluster"] = kmeans.fit_predict(data)

        return inventory_df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error in clustering analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint to broadcast real-time notifications about routes or inventory updates.
    """
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Keep connection open
            await asyncio.sleep(10)  # Placeholder for real-time updates
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logging.info("WebSocket client disconnected.")


def broadcast_notification(event: dict):
    """
    Broadcast an event to all connected WebSocket clients.

    Args:
        event (dict): Event data to send.
    """
    for websocket in connected_clients:
        asyncio.create_task(websocket.send_json(event))
